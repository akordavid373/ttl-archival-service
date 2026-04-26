import platform
import sys
import psutil
from datetime import datetime

def get_system_diagnostics() -> dict:
    return {
        "system": platform.system(),
        "processor": platform.processor(),
        "python_version": sys.version,
        "cpu_count": psutil.cpu_count(logical=True),
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
        "timestamp": datetime.utcnow().isoformat()
    }