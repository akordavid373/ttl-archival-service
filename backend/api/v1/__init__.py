"""
API v1 - Legacy TTL Archival Service API

This version includes the original API endpoints and is maintained for backward compatibility.
"""

from fastapi import APIRouter

# Create v1 router
v1_router = APIRouter(prefix="/api/v1", tags=["api-v1"])

# Import and include all v1 sub-routers
from . import audit, search, config, data

v1_router.include_router(audit.audit_router, tags=["audit-v1"])
v1_router.include_router(search.router, tags=["search-v1"])
v1_router.include_router(config.router, tags=["config-v1"])
v1_router.include_router(data.router, tags=["data-v1"])

__all__ = ["v1_router"]
