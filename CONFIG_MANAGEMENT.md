# Configuration Management System

This document describes the comprehensive configuration management system implemented for the TTL archival service.

## Overview

The configuration management system provides:

- **Environment-based configuration**: Load settings from environment variables with sensible defaults
- **Configuration validation**: Comprehensive validation of all configuration settings
- **Dynamic configuration updates**: Runtime configuration updates without service restart
- **Configuration versioning**: Track configuration changes with history and rollback capability
- **Secure secret management**: Encrypted storage and retrieval of sensitive data
- **Feature flags**: Runtime feature toggles
- **Rate limiting**: Configurable rate limits per endpoint
- **External service configuration**: Secure management of third-party service credentials

## Architecture

### Components

1. **Settings (`backend/config/settings.py`)**
   - Central configuration classes for all application settings
   - Environment variable loading with type conversion
   - Configuration section organization (database, security, features, etc.)

2. **Validators (`backend/config/validators.py`)**
   - Comprehensive validation for all configuration settings
   - Error and warning reporting
   - Pre-update validation for dynamic changes

3. **Configuration Service (`backend/services/config_service.py`)**
   - Dynamic configuration management
   - Configuration history tracking
   - Export/import functionality
   - Subscription system for configuration changes

4. **Secret Manager (`backend/utils/secret_manager.py`)**
   - Encrypted storage of secrets
   - Key rotation and backup capabilities
   - Access tracking and audit logging

5. **Configuration API (`backend/api/config.py`)**
   - RESTful endpoints for configuration management
   - Secret management endpoints
   - Health check and metrics endpoints

## Configuration Sections

### Database Configuration
```python
@dataclass
class DatabaseConfig:
    url: str = "sqlite:///./ttl_archival.db"
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
```

### Security Configuration
```python
@dataclass
class SecurityConfig:
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
```

### Feature Flags
```python
@dataclass
class FeatureFlags:
    enable_search: bool = True
    enable_analytics: bool = True
    enable_audit_log: bool = True
    enable_scheduler: bool = True
    enable_notifications: bool = False
    enable_api_rate_limiting: bool = True
    enable_advanced_filters: bool = True
```

### Rate Limiting
```python
@dataclass
class RateLimitConfig:
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_size: int = 10
```

## Environment Variables

See `.env.example` for all available environment variables. Key variables include:

### Application
- `ENVIRONMENT`: Application environment (development, testing, staging, production)
- `DEBUG`: Enable debug mode
- `HOST`: Server host
- `PORT`: Server port
- `WORKERS`: Number of worker processes

### Database
- `DATABASE_URL`: Database connection string
- `DB_POOL_SIZE`: Database connection pool size
- `DB_MAX_OVERFLOW`: Maximum pool overflow
- `DB_ECHO`: Enable SQL query logging

### Security
- `SECRET_KEY`: JWT signing secret
- `ALGORITHM`: JWT algorithm
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

### Features
- `ENABLE_SEARCH`: Enable search functionality
- `ENABLE_ANALYTICS`: Enable analytics
- `ENABLE_AUDIT_LOG`: Enable audit logging
- `ENABLE_SCHEDULER`: Enable background scheduler

## API Endpoints

### Configuration Management

#### Get Current Configuration
```http
GET /api/v1/config/current?include_secrets=false
```

#### Update Configuration
```http
POST /api/v1/config/update
Content-Type: application/json

{
  "updates": {
    "features": {
      "enable_search": false
    }
  },
  "validate_first": true
}
```

#### Get Configuration Section
```http
GET /api/v1/config/section/{section_name}?include_secrets=false
```

#### Reset Configuration Section
```http
POST /api/v1/config/reset/{section_name}
```

#### Rollback Configuration
```http
POST /api/v1/config/rollback?version={version}&steps_back=1
```

#### Get Configuration History
```http
GET /api/v1/config/history?limit=50&include_details=false
```

#### Validate Configuration Updates
```http
POST /api/v1/config/validate
Content-Type: application/json

{
  "database": {
    "pool_size": 10
  }
}
```

### Feature Flags

#### Get Feature Flags
```http
GET /api/v1/config/features
```

#### Update Feature Flags
```http
POST /api/v1/config/features
Content-Type: application/json

{
  "enable_search": false,
  "enable_notifications": true
}
```

### Secret Management

#### Store Secret
```http
POST /api/v1/config/secrets
Content-Type: application/json

{
  "key": "api_key",
  "value": "secret_value",
  "description": "External API key"
}
```

#### Get Secret
```http
GET /api/v1/config/secrets/{key}
```

#### List Secrets
```http
GET /api/v1/config/secrets?include_values=false
```

#### Delete Secret
```http
DELETE /api/v1/config/secrets/{key}
```

### System Information

