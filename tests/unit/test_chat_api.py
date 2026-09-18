import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.schemas.response import EnvironmentalResponse, Assessment, Confidence
from app.memory.manager import memory_manager

client = TestClient(app)

@patch("app.api.v1.chat.ClarificationEngine")
@patch("app.api.v1.chat.generate_conversational_response")
@patch("app.api.v1.chat.profile_service.get_profile")
def test_chat_endpoint_orchestration(mock_get_profile, mock_generate, mock_clarification_engine_cls):
    # Setup clarification mock
    mock_clarification_engine = MagicMock()
    mock_clarification_engine_cls.return_value = mock_clarification_engine
    mock_clarification_result = MagicMock()
    mock_clarification_result.needs_clarification = False
    mock_clarification_engine.evaluate.return_value = (mock_clarification_result, {}, "general")
    mock_clarification_engine.overlay_profile.side_effect = lambda p, v: p

    # Setup mocks
    mock_profile = MagicMock()
    mock_profile.id = 1
    mock_profile.soil = MagicMock()
    mock_profile.soil.organic_carbon = 0.5
    mock_profile.soil.model_dump.return_value = {"organic_carbon": 0.5}
    mock_profile.climate = MagicMock()
    mock_profile.climate.rainfall = 600
    mock_profile.climate.model_dump.return_value = {"rainfall": 600}
    mock_profile.land = MagicMock()
    mock_profile.land.cropping_system = "monoculture"
    mock_profile.land.model_dump.return_value = {"cropping_system": "monoculture"}
    mock_profile.biodiversity = None
    mock_profile.human_impact = None
    
    mock_get_profile.return_value = mock_profile
    
    mock_generate.return_value = EnvironmentalResponse(
        response_type="environmental_assessment",
        assessment=Assessment(summary="The profile indicates low organic carbon.", status="informational"),
        time_horizon={"value": "not_applicable", "reason": ""},
        confidence=Confidence(level="low", reason=""),
        metrics=[{"name": "organic_carbon", "role": "direct", "status": "low"}],
        drivers=[],
        recommendations=[],
        claims=[],
        variables_used=[],
        reasoning_trace=[]
    )
    
    # Execute Request
    response = client.post("/api/v1/chat/", json={
        "profile_id": "1",
        "message": "Why is biodiversity low?"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["assessment"]["summary"] == "The profile indicates low organic carbon."
    assert any(m["name"] == "organic_carbon" for m in data["metrics"])
    assert data["conversation_id"]
    
    # Ensure profile was loaded
    mock_get_profile.assert_called_once()
    
def test_chat_missing_profile():
    response = client.post("/api/v1/chat/", json={
        "message": "Hello"
    })
    
    assert response.status_code == 200
    assert "profile ID" in response.json()["assessment"]["summary"]
    assert response.json()["confidence"]["level"] == "undetermined"

@patch("app.api.v1.chat.ClarificationEngine")
@patch("app.api.v1.chat.generate_conversational_response")
@patch("app.api.v1.chat.build_llm_context")
@patch("app.api.v1.chat.RecommendationEngine")
@patch("app.api.v1.chat.InterventionEvaluator")
@patch("app.api.v1.chat.RiskEvaluator")
@patch("app.api.v1.chat.RelationshipEvaluator")
@patch("app.api.v1.chat.BaselineAnalyzer")
@patch("app.api.v1.chat.profile_service.get_profile")
def test_memory_failure_uses_current_profile_pipeline(
    mock_profile, mock_baseline, mock_relationships, mock_risks, mock_interventions,
    mock_recommendations, mock_context_builder, mock_generate, mock_clarification_engine_cls
):
    mock_clarification_engine = MagicMock()
    mock_clarification_engine_cls.return_value = mock_clarification_engine
    mock_clarification_result = MagicMock()
    mock_clarification_result.needs_clarification = False
    mock_clarification_engine.evaluate.return_value = (mock_clarification_result, {}, "general")
    mock_clarification_engine.overlay_profile.side_effect = lambda p, v: p
    mock_profile.return_value = MagicMock(id=7)
    mock_profile.return_value.soil = MagicMock()
    mock_profile.return_value.soil.model_dump.return_value = {"organic_carbon": 0.5}
    mock_profile.return_value.climate = MagicMock()
    mock_profile.return_value.climate.model_dump.return_value = {"rainfall": 600}
    mock_profile.return_value.land = MagicMock()
    mock_profile.return_value.land.model_dump.return_value = {"cropping_system": "monoculture"}
    mock_baseline.return_value.analyze_profile.return_value = MagicMock()
    mock_relationships.return_value.evaluate.return_value = MagicMock()
    mock_risks.return_value.evaluate.return_value = MagicMock()
    mock_interventions.return_value.evaluate.return_value = MagicMock()
    mock_recommendations.return_value.generate.return_value = MagicMock(recommendations=[])
    mock_context_builder.return_value = MagicMock()
    mock_generate.return_value = EnvironmentalResponse(
        response_type="environmental_assessment",
        assessment=Assessment(summary="Current profile remained usable.", status="informational"),
        confidence=Confidence(level="medium", reason=""),
        time_horizon={"value": "not_applicable", "reason": ""},
        metrics=[], drivers=[], recommendations=[], claims=[], variables_used=[], reasoning_trace=[]
    )

    with patch.object(memory_manager, "get_or_create_context", side_effect=RuntimeError("memory unavailable")):
        response = client.post("/api/v1/chat/", json={"profile_id": "7", "message": "What should I do?"})

    assert response.status_code == 200
    assert response.json()["assessment"]["summary"] == "Current profile remained usable."
    mock_profile.assert_called_once()
    mock_baseline.return_value.analyze_profile.assert_called_once()

def test_chat_clarification_orchestration():
    # If the user asks something without enough data, it should return a clarification response
    response = client.post("/api/v1/chat/", json={
        "profile_id": "1", # This will be fetched but let's assume it has no data
        "message": "Biodiversity is declining."
    })
    
    # We didn't mock get_profile here so it might fail with 404, let's mock it
    with patch("app.api.v1.chat.profile_service.get_profile") as mock_get_profile:
        mock_prof = MagicMock()
        mock_prof.id = 1
        mock_prof.soil = None
        mock_prof.climate = None
        mock_prof.land = None
        mock_prof.biodiversity = None
        mock_get_profile.return_value = mock_prof
        
        response = client.post("/api/v1/chat/", json={
            "profile_id": "1",
            "message": "Biodiversity is declining."
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "To assess the likely environmental drivers, please provide:" in data["assessment"]["summary"]
        # The referenced_metrics was removed from early response, we don't have to assert it unless we put it in metrics
        assert data["confidence"]["level"] == "undetermined"
