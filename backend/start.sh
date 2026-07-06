#!/bin/bash
# Start Uvicorn in the background
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} &

# Start Celery worker in the foreground with limited concurrency to save memory
celery -A app.workers.celery_app worker -c 1 --loglevel=info
