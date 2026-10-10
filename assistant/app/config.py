import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "ShopSmart RAG Assistant"
    APP_ENV: str = "development"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    API_V1_PREFIX: str = "/api/ai"

    # Database & Vector Storage
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://shopsmart_user:shopsmart_pass@localhost:5432/shopsmart",
        description="SQLAlchemy database URL. Fallback to sqlite if postgres is unavailable or in testing."
    )
    ADMIN_API_KEY: str = Field(
        default="shopsmart-admin-key-2026",
        description="Administrative secret key for policy ingestion and knowledge management endpoints."
    )

    # Embedding Configuration
    EMBEDDING_PROVIDER: str = Field(
        default="auto",
        description="Embedding provider: 'fastembed', 'huggingface', 'google', or 'local_semantic'"
    )
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

    # LLM Configuration
    LLM_PROVIDER: str = Field(
        default="auto",
        description="LLM provider: 'google', 'mock'"
    )
    LLM_MODEL: str = "gemini-1.5-flash"
    GOOGLE_API_KEY: str = ""

    # RAG Tuning Parameters
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 75
    RETRIEVAL_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.35
    MAX_HISTORY_TURNS: int = 5

    # Security & CORS
    CORS_ORIGINS: List[str] = [
        "*",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
