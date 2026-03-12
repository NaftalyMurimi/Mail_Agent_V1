from fastapi import APIRouter, Depends
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.utils.logger import logger

router = APIRouter(prefix="/settings", tags=["Settings"])

# ── Get settings ───────────────────────────────────────
@router.get("")
async def get_settings(current_user: User = Depends(get_current_user)):
    return {
        "scan_interval_minutes": 30,
        "telegram_chat_id":      current_user.telegram_chat_id,
        "subscription_tier":     current_user.subscription_tier,
        "notifications": {
            "telegram": True,
            "email":    True,
            "browser":  False,
        }
    }

# ── Update settings ────────────────────────────────────
@router.put("")
async def update_settings(
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Settings updated for {current_user.email}")
    return {"message": "Settings updated successfully"}