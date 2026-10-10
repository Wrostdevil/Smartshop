from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class CheckoutItemIn(BaseModel):
    product_slug: str = Field(min_length=1)
    quantity: int = Field(default=1, ge=1, le=99)


class CheckoutIn(BaseModel):
    session_id: Optional[str] = "guest"
    items: List[CheckoutItemIn] = []


class OrderItemOut(BaseModel):
    slug: Optional[str] = None
    name: str = ""
    qty: int = 1
    price: float = 0.0


class OrderOut(BaseModel):
    orderId: str
    order_number: Optional[str] = None
    date: str = ""
    status: str = "PROCESSING"
    items: List[OrderItemOut] = []
    subtotal: float = 0.0
    shipping: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    warehouse: str = ""
    carrier: str = ""
    trackingHistory: List[Dict[str, Any]] = []
