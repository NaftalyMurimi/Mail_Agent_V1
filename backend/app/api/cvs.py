from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.cv import CV
from app.schemas.cv import CVResponse, CVListResponse
from app.utils.dependencies import get_current_user
from app.utils.logger import logger
from datetime import datetime
import uuid
import os

router = APIRouter(prefix="/cv", tags=["CV"])

UPLOAD_DIR = "docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Upload CV ──────────────────────────────────────────
@router.post("/upload", response_model=CVResponse, status_code=201)
async def upload_cv(
    file:         UploadFile       = File(...),
    current_user: User             = Depends(get_current_user),
    db:           Session          = Depends(get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Save file locally (Supabase Storage added in Phase 2)
    file_id   = uuid.uuid4()
    save_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Extract text with pypdf
    parsed_text = ""
    try:
        from pypdf import PdfReader
        reader = PdfReader(save_path)
        for page in reader.pages:
            parsed_text += page.extract_text() or ""
    except Exception as e:
        logger.error(f"PDF parsing failed: {e}")

    new_cv = CV(
        id          = file_id,
        user_id     = current_user.id,
        filename    = file.filename,
        storage_url = save_path,
        parsed_text = parsed_text,
        uploaded_at = datetime.utcnow(),
    )

    db.add(new_cv)
    db.commit()
    db.refresh(new_cv)

    logger.info(f"CV uploaded: {file.filename} for {current_user.email}")
    return new_cv

# ── List CVs ───────────────────────────────────────────
@router.get("", response_model=CVListResponse)
async def get_cvs(
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_db)
):
    cvs   = db.query(CV).filter(CV.user_id == current_user.id).all()
    return {"total": len(cvs), "cvs": cvs}

# ── Delete CV ──────────────────────────────────────────
@router.delete("/{cv_id}", status_code=204)
async def delete_cv(
    cv_id:        str,
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_db)
):
    cv = db.query(CV).filter(
        CV.id      == cv_id,
        CV.user_id == current_user.id
    ).first()

    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    # Remove file from disk
    if cv.storage_url and os.path.exists(cv.storage_url):
        os.remove(cv.storage_url)

    db.delete(cv)
    db.commit()
    logger.info(f"CV {cv_id} deleted")
    return