from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.environmental import EnvironmentalObservationCreate, EnvironmentalObservation
from app.services import profile_service

router = APIRouter()

@router.post("", response_model=EnvironmentalObservation, status_code=status.HTTP_201_CREATED, summary="Create a new environmental profile")
def create_profile(profile_data: EnvironmentalObservationCreate, db: Session = Depends(get_db)):
    """
    Creates a new environmental profile using the provided structured observations.
    """
    return profile_service.create_profile(db, profile_data)

@router.get("/{id}", response_model=EnvironmentalObservation, summary="Retrieve an environmental profile")
def get_profile(id: int, db: Session = Depends(get_db)):
    """
    Retrieves an environmental profile by its ID.
    """
    db_obs = profile_service.get_profile(db, id)
    if not db_obs:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_obs

@router.put("/{id}", response_model=EnvironmentalObservation, summary="Update an existing environmental profile")
def update_profile(id: int, profile_data: EnvironmentalObservationCreate, db: Session = Depends(get_db)):
    """
    Updates an environmental profile by its ID.
    Returns 404 if the profile does not exist.
    """
    db_obs = profile_service.update_profile(db, id, profile_data)
    if not db_obs:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_obs

from app.reasoning.baseline.analyzer import BaselineAnalyzer
from app.reasoning.baseline.schemas import BaselineProfileResponse

@router.post('/{profile_id}/baseline', response_model=BaselineProfileResponse)
def analyze_profile_baseline(profile_id: int, db: Session = Depends(get_db)):
    profile = profile_service.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail='Profile not found')
        
    analyzer = BaselineAnalyzer()
    try:
        return analyzer.analyze_profile(profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error analyzing baseline: {str(e)}')
from app.reasoning.relationships.schemas import RelationshipProfileResponse
from app.reasoning.relationships.evaluator import RelationshipEvaluator

@router.post('/{profile_id}/relationships', response_model=RelationshipProfileResponse)
def analyze_profile_relationships(profile_id: int, db: Session = Depends(get_db)):
    profile = profile_service.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail='Profile not found')
        
    baseline_analyzer = BaselineAnalyzer()
    try:
        baseline_res = baseline_analyzer.analyze_profile(profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error analyzing baseline: {str(e)}')
        
    evaluator = RelationshipEvaluator()
    try:
        return evaluator.evaluate(baseline_res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error evaluating relationships: {str(e)}')
from app.reasoning.risk.schemas import RiskProfileResponse
from app.reasoning.risk.evaluator import RiskEvaluator

@router.post('/{profile_id}/risks', response_model=RiskProfileResponse)
def analyze_profile_risks(profile_id: int, db: Session = Depends(get_db)):
    profile = profile_service.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail='Profile not found')
        
    baseline_analyzer = BaselineAnalyzer()
    try:
        baseline_res = baseline_analyzer.analyze_profile(profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error analyzing baseline: {str(e)}')
        
    rel_evaluator = RelationshipEvaluator()
    try:
        rel_res = rel_evaluator.evaluate(baseline_res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error evaluating relationships: {str(e)}')
        
    risk_evaluator = RiskEvaluator()
    try:
        return risk_evaluator.evaluate(baseline_res, rel_res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error evaluating risks: {str(e)}')
        
from app.recommendations.interventions.schemas import InterventionProfileResponse
from app.recommendations.interventions.evaluator import InterventionEvaluator

@router.post('/{profile_id}/interventions/candidates', response_model=InterventionProfileResponse)
def get_intervention_candidates(profile_id: int, db: Session = Depends(get_db)):
    profile = profile_service.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail='Profile not found')
        
    baseline_analyzer = BaselineAnalyzer()
    try:
        baseline_res = baseline_analyzer.analyze_profile(profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error analyzing baseline: {str(e)}')
        
    rel_evaluator = RelationshipEvaluator()
    try:
        rel_res = rel_evaluator.evaluate(baseline_res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error evaluating relationships: {str(e)}')
        
    risk_evaluator = RiskEvaluator()
    try:
        risk_res = risk_evaluator.evaluate(baseline_res, rel_res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error evaluating risks: {str(e)}')
        
    intervention_evaluator = InterventionEvaluator()
    try:
        return intervention_evaluator.evaluate(risk_res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error evaluating interventions: {str(e)}')
from app.recommendations.engine.schemas import RecommendationProfileResponse
from app.recommendations.engine.generator import RecommendationEngine
from app.recommendations.guard.schemas import GuardedRecommendationProfileResponse, QualityGuardResult, CheckResult
from app.recommendations.guard.validator import RecommendationQualityGuard

@router.post('/{profile_id}/recommendations', response_model=GuardedRecommendationProfileResponse)
def generate_recommendations(profile_id: int, db: Session = Depends(get_db)):
    profile = profile_service.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail='Profile not found')
        
    baseline_analyzer = BaselineAnalyzer()
    try:
        baseline_res = baseline_analyzer.analyze_profile(profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error analyzing baseline: {str(e)}')
        
    rel_evaluator = RelationshipEvaluator()
    try:
        rel_res = rel_evaluator.evaluate(baseline_res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error evaluating relationships: {str(e)}')
        
    risk_evaluator = RiskEvaluator()
    try:
        risk_res = risk_evaluator.evaluate(baseline_res, rel_res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error evaluating risks: {str(e)}')
        
    intervention_evaluator = InterventionEvaluator()
    try:
        intervention_res = intervention_evaluator.evaluate(risk_res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error evaluating interventions: {str(e)}')
        
    engine = RecommendationEngine()
    guard = RecommendationQualityGuard()
    
    max_attempts = 2
    attempts = 1
    feedback = None
    
    while attempts <= max_attempts:
        try:
            rec_resp = engine.generate(baseline_res, rel_res, risk_res, intervention_res, validation_feedback=feedback)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'Error generating recommendations: {str(e)}')
            
        if not rec_resp.recommendations:
            # Nothing to guard
            return GuardedRecommendationProfileResponse(
                recommendation=None,
                quality_guard=QualityGuardResult(
                    status="passed",
                    action="display",
                    attempts=attempts,
                    max_attempts=max_attempts,
                    checks={},
                    reason="No recommendation generated to validate."
                ),
                recommendation_available=False
            )
            
        # We'll validate the primary recommendation (first one)
        primary_rec = rec_resp.recommendations[0]
        guard_result = guard.validate(primary_rec, baseline_res, rel_res, risk_res, intervention_res, attempts=attempts, max_attempts=max_attempts)
        
        if guard_result.action == "display":
            return GuardedRecommendationProfileResponse(
                recommendation=primary_rec,
                quality_guard=guard_result,
                recommendation_available=True
            )
        elif guard_result.action == "regenerate":
            feedback = guard_result.failed_checks
            attempts += 1
        elif guard_result.action == "safe_fallback":
            return GuardedRecommendationProfileResponse(
                recommendation=None,
                quality_guard=guard_result,
                recommendation_available=False
            )
            
    # If max attempts exceeded and still regenerate
    return GuardedRecommendationProfileResponse(
        recommendation=None,
        quality_guard=guard_result, # this will have status flagged by the validator due to attempts
        recommendation_available=False
    )
