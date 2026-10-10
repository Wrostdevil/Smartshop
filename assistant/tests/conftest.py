import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.database import Base, get_db
from app.main import app
from app.services.ingestion_service import ingestion_service

# Use an isolated test database
TEST_DB_URL = "sqlite:///./test_shopsmart.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Initializes tables and seeds sample policies for the test suite."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    # Ingest the 5 sample policies into the test database
    db = TestingSessionLocal()
    policies_dir = os.path.join(PROJECT_ROOT, "data", "policies")
    for fname in ["returns.md", "refunds.md", "shipping.md", "warranty.md", "membership.md"]:
        fpath = os.path.join(policies_dir, fname)
        if os.path.exists(fpath):
            with open(fpath, "rb") as f:
                ingestion_service.ingest_file_bytes(db, f.read(), fname)
    db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("test_shopsmart.db"):
        try:
            os.remove("test_shopsmart.db")
        except Exception:
            pass

@pytest.fixture
def db_session():
    """Provides a fresh database session for a test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db_session):
    """Provides a TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
