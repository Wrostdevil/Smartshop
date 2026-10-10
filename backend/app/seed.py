"""Idempotent seed: upserts ShopSmart products + policy docs."""
from app.db import get_db_session
from app.models.sqlalchemy import Product, Category
from app.models.sqlalchemy.support import PolicyDocument
from app.data.shopsmart_seed import PRODUCTS, POLICIES


def seed_all() -> dict:
    db = get_db_session()
    counts = {"products": 0, "policies": 0}
    try:
        for p in PRODUCTS:
            existing = db.query(Product).filter(Product.slug == p["slug"]).one_or_none()
            payload = {
                "slug": p["slug"],
                "product_name": p["product_name"],
                "product_type": p.get("product_type", p.get("category", "")),
                "price": p["price"],
                "sale_price": p.get("sale_price", p["price"]),
                "blurb": p.get("blurb", ""),
                "description": p.get("description", ""),
                "image_url": p.get("image_url", ""),
                "brand": p.get("brand", ""),
                "category": p.get("category", "General"),
                "original_price": p.get("original_price"),
                "rating": p.get("rating", 4.5),
                "review_count": p.get("review_count", 0),
                "stock_count": p.get("stock_count", 10),
                "availability": p.get("availability", "IN_STOCK"),
                "specs": p.get("specs", {}),
                "ai_summary": p.get("ai_summary", {}),
                "tags": p.get("tags", []),
            }
            if existing:
                for k, v in payload.items():
                    setattr(existing, k, v)
            else:
                db.add(Product(**payload))
                counts["products"] += 1
            # Keep legacy M2M category in sync
            cat_name = p.get("category", "General")
            cat = db.query(Category).filter(Category.name == cat_name).one_or_none()
            if not cat:
                cat = Category(name=cat_name, description=f"{cat_name} products")
                db.add(cat)
                db.flush()
            prod = db.query(Product).filter(Product.slug == p["slug"]).one_or_none()
            if prod is not None and cat not in prod.categories:
                prod.categories.append(cat)

        for pol in POLICIES:
            existing = (
                db.query(PolicyDocument)
                .filter(
                    PolicyDocument.document == pol["document"],
                    PolicyDocument.section == pol["section"],
                )
                .one_or_none()
            )
            if existing:
                existing.content = pol["content"]
                existing.version = pol["version"]
                existing.keywords = pol["keywords"]
            else:
                db.add(PolicyDocument(**pol))
                counts["policies"] += 1

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        pass

    # Build RAG chunks/embeddings for every policy doc (idempotent by doc count).
    try:
        from app.models.sqlalchemy.knowledge import KnowledgeDocument, DocumentChunk
        from app.services import rag_service

        existing_docs = {(d.document, d.section) for d in db.query(KnowledgeDocument).all()}
        for pol in POLICIES:
            if (pol["document"], pol["section"]) in existing_docs:
                continue
            rag_service.ingest_document(
                db, document=pol["document"], section=pol["section"],
                version=pol["version"], text=pol["content"], keywords=pol["keywords"],
            )
            counts["chunks"] = counts.get("chunks", 0) + 1
    except Exception as e:
        print(f"[seed] rag chunks skipped: {e}")
    finally:
        db.close()
    return counts


if __name__ == "__main__":
    print(seed_all())
