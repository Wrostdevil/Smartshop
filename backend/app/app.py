from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.product_router import product_router
from app.routers.cart_router import cart_router
from app.routers.support_router import support_router
from app.routers.ai_router import ai_router
from app.routers.order_router import order_router

from app.db import create_tables

description = """
ShopSmart AI API 🔥

Backend for the ShopSmart autonomous storefront:

* **Products** — filterable catalog (`/products`, `/products/meta`, `/products/{slug}`)
* **Cart** — guest cart by session (`/cart/{session_id}`)
* **Orders** — checkout + tracking (`/orders/checkout`, `/orders/{order_number}`)
* **AI Shopper** — intent recommendations (`/recommend`)
* **RAG Support** — grounded policy answers (`/rag-query`) + tickets (`/ticket`)
"""

app = FastAPI(
    title="ShopSmart AI API",
    description=description,
    summary="Backend for the ShopSmart AI Autonomous Shopping Platform",
    version="2.0.0",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    try:
        from app.seed import seed_all

        counts = seed_all()
        print(f"[seed] products +{counts.get('products', 0)}, policies +{counts.get('policies', 0)}")
    except Exception as e:
        print(f"[seed] skipped: {e}")
    yield


# Attach lifespan (FastAPI >= 0.93 style). Fallback: also create tables eagerly
# so `TestClient(app)` without lifespan still works.
app.router.lifespan_context = lifespan
try:
    create_tables()
    from app.seed import seed_all as _seed

    _seed()
except Exception as e:
    print(f"[startup] seed skipped: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_router)
app.include_router(cart_router)
app.include_router(support_router)
app.include_router(ai_router)
app.include_router(order_router)
# Serve the same routes under /api/* for the Vite dev proxy + docker nginx
# (frontend calls /api/...; tests + docs keep using the root paths above).
app.include_router(product_router, prefix="/api")
app.include_router(cart_router, prefix="/api")
app.include_router(support_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(order_router, prefix="/api")


@app.get("/api/")
async def api_root():
    return {"message": "ShopSmart AI API", "version": "2.0.0", "docs": "/docs"}


@app.get("/api/health")
async def api_health_alias():
    return await health()


@app.get("/")
async def root():
    return {"message": "ShopSmart AI API", "version": "2.0.0", "docs": "/docs"}


@app.get("/health")
async def health():
    from app.db import get_db_session

    try:
        db = get_db_session()
        from app.models.sqlalchemy import Product

        total = db.query(Product).count()
        db.close()
        return {"status": "ok", "products": total}
    except Exception as e:
        return {"status": "degraded", "error": str(e)[:200]}
