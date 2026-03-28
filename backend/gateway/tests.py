"""
API Gateway Tests

Test suite for gateway functionality including routing,
rate limiting, transformation, and authentication.
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, AsyncMock, patch
from fastapi import Request, HTTPException
from fastapi.testclient import TestClient
import httpx

from gateway.router import GatewayRouter, ServiceConfig, ServiceEndpoint, RouteRule, LoadBalancingStrategy
from gateway.rate_limiter import RateLimiter, RateLimitRule, RateLimitStrategy
from gateway.transformer import GatewayTransformer, TransformationRule, TransformationType, DataType
from gateway.auth_proxy import AuthProxy, AuthProvider, AuthRule, AuthType, AuthStrategy, AuthContext
from gateway.main import create_gateway_app


class TestGatewayRouter:
    """Test cases for gateway router"""
    
    @pytest.fixture
    def router(self):
        """Create a router instance for testing"""
        return GatewayRouter()
    
    @pytest.fixture
    def sample_service(self):
        """Create a sample service configuration"""
        return ServiceConfig(
            name="test-service",
            endpoints=[
                ServiceEndpoint(url="http://localhost:8001", weight=1),
                ServiceEndpoint(url="http://localhost:8002", weight=2)
            ],
            load_balancing_strategy=LoadBalancingStrategy.ROUND_ROBIN,
            health_check_path="/health",
            timeout=30,
            retries=3
        )
    
    @pytest.fixture
    def sample_route(self):
        """Create a sample route rule"""
        return RouteRule(
            path_prefix="/api/test",
            service_name="test-service",
            methods=["GET", "POST"],
            priority=100
        )
    
    @pytest.mark.asyncio
    async def test_register_service(self, router, sample_service):
        """Test service registration"""
        router.register_service(sample_service)
        
        assert sample_service.name in router.services
        assert len(router.services[sample_service.name].endpoints) == 2
        assert router.round_robin_counters[sample_service.name] == 0
    
    def test_add_route(self, router, sample_route):
        """Test route addition"""
        router.add_route(sample_route)
        
        assert len(router.routes) == 1
        assert router.routes[0].path_prefix == "/api/test"
        assert router.routes[0].service_name == "test-service"
    
    def test_remove_route(self, router, sample_route):
        """Test route removal"""
        router.add_route(sample_route)
        router.remove_route("/api/test")
        
        assert len(router.routes) == 0
    
    def test_find_matching_route(self, router, sample_route):
        """Test route matching"""
        router.add_route(sample_route)
        
        # Create mock request
        request = Mock()
        request.url.path = "/api/test/users"
        request.method = "GET"
        request.headers = {}
        
        matched_route = router._find_matching_route(request)
        assert matched_route is not None
        assert matched_route.path_prefix == "/api/test"
    
    def test_select_endpoint_round_robin(self, router, sample_service):
        """Test round-robin endpoint selection"""
        router.register_service(sample_service)
        
        endpoint1 = router._select_endpoint(sample_service)
        endpoint2 = router._select_endpoint(sample_service)
        
        # Should alternate between endpoints
        assert endpoint1.url != endpoint2.url
    
    def test_select_endpoint_random(self, router):
        """Test random endpoint selection"""
        service = ServiceConfig(
            name="test-service",
            endpoints=[
                ServiceEndpoint(url="http://localhost:8001"),
                ServiceEndpoint(url="http://localhost:8002")
            ],
            load_balancing_strategy=LoadBalancingStrategy.RANDOM
        )
        
        router.register_service(service)
        
        endpoint = router._select_endpoint(service)
        assert endpoint is not None
        assert endpoint.healthy is True
    
    @pytest.mark.asyncio
    async def test_initialize(self, router):
        """Test router initialization"""
        await router.initialize()
        assert router.http_client is not None
        
        await router.shutdown()
        assert router.http_client is None


class TestRateLimiter:
    """Test cases for rate limiter"""
    
    @pytest.fixture
    def limiter(self):
        """Create a rate limiter instance"""
        return RateLimiter()
    
    @pytest.fixture
    def sample_rule(self):
        """Create a sample rate limit rule"""
        return RateLimitRule(
            identifier="test-rule",
            strategy=RateLimitStrategy.SLIDING_WINDOW,
            requests_per_window=10,
            window_size_seconds=60,
            key_extractors=["ip"],
            paths=["/api/test"],
            methods=["GET"]
        )
    
    @pytest.mark.asyncio
    async def test_add_rule(self, limiter, sample_rule):
        """Test rule addition"""
        limiter.add_rule(sample_rule)
        
        assert len(limiter.rules) == 1
        assert limiter.rules[0].identifier == "test-rule"
    
    def test_remove_rule(self, limiter, sample_rule):
        """Test rule removal"""
        limiter.add_rule(sample_rule)
        limiter.remove_rule("test-rule")
        
        assert len(limiter.rules) == 0
    
    @pytest.mark.asyncio
    async def test_sliding_window_limit(self, limiter):
        """Test sliding window rate limiting"""
        rule = RateLimitRule(
            identifier="test",
            strategy=RateLimitStrategy.SLIDING_WINDOW,
            requests_per_window=5,
            window_size_seconds=1
        )
        
        key = "test-key"
        
        # First 5 requests should be allowed
        for i in range(5):
            result = await limiter._sliding_window_limit(rule, key)
            assert result.allowed is True
            assert result.remaining_requests == 4 - i
        
        # 6th request should be denied
        result = await limiter._sliding_window_limit(rule, key)
        assert result.allowed is False
        assert result.remaining_requests == 0
        assert result.retry_after is not None
    
    @pytest.mark.asyncio
    async def test_token_bucket_limit(self, limiter):
        """Test token bucket rate limiting"""
        rule = RateLimitRule(
            identifier="test",
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            requests_per_window=10,
            window_size_seconds=10,
            burst_size=5
        )
        
        key = "test-key"
        
        # First 5 requests should be allowed (burst)
        for i in range(5):
            result = await limiter._token_bucket_limit(rule, key)
            assert result.allowed is True
        
        # 6th request should be denied (bucket empty)
        result = await limiter._token_bucket_limit(rule, key)
        assert result.allowed is False
    
    @pytest.mark.asyncio
    async def test_rule_applies(self, limiter, sample_rule):
        """Test rule application logic"""
        # Create mock request
        request = Mock()
        request.url.path = "/api/test/users"
        request.method = "GET"
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"
        
        assert limiter._rule_applies(sample_rule, request) is True
        
        # Test non-matching path
        request.url.path = "/api/other/users"
        assert limiter._rule_applies(sample_rule, request) is False
        
        # Test non-matching method
        request.url.path = "/api/test/users"
        request.method = "POST"
        assert limiter._rule_applies(sample_rule, request) is False
    
    def test_extract_identifier(self, limiter):
        """Test identifier extraction"""
        rule = RateLimitRule(
            identifier="test",
            strategy=RateLimitStrategy.SLIDING_WINDOW,
            requests_per_window=10,
            window_size_seconds=60,
            key_extractors=["ip", "user_id"]
        )
        
        # Create mock request
        request = Mock()
        request.client.host = "192.168.1.1"
        request.headers = {"x-user-id": "user123"}
        request.query_params = {}
        
        identifier = limiter._extract_identifier(rule, request)
        assert identifier is not None
        assert isinstance(identifier, str)
    
    @pytest.mark.asyncio
    async def test_initialize(self, limiter):
        """Test limiter initialization"""
        await limiter.initialize()
        # Should not raise any exceptions
    
    @pytest.mark.asyncio
    async def test_shutdown(self, limiter):
        """Test limiter shutdown"""
        await limiter.shutdown()
        # Should not raise any exceptions


class TestGatewayTransformer:
    """Test cases for gateway transformer"""
    
    @pytest.fixture
    def transformer(self):
        """Create a transformer instance"""
        return GatewayTransformer()
    
    @pytest.fixture
    def sample_rule(self):
        """Create a sample transformation rule"""
        return TransformationRule(
            name="test-rule",
            transformation_type=TransformationType.REQUEST,
            data_type=DataType.JSON,
            priority=100
        )
    
    def test_add_transformation_rule(self, transformer, sample_rule):
        """Test rule addition"""
        transformer.add_transformation_rule(sample_rule)
        
        assert len(transformer.transformation_rules) == 1
        assert transformer.transformation_rules[0].name == "test-rule"
    
    def test_remove_transformation_rule(self, transformer, sample_rule):
        """Test rule removal"""
        transformer.add_transformation_rule(sample_rule)
        transformer.remove_transformation_rule("test-rule")
        
        assert len(transformer.transformation_rules) == 0
    
    def test_rule_applies(self, transformer, sample_rule):
        """Test rule application logic"""
        # Create mock request
        request = Mock()
        request.url.path = "/api/test"
        request.method = "GET"
        request.headers = {"content-type": "application/json"}
        
        context = {}
        
        assert transformer._rule_applies(sample_rule, request, context) is True
        
        # Test non-matching path
        sample_rule.conditions = {"path": "/api/other"}
        assert transformer._rule_applies(sample_rule, request, context) is False
    
    def test_get_transformation_stats(self, transformer):
        """Test statistics collection"""
        stats = transformer.get_transformation_stats()
        
        assert "total_rules" in stats
        assert "request_transformers" in stats
        assert "response_transformers" in stats
        assert "rules" in stats


class TestAuthProxy:
    """Test cases for authentication proxy"""
    
    @pytest.fixture
    def auth_proxy(self):
        """Create an auth proxy instance"""
        return AuthProxy()
    
    @pytest.fixture
    def sample_provider(self):
        """Create a sample auth provider"""
        return AuthProvider(
            name="test-provider",
            auth_type=AuthType.JWT,
            strategy=AuthStrategy.VALIDATE,
            secret_key="test-secret",
            algorithm="HS256"
        )
    
    @pytest.fixture
    def sample_rule(self):
        """Create a sample auth rule"""
        return AuthRule(
            name="test-rule",
            provider="test-provider",
            paths=["/api/test"],
            methods=["GET", "POST"],
            priority=100
        )
    
    def test_add_provider(self, auth_proxy, sample_provider):
        """Test provider addition"""
        auth_proxy.add_provider(sample_provider)
        
        assert sample_provider.name in auth_proxy.providers
        assert sample_provider.name in auth_proxy.validators
    
    def test_remove_provider(self, auth_proxy, sample_provider):
        """Test provider removal"""
        auth_proxy.add_provider(sample_provider)
        auth_proxy.remove_provider(sample_provider.name)
        
        assert sample_provider.name not in auth_proxy.providers
    
    def test_add_rule(self, auth_proxy, sample_rule):
        """Test rule addition"""
        auth_proxy.add_rule(sample_rule)
        
        assert len(auth_proxy.rules) == 1
        assert auth_proxy.rules[0].name == "test-rule"
    
    def test_remove_rule(self, auth_proxy, sample_rule):
        """Test rule removal"""
        auth_proxy.add_rule(sample_rule)
        auth_proxy.remove_rule("test-rule")
        
        assert len(auth_proxy.rules) == 0
    
    def test_find_applicable_rule(self, auth_proxy, sample_rule):
        """Test rule finding"""
        auth_proxy.add_rule(sample_rule)
        
        # Create mock request
        request = Mock()
        request.url.path = "/api/test/users"
        request.method = "GET"
        request.headers = {}
        
        rule = auth_proxy._find_applicable_rule(request)
        assert rule is not None
        assert rule.name == "test-rule"
    
    def test_extract_token(self, auth_proxy, sample_provider):
        """Test token extraction"""
        # Create mock request
        request = Mock()
        request.headers = {"Authorization": "Bearer test-token"}
        
        token = auth_proxy._extract_token(request, sample_provider)
        assert token == "test-token"
    
    def test_get_auth_stats(self, auth_proxy):
        """Test statistics collection"""
        stats = auth_proxy.get_auth_stats()
        
        assert "total_providers" in stats
        assert "total_rules" in stats
        assert "cache_size" in stats
        assert "providers" in stats
        assert "rules" in stats


class TestGatewayIntegration:
    """Integration tests for the complete gateway"""
    
    @pytest.fixture
    def gateway_app(self):
        """Create a gateway app for testing"""
        return create_gateway_app()
    
    @pytest.fixture
    def client(self, gateway_app):
        """Create a test client"""
        return TestClient(gateway_app)
    
    def test_gateway_health_check(self, client):
        """Test gateway health check endpoint"""
        response = client.get("/gateway/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_gateway_status(self, client):
        """Test gateway status endpoint"""
        response = client.get("/gateway/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data
        assert "routes" in data
        assert "rate_limiting" in data
        assert "transformations" in data
        assert "authentication" in data
    
    def test_register_service(self, client):
        """Test service registration"""
        service_config = {
            "name": "test-service",
            "endpoints": [
                {"url": "http://localhost:8001", "weight": 1}
            ],
            "load_balancing_strategy": "round_robin",
            "health_check_path": "/health",
            "timeout": 30,
            "retries": 3
        }
        
        response = client.post("/gateway/services", json=service_config)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_add_route(self, client):
        """Test route addition"""
        route_config = {
            "path_prefix": "/api/test",
            "service_name": "test-service",
            "methods": ["GET", "POST"],
            "priority": 100
        }
        
        response = client.post("/gateway/routes", json=route_config)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_add_rate_limit(self, client):
        """Test rate limit rule addition"""
        rule_config = {
            "identifier": "test-rule",
            "strategy": "sliding_window",
            "requests_per_window": 100,
            "window_size_seconds": 60,
            "key_extractors": ["ip"],
            "paths": ["/*"],
            "methods": ["*"],
            "priority": 0,
            "enabled": True
        }
        
        response = client.post("/gateway/rate-limits", json=rule_config)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_add_auth_provider(self, client):
        """Test auth provider addition"""
        provider_config = {
            "name": "test-provider",
            "auth_type": "jwt",
            "strategy": "validate",
            "secret_key": "test-secret",
            "algorithm": "HS256",
            "enabled": True
        }
        
        response = client.post("/gateway/auth/providers", json=provider_config)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_add_auth_rule(self, client):
        """Test auth rule addition"""
        rule_config = {
            "name": "test-rule",
            "provider": "test-provider",
            "paths": ["/api/"],
            "methods": ["POST", "PUT", "DELETE"],
            "anonymous_allowed": True,
            "priority": 0,
            "enabled": True
        }
        
        response = client.post("/gateway/auth/rules", json=rule_config)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


# Performance tests
class TestGatewayPerformance:
    """Performance tests for gateway components"""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_performance(self):
        """Test rate limiter performance under load"""
        limiter = RateLimiter()
        
        rule = RateLimitRule(
            identifier="perf-test",
            strategy=RateLimitStrategy.SLIDING_WINDOW,
            requests_per_window=10000,
            window_size_seconds=1
        )
        
        limiter.add_rule(rule)
        
        # Create mock request
        request = Mock()
        request.url.path = "/api/test"
        request.method = "GET"
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"
        
        # Measure performance
        start_time = time.time()
        
        for i in range(1000):
            await limiter.check_rate_limit(request)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should handle 1000 requests in under 1 second
        assert duration < 1.0
        assert limiter.get_stats()['total_rules'] == 1
    
    @pytest.mark.asyncio
    async def test_router_performance(self):
        """Test router performance under load"""
        router = GatewayRouter()
        
        # Add multiple services and routes
        for i in range(10):
            service = ServiceConfig(
                name=f"service-{i}",
                endpoints=[
                    ServiceEndpoint(url=f"http://localhost:{8000 + i}")
                ]
            )
            router.register_service(service)
            
            route = RouteRule(
                path_prefix=f"/api/service-{i}",
                service_name=f"service-{i}"
            )
            router.add_route(route)
        
        # Create mock request
        request = Mock()
        request.url.path = "/api/service-5/users"
        request.method = "GET"
        request.headers = {}
        
        # Measure performance
        start_time = time.time()
        
        for i in range(1000):
            router._find_matching_route(request)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should handle 1000 route lookups in under 0.1 second
        assert duration < 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
