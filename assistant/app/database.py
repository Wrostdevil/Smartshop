from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings
from app.utils.logging import logger

# Create Database Engine
# If PostgreSQL is configured, connect using pool pre-ping
# If connection fails or sqlite is requested, fallback cleanly for testing/offline mode
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        connect_args=connect_args
    )
except Exception as e:
    logger.error(f"Failed to initialize engine for {settings.DATABASE_URL}: {e}")
    # Fallback to local SQLite for development resilience
    fallback_url = "sqlite:///./shopsmart_fallback.db"
    logger.warning(f"Falling back to local SQLite database: {fallback_url}")
    engine = create_engine(fallback_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI dependency for yielding database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection() -> bool:
    """Verifies that the database is reachable and active."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

def init_db():
    """Initializes tables and pgvector extension if PostgreSQL is active."""
    try:
        if "postgresql" in str(engine.url):
            with engine.connect() as conn:
                logger.info("Ensuring PostgreSQL vector extension is enabled...")
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
        # Create all declared tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
