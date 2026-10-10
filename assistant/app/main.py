import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.api import health_router, query_router, ingestion_router, knowledge_router
from app.utils.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB and ensure tables / pgvector extension
    logger.info("Initializing ShopSmart RAG application database schema...")
    init_db()
    logger.info("ShopSmart RAG Assistant ready.")
    yield
    # Shutdown
    logger.info("Shutting down ShopSmart RAG Assistant.")

app = FastAPI(
    title="ShopSmart AI — RAG Customer Knowledge Assistant",
    description=(
        "Module 2 of ShopSmart AI platform: Approved business policy ingestion, "
        "PostgreSQL pgvector similarity search, and strictly grounded response generation."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
cors_origins = ["*"] if "*" in settings.CORS_ORIGINS else settings.CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler to prevent leaking stack traces
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later or contact support."}
    )

# Include API Routers
app.include_router(health_router)
app.include_router(query_router)
app.include_router(ingestion_router)
app.include_router(knowledge_router)

# Mount static files for demo web interface if directory exists
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/demo", StaticFiles(directory=static_dir, html=True), name="static")

@app.get("/", include_in_schema=False)
async def root():
    """Redirect root path to interactive demo UI."""
    return RedirectResponse(url="/demo")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
