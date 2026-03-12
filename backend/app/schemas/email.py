from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class EmailResponse(BaseModel):
    id:              UUID
    gmail_id:        str
    subject:         str | None
    sender:          str | None
    body_preview:    str | None
    email_type:      str | None
    company:         str | None
    role_title:      str | None
    location:        str | None
    salary:          str | None
    deadline:        str | None
    action_required: bool
    urgency:         str | None
    is_processed:    bool
    received_at:     datetime | None
    classified_at:   datetime

    class Config:
        from_attributes = True

class EmailListResponse(BaseModel):
    total:  int
    emails: list[EmailResponse]