from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from typing import Optional, Callable
import logging

from ..services.tenant_service import TenantService

logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware for multi-tenant request handling"""

    def __init__(self, app, tenant_service: TenantService):
        super().__init__(app)
        self.tenant_service = tenant_service

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        tenant_id = self._extract_tenant_id(request)

        request.state.tenant_id = tenant_id
        request.state.tenant_slug = self._extract_tenant_slug(request)

        if tenant_id:
            db = request.state.db if hasattr(request.state, "db") else None
            if db:
                is_active = await self.tenant_service.is_tenant_active(db, tenant_id)
                if not is_active:
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "Tenant is not active or does not exist"},
                    )

        response = await call_next(request)

        if tenant_id:
            response.headers["X-Tenant-ID"] = tenant_id

        return response

    def _extract_tenant_id(self, request: Request) -> Optional[str]:
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            return tenant_id

        tenant_slug = request.headers.get("X-Tenant-Slug")
        if tenant_slug:
            return tenant_slug

        path_parts = request.url.path.strip("/").split("/")
        if len(path_parts) >= 2 and path_parts[0] == "tenants":
            return path_parts[1]

        return None

    def _extract_tenant_slug(self, request: Request) -> Optional[str]:
        slug = request.headers.get("X-Tenant-Slug")
        if slug:
            return slug

        return None


class TenantContext:
    """Context for accessing current tenant in request handlers"""

    _current_tenant_id: Optional[str] = None
    _current_tenant_slug: Optional[str] = None

    @classmethod
    def set_tenant(cls, tenant_id: str, tenant_slug: Optional[str] = None):
        cls._current_tenant_id = tenant_id
        cls._current_tenant_slug = tenant_slug

    @classmethod
    def get_tenant_id(cls) -> Optional[str]:
        return cls._current_tenant_id

    @classmethod
    def get_tenant_slug(cls) -> Optional[str]:
        return cls._current_tenant_slug

    @classmethod
    def clear(cls):
        cls._current_tenant_id = None
        cls._current_tenant_slug = None


def get_current_tenant_id(request: Request) -> Optional[str]:
    """Get current tenant ID from request state"""
    if hasattr(request.state, "tenant_id"):
        return request.state.tenant_id
    return TenantContext.get_tenant_id()


def get_current_tenant_slug(request: Request) -> Optional[str]:
    """Get current tenant slug from request state"""
    if hasattr(request.state, "tenant_slug"):
        return request.state.tenant_slug
    return TenantContext.get_tenant_slug()


class TenantResourceGuard:
    """Guard for checking tenant resource quotas"""

    def __init__(self, tenant_service: TenantService):
        self.tenant_service = tenant_service

    async def check_quota(
        self, db, tenant_id: str, resource_type: str, required: int = 1
    ) -> tuple[bool, Optional[dict]]:
        """Check if tenant has required quota"""
        has_quota, resource = await self.tenant_service.check_resource_quota(
            db, tenant_id, resource_type, required
        )

        if not has_quota:
            return False, {
                "error": "quota_exceeded",
                "resource_type": resource_type,
                "quota_limit": resource.quota_limit if resource else 0,
                "quota_used": resource.quota_used if resource else 0,
                "required": required,
            }

        return True, None

    async def consume_quota(
        self, db, tenant_id: str, resource_type: str, amount: int = 1
    ) -> bool:
        """Consume quota after successful operation"""
        await self.tenant_service.increment_resource(
            db, tenant_id, resource_type, amount
        )
        return True
