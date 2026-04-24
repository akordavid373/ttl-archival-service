"""
API Gateway Rate Limiter Module

Implements advanced rate limiting with multiple strategies,
including token bucket, sliding window, and distributed rate limiting.
"""

import asyncio
import time
import logging
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import redis.asyncio as redis
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    DISTRIBUTED = "distributed"


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration"""
    identifier: str  # Rule name/ID
    strategy: RateLimitStrategy
    requests_per_window: int
    window_size_seconds: int
    burst_size: Optional[int] = None  # For token bucket
    key_extractors: List[str] = field(default_factory=lambda: ["ip", "user_id"])
    headers: Dict[str, str] = field(default_factory=dict)
    paths: List[str] = field(default_factory=lambda: ["/*"])
    methods: List[str] = field(default_factory=lambda: ["*"])
    priority: int = 0
    enabled: bool = True


@dataclass
class RateLimitResult:
    """Result of rate limit check"""
    allowed: bool
    remaining_requests: int
    reset_time: float
    retry_after: Optional[float] = None
    rule_id: Optional[str] = None
    identifier: Optional[str] = None


class TokenBucket:
    """Token bucket rate limiter implementation"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = capacity
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> Tuple[bool, float, int]:
        """Consume tokens from the bucket"""
        now = time.time()
        
        # Refill tokens
        time_passed = now - self.last_refill
        tokens_to_add = time_passed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True, now + (self.capacity - self.tokens) / self.refill_rate, int(self.tokens)
        
        retry_after = tokens / self.refill_rate
        return False, now + retry_after, int(self.tokens)


class SlidingWindow:
    """Sliding window rate limiter implementation"""
    
    def __init__(self, window_size: int, max_requests: int):
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests = deque()
    
    def is_allowed(self, timestamp: float) -> Tuple[bool, float, int]:
        """Check if request is allowed"""
        # Remove old requests outside the window
        while self.requests and self.requests[0] <= timestamp - self.window_size:
            self.requests.popleft()
        
        # Check if we can add this request
        if len(self.requests) < self.max_requests:
            self.requests.append(timestamp)
            return True, timestamp + self.window_size, self.max_requests - len(self.requests)
        
        # Find when the oldest request will expire
        oldest_request = self.requests[0]
        retry_after = oldest_request + self.window_size - timestamp
        return False, timestamp + self.window_size, 0


