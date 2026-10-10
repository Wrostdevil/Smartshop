from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.sqlalchemy import Product, ProductSize, Category
from app.db import get_db_session

# Module-level session preserves the legacy `Product_Service.get_products(page, limit)`
# call style used by ai_router + tests.
db = get_db_session()


def _specs_of(p: Product) -> dict:
    if isinstance(p.specs, dict):
        return p.specs
    return {}


def _ai_of(p: Product) -> dict:
    if isinstance(p.ai_summary, dict) and p.ai_summary:
        return {
            "pros": list(p.ai_summary.get("pros", []) or []),
            "cons": list(p.ai_summary.get("cons", []) or []),
        }
    return {"pros": [p.blurb] if p.blurb else ["Quality product from catalog"], "cons": []}


def _tags_of(p: Product) -> list:
    if isinstance(p.tags, list):
        return p.tags
    return []


def map_product(p: Product) -> Dict:
    """SQLAlchemy Product -> ShopSmart storefront dict (frontend adapter accepts both)."""
    price = float(p.sale_price if p.sale_price is not None else p.price or 0)
    original = None
    if p.original_price:
        original = float(p.original_price)
    elif p.price and p.sale_price and float(p.price) != float(p.sale_price):
        original = float(p.price)
    try:
        cats = [{"name": c.name, "id": c.id} for c in (p.categories or [])]
    except Exception:
        cats = []
    try:
        sizes = [{"size": s.size, "stock_quantity": s.stock_quantity, "size_id": s.size_id} for s in (p.sizes or [])]
    except Exception:
        sizes = []
    return {
        "id": p.slug or p.id,
        "slug": p.slug,
        "name": p.product_name,
        "brand": p.brand or "",
        "category": p.category or (cats[0]["name"] if cats else (p.product_type or "General")),
        "price": price,
        "originalPrice": original,
        "rating": float(p.rating or 4.5),
        "reviewCount": int(p.review_count or 0),
        "availability": p.availability or "IN_STOCK",
        "stockCount": int(p.stock_count or 0),
        "image": p.image_url or "",
        "description": p.description or p.blurb or "",
        "specs": _specs_of(p),
        "aiSummary": _ai_of(p),
        "tags": _tags_of(p),
        # Legacy aliases
        "product_name": p.product_name,
        "product_type": p.product_type,
        "image_url": p.image_url,
        "blurb": p.blurb,
        "sale_price": float(p.sale_price) if p.sale_price is not None else None,
        "categories": cats,
        "sizes": sizes,
    }


def _query_filtered(
    session: Session,
    search: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    max_price: Optional[float] = None,
    in_stock_only: bool = False,
    sort: str = "recommended",
):
    q = session.query(Product)
    if category and category != "All":
        q = q.filter(Product.category == category)
    if brand and brand != "All":
        q = q.filter(Product.brand == brand)
    if max_price is not None:
        q = q.filter(Product.price <= max_price)
    if in_stock_only:
        q = q.filter(Product.availability != "OUT_OF_STOCK")
    if search:
        like = f"%{search}%"
        q = q.filter(
            (Product.product_name.ilike(like))
            | (Product.brand.ilike(like))
            | (Product.category.ilike(like))
            | (Product.description.ilike(like))
        )
    if sort == "price-low":
        q = q.order_by(Product.price.asc())
    elif sort == "price-high":
        q = q.order_by(Product.price.desc())
    elif sort == "rating":
        q = q.order_by(Product.rating.desc())
    else:
        q = q.order_by(Product.id.asc())
    return q


class Product_Service:
    @staticmethod
    def get_products(page: int = 0, limit: int = 50) -> List[Dict]:
        if page is None or page < 0:
            page = 0
        if limit is None or limit <= 0:
            limit = 50
        limit = min(limit, 100)
        try:
            products = db.query(Product).order_by(Product.id.asc()).offset(page * limit).limit(limit).all()
            return [map_product(p) for p in products]
        except HTTPException:
            raise
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass
            raise HTTPException(status_code=500, detail="Error fetching products")

    @staticmethod
    def search_products(
        session: Session,
        search: Optional[str] = None,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        max_price: Optional[float] = None,
        in_stock_only: bool = False,
        sort: str = "recommended",
        page: int = 0,
        limit: int = 50,
    ) -> Dict:
        if page < 0:
            page = 0
        limit = min(max(limit, 1), 100)
        q = _query_filtered(session, search, category, brand, max_price, in_stock_only, sort)
        total = q.count()
        rows = q.offset(page * limit).limit(limit).all()
        return {"products": [map_product(p) for p in rows], "total": total, "page": page, "limit": limit}

    @staticmethod
    def get_product(product_slug: str) -> Dict:
        try:
            product = db.query(Product).filter(Product.slug == product_slug).one_or_none()
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            return map_product(product)
        except HTTPException:
            raise
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass
            raise HTTPException(status_code=404, detail="Product not found")

    @staticmethod
    def get_product_by_slug(session: Session, slug: str) -> Optional[Dict]:
        p = session.query(Product).filter(Product.slug == slug).one_or_none()
        return map_product(p) if p else None

    @staticmethod
    def catalog_meta(session: Session) -> Dict:
        cats = [r[0] for r in session.query(Product.category).distinct().all() if r[0]]
        brands = [r[0] for r in session.query(Product.brand).distinct().all() if r[0]]
        from sqlalchemy import func

        ceil = session.query(func.max(Product.price)).scalar() or 2000
        total = session.query(Product).count()
        return {
            "categories": ["All", *sorted(cats)],
            "brands": ["All", *sorted(brands)],
            "priceCeil": int(max(ceil, 200)),
            "total": total,
        }

    @staticmethod
    def create_product(session: Session, data: Dict) -> Dict:
        p = Product(**data)
        session.add(p)
        session.commit()
        session.refresh(p)
        return map_product(p)
