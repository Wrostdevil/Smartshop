import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    version = Column(String(50), nullable=False, default="1.0")
    effective_date = Column(String(50), nullable=True)
    region = Column(String(50), nullable=False, default="IN", index=True)
    status = Column(String(50), nullable=False, default="indexed", index=True)
    content_hash = Column(String(64), nullable=False, index=True)
    embedding_model = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document id={self.id} title={self.title} version={self.version} region={self.region}>"
