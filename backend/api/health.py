from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..services.health_service import HealthService

router = APIRouter(prefix="/api/v1/health", tags=["Health"])

try:
    from ..database import get_db
except ImportError:
    def get_db():
        yield None

@router.get("/")
def check_health(db: Session = Depends(get_db)):
    return HealthService.get_health_status(db)

@router.get("/diagnostics")
def get_diagnostics():
    return HealthService.get_diagnostics()