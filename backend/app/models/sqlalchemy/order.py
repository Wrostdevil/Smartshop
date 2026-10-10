from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base, JSONBType


class Order(Base):
    """Guest-friendly order. `order_number` (ORD-2026-XXXX) is what the
    ShopSmart OrderTracking UI searches by; items are snapshotted as JSONB
    so tracking works even if catalog prices later change."""

    __tablename__ = "orders"
    __table_args__ = {"extend_existing": True}

    id = Column("id", Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True, nullable=False)
    session_id = Column(String, index=True, nullable=True)
    user_id = Column(Uuid, ForeignKey("users.uuid"), nullable=True)
    status = Column(String, default="PROCESSING", index=True)  # PROCESSING | IN_TRANSIT | DELIVERED | CANCELLED
    subtotal = Column(Float, default=0.0)
    shipping = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    items = Column(JSONBType, default=list)  # [{slug, name, qty, price}]
    warehouse = Column(String, default="East Coast Automated Fulfillment Center (Hub #4)")
    carrier = Column(String, default="ShopSmart AI Express Logistics")
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="orders", foreign_keys=[user_id])
    line_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = {"extend_existing": True}

    id = Column("id", Integer, primary_key=True, index=True)
    order_id = Column("order_id", Integer, ForeignKey("orders.id"), index=True)
    product_slug = Column(String, ForeignKey("products.slug"), nullable=True)
    product_id = Column("product_id", Integer, nullable=True)
    quantity = Column("quantity", Integer, nullable=False, default=1)
    price = Column(Float, default=0.0)

    order = relationship("Order", back_populates="line_items")
