from ..tasks import celery_app

class WorkerManager:
    @staticmethod
    def get_active_workers():
        i = celery_app.control.inspect()
        return i.active() if i else {}

    @staticmethod
    def get_registered_tasks():
        i = celery_app.control.inspect()
        return i.registered() if i else {}

    @staticmethod
    def get_scheduled_tasks():
        i = celery_app.control.inspect()
        return i.scheduled() if i else {}