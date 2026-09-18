import pytest
from app.reasoning.baseline.analyzer import BaselineAnalyzer
from app.reasoning.relationships.evaluator import RelationshipEvaluator
from app.reasoning.risk.evaluator import RiskEvaluator
from app.recommendations.interventions.evaluator import InterventionEvaluator
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

@pytest.fixture(autouse=True)
def mock_search_service():
    with patch("app.recommendations.interventions.evaluator.KnowledgeSearchService") as mock:
        instance = mock.return_value
        instance.search.return_value = [
            {"chunk_id": "test_chunk", "document_id": "test_doc", "source_id": "test_src", "source": "test_src", "title": "Test Source", "page_number": 1, "relevance": 0.9}
        ]
        yield mock

def test_condition_matching(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator):
    """TEST 1 — Condition matching"""
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3, "moisture": 18},
        land={"cropping_system": "monoculture"},
        biodiversity={"species_richness": 10}
    )
    b = analyzer.analyze_profile(p)
    r = rel_evaluator.evaluate(b)
    risk = risk_evaluator.evaluate(b, r)
    inv = intervention_evaluator.evaluate(risk)
    
    cand = next((c for c in inv.intervention_candidates if c.intervention_id == "legume_intercropping"), None)
    assert cand is not None
    assert len(cand.matched_conditions) >= 2

def test_mechanism_mapping(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator):
    """TEST 2 — Mechanism mapping"""
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3, "moisture": 18},
        land={"cropping_system": "monoculture"}
    )
    b = analyzer.analyze_profile(p)
    r = rel_evaluator.evaluate(b)
    risk = risk_evaluator.evaluate(b, r)
    inv = intervention_evaluator.evaluate(risk)
    
    cand = next((c for c in inv.intervention_candidates if c.intervention_id == "legume_intercropping"), None)
    assert cand is not None
    assert "nutrient_cycling" in cand.mechanisms
    assert "crop_diversification" in cand.mechanisms

def test_metric_mapping(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator):
    """TEST 3 — Metric mapping"""
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3, "moisture": 18},
        land={"cropping_system": "monoculture"}
    )
    b = analyzer.analyze_profile(p)
    r = rel_evaluator.evaluate(b)
    risk = risk_evaluator.evaluate(b, r)
    inv = intervention_evaluator.evaluate(risk)
    
    cand = next((c for c in inv.intervention_candidates if c.intervention_id == "legume_intercropping"), None)
    assert cand is not None
    assert "organic_carbon" in cand.potentially_affected_metrics
    assert "habitat_diversity" in cand.potentially_affected_metrics

def test_evidence_mapping(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator):
    """TEST 4 — Evidence mapping"""
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3, "moisture": 18},
        land={"cropping_system": "monoculture"}
    )
    b = analyzer.analyze_profile(p)
    r = rel_evaluator.evaluate(b)
    risk = risk_evaluator.evaluate(b, r)
    inv = intervention_evaluator.evaluate(risk)
    
    cand = next((c for c in inv.intervention_candidates if c.intervention_id == "legume_intercropping"), None)
    assert cand.evidence_status == "supported"
    assert len(cand.evidence) > 0

def test_provenance(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator):
    """TEST 5 — Provenance"""
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3, "moisture": 18},
        land={"cropping_system": "monoculture"}
    )
    b = analyzer.analyze_profile(p)
    r = rel_evaluator.evaluate(b)
    risk = risk_evaluator.evaluate(b, r)
    inv = intervention_evaluator.evaluate(risk)
    
    cand = next((c for c in inv.intervention_candidates if c.intervention_id == "legume_intercropping"), None)
    e = cand.evidence[0]
    assert e.source == "test_src"
    assert e.chunk_id == "test_chunk"
    assert e.document == "Test Source"
    assert e.page_number == 1

def test_multi_condition_matching(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator):
    """TEST 6 — Multi-condition matching"""
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3, "moisture": 18},
        land={"cropping_system": "monoculture"}
    )
    b = analyzer.analyze_profile(p)
    r = rel_evaluator.evaluate(b)
    risk = risk_evaluator.evaluate(b, r)
    inv = intervention_evaluator.evaluate(risk)
    
    cand = next((c for c in inv.intervention_candidates if c.intervention_id == "legume_intercropping"), None)
    assert cand is not None
    # Ensure it matched multiple active conditions
    assert len(cand.matched_conditions) >= 2

def test_missing_context(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator):
    """TEST 7 — Missing context"""
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3} # Only one variable, insufficient for the risk pattern
    )
    b = analyzer.analyze_profile(p)
    r = rel_evaluator.evaluate(b)
    risk = risk_evaluator.evaluate(b, r)
    inv = intervention_evaluator.evaluate(risk)
    
    # In this case, risk evaluator will yield insufficient_data and no potential risks
    # The intervention evaluator won't generate any candidates because there are no active conditions
    assert len(inv.intervention_candidates) == 0

@patch("app.recommendations.interventions.evaluator.KnowledgeSearchService")
def test_unsupported_intervention(mock_search_class, analyzer, rel_evaluator, risk_evaluator):
    """TEST 8 — Unsupported intervention"""
    mock_instance = mock_search_class.return_value
    mock_instance.search.return_value = [] # No evidence found
    
    inv_evaluator = InterventionEvaluator()
    
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3, "moisture": 18},
        land={"cropping_system": "monoculture"}
    )
    b = analyzer.analyze_profile(p)
    r = rel_evaluator.evaluate(b)
    risk = risk_evaluator.evaluate(b, r)
    inv = inv_evaluator.evaluate(risk)
    
    cand = next((c for c in inv.intervention_candidates if c.intervention_id == "legume_intercropping"), None)
    assert cand is not None
    assert cand.evidence_status == "insufficient_evidence"

def test_no_arbitrary_score(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator):
    """TEST 9 — No arbitrary score"""
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3, "moisture": 18},
        land={"cropping_system": "monoculture"}
    )
    b = analyzer.analyze_profile(p)
    r = rel_evaluator.evaluate(b)
    risk = risk_evaluator.evaluate(b, r)
    inv = intervention_evaluator.evaluate(risk)
    
    for cand in inv.intervention_candidates:
        assert not hasattr(cand, "score")
        assert not hasattr(cand, "suitability")

def test_determinism(analyzer, rel_evaluator, risk_evaluator, intervention_evaluator):
    """TEST 10 — Determinism"""
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3, "moisture": 18},
        land={"cropping_system": "monoculture"}
    )
    
    b1 = analyzer.analyze_profile(p)
    r1 = rel_evaluator.evaluate(b1)
    risk1 = risk_evaluator.evaluate(b1, r1)
    inv1 = intervention_evaluator.evaluate(risk1)
    
    b2 = analyzer.analyze_profile(p)
    r2 = rel_evaluator.evaluate(b2)
    risk2 = risk_evaluator.evaluate(b2, r2)
    inv2 = intervention_evaluator.evaluate(risk2)
    
    assert inv1.model_dump() == inv2.model_dump()
