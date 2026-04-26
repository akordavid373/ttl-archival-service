import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class SecurityHeadersConfig:
    """Configuration for HTTP Security Headers."""
    x_frame_options: str = "DENY"
    x_content_type_options: str = "nosniff"
    x_xss_protection: str = "1; mode=block"
    strict_transport_security: str = "max-age=31536000; includeSubDomains; preload"
    referrer_policy: str = "strict-origin-when-cross-origin"
    content_security_policy: Dict[str, str] = field(default_factory=lambda: {
        "default-src": "'self'",
        "img-src": "'self' data: https:",
        "script-src": "'self'",
        "style-src": "'self' 'unsafe-inline'",
        "connect-src": "'self' https:",
        "frame-ancestors": "'none'",
        "base-uri": "'self'",
        "form-action": "'self'",
    })

    def __post_init__(self):
        self.x_frame_options = os.getenv("SECURITY_X_FRAME_OPTIONS", self.x_frame_options)
        self.x_content_type_options = os.getenv("SECURITY_X_CONTENT_TYPE_OPTIONS", self.x_content_type_options)
        self.x_xss_protection = os.getenv("SECURITY_X_XSS_PROTECTION", self.x_xss_protection)
        self.strict_transport_security = os.getenv("SECURITY_HSTS", self.strict_transport_security)
        self.referrer_policy = os.getenv("SECURITY_REFERRER_POLICY", self.referrer_policy)

@dataclass
class CORSConfig:
    """Configuration for Cross-Origin Resource Sharing."""
    allow_origins: List[str] = field(default_factory=lambda: ["*"])
    allow_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
    allow_headers: List[str] = field(default_factory=lambda: ["*"])
    allow_credentials: bool = True
    max_age: int = 3600

    def __post_init__(self):
        origins = os.getenv("CORS_ALLOW_ORIGINS")
        if origins:
            self.allow_origins = [o.strip() for o in origins.split(",")]
        
        methods = os.getenv("CORS_ALLOW_METHODS")
        if methods:
            self.allow_methods = [m.strip() for m in methods.split(",")]
        
        headers = os.getenv("CORS_ALLOW_HEADERS")
        if headers:
            self.allow_headers = [h.strip() for h in headers.split(",")]
        
        self.allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
        self.max_age = int(os.getenv("CORS_MAX_AGE", self.max_age))

@dataclass
class CSRFConfig:
    """Configuration for Cross-Site Request Forgery protection."""
    enabled: bool = True
    secret_key: str = "your-fallback-secret-key-for-csrf-67890"
    cookie_name: str = "csrf_token"
    header_name: str = "X-CSRF-Token"
    cookie_httponly: bool = False
    cookie_secure: bool = True
    cookie_samesite: str = "lax"
    safe_methods: List[str] = field(default_factory=lambda: ["GET", "HEAD", "OPTIONS", "TRACE"])

    def __post_init__(self):
        self.enabled = os.getenv("CSRF_ENABLED", "true").lower() == "true"
        self.secret_key = os.getenv("CSRF_SECRET_KEY", self.secret_key)
        self.cookie_name = os.getenv("CSRF_COOKIE_NAME", self.cookie_name)
        self.header_name = os.getenv("CSRF_HEADER_NAME", self.header_name)
        self.cookie_httponly = os.getenv("CSRF_COOKIE_HTTPONLY", "false").lower() == "true"
        self.cookie_secure = os.getenv("CSRF_COOKIE_SECURE", "true").lower() == "true"
        self.cookie_samesite = os.getenv("CSRF_COOKIE_SAMESITE", self.cookie_samesite)

@dataclass
class SecuritySettings:
    """Main security settings instance."""
    headers: SecurityHeadersConfig = field(default_factory=SecurityHeadersConfig)
    cors: CORSConfig = field(default_factory=CORSConfig)
    csrf: CSRFConfig = field(default_factory=CSRFConfig)

# Global security settings instance
security_settings = SecuritySettings()

def get_security_settings() -> SecuritySettings:
    """Get the global security settings instance."""
    return security_settings
