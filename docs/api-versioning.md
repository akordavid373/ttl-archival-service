# API Versioning Guide

This document describes the API versioning strategy and implementation for the TTL Archival Service.

## Overview

The TTL Archival Service implements a comprehensive API versioning system that supports:
- Multiple active API versions
- Backward compatibility
- Graceful deprecation
- Migration support
- Version negotiation through URLs and headers

## Versioning Strategy

### Semantic Versioning

We follow semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes that require migration
- **MINOR**: New features that are backward compatible
- **PATCH**: Bug fixes and minor improvements

### Current Versions

#### v1 (Legacy)
- **Status**: Active but deprecated
- **Release Date**: January 1, 2024
- **Deprecation Date**: June 1, 2025
- **Sunset Date**: December 1, 2025
- **Backward Compatible**: Yes
- **Features**: Basic CRUD operations, audit logging, search, configuration management

#### v2 (Current)
- **Status**: Active
- **Release Date**: Current date
- **Backward Compatible**: No
- **Features**: Enhanced search, batch operations, real-time notifications, webhooks, advanced analytics

## Version Negotiation

### URL-Based Versioning

API versions can be specified in the URL path:

```bash
# v1 API (deprecated)
GET /api/v1/archives
POST /api/v1/policies

# v2 API (current)
GET /api/v2/archives
POST /api/v2/policies
```

### Header-Based Versioning

API versions can be specified using headers:

```bash
# Using X-API-Version header
GET /api/archives
Headers:
  X-API-Version: v2

# Using Accept header
GET /api/archives
Headers:
  Accept: application/json; version=v2
```

### Version Priority

The system uses the following priority for version detection:
1. URL path (`/api/v1/`, `/api/v2/`)
2. `X-API-Version` header
3. `Accept` header with version parameter
4. Default to latest stable version

## Deprecation Process

### Deprecation Timeline

1. **Announcement**: Deprecation announced 6 months before deprecation date
2. **Warning Period**: 3 months of deprecation warnings in responses
3. **Final Warning**: 1 month before sunset with increased warning frequency
4. **Sunset**: Version is no longer supported

### Deprecation Headers

When using deprecated versions, responses include deprecation headers:

```http
API-Version: v1
Deprecation: true
Sunset: Sat, 01 Dec 2025 00:00:00 GMT
Warning: 299 - "API version v1 is deprecated. Please migrate to version v2."
Link: </docs/migration/v1-to-v2>; rel="migration-guide"
```

## Migration Guide

### v1 to v2 Migration

#### Breaking Changes

1. **Response Format Changes**
   - v1: Simple response objects
   - v2: Enhanced response objects with additional metadata

2. **Authentication Requirements**
   - v1: Optional authentication
   - v2: Required authentication for most endpoints

3. **Pagination Parameters**
   - v1: `skip` and `limit`
   - v2: `page` and `limit` (1-based indexing)

4. **Error Response Format**
   - v1: Simple error messages
   - v2: Structured error objects with error codes

#### Migration Steps

1. **Update Base URLs**
   ```python
   # Old
   BASE_URL = "https://api.example.com/api/v1"
   
   # New
   BASE_URL = "https://api.example.com/api/v2"
   ```

2. **Update Authentication**
   ```python
   # Add required headers
   headers = {
       "Authorization": "Bearer your-token",
       "X-API-Version": "v2"
   }
   ```

3. **Update Pagination**
   ```python
   # Old
   params = {"skip": 20, "limit": 10}
   
   # New
   params = {"page": 3, "limit": 10}  # page 3 = items 21-30
   ```

4. **Handle Enhanced Responses**
   ```python
   # v2 responses include additional metadata
   response = api_call()
   data = response.json()
   
   # Handle new fields
   items = data['items']
   total = data['total']
   filters = data.get('filters', {})
   ```

### Code Examples

#### Archives API

```python
# v1 - Create archive
response = requests.post(
    "https://api.example.com/api/v1/archives",
    json={
        "original_data_id": "data_123",
        "data": "sample data",
        "policy_id": 1
    }
)

# v2 - Create archive with enhanced features
response = requests.post(
    "https://api.example.com/api/v2/archives",
    json={
        "original_data_id": "data_123",
        "data": "sample data",
        "policy_id": 1,
        "tags": ["important", "user_data"],
        "priority": "high",
        "metadata": {"source": "user_upload"}
    },
    headers={
        "Authorization": "Bearer token",
        "X-API-Version": "v2"
    }
)
```

#### Search API

```python
# v1 - Basic search
response = requests.get(
    "https://api.example.com/api/v1/search",
    params={"q": "user data"}
)

# v2 - Enhanced search with filters
response = requests.post(
    "https://api.example.com/api/v2/search",
    json={
        "query": "user data",
        "search_type": "semantic",
        "filters": {
            "tags": ["important"],
            "date_from": "2024-01-01"
        },
        "facets": ["tags", "priority"],
        "limit": 20
    }
)
```

## Best Practices

### Client Implementation

1. **Always specify version explicitly** in headers or URLs
2. **Handle deprecation warnings** and plan migrations
3. **Use version-specific error handling**
4. **Test against both versions** during migration
5. **Monitor deprecation timelines**

### Server Implementation

1. **Maintain backward compatibility** during deprecation period
2. **Provide clear migration documentation**
3. **Implement proper version negotiation**
4. **Add comprehensive deprecation warnings**
5. **Monitor version usage patterns**

## Version Information Endpoints

### Get Version Information

```bash
GET /version
```

Response:
```json
{
  "current_version": "v2",
  "supported_versions": ["v1", "v2"],
  "deprecated_versions": ["v1"],
  "recommended_version": "v2",
  "version_info": {
    "v1": {
      "status": "deprecated",
      "release_date": "2024-01-01",
      "deprecation_date": "2025-06-01",
      "backward_compatible": true,
      "features": ["Basic CRUD", "Audit logging", "Search"],
      "breaking_changes": []
    },
    "v2": {
      "status": "active",
      "release_date": "2024-03-28",
      "deprecation_date": null,
      "backward_compatible": false,
      "features": ["Enhanced search", "Batch operations", "Webhooks"],
      "breaking_changes": [
        "Changed response format",
        "Updated authentication",
        "Modified pagination"
      ]
    }
  }
}
```

### Health Check with Version Info

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-03-28T14:30:00Z",
  "version": "v2",
  "supported_versions": ["v1", "v2"]
}
```

## Troubleshooting

### Common Issues

1. **Version Not Supported**
   - Error: `400 Unsupported API version`
   - Solution: Check supported versions via `/version` endpoint

2. **Deprecation Warnings**
   - Warning: `API version v1 is deprecated`
   - Solution: Plan migration to v2

3. **Breaking Changes**
   - Error: `400 Invalid request format`
   - Solution: Update request format for v2

### Debug Version Negotiation

Use these headers to debug version selection:

```bash
curl -H "X-API-Version: v2" \
     -H "Accept: application/json; version=v2" \
     https://api.example.com/api/archives
```

Check response headers for version information:

```bash
curl -I https://api.example.com/api/archives
```

Look for:
- `API-Version`: Selected version
- `API-Supported-Versions`: All supported versions
- `Deprecation`: Deprecation status
- `Warning`: Deprecation warnings

## Support

For questions about API versioning and migration:

- **Documentation**: Check this guide and migration guides
- **Version Info**: Use `/version` endpoint for current status
- **Support**: Contact support team with version-specific questions
- **Community**: Join our developer community for discussions
