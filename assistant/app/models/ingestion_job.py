import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, DateTime
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), nullable=True, index=True)
    filename = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="queued") # queued, processing, completed, failed
    chunks_created = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    def __repr__(self):
        return f"<IngestionJob id={self.id} status={self.status} chunks={self.chunks_created}>"
