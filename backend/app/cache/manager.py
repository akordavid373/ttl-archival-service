"""
Cache Manager - Core caching layer with Redis backend.

Provides:
- TTL-aware response caching
- Tag-based invalidation groups
- LRU eviction awareness
- Cache warming utilities
- Real-time performance metrics
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants & enumerations
# ---------------------------------------------------------------------------

class CacheNamespace(str, Enum):
    """Top-level namespaces that partition the Redis keyspace."""
    RECORDS    = "records"
    POLICIES   = "policies"
    ANALYTICS  = "analytics"
    BLOCKCHAIN = "blockchain"
    HEALTH     = "health"


# Default TTLs (seconds) per namespace
NAMESPACE_TTLS: dict[CacheNamespace, int] = {
    CacheNamespace.RECORDS:    300,   #  5 min  – mutable data
    CacheNamespace.POLICIES:   600,   # 10 min  – semi-stable
    CacheNamespace.ANALYTICS:  120,   #  2 min  – frequently updated
    CacheNamespace.BLOCKCHAIN: 900,   # 15 min  – immutable on-chain data
    CacheNamespace.HEALTH:     30,    # 30 sec  – near-real-time
}

# Redis key prefixes
PREFIX_CACHE    = "ttl_cache"
PREFIX_TAG      = "ttl_tag"
PREFIX_METRICS  = "ttl_metrics"
PREFIX_WARMING  = "ttl_warm"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class CacheEntry:
    """Serialisable wrapper stored in Redis."""
    data: Any
    created_at: float
    ttl: int
    namespace: str
    cache_key: str
    hit_count: int = 0
    etag: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "data": self.data,
            "created_at": self.created_at,
            "ttl": self.ttl,
            "namespace": self.namespace,
            "cache_key": self.cache_key,
            "hit_count": self.hit_count,
            "etag": self.etag,
        })

    @classmethod
    def from_json(cls, raw: str) -> "CacheEntry":
        d = json.loads(raw)
        return cls(**d)

    @property
    def age(self) -> float:
        return time.time() - self.created_at

    @property
    def remaining_ttl(self) -> int:
        return max(0, self.ttl - int(self.age))


@dataclass
class CacheMetrics:
    """Aggregate stats, held in-process and periodically flushed to Redis."""
    hits:          int   = 0
    misses:        int   = 0
    invalidations: int   = 0
    errors:        int   = 0
    warm_ops:      int   = 0
    total_latency: float = 0.0   # seconds
    namespace_hits: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total else 0.0

    @property
    def avg_latency_ms(self) -> float:
        total = self.hits + self.misses
        return (self.total_latency / total * 1000) if total else 0.0

    def to_dict(self) -> dict:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "invalidations": self.invalidations,
            "errors": self.errors,
            "warm_ops": self.warm_ops,
            "hit_rate_pct": round(self.hit_rate, 2),
            "avg_latency_ms": round(self.avg_latency_ms, 3),
            "namespace_hits": dict(self.namespace_hits),
        }


# ---------------------------------------------------------------------------
# Cache Manager
# ---------------------------------------------------------------------------

class CacheManager:
    """
    Async Redis-backed cache manager.

    Features
    --------
    * Namespaced keys with configurable TTLs
    * Tag-based bulk invalidation  (e.g. invalidate all ``records:*``)
    * ETag generation for HTTP conditional requests
    * In-memory metrics with optional Redis persistence
    * Cache-warming API for pre-loading hot paths
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0") -> None:
        self._redis_url = redis_url
        self._client: Optional[aioredis.Redis] = None
        self._metrics = CacheMetrics()
        self._warming_registry: dict[str, Callable] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        self._client = aioredis.from_url(
            self._redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
        await self._client.ping()
        logger.info("CacheManager connected to Redis at %s", self._redis_url)

    async def disconnect(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_key(self, namespace: str, key: str) -> str:
        return f"{PREFIX_CACHE}:{namespace}:{key}"

    def _build_tag_key(self, tag: str) -> str:
        return f"{PREFIX_TAG}:{tag}"

    @staticmethod
    def _make_etag(data: Any) -> str:
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(raw.encode()).hexdigest()  # noqa: S324 – used as cache ETag, not security

    def _record_latency(self, start: float) -> None:
        self._metrics.total_latency += time.time() - start

    async def _ensure_connected(self) -> aioredis.Redis:
        if not self._client:
            await self.connect()
        return self._client  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Core CRUD
    # ------------------------------------------------------------------

    async def get(self, namespace: str, key: str) -> Optional[CacheEntry]:
        """Return a ``CacheEntry`` if present, else ``None``."""
        t0 = time.time()
        try:
            r = await self._ensure_connected()
            redis_key = self._build_key(namespace, key)
            raw = await r.get(redis_key)

            if raw is None:
                self._metrics.misses += 1
                self._record_latency(t0)
                return None

            entry = CacheEntry.from_json(raw)
            entry.hit_count += 1

            # Persist incremented hit_count without resetting TTL
            remaining = await r.ttl(redis_key)
            if remaining > 0:
                await r.setex(redis_key, remaining, entry.to_json())

            self._metrics.hits += 1
            self._metrics.namespace_hits[namespace] += 1
            self._record_latency(t0)
            logger.debug("Cache HIT  %s", redis_key)
            return entry

        except Exception as exc:
            self._metrics.errors += 1
            logger.warning("Cache GET error for %s/%s: %s", namespace, key, exc)
            return None

    async def set(
        self,
        namespace: str,
        key: str,
        data: Any,
        ttl: Optional[int] = None,
        tags: Optional[list[str]] = None,
    ) -> bool:
        """Store *data* in cache, optionally tagged for group invalidation."""
        try:
            r = await self._ensure_connected()
            effective_ttl = ttl or NAMESPACE_TTLS.get(
                CacheNamespace(namespace),
                300,
            )
            redis_key = self._build_key(namespace, key)
            etag = self._make_etag(data)

            entry = CacheEntry(
                data=data,
                created_at=time.time(),
                ttl=effective_ttl,
                namespace=namespace,
                cache_key=key,
                etag=etag,
            )

            await r.setex(redis_key, effective_ttl, entry.to_json())

            # Register key under every supplied tag (SADD is idempotent)
            if tags:
                pipe = r.pipeline()
                for tag in tags:
                    tag_key = self._build_tag_key(tag)
                    pipe.sadd(tag_key, redis_key)
                    pipe.expire(tag_key, effective_ttl + 60)  # tag outlives entries slightly
                await pipe.execute()

            logger.debug("Cache SET  %s  ttl=%ds  tags=%s", redis_key, effective_ttl, tags)
            return True

        except Exception as exc:
            self._metrics.errors += 1
            logger.warning("Cache SET error for %s/%s: %s", namespace, key, exc)
            return False

    async def delete(self, namespace: str, key: str) -> bool:
        """Delete a single cache entry."""
        try:
            r = await self._ensure_connected()
            deleted = await r.delete(self._build_key(namespace, key))
            if deleted:
                self._metrics.invalidations += 1
            return bool(deleted)
        except Exception as exc:
            self._metrics.errors += 1
            logger.warning("Cache DELETE error: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Invalidation strategies
    # ------------------------------------------------------------------

    async def invalidate_by_tag(self, tag: str) -> int:
        """Delete all cache keys registered under *tag*. Returns count deleted."""
        try:
            r = await self._ensure_connected()
            tag_key = self._build_tag_key(tag)
            members = await r.smembers(tag_key)
            if not members:
                return 0

            pipe = r.pipeline()
            for member in members:
                pipe.delete(member)
            pipe.delete(tag_key)
            results = await pipe.execute()

            count = sum(1 for r_ in results[:-1] if r_)
            self._metrics.invalidations += count
            logger.info("Invalidated %d keys for tag '%s'", count, tag)
            return count

        except Exception as exc:
            self._metrics.errors += 1
            logger.warning("Tag invalidation error for '%s': %s", tag, exc)
            return 0

    async def invalidate_namespace(self, namespace: str) -> int:
        """Delete all cache entries in a namespace via SCAN (no KEYS)."""
        try:
            r = await self._ensure_connected()
            pattern = f"{PREFIX_CACHE}:{namespace}:*"
            count = 0
            cursor = 0

            while True:
                cursor, keys = await r.scan(cursor, match=pattern, count=200)
                if keys:
                    await r.delete(*keys)
                    count += len(keys)
                if cursor == 0:
                    break

            self._metrics.invalidations += count
            logger.info("Invalidated %d keys in namespace '%s'", count, namespace)
            return count

        except Exception as exc:
            self._metrics.errors += 1
            logger.warning("Namespace invalidation error: %s", exc)
            return 0

    async def invalidate_pattern(self, pattern: str) -> int:
        """Delete all keys matching an arbitrary glob pattern."""
        try:
            r = await self._ensure_connected()
            count = 0
            cursor = 0

            while True:
                cursor, keys = await r.scan(cursor, match=pattern, count=200)
                if keys:
                    await r.delete(*keys)
                    count += len(keys)
                if cursor == 0:
                    break

            self._metrics.invalidations += count
            return count
        except Exception as exc:
            self._metrics.errors += 1
            logger.warning("Pattern invalidation error: %s", exc)
            return 0

    # ------------------------------------------------------------------
    # Cache warming
    # ------------------------------------------------------------------

    def register_warmer(self, name: str, fn: Callable) -> None:
        """Register an async callable as a named cache warmer."""
        self._warming_registry[name] = fn
        logger.debug("Registered cache warmer: %s", name)

    async def warm(self, *names: str) -> dict[str, bool]:
        """
        Execute registered warmers by name.

        If *names* is empty all registered warmers are run.
        Returns a mapping of warmer_name -> success.
        """
        targets = names or tuple(self._warming_registry.keys())
        results: dict[str, bool] = {}

        for name in targets:
            fn = self._warming_registry.get(name)
            if fn is None:
                logger.warning("No warmer named '%s'", name)
                results[name] = False
                continue
            try:
                await fn(self)
                self._metrics.warm_ops += 1
                results[name] = True
                logger.info("Cache warmer '%s' completed", name)
            except Exception as exc:
                self._metrics.errors += 1
                results[name] = False
                logger.error("Cache warmer '%s' failed: %s", name, exc)

        return results

    async def warm_all_background(self) -> None:
        """Fire all warmers concurrently in the background."""
        tasks = [
            asyncio.create_task(self._run_warmer(name, fn))
            for name, fn in self._warming_registry.items()
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _run_warmer(self, name: str, fn: Callable) -> None:
        try:
            await fn(self)
            self._metrics.warm_ops += 1
            logger.info("Background warmer '%s' done", name)
        except Exception as exc:
            self._metrics.errors += 1
            logger.error("Background warmer '%s' failed: %s", name, exc)

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def get_metrics(self) -> dict:
        return self._metrics.to_dict()

    async def get_redis_info(self) -> dict:
        """Return selected Redis INFO fields relevant to caching."""
        try:
            r = await self._ensure_connected()
            info = await r.info("memory", "stats", "keyspace")
            return {
                "used_memory_human":     info.get("used_memory_human"),
                "maxmemory_human":       info.get("maxmemory_human"),
                "maxmemory_policy":      info.get("maxmemory_policy"),
                "keyspace_hits":         info.get("keyspace_hits"),
                "keyspace_misses":       info.get("keyspace_misses"),
                "evicted_keys":          info.get("evicted_keys"),
                "expired_keys":          info.get("expired_keys"),
                "connected_clients":     info.get("connected_clients"),
            }
        except Exception as exc:
            logger.warning("Redis INFO error: %s", exc)
            return {}

    async def flush_metrics_to_redis(self) -> None:
        """Persist in-memory metrics snapshot to Redis (for multi-process setups)."""
        try:
            r = await self._ensure_connected()
            metrics_key = f"{PREFIX_METRICS}:snapshot"
            await r.setex(metrics_key, 300, json.dumps(self._metrics.to_dict()))
        except Exception as exc:
            logger.warning("Metrics flush error: %s", exc)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    async def exists(self, namespace: str, key: str) -> bool:
        try:
            r = await self._ensure_connected()
            return bool(await r.exists(self._build_key(namespace, key)))
        except Exception:
            return False

    async def touch(self, namespace: str, key: str, extra_ttl: int = 60) -> bool:
        """Extend the TTL of an existing entry without re-fetching it."""
        try:
            r = await self._ensure_connected()
            redis_key = self._build_key(namespace, key)
            remaining = await r.ttl(redis_key)
            if remaining > 0:
                await r.expire(redis_key, remaining + extra_ttl)
                return True
            return False
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Module-level singleton (populated during app startup)
# ---------------------------------------------------------------------------

cache_manager = CacheManager()
