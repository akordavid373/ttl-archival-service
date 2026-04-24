from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from ..utils.version_manager import VersionManager, VersionInfo

logger = logging.getLogger(__name__)


class VersioningMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle API versioning through URL paths and headers.
    Supports both URL-based and header-based versioning.
    """
    
    def __init__(self, app, version_manager: VersionManager):
        super().__init__(app)
        self.version_manager = version_manager
    
    async def dispatch(self, request: Request, call_next):
        # Determine the requested API version
        version = self._extract_version(request)
        
        # Validate version
        version_info = self.version_manager.get_version_info(version)
        if not version_info:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Unsupported API version",
                    "message": f"Version '{version}' is not supported",
                    "supported_versions": list(self.version_manager.get_supported_versions().keys()),
                    "latest_version": self.version_manager.get_latest_version()
                }
            )
        
        # Add version info to request state for later use
        request.state.api_version = version
        request.state.version_info = version_info
        
        # Process the request
        response = await call_next(request)
        
        # Add version headers to response
        self._add_version_headers(response, version_info)
        
        # Add deprecation warnings if applicable
        if version_info.deprecated:
            self._add_deprecation_headers(response, version_info)
        
        return response
    
    def _extract_version(self, request: Request) -> str:
        """
        Extract API version from URL path or headers.
        Priority: URL path > Accept header > Custom header > default
        """
        # 1. Try to extract from URL path (/api/v1/, /api/v2/, etc.)
        path_parts = request.url.path.strip('/').split('/')
        if len(path_parts) >= 2 and path_parts[0] == 'api':
            potential_version = path_parts[1]
            if potential_version.startswith('v') and potential_version[1:].isdigit():
                return potential_version
        
        # 2. Try custom version header
        api_version = request.headers.get("X-API-Version")
        if api_version:
            return api_version
        
        # 3. Try Accept header with version parameter
        accept_header = request.headers.get("Accept", "")
        if "version=" in accept_header:
            # Extract version from Accept header like: application/json; version=v1
            for part in accept_header.split(';'):
                part = part.strip()
                if part.startswith('version='):
                    return part.split('=')[1].strip()
        
        # 4. Return latest version as default
        return self.version_manager.get_latest_version()
    
    def _add_version_headers(self, response: Response, version_info: VersionInfo):
        """Add version-related headers to response"""
        response.headers["API-Version"] = version_info.version
        response.headers["API-Latest-Version"] = self.version_manager.get_latest_version()
        response.headers["API-Supported-Versions"] = ",".join(
            sorted(self.version_manager.get_supported_versions().keys())
        )
    
    def _add_deprecation_headers(self, response: Response, version_info: VersionInfo):
        """Add deprecation-related headers to response"""
        response.headers["Deprecation"] = "true"
        
        if version_info.deprecation_date:
            response.headers["Sunset"] = version_info.deprecation_date.isoformat()
        
        if version_info.migration_guide:
            response.headers["Link"] = f'<{version_info.migration_guide}>; rel="migration-guide"'
        
        # Add warning header for deprecated versions
        warning_message = (
            f"API version {version_info.version} is deprecated. "
            f"Please migrate to version {version_info.recommended_version}."
        )
        if version_info.deprecation_date:
            warning_message += f" This version will be removed on {version_info.deprecation_date.strftime('%Y-%m-%d')}."
        
        response.headers["Warning"] = f'299 - "{warning_message}"'


class VersionNegotiationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for content negotiation based on API versions.
    Handles version-specific request/response transformations.
    """
    
    def __init__(self, app, version_manager: VersionManager):
        super().__init__(app)
        self.version_manager = version_manager
    
    async def dispatch(self, request: Request, call_next):
        # Get version info from request state (set by VersioningMiddleware)
        version_info = getattr(request.state, 'version_info', None)
        
        if not version_info:
            # This shouldn't happen if VersioningMiddleware is properly configured
            return await call_next(request)
        
        # Process request with version-specific logic
        await self._process_request_versioning(request, version_info)
        
        # Get response
        response = await call_next(request)
        
        # Process response with version-specific logic
        response = await self._process_response_versioning(request, response, version_info)
        
        return response
    
    async def _process_request_versioning(self, request: Request, version_info: VersionInfo):
        """Process request with version-specific transformations"""
        # Add version-specific request processing here
        # For example, parameter validation, request body transformation, etc.
        
        # Store version info in request for use in endpoints
        request.state.version_info = version_info
    
    async def _process_response_versioning(
        self, 
        request: Request, 
        response: Response, 
        version_info: VersionInfo
    ) -> Response:
        """Process response with version-specific transformations"""
        # Add version-specific response processing here
        # For example, response body transformation, field filtering, etc.
        
        return response


class APIVersionRouter:
    """
    Helper class to manage version-specific route registration.
    """
    
    def __init__(self, version_manager: VersionManager):
        self.version_manager = version_manager
        self.versioned_routers = {}
    
    def register_router(self, version: str, router):
        """Register a router for a specific API version"""
        if version not in self.versioned_routers:
            self.versioned_routers[version] = []
        self.versioned_routers[version].append(router)
    
    def get_routers_for_version(self, version: str):
        """Get all routers registered for a specific version"""
        return self.versioned_routers.get(version, [])
    
    def get_all_routers(self):
        """Get all versioned routers as a dictionary"""
        return self.versioned_routers
