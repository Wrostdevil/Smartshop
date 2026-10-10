"""Order service — checkout + tracking numbers the frontend displays."""
import random
from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.sqlalchemy import Product
from app.models.sqlalchemy.order import Order, OrderItem

WAREHOUSE = "East Coast Automated Fulfillment Center (Hub #4)"
CARRIER = "ShopSmart AI Express Logistics"


def _new_order_number(session: Session) -> str:
    for _ in range(20):
        n = f"ORD-2026-{random.randint(1000, 9999)}"
        if not session.query(Order).filter(Order.order_number == n).one_or_none():
            return n
    return f"ORD-2026-{random.randint(10000, 99999)}"


def _tracking_history(created: datetime) -> List[Dict]:
    ts = created.strftime("%I:%M %p") if created else ""
    return [
        {"title": "Order Placed", "time": ts, "done": True},
        {"title": "Warehouse Processing", "time": "Confirmed", "done": True},
        {"title": "Shipped from Distribution Hub", "time": "In progress", "done": True},
        {"title": "In Transit to Local Fulfillment", "time": "Estimated today", "done": False},
        {"title": "Out for Delivery", "time": "Pending", "done": False},
    ]


def order_to_dict(order: Order) -> Dict:
    items = []
    for it in order.items or []:
        if isinstance(it, dict):
            items.append(
                {"slug": it.get("slug"), "name": it.get("name", ""), "qty": it.get("qty", 1), "price": it.get("price", 0)}
            )
    created = order.created_at or datetime.utcnow()
    return {
        "orderId": order.order_number,
        "order_number": order.order_number,
        "date": created.strftime("%Y-%m-%d %I:%M %p"),
        "status": order.status,
        "items": items,
        "subtotal": float(order.subtotal or 0),
        "shipping": float(order.shipping or 0),
        "tax": float(order.tax or 0),
        "total": float(order.total or 0),
        "warehouse": order.warehouse or WAREHOUSE,
        "carrier": order.carrier or CARRIER,
        "trackingHistory": _tracking_history(created),
        "currentStep": 3,
    }


def checkout(session: Session, session_id: str, lines: List[Dict], is_prime: bool = True) -> Dict:
    if not lines:
        raise HTTPException(status_code=400, detail="Checkout requires at least one item")
    snapshot = []
    subtotal = 0.0
    for line in lines:
        slug = line.get("product_slug") or line.get("slug") or line.get("id")
        qty = max(1, min(int(line.get("quantity", line.get("qty", 1))), 99))
        prod = session.query(Product).filter(Product.slug == slug).one_or_none()
        if not prod:
            raise HTTPException(status_code=404, detail=f"Product '{slug}' not found")
        price = float(prod.sale_price if prod.sale_price is not None else prod.price or 0)
        subtotal += price * qty
        snapshot.append({"slug": slug, "name": prod.product_name, "qty": qty, "price": price})
    shipping = 0.0 if (is_prime or subtotal == 0) else 15.0
    tax = round(subtotal * 0.08, 2)
    total = round(subtotal + shipping + tax, 2)
    order = Order(
        order_number=_new_order_number(session),
        session_id=session_id or "guest",
        status="IN_TRANSIT",
        subtotal=round(subtotal, 2),
        shipping=shipping,
        tax=tax,
        total=total,
        items=snapshot,
        warehouse=WAREHOUSE,
        carrier=CARRIER,
    )
    session.add(order)
    session.flush()
    for s in snapshot:
        session.add(OrderItem(order_id=order.id, product_slug=s["slug"], quantity=s["qty"], price=s["price"]))
    # Decrement stock (never below zero)
    for s in snapshot:
        prod = session.query(Product).filter(Product.slug == s["slug"]).one_or_none()
        if prod and prod.stock_count is not None:
            prod.stock_count = max(0, int(prod.stock_count) - int(s["qty"]))
            if prod.stock_count == 0:
                prod.availability = "OUT_OF_STOCK"
            elif prod.stock_count < 5:
                prod.availability = "LOW_STOCK"
    session.commit()
    session.refresh(order)
    return order_to_dict(order)


def get_order(session: Session, order_number: str) -> Dict:
    order = session.query(Order).filter(Order.order_number == order_number).one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_to_dict(order)


def list_orders(session: Session, session_id: str | None = None, limit: int = 20) -> List[Dict]:
    q = session.query(Order).order_by(Order.id.desc())
    if session_id:
        q = q.filter(Order.session_id == session_id)
    return [order_to_dict(o) for o in q.limit(min(limit, 50)).all()]
