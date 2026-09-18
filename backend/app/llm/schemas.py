from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class EvidenceReference(BaseModel):
    source_id: str = Field(description="The source identifier of the retrieved evidence.")
    chunk_id: str = Field(description="The chunk identifier of the retrieved evidence.")

class LLMResponse(BaseModel):
    answer: str = Field(description="The natural language explanation answering the user's query.")
    reasoning_summary: List[str] = Field(description="A concise summary of the deterministic analysis, conditions, mechanisms, and evidence that lead to this answer.")
    referenced_metrics: List[str] = Field(description="The exact environmental metrics (e.g. 'organic_carbon') referenced in the answer.")
    evidence_references: List[EvidenceReference] = Field(default_factory=list, description="List of evidence chunks explicitly cited to support the scientific claims in the answer.")
    referenced_intervention_ids: List[str] = Field(default_factory=list)
    referenced_relationship_ids: List[str] = Field(default_factory=list)
    referenced_risk_ids: List[str] = Field(default_factory=list)
    uncertainty: str = Field(description="The overall uncertainty of the response, must be one of: 'high', 'medium', 'low', 'undetermined'.")
    limitations: List[str] = Field(default_factory=list, description="Any limitations, missing context, or missing evidence that prevent a conclusive answer.")

class ChatResponse(LLMResponse):
    conversation_id: str

class ConversationMessage(BaseModel):
    role: str
    content: str
    
class ConversationContext(BaseModel):
    conversation_id: str
    messages: List[ConversationMessage] = Field(default_factory=list)
    active_profile_id: Optional[str] = None
    last_recommendation_id: Optional[str] = None
    last_topic: Optional[str] = None
    clarification_values: Dict[str, Any] = Field(default_factory=dict)
    
class LLMContextData(BaseModel):
    user_query: str
    profile: Dict[str, Any] = Field(default_factory=dict)
    baseline: Dict[str, Any] = Field(default_factory=dict)
    relationships: Dict[str, Any] = Field(default_factory=dict)
    risks: Dict[str, Any] = Field(default_factory=dict)
    intervention_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    recommendation: Optional[Dict[str, Any]] = None
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    conversation_context: ConversationContext
    quality_guard_status: str = "unknown"
    quality_guard_reason: str = ""
    deterministic_trace: Dict[str, Any] = Field(default_factory=dict)
    claims: List[Dict[str, Any]] = Field(default_factory=list)
