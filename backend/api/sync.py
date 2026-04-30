import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..database import get_db
from ..schemas.sync import (
    SyncJobCreate, 
    SyncJobResponse, 
    SyncJobStatus, 
    SyncConflictResponse,
    SyncRecordResponse
)
from ..services.sync_service import SyncService

router = APIRouter()
sync_service = SyncService()

@router.post("/jobs", response_model=SyncJobResponse, status_code=status.HTTP_201_CREATED)
async def create_sync_job(job_data: SyncJobCreate, db: Session = Depends(get_db)):
    """
    Create a new data synchronization job.
    """
    try:
        return sync_service.create_sync_job(db, job_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/jobs/{job_id}/start", response_model=SyncJobResponse)
async def start_sync(job_id: UUID, db: Session = Depends(get_db)):
    """
    Start a previously created synchronization job.
    """
    try:
        return sync_service.start_sync(db, job_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/jobs/{job_id}/status", response_model=SyncJobStatus)
async def get_sync_status(job_id: UUID, db: Session = Depends(get_db)):
    """
    Get progress metrics and status for a sync job.
    """
    try:
        return sync_service.get_sync_status(db, job_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/jobs/{job_id}/pause")
async def pause_sync(job_id: UUID, db: Session = Depends(get_db)):
    """
    Pause a running sync job.
    """
    try:
        sync_service.pause_sync(db, job_id)
        return {"message": "Sync job paused", "job_id": job_id}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/jobs/{job_id}/resume")
async def resume_sync(job_id: UUID, db: Session = Depends(get_db)):
    """
    Resume a paused sync job.
    """
    try:
        sync_service.resume_sync(db, job_id)
        return {"message": "Sync job resumed", "job_id": job_id}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/conflicts/{conflict_id}/resolve")
async def resolve_conflict(
    conflict_id: UUID, 
    resolution: str = Query(..., regex="^(SOURCE_WINS|TARGET_WINS)$"),
    resolved_by: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Manually resolve a data conflict by choosing either source or target data.
    """
    try:
        await sync_service.resolve_conflict(db, conflict_id, resolution, resolved_by)
        return {"message": "Conflict resolved and record synced", "conflict_id": conflict_id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
