from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class ScanResponse(BaseModel):
    id:                UUID
    scanned_at:        datetime
    emails_found:      int
    emails_classified: int
    jobs_detected:     int
    status:            str
    error_message:     str | None

    class Config:
        from_attributes = True

class ScanTriggerResponse(BaseModel):
    message:   str
    status:    str
    triggered_at: datetime