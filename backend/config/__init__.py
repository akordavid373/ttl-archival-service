from celery import Celery
from ..config.celery_config import celery_settings

celery_app = Celery("ttl_archival_tasks")
celery_app.config_from_object(celery_settings)

@celery_app.task(bind=True, max_retries=3)
def archive_cleanup_task(self):
    return {"status": "success", "task": "archive_cleanup"}

@celery_app.task(bind=True, max_retries=3)
def email_sending_task(self, to_email: str, subject: str, body: str):
    return {"status": "success", "task": "email_sending", "to": to_email}

@celery_app.task(bind=True, max_retries=3)
def backup_operations_task(self):
    return {"status": "success", "task": "backup_operations"}

@celery_app.task(bind=True, max_retries=3)
def report_generation_task(self, report_type: str):
    return {"status": "success", "task": "report_generation", "type": report_type}

@celery_app.task(bind=True, max_retries=3)
def data_processing_task(self, data_id: str):
    return {"status": "success", "task": "data_processing", "data_id": data_id}