from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from ..config.security_config import get_security_settings

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to every HTTP response."""
    
    def __init__(self, app):
        super().__init__(app)
        self.settings = get_security_settings().headers

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Add basic security headers
        response.headers["X-Frame-Options"] = self.settings.x_frame_options
        response.headers["X-Content-Type-Options"] = self.settings.x_content_type_options
        response.headers["X-XSS-Protection"] = self.settings.x_xss_protection
        response.headers["Strict-Transport-Security"] = self.settings.strict_transport_security
        response.headers["Referrer-Policy"] = self.settings.referrer_policy
        
        # Build and add Content-Security-Policy header
        csp_header = "; ".join([f"{k} {v}" for k, v in self.settings.content_security_policy.items()])
        response.headers["Content-Security-Policy"] = csp_header
        
        return response
