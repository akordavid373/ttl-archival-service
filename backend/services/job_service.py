from ..tasks import (
    archive_cleanup_task,
    email_sending_task,
    backup_operations_task,
    report_generation_task,
    data_processing_task,
    celery_app
)

class JobService:
    @staticmethod
    def trigger_archive_cleanup():
        job = archive_cleanup_task.delay()
        return {"job_id": job.id}

    @staticmethod
    def trigger_email_sending(to_email: str, subject: str, body: str):
        job = email_sending_task.delay(to_email, subject, body)
        return {"job_id": job.id}

    @staticmethod
    def trigger_backup_operations():
        job = backup_operations_task.delay()
        return {"job_id": job.id}

    @staticmethod
    def trigger_report_generation(report_type: str):
        job = report_generation_task.delay(report_type)
        return {"job_id": job.id}

    @staticmethod
    def trigger_data_processing(data_id: str):
        job = data_processing_task.delay(data_id)
        return {"job_id": job.id}

    @staticmethod
    def get_job_status(job_id: str):
        result = celery_app.AsyncResult(job_id)
        return {
            "job_id": job_id,
            "status": result.status,
            "result": result.result if result.ready() else None
        }