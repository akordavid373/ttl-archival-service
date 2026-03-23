from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import logging

from .database import get_db, engine
from .models import Base, UserSettings
from .schemas import (
    ArchiveRecordCreate, ArchiveRecordResponse, 
    ArchivePolicyCreate, ArchivePolicyResponse,
    UserSettingsUpdate, UserSettingsResponse
)
from .services import ArchiveService, PolicyService, SettingsService
from .scheduler import ArchiveScheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TTL-Aware Automated Archival Service",
    description="A service for automated data archival with TTL-based cleanup",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
archive_service = ArchiveService()
policy_service = PolicyService()
settings_service = SettingsService()
scheduler = ArchiveScheduler()

@app.on_event("startup")
async def startup_event():
    """Initialize the archive scheduler on startup"""
    await scheduler.start()
    logger.info("Archive scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    await scheduler.stop()
    logger.info("Archive scheduler stopped")

@app.post("/api/v1/policies", response_model=ArchivePolicyResponse)
async def create_policy(
    policy: ArchivePolicyCreate,
    db: Session = Depends(get_db)
):
    """Create a new archival policy"""
    try:
        return await policy_service.create_policy(db, policy)
    except Exception as e:
        logger.error(f"Error creating policy: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/policies", response_model=List[ArchivePolicyResponse])
async def list_policies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all archival policies"""
    return await policy_service.list_policies(db, skip, limit)

@app.get("/api/v1/policies/{policy_id}", response_model=ArchivePolicyResponse)
async def get_policy(
    policy_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific archival policy"""
    policy = await policy_service.get_policy(db, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@app.post("/api/v1/archives", response_model=ArchiveRecordResponse)
async def create_archive_record(
    record: ArchiveRecordCreate,
    db: Session = Depends(get_db)
):
    """Create a new archive record"""
    try:
        return await archive_service.create_record(db, record)
    except Exception as e:
        logger.error(f"Error creating archive record: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/archives", response_model=List[ArchiveRecordResponse])
async def list_archives(
    skip: int = 0,
    limit: int = 100,
    policy_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List archive records with optional filtering"""
    return await archive_service.list_records(db, skip, limit, policy_id, status)

@app.get("/api/v1/archives/{record_id}", response_model=ArchiveRecordResponse)
async def get_archive_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific archive record"""
    record = await archive_service.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Archive record not found")
    return record

@app.delete("/api/v1/archives/{record_id}")
async def delete_archive_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """Manually delete an archive record"""
    success = await archive_service.delete_record(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Archive record not found")
    return {"message": "Archive record deleted successfully"}

@app.post("/api/v1/archives/cleanup")
async def trigger_cleanup(
    policy_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Manually trigger cleanup for expired records"""
    try:
        deleted_count = await archive_service.cleanup_expired_records(db, policy_id)
        return {"message": f"Cleaned up {deleted_count} expired records"}
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/api/v1/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get archival service statistics"""
    return await archive_service.get_stats(db)

@app.get("/api/v1/settings", response_model=UserSettingsResponse)
async def get_settings(db: Session = Depends(get_db)):
    """Get archival service settings"""
    return await settings_service.get_settings(db)

@app.patch("/api/v1/settings", response_model=UserSettingsResponse)
async def update_settings(
    settings_update: UserSettingsUpdate,
    db: Session = Depends(get_db)
):
    """Update archival service settings"""
    try:
        return await settings_service.update_settings(db, settings_update.dict(exclude_unset=True))
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
