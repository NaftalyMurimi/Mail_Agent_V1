from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdateRequest
from app.utils.dependencies import get_current_user
from app.utils.logger import logger
from datetime import datetime

router = APIRouter(prefix="/users", tags=["Users"])

# ── Get my profile ─────────────────────────────────────
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    logger.info(f"Profile fetched for {current_user.email}")
    return current_user

# ── Update my profile ──────────────────────────────────
@router.put("/me", response_model=UserResponse)
async def update_me(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if request.full_name is not None:
        current_user.full_name = request.full_name
    if request.phone_number is not None:
        current_user.phone_number = request.phone_number
    if request.telegram_chat_id is not None:
        current_user.telegram_chat_id = request.telegram_chat_id

    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)

    logger.info(f"Profile updated for {current_user.email}")
    return current_user

# ── Delete my account ──────────────────────────────────
@router.delete("/me", status_code=204)
async def delete_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.delete(current_user)
    db.commit()
    logger.info(f"Account deleted for {current_user.email}")
    return