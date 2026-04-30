# Migration Guide: v1 to v2

This guide provides detailed instructions for migrating from API v1 to v2.

## Overview

API v2 introduces significant enhancements while maintaining core functionality. This guide will help you migrate your applications smoothly.

## Migration Timeline

- **March 28, 2024**: v2 released
- **June 1, 2025**: v1 deprecated
- **December 1, 2025**: v1 sunset (no longer supported)

## Breaking Changes

### 1. Authentication

#### v1

```python
# Optional authentication
headers = {"Content-Type": "application/json"}
```

#### v2

```python
# Required authentication
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-api-token",
    "X-API-Version": "v2"
}
```

**Migration**: Add authentication headers to all requests.

### 2. Base URLs

#### v1

```python
BASE_URL = "https://api.example.com/api/v1"
```

#### v2

```python
BASE_URL = "https://api.example.com/api/v2"
```

**Migration**: Update base URLs in your application configuration.

### 3. Pagination

#### v1

```python
# Zero-based offset pagination
params = {
    "skip": 20,  # Skip first 20 items
    "limit": 10  # Return next 10 items
}
```

#### v2

```python
# One-based page pagination
params = {
    "page": 3,   # Page 3 (items 21-30)
    "limit": 10  # 10 items per page
}
```

**Migration**: Update pagination logic to use 1-based page numbers.

### 4. Response Format

#### v1 Archives Response

```json
{
  "id": 1,
  "original_data_id": "data_123",
  "data": "sample data",
  "policy_id": 1,
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### v2 Archives Response

```json
{
  "id": 1,
  "original_data_id": "data_123",
  "data": "sample data",
  "policy_id": 1,
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "tags": ["important", "user_data"],
  "priority": "normal",
  "size_bytes": 1024,
  "hash_value": "abc123",
  "access_count": 5,
  "last_accessed": "2024-01-15T10:30:00Z",
  "retention_days": 365,
  "days_until_expiry": 350,
  "metadata": { "source": "user_upload" }
}
```

**Migration**: Update response parsing to handle new fields.

### 5. Error Handling

#### v1 Error Response

```json
{
  "detail": "Archive not found"
}
```

#### v2 Error Response

```json
{
  "error": {
    "code": "ARCHIVE_NOT_FOUND",
    "message": "Archive not found",
    "details": {
      "archive_id": 123,
      "suggestion": "Check the archive ID and try again"
    },
    "timestamp": "2024-03-28T14:30:00Z",
    "request_id": "req_abc123"
  }
}
```

**Migration**: Update error handling to parse structured error objects.

## New Features in v2

### 1. Enhanced Search

#### v1 Basic Search

```python
response = requests.get(
    f"{BASE_URL}/search",
    params={"q": "user data"}
)
```

#### v2 Enhanced Search

```python
response = requests.post(
    f"{BASE_URL}/search",
    json={
        "query": "user data",
        "search_type": "semantic",  # fulltext, fuzzy, regex, semantic
        "filters": {
            "tags": ["important"],
            "priority": "high",
            "date_from": "2024-01-01"
        },
        "facets": ["tags", "priority"],
        "highlighting": True,
        "sort": [
            {"field": "created_at", "order": "desc"}
        ]
    }
)
```

### 2. Batch Operations

#### v1 (Individual Operations)

```python
for archive_data in archives:
    response = requests.post(
        f"{BASE_URL}/archives",
        json=archive_data
    )
```

#### v2 (Batch Operations)

```python
response = requests.post(
    f"{BASE_URL}/archives/batch",
    json={
        "archives": archives,
        "validate_all": True
    }
)
```

### 3. Webhooks

```python
# Create webhook
webhook = {
    "name": "Archive Events",
    "url": "https://your-app.com/webhook",
    "events": ["archive.created", "archive.expired"],
    "secret": "webhook-secret",
    "active": True
}

response = requests.post(
    f"{BASE_URL}/webhooks",
    json=webhook
)
```

### 4. Real-time Notifications

```python
# Create notification rule
rule = {
    "name": "High Priority Archives",
    "event_types": ["archive.created"],
    "conditions": {"priority": "high"},
    "channels": [
        {
            "type": "email",
            "config": {"recipients": ["admin@example.com"]}
        }
    ]
}

