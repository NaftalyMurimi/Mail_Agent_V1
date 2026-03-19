from fastapi import APIRouter, Depends, BackgroundTasks
from app.utils.dependencies import get_current_user
from app.utils.logger import logger
from datetime import datetime, timezone

router = APIRouter(prefix="/scan", tags=["Scan"])

def run_scan_task(user_id: str):
    from app.agent.scanner import run_scan
    run_scan(user_id)

@router.post("")
async def trigger_scan(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    logger.info(f"Manual scan triggered by {current_user['email']}")

    # Run scan in background so API returns immediately
    background_tasks.add_task(run_scan_task, user_id)

    return {
        "message":      "Scan started successfully",
        "status":       "running",
        "triggered_at": datetime.now(timezone.utc).isoformat(),
        "note":         "Fetch GET /emails and GET /jobs in 30 seconds to see results"
    }