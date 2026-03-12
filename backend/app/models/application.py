from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

class Application(Base):
    __tablename__ = "applications"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    job_id      = Column(UUID(as_uuid=True), ForeignKey("jobs.id"),  nullable=False)
    status      = Column(String(100), default="applied")  # applied, interview, offer, rejected
    applied_at  = Column(DateTime,    default=datetime.utcnow)
    deadline    = Column(DateTime,    nullable=True)
    notes       = Column(Text,        nullable=True)
    updated_at  = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Relationships ──────────────────────────────────
    user = relationship("User", back_populates="applications")
    job  = relationship("Job",  back_populates="application")