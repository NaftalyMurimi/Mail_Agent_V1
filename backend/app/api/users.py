from fastapi import APIRouter, Depends, HTTPException
from app.database import get_supabase
from app.utils.dependencies import get_current_user
from app.utils.logger import logger
from datetime import datetime

router = APIRouter(prefix="/users", tags=["Users"])

# ── Get my profile ─────────────────────────────────────
@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    logger.info(f"Profile fetched for {current_user['email']}")
    # Remove sensitive fields
    current_user.pop("hashed_password", None)
    return current_user

# ── Update my profile ──────────────────────────────────
@router.put("/me")
async def update_me(
    full_name:        str | None = None,
    phone_number:     str | None = None,
    telegram_chat_id: str | None = None,
    current_user: dict = Depends(get_current_user),
):
    sb = get_supabase()
    updates = {"updated_at": datetime.utcnow().isoformat()}

    if full_name        is not None: updates["full_name"]        = full_name
    if phone_number     is not None: updates["phone_number"]     = phone_number
    if telegram_chat_id is not None: updates["telegram_chat_id"] = telegram_chat_id

    result = sb.table("users").update(updates).eq("id", current_user["id"]).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update profile")

    updated = result.data[0]
    updated.pop("hashed_password", None)
    logger.info(f"Profile updated for {current_user['email']}")
    return updated

# ── Delete my account ──────────────────────────────────
@router.delete("/me", status_code=204)
async def delete_me(current_user: dict = Depends(get_current_user)):
    sb = get_supabase()
    sb.table("users").delete().eq("id", current_user["id"]).execute()
    logger.info(f"Account deleted for {current_user['email']}")
    return