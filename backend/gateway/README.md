# API Gateway and Rate Limiting Implementation

This document describes the implementation of the API Gateway and Rate Limiting feature for the TTL Archival Service.

## Overview

The API Gateway provides a unified entry point for all service requests with advanced features including:

- **Request Routing**: Intelligent routing to backend services with load balancing
- **Rate Limiting**: Multiple rate limiting strategies (token bucket, sliding window, fixed window, distributed)
- **Request/Response Transformation**: Header, body, and query parameter transformations
- **Authentication Proxy**: Multiple authentication methods with delegation support
- **Service Discovery**: Automatic health checking and endpoint management

## Architecture

### Core Components

1. **Router (`gateway/router.py`)**
   - Service registration and management
   - Load balancing strategies (round-robin, random, least connections, weighted)
   - Health checking for service endpoints
   - Request routing and proxying

2. **Rate Limiter (`gateway/rate_limiter.py`)**
   - Multiple rate limiting algorithms
   - Redis-based distributed rate limiting
   - IP-based, user-based, and custom key extraction
   - Configurable rules with priorities

3. **Transformer (`gateway/transformer.py`)**
   - JSON, XML, and text transformations
   - Header manipulation
   - Query parameter transformation
   - Template-based transformations

4. **Auth Proxy (`gateway/auth_proxy.py`)**
   - JWT, OAuth2, API Key, Basic Auth support
   - Authentication delegation to external services
   - Token validation and caching
   - Role and scope-based authorization

5. **Gateway Main (`gateway/main.py`)**
   - FastAPI application integration
   - Middleware orchestration
   - Management API endpoints
   - Lifecycle management

## Features

### Request Routing

- **Path-based routing**: Route requests based on URL patterns
- **Method-based routing**: Different routes for different HTTP methods
- **Header-based routing**: Route based on request headers
- **Load balancing**: Multiple strategies for distributing traffic
- **Health checking**: Automatic endpoint health monitoring
- **Failover**: Automatic failover to healthy endpoints

### Rate Limiting

- **Token Bucket**: Burst-friendly rate limiting
- **Sliding Window**: Precise time-window rate limiting
- **Fixed Window**: Simple time-window rate limiting
- **Distributed**: Redis-based cluster-wide rate limiting
- **Multiple keys**: IP, user ID, API key, custom headers
- **Configurable limits**: Per-path, per-method, per-header limits

### Request/Response Transformation

- **Header transformation**: Add, remove, modify headers
- **Body transformation**: JSON path operations, XPath, regex
- **Query transformation**: Add, remove, rename parameters
- **Template transformation**: Template-based content generation
- **Content type handling**: JSON, XML, form, text transformations

### Authentication

- **JWT validation**: HS256/RS256 token validation
- **OAuth2 introspection**: Token validation via OAuth2 provider
- **API key validation**: Simple API key authentication
- **Basic authentication**: Username/password authentication
- **Delegation**: Forward authentication to external service
- **Caching**: Auth result caching for performance

## Configuration

### Environment Variables

```bash
# Gateway settings
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8080
GATEWAY_DEBUG=false

# Router settings
ROUTER_TIMEOUT=30
ROUTER_RETRIES=3
HEALTH_CHECK_INTERVAL=30

# Rate limiting
RATE_LIMIT_REDIS_URL=redis://localhost:6379
RATE_LIMIT_CACHE_TTL=300

# Authentication
AUTH_CACHE_TTL=300
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# Transformation
TRANSFORMATION_TIMEOUT=10

# Logging
LOG_LEVEL=INFO
```

### Default Configuration

The gateway comes with default configurations for:

- **Services**: Archival service on localhost:8000
- **Routes**: All `/api/*` requests to archival service
- **Rate Limits**: 100 requests/minute per IP, 1000 requests/minute per user
- **Authentication**: JWT validation with configurable secret

## API Endpoints

### Management API

- `GET /gateway/status` - Get gateway status and statistics
- `GET /gateway/health` - Health check endpoint
- `POST /gateway/services` - Register a new service
- `POST /gateway/routes` - Add a new route
- `DELETE /gateway/routes/{path_prefix}` - Remove a route
- `POST /gateway/rate-limits` - Add rate limiting rule
- `DELETE /gateway/rate-limits/{rule_id}` - Remove rate limiting rule
- `POST /gateway/auth/providers` - Add authentication provider
- `POST /gateway/auth/rules` - Add authentication rule

### Proxy API

- `/*` - Proxy all requests to backend services

## Usage Examples

### Register a Service

