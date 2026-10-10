from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.product_schemas import ProductListOut, ProductOut, CatalogMeta
from app.services.product_service import Product_Service, map_product
from app.models.sqlalchemy import Product

product_router = APIRouter()


@product_router.get("/products", response_model=ProductListOut)
def read_products(
    page: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    max_price: Optional[float] = Query(None, ge=0),
    in_stock_only: bool = Query(False),
    sort: str = Query("recommended"),
    db: Session = Depends(get_db),
):
    return Product_Service.search_products(
        db, search, category, brand, max_price, in_stock_only, sort or "recommended", page, limit
    )


@product_router.get("/products/meta", response_model=CatalogMeta)
def catalog_meta(db: Session = Depends(get_db)):
    return Product_Service.catalog_meta(db)


@product_router.get("/products/{product_slug}", response_model=ProductOut)
def read_product(product_slug: str, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.slug == product_slug).one_or_none()
    if not p:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Product not found")
    return map_product(p)
