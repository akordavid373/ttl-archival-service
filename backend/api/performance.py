from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timedelta
import psutil
import time
import random

router = APIRouter(prefix="/api/performance", tags=["performance"])

@router.get("/metrics")
async def get_performance_metrics():
    """Get real-time performance metrics"""
    try:
        # Get system metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Simulate API metrics
        api_response_time = random.uniform(50, 300)
        error_rate = random.uniform(0, 0.05)
        active_users = random.randint(50, 200)
        requests_per_second = random.randint(20, 80)
        db_connections = random.randint(3, 15)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpuUsage": cpu_usage,
            "memoryUsage": memory.percent,
            "diskUsage": (disk.used / disk.total) * 100,
            "apiResponseTime": api_response_time,
            "errorRate": error_rate,
            "activeUsers": active_users,
            "requestsPerSecond": requests_per_second,
            "databaseConnections": db_connections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@router.get("/metrics/history")
async def get_performance_history(hours: int = 24):
    """Get historical performance metrics"""
    try:
        # Generate sample historical data
        metrics = []
        base_time = datetime.utcnow() - timedelta(hours=hours)
        
        for i in range(hours * 12):  # 5-minute intervals
            timestamp = base_time + timedelta(minutes=i * 5)
            metrics.append({
                "timestamp": timestamp.isoformat(),
                "cpuUsage": random.uniform(20, 80),
                "memoryUsage": random.uniform(40, 90),
                "diskUsage": random.uniform(30, 70),
                "apiResponseTime": random.uniform(50, 300),
                "errorRate": random.uniform(0, 0.05),
                "activeUsers": random.randint(50, 200),
                "requestsPerSecond": random.randint(20, 80),
                "databaseConnections": random.randint(3, 15)
            })
        
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance history: {str(e)}")

@router.get("/alerts")
async def get_performance_alerts():
    """Get performance alerts"""
    try:
        # Sample alerts
        alerts = [
            {
                "id": "1",
                "type": "warning",
                "message": "CPU usage approaching threshold (85%)",
                "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "resolved": False
            },
            {
                "id": "2", 
                "type": "error",
                "message": "Database connection pool exhausted",
                "timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
                "resolved": False
            }
        ]
        
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance alerts: {str(e)}")

@router.post("/alerts")
async def create_performance_alert(alert: dict):
    """Create a new performance alert"""
    try:
        # In a real implementation, this would save to database
        alert_data = {
            "id": str(int(time.time())),
            "type": alert.get("type", "info"),
            "message": alert.get("message", ""),
            "timestamp": datetime.utcnow().isoformat(),
            "resolved": False
        }
        
        return alert_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create performance alert: {str(e)}")

@router.put("/alerts/{alert_id}/resolve")
async def resolve_performance_alert(alert_id: str):
    """Resolve a performance alert"""
    try:
        # In a real implementation, this would update the database
        return {"id": alert_id, "resolved": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve performance alert: {str(e)}")

@router.get("/health")
async def get_system_health():
    """Get overall system health status"""
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Determine health status
        if cpu_usage > 90 or memory.percent > 95 or (disk.used / disk.total) * 100 > 95:
            status = "critical"
        elif cpu_usage > 70 or memory.percent > 80 or (disk.used / disk.total) * 100 > 80:
            status = "warning"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "cpu": {"status": "ok" if cpu_usage < 80 else "warning", "value": cpu_usage},
                "memory": {"status": "ok" if memory.percent < 80 else "warning", "value": memory.percent},
                "disk": {"status": "ok" if (disk.used / disk.total) * 100 < 80 else "warning", "value": (disk.used / disk.total) * 100}
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")
