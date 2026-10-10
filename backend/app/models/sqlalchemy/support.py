from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.sql import func
from app.db import Base, JSONBType


class PolicyDocument(Base):
    """RAG knowledge base row backing POST /rag-query."""

    __tablename__ = "policy_documents"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    document = Column(String, nullable=False, index=True)
    section = Column(String, nullable=False, default="")
    version = Column(String, nullable=False, default="2026.1")
    content = Column(Text, nullable=False)          # the grounded answer text
    keywords = Column(JSONBType, default=list)      # ["return", "laptop", ...]
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SupportTicket(Base):
    """Simple support ticket backing /ticket endpoints."""

    __tablename__ = "support_tickets"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    ticket_number = Column(String, unique=True, index=True)
    subject = Column(String, default="")
    message = Column(Text, default="")
    status = Column(String, default="OPEN", index=True)  # OPEN | IN_PROGRESS | RESOLVED | CLOSED
    email = Column(String, default="", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
