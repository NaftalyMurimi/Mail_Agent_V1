from fastapi import APIRouter, Depends
from app.utils.dependencies import get_current_user
from app.utils.logger import logger
from app.database import get_supabase
from datetime import datetime, timezone
import httpx
import os
import json

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("")
async def get_settings(current_user: dict = Depends(get_current_user)):
    return {
        "scan_interval_minutes": 30,
        "telegram_chat_id":      current_user.get("telegram_chat_id"),
        "subscription_tier":     current_user.get("subscription_tier"),
        "notifications": {
            "telegram": bool(current_user.get("telegram_chat_id")),
            "browser":  False,
        }
    }

@router.put("")
async def update_settings(current_user: dict = Depends(get_current_user)):
    logger.info(f"Settings updated for {current_user['email']}")
    return {"message": "Settings updated successfully"}

# ── Save Telegram chat ID ──────────────────────────────
@router.post("/telegram")
async def save_telegram(
    chat_id:      str,
    current_user: dict    = Depends(get_current_user),
):
    sb = get_supabase()
    sb.table("users").update({
        "telegram_chat_id": chat_id,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", current_user["id"]).execute()

    logger.info(f"Telegram chat ID saved for {current_user['email']}")
    return {"message": "Telegram configured successfully"}

# ── Test Telegram notification ─────────────────────────
@router.post("/telegram/test")
async def test_telegram(current_user: dict = Depends(get_current_user)):
    chat_id = current_user.get("telegram_chat_id")
    if not chat_id:
        return {"success": False, "message": "No Telegram chat ID configured"}

    from app.utils.notifications import send_telegram
    success = await send_telegram(
        chat_id,
        "🤖 <b>Email Manager Agent</b>\n\nTest notification working! ✅\n\nYou will receive job alerts here."
    )

    return {
        "success": success,
        "message": "Test sent!" if success else "Failed to send"
    }


# ── Save browser push subscription ────────────────────
@router.post("/push/subscribe")
async def subscribe_push(
    subscription: dict,
    current_user: dict = Depends(get_current_user),
):
    sb = get_supabase()
    sb.table("push_subscriptions").insert({
        "user_id":      current_user["id"],
        "subscription": json.dumps(subscription),
    }).execute()
    return {"message": "Push subscription saved"}

# ── Remove push subscription ───────────────────────────
@router.delete("/push/unsubscribe")
async def unsubscribe_push(current_user: dict = Depends(get_current_user)):
    sb = get_supabase()
    sb.table("push_subscriptions").delete().eq(
        "user_id", current_user["id"]
    ).execute()
    return {"message": "Push subscription removed"}