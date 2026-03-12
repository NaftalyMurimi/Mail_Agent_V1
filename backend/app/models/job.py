from sqlalchemy import Column, String, DateTime, Text, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

class Job(Base):
    __tablename__ = "jobs"

    id                 = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id            = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    email_id           = Column(UUID(as_uuid=True), ForeignKey("emails.id"), nullable=True)
    company            = Column(String(255), nullable=True)
    role_title         = Column(String(255), nullable=True)
    location           = Column(String(255), nullable=True)
    salary             = Column(String(255), nullable=True)
    deadline           = Column(String(100), nullable=True)
    match_score        = Column(Float,       nullable=True)
    match_reasons      = Column(Text,        nullable=True)
    gaps               = Column(Text,        nullable=True)
    apply_recommendation = Column(String(100), nullable=True)
    personalized_tip   = Column(Text,        nullable=True)
    status             = Column(String(100), default="detected")  # detected, considering, applied, interview, offer, rejected
    created_at         = Column(DateTime,    default=datetime.utcnow)
    updated_at         = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Relationships ──────────────────────────────────
    user        = relationship("User",        back_populates="jobs" if False else "jobs")
    email       = relationship("Email",       back_populates="job")
    application = relationship("Application", back_populates="job", uselist=False)