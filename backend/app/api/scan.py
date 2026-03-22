from fastapi import APIRouter, Depends, HTTPException
from app.utils.dependencies import get_current_user
from app.utils.logger import logger
from datetime import datetime, timezone

router = APIRouter(prefix="/scan", tags=["Scan"])

@router.post("")
async def trigger_scan(current_user: dict = Depends(get_current_user)):
    from app.tasks import scan_user_gmail
    user_id = current_user["id"]

    # Check Gmail is connected
    from app.database import get_supabase
    sb = get_supabase()
    gmail = sb.table("gmail_tokens").select("id").eq(
        "user_id", user_id
    ).execute()

    if not gmail.data:
        raise HTTPException(
            status_code=400,
            detail="Gmail not connected. Go to Settings to connect your Gmail."
        )

    # Queue Celery task
    task = scan_user_gmail.delay(user_id)
    logger.info(f"Scan queued for {current_user['email']} — task {task.id}")

    return {
        "message":      "Scan queued successfully",
        "task_id":      task.id,
        "status":       "queued",
        "triggered_at": datetime.now(timezone.utc).isoformat(),
    }

# ── Check scan task status ─────────────────────────────
@router.get("/status/{task_id}")
async def get_scan_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    from app.celery_app import celery
    task = celery.AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status":  task.status,
        "result":  task.result if task.ready() else None,
    }