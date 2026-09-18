from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import uuid

from app.memory.manager import memory_manager
from app.services import profile_service
from app.database.connection import get_db
from app.reasoning.baseline.analyzer import BaselineAnalyzer
from app.reasoning.relationships.evaluator import RelationshipEvaluator
from app.reasoning.risk.evaluator import RiskEvaluator
from app.recommendations.interventions.evaluator import InterventionEvaluator
from app.recommendations.engine.generator import RecommendationEngine
from app.recommendations.guard.validator import RecommendationQualityGuard
from app.clarification.engine import ClarificationEngine
from app.llm.context_builder import build_llm_context
from app.llm.orchestrator import generate_conversational_response
from app.llm.schemas import ConversationContext
from app.schemas.response import ChatResponse
from app.rag.search.search_service import KnowledgeSearchService

from app.context_engine.engine import ContextEngine

router = APIRouter()

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    profile_id: Optional[str] = None
    message: str

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    # Memory is convenience context, never a prerequisite for deterministic reasoning.
    memory_available = True
    try:
        context = memory_manager.get_or_create_context(db, request.conversation_id)
    except Exception as e:
        import logging
        logging.error(f"Memory error: {e}")
        memory_available = False
        context = ConversationContext(conversation_id=request.conversation_id or str(uuid.uuid4()))

    def create_early_chat_response(message: str, status: str = "informational", reason: str = "") -> ChatResponse:
        return ChatResponse(
            schema_version="1.0",
            conversation_id=context.conversation_id,
            response_type="clarification" if "clarification" in status else "environmental_assessment",
            assessment={"summary": message, "status": status},
            time_horizon={"value": "not_applicable", "reason": reason or "Early response."},
            confidence={"level": "undetermined", "reason": reason or "Insufficient data."},
            drivers=[],
            recommendations=[],
            metrics=[],
            claims=[],
            variables_used=[],
            reasoning_trace=[]
        )

    active_profile_id = request.profile_id or context.active_profile_id
    if not active_profile_id:
        answer = "To assess this environmental question, provide a profile ID or structured observations for soil organic carbon, moisture or rainfall, and land use."
        return create_early_chat_response(answer, status="missing_profile", reason="No environmental profile is associated with this conversation.")

    user_msg_id = None
    if memory_available:
        try:
            memory_manager.switch_profile(db, context.conversation_id, active_profile_id)
            context = memory_manager.get_or_create_context(db, context.conversation_id)
            user_msg = memory_manager.add_message(db, context.conversation_id, "user", request.message)
            user_msg_id = user_msg.id
        except Exception as e:
            import logging
            logging.error(f"Memory error: {e}")
            memory_available = False
            context = ConversationContext(conversation_id=context.conversation_id, active_profile_id=active_profile_id)
    else:
        context.active_profile_id = active_profile_id
    
    # 2. Services Initialization
    clarification_engine = ClarificationEngine()
    context_engine = ContextEngine()
    baseline_analyzer = BaselineAnalyzer()
    relationship_evaluator = RelationshipEvaluator()
    risk_evaluator = RiskEvaluator()
    search_service = KnowledgeSearchService()
    intervention_evaluator = InterventionEvaluator(search_service=search_service)
    rec_engine = RecommendationEngine()
    quality_guard = RecommendationQualityGuard()
    
    # 3. Load Upstream Data
    try:
        profile_data = profile_service.get_profile(db, int(active_profile_id))
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Profile not found: {str(e)}")
        
    # Clarification / Fact Extraction
    clarification_result, extracted_facts, topic = clarification_engine.evaluate(
        query=request.message,
        profile=profile_data,
        conversation_context=context
    )
    
    if extracted_facts or topic:
        if memory_available and user_msg_id:
            memory_manager.update_clarification(db, context.conversation_id, user_msg_id, extracted_facts, topic)
            context = memory_manager.get_or_create_context(db, context.conversation_id)
            
    if clarification_result.needs_clarification:
        if memory_available:
            memory_manager.add_message(db, context.conversation_id, "assistant", clarification_result.question)
        return create_early_chat_response(clarification_result.question, status="clarification_needed", reason=clarification_result.reason)
        
    if context.clarification_values:
        profile_data = clarification_engine.overlay_profile(profile_data, context.clarification_values)
        
    # Context-Aware Query Engine
    ctx_query = context_engine.resolve_query(request.message, context, profile_data)
    if ctx_query.clarification_required:
        if memory_available:
            memory_manager.add_message(db, context.conversation_id, "assistant", ctx_query.clarification_question)
        return create_early_chat_response(ctx_query.clarification_question, status="clarification_needed", reason="Context ambiguity detected.")
        
    # Fetch Context-Specific Evidence
    context_evidence = []
    if ctx_query.retrieval_query != request.message or ctx_query.query_intent != "general_information":
        try:
            results = search_service.search(ctx_query.retrieval_query, top_k=2)
            context_evidence = results
        except Exception as e:
            import logging
            logging.error(f"Contextual evidence search failed: {e}")

    # Reasoning Pipeline
    baseline = baseline_analyzer.analyze_profile(profile_data)
    
    # NEW: Question-Aware Context Filtering
    if ctx_query.referenced_topics and ctx_query.query_intent != "general_environment":
        topic_to_vars = {
            "soil": {"soil_ph", "organic_carbon", "moisture"},
            "climate": {"rainfall", "temperature"},
            "water": {"rainfall", "moisture"},
            "land_use": {"land_use"},
            "cropping_system": {"crop", "cropping_system"},
            "biodiversity": {"species_richness", "habitat_diversity"},
            "human_impact": {"pollution", "deforestation"},
            "pollution": {"pollution"},
            "deforestation": {"deforestation"}
        }
        
        relevant_vars = set()
        for t in ctx_query.referenced_topics:
            relevant_vars.update(topic_to_vars.get(t, set()))
            
        if relevant_vars:
            filtered_metrics = {k: v for k, v in baseline.metrics.items() if k in relevant_vars}
            if filtered_metrics:
                baseline.metrics = filtered_metrics

    relationships = relationship_evaluator.evaluate(baseline)
    risks = risk_evaluator.evaluate(baseline, relationships)
    interventions = intervention_evaluator.evaluate(risks)
    
    # Generate Recommendation (with internal Guard Loop)
    rec_response = rec_engine.generate(baseline, relationships, risks, interventions)
    structured_rec = None
    guard_result = None
    if rec_response.recommendations:
        structured_rec = rec_response.recommendations[0]
        guard_result = quality_guard.validate(
            structured_rec, baseline, relationships, risks, interventions
        )
        if guard_result.status == "regenerate":
            guard_result = quality_guard.validate(
                structured_rec, baseline, relationships, risks, interventions,
                attempts=guard_result.max_attempts,
                max_attempts=guard_result.max_attempts,
            )
        context.last_recommendation_id = structured_rec.recommendation_id
        
    # 4. Build LLM Context
    llm_context = build_llm_context(
        user_query=ctx_query.resolved_query,
        conversation_context=context,
        profile_data=profile_data,
        baseline=baseline,
        relationships=relationships,
        risks=risks,
        interventions=interventions,
        recommendation=structured_rec,
        guard_result=guard_result,
        extra_evidence=context_evidence,
        query_intent=ctx_query.query_intent
    )
    
    # 5. LLM Orchestration
    llm_response = await generate_conversational_response(llm_context)
    
    # 6. Save Assistant Message
    if memory_available:
        try:
            memory_manager.add_message(db, context.conversation_id, "assistant", llm_response.assessment.summary)
        except Exception:
            pass
    
    return ChatResponse(conversation_id=context.conversation_id, **llm_response.model_dump())

