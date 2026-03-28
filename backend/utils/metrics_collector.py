import psutil
import time
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System metrics snapshot"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    memory_used_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    process_count: int

@dataclass
class ApplicationMetrics:
    """Application-specific metrics"""
    timestamp: datetime
    request_count: int
    error_count: int
    avg_response_time_ms: float
    active_requests: int
    database_connections: int
    cache_hit_rate: float

class MetricsCollector:
    """Collects system and application metrics"""
    
    def __init__(self, collection_interval: int = 60):
        self.collection_interval = collection_interval
        self.system_metrics: List[SystemMetrics] = []
        self.application_metrics: List[ApplicationMetrics] = []
        self._collection_thread = None
        self._stop_collection = False
        self._lock = threading.Lock()
    
    def start_collection(self):
        """Start background metrics collection"""
        if self._collection_thread and self._collection_thread.is_alive():
            return
        
        self._stop_collection = False
        self._collection_thread = threading.Thread(target=self._collect_loop, daemon=True)
        self._collection_thread.start()
        logger.info("Metrics collection started")
    
    def stop_collection(self):
        """Stop background metrics collection"""
        self._stop_collection = True
        if self._collection_thread:
            self._collection_thread.join(timeout=5)
        logger.info("Metrics collection stopped")
    
    def _collect_loop(self):
        """Background collection loop"""
        while not self._stop_collection:
            try:
                self._collect_system_metrics()
                self._collect_application_metrics()
                time.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                time.sleep(self.collection_interval)
    
    def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_mb = memory.available / 1024 / 1024
            memory_used_mb = memory.used / 1024 / 1024
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            disk_free_gb = disk.free / 1024 / 1024 / 1024
            
            # Network metrics
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv
            
            # Connection metrics
            active_connections = len(psutil.net_connections())
            
            # Process metrics
            process_count = len(psutil.pids())
            
            metrics = SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_mb=memory_available_mb,
                memory_used_mb=memory_used_mb,
                disk_usage_percent=disk_usage_percent,
                disk_free_gb=disk_free_gb,
                network_bytes_sent=network_bytes_sent,
                network_bytes_recv=network_bytes_recv,
                active_connections=active_connections,
                process_count=process_count
            )
            
            with self._lock:
                self.system_metrics.append(metrics)
                # Keep only last 24 hours of data
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.system_metrics = [m for m in self.system_metrics if m.timestamp > cutoff_time]
        
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    def _collect_application_metrics(self):
        """Collect application-level metrics"""
        try:
            # These would typically be collected from application state
            # For now, we'll use placeholder values
            metrics = ApplicationMetrics(
                timestamp=datetime.utcnow(),
                request_count=0,  # Would be collected from request counter
                error_count=0,    # Would be collected from error counter
                avg_response_time_ms=0.0,  # Would be calculated from response times
                active_requests=0,  # Would be tracked via middleware
                database_connections=0,  # Would be collected from connection pool
                cache_hit_rate=0.0  # Would be collected from cache stats
            )
            
            with self._lock:
                self.application_metrics.append(metrics)
                # Keep only last 24 hours of data
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.application_metrics = [m for m in self.application_metrics if m.timestamp > cutoff_time]
        
        except Exception as e:
            logger.error(f"Failed to collect application metrics: {e}")
    
    def get_current_system_metrics(self) -> Optional[SystemMetrics]:
        """Get the most recent system metrics"""
        with self._lock:
            return self.system_metrics[-1] if self.system_metrics else None
    
    def get_current_application_metrics(self) -> Optional[ApplicationMetrics]:
        """Get the most recent application metrics"""
        with self._lock:
            return self.application_metrics[-1] if self.application_metrics else None
    
    def get_system_metrics_history(self, hours: int = 24) -> List[SystemMetrics]:
        """Get system metrics history"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        with self._lock:
            return [m for m in self.system_metrics if m.timestamp > cutoff_time]
    
    def get_application_metrics_history(self, hours: int = 24) -> List[ApplicationMetrics]:
        """Get application metrics history"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        with self._lock:
            return [m for m in self.application_metrics if m.timestamp > cutoff_time]
    
    def get_resource_usage_summary(self) -> Dict[str, Any]:
        """Get summary of resource usage"""
        current_system = self.get_current_system_metrics()
        current_app = self.get_current_application_metrics()
        
        if not current_system:
            return {}
        
        # Calculate averages over the last hour
        recent_system = self.get_system_metrics_history(hours=1)
        
        if recent_system:
            avg_cpu = sum(m.cpu_percent for m in recent_system) / len(recent_system)
            avg_memory = sum(m.memory_percent for m in recent_system) / len(recent_system)
            max_cpu = max(m.cpu_percent for m in recent_system)
            max_memory = max(m.memory_percent for m in recent_system)
        else:
            avg_cpu = max_cpu = current_system.cpu_percent
            avg_memory = max_memory = current_system.memory_percent
        
        return {
            'current': {
                'cpu_percent': current_system.cpu_percent,
                'memory_percent': current_system.memory_percent,
                'disk_usage_percent': current_system.disk_usage_percent,
                'active_connections': current_system.active_connections,
                'process_count': current_system.process_count
            },
            'averages_last_hour': {
                'cpu_percent': avg_cpu,
                'memory_percent': avg_memory
            },
            'peaks_last_hour': {
                'cpu_percent': max_cpu,
                'memory_percent': max_memory
            },
            'application': {
                'request_count': current_app.request_count if current_app else 0,
                'error_count': current_app.error_count if current_app else 0,
                'avg_response_time_ms': current_app.avg_response_time_ms if current_app else 0,
                'active_requests': current_app.active_requests if current_app else 0
            }
        }
    
    def check_resource_thresholds(self, cpu_threshold: float = 80.0, 
                               memory_threshold: float = 85.0, 
                               disk_threshold: float = 90.0) -> Dict[str, bool]:
        """Check if resource usage exceeds thresholds"""
        current = self.get_current_system_metrics()
        if not current:
            return {}
        
        return {
            'cpu_exceeded': current.cpu_percent > cpu_threshold,
            'memory_exceeded': current.memory_percent > memory_threshold,
            'disk_exceeded': current.disk_usage_percent > disk_threshold,
            'cpu_threshold': cpu_threshold,
            'memory_threshold': memory_threshold,
            'disk_threshold': disk_threshold
        }
    
    @contextmanager
    def measure_operation(self, operation_name: str):
        """Context manager to measure operation performance"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            duration_ms = (end_time - start_time) * 1000
            memory_delta_mb = end_memory - start_memory
            
            logger.debug(f"Operation {operation_name}: {duration_ms:.2f}ms, {memory_delta_mb:+.2f}MB memory")
    
    def clear_metrics(self):
        """Clear all collected metrics"""
        with self._lock:
            self.system_metrics.clear()
            self.application_metrics.clear()

# Global metrics collector instance
metrics_collector = MetricsCollector()
