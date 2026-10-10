from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.utils.logging import logger

class DocumentRepository:
    @staticmethod
    def get_by_id(db: Session, doc_id: str) -> Optional[Document]:
        return db.query(Document).filter(Document.id == doc_id).first()

    @staticmethod
    def get_by_content_hash(db: Session, content_hash: str) -> Optional[Document]:
        return db.query(Document).filter(Document.content_hash == content_hash).first()

    @staticmethod
    def get_by_title_version_region(db: Session, title: str, version: str, region: str) -> Optional[Document]:
        return db.query(Document).filter(
            Document.title == title,
            Document.version == version,
            Document.region == region
        ).first()

    @staticmethod
    def list_documents(
        db: Session,
        category: Optional[str] = None,
        region: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Document]:
        query = db.query(Document)
        if category:
            query = query.filter(Document.category == category)
        if region:
            query = query.filter(Document.region == region)
        if status:
            query = query.filter(Document.status == status)
        return query.order_by(desc(Document.created_at)).all()

    @staticmethod
    def create_document(
        db: Session,
        title: str,
        original_filename: str,
        category: str,
        version: str,
        effective_date: Optional[str],
        region: str,
        content_hash: str,
        embedding_model: str,
        status: str = "indexed"
    ) -> Document:
        doc = Document(
            title=title,
            original_filename=original_filename,
            category=category,
            version=version,
            effective_date=effective_date,
            region=region,
            status=status,
            content_hash=content_hash,
            embedding_model=embedding_model
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def mark_superseded(db: Session, category: str, region: str, current_doc_id: str):
        """Marks previous active versions in the same category & region as superseded."""
        previous_docs = db.query(Document).filter(
            Document.category == category,
            Document.region == region,
            Document.id != current_doc_id,
            Document.status == "indexed"
        ).all()
        for doc in previous_docs:
            doc.status = "superseded"
            logger.info(f"Superseding previous document version {doc.id} ({doc.title} v{doc.version})")
        db.commit()
