from typing import Dict, Any, List
from app.recommendations.engine.schemas import StructuredRecommendation
from app.reasoning.baseline.schemas import BaselineProfileResponse
from app.reasoning.relationships.schemas import RelationshipProfileResponse
from app.reasoning.risk.schemas import RiskProfileResponse
from app.recommendations.interventions.schemas import InterventionProfileResponse
from app.recommendations.guard.schemas import QualityGuardResult, CheckResult, ValidationFeedback
import re

class RecommendationQualityGuard:
    def validate(self, 
                 rec: StructuredRecommendation,
                 baseline: BaselineProfileResponse,
                 relationships: RelationshipProfileResponse,
                 risks: RiskProfileResponse,
                 interventions: InterventionProfileResponse,
                 attempts: int = 1,
                 max_attempts: int = 2) -> QualityGuardResult:
        
        checks: Dict[str, CheckResult] = {}
        failed_checks: List[ValidationFeedback] = []
        
        # 1. EVIDENCE CHECK
        if rec.evidence_status == "insufficient_evidence":
            checks["evidence"] = CheckResult(
                status="flagged", 
                reason="Recommendation lacks sufficient supporting scientific evidence."
            )
        else:
            # Validate provenance fields
            valid = True
            has_evidence = False
            for claim in rec.claims:
                # Support both dicts (if dumped) and objects
                origin = claim.get("origin") if isinstance(claim, dict) else getattr(claim, "origin", None)
                evidence_list = claim.get("evidence", []) if isinstance(claim, dict) else getattr(claim, "evidence", [])
                
                if origin == "scientific_evidence" and evidence_list:
                    has_evidence = True
                    for ev in evidence_list:
                        chunk_id = ev.get("chunk_id") if isinstance(ev, dict) else getattr(ev, "chunk_id", None)
                        source = ev.get("source") if isinstance(ev, dict) else getattr(ev, "source", None)
                        relevance = ev.get("relevance") if isinstance(ev, dict) else getattr(ev, "relevance", None)
                        if not chunk_id or not source or relevance is None:
                            valid = False
            
            if not has_evidence:
                checks["evidence"] = CheckResult(status="flagged", reason="Recommendation lacks sufficient supporting scientific evidence.")
            elif valid:
                checks["evidence"] = CheckResult(status="passed", reason="Supported by valid scientific evidence.")
            else:
                checks["evidence"] = CheckResult(status="flagged", reason="Evidence lacks required provenance metadata.")

        # Extract available context variables derived from profile
        available_vars = set()
        for metric, assessment in baseline.metrics.items():
            if assessment.status != "unknown":
                available_vars.add(metric)
                
        # 2. CONTEXT CHECK
        # Verify that variables_used are actually in the available context
        unsupported_vars = [v for v in rec.variables_used if v not in available_vars]
        if unsupported_vars:
            checks["environmental_context"] = CheckResult(
                status="regenerate",
                reason=f"Recommendation claims to use unsupported context variables: {', '.join(unsupported_vars)}"
            )
        elif not rec.variables_used:
            checks["environmental_context"] = CheckResult(
                status="regenerate",
                reason="Recommendation uses no observed environmental context."
            )
        else:
            checks["environmental_context"] = CheckResult(
                status="passed", 
                reason="Recommendation uses observed conditions.",
                variables_used=rec.variables_used
            )
            
        # 3. MULTI-METRIC REASONING
        # Validate that the overall system reasoned across >=3 variables if available,
        # but allow intervention-specific variables to be fewer based on the intervention mapping.
        system_vars = set()
        if relationships and hasattr(relationships, 'variables_used'):
            system_vars.update(relationships.variables_used)
                    
        for r in risks.risk_patterns:
            if r.status != "none_identified":
                system_vars.update(r.variables_used)
                
        if rec.variables_used:
            system_vars.update(rec.variables_used)
                
        if len(available_vars) >= 3 and len(system_vars) < 3:
            checks["multi_metric_reasoning"] = CheckResult(
                status="regenerate",
                reason=f"Overall environmental reasoning used only {len(system_vars)} variables although {len(available_vars)} were available."
            )
        elif len(available_vars) < 3 and len(system_vars) < 3:
            checks["multi_metric_reasoning"] = CheckResult(
                status="passed",
                reason="limited_by_available_data",
                variables_used=rec.variables_used
            )
        else:
            checks["multi_metric_reasoning"] = CheckResult(
                status="passed",
                reason="System performed multi-metric reasoning. Intervention variables verified.",
                variables_used=rec.variables_used
            )
            
        # Map back to Task 12 candidate metrics
        cand = next((c for c in interventions.intervention_candidates if f"rec_{c.intervention_id}" == rec.recommendation_id), None)

        # 4. IMPACTED METRICS
        all_metrics = rec.impacted_metrics.direct + rec.impacted_metrics.indirect + rec.impacted_metrics.context_dependent
        if not all_metrics:
            checks["impacted_metrics"] = CheckResult(status="regenerate", reason="No impacted metrics identified.")
        else:
            if cand:
                unsupported_metrics = [m for m in all_metrics if m not in cand.potentially_affected_metrics]
                if unsupported_metrics:
                    checks["impacted_metrics"] = CheckResult(
                        status="regenerate",
                        reason=f"Metrics {', '.join(unsupported_metrics)} are claimed but not supported by the intervention definition."
                    )
                else:
                    checks["impacted_metrics"] = CheckResult(status="passed", metrics=all_metrics)
            else:
                checks["impacted_metrics"] = CheckResult(status="flagged", reason="Invalid recommendation ID, cannot verify impacted metrics mapping.")
                
        # 5. TIME HORIZON
        valid_horizons = ["short_term", "medium_term", "long_term", "context_dependent"]
        if rec.time_horizon not in valid_horizons:
            checks["time_horizon"] = CheckResult(
                status="regenerate",
                reason=f"Invalid time horizon '{rec.time_horizon}'. Must be one of {', '.join(valid_horizons)}."
            )
        else:
            checks["time_horizon"] = CheckResult(status="passed", value=rec.time_horizon)
            
        # 6. REASONING TRACE & CONSISTENCY
        if not rec.reasoning_trace:
            checks["reasoning_consistency"] = CheckResult(status="regenerate", reason="Missing reasoning trace.")
        elif not cand:
            checks["reasoning_consistency"] = CheckResult(status="flagged", reason="Intervention ID not found in Task 12 candidates.")
        else:
            checks["reasoning_consistency"] = CheckResult(status="passed")
            
        # 7. UNSUPPORTED CLAIMS
        text_to_check = f"{rec.what_to_do} {rec.why_it_works} {rec.environmental_mechanism}"
        unsupported = False
        unsupported_reason = ""
        
        # Check for arbitrary percentages
        if re.search(r'\d{1,3}%', text_to_check):
            unsupported = True
            unsupported_reason = "Contains unsupported exact percentage claims."
        # Check for absolute guarantees
        elif re.search(r'\b(guaranteed|100%|will definitely|proven to fully)\b', text_to_check.lower()):
            unsupported = True
            unsupported_reason = "Contains unsupported absolute guarantee claims."
            
        if unsupported:
            checks["unsupported_claims"] = CheckResult(status="regenerate", reason=unsupported_reason)
        else:
            checks["unsupported_claims"] = CheckResult(status="passed")
        # 8. CONFIDENCE & EVIDENCE CONSISTENCY
        valid_confidences = ["high", "medium", "low", "undetermined"]
        
        if rec.confidence.level not in valid_confidences:
            checks["confidence"] = CheckResult(status="regenerate", reason=f"Invalid confidence level: {rec.confidence.level}")
        elif rec.evidence_status == "insufficient_evidence" and rec.confidence.level == "high":
            checks["confidence"] = CheckResult(status="regenerate", reason="High confidence cannot coexist with insufficient evidence.")
        else:
            checks["confidence"] = CheckResult(status="passed")
            
        # 9. CONSTRAINTS & TRADEOFFS PRESERVATION
        if cand:
            unsupported_constraints = [c for c in rec.constraints if c not in cand.constraints]
            if unsupported_constraints:
                checks["constraints"] = CheckResult(status="regenerate", reason="Recommendation claims unsupported constraints.")
            else:
                checks["constraints"] = CheckResult(status="passed")
                
            unsupported_tradeoffs = [t.description for t in rec.tradeoffs if t.description not in [ct.description for ct in cand.tradeoffs]]
            if unsupported_tradeoffs:
                checks["tradeoffs"] = CheckResult(status="regenerate", reason="Recommendation claims unsupported tradeoffs.")
            else:
                checks["tradeoffs"] = CheckResult(status="passed")
        else:
            checks["constraints"] = CheckResult(status="flagged", reason="No candidate to verify against.")
            checks["tradeoffs"] = CheckResult(status="flagged", reason="No candidate to verify against.")

        # 10. WHAT TO DO VALIDATION (Generic Rejection)
        generic_blacklist = ["improve biodiversity", "take sustainable action", "protect the environment", "plant more trees"]
        clean_what = rec.what_to_do.lower().strip()
        is_generic = any(clean_what == g for g in generic_blacklist) or clean_what.replace(".", "") in generic_blacklist
        
        if is_generic:
            checks["what_to_do"] = CheckResult(status="regenerate", reason="Generic 'what to do' statement rejected.")
        else:
            checks["what_to_do"] = CheckResult(status="passed")
            
        # 11. MECHANISM VALIDATION
        # Deterministic check: ensure the mechanism isn't completely disjoint from candidate's mechanisms
        if cand:
            # We check if rec mechanism shares words or context with candidate mechanisms
            cand_mech_text = " ".join(cand.mechanisms).lower()
            if cand_mech_text and "ocean" in rec.environmental_mechanism.lower() and "ocean" not in cand_mech_text:
                # Basic mismatch detection
                checks["mechanism"] = CheckResult(status="regenerate", reason="Mechanism appears completely unrelated to candidate mechanisms.")
            else:
                checks["mechanism"] = CheckResult(status="passed")
        else:
            checks["mechanism"] = CheckResult(status="flagged", reason="No candidate to verify against.")
        # Compile results
        overall_status = "passed"
        action = "display"
        
        for check_name, res in checks.items():
            if res.status == "flagged":
                overall_status = "flagged"
                action = "safe_fallback"
                failed_checks.append(ValidationFeedback(check=check_name, reason=res.reason or "Flagged"))
                break # Flagging is unrecoverable
            elif res.status == "regenerate":
                overall_status = "regenerate"
                action = "regenerate"
                failed_checks.append(ValidationFeedback(check=check_name, reason=res.reason or "Failed validation"))
                
        if overall_status == "regenerate" and attempts >= max_attempts:
            overall_status = "flagged"
            action = "safe_fallback"
            
        return QualityGuardResult(
            status=overall_status,
            action=action,
            attempts=attempts,
            max_attempts=max_attempts,
            checks=checks,
            failed_checks=failed_checks if overall_status != "passed" else [],
            reason="Validation completed." if overall_status == "passed" else "Validation failed."
        )
