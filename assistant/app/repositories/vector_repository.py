import numpy as np
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.utils.logging import logger

class VectorRepository:
    @staticmethod
    def save_chunks(db: Session, chunks_data: List[dict]) -> List[DocumentChunk]:
        created_chunks = []
        for item in chunks_data:
            chunk = DocumentChunk(
                document_id=item["document_id"],
                chunk_index=item["chunk_index"],
                section=item.get("section", "General"),
                page_number=item.get("page_number"),
                content=item["content"],
                embedding=item["embedding"]
            )
            db.add(chunk)
            created_chunks.append(chunk)
        db.commit()
        return created_chunks

    @staticmethod
    def get_chunks_by_document(db: Session, doc_id: str) -> List[DocumentChunk]:
        return db.query(DocumentChunk).filter(
            DocumentChunk.document_id == doc_id
        ).order_by(DocumentChunk.chunk_index).all()

    @staticmethod
    def similarity_search(
        db: Session,
        query_embedding: List[float],
        top_k: int = 5,
        category: Optional[str] = None,
        region: Optional[str] = None,
        active_only: bool = True
    ) -> List[Tuple[DocumentChunk, Document, float]]:
        """
        Performs vector similarity search against indexed document chunks.
        Supports native pgvector cosine distance on PostgreSQL, with fallback for SQLite testing.
        Returns a list of tuples: (DocumentChunk, Document, similarity_score).
        """
        is_postgres = "postgresql" in str(db.bind.url)

        query = db.query(DocumentChunk, Document).join(
            Document, DocumentChunk.document_id == Document.id
        )

        if active_only:
            query = query.filter(Document.status == "indexed")

        if category:
            query = query.filter(Document.category == category)

        if region:
            query = query.filter((Document.region == region) | (Document.region == "GLOBAL"))

        if is_postgres:
            try:
                # Use native pgvector cosine distance: chunk.embedding.cosine_distance(query_embedding)
                # Cosine distance = 1 - cosine_similarity. Similarity = 1 - distance
                distance_col = DocumentChunk.embedding.cosine_distance(query_embedding).label("distance")
                results = db.query(DocumentChunk, Document, distance_col).join(
                    Document, DocumentChunk.document_id == Document.id
                )
                if active_only:
                    results = results.filter(Document.status == "indexed")
                if category:
                    results = results.filter(Document.category == category)
                if region:
                    results = results.filter((Document.region == region) | (Document.region == "GLOBAL"))

                ordered_results = results.order_by(distance_col).limit(top_k).all()
                formatted = []
                for chunk, doc, dist in ordered_results:
                    sim = max(0.0, min(1.0, 1.0 - float(dist)))
                    formatted.append((chunk, doc, sim))
                return formatted
            except Exception as e:
                logger.warning(f"Native pgvector distance failed, falling back to python vector math: {e}")

        # SQLite / In-memory Fallback
        all_candidates = query.all()
        if not all_candidates:
            return []

        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []

        scored_candidates = []
        for chunk, doc in all_candidates:
            if chunk.embedding is None:
                continue
            c_vec = np.array(chunk.embedding, dtype=np.float32)
            c_norm = np.linalg.norm(c_vec)
            if c_norm == 0:
                continue
            sim = float(np.dot(q_vec, c_vec) / (q_norm * c_norm))
            scored_candidates.append((chunk, doc, sim))

        # Sort descending by similarity
        scored_candidates.sort(key=lambda x: x[2], reverse=True)
        return scored_candidates[:top_k]
