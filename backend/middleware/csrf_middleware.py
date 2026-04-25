import hmac
import hashlib
import secrets
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from ..config.security_config import get_security_settings

class CSRFMiddleware(BaseHTTPMiddleware):
    """Simple CSRF prevention middleware using a double-submit cookie pattern."""
    
    def __init__(self, app):
        super().__init__(app)
        self.settings = get_security_settings().csrf
        self.secret = self.settings.secret_key.encode()

    async def dispatch(self, request: Request, call_next) -> Response:
        if not self.settings.enabled:
            return await call_next(request)

        csrf_cookie = request.cookies.get(self.settings.cookie_name)
        
        # Ensure a CSRF token exists for the session
        new_token = None
        if not csrf_cookie:
            new_token = secrets.token_urlsafe(32)
            csrf_cookie = new_token

        # Check for non-safe methods
        if request.method not in self.settings.safe_methods:
            csrf_header = request.headers.get(self.settings.header_name)
            
            if not csrf_header or not csrf_cookie or not secrets.compare_digest(csrf_header, csrf_cookie):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF token validation failed"}
                )

        response = await call_next(request)
        
        # If we generated a new token, set it in the cookie
        if new_token:
            response.set_cookie(
                key=self.settings.cookie_name,
                value=new_token,
                httponly=self.settings.cookie_httponly,
                secure=self.settings.cookie_secure,
                samesite=self.settings.cookie_samesite
            )
            
        return response
