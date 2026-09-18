import pytest
from app.recommendations.engine.schemas import StructuredRecommendation, ImpactedMetrics, Confidence, ReasoningStep
from app.reasoning.baseline.schemas import BaselineProfileResponse, MetricAssessment
from app.reasoning.relationships.schemas import RelationshipProfileResponse
from app.reasoning.risk.schemas import RiskProfileResponse, CompositeRiskPattern
from app.recommendations.interventions.schemas import InterventionProfileResponse, CandidateIntervention, EvidenceRecord, Uncertainty
from app.recommendations.guard.validator import RecommendationQualityGuard

@pytest.fixture
def base_context():
    # Setup some dummy contexts that the guard uses to validate against
    baseline = BaselineProfileResponse(
        profile_id=1,
        metrics={
            "organic_carbon": MetricAssessment(metric="organic_carbon", observed_value=0.3, status="low", risk="high"),
            "moisture": MetricAssessment(metric="moisture", observed_value=15, status="constrained", risk="medium"),
            "cropping_system": MetricAssessment(metric="cropping_system", observed_value="monoculture", status="pressure", risk="high")
        },
        summary={"soil_status": {"status": "poor", "supporting_metrics": ["organic_carbon"]}}
    )
    relationships = RelationshipProfileResponse(profile_id=1, relationships=[], variables_used=[], reasoning_trace=[])
    risks = RiskProfileResponse(profile_id=1, risk_patterns=[])
    interventions = InterventionProfileResponse(
        profile_id=1, 
        risk_patterns_used=[],
        intervention_candidates=[
            CandidateIntervention(
                intervention_id="test_intervention",
                name="Test Intervention",
                matched_conditions=["low_organic_carbon"],
                mechanisms=["test_mech"],
                potentially_affected_metrics=["organic_carbon", "moisture"],
                evidence_status="supported",
                evidence=[EvidenceRecord(chunk_id="c1", document_id="d1", source_id="s1", source="s1", document="t1", relevance=0.9)],
                time_horizon="medium_term",
                uncertainty=Uncertainty(level="low", reasons=[])
            )
        ]
    )
    return baseline, relationships, risks, interventions

@pytest.fixture
def valid_rec():
    return StructuredRecommendation(
        recommendation_id="rec_test_intervention",
        what_to_do="Do test intervention.",
        why_it_works="Because of science.",
        environmental_mechanism="Mechanism X.",
        impacted_metrics=ImpactedMetrics(direct=["organic_carbon"], indirect=[], context_dependent=[]),
        time_horizon="medium_term",
        confidence=Confidence(level="high", reason="Test"),
        evidence_status="supported",
        evidence_claims=["c1"],
        claims=[
            {
                "claim_id": "c1",
                "claim_text": "text",
                "claim_type": "environmental_mechanism",
                "origin": "scientific_evidence",
                "support_status": "supported",
                "reasoning_reference": None,
                "evidence": [{"chunk_id": "c1", "document_id": "d1", "source_id": "s1", "source": "s1", "document": "t1", "relevance": 0.9}]
            }
        ],
        evidence=[],  # Backward compatibility
        risk_patterns_used=[],
        relationships_used=[],
        variables_used=["organic_carbon", "moisture", "cropping_system"],
        applicability="applicable",
        reasoning_trace=[ReasoningStep(step=1, type="intervention", intervention_id="test_intervention")]
    )

def test_evidence_validation(base_context, valid_rec):
    b, rel, r, i = base_context
    guard = RecommendationQualityGuard()
    
    # 1. Valid evidence -> PASS
    res = guard.validate(valid_rec, b, rel, r, i)
    assert res.checks["evidence"].status == "passed"
    
    # 2. Empty evidence -> FLAG
    rec_no_ev = valid_rec.model_copy(deep=True)
    rec_no_ev.claims[0]["evidence"] = []
    res2 = guard.validate(rec_no_ev, b, rel, r, i)
    assert res2.checks["evidence"].status == "flagged"
    assert res2.status == "flagged"
    
    # 3. Missing provenance -> FLAG
    rec_bad_ev = valid_rec.model_copy(deep=True)
    rec_bad_ev.claims[0]["evidence"][0]["chunk_id"] = "" # invalidate provenance
    res3 = guard.validate(rec_bad_ev, b, rel, r, i)
    assert res3.checks["evidence"].status == "flagged"

