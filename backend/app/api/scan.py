from fastapi import APIRouter, Depends
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.utils.logger import logger
from datetime import datetime

router = APIRouter(prefix="/scan", tags=["Scan"])

# ── Trigger manual scan ────────────────────────────────
@router.post("", )
async def trigger_scan(
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Manual scan triggered by {current_user.email}")

    # Celery task will be wired here in Phase 6
    return {
        "message":      "Scan triggered successfully",
        "status":       "queued",
        "triggered_at": datetime.utcnow(),
        "note":         "Celery background worker will be connected in Phase 6"
    }