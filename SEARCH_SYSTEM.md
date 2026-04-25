# Search and Indexing System

This document describes the comprehensive search and indexing system implemented for the TTL archival service.

## Overview

The search system provides full-text search capabilities, faceted search, autocomplete, search suggestions, and comprehensive analytics for the archival service. It uses Elasticsearch as the search engine and provides both REST API endpoints and Python services for integration.

## Features

### Core Search Features
- **Full-text search**: Advanced text search with relevance scoring
- **Faceted search**: Filter and aggregate search results by various fields
- **Auto-complete**: Real-time suggestions as users type
- **Search suggestions**: Historical query-based suggestions
- **Advanced filtering**: Complex filter combinations with multiple operators
- **Sorting**: Sort by relevance, date, size, and other fields
- **Pagination**: Efficient pagination through large result sets

### Analytics Features
- **Search metrics**: Track search volume, response times, and success rates
- **User analytics**: Monitor unique users and sessions
- **Popular queries**: Identify trending search terms
- **Performance monitoring**: Track slow searches and errors
- **Time series data**: Analyze search trends over time
- **Search funnel**: Understand user journey through search

### Index Management
- **Automatic indexing**: Index updates when archive records change
- **Bulk operations**: Efficient bulk indexing and reindexing
- **Index optimization**: Automatic index optimization and maintenance
- **Health monitoring**: Monitor index health and performance
- **Time-based indices**: Support for time-based index patterns

## Architecture

### Components

1. **Models** (`backend/models/search.py`)
   - `SearchQuery`: Stores search queries and metadata
   - `SearchResult`: Individual search results with scores
   - `SearchSuggestion`: Auto-complete and suggestion data
   - `SearchAnalytics`: Aggregated analytics data
   - `SearchIndex`: Index configuration and status

2. **Schemas** (`backend/schemas/search.py`)
   - Request/response models for API endpoints
   - Validation and serialization
   - Comprehensive type definitions

3. **Services**
   - `SearchService` (`backend/services/search_service.py`): Core search functionality
   - `SearchAnalyticsService` (`backend/services/search_analytics_service.py`): Analytics processing
   - `IndexManager` (`backend/utils/index_manager.py`): Elasticsearch index management

4. **API** (`backend/api/search.py`)
   - RESTful endpoints for all search operations
   - Comprehensive error handling
   - Request validation and response formatting

## API Endpoints

### Search Operations

#### POST /api/v1/search/
Perform a search with advanced filtering and sorting.

```json
{
  "query": "user data",
  "search_type": "full_text",
  "filters": [
    {
      "field": "status",
      "operator": "eq",
      "value": "archived"
    }
  ],
  "sort_by": "relevance",
  "sort_order": "desc",
  "page": 1,
  "size": 10,
  "highlight": true,
  "include_aggregations": true,
  "aggregation_fields": ["data_type", "status"]
}
```

#### GET /api/v1/search/
Simple search using query parameters.

```
GET /api/v1/search?q=user&type=full_text&page=1&size=10&sort_by=relevance
```

#### POST /api/v1/search/advanced
Advanced search with archive-specific filters.

```json
{
  "query": "user data",
  "archive_filters": {
    "policy_id": [1, 2],
    "data_type": ["user_data", "logs"],
    "status": ["archived"],
    "file_size_min": 1000,
    "file_size_max": 1000000,
    "archived_after": "2024-01-01T00:00:00Z"
  },
  "include_deleted": false,
  "include_expired": true
}
```

### Auto-complete and Suggestions

#### POST /api/v1/search/autocomplete
Get auto-complete suggestions.

```json
{
  "prefix": "user",
  "field": "original_data_id",
  "size": 10,
  "suggest_type": "completion"
}
```

#### GET /api/v1/search/suggestions
Get search suggestions based on historical queries.

```
GET /api/v1/search/suggestions?q=user&size=5
```

### Analytics and Monitoring

#### GET /api/v1/search/analytics
Get search analytics for a specified period.

```
GET /api/v1/search/analytics?period_type=day&periods=7
```

#### GET /api/v1/search/stats
Get comprehensive search system statistics.

#### GET /api/v1/search/health
Check the health of the search system.

### Index Management

#### POST /api/v1/search/reindex
Reindex all archive records from the database.

#### POST /api/v1/search/index/refresh
Refresh the search index to make changes visible.

## Configuration

### Environment Variables

```bash
# Elasticsearch configuration
ELASTICSEARCH_URL=http://localhost:9200

# Search configuration
SEARCH_INDEX_NAME=archive_records
SEARCH_AUTO_REINDEX=true
SEARCH_REINDEX_INTERVAL_HOURS=24
```

### Elasticsearch Settings

The system uses the following default Elasticsearch settings:

