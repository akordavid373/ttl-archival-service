from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import dataclass, asdict
from enum import Enum

from ..utils.profiler import profiler, ProfileResult, QueryProfile

logger = logging.getLogger(__name__)

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PerformanceAlert:
    """Performance alert definition"""
    id: str
    name: str
    description: str
    severity: AlertSeverity
    threshold_value: float
    current_value: float
    metric_type: str
    timestamp: datetime
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class PerformanceMetrics:
    """Current performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_usage_mb: float
    disk_usage_percent: float
    network_io_bytes_sent: int
    network_io_bytes_recv: int
    active_connections: int
    request_rate: float
    error_rate: float
    avg_response_time_ms: float

class MonitoringService:
    """Service for monitoring system performance and generating alerts"""
    
    def __init__(self):
        self.alerts: List[PerformanceAlert] = []
        self.metrics_history: List[PerformanceMetrics] = []
        self.alert_rules = self._initialize_alert_rules()
        self._monitoring_enabled = True
    
    def _initialize_alert_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize default alert rules"""
        return {
            "high_cpu": {
                "name": "High CPU Usage",
                "description": "CPU usage exceeds threshold",
                "threshold": 80.0,
                "severity": AlertSeverity.HIGH,
                "metric": "cpu_percent"
            },
            "high_memory": {
                "name": "High Memory Usage",
                "description": "Memory usage exceeds threshold",
                "threshold": 85.0,
                "severity": AlertSeverity.HIGH,
                "metric": "memory_usage_mb"
            },
            "slow_requests": {
                "name": "Slow API Requests",
                "description": "Average response time exceeds threshold",
                "threshold": 2000.0,
                "severity": AlertSeverity.MEDIUM,
                "metric": "avg_response_time_ms"
            },
            "high_error_rate": {
                "name": "High Error Rate",
                "description": "Error rate exceeds threshold",
                "threshold": 10.0,
                "severity": AlertSeverity.CRITICAL,
                "metric": "error_rate"
            },
            "slow_database": {
                "name": "Slow Database Queries",
                "description": "Average query time exceeds threshold",
                "threshold": 1000.0,
                "severity": AlertSeverity.MEDIUM,
                "metric": "avg_query_duration_ms"
            }
        }
    
    async def collect_metrics(self) -> PerformanceMetrics:
        """Collect current system metrics"""
        try:
            import psutil
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # Get application metrics from profiler
            stats = profiler.get_stats()
            
            # Calculate request rate and error rate from recent requests
            recent_results = profiler.get_results(limit=100)
            total_requests = len(recent_results)
            error_requests = len([r for r in recent_results if not r.success])
            
            request_rate = total_requests / 60  # requests per minute (assuming 1-minute window)
            error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0
            
            metrics = PerformanceMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_usage_mb=memory.used / 1024 / 1024,
                disk_usage_percent=disk.percent,
                network_io_bytes_sent=network.bytes_sent,
                network_io_bytes_recv=network.bytes_recv,
                active_connections=len(psutil.net_connections()),
                request_rate=request_rate,
                error_rate=error_rate,
                avg_response_time_ms=stats.get('avg_duration_ms', 0)
            )
            
            # Store metrics history
            self.metrics_history.append(metrics)
            
            # Keep only last 24 hours of metrics
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            self.metrics_history = [m for m in self.metrics_history if m.timestamp > cutoff_time]
            
            # Check for alerts
            await self._check_alerts(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            raise
    
    async def _check_alerts(self, metrics: PerformanceMetrics):
        """Check metrics against alert rules and generate alerts"""
        try:
            for rule_id, rule in self.alert_rules.items():
                metric_value = getattr(metrics, rule['metric'], None)
                if metric_value is None:
                    continue
                
                if metric_value > rule['threshold']:
                    await self._create_alert(
                        rule_id=rule_id,
                        rule=rule,
                        current_value=metric_value
                    )
                else:
                    # Clear alert if condition is resolved
                    await self._clear_alert(rule_id)
        
        except Exception as e:
            logger.error(f"Failed to check alerts: {e}")
    
    async def _create_alert(self, rule_id: str, rule: Dict[str, Any], current_value: float):
        """Create or update an alert"""
        try:
            # Check if alert already exists
            existing_alert = next((a for a in self.alerts if a.id == rule_id), None)
            
            if existing_alert:
                # Update existing alert
                existing_alert.current_value = current_value
                existing_alert.timestamp = datetime.utcnow()
                existing_alert.is_active = True
            else:
                # Create new alert
                alert = PerformanceAlert(
                    id=rule_id,
                    name=rule['name'],
                    description=rule['description'],
                    severity=rule['severity'],
                    threshold_value=rule['threshold'],
                    current_value=current_value,
                    metric_type=rule['metric'],
                    timestamp=datetime.utcnow()
                )
                self.alerts.append(alert)
                
                logger.warning(f"Alert triggered: {alert.name} - {current_value:.2f} (threshold: {rule['threshold']})")
        
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
    
    async def _clear_alert(self, rule_id: str):
        """Clear an alert"""
        try:
            alert = next((a for a in self.alerts if a.id == rule_id), None)
            if alert and alert.is_active:
                alert.is_active = False
                logger.info(f"Alert cleared: {alert.name}")
        
        except Exception as e:
            logger.error(f"Failed to clear alert: {e}")
    
    def get_active_alerts(self) -> List[PerformanceAlert]:
        """Get all active alerts"""
        return [alert for alert in self.alerts if alert.is_active]
    
    def get_all_alerts(self) -> List[PerformanceAlert]:
        """Get all alerts (active and inactive)"""
        return self.alerts.copy()
    
    def get_metrics_history(self, hours: int = 24) -> List[PerformanceMetrics]:
        """Get metrics history for specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [m for m in self.metrics_history if m.timestamp > cutoff_time]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics_history:
            return {}
        
        latest_metrics = self.metrics_history[-1]
        stats = profiler.get_stats()
        
        return {
            'current_metrics': asdict(latest_metrics),
            'profiling_stats': stats,
            'active_alerts_count': len(self.get_active_alerts()),
            'total_alerts_count': len(self.alerts),
            'slow_operations': len(profiler.get_slow_operations()),
            'slow_queries': len(profiler.get_slow_queries()),
            'uptime_hours': (datetime.utcnow() - (self.metrics_history[0].timestamp if self.metrics_history else datetime.utcnow())).total_seconds() / 3600
        }
    
    def get_slow_operations_report(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get report of slow operations"""
        slow_ops = profiler.get_slow_operations()
        
        return [
            {
                'operation_name': op.operation_name,
                'duration_ms': op.duration_ms,
                'memory_usage_mb': op.memory_usage_mb,
                'timestamp': op.start_time.isoformat(),
                'metadata': op.metadata
            }
            for op in sorted(slow_ops, key=lambda x: x.duration_ms, reverse=True)[:limit]
        ]
    
    def get_database_performance_report(self) -> Dict[str, Any]:
        """Get database performance report"""
        query_profiles = profiler.get_query_profiles()
        
        if not query_profiles:
            return {'total_queries': 0}
        
        slow_queries = profiler.get_slow_queries()
        
        return {
            'total_queries': len(query_profiles),
            'slow_queries_count': len(slow_queries),
            'avg_query_duration_ms': sum(q.duration_ms for q in query_profiles) / len(query_profiles),
            'max_query_duration_ms': max(q.duration_ms for q in query_profiles),
            'total_rows_affected': sum(q.rows_affected for q in query_profiles),
            'failed_queries_count': len([q for q in query_profiles if not q.success]),
            'slow_queries': [
                {
                    'query': q.query[:100] + '...' if len(q.query) > 100 else q.query,
                    'duration_ms': q.duration_ms,
                    'rows_affected': q.rows_affected,
                    'timestamp': q.timestamp.isoformat()
                }
                for q in sorted(slow_queries, key=lambda x: x.duration_ms, reverse=True)[:10]
            ]
        }
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
    
    def enable_monitoring(self):
        """Enable performance monitoring"""
        self._monitoring_enabled = True
        profiler.enable()
    
    def disable_monitoring(self):
        """Disable performance monitoring"""
        self._monitoring_enabled = False
        profiler.disable()
    
    def is_monitoring_enabled(self) -> bool:
        """Check if monitoring is enabled"""
        return self._monitoring_enabled

# Global monitoring service instance
monitoring_service = MonitoringService()
