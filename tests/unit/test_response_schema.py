import pytest
from pydantic import ValidationError
from app.schemas.response import EnvironmentalResponse

def test_valid_structured_response():
    data = {
        "response_type": "environmental_assessment",
        "assessment": {
            "summary": "Everything is fine.",
            "status": "stable"
        },
        "drivers": [
            {
                "variable": "organic_carbon",
                "value": 0.3,
                "unit": "%",
                "status": "potential_constraint",
                "role": "primary_driver",
                "source": "environmental_profile"
            }
        ],
        "recommendations": [],
        "metrics": [],
        "time_horizon": {
            "value": "not_applicable",
            "reason": "No changes needed."
        },
        "confidence": {
            "level": "high",
            "reason": "Data is comprehensive."
        },
        "claims": [],
        "variables_used": ["organic_carbon"],
        "reasoning_trace": []
    }
    
    response = EnvironmentalResponse(**data)
    assert response.assessment.summary == "Everything is fine."
    assert response.drivers[0].variable == "organic_carbon"

def test_missing_fields_rejected():
    data = {
        "response_type": "environmental_assessment",
        "assessment": {
            "summary": "Missing fields test.",
            "status": "stable"
        },
        # time_horizon and confidence are missing
    }
    
    with pytest.raises(ValidationError):
        EnvironmentalResponse(**data)

def test_invalid_enum_rejected():
    data = {
        "response_type": "invalid_type",
        "assessment": {
            "summary": "Invalid enum.",
            "status": "stable"
        },
        "time_horizon": {
            "value": "forever", # Invalid enum
            "reason": "Test"
        },
        "confidence": {
            "level": "95%", # Invalid enum
            "reason": "Test"
        }
    }
    
    with pytest.raises(ValidationError) as exc:
        EnvironmentalResponse(**data)
    assert "response_type" in str(exc.value)
    assert "time_horizon.value" in str(exc.value) or "time_horizon" in str(exc.value)
    assert "confidence.level" in str(exc.value) or "confidence" in str(exc.value)

def test_extra_fields_forbidden():
    data = {
        "response_type": "environmental_assessment",
        "assessment": {
            "summary": "Extra fields test.",
            "status": "stable"
        },
        "time_horizon": {
            "value": "not_applicable",
            "reason": "Test"
        },
        "confidence": {
            "level": "high",
            "reason": "Test"
        },
        "invented_field": "This should fail validation"
    }
    
    with pytest.raises(ValidationError) as exc:
        EnvironmentalResponse(**data)
    assert "invented_field" in str(exc.value)

def test_invalid_evidence_structure():
    data = {
        "response_type": "environmental_assessment",
        "assessment": {
            "summary": "Evidence structure test.",
            "status": "stable"
        },
        "time_horizon": {
            "value": "not_applicable",
            "reason": "Test"
        },
        "confidence": {
            "level": "high",
            "reason": "Test"
        },
        "claims": [
            {
                "claim_id": "test",
                # missing claim_text, claim_type, origin, support_status
            }
        ]
    }
    
    with pytest.raises(ValidationError):
        EnvironmentalResponse(**data)
