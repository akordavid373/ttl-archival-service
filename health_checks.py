import os
import psutil
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis

def check_database(db: Session) -> bool:
    try:
        if db is None:
            return False
        db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

def check_redis(redis_url: str) -> bool:
    try:
        r = redis.Redis.from_url(redis_url)
        return r.ping()
    except Exception:
        return False

def check_disk_space(path: str = "/") -> dict:
    usage = psutil.disk_usage(path)
    return {
        "total": usage.total,
        "used": usage.used,
        "free": usage.free,
        "percent": usage.percent
    }

def check_memory() -> dict:
    mem = psutil.virtual_memory()
    return {
        "total": mem.total,
        "available": mem.available,
        "percent": mem.percent,
        "used": mem.used
    }

def check_file_system(path: str = ".") -> bool:
    try:
        test_file = os.path.join(path, ".healthcheck")
        with open(test_file, 'w') as f:
            f.write("ok")
        os.remove(test_file)
        return True
    except Exception:
        return False