import json
import logging
import re
from pydantic import ValidationError
from openai import AsyncOpenAI
import httpx

from app.core.config import settings
from app.llm.schemas import LLMContextData
from app.schemas.response import EnvironmentalResponse, Assessment, Confidence
from app.llm.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

async def generate_conversational_response(context_data: LLMContextData) -> EnvironmentalResponse:
    if context_data.quality_guard_status == "flagged":
        return _fallback_response(context_data, reason=context_data.quality_guard_reason or "Recommendation quality validation flagged this result.")

    if not settings.LLM_API_KEY:
        return _fallback_response(context_data, reason="Conversational explanation service is not configured.")
        
    client = AsyncOpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        timeout=httpx.Timeout(settings.LLM_TIMEOUT),
        max_retries=settings.LLM_MAX_RETRIES,
    )
    
    # Construct the User message from the context data
    context_json = context_data.model_dump_json(exclude={"conversation_context"})
    dt = context_data.deterministic_trace
    
    # Pre-construct the strict deterministic fields
    deterministic_payload = {
        "drivers": dt.get("drivers", []),
        "recommendations": dt.get("recommendations", []),
        "metrics": dt.get("metrics", []),
        "time_horizon": dt.get("time_horizon", {}),
        "claims": dt.get("claims", []),
        "variables_used": dt.get("variables_used", []),
        "reasoning_trace": dt.get("reasoning_trace", [])
    }
    
    # Instruct the LLM to output the entire schema, mixing its generation with the deterministic fields
    user_prompt = f"""
Here is the structured environmental context for this query:
{context_json}

The backend has already computed the deterministic environmental trace. You must output a JSON object exactly matching the `EnvironmentalResponse` schema.
You MUST include the following deterministic fields EXACTLY as provided below:
{json.dumps(deterministic_payload, indent=2)}

You only need to generate the `assessment` and `confidence` objects based on the context, and select an appropriate `response_type`.

User Query: {context_data.user_query}
"""
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Append recent conversation history
    for msg in context_data.conversation_context.messages:
        messages.append({"role": msg.role, "content": msg.content})
        
    messages.append({"role": "user", "content": user_prompt})
    
    # Attempt 1
    try:
        response_text = await _call_llm(client, messages)
        response_dict = json.loads(response_text)
        validated_response = EnvironmentalResponse(**response_dict)
        _validate_environmental_consistency(validated_response, context_data)
        return validated_response
    except (ValidationError, ValueError) as e:
        logger.warning(f"LLM output failed schema or consistency validation: {e}")
        return _fallback_response(context_data, reason="Validation failed on LLM output.")
    except Exception as e:
        logger.warning(f"LLM generation failed: {e}")
        return _fallback_response(context_data, reason="LLM service unavailable.")

async def _call_llm(client: AsyncOpenAI, messages: list) -> str:
    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=messages,
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS,
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content

def _validate_environmental_consistency(response: EnvironmentalResponse, context: LLMContextData) -> None:
    # Validate Variables Used
    allowed_vars = set(context.deterministic_trace.get("variables_used", []))
    for var in response.variables_used:
        if var not in allowed_vars:
            raise ValueError(f"Unknown or unsupported variable used: {var}")
            
    # Validate Claims
    allowed_claim_ids = {c.get("claim_id") for c in context.claims}
    for claim in response.claims:
        if claim.claim_id not in allowed_claim_ids:
            raise ValueError(f"Unknown or fabricated claim id: {claim.claim_id}")
        
        # Verify evidence within claims are valid (only for scientific claims)
        if claim.origin == "scientific_evidence" and not claim.evidence:
            if claim.support_status != "insufficient_evidence":
                raise ValueError(f"Scientific claim '{claim.claim_id}' must contain evidence or be marked 'insufficient_evidence'")
                
        # Validate that the chunk_ids inside the claim exist in the context evidence
        allowed_evidence_chunks = {item.get("chunk_id") for item in context.evidence}
        for ev in claim.evidence:
            if ev.chunk_id not in allowed_evidence_chunks:
                raise ValueError(f"Unknown or fabricated evidence chunk: {ev.chunk_id} in claim {claim.claim_id}")
            
    # Validate Interventions
    allowed_interventions = {item.get("intervention_id") for item in context.intervention_candidates}
    for rec in response.recommendations:
        if rec.intervention_id not in allowed_interventions:
            raise ValueError(f"Unknown intervention id: {rec.intervention_id}")
            
    # Validate Metrics
    allowed_metrics = set(context.baseline.keys())
    for m in response.metrics:
        if m.name not in allowed_metrics:
            raise ValueError(f"Unknown metric referenced: {m.name}")

def _fallback_response(context_data: LLMContextData, reason: str) -> EnvironmentalResponse:
    dt = context_data.deterministic_trace
    
    if context_data.quality_guard_status == "flagged":
        assessment_text = f"Action was flagged: {context_data.quality_guard_reason}"
        status = "flagged"
    else:
        assessment_text = "LLM explanation unavailable — deterministic environmental analysis shown. "
        parts = []
        
        if dt.get("variables_used"):
            parts.append(f"Focal variables: {', '.join(dt.get('variables_used'))}.")
            
        if dt.get("drivers"):
            # Deduplicate by variable name just for the summary text
            driver_names = list(dict.fromkeys(d.get("variable") for d in dt.get("drivers")))
            if driver_names:
                parts.append(f"Identified drivers: {', '.join(driver_names)}.")
                
        if dt.get("recommendations"):
            rec = dt.get("recommendations")[0]
            parts.append(f"Recommendation: {rec.get('what_to_do', '')}")
            if rec.get('environmental_mechanism'):
                parts.append(f"Mechanism: {rec.get('environmental_mechanism')}")
                
        if not parts:
            parts.append("Deterministic analysis completed.")
            
        assessment_text += " ".join(parts)
        status = "informational"
        
    assessment = Assessment(
        summary=assessment_text,
        status=status
    )
    
    # Mask "Validation failed" so frontend doesn't falsely show "ACTION FLAGGED BY QUALITY GUARD"
    safe_reason = reason.replace("Validation failed", "LLM output rejected")
    
    confidence = Confidence(
        level="undetermined",
        reason=f"Fallback response used due to: {safe_reason}"
    )
    
    return EnvironmentalResponse(
        response_type="environmental_assessment",
        assessment=assessment,
        drivers=dt.get("drivers", []),
        recommendations=dt.get("recommendations", []),
        metrics=dt.get("metrics", []),
        time_horizon=dt.get("time_horizon", {"value": "not_applicable", "reason": "Fallback"}),
        confidence=confidence,
        claims=dt.get("claims", []),
        variables_used=dt.get("variables_used", []),
        reasoning_trace=dt.get("reasoning_trace", [])
    )
