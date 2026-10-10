"""RAG knowledge tables: uploaded enterprise documents + text chunks with embeddings.

Postgres: `embedding` uses pgvector Vector(384) when available so
`ORDER BY embedding <=> query` runs inside the DB. SQLite/test runs fall
back to the JSON `embedding_json` column + Python cosine similarity.

Both columns are kept in sync by `rag_service.embed()`.
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base, JSONBType

EMBEDDING_DIM = 384

try:  # pgvector is optional — only used on Postgres
    from pgvector.sqlalchemy import Vector as _PgVector  # type: ignore

    EmbeddingColumnType = _PgVector(EMBEDDING_DIM)
    HAS_PGVECTOR = True
except Exception:  # pragma: no cover - CI / SQLite without pgvector
    EmbeddingColumnType = None  # type: ignore
    HAS_PGVECTOR = False


class KnowledgeDocument(Base):
    """An uploaded / seeded enterprise knowledge document (Module 2 source)."""

    __tablename__ = "knowledge_documents"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    document = Column(String, nullable=False, index=True)  # e.g. "Laptop Return Policy"
    section = Column(String, nullable=False, default="")
    version = Column(String, nullable=False, default="2026.1")
    category = Column(String, nullable=False, default="policy")
    region = Column(String, nullable=False, default="global")
    source_filename = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chunks = relationship("DocumentChunk", back_populates="doc", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """Overlapping text chunk + deterministic embedding for vector search."""

    __tablename__ = "document_chunks"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("knowledge_documents.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False, default=0)
    content = Column(Text, nullable=False)
    # Portable embedding: JSON list always written; pgvector column when available.
    embedding_json = Column(JSONBType, default=list)

    doc = relationship("KnowledgeDocument", back_populates="chunks")


# Attach the pgvector column only when the library is installed.
# (Table definition stays valid on SQLite where pgvector is absent.)
if HAS_PGVECTOR:
    from sqlalchemy import Column as _Col

    DocumentChunk.embedding = _Col("embedding", EmbeddingColumnType, nullable=True)
