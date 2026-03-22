from app.celery_app import celery
from app.agent.scanner import run_scan
from app.database import get_supabase
from app.utils.logger import logger
import asyncio

# ── Single user scan task ──────────────────────────────
@celery.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="app.tasks.scan_user_gmail"
)
def scan_user_gmail(self, user_id: str):
    logger.info(f"Celery task started for user {user_id}")
    try:
        result = run_scan(user_id=user_id)
        logger.info(f"Scan complete for {user_id}: {result}")

        # Send Telegram notification
        if result.get("status") == "success":
            from app.utils.notifications import notify_scan_complete
            asyncio.run(notify_scan_complete(user_id, result))

        return result
    except Exception as exc:
        logger.error(f"Celery task failed for user {user_id}: {exc}")
        raise self.retry(exc=exc)

# ── Scheduled scan for ALL users ──────────────────────
@celery.task(name="app.tasks.scheduled_scan_all_users")
def scheduled_scan_all_users():
    logger.info("Running scheduled scan for all users")
    sb = get_supabase()

    result = sb.table("gmail_tokens").select("user_id").execute()

    if not result.data:
        logger.info("No users with Gmail connected")
        return {"scanned": 0}

    count = 0
    for row in result.data:
        scan_user_gmail.delay(row["user_id"])
        count += 1

    return {"scanned": count}