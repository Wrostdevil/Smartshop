from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.cart_schemas import CartOut, CartAddIn, CartUpdateIn
from app.services import cart_service

cart_router = APIRouter()


@cart_router.get("/cart/{session_id}", response_model=CartOut)
def get_cart(session_id: str, db: Session = Depends(get_db)):
    return cart_service.get_cart(db, session_id)


@cart_router.post("/cart/{session_id}/items", response_model=CartOut)
def add_item(session_id: str, body: CartAddIn, db: Session = Depends(get_db)):
    return cart_service.add_item(db, session_id, body.product_slug, body.quantity)


@cart_router.put("/cart/{session_id}/items/{product_slug}", response_model=CartOut)
def update_item(session_id: str, product_slug: str, body: CartUpdateIn, db: Session = Depends(get_db)):
    return cart_service.update_item(db, session_id, product_slug, body.quantity)


@cart_router.delete("/cart/{session_id}/items/{product_slug}", response_model=CartOut)
def remove_item(session_id: str, product_slug: str, db: Session = Depends(get_db)):
    return cart_service.remove_item(db, session_id, product_slug)


@cart_router.delete("/cart/{session_id}", response_model=CartOut)
def clear_cart(session_id: str, db: Session = Depends(get_db)):
    return cart_service.clear_cart(db, session_id)


@cart_router.get("/cart/{session_id}/price")
def cart_price(session_id: str, db: Session = Depends(get_db)):
    cart = cart_service.get_cart(db, session_id)
    shipping = 0.0 if cart["subtotal"] == 0 else 15.0
    tax = round(cart["subtotal"] * 0.08, 2)
    return {
        "subtotal": cart["subtotal"],
        "shipping": shipping,
        "tax": tax,
        "total": round(cart["subtotal"] + shipping + tax, 2),
        "count": cart["count"],
    }
