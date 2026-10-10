from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.config import settings
from app.services.retrieval_service import retrieval_service
from app.models.document import Document

def test_retrieval_service_similarity(db_session: Session):
    results = retrieval_service.retrieve_evidence(
        db=db_session,
        question="What is the laptop return policy for opened items?",
        category="returns",
        region="IN",
        top_k=3
    )
    assert len(results) > 0
    top_chunk, top_doc, score = results[0]
    assert "laptop" in top_chunk.content.lower()
    assert top_doc.category == "returns"
    assert score > 0.0

def test_retrieval_category_filter(db_session: Session):
    # Query with category 'warranty'
    results = retrieval_service.retrieve_evidence(
        db=db_session,
        question="What is the warranty period for smartphone?",
        category="warranty",
        top_k=3
    )
    assert len(results) > 0
    for chunk, doc, _ in results:
        assert doc.category == "warranty"

def test_retrieval_region_filter(db_session: Session):
    results = retrieval_service.retrieve_evidence(
        db=db_session,
        question="What is the return window?",
        region="IN",
        top_k=3
    )
    assert len(results) > 0
    for chunk, doc, _ in results:
        assert doc.region in ["IN", "GLOBAL"]

def test_retrieve_debug_endpoint(client: TestClient):
    response = client.post(
        "/api/ai/retrieve-debug",
        headers={"X-API-Key": settings.ADMIN_API_KEY},
        json={
            "question": "How many days for refund to bank account?",
            "category": "refunds",
            "topK": 3
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["resultsCount"] >= 1
    assert "similarityScore" in data["results"][0]
    assert "documentTitle" in data["results"][0]
