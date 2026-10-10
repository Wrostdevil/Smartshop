from sqlalchemy import Column, Integer, Text, ForeignKey, Uuid
from sqlalchemy.orm import relationship
from app.db import Base


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    user_id = Column(Uuid, ForeignKey("users.uuid"), nullable=True)
    content = Column(Text, nullable=False, default="")
    rating = Column(Integer, nullable=False, default=5)

    product = relationship("Product", back_populates="reviews")
    author = relationship("User", back_populates="reviews")
