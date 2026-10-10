from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.config import settings
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.repositories.vector_repository import VectorRepository
from app.services.document_loader import DocumentLoader, LoadedDocument, DocumentLoaderError
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import embedding_service
from app.schemas import IngestionResponse
from app.utils.logging import logger

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit

class IngestionError(Exception):
    pass

class IngestionService:
    def __init__(self):
        self.chunker = ChunkingService(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

    def ingest_file_bytes(
        self,
        db: Session,
        file_bytes: bytes,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrates full ingestion pipeline:
        Validation -> Loading -> Deduplication -> Chunking -> Embedding -> Storage.
        """
        warnings = []
        metadata = metadata or {}

        # 1. Validation: Size check
        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            raise IngestionError(f"File size exceeds maximum allowed threshold of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB.")

        if not file_bytes:
            raise IngestionError("Uploaded file is empty (0 bytes).")

        # 2. Extract and parse
        ext = filename.lower().split(".")[-1] if "." in filename else ""
        try:
            if ext in ["md", "markdown"]:
                loaded_doc = DocumentLoader.load_markdown(file_bytes, filename, metadata)
            elif ext == "pdf":
                loaded_doc = DocumentLoader.load_pdf(file_bytes, filename, metadata)
            elif ext == "json":
                loaded_doc = DocumentLoader.load_json(file_bytes, filename, metadata)
            else:
                raise IngestionError(f"Unsupported file type: '.{ext}'. Supported formats: .pdf, .md, .json")
        except DocumentLoaderError as dle:
            logger.error(f"Loader error for {filename}: {dle}")
            raise IngestionError(str(dle))

        # 3. Duplicate Detection via content hash
        existing = DocumentRepository.get_by_content_hash(db, loaded_doc.content_hash)
        if existing and existing.status == "indexed":
            logger.info(f"Document '{filename}' already indexed as {existing.id} (matching content hash).")
            return {
                "documentId": existing.id,
                "status": "already_indexed",
                "chunksCreated": len(existing.chunks),
                "embeddingModel": existing.embedding_model,
                "warnings": ["Duplicate content detected. Existing active policy retained without re-indexing."]
            }

        # 4. Handle Policy Versioning: Supersede prior versions in same category & region
        try:
            # Create Document record
            doc = DocumentRepository.create_document(
                db=db,
                title=loaded_doc.title,
                original_filename=filename,
                category=loaded_doc.category,
                version=loaded_doc.version,
                effective_date=loaded_doc.effective_date,
                region=loaded_doc.region,
                content_hash=loaded_doc.content_hash,
                embedding_model=embedding_service.model_name,
                status="indexing"
            )

            # Supersede previous versions
            DocumentRepository.mark_superseded(
                db=db,
                category=loaded_doc.category,
                region=loaded_doc.region,
                current_doc_id=doc.id
            )

            # 5. Chunking
            raw_chunks = self.chunker.chunk_document(loaded_doc)
            if not raw_chunks:
                doc.status = "failed"
                db.commit()
                raise IngestionError(f"Document produced 0 chunks after text extraction.")

            # 6. Embedding Generation
            contents = [c["content"] for c in raw_chunks]
            embeddings = embedding_service.embed_texts(contents)

            # 7. Persistence
            chunks_to_save = []
            for idx, c in enumerate(raw_chunks):
                c_data = {
                    "document_id": doc.id,
                    "chunk_index": c["chunk_index"],
                    "section": c["section"],
                    "page_number": c["page_number"],
                    "content": c["content"],
                    "embedding": embeddings[idx]
                }
                chunks_to_save.append(c_data)

            saved = VectorRepository.save_chunks(db, chunks_to_save)
            doc.status = "indexed"
            db.commit()

            logger.info(f"Successfully indexed document {doc.id} with {len(saved)} chunks.")
            return {
                "documentId": doc.id,
                "status": "indexed",
                "chunksCreated": len(saved),
                "embeddingModel": embedding_service.model_name,
                "warnings": warnings
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Ingestion pipeline failure for {filename}: {e}", exc_info=True)
            raise IngestionError(f"Ingestion failed: {str(e)}")

ingestion_service = IngestionService()
