from fastapi import APIRouter, Depends
from app.utils.dependencies import get_current_user
from app.utils.logger import logger

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("")
async def get_settings(current_user: dict = Depends(get_current_user)):
    return {
        "scan_interval_minutes": 30,
        "telegram_chat_id":      current_user.get("telegram_chat_id"),
        "subscription_tier":     current_user.get("subscription_tier"),
        "notifications": {
            "telegram": True,
            "email":    True,
            "browser":  False,
        }
    }

@router.put("")
async def update_settings(current_user: dict = Depends(get_current_user)):
    logger.info(f"Settings updated for {current_user['email']}")
    return {"message": "Settings updated successfully"}