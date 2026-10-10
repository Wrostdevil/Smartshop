from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import verify_admin_key
from app.services.ingestion_service import ingestion_service, IngestionError
from app.schemas import IngestionResponse
from app.utils.logging import logger

router = APIRouter(prefix="/api/ai", tags=["Knowledge Ingestion"])

@router.post(
    "/ingest-document",
    response_model=IngestionResponse,
    dependencies=[Depends(verify_admin_key)]
)
async def ingest_policy_document(
    file: UploadFile = File(..., description="The policy document to ingest (.pdf, .md, or .json)"),
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    version: Optional[str] = Form(None),
    region: Optional[str] = Form(None),
    effective_date: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Ingests an approved business policy document into PostgreSQL and pgvector.
    Requires administrative authentication header (X-API-Key or Bearer token).
    """
    try:
        content_bytes = await file.read()
        metadata = {}
        if title:
            metadata["title"] = title
        if category:
            metadata["category"] = category
        if version:
            metadata["version"] = version
        if region:
            metadata["region"] = region
        if effective_date:
            metadata["effective_date"] = effective_date

        result = ingestion_service.ingest_file_bytes(
            db=db,
            file_bytes=content_bytes,
            filename=file.filename,
            metadata=metadata
        )
        return IngestionResponse(**result)
    except IngestionError as ie:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ie)
        )
    except Exception as e:
        logger.error(f"Ingestion API unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest document due to internal server error."
        )
