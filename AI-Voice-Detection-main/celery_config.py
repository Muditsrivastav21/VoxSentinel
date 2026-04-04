# ============================================================
# VOXSENTINEL - CELERY CONFIGURATION
# Async task processing for voice analytics
# ============================================================

import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Redis URL (use environment variable or local Redis)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "voxsentinel",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks"]
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task settings
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per task
    task_soft_time_limit=540,  # Soft limit at 9 minutes
    
    # Result expiration (24 hours)
    result_expires=86400,
    
    # Worker settings
    worker_prefetch_multiplier=1,  # One task at a time for audio processing
    worker_concurrency=4,  # 4 concurrent workers
    
    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Optional: Task routing for different queues
celery_app.conf.task_routes = {
    "tasks.process_audio_task": {"queue": "audio"},
    "tasks.analyze_transcript_task": {"queue": "analysis"},
}

if __name__ == "__main__":
    celery_app.start()