response = requests.post(
    f"{BASE_URL}/notifications/rules",
    json=rule
)
```

## Step-by-Step Migration

### Phase 1: Preparation (Week 1-2)

1. **Audit Current Usage**

   ```python
   # List all v1 endpoints used
   v1_endpoints = [
       "/api/v1/archives",
       "/api/v1/policies",
       "/api/v1/search",
       "/api/v1/audit"
   ]
   ```

2. **Set Up Authentication**

   ```python
   # Generate API tokens
   # Update configuration files
   # Test authentication
   ```

3. **Update Configuration**
   ```python
   # config.py
   API_VERSION = "v2"
   BASE_URL = "https://api.example.com/api/v2"
   API_TOKEN = "your-api-token"
   ```

### Phase 2: Core Migration (Week 3-4)

1. **Update Base Client**

   ```python
   class APIClient:
       def __init__(self, base_url, token):
           self.base_url = base_url
           self.headers = {
               "Authorization": f"Bearer {token}",
               "X-API-Version": "v2",
               "Content-Type": "application/json"
           }

       def request(self, method, endpoint, **kwargs):
           url = f"{self.base_url}{endpoint}"
           kwargs['headers'] = {**self.headers, **kwargs.get('headers', {})}
           return requests.request(method, url, **kwargs)
   ```

2. **Migrate Archives API**

   ```python
   # Old v1 method
   def create_archive_v1(data):
       return requests.post("/api/v1/archives", json=data)

   # New v2 method
   def create_archive_v2(data):
       # Add v2-specific fields
       v2_data = {
           **data,
           "tags": data.get("tags", []),
           "priority": data.get("priority", "normal"),
           "metadata": data.get("metadata", {})
       }
       return client.request("POST", "/archives", json=v2_data)
   ```

3. **Update Pagination**

   ```python
   # Old pagination logic
   def get_archives_v1(page=0, page_size=10):
       params = {"skip": page * page_size, "limit": page_size}
       return requests.get("/api/v1/archives", params=params)

   # New pagination logic
   def get_archives_v2(page=1, page_size=10):
       params = {"page": page, "limit": page_size}
       response = client.request("GET", "/archives", params=params)
       data = response.json()
       return data['items'], data['total']
   ```

### Phase 3: Enhanced Features (Week 5-6)

1. **Implement Enhanced Search**

   ```python
   def search_archives(query, filters=None):
       search_request = {
           "query": query,
           "search_type": "semantic",
           "filters": filters or {},
           "highlighting": True
       }
       response = client.request("POST", "/search", json=search_request)
       return response.json()
   ```

2. **Add Batch Operations**

   ```python
   def create_archives_batch(archives):
       batch_request = {
           "archives": archives,
           "validate_all": True
       }
       response = client.request("POST", "/archives/batch", json=batch_request)
       return response.json()
   ```

3. **Set Up Webhooks**
   ```python
   def create_webhook(name, url, events):
       webhook = {
           "name": name,
           "url": url,
           "events": events,
           "active": True
       }
       response = client.request("POST", "/webhooks", json=webhook)
       return response.json()
   ```

### Phase 4: Testing & Validation (Week 7-8)

1. **Unit Tests**

   ```python
   def test_archive_creation():
       # Test v2 archive creation
       data = {
           "original_data_id": "test_123",
           "data": "test data",
           "policy_id": 1,
           "tags": ["test"]
       }
       response = create_archive_v2(data)
       assert response.status_code == 201

       # Validate response format
       result = response.json()
       assert "tags" in result
       assert "priority" in result
   ```

2. **Integration Tests**

   ```python
   def test_end_to_end_workflow():
       # Create archive
       archive = create_archive_v2(test_data)

       # Search for archive
       search_results = search_archives("test")
       assert len(search_results['results']) > 0

       # Verify webhook notification
       # (mock webhook endpoint)
   ```

3. **Performance Testing**
   ```python
   def test_batch_performance():
       archives = [generate_test_data() for _ in range(100)]

       start_time = time.time()
       response = create_archives_batch(archives)
       end_time = time.time()

       assert response['success_count'] == 100
       assert end_time - start_time < 10  # Should complete in < 10 seconds
   ```

### Phase 5: Deployment (Week 9)

1. **Gradual Rollout**
   - Deploy v2 client to staging environment
   - Run comprehensive tests
   - Deploy to production with feature flags
   - Monitor for issues

2. **Monitoring**

   ```python
   # Monitor API response times
   # Track error rates
   # Watch deprecation warnings
   # Monitor webhook delivery
   ```

3. **Rollback Plan**
   - Keep v1 client code available
   - Monitor for critical issues
   - Have rollback procedure ready

## Code Examples

### Complete Migration Example

#### Before (v1)

```python
import requests

