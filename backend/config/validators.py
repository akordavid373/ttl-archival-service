"""
Configuration validation system for TTL archival service.
Provides comprehensive validation for all configuration settings.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Union, Callable
from urllib.parse import urlparse
from pathlib import Path
import ipaddress
from dataclasses import fields
from .settings import Settings, DatabaseConfig, RedisConfig, StorageConfig, SecurityConfig

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Configuration validation error."""
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"Validation failed for {field}: {message}")


class ValidationResult:
    """Validation result containing errors and warnings."""
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[str] = []
    
    def is_valid(self) -> bool:
        """Check if configuration is valid (no errors)."""
        return len(self.errors) == 0
    
    def add_error(self, field: str, message: str, value: Any = None):
        """Add a validation error."""
        self.errors.append(ValidationError(field, message, value))
    
    def add_warning(self, message: str):
        """Add a validation warning."""
        self.warnings.append(message)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            "valid": self.is_valid(),
            "errors": [{"field": e.field, "message": e.message, "value": e.value} for e in self.errors],
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }


class ConfigValidator:
    """Main configuration validator."""
    
    def __init__(self):
        self.validators = {
            "database": self._validate_database,
            "redis": self._validate_redis,
            "storage": self._validate_storage,
            "security": self._validate_security,
            "features": self._validate_features,
            "rate_limits": self._validate_rate_limits,
            "external_services": self._validate_external_services,
            "scheduler": self._validate_scheduler,
            "logging": self._validate_logging,
            "general": self._validate_general
        }
    
    def validate_settings(self, settings: Settings) -> ValidationResult:
        """Validate all settings."""
        result = ValidationResult()
        
        # Validate general settings first
        self._validate_general(settings, result)
        
        # Validate each configuration section
        for section_name, validator in self.validators.items():
            if section_name != "general" and hasattr(settings, section_name):
                try:
                    validator(getattr(settings, section_name), result)
                except Exception as e:
                    result.add_error(section_name, f"Validation failed: {str(e)}")
        
        return result
    
    def validate_config_update(self, updates: Dict[str, Any]) -> ValidationResult:
        """Validate configuration updates before applying."""
        result = ValidationResult()
        
        for section_name, section_data in updates.items():
            if section_name in self.validators:
                try:
                    # Create a temporary object for validation
                    temp_obj = self._create_temp_config_object(section_name, section_data)
                    self.validators[section_name](temp_obj, result)
                except Exception as e:
                    result.add_error(section_name, f"Validation failed: {str(e)}")
            else:
                result.add_warning(f"Unknown configuration section: {section_name}")
        
        return result
    
    def _create_temp_config_object(self, section: str, data: Dict[str, Any]) -> Any:
        """Create a temporary configuration object for validation."""
        config_classes = {
            "database": DatabaseConfig,
            "redis": RedisConfig,
            "storage": StorageConfig,
            "security": SecurityConfig,
        }
        
        if section in config_classes:
            return config_classes[section](**data)
        else:
            # For other sections, return a simple object
            class TempConfig:
                def __init__(self, **kwargs):
                    for k, v in kwargs.items():
                        setattr(self, k, v)
            return TempConfig(**data)
    
    def _validate_general(self, settings: Settings, result: ValidationResult):
        """Validate general application settings."""
        # Validate environment
        if not settings.environment.value in ["development", "testing", "staging", "production"]:
            result.add_error("environment", f"Invalid environment: {settings.environment.value}")
        
        # Validate port
        if not (1 <= settings.port <= 65535):
            result.add_error("port", f"Port must be between 1 and 65535, got: {settings.port}")
        
        # Validate workers
        if settings.workers < 1:
            result.add_error("workers", f"Workers must be at least 1, got: {settings.workers}")
        
        # Validate host
        try:
            ipaddress.ip_address(settings.host)
        except ValueError:
            if settings.host != "0.0.0.0" and settings.host != "localhost":
                # Check if it's a valid hostname
                if not re.match(r'^[a-zA-Z0-9.-]+$', settings.host):
                    result.add_error("host", f"Invalid host: {settings.host}")
    
    def _validate_database(self, db_config: DatabaseConfig, result: ValidationResult):
        """Validate database configuration."""
        if not db_config.url:
            result.add_error("database.url", "Database URL is required")
            return
        
        # Validate database URL format
        try:
            parsed = urlparse(db_config.url)
            if not parsed.scheme in ["sqlite", "postgresql", "mysql", "oracle"]:
                result.add_error("database.url", f"Unsupported database scheme: {parsed.scheme}")
        except Exception as e:
            result.add_error("database.url", f"Invalid database URL format: {str(e)}")
        
        # Validate connection pool settings
        if db_config.pool_size < 1:
            result.add_error("database.pool_size", f"Pool size must be at least 1, got: {db_config.pool_size}")
        
        if db_config.max_overflow < 0:
            result.add_error("database.max_overflow", f"Max overflow cannot be negative, got: {db_config.max_overflow}")
        
        if db_config.pool_timeout < 1:
            result.add_error("database.pool_timeout", f"Pool timeout must be at least 1, got: {db_config.pool_timeout}")
        
        if db_config.pool_recycle < 0:
            result.add_error("database.pool_recycle", f"Pool recycle cannot be negative, got: {db_config.pool_recycle}")
    
    def _validate_redis(self, redis_config: RedisConfig, result: ValidationResult):
        """Validate Redis configuration."""
        if not redis_config.url:
            result.add_warning("Redis URL not configured, caching will be disabled")
            return
        
        # Validate Redis URL format
        try:
            parsed = urlparse(redis_config.url)
            if parsed.scheme not in ["redis", "rediss"]:
                result.add_error("redis.url", f"Invalid Redis scheme: {parsed.scheme}")
            
            if parsed.hostname and not re.match(r'^[a-zA-Z0-9.-]+$', parsed.hostname):
                result.add_error("redis.url", f"Invalid Redis hostname: {parsed.hostname}")
                
        except Exception as e:
            result.add_error("redis.url", f"Invalid Redis URL format: {str(e)}")
        
        # Validate connection settings
        if redis_config.max_connections < 1:
            result.add_error("redis.max_connections", f"Max connections must be at least 1, got: {redis_config.max_connections}")
        
        if redis_config.socket_timeout < 1:
            result.add_error("redis.socket_timeout", f"Socket timeout must be at least 1, got: {redis_config.socket_timeout}")
        
        if redis_config.socket_connect_timeout < 1:
            result.add_error("redis.socket_connect_timeout", f"Socket connect timeout must be at least 1, got: {redis_config.socket_connect_timeout}")
    
    def _validate_storage(self, storage_config: StorageConfig, result: ValidationResult):
        """Validate storage configuration."""
        if not storage_config.archive_path:
            result.add_error("storage.archive_path", "Archive path is required")
            return
        
        # Validate archive path
        try:
            path = Path(storage_config.archive_path)
            if not path.exists():
                result.add_warning(f"Archive path does not exist: {storage_config.archive_path}")
            elif not path.is_dir():
                result.add_error("storage.archive_path", f"Archive path is not a directory: {storage_config.archive_path}")
        except Exception as e:
            result.add_error("storage.archive_path", f"Invalid archive path: {str(e)}")
        
        # Validate file size limit
        if storage_config.max_file_size_mb < 1:
            result.add_error("storage.max_file_size_mb", f"Max file size must be at least 1MB, got: {storage_config.max_file_size_mb}")
        
        if storage_config.max_file_size_mb > 10240:  # 10GB
            result.add_warning("storage.max_file_size_mb", "Very large file size limit may cause performance issues")
        
        # Validate backup retention
        if storage_config.backup_retention_days < 1:
            result.add_error("storage.backup_retention_days", f"Backup retention must be at least 1 day, got: {storage_config.backup_retention_days}")
        
        if storage_config.backup_retention_days > 365:
            result.add_warning("storage.backup_retention_days", "Very long backup retention may consume significant storage")
    
    def _validate_security(self, security_config: SecurityConfig, result: ValidationResult):
        """Validate security configuration."""
        # Validate secret key
        if not security_config.secret_key:
            result.add_error("security.secret_key", "Secret key is required")
        elif len(security_config.secret_key) < 32:
            result.add_error("security.secret_key", "Secret key must be at least 32 characters long")
        elif security_config.secret_key == "your-secret-key-here":
            result.add_error("security.secret_key", "Secret key must be changed from default value")
        
        # Validate algorithm
        if security_config.algorithm not in ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]:
            result.add_error("security.algorithm", f"Unsupported algorithm: {security_config.algorithm}")
        
        # Validate token expiration
        if security_config.access_token_expire_minutes < 1:
            result.add_error("security.access_token_expire_minutes", f"Access token expiration must be at least 1 minute, got: {security_config.access_token_expire_minutes}")
        
        if security_config.access_token_expire_minutes > 1440:  # 24 hours
            result.add_warning("security.access_token_expire_minutes", "Long access token expiration may be a security risk")
        
        if security_config.refresh_token_expire_days < 1:
            result.add_error("security.refresh_token_expire_days", f"Refresh token expiration must be at least 1 day, got: {security_config.refresh_token_expire_days}")
        
        # Validate password policy
        if security_config.password_min_length < 8:
            result.add_error("security.password_min_length", f"Password minimum length should be at least 8, got: {security_config.password_min_length}")
        
        # Validate login attempt limits
        if security_config.max_login_attempts < 1:
            result.add_error("security.max_login_attempts", f"Max login attempts must be at least 1, got: {security_config.max_login_attempts}")
        
        if security_config.lockout_duration_minutes < 1:
            result.add_error("security.lockout_duration_minutes", f"Lockout duration must be at least 1 minute, got: {security_config.lockout_duration_minutes}")
    
    def _validate_features(self, features, result: ValidationResult):
        """Validate feature flags."""
        # Feature flags should be boolean
        boolean_fields = ["enable_search", "enable_analytics", "enable_audit_log", 
                         "enable_scheduler", "enable_notifications", "enable_api_rate_limiting", 
                         "enable_advanced_filters"]
        
        for field in boolean_fields:
            if hasattr(features, field):
                value = getattr(features, field)
                if not isinstance(value, bool):
                    result.add_error(f"features.{field}", f"Feature flag must be boolean, got: {type(value).__name__}")
        
        # Check for logical dependencies
        if hasattr(features, 'enable_search') and features.enable_search:
            if hasattr(features, 'enable_advanced_filters') and not features.enable_advanced_filters:
                result.add_warning("Search is enabled but advanced filters are disabled")
    
    def _validate_rate_limits(self, rate_limits, result: ValidationResult):
        """Validate rate limiting configuration."""
        # Validate rate limit values
        if rate_limits.requests_per_minute < 1:
            result.add_error("rate_limits.requests_per_minute", f"Requests per minute must be at least 1, got: {rate_limits.requests_per_minute}")
        
        if rate_limits.requests_per_hour < rate_limits.requests_per_minute:
            result.add_error("rate_limits.requests_per_hour", f"Requests per hour must be >= requests per minute, got: {rate_limits.requests_per_hour}")
        
        if rate_limits.requests_per_day < rate_limits.requests_per_hour:
            result.add_error("rate_limits.requests_per_day", f"Requests per day must be >= requests per hour, got: {rate_limits.requests_per_day}")
        
        if rate_limits.burst_size < 1:
            result.add_error("rate_limits.burst_size", f"Burst size must be at least 1, got: {rate_limits.burst_size}")
        
        if rate_limits.burst_size > rate_limits.requests_per_minute:
            result.add_warning("rate_limits.burst_size", "Burst size larger than requests per minute may be ineffective")
    
    def _validate_external_services(self, external_services, result: ValidationResult):
        """Validate external service configuration."""
        service_configs = [
            ("notification_service_url", "notification_service_key"),
            ("analytics_service_url", "analytics_service_key"),
            ("backup_service_url", "backup_service_key")
        ]
        
        for url_field, key_field in service_configs:
            url = getattr(external_services, url_field, None)
            key = getattr(external_services, key_field, None)
            
            if url and not key:
                result.add_warning(f"{url_field} is configured but {key_field} is missing")
            elif key and not url:
                result.add_warning(f"{key_field} is configured but {url_field} is missing")
            elif url:
                # Validate URL format
                try:
                    parsed = urlparse(url)
                    if not parsed.scheme in ["http", "https"]:
                        result.add_error(url_field, f"Invalid URL scheme: {parsed.scheme}")
                    if not parsed.netloc:
                        result.add_error(url_field, f"Invalid URL: missing domain")
                except Exception as e:
                    result.add_error(url_field, f"Invalid URL format: {str(e)}")
    
    def _validate_scheduler(self, scheduler, result: ValidationResult):
        """Validate scheduler configuration."""
        if scheduler.cleanup_interval_hours < 1:
            result.add_error("scheduler.cleanup_interval_hours", f"Cleanup interval must be at least 1 hour, got: {scheduler.cleanup_interval_hours}")
        
        if scheduler.backup_interval_hours < 1:
            result.add_error("scheduler.backup_interval_hours", f"Backup interval must be at least 1 hour, got: {scheduler.backup_interval_hours}")
        
        if scheduler.health_check_interval_minutes < 1:
            result.add_error("scheduler.health_check_interval_minutes", f"Health check interval must be at least 1 minute, got: {scheduler.health_check_interval_minutes}")
        
        if scheduler.max_worker_threads < 1:
            result.add_error("scheduler.max_worker_threads", f"Max worker threads must be at least 1, got: {scheduler.max_worker_threads}")
        
        if scheduler.max_worker_threads > 32:
            result.add_warning("scheduler.max_worker_threads", "Very high worker thread count may cause performance issues")
    
    def _validate_logging(self, logging_config, result: ValidationResult):
        """Validate logging configuration."""
        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if logging_config.level.value not in valid_levels:
            result.add_error("logging.level", f"Invalid log level: {logging_config.level.value}")
        
        # Validate file path if specified
        if logging_config.file_path:
            try:
                path = Path(logging_config.file_path)
                parent_dir = path.parent
                if not parent_dir.exists():
                    result.add_warning(f"Log file parent directory does not exist: {parent_dir}")
            except Exception as e:
                result.add_error("logging.file_path", f"Invalid log file path: {str(e)}")
        
        # Validate file size
        if logging_config.max_file_size_mb < 1:
            result.add_error("logging.max_file_size_mb", f"Max file size must be at least 1MB, got: {logging_config.max_file_size_mb}")
        
        if logging_config.backup_count < 1:
            result.add_error("logging.backup_count", f"Backup count must be at least 1, got: {logging_config.backup_count}")


# Global validator instance
validator = ConfigValidator()


def validate_configuration(settings: Settings) -> ValidationResult:
    """Validate the complete configuration."""
    return validator.validate_settings(settings)


def validate_config_update(updates: Dict[str, Any]) -> ValidationResult:
    """Validate configuration updates."""
    return validator.validate_config_update(updates)
