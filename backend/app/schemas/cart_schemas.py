from pydantic import BaseModel, Field
from typing import List, Optional


class CartItemOut(BaseModel):
    product_slug: str
    name: str = ""
    image: str = ""
    price: float = 0.0
    quantity: int = 1
    line_total: float = 0.0


class CartOut(BaseModel):
    session_id: str
    items: List[CartItemOut] = []
    subtotal: float = 0.0
    count: int = 0


class CartAddIn(BaseModel):
    product_slug: str = Field(min_length=1)
    quantity: int = Field(default=1, ge=1, le=99)


class CartUpdateIn(BaseModel):
    quantity: int = Field(ge=0, le=99)


# Legacy names (old stub router imported these)
class CartItemBase(BaseModel):
    product_slug: str = ""
    product_id: Optional[int] = None
    product_size: Optional[str] = None
    quantity: int = 1
    price: float = 0.0


class CartBase(BaseModel):
    id: Optional[int] = None
    session_id: str = "guest"
    user_id: Optional[str] = None
    items: List[CartItemBase] = []
