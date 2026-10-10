from sqlalchemy import Column, String, Boolean, DateTime, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db import Base


class User(Base):
    """Postgres-native user — `Uuid` maps to UUID on Postgres,
    CHAR(32) on SQLite, so one schema serves both."""

    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    uuid = Column(Uuid, primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False, default="")
    salt = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    verification_token = Column(String, nullable=True)
    email_verified = Column(Boolean, default=False, nullable=False)
    cart = relationship("Cart", back_populates="user", uselist=False, cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="author")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
