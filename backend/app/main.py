"""
main.py – FastAPI application with caching wired in.

This file shows exactly how to integrate the caching layer into the
existing TTL Archival Service entry point.  Changes vs. the original
scaffold are marked with  # ← CACHE  comments.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ← CACHE: import the three caching components
from app.cache.manager import cache_manager
from app.cache.warming import CacheWarmingScheduler, register_all_warmers
from app.middleware.cache_middleware import CacheMiddleware

# Existing routers (unchanged)
# from app.api.routes import records, policies, analytics, blockchain, health

# ← CACHE: import the new cache management router
from app.api.routes.cache import router as cache_router

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan  (replaces on_event startup/shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # -----------------------------------------------------------------------
    # Startup
    # -----------------------------------------------------------------------
    logger.info("Starting TTL Archival Service…")

    # ← CACHE: connect to Redis
    await cache_manager.connect()

    # ← CACHE: register warmers and run them concurrently in the background
    register_all_warmers(cache_manager)
    await cache_manager.warm_all_background()

    # ← CACHE: start the scheduled re-warmer
    warming_scheduler = CacheWarmingScheduler(cache_manager)
    warming_scheduler.start()

    # Attach scheduler to app state so lifespan can stop it
    app.state.warming_scheduler = warming_scheduler

    yield  # ← application runs here

    # -----------------------------------------------------------------------
    # Shutdown
    # -----------------------------------------------------------------------
    logger.info("Shutting down TTL Archival Service…")

    # ← CACHE: flush in-memory metrics to Redis for observability
    await cache_manager.flush_metrics_to_redis()

    # ← CACHE: stop re-warmer and disconnect Redis
    app.state.warming_scheduler.stop()
    await cache_manager.disconnect()


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    app = FastAPI(
        title="TTL Archival Service",
        description="Full-stack TTL-aware archival service with blockchain integration",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS (unchanged from scaffold)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ← CACHE: add the cache middleware AFTER CORS so it wraps API routes
    #   Order matters: middlewares run in reverse registration order for requests.
    #   CORS → CacheMiddleware → route handler
    app.add_middleware(
        CacheMiddleware,
        vary_headers=["Accept-Encoding", "Accept"],
    )

    # Register existing routers (unchanged)
    # app.include_router(records.router,    prefix="/api/v1")
    # app.include_router(policies.router,   prefix="/api/v1")
    # app.include_router(analytics.router,  prefix="/api/v1")
    # app.include_router(blockchain.router, prefix="/api/v1")
    # app.include_router(health.router,     prefix="/api/v1")

    # ← CACHE: register cache management router
    app.include_router(cache_router)

    return app


app = create_app()
