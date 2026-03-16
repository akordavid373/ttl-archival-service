import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from .database import SessionLocal
from .services import ArchiveService

logger = logging.getLogger(__name__)

class ArchiveScheduler:
    """Scheduler for automated archival cleanup tasks"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.archive_service = ArchiveService()
        self.running = False
        
    async def start(self):
        """Start the scheduler"""
        if self.running:
            return
        
        # Schedule cleanup job to run every hour
        self.scheduler.add_job(
            func=self._scheduled_cleanup,
            trigger=IntervalTrigger(hours=1),
            id="hourly_cleanup",
            name="Hourly cleanup of expired archives",
            replace_existing=True
        )
        
        # Schedule daily summary job at midnight
        self.scheduler.add_job(
            func=self._daily_summary,
            trigger=CronTrigger(hour=0, minute=0),
            id="daily_summary",
            name="Daily archival summary",
            replace_existing=True
        )
        
        # Schedule health check every 5 minutes
        self.scheduler.add_job(
            func=self._health_check,
            trigger=IntervalTrigger(minutes=5),
            id="health_check",
            name="Health check",
            replace_existing=True
        )
        
        self.scheduler.start()
        self.running = True
        logger.info("Archive scheduler started successfully")
    
    async def stop(self):
        """Stop the scheduler"""
        if not self.running:
            return
        
        self.scheduler.shutdown()
        self.running = False
        logger.info("Archive scheduler stopped")
    
    async def _scheduled_cleanup(self):
        """Scheduled cleanup job for expired records"""
        logger.info("Starting scheduled cleanup of expired archives")
        start_time = datetime.utcnow()
        
        try:
            db = SessionLocal()
            try:
                # Clean up all expired records
                deleted_count = await self.archive_service.cleanup_expired_records(db)
                
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.info(f"Scheduled cleanup completed: {deleted_count} records deleted in {duration:.2f}s")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error during scheduled cleanup: {e}")
    
    async def _daily_summary(self):
        """Generate daily archival summary"""
        logger.info("Generating daily archival summary")
        
        try:
            db = SessionLocal()
            try:
                stats = await self.archive_service.get_stats(db)
                
                summary = f"""
Daily Archival Summary - {datetime.utcnow().strftime('%Y-%m-%d')}
==========================================
Total Records: {stats.total_records}
Active Records: {stats.active_records}
Expired Records: {stats.expired_records}
Deleted Records: {stats.deleted_records}
Total Storage: {stats.total_storage_bytes / (1024**2):.2f} MB
Active Policies: {stats.policies_count}
==========================================
                """.strip()
                
                logger.info(summary)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
    
    async def _health_check(self):
        """Health check for the archival system"""
        try:
            db = SessionLocal()
            try:
                # Test database connection
                db.execute("SELECT 1")
                
                # Check if scheduler is running
                scheduler_status = "running" if self.running else "stopped"
                
                logger.debug(f"Health check - Database: OK, Scheduler: {scheduler_status}")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
    
    def get_job_status(self) -> dict:
        """Get status of all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "scheduler_running": self.running,
            "jobs": jobs
        }
