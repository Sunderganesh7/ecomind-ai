import uuid
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.models.conversation import ConversationModel, MessageModel, EnvironmentalFactModel
from app.llm.schemas import ConversationContext, ConversationMessage
from app.schemas.memory import EnvironmentalFactCreate

MAX_CONVERSATION_MESSAGES = 10

class MemoryManager:
    def get_or_create_context(self, db: Session, conversation_id: str = None) -> ConversationContext:
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            
        conv = db.query(ConversationModel).filter(ConversationModel.id == conversation_id).first()
        if not conv:
            conv = ConversationModel(id=conversation_id)
            db.add(conv)
            db.commit()
            db.refresh(conv)
            
        messages = db.query(MessageModel).filter(
            MessageModel.conversation_id == conversation_id
        ).order_by(MessageModel.created_at.desc(), MessageModel.id.desc()).limit(MAX_CONVERSATION_MESSAGES).all()
        
        # reverse to chronological
        messages = list(reversed(messages))
        
        context_messages = [
            ConversationMessage(role=m.role, content=m.content)
            for m in messages
        ]
        
        clarification_values = self._get_active_facts_dict(db, conversation_id)
        
        return ConversationContext(
            conversation_id=conversation_id,
            messages=context_messages,
            active_profile_id=conv.active_profile_id,
            last_topic=conv.last_topic,
            clarification_values=clarification_values
        )

    def _get_active_facts_dict(self, db: Session, conversation_id: str) -> Dict[str, Any]:
        # Return only the most recent 'active' fact for each variable
        facts = db.query(EnvironmentalFactModel).filter(
            EnvironmentalFactModel.conversation_id == conversation_id,
            EnvironmentalFactModel.status == "active"
        ).order_by(EnvironmentalFactModel.created_at.asc()).all()
        
        return {f.variable: self._parse_value(f.value) for f in facts}
        
    def _parse_value(self, val_str: str) -> Any:
        try:
            val = float(val_str)
            if val.is_integer():
                return int(val)
            return val
        except (ValueError, TypeError):
            return val_str

    def add_message(self, db: Session, conversation_id: str, role: str, content: str) -> MessageModel:
        conv = db.query(ConversationModel).filter(ConversationModel.id == conversation_id).first()
        if not conv:
            self.get_or_create_context(db, conversation_id)
            
        msg = MessageModel(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

    def set_active_profile(self, db: Session, conversation_id: str, profile_id: str):
        conv = db.query(ConversationModel).filter(ConversationModel.id == conversation_id).first()
        if conv:
            conv.active_profile_id = str(profile_id)
            db.commit()

    def switch_profile(self, db: Session, conversation_id: str, profile_id: str):
        """Start a clean profile-scoped history when a caller changes profile."""
        conv = db.query(ConversationModel).filter(ConversationModel.id == conversation_id).first()
        if not conv:
            self.get_or_create_context(db, conversation_id)
            conv = db.query(ConversationModel).filter(ConversationModel.id == conversation_id).first()
            
        if conv.active_profile_id and conv.active_profile_id != str(profile_id):
            # Soft reset or just hard delete messages? We'll delete them to simulate old behavior
            db.query(MessageModel).filter(MessageModel.conversation_id == conversation_id).delete()
            db.query(EnvironmentalFactModel).filter(EnvironmentalFactModel.conversation_id == conversation_id).delete()
            conv.last_topic = None
            
        conv.active_profile_id = str(profile_id)
        db.commit()

    def update_clarification(self, db: Session, conversation_id: str, message_id: int, facts: List[EnvironmentalFactCreate], topic: str):
        conv = db.query(ConversationModel).filter(ConversationModel.id == conversation_id).first()
        if conv:
            conv.last_topic = topic
            
        for fact in facts:
            # Mark previous explicit values for this variable as historical
            db.query(EnvironmentalFactModel).filter(
                EnvironmentalFactModel.conversation_id == conversation_id,
                EnvironmentalFactModel.variable == fact.variable,
                EnvironmentalFactModel.status == "active"
            ).update({"status": "historical"})
            
            new_fact = EnvironmentalFactModel(
                conversation_id=conversation_id,
                message_id=message_id,
                variable=fact.variable,
                value=str(fact.value),
                unit=fact.unit,
                time_context=fact.time_context,
                certainty=fact.certainty,
                status="active"
            )
            db.add(new_fact)
            
        db.commit()

# Global singleton for this phase
memory_manager = MemoryManager()
