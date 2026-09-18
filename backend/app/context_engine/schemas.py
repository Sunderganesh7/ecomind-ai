from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ContextualizedQuery(BaseModel):
    original_query: str = Field(description="The original user query.")
    resolved_query: str = Field(description="The query rewritten with contextual references resolved.")
    query_intent: str = Field(description="The identified intent of the query.")
    referenced_topics: List[str] = Field(default_factory=list, description="Topics referenced in the query.")
    referenced_variables: List[str] = Field(default_factory=list, description="Environmental variables relevant to the query.")
    conversation_context: Dict[str, Any] = Field(default_factory=dict, description="Contextual elements used for resolution.")
    retrieval_query: str = Field(description="The query optimized for semantic retrieval.")
    context_confidence: str = Field(description="Confidence level of the context resolution: high, medium, low, undetermined.")
    clarification_required: bool = Field(default=False, description="Whether the query is too ambiguous and needs clarification.")
    clarification_question: Optional[str] = Field(default=None, description="The clarification question to ask the user.")
