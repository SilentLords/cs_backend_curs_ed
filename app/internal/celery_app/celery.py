from datetime import timedelta

from celery import Celery
from celery.utils.log import get_task_logger
from celery.schedules import crontab

from app.configuration.settings import Settings
settings = Settings()

celery_app = Celery('app.internal.celery_app',
        broker=settings.celery_broker_url,
        backend=settings.celery_backend_url,
        include=['app.app.internal.celery_app.tasks'],
    )

celery_app.conf.result_expires = 60

celery_app.conf.ONCE = {
  'backend': 'celery_once.backends.Redis',
  'result_expires': 60,
  'settings': {
    'url': settings.celery_backend_url,
    'default_timeout': 60
  }
}

celery_app.autodiscover_tasks()

celery_log = get_task_logger(__name__)

celery_app.conf.beat_schedule = {
    'Striga email statements': {
        'task': 'work_with_statement_requests',
        "schedule": timedelta(seconds=30),
    },
}
