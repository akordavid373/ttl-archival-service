import time
import functools
import asyncio
import threading
import psutil
import traceback
from typing import Dict, Any, Optional, Callable, Union
from datetime import datetime
from contextlib import contextmanager, asynccontextmanager
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProfileResult:
    """Result of a profiling operation"""
    operation_name: str
    start_time: datetime
    end_time: datetime
    duration_ms: float
    memory_usage_mb: float
    cpu_percent: float
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class QueryProfile:
    """Database query profile"""
    query: str
    duration_ms: float
    rows_affected: int
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None

class Profiler:
    """Performance profiler for tracking operations and resource usage"""
    
    def __init__(self):
        self.results: List[ProfileResult] = []
        self.query_profiles: List[QueryProfile] = []
        self._lock = threading.Lock()
        self._enabled = True
    
    def enable(self):
        """Enable profiling"""
        self._enabled = True
    
    def disable(self):
        """Disable profiling"""
        self._enabled = False
    
    def is_enabled(self) -> bool:
        """Check if profiling is enabled"""
        return self._enabled
    
    @contextmanager
    def profile(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None):
        """Context manager for profiling synchronous operations"""
        if not self._enabled:
            yield
            return
        
        start_time = datetime.utcnow()
        start_memory = self._get_memory_usage()
        start_cpu = psutil.cpu_percent()
        
        try:
            yield
            success = True
            error_message = None
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            end_time = datetime.utcnow()
            end_memory = self._get_memory_usage()
            end_cpu = psutil.cpu_percent()
            
            duration_ms = (end_time - start_time).total_seconds() * 1000
            memory_usage_mb = end_memory - start_memory
            cpu_percent = end_cpu - start_cpu
            
            result = ProfileResult(
                operation_name=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                memory_usage_mb=memory_usage_mb,
                cpu_percent=cpu_percent,
                success=success,
                error_message=error_message,
                metadata=metadata
            )
            
            with self._lock:
                self.results.append(result)
            
            logger.debug(f"Profiled {operation_name}: {duration_ms:.2f}ms, {memory_usage_mb:.2f}MB")
    
    @asynccontextmanager
    async def profile_async(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None):
        """Async context manager for profiling asynchronous operations"""
        if not self._enabled:
            yield
            return
        
        start_time = datetime.utcnow()
        start_memory = self._get_memory_usage()
        start_cpu = psutil.cpu_percent()
        
        try:
            yield
            success = True
            error_message = None
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            end_time = datetime.utcnow()
            end_memory = self._get_memory_usage()
            end_cpu = psutil.cpu_percent()
            
            duration_ms = (end_time - start_time).total_seconds() * 1000
            memory_usage_mb = end_memory - start_memory
            cpu_percent = end_cpu - start_cpu
            
            result = ProfileResult(
                operation_name=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                memory_usage_mb=memory_usage_mb,
                cpu_percent=cpu_percent,
                success=success,
                error_message=error_message,
                metadata=metadata
            )
            
            with self._lock:
                self.results.append(result)
            
            logger.debug(f"Profiled async {operation_name}: {duration_ms:.2f}ms, {memory_usage_mb:.2f}MB")
    
    def profile_function(self, operation_name: Optional[str] = None):
        """Decorator for profiling functions"""
        def decorator(func: Callable):
            name = operation_name or f"{func.__module__}.{func.__name__}"
            
            if asyncio.iscoroutinefunction(func):
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    async with self.profile_async(name):
                        return await func(*args, **kwargs)
                return async_wrapper
            else:
                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs):
                    with self.profile(name):
                        return func(*args, **kwargs)
                return sync_wrapper
        
        return decorator
    
    def profile_query(self, query: str, duration_ms: float, rows_affected: int, 
                     success: bool = True, error_message: Optional[str] = None):
        """Profile a database query"""
        if not self._enabled:
            return
        
        profile = QueryProfile(
            query=query,
            duration_ms=duration_ms,
            rows_affected=rows_affected,
            timestamp=datetime.utcnow(),
            success=success,
            error_message=error_message
        )
        
        with self._lock:
            self.query_profiles.append(profile)
        
        logger.debug(f"Profiled query: {duration_ms:.2f}ms, {rows_affected} rows")
    
    def get_results(self, limit: Optional[int] = None) -> List[ProfileResult]:
        """Get profiling results"""
        with self._lock:
            if limit:
                return self.results[-limit:]
            return self.results.copy()
    
    def get_query_profiles(self, limit: Optional[int] = None) -> List[QueryProfile]:
        """Get query profiles"""
        with self._lock:
            if limit:
                return self.query_profiles[-limit:]
            return self.query_profiles.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get profiling statistics"""
        with self._lock:
            if not self.results:
                return {}
            
            successful_results = [r for r in self.results if r.success]
            failed_results = [r for r in self.results if not r.success]
            
            durations = [r.duration_ms for r in successful_results]
            memory_usage = [r.memory_usage_mb for r in successful_results]
            
            return {
                'total_operations': len(self.results),
                'successful_operations': len(successful_results),
                'failed_operations': len(failed_results),
                'success_rate': len(successful_results) / len(self.results) * 100,
                'avg_duration_ms': sum(durations) / len(durations) if durations else 0,
                'max_duration_ms': max(durations) if durations else 0,
                'min_duration_ms': min(durations) if durations else 0,
                'avg_memory_usage_mb': sum(memory_usage) / len(memory_usage) if memory_usage else 0,
                'max_memory_usage_mb': max(memory_usage) if memory_usage else 0,
                'total_queries': len(self.query_profiles),
                'avg_query_duration_ms': sum(q.duration_ms for q in self.query_profiles) / len(self.query_profiles) if self.query_profiles else 0
            }
    
    def clear_results(self):
        """Clear all profiling results"""
        with self._lock:
            self.results.clear()
            self.query_profiles.clear()
    
    def get_slow_operations(self, threshold_ms: float = 1000.0) -> List[ProfileResult]:
        """Get operations slower than threshold"""
        with self._lock:
            return [r for r in self.results if r.duration_ms > threshold_ms]
    
    def get_slow_queries(self, threshold_ms: float = 500.0) -> List[QueryProfile]:
        """Get queries slower than threshold"""
        with self._lock:
            return [q for q in self.query_profiles if q.duration_ms > threshold_ms]
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0

# Global profiler instance
profiler = Profiler()

def profile(operation_name: Optional[str] = None):
    """Decorator for profiling functions"""
    return profiler.profile_function(operation_name)

def profile_query(query: str, duration_ms: float, rows_affected: int, 
                 success: bool = True, error_message: Optional[str] = None):
    """Profile a database query"""
    profiler.profile_query(query, duration_ms, rows_affected, success, error_message)
