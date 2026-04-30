from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID
from enum import Enum

class SyncType(str, Enum):
    FULL = "FULL"
    INCREMENTAL = "INCREMENTAL"
    REAL_TIME = "REAL_TIME"

class SyncStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"

class ConflictStrategy(str, Enum):
    LAST_WRITE_WINS = "LAST_WRITE_WINS"
    SOURCE_WINS = "SOURCE_WINS"
    TARGET_WINS = "TARGET_WINS"
    MANUAL = "MANUAL"

class RecordSyncStatus(str, Enum):
    SYNCED = "SYNCED"
    CONFLICT = "CONFLICT"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class SyncJobBase(BaseModel):
    name: str = Field(..., description="Human-readable job name")
    source_system: str = Field(..., description="Source system identifier (e.g. 'postgresql')")
    target_system: str = Field(..., description="Target system identifier (e.g. 'stellar')")
    sync_type: SyncType
    conflict_strategy: ConflictStrategy = ConflictStrategy.LAST_WRITE_WINS
    max_retries: int = 3

class SyncJobCreate(SyncJobBase):
    pass

class SyncJobUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[SyncStatus] = None
    conflict_strategy: Optional[ConflictStrategy] = None
    next_sync_at: Optional[datetime] = None

class SyncJobResponse(SyncJobBase):
    id: UUID
    status: SyncStatus
    last_sync_at: Optional[datetime] = None
    next_sync_at: Optional[datetime] = None
    records_synced: int
    records_failed: int
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SyncRecordResponse(BaseModel):
    id: UUID
    sync_job_id: UUID
    record_id: str
    record_type: str
    status: RecordSyncStatus
    synced_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SyncConflictResponse(BaseModel):
    id: UUID
    sync_job_id: UUID
    sync_record_id: UUID
    source_data: Any
    target_data: Any
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SyncJobStatus(BaseModel):
    id: UUID
    status: SyncStatus
    progress_percentage: float
    records_synced: int
    records_failed: int
    error_message: Optional[str] = None
