from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import RagQueryRequest, RagQueryResponse
from app.services.rag_service import rag_service
from app.utils.logging import logger

router = APIRouter(prefix="/api/ai", tags=["Customer Knowledge Assistant"])

@router.post("/rag-query", response_model=RagQueryResponse)
def ask_policy_question(
    request: RagQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Submits a customer policy inquiry to the RAG pipeline.
    Retrieves grounded evidence from PostgreSQL pgvector and returns citations and confidence.
    """
    try:
        response = rag_service.answer_query(db, request)
        return response
    except Exception as e:
        logger.error(f"Error handling rag-query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the policy inquiry."
        )

@router.post("/rag-query-stream")
async def stream_policy_question(
    request: RagQueryRequest
):
    """
    Submits a policy inquiry and streams the response token-by-token with real-time thinking process.
    Returns Server-Sent Events (text/event-stream).
    """
    return StreamingResponse(
        rag_service.stream_answer_query(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
