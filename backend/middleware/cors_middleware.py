from fastapi.middleware.cors import CORSMiddleware
from ..config.security_config import get_security_settings

def add_cors_middleware(app):
    """Adds configured CORSMiddleware to the FastAPI application."""
    cors_settings = get_security_settings().cors
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_settings.allow_origins,
        allow_credentials=cors_settings.allow_credentials,
        allow_methods=cors_settings.allow_methods,
        allow_headers=cors_settings.allow_headers,
        max_age=cors_settings.max_age,
    )
