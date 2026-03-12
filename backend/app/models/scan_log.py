from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

class ScanLog(Base):
    __tablename__ = "scan_logs"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id        = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    scanned_at     = Column(DateTime, default=datetime.utcnow)
    emails_found   = Column(Integer,  default=0)
    emails_classified = Column(Integer, default=0)
    jobs_detected  = Column(Integer,  default=0)
    status         = Column(String(50), default="success")  # success, failed, partial
    error_message  = Column(String(500), nullable=True)

    # ── Relationships ──────────────────────────────────
    user = relationship("User", back_populates="scan_logs")