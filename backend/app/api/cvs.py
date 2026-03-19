from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.database import get_supabase
from app.utils.dependencies import get_current_user
from app.utils.logger import logger
from datetime import datetime
import uuid
import os

router = APIRouter(prefix="/cv", tags=["CV"])

UPLOAD_DIR = "docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Upload CV ──────────────────────────────────────────
@router.post("/upload", status_code=201)
async def upload_cv(
    file:         UploadFile = File(...),
    current_user: dict       = Depends(get_current_user),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_id   = str(uuid.uuid4())
    save_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Extract text
    parsed_text = ""
    try:
        from pypdf import PdfReader
        reader = PdfReader(save_path)
        for page in reader.pages:
            parsed_text += page.extract_text() or ""
    except Exception as e:
        logger.error(f"PDF parsing failed: {e}")

    sb     = get_supabase()
    new_cv = {
        "id":          file_id,
        "user_id":     current_user["id"],
        "filename":    file.filename,
        "storage_url": save_path,
        "parsed_text": parsed_text,
        "is_active":   True,
        "uploaded_at": datetime.utcnow().isoformat(),
    }

    result = sb.table("cvs").insert(new_cv).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save CV")

    logger.info(f"CV uploaded: {file.filename} for {current_user['email']}")
    # Return without parsed_text (too large)
    cv = result.data[0]
    cv.pop("parsed_text", None)
    return cv

# ── List CVs ───────────────────────────────────────────
@router.get("")
async def get_cvs(current_user: dict = Depends(get_current_user)):
    sb     = get_supabase()
    result = sb.table("cvs").select("id, filename, storage_url, is_active, uploaded_at").eq("user_id", current_user["id"]).execute()
    return {"total": len(result.data), "cvs": result.data}

# ── Delete CV ──────────────────────────────────────────
@router.delete("/{cv_id}", status_code=204)
async def delete_cv(
    cv_id:        str,
    current_user: dict = Depends(get_current_user),
):
    sb     = get_supabase()
    result = sb.table("cvs").select("id, storage_url").eq("id", cv_id).eq("user_id", current_user["id"]).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="CV not found")

    # Remove file from disk
    storage_url = result.data[0].get("storage_url")
    if storage_url and os.path.exists(storage_url):
        os.remove(storage_url)

    sb.table("cvs").delete().eq("id", cv_id).execute()
    logger.info(f"CV {cv_id} deleted")
    return