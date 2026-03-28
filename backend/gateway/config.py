"""
API Gateway Configuration Module

Configuration management for the gateway components.
"""

import os
from typing import Dict, List, Optional, Any
from pydantic import BaseSettings, Field
from dataclasses import dataclass


class GatewaySettings(BaseSettings):
    """Main gateway configuration settings"""
    
    # Gateway basic settings
    gateway_host: str = Field(default="0.0.0.0", env="GATEWAY_HOST")
    gateway_port: int = Field(default=8080, env="GATEWAY_PORT")
    gateway_debug: bool = Field(default=False, env="GATEWAY_DEBUG")
    
    # Router settings
    router_timeout: int = Field(default=30, env="ROUTER_TIMEOUT")
    router_retries: int = Field(default=3, env="ROUTER_RETRIES")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    # Rate limiting settings
    rate_limit_redis_url: Optional[str] = Field(default=None, env="RATE_LIMIT_REDIS_URL")
    rate_limit_cache_ttl: int = Field(default=300, env="RATE_LIMIT_CACHE_TTL")
    
    # Authentication settings
    auth_cache_ttl: int = Field(default=300, env="AUTH_CACHE_TTL")
    jwt_secret_key: Optional[str] = Field(default=None, env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    
    # Transformation settings
    transformation_timeout: int = Field(default=10, env="TRANSFORMATION_TIMEOUT")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Default configuration for development
DEFAULT_SERVICES = [
    {
        "name": "archival-service",
        "endpoints": [
            {"url": "http://localhost:8000", "weight": 1}
        ],
        "load_balancing_strategy": "round_robin",
        "health_check_path": "/health",
        "health_check_interval": 30,
        "timeout": 30,
        "retries": 3
    }
]

DEFAULT_ROUTES = [
    {
        "path_prefix": "/api/",
        "service_name": "archival-service",
        "methods": ["*"],
        "priority": 100,
        "strip_prefix": False
    }
]

DEFAULT_RATE_LIMITS = [
    {
        "identifier": "default",
        "strategy": "sliding_window",
        "requests_per_window": 100,
        "window_size_seconds": 60,
        "key_extractors": ["ip"],
        "paths": ["/*"],
        "methods": ["*"],
        "priority": 0,
        "enabled": True
    },
    {
        "identifier": "authenticated_users",
        "strategy": "sliding_window",
        "requests_per_window": 1000,
        "window_size_seconds": 60,
        "key_extractors": ["user_id"],
        "paths": ["/*"],
        "methods": ["*"],
        "priority": 10,
        "enabled": True
    }
]

DEFAULT_AUTH_PROVIDERS = [
    {
        "name": "jwt_provider",
        "auth_type": "jwt",
        "strategy": "validate",
        "secret_key": None,  # Will be set from environment
        "algorithm": "HS256",
        "token_header": "Authorization",
        "token_prefix": "Bearer ",
        "cache_ttl": 300,
        "timeout": 10,
        "retries": 3,
        "enabled": True
    }
]

DEFAULT_AUTH_RULES = [
    {
        "name": "default_auth",
        "provider": "jwt_provider",
        "paths": ["/api/"],
        "methods": ["POST", "PUT", "DELETE"],
        "anonymous_allowed": True,
        "priority": 0,
        "enabled": True
    }
]


def get_gateway_settings() -> GatewaySettings:
    """Get gateway settings"""
    return GatewaySettings()


def get_default_services() -> List[Dict[str, Any]]:
    """Get default service configurations"""
    return DEFAULT_SERVICES


def get_default_routes() -> List[Dict[str, Any]]:
    """Get default route configurations"""
    return DEFAULT_ROUTES


def get_default_rate_limits() -> List[Dict[str, Any]]:
    """Get default rate limit configurations"""
    return DEFAULT_RATE_LIMITS


def get_default_auth_providers() -> List[Dict[str, Any]]:
    """Get default auth provider configurations"""
    providers = DEFAULT_AUTH_PROVIDERS.copy()
    
    # Set JWT secret key from environment if available
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    if jwt_secret:
        for provider in providers:
            if provider["auth_type"] == "jwt":
                provider["secret_key"] = jwt_secret
    
    return providers


def get_default_auth_rules() -> List[Dict[str, Any]]:
    """Get default auth rule configurations"""
    return DEFAULT_AUTH_RULES
