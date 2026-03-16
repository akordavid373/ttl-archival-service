from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

class ArchiveStatus(str, Enum):
    ARCHIVED = "archived"
    EXPIRED = "expired"
    DELETED = "deleted"

class DataType(str, Enum):
    USER_DATA = "user_data"
    LOGS = "logs"
    BACKUP = "backup"
    TEMP_FILES = "temp_files"
    CACHE = "cache"
    OTHER = "other"

class ArchivePolicyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    ttl_days: int = Field(..., gt=0, description="Time to live in days")
    storage_location: Optional[str] = None
    compression_enabled: bool = True
    encryption_enabled: bool = False
    auto_cleanup: bool = True

class ArchivePolicyCreate(ArchivePolicyBase):
    pass

class ArchivePolicyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    ttl_days: Optional[int] = Field(None, gt=0)
    storage_location: Optional[str] = None
    compression_enabled: Optional[bool] = None
    encryption_enabled: Optional[bool] = None
    auto_cleanup: Optional[bool] = None

class ArchivePolicyResponse(ArchivePolicyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ArchiveRecordBase(BaseModel):
    policy_id: int = Field(..., gt=0)
    original_data_id: str = Field(..., min_length=1, max_length=255)
    data_type: DataType
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = Field(None, ge=0)
    checksum: Optional[str] = Field(None, min_length=64, max_length=64)
    metadata: Optional[str] = None

class ArchiveRecordCreate(ArchiveRecordBase):
    pass

class ArchiveRecordResponse(ArchiveRecordBase):
    id: int
    status: ArchiveStatus
    expires_at: datetime
    archived_at: datetime
    deleted_at: Optional[datetime] = None
    days_until_expiry: int
    is_expired: bool
    policy: Optional[ArchivePolicyResponse] = None
    
    class Config:
        from_attributes = True

class CleanupStats(BaseModel):
    total_records: int
    active_records: int
    expired_records: int
    deleted_records: int
    total_storage_bytes: int
    policies_count: int

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    database_connected: bool
    scheduler_running: bool

class CleanupResult(BaseModel):
    deleted_count: int
    errors: List[str] = []
    duration_seconds: float
