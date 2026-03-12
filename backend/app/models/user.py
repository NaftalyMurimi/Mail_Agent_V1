from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

class User(Base):
    __tablename__ = "users"

    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email             = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password   = Column(String(255), nullable=False)
    full_name         = Column(String(255), nullable=True)
    phone_number      = Column(String(50),  nullable=True)
    telegram_chat_id  = Column(String(100), nullable=True)
    subscription_tier = Column(String(50),  default="free")
    is_active         = Column(Boolean, default=True)
    is_verified       = Column(Boolean, default=False)
    created_at        = Column(DateTime, default=datetime.utcnow)
    updated_at        = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Relationships ──────────────────────────────────
    emails       = relationship("Email",       back_populates="user", cascade="all, delete")
    cvs          = relationship("CV",          back_populates="user", cascade="all, delete")
    applications = relationship("Application", back_populates="user", cascade="all, delete")
    scan_logs    = relationship("ScanLog",     back_populates="user", cascade="all, delete")
    settings     = relationship("UserSettings",back_populates="user", cascade="all, delete", uselist=False)