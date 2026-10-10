"""Cart service — slug-based, guest-friendly."""
from typing import Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.sqlalchemy import Product
from app.models.sqlalchemy.cart import Cart, CartItem


def _get_or_create_cart(session: Session, session_id: str) -> Cart:
    cart = session.query(Cart).filter(Cart.session_id == session_id).one_or_none()
    if not cart:
        cart = Cart(session_id=session_id or "guest")
        session.add(cart)
        session.flush()
    return cart


def _price_of(product: Product) -> float:
    if product.sale_price is not None:
        return float(product.sale_price)
    return float(product.price or 0)


def cart_to_dict(session: Session, cart: Cart) -> Dict:
    items = []
    subtotal = 0.0
    for it in cart.items:
        prod = session.query(Product).filter(Product.slug == it.product_slug).one_or_none()
        name = prod.product_name if prod else it.product_slug
        image = prod.image_url if prod else ""
        line = float(it.price or 0) * int(it.quantity or 0)
        subtotal += line
        items.append(
            {
                "product_slug": it.product_slug,
                "name": name,
                "image": image,
                "price": float(it.price or 0),
                "quantity": int(it.quantity or 0),
                "line_total": line,
            }
        )
    return {
        "session_id": cart.session_id,
        "items": items,
        "subtotal": subtotal,
        "count": sum(i["quantity"] for i in items),
    }


def get_cart(session: Session, session_id: str) -> Dict:
    cart = _get_or_create_cart(session, session_id)
    session.commit()
    return cart_to_dict(session, cart)


def add_item(session: Session, session_id: str, slug: str, quantity: int = 1) -> Dict:
    prod = session.query(Product).filter(Product.slug == slug).one_or_none()
    if not prod:
        raise HTTPException(status_code=404, detail=f"Product '{slug}' not found")
    cart = _get_or_create_cart(session, session_id)
    existing = (
        session.query(CartItem)
        .filter(CartItem.cart_id == cart.id, CartItem.product_slug == slug)
        .one_or_none()
    )
    if existing:
        existing.quantity = min(int(existing.quantity or 0) + int(quantity), 99)
    else:
        session.add(CartItem(cart_id=cart.id, product_slug=slug, quantity=quantity, price=_price_of(prod)))
    session.commit()
    session.refresh(cart)
    return cart_to_dict(session, cart)


def update_item(session: Session, session_id: str, slug: str, quantity: int) -> Dict:
    cart = _get_or_create_cart(session, session_id)
    item = (
        session.query(CartItem)
        .filter(CartItem.cart_id == cart.id, CartItem.product_slug == slug)
        .one_or_none()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    if quantity <= 0:
        session.delete(item)
    else:
        item.quantity = min(quantity, 99)
    session.commit()
    session.refresh(cart)
    return cart_to_dict(session, cart)


def remove_item(session: Session, session_id: str, slug: str) -> Dict:
    return update_item(session, session_id, slug, 0)


def clear_cart(session: Session, session_id: str) -> Dict:
    cart = _get_or_create_cart(session, session_id)
    session.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    session.commit()
    session.refresh(cart)
    return cart_to_dict(session, cart)
