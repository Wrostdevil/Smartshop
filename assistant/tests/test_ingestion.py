import io
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.config import settings
from app.models.document import Document

def test_ingestion_unauthorized_missing_key(client: TestClient):
    file_content = b"# Test Policy\nThis is a test policy content."
    response = client.post(
        "/api/ai/ingest-document",
        files={"file": ("test.md", file_content, "text/markdown")}
    )
    assert response.status_code == 403

def test_ingestion_valid_markdown(client: TestClient):
    md_content = (
        b"# Custom Drone Delivery Policy\n"
        b"- **Category**: shipping\n"
        b"- **Version**: 2026.2\n"
        b"- **Region**: IN\n\n"
        b"## Section 1: Drone Operations\n"
        b"Drone deliveries operate exclusively in designated aerial corridors."
    )
    response = client.post(
        "/api/ai/ingest-document",
        headers={"X-API-Key": settings.ADMIN_API_KEY},
        files={"file": ("drone_shipping.md", md_content, "text/markdown")},
        data={"category": "shipping", "region": "IN"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "indexed"
    assert data["chunksCreated"] >= 1
    assert "documentId" in data

def test_ingestion_valid_json(client: TestClient):
    policy_json = {
        "title": "ShopSmart Gift Card Rules",
        "category": "gift_cards",
        "version": "1.5",
        "region": "IN",
        "sections": [
            {
                "section": "Card Validity",
                "content": "Digital gift cards remain active for exactly 365 calendar days from issuance."
            }
        ]
    }
    json_bytes = json.dumps(policy_json).encode("utf-8")
    response = client.post(
        "/api/ai/ingest-document",
        headers={"X-API-Key": settings.ADMIN_API_KEY},
        files={"file": ("gift_cards.json", json_bytes, "application/json")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "indexed"
    assert data["chunksCreated"] >= 1

def test_ingestion_duplicate_detection(client: TestClient):
    content = b"# Duplicate Policy Test\nContent to verify deduplication."
    res1 = client.post(
        "/api/ai/ingest-document",
        headers={"X-API-Key": settings.ADMIN_API_KEY},
        files={"file": ("dup.md", content, "text/markdown")}
    )
    assert res1.status_code == 200
    assert res1.json()["status"] == "indexed"

    # Second upload with identical bytes
    res2 = client.post(
        "/api/ai/ingest-document",
        headers={"X-API-Key": settings.ADMIN_API_KEY},
        files={"file": ("dup_copy.md", content, "text/markdown")}
    )
    assert res2.status_code == 200
    assert res2.json()["status"] == "already_indexed"

def test_ingestion_empty_file_rejected(client: TestClient):
    response = client.post(
        "/api/ai/ingest-document",
        headers={"X-API-Key": settings.ADMIN_API_KEY},
        files={"file": ("empty.md", b"", "text/markdown")}
    )
    assert response.status_code == 400

def test_ingestion_empty_pdf_rejected(client: TestClient, db_session: Session):
    # Construct a minimal 0-page or empty text PDF
    from pypdf import PdfWriter
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100) # Blank page with no text
    buf = io.BytesIO()
    writer.write(buf)
    blank_pdf_bytes = buf.getvalue()

    response = client.post(
        "/api/ai/ingest-document",
        headers={"X-API-Key": settings.ADMIN_API_KEY},
        files={"file": ("blank_scanned.pdf", blank_pdf_bytes, "application/pdf")}
    )
    assert response.status_code == 400
    assert "no extractable text" in response.json()["detail"].lower()
