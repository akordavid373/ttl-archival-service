# API Versioning Implementation

This document provides an overview of the API versioning implementation for the TTL Archival Service.

## 🚀 Features Implemented

### ✅ Core Versioning Features
- **URL-based versioning** (`/api/v1/`, `/api/v2/`)
- **Header-based versioning** (`X-API-Version`, `Accept` header)
- **Version negotiation middleware**
- **Semantic versioning support**
- **Backward compatibility**

### ✅ Deprecation & Migration
- **Deprecation headers** (`Deprecation`, `Sunset`, `Warning`)
- **Migration guide links** in response headers
- **Version-specific documentation**
- **Comprehensive migration guides**

### ✅ Enhanced v2 Features
- **Batch operations** for archives and policies
- **Enhanced search** with semantic, fuzzy, and regex options
- **Real-time notifications** with multiple channels
- **Webhooks** for event-driven architecture
- **Advanced filtering** and faceting
- **Improved error handling** with structured responses

## 📁 File Structure

```
backend/
├── api/
│   ├── v1/                    # Legacy API (copied from original)
│   │   ├── __init__.py
│   │   ├── audit.py
│   │   ├── config.py
│   │   ├── data.py
│   │   └── search.py
│   ├── v2/                    # Enhanced API with new features
│   │   ├── __init__.py
│   │   ├── archives.py        # Enhanced archive management
│   │   ├── policies.py        # Enhanced policy management
│   │   ├── audit.py          # Enhanced audit logging
│   │   ├── search.py        # Enhanced search capabilities
│   │   ├── config.py        # Enhanced configuration management
│   │   ├── data.py          # Data import/export/streaming
│   │   ├── webhooks.py      # Webhook management
│   │   └── notifications.py # Real-time notifications
│   ├── audit.py             # Original files (kept for reference)
│   ├── config.py
│   ├── data.py
│   └── search.py
├── middleware/
│   └── version_middleware.py # Version negotiation & headers
├── utils/
│   └── version_manager.py   # Version management & validation
└── main.py                  # Updated with versioning support

docs/
├── api-versioning.md        # Comprehensive versioning guide
└── migration/
    └── v1-to-v2.md         # Detailed migration guide
```

## 🔧 How It Works

### Version Detection Priority

1. **URL Path** (`/api/v1/`, `/api/v2/`)
2. **X-API-Version Header**
3. **Accept Header** (`application/json; version=v2`)
4. **Default** (latest stable version)

### Middleware Flow

```
Request → VersioningMiddleware → VersionNegotiationMiddleware → API Routes
                ↓                           ↓
         Version Detection         Version-Specific Processing
                ↓                           ↓
         Version Headers        Response Transformation
                ↓                           ↓
         Deprecation Warnings    Enhanced Features
```

### Version Manager

The `VersionManager` class handles:
- Version registration and validation
- Deprecation timeline management
- Compatibility checking
- Migration path determination
- Statistics and analytics

## 📊 Version Status

| Version | Status | Release Date | Deprecation | Sunset | Features |
|---------|--------|--------------|-------------|---------|----------|
| v1 | 🟡 Deprecated | 2024-01-01 | 2025-06-01 | 2025-12-01 | Basic CRUD, Audit, Search |
| v2 | 🟢 Active | 2024-03-28 | - | - | Enhanced features, Batch ops, Webhooks |

## 🧪 Testing the Implementation

### 1. Version Negotiation

```bash
# URL-based versioning
curl -H "Accept: application/json" http://localhost:8000/api/v1/archives
curl -H "Accept: application/json" http://localhost:8000/api/v2/archives

# Header-based versioning
curl -H "X-API-Version: v1" http://localhost:8000/archives
curl -H "X-API-Version: v2" http://localhost:8000/archives

# Accept header versioning
curl -H "Accept: application/json; version=v1" http://localhost:8000/archives
curl -H "Accept: application/json; version=v2" http://localhost:8000/archives
```

### 2. Version Information

```bash
# Get version information
curl http://localhost:8000/version

# Health check with version info
curl http://localhost:8000/health

# API version endpoint
curl http://localhost:8000/api/version
```

### 3. Deprecation Headers

```bash
# Check deprecation headers for v1
curl -I http://localhost:8000/api/v1/archives

# Expected headers:
# API-Version: v1
# Deprecation: true
# Sunset: Sat, 01 Dec 2025 00:00:00 GMT
# Warning: 299 - "API version v1 is deprecated..."
```

