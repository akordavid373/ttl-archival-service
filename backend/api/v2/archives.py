from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from ...database import get_db
from ...services import ArchiveService
from ...schemas import (
    ArchiveRecordCreate, ArchiveRecordResponse, 
    ArchiveListParams, ArchiveListResponse
)
from ...utils.audit_logger import audit_logger_instance, AuditAction

logger = logging.getLogger(__name__)
router = APIRouter()

# Enhanced schemas for v2
class ArchiveRecordCreateV2(BaseModel):
    """Enhanced archive record creation schema for v2"""
    original_data_id: str = Field(..., description="Original data identifier")
    data: str = Field(..., description="Archived data content")
    metadata: Optional[dict] = Field(None, description="Enhanced metadata")
    policy_id: int = Field(..., description="Archive policy ID")
    tags: Optional[List[str]] = Field(default_factory=list, description="Data tags")
    priority: Optional[str] = Field("normal", description="Archive priority")
    retention_override: Optional[int] = Field(None, description="Override retention period in days")
    
    class Config:
        schema_extra = {
            "example": {
                "original_data_id": "user_data_12345",
                "data": "Sample archived data",
                "metadata": {"source": "user_upload", "category": "personal"},
                "policy_id": 1,
                "tags": ["user_data", "personal"],
                "priority": "high",
                "retention_override": 365
            }
        }

class ArchiveRecordResponseV2(BaseModel):
    """Enhanced archive record response schema for v2"""
    id: int
    original_data_id: str
    data: str
    metadata: Optional[dict]
    policy_id: int
    status: str
    created_at: datetime
    expires_at: Optional[datetime]
    tags: List[str]
    priority: str
    size_bytes: int
    hash_value: str
    access_count: int
    last_accessed: Optional[datetime]
    retention_days: int
    days_until_expiry: Optional[int]

class BatchArchiveRequest(BaseModel):
    """Batch archive creation request"""
    archives: List[ArchiveRecordCreateV2]
    validate_all: bool = Field(True, description="Validate all records before processing")
    
class BatchArchiveResponse(BaseModel):
    """Batch archive creation response"""
    successful: List[ArchiveRecordResponseV2]
    failed: List[dict]
    total_processed: int
    success_count: int
    failure_count: int

class ArchiveSearchParams(BaseModel):
    """Enhanced search parameters for v2"""
    query: Optional[str] = None
    policy_id: Optional[int] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    priority: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    size_min: Optional[int] = None
    size_max: Optional[int] = None
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    sort_by: str = Field("created_at", description="Field to sort by")
    sort_order: str = Field("desc", regex="^(asc|desc)$")

# Initialize service
archive_service = ArchiveService()

