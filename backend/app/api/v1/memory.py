from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.conversation import ConversationModel, MessageModel, EnvironmentalFactModel
from app.schemas.memory import ConversationResponse

router = APIRouter()

@router.get("/{conversation_id}/memory", response_model=ConversationResponse)
def get_conversation_memory(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.query(ConversationModel).filter(ConversationModel.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    return conv

@router.delete("/{conversation_id}/memory")
def clear_conversation_memory(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.query(ConversationModel).filter(ConversationModel.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    db.delete(conv)
    db.commit()
    return {"status": "success", "message": "Conversation memory cleared"}