class FixedWindow:
    """Fixed window rate limiter implementation"""
    
    def __init__(self, window_size: int, max_requests: int):
        self.window_size = window_size
        self.max_requests = max_requests
        self.current_window_start = 0
        self.request_count = 0
    
    def is_allowed(self, timestamp: float) -> Tuple[bool, float, int]:
        """Check if request is allowed"""
        window_start = int(timestamp // self.window_size) * self.window_size
        
        # Reset window if we're in a new window
        if window_start != self.current_window_start:
            self.current_window_start = window_start
            self.request_count = 0
        
        # Check if we can add this request
        if self.request_count < self.max_requests:
            self.request_count += 1
            return True, window_start + self.window_size, self.max_requests - self.request_count
        
        retry_after = self.current_window_start + self.window_size - timestamp
        return False, self.current_window_start + self.window_size, 0


class RateLimiter:
    """
    Advanced rate limiter supporting multiple strategies
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.rules: List[RateLimitRule] = []
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.sliding_windows: Dict[str, SlidingWindow] = {}
        self.fixed_windows: Dict[str, FixedWindow] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.local_cache: Dict[str, Any] = {}
        self.cache_ttl = 60  # Cache TTL for local storage
        
        # Initialize Redis if provided
        if redis_url:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
    
    async def initialize(self):
        """Initialize the rate limiter"""
        if self.redis_client:
            try:
                await self.redis_client.ping()
                logger.info("Rate limiter connected to Redis")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self.redis_client = None
        else:
            logger.info("Rate limiter running in local mode")
    
    async def shutdown(self):
        """Shutdown the rate limiter"""
        if self.redis_client:
            await self.redis_client.close()
    
    def add_rule(self, rule: RateLimitRule):
        """Add a rate limiting rule"""
        self.rules.append(rule)
        # Sort rules by priority
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info(f"Rate limit rule added: {rule.identifier}")
    
    def remove_rule(self, rule_id: str):
        """Remove a rate limiting rule"""
        self.rules = [r for r in self.rules if r.identifier != rule_id]
        logger.info(f"Rate limit rule removed: {rule_id}")
    
    async def check_rate_limit(self, request: Request) -> RateLimitResult:
        """
        Check if a request should be rate limited
        """
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            # Check if rule applies to this request
            if not self._rule_applies(rule, request):
                continue
            
            # Extract identifier for this request
            identifier = self._extract_identifier(rule, request)
            
            # Apply rate limiting based on strategy
            result = await self._apply_rate_limit(rule, identifier, request)
            
            if not result.allowed:
                result.rule_id = rule.identifier
                result.identifier = identifier
                return result
        
        # Default: allow all requests
        return RateLimitResult(
            allowed=True,
            remaining_requests=999999,
            reset_time=time.time() + 3600
        )
    
    def _rule_applies(self, rule: RateLimitRule, request: Request) -> bool:
        """Check if a rule applies to the current request"""
        # Check method
        if "*" not in rule.methods and request.method not in rule.methods:
            return False
        
        # Check path
        path = request.url.path
        path_match = False
        for rule_path in rule.paths:
            if rule_path == "/*" or path.startswith(rule_path.rstrip('*')):
                path_match = True
                break
        
        if not path_match:
            return False
        
        # Check headers
        headers = dict(request.headers)
        for key, value in rule.headers.items():
            if headers.get(key) != value:
                return False
        
        return True
    
    def _extract_identifier(self, rule: RateLimitRule, request: Request) -> str:
        """Extract unique identifier for rate limiting"""
        parts = []
        
        for extractor in rule.key_extractors:
            if extractor == "ip":
                parts.append(request.client.host if request.client else "unknown")
            elif extractor == "user_id":
                user_id = request.headers.get("x-user-id") or request.headers.get("user-id")
                parts.append(user_id or "anonymous")
            elif extractor == "api_key":
                api_key = request.headers.get("x-api-key") or request.headers.get("authorization")
                parts.append(api_key or "none")
            elif extractor == "path":
                parts.append(request.url.path)
            elif extractor.startswith("header:"):
                header_name = extractor[7:]
                header_value = request.headers.get(header_name, "")
                parts.append(header_value)
            elif extractor.startswith("query:"):
                query_param = extractor[6:]
                query_value = request.query_params.get(query_param, "")
                parts.append(query_value)
        
        # Create a hash for consistent identifier
        identifier = ":".join(parts)
        return hashlib.md5(identifier.encode()).hexdigest()
    
    async def _apply_rate_limit(self, rule: RateLimitRule, identifier: str, request: Request) -> RateLimitResult:
        """Apply rate limiting based on strategy"""
        key = f"{rule.identifier}:{identifier}"
        
        if rule.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return await self._token_bucket_limit(rule, key)
        elif rule.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return await self._sliding_window_limit(rule, key)
        elif rule.strategy == RateLimitStrategy.FIXED_WINDOW:
            return await self._fixed_window_limit(rule, key)
        elif rule.strategy == RateLimitStrategy.DISTRIBUTED:
            return await self._distributed_limit(rule, key)
        
        # Default: allow
        return RateLimitResult(
            allowed=True,
            remaining_requests=999999,
            reset_time=time.time() + 3600
        )
    
    async def _token_bucket_limit(self, rule: RateLimitRule, key: str) -> RateLimitResult:
        """Token bucket rate limiting"""
        if key not in self.token_buckets:
            burst_size = rule.burst_size or rule.requests_per_window
            refill_rate = rule.requests_per_window / rule.window_size_seconds
            self.token_buckets[key] = TokenBucket(burst_size, refill_rate)
        
        bucket = self.token_buckets[key]
        allowed, reset_time, remaining = bucket.consume()
        
        return RateLimitResult(
            allowed=allowed,
            remaining_requests=remaining,
            reset_time=reset_time,
            retry_after=None if allowed else reset_time - time.time()
        )
    
    async def _sliding_window_limit(self, rule: RateLimitRule, key: str) -> RateLimitResult:
        """Sliding window rate limiting"""
        if key not in self.sliding_windows:
            self.sliding_windows[key] = SlidingWindow(rule.window_size_seconds, rule.requests_per_window)
        
        window = self.sliding_windows[key]
        allowed, reset_time, remaining = window.is_allowed(time.time())
        
        return RateLimitResult(
            allowed=allowed,
            remaining_requests=remaining,
            reset_time=reset_time,
            retry_after=None if allowed else reset_time - time.time()
        )
    
    async def _fixed_window_limit(self, rule: RateLimitRule, key: str) -> RateLimitResult:
        """Fixed window rate limiting"""
        if key not in self.fixed_windows:
            self.fixed_windows[key] = FixedWindow(rule.window_size_seconds, rule.requests_per_window)
        
        window = self.fixed_windows[key]
        allowed, reset_time, remaining = window.is_allowed(time.time())
        
        return RateLimitResult(
            allowed=allowed,
            remaining_requests=remaining,
            reset_time=reset_time,
            retry_after=None if allowed else reset_time - time.time()
        )
    
    async def _distributed_limit(self, rule: RateLimitRule, key: str) -> RateLimitResult:
        """Distributed rate limiting using Redis"""
        if not self.redis_client:
            # Fallback to local sliding window
            return await self._sliding_window_limit(rule, key)
        
        try:
            # Use Redis sliding window algorithm
            now = time.time()
            window_start = now - rule.window_size_seconds
            
            # Remove old entries
            await self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            current_requests = await self.redis_client.zcard(key)
            
            if current_requests < rule.requests_per_window:
                # Add this request
                await self.redis_client.zadd(key, {str(now): now})
                # Set expiration
                await self.redis_client.expire(key, rule.window_size_seconds)
                
                remaining = rule.requests_per_window - current_requests - 1
                return RateLimitResult(
                    allowed=True,
                    remaining_requests=remaining,
                    reset_time=now + rule.window_size_seconds
                )
            
            # Get oldest request to calculate retry after
            oldest = await self.redis_client.zrange(key, 0, 0, withscores=True)
            if oldest:
                oldest_timestamp = float(oldest[0][1])
                retry_after = oldest_timestamp + rule.window_size_seconds - now
            else:
                retry_after = rule.window_size_seconds
            
            return RateLimitResult(
                allowed=False,
                remaining_requests=0,
                reset_time=now + rule.window_size_seconds,
                retry_after=retry_after
            )
        
        except Exception as e:
            logger.error(f"Redis rate limiting error: {e}")
            # Fallback to local sliding window
            return await self._sliding_window_limit(rule, key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        stats = {
            'total_rules': len(self.rules),
            'active_buckets': len(self.token_buckets),
            'active_sliding_windows': len(self.sliding_windows),
            'active_fixed_windows': len(self.fixed_windows),
            'redis_connected': self.redis_client is not None,
            'rules': []
        }
        
        for rule in self.rules:
            rule_stats = {
                'identifier': rule.identifier,
                'strategy': rule.strategy.value,
                'requests_per_window': rule.requests_per_window,
                'window_size_seconds': rule.window_size_seconds,
                'enabled': rule.enabled,
                'priority': rule.priority
            }
            stats['rules'].append(rule_stats)
        
        return stats
    
    def cleanup_expired_data(self):
        """Clean up expired rate limiting data"""
        current_time = time.time()
        
        # Clean up old token buckets (could be improved with LRU)
        if len(self.token_buckets) > 10000:
            # Remove buckets that haven't been used recently
            # This is a simple cleanup - in production you'd want a more sophisticated approach
            keys_to_remove = list(self.token_buckets.keys())[:5000]
            for key in keys_to_remove:
                del self.token_buckets[key]
        
        # Similar cleanup for sliding and fixed windows
        if len(self.sliding_windows) > 10000:
            keys_to_remove = list(self.sliding_windows.keys())[:5000]
            for key in keys_to_remove:
                del self.sliding_windows[key]
        
        if len(self.fixed_windows) > 10000:
            keys_to_remove = list(self.fixed_windows.keys())[:5000]
            for key in keys_to_remove:
                del self.fixed_windows[key]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting"""
    
    def __init__(self, app, rate_limiter: RateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter
    
    async def dispatch(self, request: Request, call_next):
        """Process request through rate limiting"""
        # Check rate limit
        result = await self.rate_limiter.check_rate_limit(request)
        
        # Add rate limit headers
        headers = {
            'X-RateLimit-Remaining': str(result.remaining_requests),
            'X-RateLimit-Reset': str(int(result.reset_time))
        }
        
        if not result.allowed:
            # Add retry after header if available
            if result.retry_after:
                headers['Retry-After'] = str(int(result.retry_after))
            
            # Log rate limit hit
            logger.warning(
                f"Rate limit exceeded for {result.identifier} "
                f"(rule: {result.rule_id}, retry_after: {result.retry_after})"
            )
            
            return Response(
                content=json.dumps({
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests',
                    'retry_after': result.retry_after,
                    'rule_id': result.rule_id
                }),
                status_code=429,
                headers=headers,
                media_type='application/json'
            )
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to response
        for key, value in headers.items():
            response.headers[key] = value
        
        return response


# Global rate limiter instance
rate_limiter = RateLimiter()
