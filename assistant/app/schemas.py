from typing import List, Optional
from pydantic import BaseModel, Field

# Health Schema
class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "shopsmart-rag"
    database: str = "connected"
    embedding_provider: Optional[str] = None
    embedding_model: Optional[str] = None
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None

# Citation Schema
class SourceCitation(BaseModel):
    documentId: str
    document: str
    section: Optional[str] = None
    version: Optional[str] = None
    effectiveDate: Optional[str] = None
    region: Optional[str] = None
    page: Optional[int] = None
    chunkId: str

# RAG Query Request & Response
class RagQueryRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000, description="The customer policy question.")
    conversationId: Optional[str] = Field(None, description="Optional conversation session ID for multi-turn follow-ups.")
    region: Optional[str] = Field(None, description="Regional scope filter (e.g., 'IN', 'US').")
    category: Optional[str] = Field(None, description="Policy category filter (e.g., 'returns', 'refunds', 'shipping', 'warranty', 'membership').")

class RagQueryResponse(BaseModel):
    answer: str
    confidence: str = Field(..., description="HIGH, MEDIUM, or LOW based on evidence verification.")
    sources: List[SourceCitation] = Field(default_factory=list)
    followUpRequired: bool = False
    followUpQuestion: Optional[str] = None
    conversationId: str

# Document Ingestion Schema
class IngestionResponse(BaseModel):
    documentId: str
    status: str
    chunksCreated: int
    embeddingModel: str
    warnings: List[str] = Field(default_factory=list)

# Knowledge Studio Inspection Schemas
class DocumentListItem(BaseModel):
    id: str
    title: str
    originalFilename: str
    category: str
    version: str
    effectiveDate: Optional[str] = None
    region: str
    status: str
    embeddingModel: str
    chunksCount: int
    createdAt: str

class ChunkDetailItem(BaseModel):
    chunkId: str
    chunkIndex: int
    section: Optional[str] = None
    page: Optional[int] = None
    content: str
    createdAt: str

# Retrieval Debugging Schema
class RetrievalDebugRequest(BaseModel):
    question: str
    category: Optional[str] = None
    region: Optional[str] = None
    topK: Optional[int] = 5

class RetrievalDebugItem(BaseModel):
    chunkId: str
    documentId: str
    documentTitle: str
    section: Optional[str] = None
    version: Optional[str] = None
    region: Optional[str] = None
    similarityScore: float
    content: str

class RetrievalDebugResponse(BaseModel):
    query: str
    resultsCount: int
    results: List[RetrievalDebugItem]