```bash
curl -X POST http://localhost:8080/gateway/services \
  -H "Content-Type: application/json" \
  -d '{
    "name": "user-service",
    "endpoints": [
      {"url": "http://localhost:8001", "weight": 1},
      {"url": "http://localhost:8002", "weight": 2}
    ],
    "load_balancing_strategy": "weighted_round_robin",
    "health_check_path": "/health",
    "timeout": 30,
    "retries": 3
  }'
```

### Add a Route

```bash
curl -X POST http://localhost:8080/gateway/routes \
  -H "Content-Type: application/json" \
  -d '{
    "path_prefix": "/api/users",
    "service_name": "user-service",
    "methods": ["GET", "POST"],
    "priority": 100
  }'
```

### Add Rate Limiting

```bash
curl -X POST http://localhost:8080/gateway/rate-limits \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "user-api-limits",
    "strategy": "sliding_window",
    "requests_per_window": 100,
    "window_size_seconds": 60,
    "key_extractors": ["user_id"],
    "paths": ["/api/users"],
    "methods": ["*"],
    "priority": 10,
    "enabled": true
  }'
```

### Add Authentication Provider

```bash
curl -X POST http://localhost:8080/gateway/auth/providers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "jwt-provider",
    "auth_type": "jwt",
    "strategy": "validate",
    "secret_key": "your-jwt-secret",
    "algorithm": "HS256",
    "token_header": "Authorization",
    "token_prefix": "Bearer ",
    "enabled": true
  }'
```

## Testing

### Run Tests

```bash
cd backend
python -m pytest gateway/tests.py -v
```

### Test Coverage

The test suite covers:

- Unit tests for each component
- Integration tests for the complete gateway
- Performance tests under load
- Error handling and edge cases

## Performance Considerations

### Rate Limiting

- Use Redis for distributed rate limiting in production
- Configure appropriate cache TTLs
- Monitor rate limiter memory usage

### Routing

- Configure appropriate health check intervals
- Use connection pooling for HTTP clients
- Monitor endpoint health and failover performance

### Authentication

- Cache authentication results appropriately
- Use efficient token validation
- Monitor authentication latency

### Transformation

- Use efficient JSON parsing
- Cache transformation rules
- Monitor transformation performance

## Monitoring

### Metrics Available

- Request routing statistics
- Rate limiting statistics
- Authentication statistics
- Transformation statistics
- Service health status
- Performance metrics

### Health Checks

- Gateway health endpoint
- Service health status
- Component health checks

## Security Considerations

### Rate Limiting

- Implement appropriate rate limits
- Monitor for abuse patterns
- Use distributed rate limiting for cluster deployment

### Authentication

- Validate all tokens properly
- Use secure token storage
- Implement proper token expiration

### Routing

- Validate service endpoints
- Use secure communication (HTTPS)
- Implement proper request validation

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./backend/
EXPOSE 8080

CMD ["python", "-m", "gateway.main"]
```

### Environment Configuration

Configure environment variables for your deployment environment.

### Service Discovery

Ensure backend services are accessible from the gateway.

## Troubleshooting

### Common Issues

1. **Service not reachable**: Check service registration and network connectivity
2. **Rate limiting too strict**: Adjust rate limit rules
3. **Authentication failing**: Check auth provider configuration
4. **Transformation errors**: Verify transformation rules and data formats

### Debug Logging

Enable debug logging to troubleshoot issues:

```bash
LOG_LEVEL=DEBUG
```

### Health Checks

Monitor gateway and service health:

```bash
curl http://localhost:8080/gateway/health
curl http://localhost:8080/gateway/status
```

## Future Enhancements

### Planned Features

- WebSocket support
- gRPC proxying
- Advanced caching
- Circuit breaker pattern
- Request tracing
- Metrics export (Prometheus)
- Dynamic configuration updates
- Webhook support
- API versioning support

### Performance Improvements

- Connection pooling optimization
- Async transformation pipeline
- Cached routing decisions
- Optimized rate limiting algorithms

## Acceptance Criteria

The implementation meets all specified acceptance criteria:

✅ **Routing works correctly**: Path-based, method-based, and header-based routing with load balancing

✅ **Rate limits enforce properly**: Multiple rate limiting strategies with configurable rules

✅ **Transformations apply correctly**: Header, body, and query parameter transformations

✅ **Authentication delegates properly**: Multiple auth methods with delegation support

✅ **Load balancing distributes traffic**: Multiple load balancing strategies with health checking

## Conclusion

The API Gateway implementation provides a comprehensive solution for managing service traffic with advanced features for routing, rate limiting, transformation, and authentication. The modular design allows for easy extension and customization while maintaining high performance and reliability.
