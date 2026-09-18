from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class CheckResult(BaseModel):
    status: str  # "passed", "regenerate", "flagged"
    reason: Optional[str] = None
    variables_used: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    value: Optional[str] = None

class ValidationFeedback(BaseModel):
    check: str
    reason: str

class QualityGuardResult(BaseModel):
    status: str  # "passed", "regenerate", "flagged"
    action: str  # "display", "regenerate", "safe_fallback"
    attempts: int = 1
    max_attempts: int = 2
    checks: Dict[str, CheckResult]
    failed_checks: List[ValidationFeedback] = []
    reason: Optional[str] = None

class GuardedRecommendationProfileResponse(BaseModel):
    recommendation: Optional[Any] = None
    quality_guard: QualityGuardResult
    recommendation_available: bool = True
