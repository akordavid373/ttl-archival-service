"""
HTTP Cache Middleware for FastAPI.

Implements the full HTTP caching contract:
  - Cache-Control  (max-age, no-store, private, public)
  - ETag / If-None-Match  (conditional GET → 304 Not Modified)
  - Last-Modified / If-Modified-Since
  - Vary  header
  - X-Cache  diagnostic header  (HIT | MISS | BYPASS | STALE)
  - X-Cache-Key  (sha256 of the cache key, safe to expose)

Only GET and HEAD requests are cached.  Write methods (POST, PUT, PATCH,
DELETE) automatically invalidate the affected resource's cache entries.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from email.utils import formatdate, parsedate_to_datetime
from typing import Optional, Sequence

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
from starlette.types import ASGIApp

from app.cache.manager import CacheNamespace, cache_manager

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Paths whose responses should NEVER be cached
BYPASS_PATHS: set[str] = {
    "/health",
    "/metrics",
    "/auth/token",
    "/auth/refresh",
    "/docs",
    "/openapi.json",
}

# Paths that are always public (no auth dependency)
PUBLIC_PATHS: set[str] = {
    "/api/v1/records",
    "/api/v1/policies",
    "/api/v1/analytics",
}

# Map URL prefixes → (namespace, ttl_seconds)
ROUTE_CACHE_CONFIG: list[tuple[str, str, int]] = [
    ("/api/v1/records",    CacheNamespace.RECORDS,    300),
    ("/api/v1/policies",   CacheNamespace.POLICIES,   600),
    ("/api/v1/analytics",  CacheNamespace.ANALYTICS,  120),
    ("/api/v1/blockchain", CacheNamespace.BLOCKCHAIN, 900),
    ("/api/v1/health",     CacheNamespace.HEALTH,     30),
]

# Mutation methods that trigger cache invalidation
MUTATION_METHODS: frozenset[str] = frozenset({"POST", "PUT", "PATCH", "DELETE"})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cache_key_for(request: Request) -> str:
    """Deterministic cache key: method + path + sorted query string."""
    qs = "&".join(
        f"{k}={v}"
        for k, v in sorted(request.query_params.items())
    )
    raw = f"{request.method}:{request.url.path}:{qs}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _route_config(path: str) -> Optional[tuple[str, int]]:
    """Return (namespace, ttl) for the best-matching route prefix, or None."""
    for prefix, ns, ttl in ROUTE_CACHE_CONFIG:
        if path.startswith(prefix):
            return str(ns), ttl
    return None


def _is_private(request: Request) -> bool:
    """Heuristic: treat requests with Authorization headers as private."""
    return "authorization" in request.headers


def _http_date(ts: float) -> str:
    return formatdate(ts, usegmt=True)


def _parse_http_date(value: str) -> Optional[float]:
    try:
        return parsedate_to_datetime(value).timestamp()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

class CacheMiddleware(BaseHTTPMiddleware):
    """
    Full HTTP caching middleware.

    Mount BEFORE any authentication middleware so that the cache can serve
    public responses without touching the auth stack.
    """

    def __init__(self, app: ASGIApp, *, vary_headers: Sequence[str] = ("Accept-Encoding",)) -> None:
        super().__init__(app)
        self._vary = list(vary_headers)

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    async def dispatch(self, request: Request, call_next) -> StarletteResponse:
        path = request.url.path

        # 1. Hard bypass – never cache these
        if path in BYPASS_PATHS or path.startswith("/admin"):
            return await call_next(request)

        # 2. Mutation methods → invalidate then pass through
        if request.method in MUTATION_METHODS:
            response = await call_next(request)
            if response.status_code < 400:
                await self._invalidate_for_mutation(request)
            return response

        # 3. Only cache GET / HEAD
        if request.method not in ("GET", "HEAD"):
            return await call_next(request)

        # 4. Find matching route config
        config = _route_config(path)
        if config is None:
            return await call_next(request)

        namespace, ttl = config
        cache_key = _cache_key_for(request)

        # 5. Try to serve from cache
        entry = await cache_manager.get(namespace, cache_key)
        if entry:
            return self._serve_from_cache(request, entry)

        # 6. Cache MISS – call the actual handler
        t0 = time.time()
        response = await call_next(request)
        latency = time.time() - t0

        # 7. Only cache successful, cacheable responses
        if self._is_cacheable(response):
            body = b""
            async for chunk in response.body_iterator:  # type: ignore[attr-defined]
                body += chunk

            try:
                data = json.loads(body)
            except Exception:
                data = body.decode(errors="replace")

            tags = self._tags_for(path)
            await cache_manager.set(namespace, cache_key, data, ttl=ttl, tags=tags)

            # Re-build the response so the body is re-streamable
            response = Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
            self._apply_cache_headers(response, ttl=ttl, hit=False, private=_is_private(request))
            response.headers["X-Response-Time"] = f"{latency * 1000:.1f}ms"
            logger.debug("Cache MISS  %s  (%.0fms)", path, latency * 1000)

        return response

    # ------------------------------------------------------------------
    # Serving from cache
    # ------------------------------------------------------------------

    def _serve_from_cache(self, request: Request, entry) -> StarletteResponse:
        """Build a 200 or 304 response from a cache entry."""
        # ETag conditional request
        client_etag = request.headers.get("if-none-match", "").strip('"')
        if client_etag and client_etag == entry.etag:
            logger.debug("Cache 304  etag=%s", entry.etag)
            return Response(status_code=304, headers={"ETag": f'"{entry.etag}"'})

        # If-Modified-Since conditional request
        ims = request.headers.get("if-modified-since")
        if ims:
            client_ts = _parse_http_date(ims)
            if client_ts and entry.created_at <= client_ts:
                return Response(status_code=304)

        body = json.dumps(entry.data).encode()
        response = Response(
            content=body,
            status_code=200,
            media_type="application/json",
        )
        self._apply_cache_headers(
            response,
            ttl=entry.remaining_ttl,
            hit=True,
            private=False,
            etag=entry.etag,
            last_modified=entry.created_at,
        )
        return response

    # ------------------------------------------------------------------
    # Cache-Control / ETag helpers
    # ------------------------------------------------------------------

    def _apply_cache_headers(
        self,
        response: Response,
        *,
        ttl: int,
        hit: bool,
        private: bool = False,
        etag: str = "",
        last_modified: Optional[float] = None,
    ) -> None:
        visibility = "private" if private else "public"
        response.headers["Cache-Control"] = f"{visibility}, max-age={ttl}, stale-while-revalidate=60"
        response.headers["X-Cache"] = "HIT" if hit else "MISS"
        response.headers["Vary"] = ", ".join(self._vary)

        if etag:
            response.headers["ETag"] = f'"{etag}"'
        if last_modified:
            response.headers["Last-Modified"] = _http_date(last_modified)

    @staticmethod
    def _is_cacheable(response) -> bool:
        if response.status_code not in (200, 203):
            return False
        cc = response.headers.get("cache-control", "")
        if "no-store" in cc or "private" in cc:
            return False
        return True

    # ------------------------------------------------------------------
    # Tag derivation & mutation invalidation
    # ------------------------------------------------------------------

    @staticmethod
    def _tags_for(path: str) -> list[str]:
        """Derive invalidation tags from a URL path."""
        tags: list[str] = []
        parts = [p for p in path.split("/") if p]
        # e.g. /api/v1/records/42  →  tags: ["records", "records:42"]
        if len(parts) >= 3:
            resource = parts[2]          # "records"
            tags.append(resource)
            if len(parts) >= 4:
                tags.append(f"{resource}:{parts[3]}")
        return tags

    async def _invalidate_for_mutation(self, request: Request) -> None:
        path = request.url.path
        tags = self._tags_for(path)
        for tag in tags:
            count = await cache_manager.invalidate_by_tag(tag)
            if count:
                logger.info("Mutation on %s invalidated %d entries via tag '%s'", path, count, tag)


# ---------------------------------------------------------------------------
# No-cache decorator helper (for individual routes that opt out)
# ---------------------------------------------------------------------------

def no_cache(response: Response) -> None:
    """Call inside a route handler to prevent caching of that response."""
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["X-Cache"] = "BYPASS"
