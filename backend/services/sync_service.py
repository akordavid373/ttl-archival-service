import os
import logging
import asyncio
import uuid
import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import redis

from ..models.sync import SyncJob, SyncRecord, SyncConflict, SyncType, SyncStatus, ConflictStrategy, RecordSyncStatus
from ..schemas.sync import SyncJobCreate, SyncJobStatus
from ..config import celery_app

logger = logging.getLogger(__name__)

class SyncService:
    """
    Service for managing data synchronization between different systems and databases.
    Handles full, incremental, and real-time sync jobs with conflict resolution.
    """

    def __init__(self):
        self.batch_size = int(os.getenv("SYNC_BATCH_SIZE", 100))
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = redis.from_url(redis_url)

    def create_sync_job(self, db: Session, job_data: SyncJobCreate) -> SyncJob:
        """
        Creates and persists a new sync job with PENDING status.
        Validates that source and target systems are supported.
        """
        # In a real system, these would be validated against a registry of adapters
        supported_systems = ["postgresql", "stellar", "api", "mongodb", "s3", "elasticsearch"]
        
        if job_data.source_system.lower() not in supported_systems:
            raise ValueError(f"Unsupported source system: {job_data.source_system}")
        if job_data.target_system.lower() not in supported_systems:
            raise ValueError(f"Unsupported target system: {job_data.target_system}")

        db_job = SyncJob(
            name=job_data.name,
            source_system=job_data.source_system,
            target_system=job_data.target_system,
            sync_type=job_data.sync_type,
            conflict_strategy=job_data.conflict_strategy,
            max_retries=job_data.max_retries,
            status=SyncStatus.PENDING
        )
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        
        logger.info(f"Created sync job {db_job.id}: {db_job.name}")
        return db_job

    def start_sync(self, db: Session, job_id: uuid.UUID) -> SyncJob:
        """
        Sets status to RUNNING, records start time and dispatches Celery tasks.
        """
        job = db.query(SyncJob).filter(SyncJob.id == job_id).first()
        if not job:
            raise ValueError(f"Sync job {job_id} not found")

        job.status = SyncStatus.RUNNING
        job.last_sync_at = datetime.utcnow()
        db.commit()

        # Dispatch the appropriate Celery task
        # Note: We import here to avoid circular imports
        from ..tasks.sync_tasks import run_full_sync, run_incremental_sync
        
        if job.sync_type == SyncType.FULL:
            run_full_sync.delay(str(job_id))
        elif job.sync_type == SyncType.INCREMENTAL:
            # Determine watermark: use last_sync_at or 24h ago
            since = job.last_sync_at or (datetime.utcnow() - timedelta(days=1))
            run_incremental_sync.delay(str(job_id), since.isoformat())
        
        logger.info(f"Started sync job {job_id} ({job.sync_type})")
        return job

    async def execute_full_sync(self, db: Session, job_id: uuid.UUID) -> SyncJob:
        """
        Fetches all records from source, computes checksums, compares with target,
        applies conflict strategy, and writes to target.
        """
        job = db.query(SyncJob).filter(SyncJob.id == job_id).first()
        if not job:
            return None

        job.status = SyncStatus.RUNNING
        db.commit()

        try:
            # 1. Fetch records from source
            source_records = await self._fetch_records_from_source(job.source_system)
            
            # 2. Process in batches
            for i in range(0, len(source_records), self.batch_size):
                batch = source_records[i : i + self.batch_size]
                await self._process_batch(db, job, batch)
            
            job.status = SyncStatus.COMPLETED
            job.error_message = None
            job.last_sync_at = datetime.utcnow()
        except Exception as e:
            logger.error(f"Full sync failed for job {job_id}: {str(e)}")
            job.status = SyncStatus.FAILED
            job.error_message = str(e)
            await self._handle_sync_failure(db, job)
        
        db.commit()
        return job

    async def execute_incremental_sync(self, db: Session, job_id: uuid.UUID, since: datetime) -> SyncJob:
        """
        Like full sync but only fetches records modified since the watermark.
        """
        job = db.query(SyncJob).filter(SyncJob.id == job_id).first()
        if not job:
            return None

        job.status = SyncStatus.RUNNING
        db.commit()

        try:
            # Fetch only modified records
            source_records = await self._fetch_records_from_source(job.source_system, since=since)
            
            for i in range(0, len(source_records), self.batch_size):
                batch = source_records[i : i + self.batch_size]
                await self._process_batch(db, job, batch)
            
            job.status = SyncStatus.COMPLETED
            job.error_message = None
            job.last_sync_at = datetime.utcnow()
        except Exception as e:
            logger.error(f"Incremental sync failed for job {job_id}: {str(e)}")
            job.status = SyncStatus.FAILED
            job.error_message = str(e)
            await self._handle_sync_failure(db, job)
        
        db.commit()
        return job

    async def resolve_conflict(self, db: Session, conflict_id: uuid.UUID, resolution: str, resolved_by: str):
        """
        Applies the chosen resolution to the conflicting record and retries writing to target.
        """
        conflict = db.query(SyncConflict).filter(SyncConflict.id == conflict_id).first()
        if not conflict:
            raise ValueError(f"Conflict {conflict_id} not found")

        job = conflict.sync_job
        
        # Determine which data to use
        if resolution == "SOURCE_WINS":
            final_data = conflict.source_data
        elif resolution == "TARGET_WINS":
            final_data = conflict.target_data
        else:
            # Custom resolution could be handled here
            final_data = conflict.source_data 

        # Retry write to target
        try:
            await self._write_to_target(job.target_system, final_data)
            
            # Update conflict status
            conflict.resolution = resolution
            conflict.resolved_at = datetime.utcnow()
            conflict.resolved_by = resolved_by
            
            # Update record status
            record = conflict.sync_record
            record.status = RecordSyncStatus.SYNCED
            record.synced_at = datetime.utcnow()
            
            job.records_synced += 1
            job.records_failed = max(0, job.records_failed - 1)
            
            db.commit()
            logger.info(f"Resolved conflict {conflict_id} using {resolution}")
        except Exception as e:
            logger.error(f"Failed to resolve conflict {conflict_id}: {str(e)}")
            raise

    def get_sync_status(self, db: Session, job_id: uuid.UUID) -> SyncJobStatus:
        """
        Returns current job status, progress metrics, and recent error if any.
        """
        job = db.query(SyncJob).filter(SyncJob.id == job_id).first()
        if not job:
            raise ValueError(f"Sync job {job_id} not found")

        total_records = job.records_synced + job.records_failed
        progress = (job.records_synced / total_records * 100) if total_records > 0 else 0
        
        return SyncJobStatus(
            id=job.id,
            status=job.status,
            progress_percentage=round(progress, 2),
            records_synced=job.records_synced,
            records_failed=job.records_failed,
            error_message=job.error_message
        )

    def pause_sync(self, db: Session, job_id: uuid.UUID):
        """Sets status to PAUSED and revokes pending Celery tasks."""
        job = db.query(SyncJob).filter(SyncJob.id == job_id).first()
        if job:
            job.status = SyncStatus.PAUSED
            db.commit()
            # Revoke Celery task if it's currently running/queued
            celery_app.control.revoke(str(job_id), terminate=True)
            logger.info(f"Paused sync job {job_id}")

    def resume_sync(self, db: Session, job_id: uuid.UUID):
        """Sets status back to RUNNING and re-triggers the sync."""
        job = db.query(SyncJob).filter(SyncJob.id == job_id).first()
        if job and job.status == SyncStatus.PAUSED:
            job.status = SyncStatus.PENDING
            db.commit()
            self.start_sync(db, job_id)
            logger.info(f"Resumed sync job {job_id}")

    # Internal helper methods

    async def _process_batch(self, db: Session, job: SyncJob, batch: List[Dict]):
        """Processes a batch of records from the source system."""
        for source_data in batch:
            record_id = str(source_data.get("id"))
            record_type = source_data.get("type", "archival_record")
            source_checksum = self._compute_checksum(source_data)
            
            # 1. Check Redis cache for target checksum to avoid redundant reads
            cache_key = f"sync:{job.id}:checksum:{record_id}"
            target_checksum = self.redis_client.get(cache_key)
            
            if target_checksum:
                target_checksum = target_checksum.decode('utf-8')
            else:
                # Cache miss: fetch from target system
                target_record = await self._fetch_record_from_target(job.target_system, record_id)
                target_checksum = self._compute_checksum(target_record) if target_record else None
                if target_checksum:
                    self.redis_client.setex(cache_key, 3600, target_checksum)

            # 2. Check if sync is needed
            if source_checksum == target_checksum:
                self._update_sync_record(db, job, record_id, record_type, source_checksum, target_checksum, RecordSyncStatus.SYNCED)
                job.records_synced += 1
                continue

            # 3. Handle conflict resolution
            final_data = source_data
            status = RecordSyncStatus.SYNCED
            
            if target_checksum:
                # Fetch full target record for resolution if not already fetched
                target_record = await self._fetch_record_from_target(job.target_system, record_id)
                
                if job.conflict_strategy == ConflictStrategy.MANUAL:
                    sync_rec = self._update_sync_record(db, job, record_id, record_type, source_checksum, target_checksum, RecordSyncStatus.CONFLICT)
                    self._create_conflict_entry(db, job, sync_rec, source_data, target_record)
                    job.records_failed += 1
                    continue
                else:
                    final_data = self._resolve_conflict_logic(source_data, target_record, job.conflict_strategy)

            # 4. Write to target system
            try:
                await self._write_to_target(job.target_system, final_data)
                self._update_sync_record(db, job, record_id, record_type, source_checksum, source_checksum, RecordSyncStatus.SYNCED)
                job.records_synced += 1
                # Update cache with new checksum
                self.redis_client.setex(cache_key, 3600, source_checksum)
            except Exception as e:
                logger.error(f"Failed to write record {record_id} to {job.target_system}: {str(e)}")
                self._update_sync_record(db, job, record_id, record_type, source_checksum, target_checksum, RecordSyncStatus.FAILED)
                job.records_failed += 1

        db.commit()

    def _resolve_conflict_logic(self, source: dict, target: dict, strategy: ConflictStrategy) -> dict:
        """Internal conflict resolution strategy application."""
        if strategy == ConflictStrategy.LAST_WRITE_WINS:
            source_ts = source.get("updated_at", "1970-01-01T00:00:00Z")
            target_ts = target.get("updated_at", "1970-01-01T00:00:00Z")
            return source if source_ts >= target_ts else target
        elif strategy == ConflictStrategy.SOURCE_WINS:
            return source
        elif strategy == ConflictStrategy.TARGET_WINS:
            return target
        return source

    async def _handle_sync_failure(self, db: Session, job: SyncJob):
        """Handles retries with exponential backoff if possible."""
        if job.retry_count < job.max_retries:
            job.retry_count += 1
            delay = 2 ** job.retry_count
            logger.info(f"Sync job {job.id} failed. Retrying in {delay} seconds (Attempt {job.retry_count}/{job.max_retries})")
            
            # Re-enqueue with delay
            from ..tasks.sync_tasks import run_full_sync, run_incremental_sync
            if job.sync_type == SyncType.FULL:
                run_full_sync.apply_async((str(job.id),), countdown=delay)
            elif job.sync_type == SyncType.INCREMENTAL:
                since = job.last_sync_at or (datetime.utcnow() - timedelta(days=1))
                run_incremental_sync.apply_async((str(job.id), since.isoformat()), countdown=delay)
        else:
            logger.error(f"Sync job {job.id} reached max retries and failed permanently.")

    def _compute_checksum(self, data: Dict) -> Optional[str]:
        """Computes a SHA-256 checksum for a data dictionary."""
        if not data:
            return None
        # Canonical JSON string representation
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _update_sync_record(self, db: Session, job: SyncJob, record_id: str, record_type: str, 
                           source_cs: str, target_cs: str, status: RecordSyncStatus) -> SyncRecord:
        """Creates or updates a sync record entry."""
        sync_rec = db.query(SyncRecord).filter(
            SyncRecord.sync_job_id == job.id, 
            SyncRecord.record_id == record_id
        ).first()
        
        if not sync_rec:
            sync_rec = SyncRecord(
                sync_job_id=job.id,
                record_id=record_id,
                record_type=record_type
            )
            db.add(sync_rec)
        
        sync_rec.source_checksum = source_cs
        sync_rec.target_checksum = target_cs
        sync_rec.status = status
        sync_rec.synced_at = datetime.utcnow() if status == RecordSyncStatus.SYNCED else sync_rec.synced_at
        
        return sync_rec

    def _create_conflict_entry(self, db: Session, job: SyncJob, sync_rec: SyncRecord, source_data: Dict, target_data: Dict):
        """Creates a new entry in the sync_conflicts table."""
        conflict = SyncConflict(
            sync_job_id=job.id,
            sync_record_id=sync_rec.id,
            source_data=source_data,
            target_data=target_data
        )
        db.add(conflict)

    # Mock adapter methods - these would be replaced by actual system integrations

    async def _fetch_records_from_source(self, system: str, since: datetime = None) -> List[Dict]:
        """Mock: Fetch records from the source system."""
        # For demonstration purposes, we return some mock data
        return [
            {"id": f"mock_record_{i}", "type": "archival_record", "data": "...", "updated_at": datetime.utcnow().isoformat()} 
            for i in range(10)
        ]

    async def _fetch_record_from_target(self, system: str, record_id: str) -> Optional[Dict]:
        """Mock: Fetch a single record from the target system."""
        return None

    async def _write_to_target(self, system: str, data: Dict):
        """Mock: Write data to the target system."""
        await asyncio.sleep(0.01) # Simulate I/O
        pass
