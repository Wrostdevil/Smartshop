"""ShopSmart backend smoke tests — run with `pytest` from backend/."""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_shopsmart.db")

# Fresh test DB on every run
for f in ("test_shopsmart.db",):
    try:
        os.remove(f)
    except FileNotFoundError:
        pass

from fastapi.testclient import TestClient  # noqa: E402
from app.app import app  # noqa: E402

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] in ("ok", "degraded")


def test_products_seeded():
    r = client.get("/products?limit=50")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] >= 6, body
    slugs = {p["slug"] for p in body["products"]}
    assert {"LAP101", "LAP102", "LAP103", "PHN201", "AUD301", "HOM401"} <= slugs


def test_product_filters():
    r = client.get("/products?category=Laptops")
    assert r.status_code == 200
    assert all(p["category"] == "Laptops" for p in r.json()["products"])
    r = client.get("/products?brand=Sony")
    assert r.status_code == 200
    assert all(p["brand"] == "Sony" for p in r.json()["products"])
    r = client.get("/products?max_price=400")
    assert r.status_code == 200
    assert all(p["price"] <= 400 for p in r.json()["products"])
    r = client.get("/products?sort=price-low&limit=6")
    prices = [p["price"] for p in r.json()["products"]]
    assert prices == sorted(prices), prices


def test_product_detail_and_meta():
    r = client.get("/products/LAP101")
    assert r.status_code == 200
    p = r.json()
    assert p["name"] == "Dell Inspiron 15 AI Edition"
    assert p["specs"]["ram"] == "16GB DDR5"
    assert len(p["aiSummary"]["pros"]) >= 2
    r = client.get("/products/meta")
    assert r.status_code == 200
    meta = r.json()
    assert "Laptops" in meta["categories"] and "Sony" in meta["brands"]


def test_recommend_and_rag():
    r = client.post("/recommend", json={"query": "laptop under $1000 for AI projects"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["budget"] == 1000
    assert len(body["recommendations"]) >= 1
    r = client.post("/rag-query", json={"query": "Can I return an opened laptop?"})
    assert r.status_code == 200
    assert "7 days" in r.json()["answer"]
    assert len(r.json()["sources"]) >= 1


def test_cart_flow():
    sid = "pytest-cart"
    client.delete(f"/cart/{sid}")
    r = client.post(f"/cart/{sid}/items", json={"product_slug": "LAP101", "quantity": 2})
    assert r.status_code == 200, r.text
    assert r.json()["count"] == 2
    r = client.put(f"/cart/{sid}/items/LAP101", json={"quantity": 1})
    assert r.json()["count"] == 1
    r = client.get(f"/cart/{sid}/price")
    assert r.json()["total"] > 0


def test_checkout_and_tracking():
    r = client.post(
        "/orders/checkout",
        json={"session_id": "pytest-order", "is_prime": True, "items": [{"product_slug": "AUD301", "quantity": 1}]},
    )
    assert r.status_code == 200, r.text
    order = r.json()
    assert order["orderId"].startswith("ORD-2026-")
    r2 = client.get(f"/orders/{order['orderId']}")
    assert r2.status_code == 200
    assert r2.json()["status"] in ("PROCESSING", "IN_TRANSIT")


def test_tickets():
    r = client.post("/ticket", json={"subject": "Where is my order?", "message": "test", "email": "a@b.c"})
    assert r.status_code == 200
    num = r.json()["ticket_number"]
    r2 = client.get(f"/ticket/{num}")
    assert r2.status_code == 200
    r3 = client.put(f"/ticket/{num}", json={"status": "RESOLVED", "subject": "", "message": ""})
    assert r3.json()["status"] == "RESOLVED"
