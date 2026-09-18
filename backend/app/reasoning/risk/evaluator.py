import logging
from typing import List, Dict, Any, Optional
from app.reasoning.baseline.schemas import BaselineProfileResponse
from app.reasoning.relationships.schemas import RelationshipProfileResponse, RelationshipEvaluation
from app.reasoning.risk.schemas import (
    RiskProfileResponse, CompositeRiskPattern, Driver, 
    EvidenceRecord, Uncertainty, TraceStep, Synthesis
)
from app.reasoning.risk.registry import RiskRegistry

logger = logging.getLogger(__name__)

class RiskEvaluator:
    def __init__(self, registry: RiskRegistry = None):
        self.registry = registry or RiskRegistry()

    def evaluate(self, baseline: BaselineProfileResponse, relationships_resp: RelationshipProfileResponse) -> RiskProfileResponse:
        definitions = self.registry.get_all()
        risk_patterns: List[CompositeRiskPattern] = []
        
        # Build lookup maps for faster access
        baseline_metrics = baseline.metrics
        evaluated_rels = {r.relationship_id: r for r in relationships_resp.relationships}
        
        for idx, pattern_def in enumerate(definitions):
            step_counter = 1
            trace: List[TraceStep] = []
            primary_drivers: List[Driver] = []
            supporting_drivers: List[Driver] = []
            secondary_consequences: List[Driver] = []
            evidence: List[EvidenceRecord] = []
            variables_used = set()
            rels_used = []
            missing_variables = []
            
            # 1. Check required signals (variables)
            for req in pattern_def.required_signals:
                if req in baseline_metrics and baseline_metrics[req].status != "unknown":
                    stat = baseline_metrics[req].status
                    # For this task, we will add all available required variables as observed drivers.
                    # A more nuanced engine would only add them if they are in a constrained state.
                    primary_drivers.append(Driver(
                        variable=req,
                        status=stat,
                        type="observed",
                        role="primary_driver",
                        value=baseline_metrics[req].observed_value
                    ))
                    variables_used.add(req)
                    trace.append(TraceStep(step=step_counter, type="observed_signal", variable=req, status=stat))
                    step_counter += 1
                else:
                    missing_variables.append(req)
                    
            if missing_variables:
                risk_patterns.append(CompositeRiskPattern(
                    risk_pattern_id=pattern_def.risk_pattern_id,
                    name=pattern_def.name,
                    status="insufficient_data",
                    variables_used=[],
                    primary_drivers=[],
                    supporting_signals=[],
                    relationships_used=[],
                    secondary_consequences=[],
                    evidence_status="insufficient_evidence",
                    evidence=[],
                    uncertainty=Uncertainty(level="high", reasons=[f"Missing variables: {', '.join(missing_variables)}"]),
                    reasoning_trace=[],
                    missing_variables=missing_variables
                ))
                continue
                
            # 2. Check supporting signals
            for sup in pattern_def.supporting_signals:
                if sup in baseline_metrics and baseline_metrics[sup].status != "unknown":
                    stat = baseline_metrics[sup].status
                    supporting_drivers.append(Driver(
                        variable=sup,
                        status=stat,
                        type="observed",
                        role="primary_driver",
                        value=baseline_metrics[sup].observed_value
                    ))
                    variables_used.add(sup)
                    trace.append(TraceStep(step=step_counter, type="observed_signal", variable=sup, status=stat))
                    step_counter += 1
            
            # 3. Pull relationships
            evidence_status = "insufficient_evidence"
            has_evidence = False
            has_uncertainty = False
            uncertainty_reasons = set()
            
            for rel_id in pattern_def.relationships:
                if rel_id in evaluated_rels:
                    rel = evaluated_rels[rel_id]
                    if rel.status == "evaluable":
                        rels_used.append(rel_id)
                        trace.append(TraceStep(step=step_counter, type="relationship", relationship_id=rel_id))
                        step_counter += 1
                        
                        # Extract derived states as secondary consequences
                        for d_state in rel.downstream_states:
                            if d_state.status != "none_identified":
                                secondary_consequences.append(Driver(
                                    variable=d_state.name,
                                    status=d_state.status,
                                    type="inferred",
                                    role="secondary_consequence"
                                ))
                                trace.append(TraceStep(step=step_counter, type="derived_state", state=d_state.name, status=d_state.status))
                                step_counter += 1
                        
                        # Aggregate evidence
                        for e in rel.evidence:
                            has_evidence = True
                            # mapping to our local evidence record
                            evidence.append(EvidenceRecord(
                                chunk_id=e.chunk_id,
                                source=e.source,
                                title=e.title,
                                page_number=e.page_number,
                                section=e.section,
                                relevance=e.relevance
                            ))
                            
                        if rel.uncertainty.level in ["medium", "high"]:
                            has_uncertainty = True
                            uncertainty_reasons.update(rel.uncertainty.reasons)

            # Deduplicate secondary consequences
            unique_sc = {sc.variable: sc for sc in secondary_consequences}
            secondary_consequences = list(unique_sc.values())
            
            # Determine if this risk is actually supported by any constrained conditions
            is_active = False
            for d in primary_drivers + supporting_drivers:
                if d.status in ["low", "high", "degraded", "simplified", "elevated"]:
                    is_active = True
                    break
            
            if not is_active:
                for sc in secondary_consequences:
                    if sc.status != "none_identified":
                        is_active = True
                        break
                        
            if not is_active:
                continue
            
            trace.append(TraceStep(step=step_counter, type="composite_pattern", pattern=pattern_def.risk_pattern_id))
            step_counter += 1
            
            if has_evidence:
                evidence_status = "supported"
                source_ids = list(set([e.source for e in evidence]))
                trace.append(TraceStep(step=step_counter, type="evidence", source_ids=source_ids))
                step_counter += 1
                
            uncertainty_level = "low"
            if has_uncertainty or not has_evidence:
                uncertainty_level = "medium"
            if not has_evidence and len(variables_used) < 3:
                uncertainty_level = "high"
                
            if not uncertainty_reasons:
                if has_evidence:
                    uncertainty_reasons.add("Supported by converging multiple inputs and scientific evidence.")
                else:
                    uncertainty_reasons.add("Evidence retrieval limitations exist.")
            
            # Synthesis
            synthesis = None
            if len(rels_used) >= 2:
                synthesis = Synthesis(
                    type="converging_pressures",
                    affected_system=pattern_def.outcome,
                    supporting_relationships=rels_used
                )
                
            risk_patterns.append(CompositeRiskPattern(
                risk_pattern_id=pattern_def.risk_pattern_id,
                name=pattern_def.name,
                status="potential",
                variables_used=list(variables_used),
                primary_drivers=primary_drivers,
                supporting_signals=supporting_drivers,
                relationships_used=rels_used,
                secondary_consequences=secondary_consequences,
                evidence_status=evidence_status,
                evidence=evidence,
                uncertainty=Uncertainty(level=uncertainty_level, reasons=list(uncertainty_reasons)),
                reasoning_trace=trace,
                synthesis=synthesis
            ))
            
        return RiskProfileResponse(
            profile_id=baseline.profile_id,
            risk_patterns=risk_patterns
        )
