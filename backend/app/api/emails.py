from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.email import Email
from app.schemas.email import EmailResponse, EmailListResponse
from app.utils.dependencies import get_current_user
from app.utils.logger import logger

router = APIRouter(prefix="/emails", tags=["Emails"])

# ── Get all emails ─────────────────────────────────────
@router.get("", response_model=EmailListResponse)
async def get_emails(
    email_type: str | None = Query(None, description="Filter by type e.g. job_advert"),
    limit:      int        = Query(50,   description="Max results to return"),
    offset:     int        = Query(0,    description="Pagination offset"),
    current_user: User     = Depends(get_current_user),
    db: Session            = Depends(get_db)
):
    query = db.query(Email).filter(Email.user_id == current_user.id)

    if email_type:
        query = query.filter(Email.email_type == email_type)

    total  = query.count()
    emails = query.order_by(Email.classified_at.desc()).offset(offset).limit(limit).all()

    logger.info(f"Returned {len(emails)} emails for {current_user.email}")
    return {"total": total, "emails": emails}

# ── Get single email ───────────────────────────────────
@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(
    email_id:     str,
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_db)
):
    email = db.query(Email).filter(
        Email.id      == email_id,
        Email.user_id == current_user.id
    ).first()

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    return email

# ── Delete single email ────────────────────────────────
@router.delete("/{email_id}", status_code=204)
async def delete_email(
    email_id:     str,
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_db)
):
    email = db.query(Email).filter(
        Email.id      == email_id,
        Email.user_id == current_user.id
    ).first()

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    db.delete(email)
    db.commit()
    logger.info(f"Email {email_id} deleted")
    return