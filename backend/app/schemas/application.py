from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class ApplicationResponse(BaseModel):
    id:         UUID
    job_id:     UUID
    status:     str
    applied_at: datetime
    deadline:   datetime | None
    notes:      str | None
    updated_at: datetime

    class Config:
        from_attributes = True

class ApplicationUpdateRequest(BaseModel):
    status:   str | None = None
    notes:    str | None = None
    deadline: datetime | None = None