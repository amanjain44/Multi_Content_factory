import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(100), nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), nullable=False, default="Scheduled")
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship back to project
    project = relationship("Project", back_populates="schedules")
