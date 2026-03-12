from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

class CV(Base):
    __tablename__ = "cvs"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename    = Column(String(255), nullable=False)
    storage_url = Column(String(500), nullable=True)
    parsed_text = Column(Text,        nullable=True)
    is_active   = Column(Boolean,     default=True)
    uploaded_at = Column(DateTime,    default=datetime.utcnow)

    # ── Relationships ──────────────────────────────────
    user = relationship("User", back_populates="cvs")