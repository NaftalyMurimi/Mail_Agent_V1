from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

class UserResponse(BaseModel):
    id:                UUID
    email:             EmailStr
    full_name:         str | None
    phone_number:      str | None
    telegram_chat_id:  str | None
    subscription_tier: str
    is_active:         bool
    is_verified:       bool
    created_at:        datetime

    class Config:
        from_attributes = True

class UserUpdateRequest(BaseModel):
    full_name:        str | None = None
    phone_number:     str | None = None
    telegram_chat_id: str | None = None