from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.job import Job
from app.schemas.job import JobResponse, JobUpdateRequest, JobListResponse
from app.utils.dependencies import get_current_user
from app.utils.logger import logger
from datetime import datetime

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# ── Get all jobs ───────────────────────────────────────
@router.get("", response_model=JobListResponse)
async def get_jobs(
    status:       str | None = Query(None, description="Filter by status"),
    min_score:    float | None = Query(None, description="Minimum match score"),
    limit:        int        = Query(50,   description="Max results"),
    offset:       int        = Query(0,    description="Pagination offset"),
    current_user: User       = Depends(get_current_user),
    db:           Session    = Depends(get_db)
):
    query = db.query(Job).filter(Job.user_id == current_user.id)

    if status:
        query = query.filter(Job.status == status)
    if min_score is not None:
        query = query.filter(Job.match_score >= min_score)

    total = query.count()
    jobs  = query.order_by(Job.match_score.desc()).offset(offset).limit(limit).all()

    logger.info(f"Returned {len(jobs)} jobs for {current_user.email}")
    return {"total": total, "jobs": jobs}

# ── Get single job ─────────────────────────────────────
@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id:       str,
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_db)
):
    job = db.query(Job).filter(
        Job.id      == job_id,
        Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job

# ── Update job status ──────────────────────────────────
@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id:       str,
    request:      JobUpdateRequest,
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_db)
):
    valid_statuses = ["detected","considering","applied","interview","offer","rejected"]
    if request.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    job = db.query(Job).filter(
        Job.id      == job_id,
        Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status     = request.status
    job.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(job)

    logger.info(f"Job {job_id} status updated to {request.status}")
    return job