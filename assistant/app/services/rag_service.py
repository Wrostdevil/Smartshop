import json
import asyncio
from typing import Optional, AsyncGenerator
from sqlalchemy.orm import Session
from app.config import settings
from app.database import SessionLocal
from app.repositories.conversation_repository import ConversationRepository
from app.services.retrieval_service import retrieval_service
from app.services.answer_service import answer_service
from app.schemas import RagQueryRequest, RagQueryResponse
from app.utils.logging import logger

class RagService:
    @staticmethod
    def answer_query(
        db: Session,
        request: RagQueryRequest
    ) -> RagQueryResponse:
        """
        Executes end-to-end RAG pipeline:
        Conversation -> Coreference Resolution -> pgvector Retrieval -> Grounded Answer -> Citations -> Persistence.
        """
        logger.info(f"Processing RAG query: '{request.question}' (conv_id={request.conversationId})")

        # 1. Manage Conversation Context
        conv = ConversationRepository.get_or_create(db, request.conversationId)
        history = ConversationRepository.get_recent_history(db, conv.id, max_turns=settings.MAX_HISTORY_TURNS)

        # 2. Retrieve Evidence Chunks from pgvector
        retrieved_items = retrieval_service.retrieve_evidence(
            db=db,
            question=request.question,
            category=request.category,
            region=request.region,
            top_k=settings.RETRIEVAL_TOP_K,
            history=history
        )

        # 3. Grounded Answer Synthesis with Citation Validation
        result = answer_service.generate_answer(
            question=request.question,
            retrieved_items=retrieved_items,
            history=history
        )

        # 4. Persist User and Assistant Messages
        ConversationRepository.save_message(
            db=db,
            conversation_id=conv.id,
            role="user",
            content=request.question
        )

        sources_data = [s.model_dump() for s in result["sources"]]
        ConversationRepository.save_message(
            db=db,
            conversation_id=conv.id,
            role="assistant",
            content=result["answer"],
            sources=sources_data,
            confidence=result["confidence"]
        )

        return RagQueryResponse(
            answer=result["answer"],
            confidence=result["confidence"],
            sources=result["sources"],
            followUpRequired=result["followUpRequired"],
            followUpQuestion=result["followUpQuestion"],
            conversationId=conv.id
        )

    @staticmethod
    async def stream_answer_query(
        request: RagQueryRequest
    ) -> AsyncGenerator[str, None]:
        """
        Executes streaming RAG pipeline with Server-Sent Events (SSE).
        Yields real-time thinking steps and token chunks.
        """
        db = SessionLocal()
        try:
            logger.info(f"Processing streaming RAG query: '{request.question}' (conv_id={request.conversationId})")

            # 1. Manage Conversation Context
            conv = ConversationRepository.get_or_create(db, request.conversationId)
            history = ConversationRepository.get_recent_history(db, conv.id, max_turns=settings.MAX_HISTORY_TURNS)

            yield f"data: {json.dumps({'type': 'thought', 'content': 'Loading conversation session and history...'})}\n\n"

            # 2. Retrieve Evidence Chunks
            yield f"data: {json.dumps({'type': 'thought', 'content': 'Executing semantic retrieval with FastEmbed dense vectors...'})}\n\n"

            retrieved_items = retrieval_service.retrieve_evidence(
                db=db,
                question=request.question,
                category=request.category,
                region=request.region,
                top_k=settings.RETRIEVAL_TOP_K,
                history=history
            )

            # 3. Stream from answer_service
            accumulated_tokens = []
            final_metadata = {}

            async for event in answer_service.stream_answer(request.question, retrieved_items, history):
                if event["type"] == "token":
                    accumulated_tokens.append(event["content"])
                elif event["type"] == "metadata":
                    final_metadata = event

                yield f"data: {json.dumps(event)}\n\n"

            # 4. Persist User and Assistant Messages
            ConversationRepository.save_message(
                db=db,
                conversation_id=conv.id,
                role="user",
                content=request.question
            )

            full_answer = "".join(accumulated_tokens).strip()
            ConversationRepository.save_message(
                db=db,
                conversation_id=conv.id,
                role="assistant",
                content=full_answer,
                sources=final_metadata.get("sources", []),
                confidence=final_metadata.get("confidence", "MEDIUM")
            )

            yield f"data: {json.dumps({'type': 'done', 'conversationId': conv.id})}\n\n"

        except Exception as e:
            logger.error(f"Error in stream_answer_query: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            db.close()

rag_service = RagService()
