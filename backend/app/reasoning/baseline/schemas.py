from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class ReferenceSource(BaseModel):
    source: Optional[str] = None
    title: Optional[str] = None
    year: Optional[int] = None
    url: Optional[str] = None

class ReferenceContext(BaseModel):
    type: str = Field(..., description="The type of reference (range, categorical, context_dependent)")
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    unit: Optional[str] = None
    context: Optional[str] = None
    source: Optional[ReferenceSource] = None

class MetricAssessment(BaseModel):
    metric: str
    observed_value: Any
    unit: Optional[str] = None
    status: str
    risk: str
    reason: Optional[str] = None
    reference: Optional[ReferenceContext] = None
    evidence: Optional[ReferenceSource] = None

class BaselineAggregateStatus(BaseModel):
    status: str
    supporting_metrics: List[str]

class AggregatedBaseline(BaseModel):
    soil_status: Optional[BaselineAggregateStatus] = None
    water_status: Optional[BaselineAggregateStatus] = None
    habitat_status: Optional[BaselineAggregateStatus] = None
    
class BaselineProfileResponse(BaseModel):
    profile_id: int
    metrics: Dict[str, MetricAssessment]
    summary: AggregatedBaseline
