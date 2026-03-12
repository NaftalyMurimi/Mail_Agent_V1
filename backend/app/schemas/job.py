from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class JobResponse(BaseModel):
    id:                   UUID
    company:              str | None
    role_title:           str | None
    location:             str | None
    salary:               str | None
    deadline:             str | None
    match_score:          float | None
    match_reasons:        str | None
    gaps:                 str | None
    apply_recommendation: str | None
    personalized_tip:     str | None
    status:               str
    created_at:           datetime

    class Config:
        from_attributes = True

class JobUpdateRequest(BaseModel):
    status: str  # detected, considering, applied, interview, offer, rejected

class JobListResponse(BaseModel):
    total: int
    jobs:  list[JobResponse]