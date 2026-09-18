from typing import Dict, Any
from app.llm.schemas import LLMContextData, ConversationContext
from app.reasoning.baseline.schemas import BaselineProfileResponse
from app.reasoning.relationships.schemas import RelationshipProfileResponse
from app.reasoning.risk.schemas import RiskProfileResponse
from app.recommendations.interventions.schemas import InterventionProfileResponse
from app.recommendations.engine.schemas import StructuredRecommendation
from app.recommendations.guard.schemas import QualityGuardResult

def build_llm_context(
    user_query: str,
    conversation_context: ConversationContext,
    profile_data: Dict[str, Any],
    baseline: BaselineProfileResponse,
    relationships: RelationshipProfileResponse,
    risks: RiskProfileResponse,
    interventions: InterventionProfileResponse,
    recommendation: StructuredRecommendation = None,
    guard_result: QualityGuardResult = None,
    extra_evidence: list = None,
    query_intent: str = "general_environment"
) -> LLMContextData:
    
    # Only pass environmental observations and provenance needed for an
    # explanation.  ORM state, credentials, and arbitrary database metadata
    # must never become model context.
    profile_dict: Dict[str, Any] = {}
    if isinstance(profile_data, dict):
        allowed = {"id", "location", "soil", "climate", "land", "biodiversity", "human_impact", "observed_at", "source_name", "source_type", "data_quality", "confidence"}
        profile_dict = {key: value for key, value in profile_data.items() if key in allowed}
    elif hasattr(profile_data, "id"):
        profile_dict = {"id": profile_data.id}
        for section in ("location", "soil", "climate", "land", "biodiversity", "human_impact"):
            value = getattr(profile_data, section, None)
            if value is None:
                continue
            fields = ("latitude", "longitude", "region") if section == "location" else {
                "soil": ("soil_ph", "organic_carbon", "moisture"),
                "climate": ("rainfall", "temperature"),
                "land": ("land_use", "crop", "cropping_system"),
                "biodiversity": ("species_richness", "habitat_diversity"),
                "human_impact": ("pollution", "deforestation"),
            }[section]
            profile_dict[section] = {
                field: getattr(value, field)
                for field in fields
                if getattr(value, field, None) is not None
            }
    
    # Extract only essential baseline information (preserving values/units)
    baseline_context = {}
    if baseline and baseline.metrics:
        for metric, data in baseline.metrics.items():
            if data.status != "unknown":
                baseline_context[metric] = {
                "value": data.observed_value,
                "unit": data.unit,
                "status": data.status,
                "type": "observed",
                "uncertainty": data.risk,
                }
                
    # Extract relationships
    rel_context = {}
    if relationships and relationships.relationships:
        for r in relationships.relationships:
            rel_context[r.relationship_id] = {
                "variables": r.inputs,
                "input_states": {name: state.model_dump() for name, state in r.input_states.items()},
                "intermediate_states": [s.name for s in r.intermediate_states],
                "downstream_states": [s.name for s in r.downstream_states]
            }
            
    # Extract risks
    risk_context = {}
    if risks and risks.risk_patterns:
        for r in risks.risk_patterns:
            risk_context[r.risk_pattern_id] = {
                "primary_drivers": [d.model_dump() for d in r.primary_drivers],
                "secondary_consequences": [c.model_dump() for c in r.secondary_consequences],
                "relationships_used": r.relationships_used,
                "uncertainty": r.uncertainty.model_dump(),
            }
            
    # Extract evidence from recommendation
    evidence_context = []
    rec_ev_list = getattr(recommendation, 'evidence', None) if recommendation else None
    if not rec_ev_list and recommendation and getattr(recommendation, 'claims', None):
        rec_ev_list = []
        for cl in recommendation.claims:
            cl_ev = getattr(cl, 'evidence', None) or (cl.get('evidence') if isinstance(cl, dict) else None)
            if cl_ev:
                rec_ev_list.extend(cl_ev)

    if rec_ev_list:
        for ev in rec_ev_list:
            evidence_context.append({
                "source": getattr(ev, 'source', None) or (ev.get('source') if isinstance(ev, dict) else 'Unknown'),
                "source_id": getattr(ev, 'source', None) or (ev.get('source') if isinstance(ev, dict) else 'Unknown'),
                "chunk_id": getattr(ev, 'chunk_id', None) or (ev.get('chunk_id') if isinstance(ev, dict) else ''),
                "title": getattr(ev, 'title', None) or (ev.get('title') if isinstance(ev, dict) else ''),
                "page_number": getattr(ev, 'page_number', None) or (ev.get('page_number') if isinstance(ev, dict) else None),
                "section": getattr(ev, 'section', None) or (ev.get('section') if isinstance(ev, dict) else None),
                "relevance": getattr(ev, 'relevance', 0.0) if hasattr(ev, 'relevance') else (ev.get('relevance', 0.0) if isinstance(ev, dict) else 0.0)
            })
            
    if extra_evidence:
        for ev in extra_evidence:
            evidence_context.append({
                "source": ev.get("source_id", "Unknown"),
                "source_id": ev.get("source_id", "Unknown"),
                "chunk_id": ev.get("chunk_id", ""),
                "title": ev.get("title", ""),
                "page_number": ev.get("page_number"),
                "section": ev.get("section"),
                "relevance": ev.get("relevance", 0.0)
            })
            
    # Extract candidate interventions
    cands_context = []
    if interventions and interventions.intervention_candidates:
        for c in interventions.intervention_candidates:
            cands_context.append({
                "intervention_id": c.intervention_id,
                "name": c.name,
                "mechanisms": c.mechanisms,
                "matched_conditions": c.matched_conditions
            })
            
    rec_context = None
    if recommendation:
        rec_context = {
                "what_to_do": recommendation.what_to_do,
                "why_it_works": recommendation.why_it_works,
                "environmental_mechanism": recommendation.environmental_mechanism,
                "impacted_metrics": recommendation.impacted_metrics.model_dump(),
                "time_horizon": recommendation.time_horizon,
                "confidence": recommendation.confidence.model_dump(),
                "evidence_status": recommendation.evidence_status,
                "constraints": recommendation.constraints,
                "tradeoffs": [tradeoff.model_dump() for tradeoff in recommendation.tradeoffs],
                "recommendation_id": recommendation.recommendation_id,
                "claims": [c.model_dump() for c in recommendation.claims],
                "evidence_claims": recommendation.evidence_claims
        }
        
    # ---------------------------------------------------------
    # TASK 24 (INTENT FILTERING) - Determine focal variables
    # ---------------------------------------------------------
    focal_vars = {
        "biodiversity": ["species_richness", "habitat_diversity", "biodiversity_pressure"],
        "soil": ["soil_ph", "organic_carbon", "moisture", "soil_quality"],
        "climate": ["rainfall", "temperature", "moisture", "climate_stress"],
        "water": ["rainfall", "moisture", "water_stress"],
        "land_use": ["land_use", "habitat_quality"],
        "cropping_system": ["crop", "cropping_system", "soil_quality"],
        "pollution": ["pollution", "water_quality"],
        "deforestation": ["deforestation", "habitat_diversity"],
    }
    target_vars = focal_vars.get(query_intent, [])
    
    # ---------------------------------------------------------
    # TASK 19 DETERMINISTIC TRACE CONSTRUCTION
    # ---------------------------------------------------------
    dt_drivers = []
    dt_metrics = []
    dt_variables_used = set()
    dt_reasoning_trace = []
    
    step_counter = 1
    
    # 1. Baseline / Observed Variables
    if baseline and baseline.metrics:
        observed_vars = []
        for metric_name, m_data in baseline.metrics.items():
            if m_data.status != "unknown":
                observed_vars.append(metric_name)
                dt_variables_used.add(metric_name)
                # Determine role
                role = "direct" if getattr(m_data, "direct_measurement", True) else "indirect"
                dt_metrics.append({
                    "name": metric_name,
                    "current_value": m_data.observed_value,
                    "unit": m_data.unit,
                    "role": role,
                    "status": m_data.status
                })
                # If metric is a constraint or issue, it's a driver
                if "constraint" in m_data.status or "pressure" in m_data.status:
                    dt_drivers.append({
                        "variable": metric_name,
                        "value": m_data.observed_value,
                        "unit": m_data.unit,
                        "status": m_data.status,
                        "role": "primary_driver",
                        "source": "environmental_profile"
                    })
        
        if observed_vars:
            dt_reasoning_trace.append({
                "step": step_counter,
                "type": "observed_condition",
                "variables": observed_vars
            })
            step_counter += 1

    # 2. Relationships
    if relationships and relationships.relationships:
        for r in relationships.relationships:
            for inp in r.inputs:
                dt_variables_used.add(inp)
            dt_reasoning_trace.append({
                "step": step_counter,
                "type": "relationship",
                "relationship_id": r.relationship_id,
                "variables": r.inputs
            })
            step_counter += 1
            
    # 3. Risks
    if risks and risks.risk_patterns:
        for r in risks.risk_patterns:
            for pd in r.primary_drivers:
                pd_var = getattr(pd, 'variable', None)
                if pd_var:
                    dt_variables_used.add(str(pd_var))
            dt_reasoning_trace.append({
                "step": step_counter,
                "type": "risk_pattern",
                "risk_pattern_id": r.risk_pattern_id
            })
            step_counter += 1
            
            # Add secondary consequences as drivers
            for sc in r.secondary_consequences:
                sc_var = getattr(sc, 'variable', None) or getattr(sc, 'state', None) or "consequence"
                dt_variables_used.add(str(sc_var))
                dt_drivers.append({
                    "variable": str(sc_var),
                    "value": getattr(sc, 'value', None),
                    "unit": getattr(sc, 'unit', None),
                    "status": getattr(sc, 'state', "inferred_risk") or getattr(sc, 'status', "inferred_risk") or "inferred_risk",
                    "role": "secondary_consequence",
                    "source": r.risk_pattern_id
                })

    # Deduplicate Drivers
    unique_drivers = {}
    for d in dt_drivers:
        key = d['variable']
        if key not in unique_drivers:
            unique_drivers[key] = d
    dt_drivers = list(unique_drivers.values())
    
    # Filter by intent if applicable
    if target_vars and query_intent not in ["intervention", "reasoning", "risk"]:
        # We filter the trace to only include steps and drivers relevant to target_vars
        # But we also keep variables that are linked in the reasoning trace
        linked_vars = set(target_vars)
        for r in relationships.relationships if relationships else []:
            if any(tv in r.inputs for tv in linked_vars) or any(tv in [s.name for s in r.downstream_states] for tv in linked_vars):
                linked_vars.update(r.inputs)
                linked_vars.update([s.name for s in r.downstream_states])
                
        dt_drivers = [d for d in dt_drivers if d['variable'] in linked_vars or d.get('role') == 'secondary_consequence']
        dt_metrics = [m for m in dt_metrics if m['name'] in linked_vars]
        dt_variables_used = set(linked_vars).intersection(dt_variables_used)
        
    # Remove recommendation for informational queries if it doesn't directly address the target
    if query_intent not in ["intervention", "general_environment"]:
        if target_vars and recommendation:
            impacted = set()
            if hasattr(recommendation.impacted_metrics, 'direct'):
                impacted.update(recommendation.impacted_metrics.direct or [])
            if hasattr(recommendation.impacted_metrics, 'indirect'):
                impacted.update(recommendation.impacted_metrics.indirect or [])
            # If the recommendation doesn't impact any focal variable, hide it
            if not impacted.intersection(set(target_vars)):
                recommendation = None
                rec_context = None

    # 4. Recommendation & Evidence
    dt_recommendations = []
    dt_time_horizon = {"value": "not_applicable", "reason": "No recommendation generated."}
    if recommendation:
        impacted_list = []
        if hasattr(recommendation.impacted_metrics, 'direct'):
            impacted_list.extend(recommendation.impacted_metrics.direct or [])
        if hasattr(recommendation.impacted_metrics, 'indirect'):
            impacted_list.extend(recommendation.impacted_metrics.indirect or [])
        elif isinstance(recommendation.impacted_metrics, dict):
            impacted_list.extend(recommendation.impacted_metrics.get('direct', []))
            impacted_list.extend(recommendation.impacted_metrics.get('indirect', []))

        conf_str = recommendation.confidence.level if hasattr(recommendation.confidence, 'level') else str(recommendation.confidence)
        rec_id = getattr(recommendation, 'recommendation_id', 'rec')
        intervention_id = rec_id.replace("rec_", "") if rec_id.startswith("rec_") else rec_id

        dt_recommendations.append({
            "intervention_id": intervention_id,
            "what_to_do": recommendation.what_to_do,
            "why_it_works": recommendation.why_it_works,
            "environmental_mechanism": recommendation.environmental_mechanism,
            "impacted_metrics": impacted_list,
            "time_horizon": recommendation.time_horizon,
            "confidence": conf_str,
            "evidence_claims": getattr(recommendation, 'evidence_claims', []) or []
        })
        
        valid_horizons = ["short_term", "medium_term", "long_term", "context_dependent", "not_applicable"]
        horizon_val = recommendation.time_horizon if recommendation.time_horizon in valid_horizons else "context_dependent"
        dt_time_horizon = {
            "value": horizon_val,
            "reason": "Derived from environmental recommendation."
        }
        dt_reasoning_trace.append({
            "step": step_counter,
            "type": "intervention",
            "intervention_id": rec_id
        })
        step_counter += 1
        
        rec_ev = getattr(recommendation, 'evidence', None)
        if rec_ev:
            dt_reasoning_trace.append({
                "step": step_counter,
                "type": "evidence",
                "chunk_ids": [getattr(e, 'chunk_id', str(e)) for e in rec_ev]
            })
            step_counter += 1

    deterministic_trace = {
        "drivers": dt_drivers,
        "metrics": dt_metrics,
        "recommendations": dt_recommendations,
        "time_horizon": dt_time_horizon,
        "evidence": evidence_context,
        "variables_used": [str(v) for v in dt_variables_used if v is not None],
        "reasoning_trace": dt_reasoning_trace,
        "claims": recommendation.claims if recommendation else [],
    }

    return LLMContextData(
        user_query=user_query,
        conversation_context=conversation_context,
        profile=profile_dict,
        baseline=baseline_context,
        relationships=rel_context,
        risks=risk_context,
        intervention_candidates=cands_context,
        recommendation=rec_context,
        evidence=evidence_context,
        quality_guard_status=guard_result.status if guard_result else "unknown",
        quality_guard_reason=guard_result.reason if guard_result else "",
        deterministic_trace=deterministic_trace,
        claims=[c.model_dump() for c in recommendation.claims] if recommendation else []
    )
