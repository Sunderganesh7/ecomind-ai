from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.recommendations.interventions.schemas import Tradeoff, EvidenceRecord

class Confidence(BaseModel):
    level: str
    reason: str

class ImpactedMetrics(BaseModel):
    direct: List[str] = []
    indirect: List[str] = []
    context_dependent: List[str] = []

class ReasoningStep(BaseModel):
    step: int
    type: str
    variables: Optional[List[str]] = None
    relationship_id: Optional[str] = None
    risk_pattern_id: Optional[str] = None
    intervention_id: Optional[str] = None
    chunk_ids: Optional[List[str]] = None
    status: Optional[str] = None

class StructuredRecommendation(BaseModel):
    recommendation_id: str
    what_to_do: str
    why_it_works: str
    environmental_mechanism: str
    impacted_metrics: ImpactedMetrics
    time_horizon: str
    confidence: Confidence
    evidence_status: str
    evidence_claims: List[str] = []
    evidence: List[Any] = []
    claims: List[Any] = []  # We will cast this or import Claim where needed
    risk_patterns_used: List[str] = []
    relationships_used: List[str] = []
    variables_used: List[str] = []
    matched_conditions: List[str] = []
    constraints: List[str] = []
    tradeoffs: List[Tradeoff] = []
    applicability: str
    missing_context: List[str] = []
    reasoning_trace: List[ReasoningStep] = []

class RecommendationProfileResponse(BaseModel):
    profile_id: int
    recommendations: List[StructuredRecommendation]
    recommendation_status: Optional[str] = None
    reason: Optional[str] = None
