from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import hashlib
import os
import shutil
import gzip
import logging
from pathlib import Path

from .models import ArchiveRecord, ArchivePolicy, UserSettings
from .schemas import ArchiveRecordCreate, ArchivePolicyCreate, ArchiveStatus, CleanupStats, UserSettingsUpdate

logger = logging.getLogger(__name__)

class ArchiveService:
    """Service for managing archive records and operations"""
    
    def __init__(self):
        self.archive_storage = os.getenv("ARCHIVE_STORAGE_PATH", "./archives")
        # Ensure archive storage directory exists
        Path(self.archive_storage).mkdir(parents=True, exist_ok=True)
    
    async def create_record(self, db: Session, record: ArchiveRecordCreate) -> ArchiveRecord:
        """Create a new archive record"""
        # Get policy to determine TTL
        policy = db.query(ArchivePolicy).filter(ArchivePolicy.id == record.policy_id).first()
        if not policy:
            raise ValueError(f"Policy with id {record.policy_id} not found")
        
        # Calculate expiry date
        expires_at = datetime.utcnow() + timedelta(days=policy.ttl_days)
        
        # Handle file archival if file_path is provided
        archived_file_path = None
        file_size = record.file_size_bytes
        
        if record.file_path and os.path.exists(record.file_path):
            archived_file_path, file_size = await self._archive_file(
                record.file_path, 
                policy,
                record.original_data_id
            )
        
        # Create archive record
        db_record = ArchiveRecord(
            policy_id=record.policy_id,
            original_data_id=record.original_data_id,
            data_type=record.data_type.value,
            file_path=archived_file_path,
            file_size_bytes=file_size,
            checksum=record.checksum or await self._calculate_checksum(record.file_path),
            metadata=record.metadata,
            expires_at=expires_at
        )
        
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        logger.info(f"Created archive record {db_record.id} for data {record.original_data_id}")
        return db_record
    
    async def get_record(self, db: Session, record_id: int) -> Optional[ArchiveRecord]:
        """Get an archive record by ID"""
        return db.query(ArchiveRecord).filter(ArchiveRecord.id == record_id).first()
    
    async def list_records(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        policy_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[ArchiveRecord]:
        """List archive records with optional filtering"""
        query = db.query(ArchiveRecord)
        
        if policy_id:
            query = query.filter(ArchiveRecord.policy_id == policy_id)
        
        if status:
            query = query.filter(ArchiveRecord.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    async def delete_record(self, db: Session, record_id: int) -> bool:
        """Delete an archive record and its associated file"""
        record = await self.get_record(db, record_id)
        if not record:
            return False
        
        # Delete archived file if it exists
        if record.file_path and os.path.exists(record.file_path):
            try:
                os.remove(record.file_path)
                logger.info(f"Deleted archived file: {record.file_path}")
            except Exception as e:
                logger.error(f"Error deleting file {record.file_path}: {e}")
        
        # Mark record as deleted
        record.status = ArchiveStatus.DELETED
        record.deleted_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Marked archive record {record_id} as deleted")
        return True
    
    async def cleanup_expired_records(self, db: Session, policy_id: Optional[int] = None) -> int:
        """Clean up expired archive records"""
        query = db.query(ArchiveRecord).filter(
            and_(
                ArchiveRecord.expires_at < datetime.utcnow(),
                ArchiveRecord.status == ArchiveStatus.ARCHIVED
            )
        )
        
        if policy_id:
            query = query.filter(ArchiveRecord.policy_id == policy_id)
        
        expired_records = query.all()
        deleted_count = 0
        
        for record in expired_records:
            try:
                await self.delete_record(db, record.id)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Error cleaning up record {record.id}: {e}")
        
        logger.info(f"Cleaned up {deleted_count} expired records")
        return deleted_count
    
    async def get_stats(self, db: Session) -> CleanupStats:
        """Get archival service statistics"""
        total_records = db.query(ArchiveRecord).count()
        active_records = db.query(ArchiveRecord).filter(
            ArchiveRecord.status == ArchiveStatus.ARCHIVED
        ).count()
        expired_records = db.query(ArchiveRecord).filter(
            and_(
                ArchiveRecord.expires_at < datetime.utcnow(),
                ArchiveRecord.status == ArchiveStatus.ARCHIVED
            )
        ).count()
        deleted_records = db.query(ArchiveRecord).filter(
            ArchiveRecord.status == ArchiveStatus.DELETED
        ).count()
        
        total_storage = db.query(func.sum(ArchiveRecord.file_size_bytes)).filter(
            ArchiveRecord.status == ArchiveStatus.ARCHIVED
        ).scalar() or 0
        
        policies_count = db.query(ArchivePolicy).count()
        
        return CleanupStats(
            total_records=total_records,
            active_records=active_records,
            expired_records=expired_records,
            deleted_records=deleted_records,
            total_storage_bytes=total_storage,
            policies_count=policies_count
        )
    
    async def _archive_file(self, source_path: str, policy: ArchivePolicy, data_id: str) -> tuple[str, int]:
        """Archive a file according to policy settings"""
        source_path = Path(source_path)
        
        # Create policy-specific directory
        policy_dir = Path(self.archive_storage) / str(policy.id)
        policy_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_id}_{timestamp}{source_path.suffix}"
        target_path = policy_dir / filename
        
        # Copy and optionally compress
        if policy.compression_enabled:
            target_path = target_path.with_suffix(target_path.suffix + '.gz')
            with open(source_path, 'rb') as f_in:
                with gzip.open(target_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            shutil.copy2(source_path, target_path)
        
        file_size = target_path.stat().st_size
        return str(target_path), file_size
    
    async def _calculate_checksum(self, file_path: str) -> Optional[str]:
        """Calculate SHA-256 checksum of a file"""
        if not file_path or not os.path.exists(file_path):
            return None
        
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()

class PolicyService:
    """Service for managing archive policies"""
    
    async def create_policy(self, db: Session, policy: ArchivePolicyCreate) -> ArchivePolicy:
        """Create a new archive policy"""
        db_policy = ArchivePolicy(**policy.dict())
        db.add(db_policy)
        db.commit()
        db.refresh(db_policy)
        
        logger.info(f"Created archive policy {db_policy.id}: {db_policy.name}")
        return db_policy
    
    async def get_policy(self, db: Session, policy_id: int) -> Optional[ArchivePolicy]:
        """Get an archive policy by ID"""
        return db.query(ArchivePolicy).filter(ArchivePolicy.id == policy_id).first()
    
    async def list_policies(self, db: Session, skip: int = 0, limit: int = 100) -> List[ArchivePolicy]:
        """List all archive policies"""
        return db.query(ArchivePolicy).offset(skip).limit(limit).all()
    
    async def update_policy(self, db: Session, policy_id: int, policy_update: Dict[str, Any]) -> Optional[ArchivePolicy]:
        """Update an archive policy"""
        policy = await self.get_policy(db, policy_id)
        if not policy:
            return None
        
        for field, value in policy_update.items():
            setattr(policy, field, value)
        
        db.commit()
        db.refresh(policy)
        
        logger.info(f"Updated archive policy {policy_id}")
        return policy
    
    async def delete_policy(self, db: Session, policy_id: int) -> bool:
        """Delete an archive policy (only if no records are associated)"""
        policy = await self.get_policy(db, policy_id)
        if not policy:
            return False
        
        # Check if any records are associated
        record_count = db.query(ArchiveRecord).filter(ArchiveRecord.policy_id == policy_id).count()
        if record_count > 0:
            raise ValueError(f"Cannot delete policy with {record_count} associated records")
        
        db.delete(policy)
        db.commit()
        
        logger.info(f"Deleted archive policy {policy_id}")
        return True

class SettingsService:
    """Service for managing application and user settings"""
    
    async def get_settings(self, db: Session) -> UserSettings:
        """Get the current user settings, creating defaults if not found"""
        settings = db.query(UserSettings).first()
        if not settings:
            settings = UserSettings()
            db.add(settings)
            db.commit()
            db.refresh(settings)
            logger.info("Created default user settings")
        return settings
    
    async def update_settings(self, db: Session, settings_update: Dict[str, Any]) -> UserSettings:
        """Update current settings"""
        settings = await self.get_settings(db)
        
        for field, value in settings_update.items():
            if value is not None:
                setattr(settings, field, value)
        
        db.commit()
        db.refresh(settings)
        
        logger.info("Updated user settings")
        return settings
