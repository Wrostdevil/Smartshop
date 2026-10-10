from app.api.health import router as health_router
from app.api.query import router as query_router
from app.api.ingestion import router as ingestion_router
from app.api.knowledge import router as knowledge_router

__all__ = ["health_router", "query_router", "ingestion_router", "knowledge_router"]
