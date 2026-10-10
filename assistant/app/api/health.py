from fastapi import APIRouter, Response, status
from app.database import check_db_connection
from app.schemas import HealthResponse
from app.services.embedding_service import embedding_service
from app.services.answer_service import answer_service

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
def health_check(response: Response):
    """
    Service health probe. Verifies database connectivity and model provider initialization.
    """
    db_alive = check_db_connection()
    if not db_alive:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        db_status = "disconnected"
        service_status = "degraded"
    else:
        db_status = "connected"
        service_status = "ok"

    return HealthResponse(
        status=service_status,
        service="shopsmart-rag",
        database=db_status,
        embedding_provider=embedding_service.provider,
        embedding_model=embedding_service.model_name,
        llm_provider=answer_service.provider,
        llm_model=answer_service.model_name
    )