class ArchiveService:
    def __init__(self):
        self.base_url = "https://api.example.com/api/v1"

    def create_archive(self, data):
        response = requests.post(
            f"{self.base_url}/archives",
            json=data
        )
        return response.json()

    def get_archives(self, skip=0, limit=10):
        response = requests.get(
            f"{self.base_url}/archives",
            params={"skip": skip, "limit": limit}
        )
        return response.json()

    def search(self, query):
        response = requests.get(
            f"{self.base_url}/search",
            params={"q": query}
        )
        return response.json()
```

#### After (v2)

```python
import requests
from typing import List, Dict, Any

class ArchiveServiceV2:
    def __init__(self, api_token: str):
        self.base_url = "https://api.example.com/api/v2"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "X-API-Version": "v2",
            "Content-Type": "application/json"
        }

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        kwargs['headers'] = {**self.headers, **kwargs.get('headers', {})}
        return requests.request(method, url, **kwargs)

    def create_archive(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create archive with enhanced v2 features"""
        v2_data = {
            **data,
            "tags": data.get("tags", []),
            "priority": data.get("priority", "normal"),
            "metadata": data.get("metadata", {})
        }

        response = self._request("POST", "/archives", json=v2_data)
        response.raise_for_status()
        return response.json()

    def create_archives_batch(self, archives: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple archives in batch"""
        batch_request = {
            "archives": archives,
            "validate_all": True
        }

        response = self._request("POST", "/archives/batch", json=batch_request)
        response.raise_for_status()
        return response.json()

    def get_archives(self, page: int = 1, limit: int = 10, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get archives with pagination and filtering"""
        params = {"page": page, "limit": limit}
        if filters:
            params.update(filters)

        response = self._request("GET", "/archives", params=params)
        response.raise_for_status()
        return response.json()

    def search(self, query: str, search_type: str = "semantic", filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhanced search with multiple types and filters"""
        search_request = {
            "query": query,
            "search_type": search_type,
            "filters": filters or {},
            "highlighting": True
        }

        response = self._request("POST", "/search", json=search_request)
        response.raise_for_status()
        return response.json()

    def create_webhook(self, name: str, url: str, events: List[str]) -> Dict[str, Any]:
        """Create webhook for real-time notifications"""
        webhook = {
            "name": name,
            "url": url,
            "events": events,
            "active": True
        }

        response = self._request("POST", "/webhooks", json=webhook)
        response.raise_for_status()
        return response.json()
```

## Troubleshooting

### Common Migration Issues

1. **Authentication Errors**

   ```
   Error: 401 Unauthorized
   Solution: Verify API token and headers
   ```

2. **Version Not Supported**

   ```
   Error: 400 Unsupported API version
   Solution: Check X-API-Version header
   ```

3. **Pagination Issues**

   ```
   Error: Missing required parameter 'page'
   Solution: Update from skip/limit to page/limit
   ```

4. **Response Format Changes**
   ```
   Error: KeyError 'items'
   Solution: Update response parsing for v2 format
   ```

### Debug Tools

```python
# Test version negotiation
def test_version_negotiation():
    headers = {
        "X-API-Version": "v2",
        "Authorization": "Bearer token"
    }

    response = requests.get(
        "https://api.example.com/health",
        headers=headers
    )

    print("Response headers:")
    for header, value in response.headers.items():
        if 'api' in header.lower() or 'version' in header.lower():
            print(f"{header}: {value}")
```

## Support Resources

- **API Documentation**: `/docs` endpoint
- **Version Information**: `/version` endpoint
- **Migration Support**: Contact support team
- **Community Forum**: developer.example.com
- **Status Page**: status.example.com

## Checklist

- [ ] Audit current v1 usage
- [ ] Set up authentication
- [ ] Update base URLs and headers
- [ ] Migrate pagination logic
- [ ] Update response parsing
- [ ] Implement enhanced features
- [ ] Write comprehensive tests
- [ ] Deploy to staging
- [ ] Monitor production rollout
- [ ] Update documentation
- [ ] Train team on v2 features

## Timeline Summary

| Week | Activity                         |
| ---- | -------------------------------- |
| 1-2  | Preparation and setup            |
| 3-4  | Core API migration               |
| 5-6  | Enhanced features implementation |
| 7-8  | Testing and validation           |
| 9    | Production deployment            |
| 10+  | Optimization and monitoring      |

Remember: Start migration early to ensure smooth transition before v1 deprecation!
