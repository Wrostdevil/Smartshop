import re
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.message import ChatMessage
from app.repositories.vector_repository import VectorRepository
from app.services.embedding_service import embedding_service
from app.utils.logging import logger

class RetrievalService:
    @staticmethod
    def reformulate_query_with_context(question: str, history: Optional[List[ChatMessage]] = None) -> str:
        """
        Resolves coreferences (e.g. 'it', 'opened it', 'what about that') by combining
        the context of previous user queries if available.
        """
        if not history:
            return question

        followup_signals = ["it", "that", "this", "opened it", "opened the box", "what about", "how long will that take", "can i still"]
        q_lower = question.lower()

        needs_resolution = any(re.search(r"\b" + re.escape(sig) + r"\b", q_lower) for sig in followup_signals) or len(question.split()) <= 4

        if needs_resolution:
            # Find the most recent user question
            user_prev = [m.content for m in history if m.role == "user"]
            if user_prev:
                last_user_query = user_prev[-1]
                # Combined query providing contextual anchor
                combined = f"{last_user_query} Context: {question}"
                logger.info(f"Resolved follow-up query '{question}' to contextual query: '{combined}'")
                return combined

        return question

    @classmethod
    def retrieve_evidence(
        cls,
        db: Session,
        question: str,
        category: Optional[str] = None,
        region: Optional[str] = None,
        top_k: int = settings.RETRIEVAL_TOP_K,
        history: Optional[List[ChatMessage]] = None
    ) -> List[Tuple[DocumentChunk, Document, float]]:
        """
        Embeds the resolved query and retrieves top matching chunks from the database.
        Returns a list of (DocumentChunk, Document, similarity_score).
        """
        resolved_query = cls.reformulate_query_with_context(question, history)
        query_embedding = embedding_service.embed_query(resolved_query)

        results = VectorRepository.similarity_search(
            db=db,
            query_embedding=query_embedding,
            top_k=top_k,
            category=category,
            region=region,
            active_only=True
        )

        logger.info(f"Retrieved {len(results)} chunks for query: '{question}' (region={region}, cat={category})")
        return results

retrieval_service = RetrievalService()
