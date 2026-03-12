from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class CVResponse(BaseModel):
    id:          UUID
    filename:    str
    storage_url: str | None
    is_active:   bool
    uploaded_at: datetime

    class Config:
        from_attributes = True

class CVListResponse(BaseModel):
    total: int
    cvs:   list[CVResponse]