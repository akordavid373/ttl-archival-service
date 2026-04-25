"""
Configuration management system for TTL archival service.
Provides environment-based configuration with validation and dynamic updates.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Available log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    url: str = "sqlite:///./ttl_archival.db"
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    
    def __post_init__(self):
        if "sqlite" not in self.url:
            self.pool_size = int(os.getenv("DB_POOL_SIZE", self.pool_size))
            self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", self.max_overflow))
            self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", self.pool_timeout))
            self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", self.pool_recycle))
        self.echo = os.getenv("DB_ECHO", "false").lower() == "true"


@dataclass
class RedisConfig:
    """Redis configuration for caching."""
    url: str = "redis://localhost:6379/0"
    max_connections: int = 10
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True
    
    def __post_init__(self):
        self.url = os.getenv("REDIS_URL", self.url)
        self.max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", self.max_connections))
        self.socket_timeout = int(os.getenv("REDIS_SOCKET_TIMEOUT", self.socket_timeout))
        self.socket_connect_timeout = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", self.socket_connect_timeout))
        self.retry_on_timeout = os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower() == "true"


@dataclass
class StorageConfig:
    """Storage configuration for archives."""
    archive_path: str = "./archives"
    max_file_size_mb: int = 1024  # 1GB
    compression_enabled: bool = True
    encryption_enabled: bool = False
    backup_enabled: bool = True
    backup_retention_days: int = 30
    
    def __post_init__(self):
        self.archive_path = os.getenv("ARCHIVE_STORAGE_PATH", self.archive_path)
        self.max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", self.max_file_size_mb))
        self.compression_enabled = os.getenv("COMPRESSION_ENABLED", "true").lower() == "true"
        self.encryption_enabled = os.getenv("ENCRYPTION_ENABLED", "false").lower() == "true"
        self.backup_enabled = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
        self.backup_retention_days = int(os.getenv("BACKUP_RETENTION_DAYS", self.backup_retention_days))


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    def __post_init__(self):
        self.secret_key = os.getenv("SECRET_KEY", self.secret_key)
        self.algorithm = os.getenv("ALGORITHM", self.algorithm)
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", self.access_token_expire_minutes))
        self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", self.refresh_token_expire_days))
        self.password_min_length = int(os.getenv("PASSWORD_MIN_LENGTH", self.password_min_length))
        self.max_login_attempts = int(os.getenv("MAX_LOGIN_ATTEMPTS", self.max_login_attempts))
        self.lockout_duration_minutes = int(os.getenv("LOCKOUT_DURATION_MINUTES", self.lockout_duration_minutes))


@dataclass
class FeatureFlags:
    """Feature toggle configuration."""
    enable_search: bool = True
    enable_analytics: bool = True
    enable_audit_log: bool = True
    enable_scheduler: bool = True
    enable_notifications: bool = False
    enable_api_rate_limiting: bool = True
    enable_advanced_filters: bool = True
    
    def __post_init__(self):
        self.enable_search = os.getenv("ENABLE_SEARCH", "true").lower() == "true"
        self.enable_analytics = os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"
        self.enable_audit_log = os.getenv("ENABLE_AUDIT_LOG", "true").lower() == "true"
        self.enable_scheduler = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"
        self.enable_notifications = os.getenv("ENABLE_NOTIFICATIONS", "false").lower() == "true"
        self.enable_api_rate_limiting = os.getenv("ENABLE_API_RATE_LIMITING", "true").lower() == "true"
        self.enable_advanced_filters = os.getenv("ENABLE_ADVANCED_FILTERS", "true").lower() == "true"


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_size: int = 10
    
    def __post_init__(self):
        self.requests_per_minute = int(os.getenv("RATE_LIMIT_RPM", self.requests_per_minute))
        self.requests_per_hour = int(os.getenv("RATE_LIMIT_RPH", self.requests_per_hour))
        self.requests_per_day = int(os.getenv("RATE_LIMIT_RPD", self.requests_per_day))
        self.burst_size = int(os.getenv("RATE_LIMIT_BURST", self.burst_size))


@dataclass
class ExternalServiceConfig:
    """External service API configuration."""
    notification_service_url: Optional[str] = None
    notification_service_key: Optional[str] = None
    analytics_service_url: Optional[str] = None
    analytics_service_key: Optional[str] = None
    backup_service_url: Optional[str] = None
    backup_service_key: Optional[str] = None
    
    def __post_init__(self):
        self.notification_service_url = os.getenv("NOTIFICATION_SERVICE_URL")
        self.notification_service_key = os.getenv("NOTIFICATION_SERVICE_KEY")
        self.analytics_service_url = os.getenv("ANALYTICS_SERVICE_URL")
        self.analytics_service_key = os.getenv("ANALYTICS_SERVICE_KEY")
        self.backup_service_url = os.getenv("BACKUP_SERVICE_URL")
        self.backup_service_key = os.getenv("BACKUP_SERVICE_KEY")


@dataclass
class SchedulerConfig:
    """Scheduler configuration."""
    cleanup_interval_hours: int = 1
    backup_interval_hours: int = 24
    health_check_interval_minutes: int = 5
    max_worker_threads: int = 4
    
    def __post_init__(self):
        self.cleanup_interval_hours = int(os.getenv("CLEANUP_INTERVAL_HOURS", self.cleanup_interval_hours))
        self.backup_interval_hours = int(os.getenv("BACKUP_INTERVAL_HOURS", self.backup_interval_hours))
        self.health_check_interval_minutes = int(os.getenv("HEALTH_CHECK_INTERVAL_MINUTES", self.health_check_interval_minutes))
        self.max_worker_threads = int(os.getenv("MAX_WORKER_THREADS", self.max_worker_threads))


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: LogLevel = LogLevel.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size_mb: int = 10
    backup_count: int = 5
    enable_json_logs: bool = False
    
    def __post_init__(self):
        self.level = LogLevel(os.getenv("LOG_LEVEL", self.level.value))
        self.file_path = os.getenv("LOG_FILE_PATH")
        self.max_file_size_mb = int(os.getenv("LOG_MAX_FILE_SIZE_MB", self.max_file_size_mb))
        self.backup_count = int(os.getenv("LOG_BACKUP_COUNT", self.backup_count))
        self.enable_json_logs = os.getenv("ENABLE_JSON_LOGS", "false").lower() == "true"


@dataclass
class Settings:
    """Main application settings."""
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Configuration sections
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    features: FeatureFlags = field(default_factory=FeatureFlags)
    rate_limits: RateLimitConfig = field(default_factory=RateLimitConfig)
    external_services: ExternalServiceConfig = field(default_factory=ExternalServiceConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Runtime configuration
    config_version: str = "1.0.0"
    last_updated: Optional[datetime] = None
    config_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        self.environment = Environment(os.getenv("ENVIRONMENT", self.environment.value))
        self.debug = os.getenv("DEBUG", "false").lower() == "true" or self.environment == Environment.DEVELOPMENT
        self.host = os.getenv("HOST", self.host)
        self.port = int(os.getenv("PORT", self.port))
        self.workers = int(os.getenv("WORKERS", self.workers))
        self.config_version = os.getenv("CONFIG_VERSION", self.config_version)
        
        # Ensure storage directory exists
        Path(self.storage.archive_path).mkdir(parents=True, exist_ok=True)
        
        self.last_updated = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary (excluding secrets)."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, (DatabaseConfig, RedisConfig, StorageConfig, SecurityConfig, 
                                FeatureFlags, RateLimitConfig, ExternalServiceConfig, 
                                SchedulerConfig, LoggingConfig)):
                result[key] = value.__dict__.copy()
                # Remove sensitive fields
                if key == "security":
                    result[key].pop("secret_key", None)
                elif key == "external_services":
                    for service_key in ["notification_service_key", "analytics_service_key", "backup_service_key"]:
                        result[key].pop(service_key, None)
            else:
                result[key] = value
        return result
    
    def get_masked_dict(self) -> Dict[str, Any]:
        """Get settings dictionary with masked secrets for logging."""
        result = self.to_dict()
        if "security" in result and "secret_key" not in result["security"]:
            result["security"]["secret_key"] = "***MASKED***"
        
        if "external_services" in result:
            for key in ["notification_service_key", "analytics_service_key", "backup_service_key"]:
                if key not in result["external_services"]:
                    result["external_services"][key] = "***MASKED***" if result["external_services"].get(key.replace("_key", "_url")) else None
        
        return result
    
    def update_config(self, updates: Dict[str, Any], source: str = "manual") -> bool:
        """Update configuration dynamically."""
        try:
            # Store current config in history
            history_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "source": source,
                "previous_config": self.get_masked_dict()
            }
            self.config_history.append(history_entry)
            
            # Apply updates
            for section, values in updates.items():
                if hasattr(self, section) and isinstance(values, dict):
                    section_obj = getattr(self, section)
                    for key, value in values.items():
                        if hasattr(section_obj, key):
                            setattr(section_obj, key, value)
                        else:
                            logger.warning(f"Unknown config key: {section}.{key}")
                else:
                    logger.warning(f"Unknown config section: {section}")
            
            self.last_updated = datetime.utcnow()
            logger.info(f"Configuration updated from {source}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False
    
    def get_config_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get configuration change history."""
        return self.config_history[-limit:]


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment variables."""
    global settings
    settings = Settings()
    logger.info("Settings reloaded from environment")
    return settings
