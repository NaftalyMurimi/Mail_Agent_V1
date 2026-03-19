from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import get_supabase
from app.utils.dependencies import get_current_user
from app.utils.logger import logger
from datetime import datetime

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# ── Get all jobs ───────────────────────────────────────
@router.get("")
async def get_jobs(
    status:       str   | None = Query(None),
    min_score:    float | None = Query(None),
    limit:        int          = Query(50),
    offset:       int          = Query(0),
    current_user: dict         = Depends(get_current_user),
):
    sb    = get_supabase()
    query = sb.table("jobs").select("*").eq("user_id", current_user["id"])

    if status:
        query = query.eq("status", status)
    if min_score is not None:
        query = query.gte("match_score", min_score)

    result = query.order("match_score", desc=True).range(offset, offset+limit-1).execute()
    logger.info(f"Returned {len(result.data)} jobs for {current_user['email']}")
    return {"total": len(result.data), "jobs": result.data}

# ── Get single job ─────────────────────────────────────
@router.get("/{job_id}")
async def get_job(
    job_id:       str,
    current_user: dict = Depends(get_current_user),
):
    sb     = get_supabase()
    result = sb.table("jobs").select("*").eq("id", job_id).eq("user_id", current_user["id"]).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found")

    return result.data[0]

# ── Update job status ──────────────────────────────────
@router.put("/{job_id}")
async def update_job(
    job_id:       str,
    status:       str,
    current_user: dict = Depends(get_current_user),
):
    valid_statuses = ["detected","considering","applied","interview","offer","rejected"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    sb     = get_supabase()
    result = sb.table("jobs").select("id").eq("id", job_id).eq("user_id", current_user["id"]).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found")

    updated = sb.table("jobs").update({
        "status":     status,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", job_id).execute()

    logger.info(f"Job {job_id} updated to {status}")
    return updated.data[0]