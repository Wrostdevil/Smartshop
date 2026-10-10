from sqlalchemy import create_engine, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator
from colorama import Fore

from app.config import DATABASE_URL, IS_SQLITE

Base = declarative_base()

# Portable JSON: real JSONB on Postgres, generic JSON/TEXT on SQLite.
JSONBType = JSON().with_variant(JSONB(), "postgresql")

connect_args = {"check_same_thread": False} if IS_SQLITE else {"connect_timeout": 5}


def get_db_engine():
    try:
        engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)
        # Fail fast with a useful hint instead of a cryptic None later.
        with engine.connect():
            pass
        return engine
    except Exception as e:
        masked = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
        print(
            f"{Fore.RED}Cannot connect to Postgres at {masked}: {e}\n"
            f"Start it with `docker compose up postgres`, or set SQLITE_URL=sqlite:///./shopsmart.db for local runs.{Fore.WHITE}"
        )
        return None


def get_db_session() -> Session:
    """Legacy helper — returns a standalone session (used by services)."""
    engine = get_db_engine()
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return SessionLocal()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a request-scoped session."""
    engine = get_db_engine()
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    engine = get_db_engine()
    if engine is None:
        print(f"{Fore.RED}Skipping create_tables: no engine{Fore.WHITE}")
        return
    # pgvector extension for RAG vector search (Postgres only; ignored on SQLite).
    if not IS_SQLITE:
        try:
            with engine.connect() as conn:
                conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector")
                conn.commit()
        except Exception as e:
            print(f"[db] pgvector extension unavailable ({e}); using JSON fallback")
    # Import models so metadata is populated (importlib: `import *` is illegal inside functions)
    import importlib

    importlib.import_module("app.models.sqlalchemy")
    Base.metadata.create_all(bind=engine)
