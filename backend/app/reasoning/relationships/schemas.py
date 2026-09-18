from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class RelationshipDefinition(BaseModel):
    relationship_id: str
    name: str
    required_inputs: List[str]
    intermediate_states: List[str]
    downstream_states: List[str]
    evidence_topics: List[str]

class EvidenceRecord(BaseModel):
    chunk_id: str
    source: str
    title: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    relevance: float

class InferredState(BaseModel):
    name: str
    status: str
    type: str = "inferred"

class InputState(BaseModel):
    value: Any
    status: str
    type: str = "observed"

class Uncertainty(BaseModel):
    level: str
    reasons: List[str]

class RelationshipEvaluation(BaseModel):
    relationship_id: str
    inputs: List[str]
    input_states: Dict[str, InputState]
    intermediate_states: List[InferredState]
    downstream_states: List[InferredState]
    status: str
    evidence_status: str
    evidence: List[EvidenceRecord] = []
    uncertainty: Uncertainty

class TraceStep(BaseModel):
    step: int
    type: str
    variables: Optional[List[str]] = None
    relationship_id: Optional[str] = None
    state: Optional[str] = None
    source_ids: Optional[List[str]] = None

class RelationshipProfileResponse(BaseModel):
    profile_id: int
    variables_used: List[str]
    relationships: List[RelationshipEvaluation]
    reasoning_trace: List[TraceStep]