def test_context_validation(base_context, valid_rec):
    b, rel, r, i = base_context
    guard = RecommendationQualityGuard()
    
    # 1. Recommendation matches profile -> PASS
    res = guard.validate(valid_rec, b, rel, r, i)
    assert res.checks["environmental_context"].status == "passed"
    
    # 2. Unsupported environmental condition -> REGENERATE
    rec_bad_ctx = valid_rec.model_copy(deep=True)
    rec_bad_ctx.variables_used = ["fake_metric"]
    res2 = guard.validate(rec_bad_ctx, b, rel, r, i)
    assert res2.checks["environmental_context"].status == "regenerate"

def test_multi_variable_validation(base_context, valid_rec):
    b, rel, r, i = base_context
    guard = RecommendationQualityGuard()
    
    # 1. 3+ variables available and used -> PASS
    res = guard.validate(valid_rec, b, rel, r, i)
    assert res.checks["multi_metric_reasoning"].status == "passed"
    
    # 2. Only 1 used when 3 available -> REGENERATE
    rec_1var = valid_rec.model_copy(deep=True)
    rec_1var.variables_used = ["organic_carbon"]
    res2 = guard.validate(rec_1var, b, rel, r, i)
    assert res2.checks["multi_metric_reasoning"].status == "regenerate"
    
    # 3. Insufficient profile data -> PASS (limited)
    b.metrics = {"organic_carbon": MetricAssessment(metric="organic_carbon", observed_value=0.3, status="low", risk="high")}
    # Now only 1 var available
    rec_1var.variables_used = ["organic_carbon"]
    res3 = guard.validate(rec_1var, b, rel, r, i)
    assert res3.checks["multi_metric_reasoning"].status == "passed"
    assert res3.checks["multi_metric_reasoning"].reason == "limited_by_available_data"

def test_metrics_validation(base_context, valid_rec):
    b, rel, r, i = base_context
    guard = RecommendationQualityGuard()
    
    # 1. Valid impacted metrics -> PASS
    res = guard.validate(valid_rec, b, rel, r, i)
    assert res.checks["impacted_metrics"].status == "passed"
    
    # 2. Unsupported metric -> REGENERATE
    rec_bad_metric = valid_rec.model_copy(deep=True)
    rec_bad_metric.impacted_metrics.direct = ["fake_metric"]
    res2 = guard.validate(rec_bad_metric, b, rel, r, i)
    assert res2.checks["impacted_metrics"].status == "regenerate"
    
    # 3. Missing metrics -> REGENERATE
    rec_no_metric = valid_rec.model_copy(deep=True)
    rec_no_metric.impacted_metrics = ImpactedMetrics()
    res3 = guard.validate(rec_no_metric, b, rel, r, i)
    assert res3.checks["impacted_metrics"].status == "regenerate"

def test_time_horizon_validation(base_context, valid_rec):
    b, rel, r, i = base_context
    guard = RecommendationQualityGuard()
    
    res = guard.validate(valid_rec, b, rel, r, i)
    assert res.checks["time_horizon"].status == "passed"
    
    rec_bad_time = valid_rec.model_copy(deep=True)
    rec_bad_time.time_horizon = "3 months"
    res2 = guard.validate(rec_bad_time, b, rel, r, i)
    assert res2.checks["time_horizon"].status == "regenerate"

def test_intervention_consistency(base_context, valid_rec):
    b, rel, r, i = base_context
    guard = RecommendationQualityGuard()
    
    res = guard.validate(valid_rec, b, rel, r, i)
    assert res.checks["reasoning_consistency"].status == "passed"
    
    rec_unknown = valid_rec.model_copy(deep=True)
    rec_unknown.recommendation_id = "rec_unknown_intervention"
    res2 = guard.validate(rec_unknown, b, rel, r, i)
    assert res2.checks["reasoning_consistency"].status == "flagged"

