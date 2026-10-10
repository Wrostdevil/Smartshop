from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base


class Cart(Base):
    """Guest-friendly cart keyed by session/user string.

    ShopSmart adds to cart by product slug with no login, so the cart is
    keyed by `session_id`. `user_id` is a native UUID FK, nullable.
    """

    __tablename__ = "carts"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    session_id = Column(String, index=True, nullable=False, default="guest")
    user_id = Column(Uuid, ForeignKey("users.uuid"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="cart", foreign_keys=[user_id])
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False, index=True)
    product_slug = Column(String, ForeignKey("products.slug"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False, default=0.0)

    cart = relationship("Cart", back_populates="items")


# Back-compat alias (legacy code imported Cart_Item)
Cart_Item = CartItem
