from sqlalchemy import Column, String, Float, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base, JSONBType
from .join_tables import product_categories


class Product(Base):
    """ShopSmart catalog product.

    Denormalized `brand` / `category` columns exist for fast storefront
    filtering, alongside the legacy `categories` M2M + `sizes` relations
    which are kept for backward compatibility.

    JSON columns are JSONB on Postgres (queryable with @> / ->),
    generic JSON on SQLite.
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    # Legacy fields
    product_type = Column(String, index=True, default="")
    product_name = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)          # effective / sale price
    sale_price = Column(Float, nullable=True)
    blurb = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)

    # ShopSmart storefront fields
    brand = Column(String, index=True, default="")
    category = Column(String, index=True, default="General")
    original_price = Column(Float, nullable=True)
    rating = Column(Float, default=4.5)
    review_count = Column(Integer, default=0)
    stock_count = Column(Integer, default=10)
    availability = Column(String, default="IN_STOCK")  # IN_STOCK | LOW_STOCK | OUT_OF_STOCK
    specs = Column(JSONBType, default=dict)            # { processor: ..., ram: ... }
    ai_summary = Column(JSONBType, default=dict)       # { pros: [...], cons: [...] }
    tags = Column(JSONBType, default=list)             # ["AI Learning", ...]
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    categories = relationship("Category", secondary=product_categories, back_populates="products")
    sizes = relationship("ProductSize", back_populates="product", cascade="all, delete-orphan")


class ProductSize(Base):
    __tablename__ = "product_sizes"
    __table_args__ = {"extend_existing": True}

    size_id = Column("id", Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    size = Column(String, default="")
    stock_quantity = Column(Integer, nullable=False, default=0)

    product = relationship("Product", back_populates="sizes")
