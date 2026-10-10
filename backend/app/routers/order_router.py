from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List

from app.db import get_db
from app.schemas.order_schema import OrderOut, CheckoutItemIn
from app.services import order_service

order_router = APIRouter()


class CheckoutBody(BaseModel):
    session_id: Optional[str] = "guest"
    is_prime: bool = True
    items: List[CheckoutItemIn] = Field(default_factory=list)


@order_router.post("/orders/checkout", response_model=OrderOut)
def checkout(body: CheckoutBody, db: Session = Depends(get_db)):
    lines = [{"product_slug": i.product_slug, "quantity": i.quantity} for i in body.items]
    return order_service.checkout(db, body.session_id or "guest", lines, body.is_prime)


@order_router.get("/orders", response_model=List[OrderOut])
def list_orders(
    session_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return order_service.list_orders(db, session_id, limit)


@order_router.get("/orders/{order_number}", response_model=OrderOut)
def get_order(order_number: str, db: Session = Depends(get_db)):
    return order_service.get_order(db, order_number)
