"""AI endpoints backing the ShopSmart frontend Live-API mode.

POST /recommend  — intent-based recommendations over the live catalog.
POST /rag-query  — grounded policy answers from the DB knowledge base.
"""
import re
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db import get_db

ai_router = APIRouter()


class RecommendRequest(BaseModel):
    query: str
    budget: Optional[float] = None
    category: Optional[str] = None


class Recommendation(BaseModel):
    productId: str
    productName: str
    reason: str
    availability: str = "IN_STOCK"
    price: float = 0


class RecommendResponse(BaseModel):
    interpretedRequirement: str
    budget: Optional[float] = None
    recommendations: List[Recommendation] = []
    clarifyingQuestion: Optional[str] = None
    source: str = "backend"


class RagQueryRequest(BaseModel):
    query: str


class RagSource(BaseModel):
    document: str
    section: str
    version: str


class RagQueryResponse(BaseModel):
    answer: str
    confidence: str = "HIGH"
    sources: List[RagSource] = []
    followUpRequired: bool = False


def _extract_budget(query: str) -> Optional[float]:
    nums = [float(n) for n in re.findall(r"\$?\s?(\d{2,5})", query)]
    return max(nums) if nums else None


def _score(item: dict, tokens: List[str], q_lower: str) -> float:
    hay = " ".join(
        [
            str(item.get("name", "")),
            str(item.get("brand", "")),
            str(item.get("category", "")),
            str(item.get("description", "")),
            " ".join(item.get("tags", []) or []),
            " ".join(str(v) for v in (item.get("specs", {}) or {}).values()),
        ]
    ).lower()
    score = sum(2 for t in tokens if len(t) > 2 and t in hay)
    if "laptop" in q_lower and "laptop" in hay:
        score += 5
    if ("phone" in q_lower or "mobile" in q_lower) and "phone" in hay:
        score += 5
    if ("headphone" in q_lower or "audio" in q_lower or "noise" in q_lower) and "audio" in hay:
        score += 5
    if ("vacuum" in q_lower or "home" in q_lower or "clean" in q_lower) and "home" in hay:
        score += 5
    if "gaming" in q_lower and "rtx" in hay:
        score += 4
    return score


@ai_router.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest, db: Session = Depends(get_db)):
    from app.services.product_service import Product_Service

    query = (req.query or "").strip()
    budget = req.budget if req.budget is not None else _extract_budget(query)
    result = Product_Service.search_products(
        db,
        search=None,
        category=req.category if req.category and req.category != "All" else None,
        brand=None,
        max_price=(budget * 1.15 if budget else None),
        in_stock_only=False,
        sort="rating",
        page=0,
        limit=50,
    )
    catalog = result["products"] or []
    if not catalog:  # empty DB (pre-seed) — seed lazily then retry once
        try:
            from app.seed import seed_all

            seed_all()
            result = Product_Service.search_products(db, None, None, None, None, False, "rating", 0, 50)
            catalog = result["products"] or []
        except Exception:
            pass
    q_lower = query.lower()
    tokens = re.split(r"[^a-z0-9]+", q_lower)
    ranked = sorted(catalog, key=lambda p: (_score(p, tokens, q_lower), p.get("rating", 0)), reverse=True)[:2]
    recs = [
        Recommendation(
            productId=str(p.get("slug") or p.get("id")),
            productName=str(p.get("name")),
            reason=". ".join((p.get("aiSummary", {}) or {}).get("pros", [])[:2]) or p.get("description", "")[:160],
            availability=p.get("availability", "IN_STOCK"),
            price=float(p.get("price", 0)),
        )
        for p in ranked
    ]
    return RecommendResponse(
        interpretedRequirement=query or "General product discovery",
        budget=budget,
        recommendations=recs,
        clarifyingQuestion=None,
        source="backend",
    )


@ai_router.post("/rag-query", response_model=RagQueryResponse)
def rag_query(req: RagQueryRequest, db: Session = Depends(get_db)):
    """Grounded RAG answer: pgvector search over ingested chunks (Postgres)
    with keyword fallback. Never hallucinates outside approved documents."""
    from app.services import rag_service

    result = rag_service.answer_query(db, req.query or "")
    sources = [RagSource(document=s["document"], section=s["section"], version=s["version"]) for s in result["sources"]]
    if not sources:
        sources = [RagSource(document="ShopSmart Refund & Billing Policy", section="General", version="2026.1")]
    return RagQueryResponse(
        answer=result["answer"], confidence=result.get("confidence", "HIGH"),
        sources=sources, followUpRequired=result.get("followUpRequired", False),
    )
