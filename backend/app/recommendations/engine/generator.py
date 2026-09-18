import uuid
from typing import List, Dict, Any, Optional
from app.reasoning.baseline.schemas import BaselineProfileResponse
from app.reasoning.relationships.schemas import RelationshipProfileResponse
from app.reasoning.risk.schemas import RiskProfileResponse
from app.recommendations.interventions.schemas import InterventionProfileResponse, CandidateIntervention
from app.recommendations.engine.schemas import (
    StructuredRecommendation, RecommendationProfileResponse,
    ImpactedMetrics, Confidence, ReasoningStep
)
from app.schemas.response import Claim, EvidenceReference

from app.recommendations.guard.schemas import ValidationFeedback

class RecommendationEngine:
    def generate(self, 
                 baseline: BaselineProfileResponse, 
                 relationships: RelationshipProfileResponse,
                 risks: RiskProfileResponse, 
                 interventions: InterventionProfileResponse,
                 validation_feedback: Optional[List[ValidationFeedback]] = None) -> RecommendationProfileResponse:
        
        recs: List[StructuredRecommendation] = []
        
        if not interventions.intervention_candidates:
            return RecommendationProfileResponse(
                profile_id=baseline.profile_id,
                recommendations=[],
                recommendation_status="no_supported_intervention",
                reason="No intervention in the curated intervention knowledge base matches the detected environmental conditions with sufficient evidence."
            )
            
        # Base risk and relationships available
        available_risk_ids = [r.risk_pattern_id for r in risks.risk_patterns if r.status == "potential"]
        
        # Build recommendation from candidates
        for cand in interventions.intervention_candidates:
            
            # Trace variables strictly from matched conditions
            variables_used_set = set()
            risk_ids_used = []
            rel_ids_used = []
            
            for condition in cand.matched_conditions:
                matched_risk = next((r for r in risks.risk_patterns if r.risk_pattern_id == condition), None)
                if matched_risk:
                    risk_ids_used.append(matched_risk.risk_pattern_id)
                    variables_used_set.update(matched_risk.variables_used)
                    rel_ids_used.extend(matched_risk.relationships_used)
                else:
                    for risk in risks.risk_patterns:
                        for d in risk.primary_drivers + risk.secondary_consequences:
                            var_name = d.variable or d.state
                            if var_name and f"{d.status}_{var_name}" == condition:
                                variables_used_set.add(var_name)
            
            variables_used = list(variables_used_set)
            
            # Applicability Check
            missing_context = []
            if len(variables_used) >= 3:
                applicability = "applicable"
            else:
                applicability = "context_dependent"
                missing_context.append("More environmental variables needed for full context")
                
            # Confidence Logic
            confidence_level = "medium"
            confidence_reason = "Supported by scientific evidence."
            
            if cand.evidence_status == "insufficient_evidence":
                if applicability == "applicable":
                    confidence_level = "high"
                    confidence_reason = "High — deterministic applicability confidence; scientific evidence trace is incomplete."
                else:
                    confidence_level = "low"
                    confidence_reason = "Insufficient evidence to confidently recommend."
            elif cand.evidence_status == "supported":
                if applicability == "context_dependent":
                    confidence_level = "medium"
                    confidence_reason = "The intervention is supported by scientific evidence, but some contextual environmental information is unavailable."
                elif len(variables_used) >= 3:
                    confidence_level = "high"
                    confidence_reason = "The intervention is supported by scientific evidence and matches multiple observed environmental conditions."

            # Construct mechanisms text (deterministic generation)
            mechanisms_text = " and ".join(cand.mechanisms).replace("_", " ") if cand.mechanisms else "general principles"
            
            # Construct metrics (we use a simple splitting for demonstration)
            direct_metrics = []
            indirect_metrics = []
            for metric in cand.potentially_affected_metrics:
                if metric in variables_used:
                    direct_metrics.append(metric)
                else:
                    indirect_metrics.append(metric)
                    
            impacted = ImpactedMetrics(
                direct=direct_metrics,
                indirect=indirect_metrics,
                context_dependent=[]
            )

            # Build reasoning trace
            trace = []
            step = 1
            trace.append(ReasoningStep(
                step=step,
                type="observed_condition",
                variables=variables_used
            ))
            step += 1
            for rel in rel_ids_used:
                trace.append(ReasoningStep(step=step, type="relationship", relationship_id=rel))
                step += 1
            for risk_id in risk_ids_used:
                trace.append(ReasoningStep(step=step, type="risk_pattern", risk_pattern_id=risk_id))
                step += 1
            
            trace.append(ReasoningStep(step=step, type="intervention", intervention_id=cand.intervention_id))
            step += 1
            trace.append(ReasoningStep(step=step, type="evidence", chunk_ids=[e.chunk_id for e in cand.evidence]))
            step += 1
            trace.append(ReasoningStep(step=step, type="recommendation", status=cand.evidence_status))
            
            what_to_do = f"Introduce {cand.name.lower()} to address the identified environmental conditions."
            why_it_works = f"The current profile exhibits patterns related to {', '.join(cand.matched_conditions)}. {cand.name} can address multiple parts of this pressure by operating through {mechanisms_text}."
            env_mechanism = f"{cand.name} -> {mechanisms_text} -> potential effects on {', '.join(cand.potentially_affected_metrics)}."

            # Construct Claims
            claims = []
            
            # 1. Deterministic Analysis Claims (Why it works / Risk Patterns)
            claim_id_det = f"claim_{cand.intervention_id}_det"
            claims.append(Claim(
                claim_id=claim_id_det,
                claim_text=why_it_works,
                claim_type="relationship",
                origin="deterministic_analysis",
                support_status="supported",
                reasoning_reference={"risk_patterns": risk_ids_used},
                evidence=[]
            ))
            
            # 2. Scientific Claims (Mechanisms backed by Evidence)
            claim_id_sci = f"claim_{cand.intervention_id}_sci"
            sci_evidence = []
            for idx, e in enumerate(cand.evidence):
                sci_evidence.append(EvidenceReference(
                    source_id=e.source_id,
                    chunk_id=e.chunk_id,
                    document_id=e.document_id,
                    source=e.source,
                    document=e.document,
                    year=None,
                    page_number=e.page_number,
                    section=e.section,
                    url=e.url,
                    relevance=e.relevance
                ))
            
            claims.append(Claim(
                claim_id=claim_id_sci,
                claim_text=env_mechanism,
                claim_type="environmental_mechanism",
                origin="scientific_evidence",
                support_status="supported" if sci_evidence else "insufficient_evidence",
                reasoning_reference=None,
                evidence=sci_evidence
            ))

            rec = StructuredRecommendation(
                recommendation_id=f"rec_{cand.intervention_id}",
                what_to_do=what_to_do,
                why_it_works=why_it_works,
                environmental_mechanism=env_mechanism,
                impacted_metrics=impacted,
                time_horizon=cand.time_horizon,
                confidence=Confidence(level=confidence_level, reason=confidence_reason),
                evidence_status=cand.evidence_status,
                evidence_claims=[c.claim_id for c in claims],
                evidence=sci_evidence,
                claims=claims,
                risk_patterns_used=risk_ids_used,
                relationships_used=rel_ids_used,
                variables_used=variables_used,
                matched_conditions=cand.matched_conditions,
                constraints=cand.constraints,
                tradeoffs=cand.tradeoffs,
                applicability=applicability,
                missing_context=missing_context,
                reasoning_trace=trace
            )
            recs.append(rec)
            
        return RecommendationProfileResponse(
            profile_id=baseline.profile_id,
            recommendations=recs,
            recommendation_status="success" if recs else "no_supported_intervention"
        )