```json
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
      "analyzer": {
        "archive_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "stop", "snowball"]
        }
      }
    }
  }
}
```

## Installation and Setup

### Prerequisites

1. **Elasticsearch** (version 8.x recommended)
2. **Python 3.8+**
3. **PostgreSQL** (for analytics data)

### Installation Steps

1. **Install Elasticsearch**
   ```bash
   # Download and install Elasticsearch
   wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.11.0-linux-x86_64.tar.gz
   tar -xzf elasticsearch-8.11.0-linux-x86_64.tar.gz
   cd elasticsearch-8.11.0/
   ./bin/elasticsearch
   ```

2. **Install Python Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Initialize Database**
   ```bash
   # Create database tables
   python -c "from backend.database import engine, Base; Base.metadata.create_all(bind=engine)"
   ```

4. **Start the Application**
   ```bash
   python -m backend.main
   ```

### Initial Index Setup

The search service will automatically create the necessary indices when it starts. You can also manually initialize:

```python
from backend.services.search_service import search_service
from backend.database import get_db

db = next(get_db())
await search_service.initialize_search(db)
```

## Usage Examples

### Basic Search

```python
from backend.services.search_service import search_service
from backend.schemas.search import SearchRequest, SearchType

# Create search request
request = SearchRequest(
    query="user data",
    search_type=SearchType.FULL_TEXT,
    page=1,
    size=10
)

# Perform search
result = await search_service.search(request, db)
print(f"Found {result.total} results")
```

### Advanced Filtering

```python
request = SearchRequest(
    query="logs",
    filters=[
        {"field": "data_type", "operator": "eq", "value": "logs"},
        {"field": "file_size_bytes", "operator": "range", "value": {"gte": 1000, "lte": 1000000}},
        {"field": "archived_at", "operator": "range", "value": {"gte": "2024-01-01"}}
    ],
    sort_by="archived_at",
    sort_order="desc"
)
```

### Auto-complete

```python
from backend.schemas.search import AutocompleteRequest

request = AutocompleteRequest(
    prefix="user",
    field="original_data_id",
    size=5
)

suggestions = await search_service.autocomplete(request)
print([s.text for s in suggestions.suggestions])
```

### Analytics

```python
from backend.services.search_analytics_service import analytics_service

# Get analytics for the last 7 days
analytics = await analytics_service.get_analytics(db, "day", 7)
print(f"Total searches: {analytics.total_searches}")
print(f"Average response time: {analytics.avg_response_time_ms}ms")

# Get time series data
time_series = await analytics_service.get_time_series_data(db, "day", 30)
```

## Performance Optimization

### Index Optimization

1. **Bulk Operations**: Use bulk indexing for multiple documents
2. **Refresh Strategy**: Control when indices are refreshed
3. **Index Sharding**: Configure appropriate number of shards
4. **Mapping Optimization**: Use appropriate field types and analyzers

### Query Optimization

1. **Filter vs Query**: Use filters for exact matches, queries for text search
2. **Pagination**: Use efficient pagination with search_after for deep pagination
3. **Caching**: Enable query caching for frequently used queries
4. **Aggregations**: Limit aggregation size and use appropriate sampling

### Monitoring

1. **Response Times**: Monitor average and p95 response times
2. **Index Size**: Track index size and document count
3. **Error Rates**: Monitor search failures and timeouts
4. **Resource Usage**: Monitor CPU, memory, and disk usage

## Testing

Run the test script to verify the search system:

```bash
python test_search.py
```

The test script will verify:
- Elasticsearch connection
- Index creation and management
- Document indexing
- Search functionality
- Database models
- Schema validation

## Troubleshooting

### Common Issues

1. **Elasticsearch Connection Failed**
   - Check if Elasticsearch is running
   - Verify the connection URL
   - Check network connectivity

2. **Index Creation Failed**
   - Check Elasticsearch cluster health
   - Verify sufficient disk space
   - Check index naming conflicts

3. **Search Returns No Results**
   - Verify documents are indexed
   - Check index refresh status
   - Validate search query syntax

4. **Slow Search Performance**
   - Check index optimization
   - Monitor query complexity
   - Consider index sharding

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

1. **Machine Learning**: Implement learning-to-rank for better relevance
2. **Geospatial Search**: Add location-based search capabilities
3. **Multi-language Support**: Support for multiple languages and analyzers
4. **Real-time Updates**: Implement real-time search updates
5. **Advanced Analytics**: More sophisticated analytics and reporting
6. **Search Personalization**: Personalized search results based on user behavior

## Contributing

When contributing to the search system:

1. Follow the existing code style and patterns
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Consider performance implications
5. Ensure backward compatibility

## License

This search system is part of the TTL archival service and follows the same licensing terms.
