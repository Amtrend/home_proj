import os

from celery import Celery
from smart_home.settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_home.settings')
celery_app = Celery('smart_home')
celery_app.conf.broker_url = CELERY_BROKER_URL
celery_app.conf.result_backend = CELERY_RESULT_BACKEND
celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.worker_max_tasks_per_child = 1
celery_app.autodiscover_tasks()
