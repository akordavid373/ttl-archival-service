import os
from sqlalchemy.orm import Session
from ..checks.health_checks import check_database, check_redis, check_disk_space, check_memory, check_file_system
from ..utils.diagnostics import get_system_diagnostics

class HealthService:
    @staticmethod
    def get_health_status(db: Session = None) -> dict:
        redis_url = os.getenv("RATE_LIMIT_REDIS_URL", "redis://localhost:6379/0")
        
        db_status = check_database(db)
        redis_status = check_redis(redis_url)
        disk_status = check_disk_space()
        memory_status = check_memory()
        fs_status = check_file_system()
        
        is_healthy = db_status and redis_status and fs_status and disk_status["percent"] < 90 and memory_status["percent"] < 90
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "checks": {
                "database": "up" if db_status else "down",
                "redis": "up" if redis_status else "down",
                "file_system": "ok" if fs_status else "error",
                "disk": "ok" if disk_status["percent"] < 90 else "warning",
                "memory": "ok" if memory_status["percent"] < 90 else "warning"
            },
            "metrics": {
                "disk": disk_status,
                "memory": memory_status
            }
        }

    @staticmethod
    def get_diagnostics() -> dict:
        return get_system_diagnostics()