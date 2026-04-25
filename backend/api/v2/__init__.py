"""
API v2 - Enhanced TTL Archival Service API

This version includes:
- Enhanced search with filters
- Batch operations
- Real-time notifications
- Advanced analytics
- Improved error handling
- Rate limiting
- Webhook support
"""

from fastapi import APIRouter

# Create v2 router
v2_router = APIRouter(prefix="/api/v2", tags=["api-v2"])

# Import and include all v2 sub-routers
from . import archives, policies, audit, search, config, data, webhooks, notifications

v2_router.include_router(archives.router, prefix="/archives", tags=["archives-v2"])
v2_router.include_router(policies.router, prefix="/policies", tags=["policies-v2"])
v2_router.include_router(audit.router, prefix="/audit", tags=["audit-v2"])
v2_router.include_router(search.router, prefix="/search", tags=["search-v2"])
v2_router.include_router(config.router, prefix="/config", tags=["config-v2"])
v2_router.include_router(data.router, prefix="/data", tags=["data-v2"])
v2_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks-v2"])
v2_router.include_router(notifications.router, prefix="/notifications", tags=["notifications-v2"])

__all__ = ["v2_router"]
