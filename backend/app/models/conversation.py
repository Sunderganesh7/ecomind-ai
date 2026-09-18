from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

class ConversationModel(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, index=True) # UUID string
    active_profile_id = Column(String, nullable=True) # Optional profile ID
    last_topic = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    messages = relationship("MessageModel", back_populates="conversation", cascade="all, delete-orphan", order_by="MessageModel.created_at")
    environmental_facts = relationship("EnvironmentalFactModel", back_populates="conversation", cascade="all, delete-orphan")

class MessageModel(Base):
    __tablename__ = "conversation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, nullable=False) # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    
    conversation = relationship("ConversationModel", back_populates="messages")
    extracted_facts = relationship("EnvironmentalFactModel", back_populates="source_message", cascade="all, delete-orphan")

class EnvironmentalFactModel(Base):
    __tablename__ = "environmental_facts"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    message_id = Column(Integer, ForeignKey("conversation_messages.id", ondelete="CASCADE"), nullable=False, index=True)
    
    variable = Column(String, nullable=False, index=True) # e.g. "organic_carbon"
    value = Column(String, nullable=False) # Stored as string to support "wheat" or "0.3"
    unit = Column(String, nullable=True)
    time_context = Column(String, default="current_year", nullable=False)
    certainty = Column(String, default="explicit", nullable=False) # "explicit", "derived"
    status = Column(String, default="active", nullable=False) # "active", "historical", "conflicting"
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    conversation = relationship("ConversationModel", back_populates="environmental_facts")
    source_message = relationship("MessageModel", back_populates="extracted_facts")
