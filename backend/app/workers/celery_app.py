from celery import Celery
from app.config import settings

celery_app = Celery(
    "antiraging_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['app.workers.ingestion_task']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
