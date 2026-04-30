"""
Cache Management API Routes

Exposes:
  GET  /api/v1/cache/metrics          – hit/miss rates, latency, namespace breakdown
  GET  /api/v1/cache/redis-info       – memory, evictions, keyspace stats
  POST /api/v1/cache/invalidate/tag/{tag}       – invalidate by tag
  POST /api/v1/cache/invalidate/namespace/{ns}  – invalidate entire namespace
  POST /api/v1/cache/invalidate/pattern         – SCAN-based pattern invalidation
  POST /api/v1/cache/warm                       – trigger named warmers (or all)
  GET  /api/v1/cache/health                     – combined cache health check
"""

from __future__ import annotations

import time
from typing import Optional

from fastapi import APIRouter, Body, HTTPException, Query, status
from pydantic import BaseModel

from app.cache.manager import CacheNamespace, cache_manager
from app.cache.warming import register_all_warmers

router = APIRouter(prefix="/api/v1/cache", tags=["Cache Management"])


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class InvalidatePatternRequest(BaseModel):
    pattern: str


class WarmRequest(BaseModel):
    warmers: Optional[list[str]] = None   # None → run all registered warmers


class MetricsResponse(BaseModel):
    hits: int
    misses: int
    invalidations: int
    errors: int
    warm_ops: int
    hit_rate_pct: float
    avg_latency_ms: float
    namespace_hits: dict[str, int]
    timestamp: float


class CacheHealthResponse(BaseModel):
    status: str           # "healthy" | "degraded" | "unavailable"
    redis_connected: bool
    hit_rate_pct: float
    avg_latency_ms: float
    details: dict


# ---------------------------------------------------------------------------
# Metrics endpoint
# ---------------------------------------------------------------------------

@router.get("/metrics", response_model=MetricsResponse, summary="Cache performance metrics")
async def get_cache_metrics():
    """
    Returns in-process cache counters:
    - **hits / misses / hit_rate_pct** – cache effectiveness
    - **avg_latency_ms** – average cache round-trip
    - **invalidations / warm_ops** – operational counters
    - **namespace_hits** – per-namespace breakdown
    """
    metrics = cache_manager.get_metrics()
    metrics["timestamp"] = time.time()
    return metrics


# ---------------------------------------------------------------------------
# Redis info endpoint
# ---------------------------------------------------------------------------

@router.get("/redis-info", summary="Redis server statistics")
async def get_redis_info():
    """
    Returns selected fields from Redis ``INFO`` covering memory usage,
    hit/miss counters at the Redis level, evictions, and connected clients.
    """
    info = await cache_manager.get_redis_info()
    if not info:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not retrieve Redis info",
        )
    return info


# ---------------------------------------------------------------------------
# Invalidation endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/invalidate/tag/{tag}",
    summary="Invalidate all entries for a tag",
    status_code=status.HTTP_200_OK,
)
async def invalidate_by_tag(tag: str):
    """
    Deletes every cache entry registered under *tag*.

    Tags are derived automatically by the middleware from URL path segments.
    For example, ``/api/v1/records/42`` creates tags ``records`` and
    ``records:42``.  Invalidating ``records`` clears all record list caches;
    invalidating ``records:42`` clears only that record's cache.
    """
    count = await cache_manager.invalidate_by_tag(tag)
    return {"tag": tag, "invalidated": count}


@router.post(
    "/invalidate/namespace/{namespace}",
    summary="Invalidate an entire cache namespace",
    status_code=status.HTTP_200_OK,
)
async def invalidate_namespace(namespace: str):
    """
    Scans and deletes all keys in the given namespace (e.g. ``records``,
    ``policies``, ``analytics``, ``blockchain``, ``health``).

    Uses Redis SCAN to avoid blocking the server.
    """
    valid_namespaces = {ns.value for ns in CacheNamespace}
    if namespace not in valid_namespaces:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid namespace. Valid values: {sorted(valid_namespaces)}",
        )
    count = await cache_manager.invalidate_namespace(namespace)
    return {"namespace": namespace, "invalidated": count}


@router.post(
    "/invalidate/pattern",
    summary="Invalidate by Redis glob pattern",
    status_code=status.HTTP_200_OK,
)
async def invalidate_by_pattern(body: InvalidatePatternRequest):
    """
    Deletes all cache keys matching *pattern* (Redis glob syntax).

    Example: ``ttl_cache:records:*`` removes all record cache entries.

    ⚠️ Use with care in production – a broad pattern can evict large amounts
    of cached data.
    """
    count = await cache_manager.invalidate_pattern(body.pattern)
    return {"pattern": body.pattern, "invalidated": count}


# ---------------------------------------------------------------------------
# Cache warming endpoint
# ---------------------------------------------------------------------------

@router.post("/warm", summary="Trigger cache warmers", status_code=status.HTTP_200_OK)
async def warm_cache(body: WarmRequest = Body(default=WarmRequest())):
    """
    Executes one or more named cache warmers.

    - If ``warmers`` is omitted or empty, **all** registered warmers run.
    - Pass ``warmers: ["active_policies", "recent_records"]`` to run a subset.

    Returns a mapping of warmer name → success (bool).
    """
    # Ensure warmers are registered (idempotent)
    register_all_warmers(cache_manager)

    names = tuple(body.warmers) if body.warmers else ()
    results = await cache_manager.warm(*names)
    return {"results": results, "total_warmed": sum(results.values())}


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

@router.get("/health", response_model=CacheHealthResponse, summary="Cache subsystem health")
async def cache_health():
    """
    Returns an aggregate health status for the caching subsystem.

    - **healthy**     – Redis is reachable and hit rate > 50 %
    - **degraded**    – Redis is reachable but hit rate is low (< 20 %)
    - **unavailable** – Redis is not reachable
    """
    redis_connected = False
    redis_info: dict = {}

    try:
        redis_info = await cache_manager.get_redis_info()
        redis_connected = bool(redis_info)
    except Exception:
        pass

    metrics = cache_manager.get_metrics()
    hit_rate = metrics.get("hit_rate_pct", 0.0)

    if not redis_connected:
        cache_status = "unavailable"
    elif hit_rate < 20:
        cache_status = "degraded"
    else:
        cache_status = "healthy"

    return CacheHealthResponse(
        status=cache_status,
        redis_connected=redis_connected,
        hit_rate_pct=hit_rate,
        avg_latency_ms=metrics.get("avg_latency_ms", 0.0),
        details={
            "metrics": metrics,
            "redis": redis_info,
        },
    )
