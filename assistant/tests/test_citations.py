from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.chunk import DocumentChunk
from app.models.document import Document

def test_citations_map_to_actual_database_chunks(client: TestClient, db_session: Session):
    response = client.post(
        "/api/ai/rag-query",
        json={"question": "What is the warranty period for this smartphone?"}
    )
    assert response.status_code == 200
    data = response.json()
    sources = data["sources"]
    assert len(sources) >= 1

    for src in sources:
        chunk_id = src["chunkId"]
        doc_id = src["documentId"]

        # Verify that chunk exists in DB
        chunk_db = db_session.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        assert chunk_db is not None, f"Cited chunk {chunk_id} does not exist in DB!"

        # Verify that document exists and matches
        doc_db = db_session.query(Document).filter(Document.id == doc_id).first()
        assert doc_db is not None
        assert doc_db.title == src["document"]
        assert doc_db.version == src["version"]

def test_unsupported_query_returns_zero_citations(client: TestClient):
    response = client.post(
        "/api/ai/rag-query",
        json={"question": "What is the policy regarding interstellar spaceship parking spaces?"}
    )
    assert response.status_code == 200
    data = response.json()
    # Must have no citations for unsupported questions
    assert len(data["sources"]) == 0
