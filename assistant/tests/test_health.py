from fastapi.testclient import TestClient

def test_health_endpoint_success(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "shopsmart-rag"
    assert data["database"] == "connected"
    assert "embedding_provider" in data
    assert "llm_provider" in data
