from fastapi.testclient import TestClient
from app.config import settings

def test_unauthorized_ingestion_rejected(client: TestClient):
    response = client.post(
        "/api/ai/ingest-document",
        files={"file": ("fake_policy.md", b"Fake policy", "text/markdown")}
    )
    assert response.status_code == 403

def test_unauthorized_retrieve_debug_rejected(client: TestClient):
    response = client.post(
        "/api/ai/retrieve-debug",
        json={"question": "Test debug query"}
    )
    assert response.status_code == 403

def test_invalid_api_key_rejected(client: TestClient):
    response = client.post(
        "/api/ai/ingest-document",
        headers={"X-API-Key": "WRONG_SECRET_KEY"},
        files={"file": ("fake_policy.md", b"Fake policy", "text/markdown")}
    )
    assert response.status_code == 403

def test_nonexistent_document_chunks_404(client: TestClient):
    response = client.get("/api/ai/knowledge/non-existent-doc-uuid-999/chunks")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found."

def test_sql_injection_safety(client: TestClient):
    malicious_query = "' UNION SELECT * FROM documents; --"
    response = client.post(
        "/api/ai/rag-query",
        json={"question": malicious_query}
    )
    assert response.status_code == 200
    # Service handles parametrized input safely without SQL failure