def test_unsupported_claims(base_context, valid_rec):
    b, rel, r, i = base_context
    guard = RecommendationQualityGuard()
    
    # Valid -> PASS
    res = guard.validate(valid_rec, b, rel, r, i)
    assert res.checks["unsupported_claims"].status == "passed"
    
    # Percentage -> REGENERATE
    rec_pct = valid_rec.model_copy(deep=True)
    rec_pct.what_to_do = "This will increase organic carbon by 30%."
    res2 = guard.validate(rec_pct, b, rel, r, i)
    assert res2.checks["unsupported_claims"].status == "regenerate"
    
    # Guarantee -> REGENERATE
    rec_guar = valid_rec.model_copy(deep=True)
    rec_guar.what_to_do = "100% guaranteed to work."
    res3 = guard.validate(rec_guar, b, rel, r, i)
    assert res3.checks["unsupported_claims"].status == "regenerate"

def test_regeneration_loop(base_context, valid_rec):
    b, rel, r, i = base_context
    guard = RecommendationQualityGuard()
    
    # Force a REGENERATE state
    rec_bad = valid_rec.model_copy(deep=True)
    rec_bad.variables_used = ["organic_carbon"] # 1 variable used when 3 available
    
    # First attempt -> REGENERATE
    res1 = guard.validate(rec_bad, b, rel, r, i, attempts=1, max_attempts=2)
    assert res1.action == "regenerate"
    assert res1.status == "regenerate"
    
    # Second attempt fails again -> Safe fallback (FLAGGED)
    res2 = guard.validate(rec_bad, b, rel, r, i, attempts=2, max_attempts=2)
    assert res2.action == "safe_fallback"
    assert res2.status == "flagged"

def test_confidence_validation(base_context, valid_rec):
    b, rel, r, i = base_context
    guard = RecommendationQualityGuard()
    
    # 1. Valid -> PASS
    res = guard.validate(valid_rec, b, rel, r, i)
    assert res.checks["confidence"].status == "passed"
    
    # 2. Arbitrary percentage -> REGENERATE
    rec_pct = valid_rec.model_copy(deep=True)
    rec_pct.confidence.level = "94%"
    res2 = guard.validate(rec_pct, b, rel, r, i)
    assert res2.checks["confidence"].status == "regenerate"
    
    # 3. Insufficient evidence + high confidence -> REGENERATE
    rec_contradiction = valid_rec.model_copy(deep=True)
    rec_contradiction.evidence_status = "insufficient_evidence"
    rec_contradiction.confidence.level = "high"
    res3 = guard.validate(rec_contradiction, b, rel, r, i)
    assert res3.checks["confidence"].status == "regenerate"

def test_constraints_tradeoffs_validation(base_context, valid_rec):
    b, rel, r, i = base_context
    guard = RecommendationQualityGuard()
    
    # Valid (empty lists in both) -> PASS
    res = guard.validate(valid_rec, b, rel, r, i)
    assert res.checks["constraints"].status == "passed"
    assert res.checks["tradeoffs"].status == "passed"
    
    # Unsupported constraint -> REGENERATE
    rec_unsupp_c = valid_rec.model_copy(deep=True)
    rec_unsupp_c.constraints = ["fake_constraint"]
    res2 = guard.validate(rec_unsupp_c, b, rel, r, i)
    assert res2.checks["constraints"].status == "regenerate"

def test_what_to_do_validation(base_context, valid_rec):
    b, rel, r, i = base_context
    guard = RecommendationQualityGuard()
    
    res = guard.validate(valid_rec, b, rel, r, i)
    assert res.checks["what_to_do"].status == "passed"
    
    rec_generic = valid_rec.model_copy(deep=True)
    rec_generic.what_to_do = "Improve biodiversity."
    res2 = guard.validate(rec_generic, b, rel, r, i)
    assert res2.checks["what_to_do"].status == "regenerate"

def test_mechanism_validation(base_context, valid_rec):
    b, rel, r, i = base_context
    guard = RecommendationQualityGuard()
    
    res = guard.validate(valid_rec, b, rel, r, i)
    assert res.checks["mechanism"].status == "passed"
    
    rec_bad_mech = valid_rec.model_copy(deep=True)
    rec_bad_mech.environmental_mechanism = "unrelated ocean restoration"
    res2 = guard.validate(rec_bad_mech, b, rel, r, i)
    assert res2.checks["mechanism"].status == "regenerate"