#### Export Configuration
```http
POST /api/v1/config/export?include_secrets=false
```

#### Get Metrics
```http
GET /api/v1/config/metrics
```

#### Health Check
```http
GET /api/v1/config/health
```

## Usage Examples

### Python Code

```python
from backend.config.settings import get_settings
from backend.services.config_service import config_service
from backend.utils.secret_manager import secret_manager

# Get current settings
settings = get_settings()
print(f"Database URL: {settings.database.url}")

# Update configuration dynamically
result = config_service.update_config({
    "features": {"enable_search": False}
}, source="code_update")

if result["success"]:
    print("Configuration updated successfully")

# Store a secret
secret_manager.store_secret(
    key="external_api_key",
    value="secret123",
    description="External service API key"
)

# Retrieve a secret
api_key = secret_manager.get_secret("external_api_key")
```

### Environment-based Configuration

```bash
# Set environment variables
export ENVIRONMENT=production
export DATABASE_URL=postgresql://user:pass@localhost/ttl_archival
export SECRET_KEY=your-production-secret-key
export ENABLE_ANALYTICS=true

# Run the application
python -m backend.main
```

### Configuration Validation

```python
from backend.config.validators import validate_configuration

settings = get_settings()
validation_result = validate_configuration(settings)

if not validation_result.is_valid():
    print("Configuration errors:")
    for error in validation_result.errors:
        print(f"  {error.field}: {error.message}")
else:
    print("Configuration is valid")
```

## Security Considerations

### Secret Management
- All secrets are encrypted using Fernet symmetric encryption
- Master key is derived from environment variable or generated file
- Secret access is tracked with audit logging
- Secrets can be rotated and backed up securely

### Configuration Security
- Sensitive values are masked in logs and exports
- Configuration changes require validation
- History tracking enables audit trails
- Rollback capability for quick recovery

### Access Control
- API endpoints should be protected with authentication
- User tracking for configuration changes
- Role-based access for sensitive operations

## Best Practices

### Environment Configuration
1. Use different configurations for each environment
2. Never commit secrets to version control
3. Use environment-specific .env files
4. Validate configuration on startup

### Secret Management
1. Rotate secrets regularly
2. Use strong master keys
3. Backup secrets securely
4. Monitor secret access

### Configuration Updates
1. Validate changes before applying
2. Test in non-production environments first
3. Monitor for configuration errors
4. Keep configuration history

## Troubleshooting

### Common Issues

#### Configuration Validation Errors
```python
# Check validation result
validation_result = validate_configuration(settings)
for error in validation_result.errors:
    print(f"Error in {error.field}: {error.message}")
```

#### Secret Manager Issues
```python
# Check secret manager health
health = secret_manager.health_check()
if health["status"] != "healthy":
    print(f"Secret manager issue: {health.get('error')}")
```

#### Configuration Service Issues
```python
# Check configuration service health
health = config_service.health_check()
if health["status"] != "healthy":
    print(f"Config service issue: {health.get('error')}")
```

### Debug Mode
Enable debug mode for detailed logging:
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## Migration from Old Configuration

To migrate from the old configuration system:

1. Update environment variables to match new format
2. Update code to use new configuration classes
3. Test configuration validation
4. Verify secret management setup

### Migration Steps

1. **Update Environment Variables**
   ```bash
   # Old format
   DATABASE_URL=sqlite:///./ttl_archival.db
   
   # New format (same variable, but more options available)
   DATABASE_URL=postgresql://user:pass@localhost/ttl_archival
   DB_POOL_SIZE=10
   DB_MAX_OVERFLOW=20
   ```

2. **Update Code**
   ```python
   # Old approach
   import os
   database_url = os.getenv("DATABASE_URL")
   
   # New approach
   from backend.config.settings import get_settings
   settings = get_settings()
   database_url = settings.database.url
   ```

3. **Validate Configuration**
   ```python
   from backend.config.validators import validate_configuration
   settings = get_settings()
   validation_result = validate_configuration(settings)
   assert validation_result.is_valid()
   ```

## Testing

Run the configuration system tests:

```bash
cd backend
python test_config_system.py
```

The test suite validates:
- Settings initialization
- Configuration validation
- Dynamic updates
- Secret management
- History tracking
- Feature flags
- Export/import functionality
- Health checks
- Error handling

## Performance Considerations

- Configuration is cached for 5 minutes to reduce database load
- Secret encryption/decryption uses efficient symmetric encryption
- Configuration updates are validated before application
- History is limited to prevent excessive storage growth

## Future Enhancements

Potential future improvements:
- Configuration templates for different deployment types
- Integration with external secret managers (AWS Secrets Manager, Azure Key Vault)
- Configuration change notifications (webhooks, email)
- Advanced configuration validation rules
- Configuration dependency management
- Multi-tenant configuration support
