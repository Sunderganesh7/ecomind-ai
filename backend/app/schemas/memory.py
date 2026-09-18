from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

class EnvironmentalFactBase(BaseModel):
    variable: str = Field(description="The canonical name of the environmental variable (e.g. organic_carbon)")
    value: Any = Field(description="The extracted value")
    unit: Optional[str] = Field(default=None, description="The unit if provided (e.g. %, mm)")
    time_context: str = Field(default="current_year", description="Temporal context of the measurement")
    certainty: str = Field(default="explicit", description="How the fact was derived (e.g. explicit, inferred)")

class EnvironmentalFactCreate(EnvironmentalFactBase):
    pass

class EnvironmentalFactResponse(EnvironmentalFactBase):
    id: int
    conversation_id: str
    message_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationMessageBase(BaseModel):
    role: str
    content: str

class ConversationMessageResponse(ConversationMessageBase):
    id: int
    conversation_id: str
    created_at: datetime
    extracted_facts: List[EnvironmentalFactResponse] = []

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: str
    active_profile_id: Optional[str] = None
    last_topic: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[ConversationMessageResponse] = []
    
    class Config:
        from_attributes = True
