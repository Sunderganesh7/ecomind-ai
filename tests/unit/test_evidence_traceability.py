import pytest
from app.recommendations.engine.schemas import StructuredRecommendation
from app.schemas.response import EnvironmentalResponse, Claim, EvidenceReference, Assessment, Confidence
from app.llm.schemas import LLMContextData, ConversationContext
from app.llm.orchestrator import _validate_environmental_consistency

def test_claims_structure_generation():
    # Verify generator creates claims properly
    from app.recommendations.engine.generator import RecommendationEngine
    from app.reasoning.baseline.schemas import BaselineProfileResponse, AggregatedBaseline
    from app.reasoning.relationships.schemas import RelationshipProfileResponse
    from app.reasoning.risk.schemas import RiskProfileResponse, CompositeRiskPattern, Driver, Uncertainty as RiskUncertainty
    from app.recommendations.interventions.schemas import InterventionProfileResponse, CandidateIntervention, EvidenceRecord, Uncertainty
    
    b = BaselineProfileResponse(profile_id=1, metrics={}, warnings=[], summary=AggregatedBaseline(soil_status=None, water_status=None, habitat_status=None))
    rel = RelationshipProfileResponse(profile_id=1, relationships=[], variables_used=[], reasoning_trace=[])
    
    risk = RiskProfileResponse(
        profile_id=1, 
        risk_patterns=[
            CompositeRiskPattern(
                risk_pattern_id="test_risk",
                name="Test Risk",
                status="potential",
                variables_used=["organic_carbon"],
                primary_drivers=[Driver(variable="organic_carbon", status="low", type="observed", role="primary_driver")],
                supporting_signals=[],
                relationships_used=[],
                secondary_consequences=[],
                evidence_status="supported",
                evidence=[],
                uncertainty=RiskUncertainty(level="low", reasons=[]),
                reasoning_trace=[]
            )
        ]
    )
    
    cand = CandidateIntervention(
        intervention_id="test_intervention",
        name="Test",
        matched_conditions=["test_risk"],
        mechanisms=["mech_1"],
        potentially_affected_metrics=["organic_carbon"],
        evidence_status="supported",
        evidence=[
            EvidenceRecord(
                chunk_id="chunk_001",
                document_id="doc_001",
                source_id="fao_001",
                source="FAO",
                document="Test Document",
                page_number=12,
                relevance=0.9
            )
        ],
        constraints=[],
        tradeoffs=[],
        time_horizon="short_term",
        uncertainty=Uncertainty(level="low", reasons=[])
    )
    
    inv = InterventionProfileResponse(
        profile_id=1,
        risk_patterns_used=["test_risk"],
        intervention_candidates=[cand]
    )
    
    engine = RecommendationEngine()
    resp = engine.generate(b, rel, risk, inv)
    rec = resp.recommendations[0]
    
    assert len(rec.claims) == 2 # One deterministic, one scientific
    sci_claim = next((c for c in rec.claims if c.origin == "scientific_evidence"), None)
    assert sci_claim is not None
    assert sci_claim.claim_type == "environmental_mechanism"
    assert len(sci_claim.evidence) == 1
    
    ev = sci_claim.evidence[0]
    assert ev.chunk_id == "chunk_001"
    assert ev.document_id == "doc_001"
    assert ev.source_id == "fao_001"

def test_traceability_orchestrator_validation():
    # Ensure orchestrator rejects hallucinated claims
    ctx = LLMContextData(
        user_query="Test",
        conversation_context=ConversationContext(conversation_id="test"),
        claims=[
            {
                "claim_id": "c1",
                "claim_text": "Mechanism is X",
                "claim_type": "environmental_mechanism",
                "origin": "scientific_evidence",
                "support_status": "supported",
                "evidence": [
                    {
                        "chunk_id": "chunk_001",
                        "document_id": "doc_001",
                        "source_id": "fao_001",
                        "source": "FAO",
                        "document": "Test Doc",
                        "relevance": 0.9
                    }
                ]
            }
        ],
        evidence=[{"chunk_id": "chunk_001", "source_id": "fao_001"}], # Simulating available evidence in context
        baseline={"organic_carbon": {"value": 0.5}},
        deterministic_trace={"variables_used": ["organic_carbon"]}
    )
    
    valid_resp = EnvironmentalResponse(
        response_type="environmental_assessment",
        assessment=Assessment(summary="Test", status="informational"),
        confidence=Confidence(level="high", reason=""),
        time_horizon={"value": "not_applicable", "reason": ""},
        claims=[
            Claim(
                claim_id="c1",
                claim_text="Mechanism is X",
                claim_type="environmental_mechanism",
                origin="scientific_evidence",
                support_status="supported",
                evidence=[
                    EvidenceReference(
                        chunk_id="chunk_001",
                        document_id="doc_001",
                        source_id="fao_001",
                        source="FAO",
                        document="Test Doc",
                        relevance=0.9
                    )
                ]
            )
        ],
        variables_used=["organic_carbon"],
        drivers=[],
        recommendations=[],
        metrics=[],
        reasoning_trace=[]
    )
    
    # Passes validation
    _validate_environmental_consistency(valid_resp, ctx)
    
    # 1. Reject fabricated claim ID
    invalid_claim_id = valid_resp.model_copy(deep=True)
    invalid_claim_id.claims[0].claim_id = "c2_fabricated"
    with pytest.raises(ValueError, match="fabricated claim id"):
        _validate_environmental_consistency(invalid_claim_id, ctx)
        
    # 2. Reject scientific claim without evidence
    invalid_no_evidence = valid_resp.model_copy(deep=True)
    invalid_no_evidence.claims[0].evidence = []
    with pytest.raises(ValueError, match="must contain evidence"):
        _validate_environmental_consistency(invalid_no_evidence, ctx)
        
    # 3. Reject fabricated chunk within claim
    invalid_chunk = valid_resp.model_copy(deep=True)
    invalid_chunk.claims[0].evidence[0].chunk_id = "fabricated_chunk"
    with pytest.raises(ValueError, match="fabricated evidence chunk"):
        _validate_environmental_consistency(invalid_chunk, ctx)
