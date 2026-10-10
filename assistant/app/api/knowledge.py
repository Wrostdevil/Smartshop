from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import verify_admin_key
from app.repositories.document_repository import DocumentRepository
from app.repositories.vector_repository import VectorRepository
from app.services.retrieval_service import retrieval_service
from app.schemas import (
    DocumentListItem,
    ChunkDetailItem,
    RetrievalDebugRequest,
    RetrievalDebugResponse,
    RetrievalDebugItem
)

router = APIRouter(prefix="/api/ai", tags=["Knowledge Studio"])

@router.get("/knowledge", response_model=List[DocumentListItem])
def list_indexed_documents(
    category: Optional[str] = Query(None, description="Filter by category"),
    region: Optional[str] = Query(None, description="Filter by region"),
    status: Optional[str] = Query(None, description="Filter by document status (e.g. 'indexed', 'superseded')"),
    db: Session = Depends(get_db)
):
    """
    Lists indexed policy documents, versions, and chunk counts for Knowledge Studio inspection.
    """
    docs = DocumentRepository.list_documents(db, category=category, region=region, status=status)
    items = []
    for d in docs:
        items.append(DocumentListItem(
            id=d.id,
            title=d.title,
            originalFilename=d.original_filename,
            category=d.category,
            version=d.version,
            effectiveDate=d.effective_date,
            region=d.region,
            status=d.status,
            embeddingModel=d.embedding_model,
            chunksCount=len(d.chunks),
            createdAt=d.created_at.isoformat()
        ))
    return items

@router.get("/knowledge/{document_id}/chunks", response_model=List[ChunkDetailItem])
def inspect_document_chunks(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns indexed chunks and section metadata for a specific document without dumping raw vector arrays.
    """
    doc = DocumentRepository.get_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    chunks = VectorRepository.get_chunks_by_document(db, document_id)
    return [
        ChunkDetailItem(
            chunkId=c.id,
            chunkIndex=c.chunk_index,
            section=c.section,
            page=c.page_number,
            content=c.content,
            createdAt=c.created_at.isoformat()
        )
        for c in chunks
    ]

@router.post(
    "/retrieve-debug",
    response_model=RetrievalDebugResponse,
    dependencies=[Depends(verify_admin_key)]
)
def inspect_retrieval(
    request: RetrievalDebugRequest,
    db: Session = Depends(get_db)
):
    """
    Developer-only retrieval debugging endpoint.
    Returns matched chunks and similarity scores without calling LLM generation.
    """
    retrieved = retrieval_service.retrieve_evidence(
        db=db,
        question=request.question,
        category=request.category,
        region=request.region,
        top_k=request.topK or 5
    )

    items = []
    for chunk, doc, score in retrieved:
        items.append(RetrievalDebugItem(
            chunkId=chunk.id,
            documentId=doc.id,
            documentTitle=doc.title,
            section=chunk.section,
            version=doc.version,
            region=doc.region,
            similarityScore=round(score, 4),
            content=chunk.content
        ))

    return RetrievalDebugResponse(
        query=request.question,
        resultsCount=len(items),
        results=items
    )
