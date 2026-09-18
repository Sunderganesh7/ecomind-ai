from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Literal

class Assessment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    summary: str = Field(description="The natural language explanation answering the user's query.")
    status: str = Field(description="The overall status (e.g. 'potential_pressure', 'informational', 'stable').")

class Driver(BaseModel):
    model_config = ConfigDict(extra="ignore")
    variable: str = "unspecified"
    value: Any = None
    unit: Optional[str] = None
    status: str = "unknown"
    role: Literal["primary_driver", "secondary_consequence", "context"] = "context"
    source: str = "unknown"

class Recommendation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    intervention_id: str
    what_to_do: str
    why_it_works: str
    environmental_mechanism: str
    impacted_metrics: List[str]
    time_horizon: str
    confidence: str
    evidence_claims: List[str] = Field(default_factory=list)

class Metric(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str
    current_value: Any = None
    unit: Optional[str] = None
    role: Literal["direct", "indirect", "context", "context_dependent"]
    status: str

class TimeHorizon(BaseModel):
    model_config = ConfigDict(extra="ignore")
    value: Literal["short_term", "medium_term", "long_term", "context_dependent", "not_applicable"]
    reason: str

class Confidence(BaseModel):
    model_config = ConfigDict(extra="ignore")
    level: Literal["high", "medium", "low", "undetermined"]
    reason: str

class EvidenceReference(BaseModel):
    model_config = ConfigDict(extra="ignore")
    source_id: str
    chunk_id: str
    document_id: str
    source: str
    document: str
    year: Optional[int] = None
    page_number: Optional[int] = None
    section: Optional[str] = None
    url: Optional[str] = None
    relevance: float

class Claim(BaseModel):
    model_config = ConfigDict(extra="ignore")
    claim_id: str
    claim_text: str
    claim_type: Literal["environmental_observation", "baseline_assessment", "relationship", "risk_driver", "risk_consequence", "environmental_mechanism", "recommendation_reason", "metric_impact", "general_scientific_statement"]
    origin: Literal["user_observed", "deterministic_analysis", "scientific_evidence", "llm_synthesis"]
    support_status: Literal["supported", "partially_supported", "insufficient_evidence", "untraceable"]
    reasoning_reference: Optional[dict] = None
    evidence: List[EvidenceReference] = Field(default_factory=list)

class ReasoningStep(BaseModel):
    model_config = ConfigDict(extra="ignore")
    step: int
    type: Literal["observed_condition", "relationship", "risk_pattern", "intervention", "evidence"]
    variables: Optional[List[str]] = None
    relationship_id: Optional[str] = None
    risk_pattern_id: Optional[str] = None
    intervention_id: Optional[str] = None
    chunk_ids: Optional[List[str]] = None

class EnvironmentalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: str = Field(default="1.0")
    response_type: Literal["environmental_assessment", "recommendation", "explanation", "evidence_answer", "clarification", "general_information"]
    assessment: Assessment
    drivers: List[Driver] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)
    metrics: List[Metric] = Field(default_factory=list)
    time_horizon: TimeHorizon
    confidence: Confidence
    claims: List[Claim] = Field(default_factory=list)
    variables_used: List[str] = Field(default_factory=list)
    reasoning_trace: List[ReasoningStep] = Field(default_factory=list)
    
class ChatResponse(EnvironmentalResponse):
    model_config = ConfigDict(extra="ignore")
    conversation_id: str
