from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import get_supabase
from app.utils.dependencies import get_current_user
from app.utils.logger import logger

router = APIRouter(prefix="/emails", tags=["Emails"])

# ── Get all emails ─────────────────────────────────────
@router.get("")
async def get_emails(
    email_type: str | None = Query(None),
    limit:      int        = Query(50),
    offset:     int        = Query(0),
    current_user: dict     = Depends(get_current_user),
):
    sb    = get_supabase()
    query = sb.table("emails").select("*").eq("user_id", current_user["id"])

    if email_type:
        query = query.eq("email_type", email_type)

    result = query.order("classified_at", desc=True).range(offset, offset+limit-1).execute()
    logger.info(f"Returned {len(result.data)} emails for {current_user['email']}")
    return {"total": len(result.data), "emails": result.data}

# ── Get single email ───────────────────────────────────
@router.get("/{email_id}")
async def get_email(
    email_id:     str,
    current_user: dict = Depends(get_current_user),
):
    sb     = get_supabase()
    result = sb.table("emails").select("*").eq("id", email_id).eq("user_id", current_user["id"]).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Email not found")

    return result.data[0]

# ── Delete email ───────────────────────────────────────
@router.delete("/{email_id}", status_code=204)
async def delete_email(
    email_id:     str,
    current_user: dict = Depends(get_current_user),
):
    sb     = get_supabase()
    result = sb.table("emails").select("id").eq("id", email_id).eq("user_id", current_user["id"]).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Email not found")

    sb.table("emails").delete().eq("id", email_id).execute()
    logger.info(f"Email {email_id} deleted")
    return