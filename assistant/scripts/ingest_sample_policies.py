import os
import sys

# Ensure project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.database import init_db, SessionLocal
from app.services.ingestion_service import ingestion_service
from app.utils.logging import logger

def ingest_sample_policies():
    """
    Ingests the sample policy corpus into PostgreSQL and pgvector.
    Safe to rerun idempotently: identical files are recognized via content hashing.
    """
    logger.info("Initializing database schema...")
    init_db()

    policies_dir = os.path.join(PROJECT_ROOT, "data", "policies")
    if not os.path.exists(policies_dir):
        logger.error(f"Policies directory not found at: {policies_dir}")
        return

    sample_files = [
        "returns.md",
        "refunds.md",
        "shipping.md",
        "warranty.md",
        "membership.md"
    ]

    db = SessionLocal()
    try:
        logger.info(f"Beginning ingestion of {len(sample_files)} sample policies from {policies_dir}...")
        for filename in sample_files:
            file_path = os.path.join(policies_dir, filename)
            if not os.path.exists(file_path):
                logger.warning(f"File {filename} not found, skipping.")
                continue

            with open(file_path, "rb") as f:
                file_bytes = f.read()

            result = ingestion_service.ingest_file_bytes(
                db=db,
                file_bytes=file_bytes,
                filename=filename
            )
            logger.info(
                f"[{result['status'].upper()}] {filename} -> Document ID: {result['documentId']} "
                f"({result['chunksCreated']} chunks, Model: {result['embeddingModel']})"
            )
        logger.info("Sample policies ingestion completed successfully.")
    except Exception as e:
        logger.error(f"Error during sample policy ingestion: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    ingest_sample_policies()
