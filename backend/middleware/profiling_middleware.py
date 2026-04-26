from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable
import time
import psutil
import logging
from datetime import datetime

from ..utils.profiler import profiler, ProfileResult

logger = logging.getLogger(__name__)

class ProfilingMiddleware(BaseHTTPMiddleware):
    """Middleware for profiling HTTP requests"""
    
    def __init__(self, app: ASGIApp, exclude_paths: list = None, slow_request_threshold_ms: float = 1000.0):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/api/v1/data/export", "/api/v1/data/import"]
        self.slow_request_threshold_ms = slow_request_threshold_ms
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Profile incoming HTTP request"""
        # Skip profiling for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        start_time = datetime.utcnow()
        start_memory = self._get_memory_usage()
        start_cpu = psutil.cpu_percent()
        
        # Process request
        response = await call_next(request)
        
        # Calculate metrics
        end_time = datetime.utcnow()
        end_memory = self._get_memory_usage()
        end_cpu = psutil.cpu_percent()
        
        duration_ms = (end_time - start_time).total_seconds() * 1000
        memory_usage_mb = end_memory - start_memory
        cpu_percent = end_cpu - start_cpu
        
        # Create profile result
        result = ProfileResult(
            operation_name=f"{request.method} {request.url.path}",
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            memory_usage_mb=memory_usage_mb,
            cpu_percent=cpu_percent,
            success=response.status_code < 400,
            metadata={
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "status_code": response.status_code,
                "user_agent": request.headers.get("user-agent"),
                "client_ip": request.client.host if request.client else None
            }
        )
        
        # Store result
        profiler.results.append(result)
        
        # Log slow requests
        if duration_ms > self.slow_request_threshold_ms:
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path} "
                f"- {duration_ms:.2f}ms (threshold: {self.slow_request_threshold_ms}ms)"
            )
        
        # Add profiling headers
        response.headers["X-Profiler-Duration-Ms"] = str(duration_ms)
        response.headers["X-Profiler-Memory-MB"] = str(memory_usage_mb)
        
        return response
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0
