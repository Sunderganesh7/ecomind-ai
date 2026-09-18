from typing import List, Optional

from pydantic import BaseModel, Field


class ClarificationResult(BaseModel):
    needs_clarification: bool
    missing_required: List[str] = Field(default_factory=list)
    optional_variables: List[str] = Field(default_factory=list)
    question: Optional[str] = None
    reason: Optional[str] = None
