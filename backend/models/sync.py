import uuid
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, JSON, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from ..database import Base

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

class SyncJob(Base):
    __tablename__ = "sync_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    source_system = Column(String(100), nullable=False)
    target_system = Column(String(100), nullable=False)
    sync_type = Column(SQLEnum(SyncType), nullable=False)
    status = Column(SQLEnum(SyncStatus), default=SyncStatus.PENDING, index=True)
    conflict_strategy = Column(SQLEnum(ConflictStrategy), default=ConflictStrategy.LAST_WRITE_WINS)
    
    last_sync_at = Column(DateTime(timezone=True))
    next_sync_at = Column(DateTime(timezone=True))
    
    records_synced = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    error_message = Column(String)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # Relationships
    records = relationship("SyncRecord", back_populates="sync_job", cascade="all, delete-orphan")
    conflicts = relationship("SyncConflict", back_populates="sync_job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SyncJob(id={self.id}, name='{self.name}', status='{self.status}')>"

class SyncRecord(Base):
    __tablename__ = "sync_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sync_job_id = Column(UUID(as_uuid=True), ForeignKey("sync_jobs.id"), nullable=False, index=True)
    
    record_id = Column(String(255), nullable=False, index=True)
    record_type = Column(String(100), nullable=False, index=True)
    
    source_checksum = Column(String(64))
    target_checksum = Column(String(64))
    
    status = Column(SQLEnum(RecordSyncStatus), nullable=False, index=True)
    conflict_details = Column(JSON)
    
    synced_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    sync_job = relationship("SyncJob", back_populates="records")
    conflicts = relationship("SyncConflict", back_populates="sync_record", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_sync_record_job_type', 'sync_job_id', 'record_type'),
    )

    def __repr__(self):
        return f"<SyncRecord(id={self.id}, record_id='{self.record_id}', status='{self.status}')>"

class SyncConflict(Base):
    __tablename__ = "sync_conflicts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sync_job_id = Column(UUID(as_uuid=True), ForeignKey("sync_jobs.id"), nullable=False, index=True)
    sync_record_id = Column(UUID(as_uuid=True), ForeignKey("sync_records.id"), nullable=False, index=True)
    
    source_data = Column(JSON, nullable=False)
    target_data = Column(JSON, nullable=False)
    
    resolution = Column(String)
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    sync_job = relationship("SyncJob", back_populates="conflicts")
    sync_record = relationship("SyncRecord", back_populates="conflicts")

    def __repr__(self):
        return f"<SyncConflict(id={self.id}, sync_job_id={self.sync_job_id}, resolved={self.resolved_at is not None})>"
