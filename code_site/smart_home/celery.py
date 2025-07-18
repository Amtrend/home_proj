import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_home.settings')
celery_app = Celery('smart_home')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.worker_max_tasks_per_child = 1
celery_app.autodiscover_tasks()