### 4. Enhanced v2 Features

```bash
# Batch archive creation
curl -X POST http://localhost:8000/api/v2/archives/batch \
  -H "Content-Type: application/json" \
  -d '{
    "archives": [
      {
        "original_data_id": "test_1",
        "data": "sample data 1",
        "policy_id": 1,
        "tags": ["test"]
      },
      {
        "original_data_id": "test_2", 
        "data": "sample data 2",
        "policy_id": 1,
        "priority": "high"
      }
    ],
    "validate_all": true
  }'

# Enhanced search
curl -X POST http://localhost:8000/api/v2/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "user data",
    "search_type": "semantic",
    "filters": {
      "tags": ["important"],
      "priority": "high"
    },
    "facets": ["tags", "priority"],
    "highlighting": true
  }'

# Create webhook
curl -X POST http://localhost:8000/api/v2/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Webhook",
    "url": "https://example.com/webhook",
    "events": ["archive.created", "archive.expired"],
    "active": true
  }'
```

## 🔄 Migration Process

### For API Consumers

1. **Update Base URLs**: Change from `/api/v1/` to `/api/v2/`
2. **Add Authentication**: Include `Authorization` and `X-API-Version` headers
3. **Update Pagination**: Change from `skip/limit` to `page/limit`
4. **Handle New Response Format**: Parse enhanced response objects
5. **Implement New Features**: Use batch operations, enhanced search, etc.

### For Developers

1. **Run Tests**: Ensure all versioning tests pass
2. **Update Documentation**: Keep version-specific docs current
3. **Monitor Usage**: Track version usage patterns
4. **Plan Deprecation**: Follow deprecation timeline for v1

## 📈 Monitoring & Analytics

### Version Usage Tracking

The version manager provides statistics:

```python
from backend.utils.version_manager import version_manager

# Get version statistics
stats = version_manager.get_version_statistics()
print(f"Total versions: {stats['total_versions']}")
print(f"Active versions: {stats['active_versions']}")
print(f"Deprecated versions: {stats['deprecated_versions']}")

# Get versions needing migration soon
upcoming = version_manager.get_versions_needing_migration(days_ahead=30)
print(f"Versions degrading soon: {list(upcoming.keys())}")
```

### Health Check Integration

The health check endpoint includes version information:

```json
{
  "status": "healthy",
  "timestamp": "2024-03-28T14:30:00Z",
  "version": "v2",
  "supported_versions": ["v1", "v2"]
}
```

## 🛡️ Security Considerations

### Authentication
- v2 requires authentication for most endpoints
- API tokens should be securely stored
- Consider rate limiting per version

### Deprecation Security
- Deprecated versions may have reduced security features
- Encourage migration to latest version for security updates
- Monitor for abuse of deprecated endpoints

## 🔮 Future Enhancements

### Planned Features
1. **v3 API Development**: Next major version with breaking changes
2. **Automatic Migration Tools**: Scripts to help migrate v1 to v2
3. **Version Analytics Dashboard**: Real-time usage monitoring
4. **API Gateway Integration**: Advanced routing and rate limiting
5. **Feature Flags**: Gradual feature rollout per version

### Extension Points
- Custom version negotiation strategies
- Additional deprecation policies
- Enhanced validation rules
- Custom transformation pipelines

## 📞 Support

### Documentation
- **API Versioning Guide**: `docs/api-versioning.md`
- **Migration Guide**: `docs/migration/v1-to-v2.md`
- **API Documentation**: Available at `/docs` endpoint

### Endpoints
- **Version Info**: `/version`
- **Health Check**: `/health`
- **API Version**: `/api/version`

### Troubleshooting
- Check response headers for version information
- Use `/version` endpoint to verify supported versions
- Monitor deprecation warnings in responses
- Review migration guides for breaking changes

## 🎯 Success Metrics

### Implementation Success
- ✅ Multiple API versions working
- ✅ Version negotiation functioning
- ✅ Deprecation warnings appearing
- ✅ Documentation is version-specific
- ✅ Migration is smooth

### Operational Success
- 📊 Version usage monitoring
- 🔄 Smooth deprecation process
- 📈 Migration rate tracking
- 🛡️ Security maintenance
- 📚 Documentation completeness

---

**Implementation Complete**: All acceptance criteria have been met. The API versioning system is ready for production use with comprehensive documentation, migration guides, and enhanced v2 features.
