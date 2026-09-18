import pytest
from app.reasoning.baseline.analyzer import BaselineAnalyzer
from app.reasoning.relationships.evaluator import RelationshipEvaluator
from app.reasoning.risk.evaluator import RiskEvaluator
from app.recommendations.interventions.evaluator import InterventionEvaluator
from app.recommendations.engine.generator import RecommendationEngine
from app.schemas.environmental import EnvironmentalObservation
from unittest.mock import patch, MagicMock

@pytest.fixture
def analyzer():
    return BaselineAnalyzer()

@pytest.fixture
def rel_evaluator():
    return RelationshipEvaluator()

@pytest.fixture
def risk_evaluator():
    return RiskEvaluator()

@pytest.fixture
def intervention_evaluator():
    return InterventionEvaluator()
    
@pytest.fixture
def recommendation_engine():
    return RecommendationEngine()

@pytest.fixture(autouse=True)
def mock_search_service():
    with patch("app.recommendations.interventions.evaluator.KnowledgeSearchService") as mock:
        instance = mock.return_value
        instance.search.return_value = [
            {"chunk_id": "test_chunk", "source_id": "test_src", "title": "Test Source", "page_number": 1, "relevance": 0.9}
        ]
        yield mock

def _generate_full_chain(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator, engine, profile):
    b = analyzer.analyze_profile(profile)
    r = rel_evaluator.evaluate(b)
    risk = risk_evaluator.evaluate(b, r)
    inv = intervention_evaluator.evaluate(risk)
    return engine.generate(b, r, risk, inv)

def test_basic_recommendation_and_mandatory_fields(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator, recommendation_engine):
    """TEST 1 & 2 — Basic recommendation and mandatory fields"""
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3, "moisture": 18},
        land={"cropping_system": "monoculture"},
        biodiversity={"species_richness": 10}
    )
    res = _generate_full_chain(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator, recommendation_engine, p)
    
    assert res.recommendation_status == "success"
    assert len(res.recommendations) > 0
    rec = res.recommendations[0]
    
    assert rec.what_to_do is not None
    assert rec.why_it_works is not None
    assert rec.environmental_mechanism is not None
    assert rec.impacted_metrics is not None
    assert rec.time_horizon is not None
    assert rec.confidence is not None
    assert rec.evidence_status is not None

def test_multi_metric_reasoning(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator, recommendation_engine):
    """TEST 3 — Multi-metric reasoning"""
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3, "moisture": 18},
        land={"cropping_system": "monoculture"}
    )
    res = _generate_full_chain(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator, recommendation_engine, p)
    
    rec = res.recommendations[0]
    # Verify at least 3 variables are used when sufficient data exists
    assert len(rec.variables_used) >= 3

def test_missing_data(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator, recommendation_engine):
    """TEST 4 — Missing data handling"""
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3} # Not enough data
    )
    res = _generate_full_chain(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator, recommendation_engine, p)
    
    assert res.recommendation_status == "no_supported_intervention"
    assert len(res.recommendations) == 0

@patch("app.recommendations.interventions.evaluator.KnowledgeSearchService")
def test_insufficient_evidence(mock_search_class, analyzer, rel_evaluator, risk_evaluator, intervention_evaluator, recommendation_engine):
    """TEST 5 — Evidence testing (insufficient evidence)"""
    mock_instance = mock_search_class.return_value
    mock_instance.search.return_value = [] # No evidence found
    
    inv_evaluator = InterventionEvaluator()
    
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3, "moisture": 18},
        land={"cropping_system": "monoculture"}
    )
    res = _generate_full_chain(analyzer, rel_evaluator, risk_evaluator, inv_evaluator, recommendation_engine, p)
    
    rec = res.recommendations[0]
    assert rec.evidence_status == "insufficient_evidence"
    assert rec.confidence.level == "low"

def test_applicability_context(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator, recommendation_engine):
    """TEST 6 — Applicability and context check"""
    # 2 variables available, applicability should be "context_dependent"
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3, "moisture": 18} # only 2 valid variables, no cropping_system
    )
    # 2 variables might not trigger intervention for legume_intercropping since it needs monoculture, 
    # but soil_vegetation_pressure might trigger cover_crops
    res = _generate_full_chain(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator, recommendation_engine, p)
    if res.recommendations:
        rec = res.recommendations[0]
        assert rec.applicability == "context_dependent"
        assert len(rec.missing_context) > 0

def test_determinism(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator, recommendation_engine):
    """TEST 7 — Determinism"""
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3, "moisture": 18},
        land={"cropping_system": "monoculture"}
    )
    
    r1 = _generate_full_chain(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator, recommendation_engine, p)
    r2 = _generate_full_chain(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator, recommendation_engine, p)
    
    assert r1.model_dump() == r2.model_dump()

def test_no_arbitrary_score(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator, recommendation_engine):
    """Verify no hallucinated scores in confidence"""
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3, "moisture": 18},
        land={"cropping_system": "monoculture"}
    )
    res = _generate_full_chain(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator, recommendation_engine, p)
    rec = res.recommendations[0]
    
    # Must use restricted vocabulary
    assert rec.confidence.level in ["high", "medium", "low", "undetermined"]
