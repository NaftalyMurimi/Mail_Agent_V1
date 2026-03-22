from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv
import os

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    "email_manager_agent",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks"],
)

celery.conf.update(
    task_serializer       = "json",
    accept_content        = ["json"],
    result_serializer     = "json",
    timezone              = "Europe/Warsaw",
    enable_utc            = True,
    task_track_started    = True,
    task_acks_late        = True,
    worker_prefetch_multiplier = 1,

    # ── Scheduled tasks ────────────────────────────────
    beat_schedule = {
        "auto-scan-all-users": {
            "task":     "app.tasks.scheduled_scan_all_users",
            "schedule": crontab(minute="*/30"),  # every 30 minutes
        },
    },
)
