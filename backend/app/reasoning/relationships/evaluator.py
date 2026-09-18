import logging
from typing import List, Dict, Any, Optional
from app.reasoning.baseline.schemas import BaselineProfileResponse
from app.reasoning.relationships.schemas import (
    RelationshipEvaluation, InferredState, InputState, 
    EvidenceRecord, Uncertainty, TraceStep, RelationshipProfileResponse
)
from app.reasoning.relationships.registry import RelationshipRegistry
from app.rag.search.search_service import KnowledgeSearchService

logger = logging.getLogger(__name__)

class RelationshipEvaluator:
    def __init__(self, registry: RelationshipRegistry = None, search_service: KnowledgeSearchService = None):
        self.registry = registry or RelationshipRegistry()
        self.search_service = search_service or KnowledgeSearchService()

    def evaluate(self, baseline: BaselineProfileResponse) -> RelationshipProfileResponse:
        metrics = baseline.metrics
        relationships = self.registry.get_all()
        
        evaluations: List[RelationshipEvaluation] = []
        variables_used = set()
        trace: List[TraceStep] = []
        step_counter = 1
        
        for definition in relationships:
            # Check if all required inputs are present and not 'unknown'
            missing_inputs = []
            inputs_state = {}
            for req in definition.required_inputs:
                metric_assessment = metrics.get(req)
                if not metric_assessment or metric_assessment.status == "unknown":
                    missing_inputs.append(req)
                else:
                    inputs_state[req] = InputState(
                        value=metric_assessment.observed_value,
                        status=metric_assessment.status
                    )
                    
            if missing_inputs:
                evaluations.append(RelationshipEvaluation(
                    relationship_id=definition.relationship_id,
                    inputs=definition.required_inputs,
                    input_states=inputs_state,
                    intermediate_states=[],
                    downstream_states=[],
                    status="insufficient_data",
                    evidence_status="insufficient_evidence",
                    uncertainty=Uncertainty(
                        level="high",
                        reasons=[f"Missing required input(s): {', '.join(missing_inputs)}"]
                    )
                ))
                continue
            
            # Activated!
            for req in definition.required_inputs:
                variables_used.add(req)
                
            trace.append(TraceStep(
                step=step_counter, type="observed_input", variables=definition.required_inputs
            ))
            step_counter += 1
            
            trace.append(TraceStep(
                step=step_counter, type="relationship", relationship_id=definition.relationship_id
            ))
            step_counter += 1
            
            # Generate intermediate and downstream states based on explicit relationship rules
            inferred_status = "normal"
            downstream_status = "none_identified"
            
            if definition.relationship_id == "soil_water":
                oc_stat = inputs_state.get("organic_carbon")
                m_stat = inputs_state.get("moisture")
                if (oc_stat and oc_stat.status in ["low", "degraded"]) or (m_stat and m_stat.status in ["low", "constrained"]):
                    inferred_status = "potential_constraint"
                    downstream_status = "potential_pressure"
            elif definition.relationship_id == "climate_water":
                rf_stat = inputs_state.get("rainfall")
                temp_stat = inputs_state.get("temperature")
                if (rf_stat and rf_stat.status == "low") or (temp_stat and temp_stat.status == "high"):
                    inferred_status = "potential_water_constraint"
                    downstream_status = "potential_vegetation_stress"
            elif definition.relationship_id == "land_habitat":
                lu_stat = inputs_state.get("land_use")
                cs_stat = inputs_state.get("cropping_system")
                if (lu_stat and lu_stat.status == "degraded") or (cs_stat and cs_stat.status == "simplified"):
                    inferred_status = "potential_simplification"
                    downstream_status = "potential_fragmentation_pressure"
            elif definition.relationship_id == "deforestation_habitat":
                def_stat = inputs_state.get("deforestation")
                hd_stat = inputs_state.get("habitat_diversity")
                if (def_stat and def_stat.status == "degraded") or (hd_stat and hd_stat.status == "low"):
                    inferred_status = "potential_habitat_loss"
                    downstream_status = "potential_biodiversity_pressure"
            else:
                has_constraint = any(s.status in ["low", "high", "degraded", "simplified", "constrained"] for s in inputs_state.values())
                inferred_status = "potential_constraint" if has_constraint else "normal"
                downstream_status = "potential_pressure" if has_constraint else "none_identified"
            
            intermediate_states = [InferredState(name=s, status=inferred_status) for s in definition.intermediate_states]
            for s in intermediate_states:
                trace.append(TraceStep(step=step_counter, type="derived_state", state=s.name))
                step_counter += 1
                
            downstream_states = [InferredState(name=s, status=downstream_status) for s in definition.downstream_states]
            for s in downstream_states:
                trace.append(TraceStep(step=step_counter, type="downstream_implication", state=s.name))
                step_counter += 1
                
            # Search for Evidence
            evidence_records = []
            if definition.evidence_topics:
                query = " ".join(definition.evidence_topics)
                try:
                    search_results = self.search_service.search(query, top_k=2)
                    for res in search_results:
                        evidence_records.append(EvidenceRecord(
                            chunk_id=res.get("chunk_id", ""),
                            source=res.get("source_id", "Unknown"),
                            title=res.get("title", ""),
                            page_number=res.get("page_number"),
                            relevance=res.get("relevance", 0.0)
                        ))
                except Exception as e:
                    logger.error(f"Search failed for relationship {definition.relationship_id}: {e}")
            
            evidence_status = "supported" if evidence_records else "insufficient_evidence"
            
            if evidence_records:
                source_ids = list(set([e.source for e in evidence_records]))
                trace.append(TraceStep(step=step_counter, type="evidence", source_ids=source_ids))
                step_counter += 1
                
            # Uncertainty logic
            has_context_dependent = any(s.status == "context_dependent" for s in inputs_state.values())
            has_unknown = any(s.status == "unknown" for s in inputs_state.values())
            
            uncertainty_reasons = []
            if evidence_records:
                uncertainty_reasons.append("Supported by retrieved scientific evidence.")
            else:
                uncertainty_reasons.append("Insufficient scientific evidence in corpus.")
                
            if has_context_dependent:
                uncertainty_reasons.append("Contains context-dependent variables requiring local baseline.")
            if has_unknown:
                uncertainty_reasons.append("Contains unknown or missing input statuses.")
                
            if not evidence_records or has_unknown:
                uncertainty_level = "high"
            elif has_context_dependent:
                uncertainty_level = "medium"
            else:
                uncertainty_level = "low"
                
            evaluations.append(RelationshipEvaluation(
                relationship_id=definition.relationship_id,
                inputs=definition.required_inputs,
                input_states=inputs_state,
                intermediate_states=intermediate_states,
                downstream_states=downstream_states,
                status="evaluable",
                evidence_status=evidence_status,
                evidence=evidence_records,
                uncertainty=Uncertainty(
                    level=uncertainty_level,
                    reasons=uncertainty_reasons
                )
            ))
            
        return RelationshipProfileResponse(
            profile_id=baseline.profile_id,
            variables_used=list(variables_used),
            relationships=evaluations,
            reasoning_trace=trace
        )