@router.post("/", response_model=ArchiveRecordResponseV2, status_code=201)
async def create_archive(
    archive: ArchiveRecordCreateV2,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new archive record with enhanced features"""
    try:
        # Convert v2 schema to internal format
        create_data = ArchiveRecordCreate(
            original_data_id=archive.original_data_id,
            data=archive.data,
            metadata=archive.metadata,
            policy_id=archive.policy_id
        )
        
        result = await archive_service.create_record(db, create_data)
        
        # Add background task for enhanced processing
        background_tasks.add_task(
            _process_archive_enhancements,
            result.id,
            archive.tags,
            archive.priority,
            archive.retention_override
        )
        
        # Convert to v2 response format
        return _to_v2_response(result)
        
    except Exception as e:
        logger.error(f"Error creating archive record: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/batch", response_model=BatchArchiveResponse, status_code=201)
async def create_archives_batch(
    request: BatchArchiveRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create multiple archive records in a batch"""
    successful = []
    failed = []
    
    for i, archive in enumerate(request.archives):
        try:
            # Convert v2 schema to internal format
            create_data = ArchiveRecordCreate(
                original_data_id=archive.original_data_id,
                data=archive.data,
                metadata=archive.metadata,
                policy_id=archive.policy_id
            )
            
            result = await archive_service.create_record(db, create_data)
            
            # Add background task for enhancements
            background_tasks.add_task(
                _process_archive_enhancements,
                result.id,
                archive.tags,
                archive.priority,
                archive.retention_override
            )
            
            successful.append(_to_v2_response(result))
            
        except Exception as e:
            failed.append({
                "index": i,
                "original_data_id": archive.original_data_id,
                "error": str(e)
            })
            
            # If validate_all is True, stop on first error
            if request.validate_all:
                break
    
    return BatchArchiveResponse(
        successful=successful,
        failed=failed,
        total_processed=len(request.archives),
        success_count=len(successful),
        failure_count=len(failed)
    )

@router.get("/", response_model=dict)
async def list_archives(
    params: ArchiveSearchParams = Depends(),
    db: Session = Depends(get_db)
):
    """List archive records with enhanced filtering and search"""
    try:
        records, total = await archive_service.list_records_advanced(
            db=db,
            page=params.page,
            limit=params.limit,
            policy_id=params.policy_id,
            status=params.status,
            date_from=params.date_from,
            date_to=params.date_to,
            search=params.query,
            min_size=params.size_min,
            max_size=params.size_max,
            sort_field=params.sort_by,
            sort_order=params.sort_order
        )
        
        # Convert to v2 response format
        items = [_to_v2_response(record) for record in records]
        
        # Apply additional filtering for tags and priority
        if params.tags:
            items = [item for item in items if any(tag in item.tags for tag in params.tags)]
        
        if params.priority:
            items = [item for item in items if item.priority == params.priority]
        
        return {
            'items': items,
            'total': total,
            'page': params.page,
            'limit': params.limit,
            'total_pages': (total + params.limit - 1) // params.limit,
            'filters': {
                'query': params.query,
                'policy_id': params.policy_id,
                'status': params.status,
                'tags': params.tags,
                'priority': params.priority,
                'date_from': params.date_from,
                'date_to': params.date_to,
                'size_min': params.size_min,
                'size_max': params.size_max
            }
        }
        
    except Exception as e:
        logger.error(f"Error listing archives: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{archive_id}", response_model=ArchiveRecordResponseV2)
async def get_archive(
    archive_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific archive record with enhanced information"""
    try:
        record = await archive_service.get_record(db, archive_id)
        if not record:
            raise HTTPException(status_code=404, detail="Archive record not found")
        
        # Increment access count
        await _increment_access_count(db, archive_id)
        
        return _to_v2_response(record)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting archive record: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{archive_id}")
async def delete_archive(
    archive_id: int,
    force: bool = Query(False, description="Force delete even if not expired"),
    db: Session = Depends(get_db)
):
    """Delete an archive record with optional force parameter"""
    try:
        record = await archive_service.get_record(db, archive_id)
        if not record:
            raise HTTPException(status_code=404, detail="Archive record not found")
        
        if not force and record.status != "expired":
            raise HTTPException(
                status_code=400, 
                detail="Archive record is not expired. Use force=true to delete."
            )
        
        success = await archive_service.delete_record(db, archive_id)
        
        if success:
            return {"message": "Archive record deleted successfully", "archive_id": archive_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete archive record")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting archive record: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{archive_id}/restore")
async def restore_archive(
    archive_id: int,
    db: Session = Depends(get_db)
):
    """Restore an archived record"""
    try:
        # This would implement restoration logic
        # For now, return a placeholder response
        return {
            "message": "Archive restoration initiated",
            "archive_id": archive_id,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error restoring archive record: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{archive_id}/access-log")
async def get_archive_access_log(
    archive_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get access log for a specific archive"""
    try:
        # This would implement access log retrieval
        # For now, return a placeholder response
        return {
            "archive_id": archive_id,
            "access_log": [],
            "total_accesses": 0
        }
        
    except Exception as e:
        logger.error(f"Error getting access log: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def _to_v2_response(record) -> ArchiveRecordResponseV2:
    """Convert internal record to v2 response format"""
    return ArchiveRecordResponseV2(
        id=record.id,
        original_data_id=record.original_data_id,
        data=record.data,
        metadata=getattr(record, 'metadata', None),
        policy_id=record.policy_id,
        status=record.status,
        created_at=record.created_at,
        expires_at=getattr(record, 'expires_at', None),
        tags=getattr(record, 'tags', []),
        priority=getattr(record, 'priority', 'normal'),
        size_bytes=getattr(record, 'size_bytes', len(record.data.encode())),
        hash_value=getattr(record, 'hash_value', ''),
        access_count=getattr(record, 'access_count', 0),
        last_accessed=getattr(record, 'last_accessed', None),
        retention_days=getattr(record, 'retention_days', 0),
        days_until_expiry=getattr(record, 'days_until_expiry', None)
    )

async def _process_archive_enhancements(
    archive_id: int, 
    tags: List[str], 
    priority: str, 
    retention_override: Optional[int]
):
    """Process enhanced archive features in background"""
    # This would implement tag processing, priority handling, etc.
    logger.info(f"Processing enhancements for archive {archive_id}")

async def _increment_access_count(db: Session, archive_id: int):
    """Increment access count for an archive"""
    # This would implement access count increment
    logger.info(f"Incrementing access count for archive {archive_id}")
