from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class Tradeoff(BaseModel):
    description: str
    metrics: List[str]
    context: str

class MetricImpact(BaseModel):
    metric: str
    effect: str  # potential_improvement, potential_reduction, potential_stabilization, potential_protection, context_dependent
    pathway: str

class Mechanism(BaseModel):
    mechanism_id: str
    description: str
    evidence_required: bool
    affected_metrics: List[MetricImpact] = []

class InterventionDefinition(BaseModel):
    intervention_id: str
    name: str
    target_conditions: List[str]  # e.g., low_organic_carbon, composite_biodiversity_pressure
    mechanisms: List[Mechanism]
    evidence_requirements: List[str]  # e.g., topics like soil_health
    constraints: List[str]  # e.g., water_availability
    tradeoffs: List[Tradeoff] = []
    time_horizon: str  # e.g., short_term, medium_term, long_term, context_dependent

class EvidenceRecord(BaseModel):
    chunk_id: str
    document_id: str
    source_id: str
    source: str
    document: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    url: Optional[str] = None
    relevance: float

class Uncertainty(BaseModel):
    level: str
    reasons: List[str]

class CandidateIntervention(BaseModel):
    intervention_id: str
    name: str
    matched_conditions: List[str]
    mechanisms: List[str]
    potentially_affected_metrics: List[str]
    evidence_status: str
    evidence: List[EvidenceRecord] = []
    constraints: List[str] = []
    tradeoffs: List[Tradeoff] = []
    time_horizon: str
    uncertainty: Uncertainty

class InterventionProfileResponse(BaseModel):
    profile_id: int
    risk_patterns_used: List[str]
    intervention_candidates: List[CandidateIntervention]
