"""
@cached decorator — apply directly to FastAPI route handlers.

The decorator wraps any async endpoint and handles the full
get-or-compute-and-store cycle, keeping cache logic out of
business code.

Example
-------
::

    @router.get("/records/{record_id}")
    @cached(namespace="records", ttl=300, tags=lambda req, **kw: ["records", f"records:{kw['record_id']}"])
    async def get_record(record_id: str, request: Request):
        return await db.fetch_record(record_id)
"""

from __future__ import annotations

import functools
import hashlib
import json
import logging
from typing import Any, Callable, Optional, Sequence, Union

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.cache.manager import cache_manager

logger = logging.getLogger(__name__)

# Type alias for a tag factory (receives the same kwargs as the wrapped fn)
TagFactory = Callable[..., list[str]]


def cached(
    namespace: str,
    *,
    ttl: Optional[int] = None,
    tags: Union[list[str], TagFactory, None] = None,
    key_prefix: str = "",
    skip_on_error: bool = True,
) -> Callable:
    """
    Decorator that caches the return value of an async route handler.

    Parameters
    ----------
    namespace:
        Cache namespace (maps to ``CacheNamespace`` enum values).
    ttl:
        Time-to-live in seconds.  Falls back to the namespace default.
    tags:
        Either a static list of tag strings, or a callable that receives
        ``(request, **path_params)`` and returns a list of tags.
    key_prefix:
        Additional string prepended to the auto-generated cache key.
    skip_on_error:
        If True, a Redis error lets the request fall through to the handler
        rather than raising.  Defaults to True.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Extract the FastAPI Request from args/kwargs
            request: Optional[Request] = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if request is None:
                request = kwargs.get("request")

            # Build cache key
            cache_key = _build_key(request, func.__name__, key_prefix, kwargs)

            # Try cache
            try:
                entry = await cache_manager.get(namespace, cache_key)
                if entry is not None:
                    logger.debug("@cached HIT  %s / %s", namespace, cache_key[:16])
                    response = JSONResponse(content=entry.data)
                    response.headers["X-Cache"] = "HIT"
                    response.headers["ETag"] = f'"{entry.etag}"'
                    if entry.remaining_ttl:
                        response.headers["Cache-Control"] = f"public, max-age={entry.remaining_ttl}"
                    return response
            except Exception as exc:
                if not skip_on_error:
                    raise
                logger.warning("@cached GET error: %s", exc)

            # Cache miss — call the real handler
            result = await func(*args, **kwargs)

            # Store result
            try:
                data = _extract_data(result)
                resolved_tags = _resolve_tags(tags, request, kwargs)
                await cache_manager.set(namespace, cache_key, data, ttl=ttl, tags=resolved_tags)

                # Augment response with cache headers
                if isinstance(result, Response):
                    result.headers["X-Cache"] = "MISS"
                    if ttl:
                        result.headers["Cache-Control"] = f"public, max-age={ttl}"
            except Exception as exc:
                if not skip_on_error:
                    raise
                logger.warning("@cached SET error: %s", exc)

            return result

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# cache_invalidate  helper (call from write endpoints)
# ---------------------------------------------------------------------------

async def cache_invalidate(*tags: str) -> dict[str, int]:
    """
    Convenience coroutine: invalidate one or more tags.

    Usage inside a route handler::

        await cache_invalidate("records", f"records:{record_id}")
    """
    results: dict[str, int] = {}
    for tag in tags:
        results[tag] = await cache_manager.invalidate_by_tag(tag)
    return results


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_key(
    request: Optional[Request],
    func_name: str,
    prefix: str,
    kwargs: dict,
) -> str:
    parts = [prefix, func_name]
    if request:
        qs = "&".join(f"{k}={v}" for k, v in sorted(request.query_params.items()))
        parts.append(qs)
    # Include path params (exclude 'request', 'response', 'db', 'session')
    skip = {"request", "response", "db", "session", "background_tasks"}
    for k, v in sorted(kwargs.items()):
        if k not in skip:
            parts.append(f"{k}={v}")
    raw = ":".join(str(p) for p in parts if p)
    return hashlib.sha256(raw.encode()).hexdigest()


def _extract_data(result: Any) -> Any:
    """Pull the serialisable payload out of a Starlette/FastAPI response."""
    if isinstance(result, JSONResponse):
        return json.loads(result.body)
    if isinstance(result, Response):
        try:
            return json.loads(result.body)
        except Exception:
            return result.body.decode(errors="replace")
    return result  # plain dict / Pydantic model returned by the handler


def _resolve_tags(
    tags: Union[list[str], TagFactory, None],
    request: Optional[Request],
    kwargs: dict,
) -> list[str]:
    if tags is None:
        return []
    if callable(tags):
        try:
            return tags(request, **kwargs)
        except Exception as exc:
            logger.warning("Tag factory raised: %s", exc)
            return []
    return list(tags)
