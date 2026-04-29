"""
Cache Warming Strategies

Pre-loads the most frequently accessed data into Redis on startup (or on
demand) so the first real requests are served from cache rather than
hitting the database cold.

Each warmer is a plain async function that accepts a ``CacheManager``
instance and populates it.  Register with::

    cache_manager.register_warmer("records_list", warm_records_list)

Then trigger on startup::

    await cache_manager.warm_all_background()
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from app.cache.manager import CacheManager

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Domain-specific warm functions
# ---------------------------------------------------------------------------

async def warm_active_policies(cache: "CacheManager", db_session_factory=None) -> None:
    """
    Pre-loads active archival policies.

    In a real implementation *db_session_factory* is injected from the DI
    container; here we generate representative placeholder data so the
    warmer runs in isolation (useful for integration tests and dev startup).
    """
    logger.info("[warmer] Warming active policies…")
    placeholder_policies = [
        {"id": 1, "name": "Default 30-day", "ttl_days": 30, "active": True},
        {"id": 2, "name": "Compliance 90-day", "ttl_days": 90, "active": True},
        {"id": 3, "name": "Short-term 7-day",  "ttl_days": 7,  "active": True},
    ]

    if db_session_factory:
        # Replace with real DB query:
        # async with db_session_factory() as session:
        #     rows = await session.execute(select(Policy).where(Policy.active == True))
        #     placeholder_policies = [r.to_dict() for r in rows.scalars()]
        pass

    for policy in placeholder_policies:
        await cache.set(
            namespace="policies",
            key=f"policy:{policy['id']}",
            data=policy,
            ttl=600,
            tags=["policies", f"policies:{policy['id']}"],
        )

    # Also warm the list endpoint
    await cache.set(
        namespace="policies",
        key="policies:list:active",
        data={"items": placeholder_policies, "total": len(placeholder_policies)},
        ttl=600,
        tags=["policies"],
    )
    logger.info("[warmer] Active policies warmed (%d items)", len(placeholder_policies))


async def warm_recent_records(cache: "CacheManager", db_session_factory=None) -> None:
    """Pre-loads the most recently created archival records (page 1)."""
    logger.info("[warmer] Warming recent records…")
    placeholder_records = [
        {
            "id": f"rec-{i}",
            "name": f"Record {i}",
            "status": "active",
            "ttl_expires_at": "2026-05-01T00:00:00Z",
        }
        for i in range(1, 11)
    ]

    await cache.set(
        namespace="records",
        key="records:list:page=1&per_page=10",
        data={"items": placeholder_records, "total": 10, "page": 1},
        ttl=300,
        tags=["records"],
    )
    logger.info("[warmer] Recent records warmed")


async def warm_analytics_summary(cache: "CacheManager", db_session_factory=None) -> None:
    """Pre-loads the dashboard analytics summary."""
    logger.info("[warmer] Warming analytics summary…")
    placeholder_summary = {
        "total_records":   1_024,
        "active_records":    980,
        "archived_records":   44,
        "expiring_soon":      12,
        "storage_used_gb":   3.7,
        "last_updated":   "2026-04-29T00:00:00Z",
    }

    await cache.set(
        namespace="analytics",
        key="analytics:summary",
        data=placeholder_summary,
        ttl=120,
        tags=["analytics"],
    )
    logger.info("[warmer] Analytics summary warmed")


async def warm_blockchain_status(cache: "CacheManager", blockchain_client=None) -> None:
    """Pre-loads Stellar network status to avoid cold calls on the blockchain layer."""
    logger.info("[warmer] Warming blockchain status…")
    placeholder_status = {
        "network": "testnet",
        "latest_ledger": 49_000_000,
        "fee_charged": 100,
        "healthy": True,
    }

    if blockchain_client:
        try:
            # placeholder_status = await blockchain_client.get_network_status()
            pass
        except Exception as exc:
            logger.warning("[warmer] Blockchain status fetch failed, using placeholder: %s", exc)

    await cache.set(
        namespace="blockchain",
        key="blockchain:status",
        data=placeholder_status,
        ttl=900,
        tags=["blockchain"],
    )
    logger.info("[warmer] Blockchain status warmed")


async def warm_health_check(cache: "CacheManager") -> None:
    """Prime the health-check response so the first probe is instant."""
    await cache.set(
        namespace="health",
        key="health:ping",
        data={"status": "ok", "cache": "warm"},
        ttl=30,
        tags=["health"],
    )


# ---------------------------------------------------------------------------
# Scheduled re-warming  (plug into APScheduler / Celery Beat)
# ---------------------------------------------------------------------------

class CacheWarmingScheduler:
    """
    Thin wrapper that wires warmers to a periodic schedule.

    Usage (inside FastAPI lifespan)::

        scheduler = CacheWarmingScheduler(cache_manager)
        scheduler.start()
        ...
        scheduler.stop()
    """

    def __init__(self, cache: "CacheManager") -> None:
        self._cache = cache
        self._scheduler: Optional[Any] = None

    def start(self) -> None:
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
        except ImportError:
            logger.warning("apscheduler not installed; scheduled re-warming disabled")
            return

        self._scheduler = AsyncIOScheduler()

        # Re-warm policies every 9 minutes (just before 10-min TTL expires)
        self._scheduler.add_job(
            self._warm("active_policies"), "interval", minutes=9, id="warm_policies"
        )
        # Re-warm records every 4 minutes
        self._scheduler.add_job(
            self._warm("recent_records"), "interval", minutes=4, id="warm_records"
        )
        # Re-warm analytics every 90 seconds
        self._scheduler.add_job(
            self._warm("analytics_summary"), "interval", seconds=90, id="warm_analytics"
        )
        # Re-warm blockchain every 14 minutes
        self._scheduler.add_job(
            self._warm("blockchain_status"), "interval", minutes=14, id="warm_blockchain"
        )

        self._scheduler.start()
        logger.info("Cache warming scheduler started")

    def stop(self) -> None:
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)

    def _warm(self, name: str):
        async def _inner():
            await self._cache.warm(name)
        return _inner


# ---------------------------------------------------------------------------
# Register all warmers onto the shared cache_manager
# ---------------------------------------------------------------------------

def register_all_warmers(cache: "CacheManager") -> None:
    """Call once during application startup."""
    cache.register_warmer("active_policies",   warm_active_policies)
    cache.register_warmer("recent_records",    warm_recent_records)
    cache.register_warmer("analytics_summary", warm_analytics_summary)
    cache.register_warmer("blockchain_status", warm_blockchain_status)
    cache.register_warmer("health_check",      warm_health_check)
    logger.info("All cache warmers registered")
