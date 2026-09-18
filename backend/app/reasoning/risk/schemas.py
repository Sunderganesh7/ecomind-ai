from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class RiskPatternDefinition(BaseModel):
    risk_pattern_id: str
    name: str
    required_signals: List[str]
    supporting_signals: List[str]
    relationships: List[str]
    outcome: str

class Driver(BaseModel):
    variable: Optional[str] = None
    state: Optional[str] = None
    status: str
    type: str  # "observed" or "inferred"
    role: str  # "primary_driver" or "secondary_consequence"
    value: Optional[Any] = None

class EvidenceRecord(BaseModel):
    chunk_id: str
    source: str
    title: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    relevance: float

class Uncertainty(BaseModel):
    level: str
    reasons: List[str]

class TraceStep(BaseModel):
    step: int
    type: str
    variable: Optional[str] = None
    state: Optional[str] = None
    status: Optional[str] = None
    relationship_id: Optional[str] = None
    pattern: Optional[str] = None
    source_ids: Optional[List[str]] = None

class Synthesis(BaseModel):
    type: str
    affected_system: str
    supporting_relationships: List[str]

class CompositeRiskPattern(BaseModel):
    risk_pattern_id: str
    name: str
    status: str
    variables_used: List[str]
    primary_drivers: List[Driver]
    supporting_signals: List[Driver]
    relationships_used: List[str]
    secondary_consequences: List[Driver]
    evidence_status: str
    evidence: List[EvidenceRecord] = []
    uncertainty: Uncertainty
    reasoning_trace: List[TraceStep]
    missing_variables: Optional[List[str]] = None
    synthesis: Optional[Synthesis] = None

class RiskProfileResponse(BaseModel):
    profile_id: int
    risk_patterns: List[CompositeRiskPattern]
