import os

import ddtrace
from celery import Celery
from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

ddtrace.config.celery['worker_service_name'] = os.environ.get(
    'CELERY_WORKER_SERVICE_NAME',
    "next-med-celery-service-live"
)
ddtrace.config.celery['producer_service_name'] = os.environ.get(
    'CELERY_PRODUCER_SERVICE_NAME',
    "next-med-celery-producer-live"
)
ddtrace.patch(celery=True)

CELERY_APP = Celery(
    'celery-next-med',
    backend=CELERY_RESULT_BACKEND,
    broker=CELERY_BROKER_URL,
    imports=['backend', 'models', 'sqlalchemy_db', 'spreadsheet'],
    include=['celery_service.tasks'],
    task_serializer='json',
    result_serializer='json',
    result_expires=0,
    worker_send_task_events=True,
    task_send_sent_event=True
)

# Optional configuration
CELERY_APP.conf.update(
    timezone='UTC',
    enable_utc=True,
    task_serializer='json',
    result_serializer='json',
    worker_send_task_events=True,
    task_send_sent_event=True
)

