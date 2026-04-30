import asyncio
import logging
from datetime import datetime, timedelta
from uuid import UUID
from ..config import celery_app
from ..database import SessionLocal
from ..services.sync_service import SyncService
from ..models.sync import SyncJob, SyncType, SyncStatus

logger = logging.getLogger(__name__)
sync_service = SyncService()

@celery_app.task(bind=True, max_retries=3)
def run_full_sync(self, job_id: str):
    """
    Celery task to execute a full data synchronization.
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting full sync task for job {job_id}")
        # Run async execute_full_sync in a synchronous context
        asyncio.run(sync_service.execute_full_sync(db, UUID(job_id)))
        return {"status": "success", "job_id": job_id, "type": "full"}
    except Exception as exc:
        db.rollback()
        logger.error(f"Error in run_full_sync for job {job_id}: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    finally:
        db.close()

@celery_app.task(bind=True, max_retries=3)
def run_incremental_sync(self, job_id: str, since: str):
    """
    Celery task to execute an incremental data synchronization.
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting incremental sync task for job {job_id} since {since}")
        since_dt = datetime.fromisoformat(since)
        asyncio.run(sync_service.execute_incremental_sync(db, UUID(job_id), since_dt))
        return {"status": "success", "job_id": job_id, "type": "incremental"}
    except Exception as exc:
        db.rollback()
        logger.error(f"Error in run_incremental_sync for job {job_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    finally:
        db.close()

@celery_app.task
def run_realtime_sync_tick(job_id: str):
    """
    Periodic task called every 30s for REAL_TIME jobs.
    """
    db = SessionLocal()
    try:
        job = db.query(SyncJob).filter(SyncJob.id == UUID(job_id)).first()
        if job and job.sync_type == SyncType.REAL_TIME and job.status == SyncStatus.RUNNING:
            # Sync records modified in the last 60 seconds (with 30s overlap for safety)
            since = datetime.utcnow() - timedelta(seconds=60)
            asyncio.run(sync_service.execute_incremental_sync(db, job.id, since))
    except Exception as e:
        logger.error(f"Error in real-time sync tick for job {job_id}: {str(e)}")
    finally:
        db.close()

# Note: In a production environment, you would use Celery Beat to schedule these.
# You can dynamically add/remove tasks from the schedule using django-celery-beat
# or by updating the beat_schedule in the celery configuration.
