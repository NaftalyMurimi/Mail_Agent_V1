from sqlalchemy import Column, String, DateTime, Text, Integer, Float, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

class Email(Base):
    __tablename__ = "emails"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id        = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    gmail_id       = Column(String(255), nullable=False)
    subject        = Column(String(500), nullable=True)
    sender         = Column(String(255), nullable=True)
    body_preview   = Column(Text,        nullable=True)
    email_type     = Column(String(100), nullable=True)  # job_advert, interview, offer etc
    company        = Column(String(255), nullable=True)
    role_title     = Column(String(255), nullable=True)
    location       = Column(String(255), nullable=True)
    salary         = Column(String(255), nullable=True)
    deadline       = Column(String(100), nullable=True)
    action_required= Column(Boolean,     default=False)
    urgency        = Column(String(50),  nullable=True)
    is_processed   = Column(Boolean,     default=False)
    received_at    = Column(DateTime,    nullable=True)
    classified_at  = Column(DateTime,    default=datetime.utcnow)

    # ── Relationships ──────────────────────────────────
    user        = relationship("User",        back_populates="emails")
    job         = relationship("Job",         back_populates="email", uselist=False)