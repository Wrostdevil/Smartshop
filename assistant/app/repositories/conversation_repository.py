import json
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.message import ChatMessage

class ConversationRepository:
    @staticmethod
    def get_or_create(db: Session, conversation_id: Optional[str] = None) -> Conversation:
        if conversation_id:
            conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conv:
                return conv
        cid = conversation_id or str(uuid.uuid4())
        conv = Conversation(id=cid)
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return conv

    @staticmethod
    def save_message(
        db: Session,
        conversation_id: str,
        role: str,
        content: str,
        sources: Optional[List[dict]] = None,
        confidence: Optional[str] = None
    ) -> ChatMessage:
        sources_json = json.dumps(sources) if sources else None
        msg = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources=sources_json,
            confidence=confidence
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

    @staticmethod
    def get_recent_history(db: Session, conversation_id: str, max_turns: int = 5) -> List[ChatMessage]:
        messages = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at.desc()).limit(max_turns * 2).all()
        # Return in chronological order
        return list(reversed(messages))
