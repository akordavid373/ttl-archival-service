"""
API Gateway Router Module

Handles request routing, service discovery, and load balancing
for the TTL Archival Service gateway.
"""

import asyncio
import httpx
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import random
import time
from urllib.parse import urljoin, urlparse
import json

from fastapi import Request, Response, HTTPException
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"


@dataclass
class ServiceEndpoint:
    """Represents a service endpoint"""
    url: str
    weight: int = 1
    connections: int = 0
    healthy: bool = True
    last_health_check: float = field(default_factory=time.time)
    failure_count: int = 0
    max_failures: int = 3


@dataclass
class RouteRule:
    """Represents a routing rule"""
    path_prefix: str
    service_name: str
    version: Optional[str] = None
    methods: List[str] = field(default_factory=lambda: ["*"])
    headers: Dict[str, str] = field(default_factory=dict)
    priority: int = 0
    strip_prefix: bool = True


@dataclass
class ServiceConfig:
    """Configuration for a service"""
    name: str
    endpoints: List[ServiceEndpoint]
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    health_check_path: str = "/health"
    health_check_interval: int = 30
    timeout: int = 30
    retries: int = 3


class GatewayRouter:
    """
    Main gateway router class handling request routing and load balancing
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
        self.routes: List[RouteRule] = []
        self.round_robin_counters: Dict[str, int] = {}
        self.http_client: Optional[httpx.AsyncClient] = None
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
    
    async def initialize(self):
        """Initialize the router and HTTP client"""
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )
        logger.info("Gateway router initialized")
    
    async def shutdown(self):
        """Shutdown the router and cleanup resources"""
        if self.http_client:
            await self.http_client.aclose()
        
        # Cancel health check tasks
        for task in self.health_check_tasks.values():
            task.cancel()
        
        logger.info("Gateway router shutdown complete")
    
    def register_service(self, service_config: ServiceConfig):
        """Register a service with the gateway"""
        self.services[service_config.name] = service_config
        self.round_robin_counters[service_config.name] = 0
        
        # Start health checking for this service
        if service_config.name not in self.health_check_tasks:
            task = asyncio.create_task(
                self._health_check_loop(service_config.name)
            )
            self.health_check_tasks[service_config.name] = task
        
        logger.info(f"Service '{service_config.name}' registered with {len(service_config.endpoints)} endpoints")
    
    def add_route(self, route_rule: RouteRule):
        """Add a routing rule"""
        self.routes.append(route_rule)
        # Sort routes by priority (higher priority first)
        self.routes.sort(key=lambda r: r.priority, reverse=True)
        logger.info(f"Route added: {route_rule.path_prefix} -> {route_rule.service_name}")
    
    def remove_route(self, path_prefix: str):
        """Remove a routing rule"""
        self.routes = [r for r in self.routes if r.path_prefix != path_prefix]
        logger.info(f"Route removed: {path_prefix}")
    
    async def route_request(self, request: Request) -> Response:
        """
        Route an incoming request to the appropriate service
        """
        # Find matching route
        route_rule = self._find_matching_route(request)
        if not route_rule:
            raise HTTPException(status_code=404, detail="No route found for request")
        
        # Get service configuration
        service = self.services.get(route_rule.service_name)
        if not service:
            raise HTTPException(status_code=503, detail=f"Service '{route_rule.service_name}' not available")
        
        # Select endpoint based on load balancing strategy
        endpoint = self._select_endpoint(service)
        if not endpoint:
            raise HTTPException(status_code=503, detail="No healthy endpoints available")
        
        # Build target URL
        target_url = self._build_target_url(request, route_rule, endpoint)
        
        # Proxy the request
        return await self._proxy_request(request, target_url, service)
    
    def _find_matching_route(self, request: Request) -> Optional[RouteRule]:
        """Find the best matching route for the request"""
        path = request.url.path
        method = request.method
        headers = dict(request.headers)
        
        for route in self.routes:
            # Check path prefix
            if not path.startswith(route.path_prefix):
                continue
            
            # Check method
            if "*" not in route.methods and method not in route.methods:
                continue
            
            # Check headers
            header_match = True
            for key, value in route.headers.items():
                if headers.get(key) != value:
                    header_match = False
                    break
            
            if header_match:
                return route
        
        return None
    
    def _select_endpoint(self, service: ServiceConfig) -> Optional[ServiceEndpoint]:
        """Select an endpoint based on load balancing strategy"""
        healthy_endpoints = [ep for ep in service.endpoints if ep.healthy]
        
        if not healthy_endpoints:
            return None
        
        if service.load_balancing_strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._select_round_robin(service.name, healthy_endpoints)
        elif service.load_balancing_strategy == LoadBalancingStrategy.RANDOM:
            return random.choice(healthy_endpoints)
        elif service.load_balancing_strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return min(healthy_endpoints, key=lambda ep: ep.connections)
        elif service.load_balancing_strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._select_weighted_round_robin(service.name, healthy_endpoints)
        
        return healthy_endpoints[0]
    
    def _select_round_robin(self, service_name: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Select endpoint using round-robin strategy"""
        counter = self.round_robin_counters.get(service_name, 0)
        endpoint = endpoints[counter % len(endpoints)]
        self.round_robin_counters[service_name] = (counter + 1) % len(endpoints)
        return endpoint
    
    def _select_weighted_round_robin(self, service_name: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Select endpoint using weighted round-robin strategy"""
        total_weight = sum(ep.weight for ep in endpoints)
        counter = self.round_robin_counters.get(service_name, 0)
        
        weight_counter = counter % total_weight
        current_weight = 0
        
        for endpoint in endpoints:
            current_weight += endpoint.weight
            if weight_counter < current_weight:
                self.round_robin_counters[service_name] = (counter + 1) % total_weight
                return endpoint
        
        # Fallback to first endpoint
        return endpoints[0]
    
    def _build_target_url(self, request: Request, route: RouteRule, endpoint: ServiceEndpoint) -> str:
        """Build the target URL for the proxy request"""
        path = request.url.path
        
        # Strip prefix if configured
        if route.strip_prefix and path.startswith(route.path_prefix):
            path = path[len(route.path_prefix):]
        
        # Ensure path starts with /
        if not path.startswith('/'):
            path = '/' + path
        
        # Build full URL
        target_url = urljoin(endpoint.url, path)
        
        # Add query parameters
        if request.url.query:
            target_url += f"?{request.url.query}"
        
        return target_url
    
    async def _proxy_request(self, request: Request, target_url: str, service: ServiceConfig) -> Response:
        """Proxy the request to the target service"""
        # Prepare request data
        headers = dict(request.headers)
        
        # Remove hop-by-hop headers
        hop_by_hop_headers = {
            'connection', 'keep-alive', 'proxy-authenticate',
            'proxy-authorization', 'te', 'trailers', 'transfer-encoding',
            'upgrade', 'proxy-connection'
        }
        for header in hop_by_hop_headers:
            headers.pop(header, None)
        
        # Update host header
        parsed_url = urlparse(target_url)
        headers['host'] = parsed_url.netloc
        
        # Get request body
        body = await request.body()
        
        # Increment connection count
        endpoint = next(ep for ep in service.endpoints if target_url.startswith(ep.url))
        endpoint.connections += 1
        
        try:
            # Make the request with retries
            response_data = await self._make_request_with_retries(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                service=service
            )
            
            return StreamingResponse(
                content=response_data.aiter_bytes(),
                status_code=response_data.status_code,
                headers=dict(response_data.headers),
                media_type=response_data.headers.get('content-type')
            )
        
        finally:
            # Decrement connection count
            endpoint.connections -= 1
    
    async def _make_request_with_retries(self, method: str, url: str, headers: Dict[str, str], 
                                        content: bytes, service: ServiceConfig) -> httpx.Response:
        """Make HTTP request with retry logic"""
        last_exception = None
        
        for attempt in range(service.retries + 1):
            try:
                response = await self.http_client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    content=content
                )
                
                # Mark endpoint as healthy on successful response
                endpoint = next(ep for ep in service.endpoints if url.startswith(ep.url))
                if endpoint.failure_count > 0:
                    endpoint.failure_count = 0
                    endpoint.healthy = True
                
                return response
            
            except httpx.RequestError as e:
                last_exception = e
                
                # Mark endpoint as failed
                endpoint = next(ep for ep in service.endpoints if url.startswith(ep.url))
                endpoint.failure_count += 1
                if endpoint.failure_count >= endpoint.max_failures:
                    endpoint.healthy = False
                
                if attempt < service.retries:
                    # Try a different endpoint
                    new_endpoint = self._select_endpoint(service)
                    if new_endpoint and new_endpoint.url != endpoint.url:
                        url = url.replace(endpoint.url, new_endpoint.url)
                        logger.warning(f"Retrying request to different endpoint: {new_endpoint.url}")
                        await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                        continue
                
                logger.error(f"Request failed after {attempt + 1} attempts: {e}")
        
        raise HTTPException(status_code=503, detail=f"Service unavailable: {last_exception}")
    
    async def _health_check_loop(self, service_name: str):
        """Continuous health check loop for a service"""
        service = self.services.get(service_name)
        if not service:
            return
        
        while True:
            try:
                await self._perform_health_checks(service)
                await asyncio.sleep(service.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error for service '{service_name}': {e}")
                await asyncio.sleep(5)  # Short delay on error
    
    async def _perform_health_checks(self, service: ServiceConfig):
        """Perform health checks on all endpoints of a service"""
        tasks = []
        for endpoint in service.endpoints:
            task = asyncio.create_task(self._check_endpoint_health(endpoint, service))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_endpoint_health(self, endpoint: ServiceEndpoint, service: ServiceConfig):
        """Check health of a single endpoint"""
        try:
            health_url = urljoin(endpoint.url, service.health_check_path)
            
            response = await self.http_client.get(
                health_url,
                timeout=5.0
            )
            
            if response.status_code == 200:
                endpoint.healthy = True
                endpoint.failure_count = 0
                endpoint.last_health_check = time.time()
            else:
                endpoint.failure_count += 1
                if endpoint.failure_count >= endpoint.max_failures:
                    endpoint.healthy = False
                    logger.warning(f"Endpoint {endpoint.url} marked unhealthy (status: {response.status_code})")
        
        except Exception as e:
            endpoint.failure_count += 1
            if endpoint.failure_count >= endpoint.max_failures:
                endpoint.healthy = False
                logger.warning(f"Endpoint {endpoint.url} marked unhealthy: {e}")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all registered services"""
        status = {}
        
        for service_name, service in self.services.items():
            healthy_endpoints = [ep for ep in service.endpoints if ep.healthy]
            total_connections = sum(ep.connections for ep in service.endpoints)
            
            status[service_name] = {
                'healthy_endpoints': len(healthy_endpoints),
                'total_endpoints': len(service.endpoints),
                'total_connections': total_connections,
                'load_balancing_strategy': service.load_balancing_strategy.value,
                'endpoints': [
                    {
                        'url': ep.url,
                        'healthy': ep.healthy,
                        'connections': ep.connections,
                        'failure_count': ep.failure_count,
                        'last_health_check': ep.last_health_check
                    }
                    for ep in service.endpoints
                ]
            }
        
        return status
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """Get all configured routes"""
        return [
            {
                'path_prefix': route.path_prefix,
                'service_name': route.service_name,
                'version': route.version,
                'methods': route.methods,
                'priority': route.priority,
                'strip_prefix': route.strip_prefix
            }
            for route in self.routes
        ]


# Global router instance
gateway_router = GatewayRouter()
