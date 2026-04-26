"""
API Gateway Main Module

Main gateway application that integrates all gateway components:
routing, rate limiting, transformation, and authentication.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .router import (
    GatewayRouter, ServiceConfig, ServiceEndpoint, RouteRule,
    LoadBalancingStrategy, gateway_router
)
from .rate_limiter import (
    RateLimiter, RateLimitRule, RateLimitStrategy,
    RateLimitMiddleware, rate_limiter
)
from .transformer import (
    GatewayTransformer, TransformationRule, TransformationType, DataType,
    gateway_transformer
)
from .auth_proxy import (
    AuthProxy, AuthProvider, AuthRule, AuthType, AuthStrategy,
    AuthMiddleware, auth_proxy
)

logger = logging.getLogger(__name__)


class GatewayService:
    """
    Main gateway service that orchestrates all components
    """
    
    def __init__(self):
        self.app = FastAPI(
            title="TTL Archival Service API Gateway",
            description="Advanced API Gateway with routing, rate limiting, transformation, and authentication",
            version="1.0.0"
        )
        
        self.router = gateway_router
        self.rate_limiter = rate_limiter
        self.transformer = gateway_transformer
        self.auth_proxy = auth_proxy
        
        self._setup_middleware()
        self._setup_routes()
        self._configure_default_services()
    
    def _setup_middleware(self):
        """Setup gateway middleware"""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Authentication middleware
        self.app.add_middleware(AuthMiddleware, auth_proxy=self.auth_proxy)
        
        # Rate limiting middleware
        self.app.add_middleware(RateLimitMiddleware, rate_limiter=self.rate_limiter)
    
    def _setup_routes(self):
        """Setup gateway management routes"""
        
        @self.app.get("/gateway/status")
        async def get_gateway_status():
            """Get gateway status and statistics"""
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "services": self.router.get_service_status(),
                "routes": self.router.get_routes(),
                "rate_limiting": self.rate_limiter.get_stats(),
                "transformations": self.transformer.get_transformation_stats(),
                "authentication": self.auth_proxy.get_auth_stats()
            }
        
        @self.app.get("/gateway/health")
        async def health_check():
            """Gateway health check"""
            return {"status": "healthy", "timestamp": time.time()}
        
        @self.app.post("/gateway/services")
        async def register_service(service_config: Dict[str, Any]):
            """Register a new service"""
            try:
                # Create service endpoints
                endpoints = []
                for ep_config in service_config.get('endpoints', []):
                    endpoint = ServiceEndpoint(
                        url=ep_config['url'],
                        weight=ep_config.get('weight', 1),
                        max_failures=ep_config.get('max_failures', 3)
                    )
                    endpoints.append(endpoint)
                
                # Create service configuration
                service = ServiceConfig(
                    name=service_config['name'],
                    endpoints=endpoints,
                    load_balancing_strategy=LoadBalancingStrategy(
                        service_config.get('load_balancing_strategy', 'round_robin')
                    ),
                    health_check_path=service_config.get('health_check_path', '/health'),
                    health_check_interval=service_config.get('health_check_interval', 30),
                    timeout=service_config.get('timeout', 30),
                    retries=service_config.get('retries', 3)
                )
                
                # Register service
                self.router.register_service(service)
                
                return {"message": f"Service '{service.name}' registered successfully"}
            
            except Exception as e:
                logger.error(f"Failed to register service: {e}")
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/gateway/routes")
        async def add_route(route_config: Dict[str, Any]):
            """Add a new route"""
            try:
                route = RouteRule(
                    path_prefix=route_config['path_prefix'],
                    service_name=route_config['service_name'],
                    version=route_config.get('version'),
                    methods=route_config.get('methods', ['*']),
                    headers=route_config.get('headers', {}),
                    priority=route_config.get('priority', 0),
                    strip_prefix=route_config.get('strip_prefix', True)
                )
                
                self.router.add_route(route)
                
                return {"message": f"Route '{route.path_prefix}' added successfully"}
            
            except Exception as e:
                logger.error(f"Failed to add route: {e}")
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.delete("/gateway/routes/{path_prefix:path}")
        async def remove_route(path_prefix: str):
            """Remove a route"""
            try:
                self.router.remove_route(path_prefix)
                return {"message": f"Route '{path_prefix}' removed successfully"}
            
            except Exception as e:
                logger.error(f"Failed to remove route: {e}")
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/gateway/rate-limits")
        async def add_rate_limit(rule_config: Dict[str, Any]):
            """Add a rate limiting rule"""
            try:
                rule = RateLimitRule(
                    identifier=rule_config['identifier'],
                    strategy=RateLimitStrategy(rule_config['strategy']),
                    requests_per_window=rule_config['requests_per_window'],
                    window_size_seconds=rule_config['window_size_seconds'],
                    burst_size=rule_config.get('burst_size'),
                    key_extractors=rule_config.get('key_extractors', ['ip', 'user_id']),
                    headers=rule_config.get('headers', {}),
                    paths=rule_config.get('paths', ['/*']),
                    methods=rule_config.get('methods', ['*']),
                    priority=rule_config.get('priority', 0),
                    enabled=rule_config.get('enabled', True)
                )
                
                self.rate_limiter.add_rule(rule)
                
                return {"message": f"Rate limit rule '{rule.identifier}' added successfully"}
            
            except Exception as e:
                logger.error(f"Failed to add rate limit rule: {e}")
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.delete("/gateway/rate-limits/{rule_id}")
        async def remove_rate_limit(rule_id: str):
            """Remove a rate limiting rule"""
            try:
                self.rate_limiter.remove_rule(rule_id)
                return {"message": f"Rate limit rule '{rule_id}' removed successfully"}
            
            except Exception as e:
                logger.error(f"Failed to remove rate limit rule: {e}")
                raise HTTPException(status_code=400, detail(str(e)))
        
        @self.app.post("/gateway/auth/providers")
        async def add_auth_provider(provider_config: Dict[str, Any]):
            """Add an authentication provider"""
            try:
                provider = AuthProvider(
                    name=provider_config['name'],
                    auth_type=AuthType(provider_config['auth_type']),
                    strategy=AuthStrategy(provider_config['strategy']),
                    endpoint=provider_config.get('endpoint'),
                    public_key=provider_config.get('public_key'),
                    secret_key=provider_config.get('secret_key'),
                    issuer=provider_config.get('issuer'),
                    audience=provider_config.get('audience'),
                    algorithm=provider_config.get('algorithm', 'HS256'),
                    token_header=provider_config.get('token_header', 'Authorization'),
                    token_prefix=provider_config.get('token_prefix', 'Bearer '),
                    api_key_header=provider_config.get('api_key_header', 'X-API-Key'),
                    cache_ttl=provider_config.get('cache_ttl', 300),
                    timeout=provider_config.get('timeout', 10),
                    retries=provider_config.get('retries', 3),
                    enabled=provider_config.get('enabled', True)
                )
                
                self.auth_proxy.add_provider(provider)
                
                return {"message": f"Auth provider '{provider.name}' added successfully"}
            
            except Exception as e:
                logger.error(f"Failed to add auth provider: {e}")
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/gateway/auth/rules")
        async def add_auth_rule(rule_config: Dict[str, Any]):
            """Add an authentication rule"""
            try:
                rule = AuthRule(
                    name=rule_config['name'],
                    provider=rule_config['provider'],
                    paths=rule_config.get('paths', ['/*']),
                    methods=rule_config.get('methods', ['*']),
                    headers=rule_config.get('headers', {}),
                    required_scopes=rule_config.get('required_scopes', []),
                    required_roles=rule_config.get('required_roles', []),
                    anonymous_allowed=rule_config.get('anonymous_allowed', False),
                    priority=rule_config.get('priority', 0),
                    enabled=rule_config.get('enabled', True)
                )
                
                self.auth_proxy.add_rule(rule)
                
                return {"message": f"Auth rule '{rule.name}' added successfully"}
            
            except Exception as e:
                logger.error(f"Failed to add auth rule: {e}")
                raise HTTPException(status_code=400, detail=str(e))
        
        # Main proxy route - catch all for proxying
        @self.app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
        async def proxy_request(request: Request, path: str):
            """Proxy requests to backend services"""
            try:
                # Transform request
                context = {
                    'path': path,
                    'method': request.method,
                    'headers': dict(request.headers),
                    'query_params': dict(request.query_params),
                    'auth_context': getattr(request.state, 'auth_context', None)
                }
                
                transformed_request = await self.transformer.transform_request(request, context)
                
                # Route the request
                response = await self.router.route_request(transformed_request)
                
                # Transform response
                transformed_response = await self.transformer.transform_response(response, context)
                
                return transformed_response
            
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Proxy request failed: {e}")
                raise HTTPException(status_code=502, detail="Bad Gateway")
    
    def _configure_default_services(self):
        """Configure default gateway services"""
        # Example: Register the main archival service
        try:
            archival_service = ServiceConfig(
                name="archival-service",
                endpoints=[
                    ServiceEndpoint(url="http://localhost:8000", weight=1)
                ],
                load_balancing_strategy=LoadBalancingStrategy.ROUND_ROBIN,
                health_check_path="/health",
                health_check_interval=30,
                timeout=30,
                retries=3
            )
            
            self.router.register_service(archival_service)
            
            # Add default route for archival service
            archival_route = RouteRule(
                path_prefix="/api/",
                service_name="archival-service",
                methods=["*"],
                priority=100
            )
            
            self.router.add_route(archival_route)
            
            logger.info("Default archival service configured")
        
        except Exception as e:
            logger.error(f"Failed to configure default services: {e}")
    
    async def initialize(self):
        """Initialize all gateway components"""
        await self.router.initialize()
        await self.rate_limiter.initialize()
        logger.info("Gateway service initialized")
    
    async def shutdown(self):
        """Shutdown all gateway components"""
        await self.router.shutdown()
        await self.rate_limiter.shutdown()
        logger.info("Gateway service shutdown complete")
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application"""
        return self.app


@asynccontextmanager
async def gateway_lifespan(app: FastAPI):
    """Gateway lifespan manager"""
    # Initialize gateway
    gateway_service = app.state.gateway_service
    await gateway_service.initialize()
    
    try:
        yield
    finally:
        # Shutdown gateway
        await gateway_service.shutdown()


def create_gateway_app() -> FastAPI:
    """Create and configure the gateway application"""
    gateway_service = GatewayService()
    app = gateway_service.get_app()
    
    # Store gateway service in app state
    app.state.gateway_service = gateway_service
    
    # Set up lifespan
    app.router.lifespan_context = gateway_lifespan
    
    return app


# Create the gateway application
gateway_app = create_gateway_app()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the gateway
    uvicorn.run(
        "gateway.main:gateway_app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
