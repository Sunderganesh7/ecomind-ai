import logging
from typing import List, Dict, Any, Optional
from app.reasoning.risk.schemas import RiskProfileResponse, CompositeRiskPattern
from app.recommendations.interventions.schemas import (
    InterventionProfileResponse, CandidateIntervention, 
    EvidenceRecord, Uncertainty, Tradeoff
)
from app.recommendations.interventions.registry import InterventionRegistry
from app.rag.search.search_service import KnowledgeSearchService

logger = logging.getLogger(__name__)

class InterventionEvaluator:
    def __init__(self, registry: InterventionRegistry = None, search_service: KnowledgeSearchService = None):
        self.registry = registry or InterventionRegistry()
        self.search_service = search_service or KnowledgeSearchService()

    def evaluate(self, risk_resp: RiskProfileResponse) -> InterventionProfileResponse:
        definitions = self.registry.get_all()
        candidates: List[CandidateIntervention] = []
        
        # Flatten available conditions from Risk response
        active_conditions = set()
        active_risk_patterns = []
        for risk in risk_resp.risk_patterns:
            if risk.status == "potential":
                active_conditions.add(risk.risk_pattern_id)
                active_risk_patterns.append(risk.risk_pattern_id)
                # Also consider primary drivers as conditions
                for driver in risk.primary_drivers:
                    if driver.variable and driver.status:
                        active_conditions.add(f"{driver.status}_{driver.variable}")
                # And secondary consequences
                for cons in risk.secondary_consequences:
                    if cons.state and cons.status:
                        active_conditions.add(f"{cons.status}_{cons.state}")

        for definition in definitions:
            # Check if this intervention targets any of the active conditions
            matched_conditions = [c for c in definition.target_conditions if c in active_conditions]
            
            if not matched_conditions:
                continue
                
            evidence_records = []
            if definition.evidence_requirements:
                query = " ".join(definition.evidence_requirements)
                try:
                    search_results = self.search_service.search(query, top_k=2)
                    for res in search_results:
                        if res.get("relevance", 0.0) >= 0.65:
                            evidence_records.append(EvidenceRecord(
                                chunk_id=res.get("chunk_id", ""),
                                document_id=res.get("document_id", "Unknown"),
                                source_id=res.get("source_id", "Unknown"),
                                source=res.get("source", res.get("source_id", "Unknown")),
                                document=res.get("title", ""),
                                page_number=res.get("page_number"),
                                section=res.get("section"),
                                url=res.get("url"),
                                relevance=res.get("relevance", 0.0)
                            ))
                except Exception as e:
                    logger.error(f"Search failed for intervention {definition.intervention_id}: {e}")
                    
            evidence_status = "supported" if evidence_records else "insufficient_evidence"
            
            # Identify mechanisms and affected metrics
            mechanism_ids = [m.mechanism_id for m in definition.mechanisms]
            affected_metrics = []
            for m in definition.mechanisms:
                for am in m.affected_metrics:
                    if am.metric not in affected_metrics:
                        affected_metrics.append(am.metric)
                        
            # Uncertainty calculation
            uncertainty_reasons = []
            uncertainty_level = "low"
            if not evidence_records:
                uncertainty_level = "high"
                uncertainty_reasons.append("Missing scientific evidence in corpus.")
            
            if not all(c in active_conditions for c in definition.target_conditions):
                uncertainty_level = "medium" if uncertainty_level != "high" else "high"
                uncertainty_reasons.append("Not all target conditions are explicitly met (partial match).")
                
            if definition.time_horizon == "context_dependent":
                uncertainty_reasons.append("Time horizon is context-dependent.")
                
            if not uncertainty_reasons:
                uncertainty_reasons.append("Supported by converging multiple conditions and explicit evidence.")
                
            candidates.append(CandidateIntervention(
                intervention_id=definition.intervention_id,
                name=definition.name,
                matched_conditions=matched_conditions,
                mechanisms=mechanism_ids,
                potentially_affected_metrics=affected_metrics,
                evidence_status=evidence_status,
                evidence=evidence_records,
                constraints=definition.constraints,
                tradeoffs=definition.tradeoffs,
                time_horizon=definition.time_horizon,
                uncertainty=Uncertainty(level=uncertainty_level, reasons=uncertainty_reasons)
            ))
            
        return InterventionProfileResponse(
            profile_id=risk_resp.profile_id,
            risk_patterns_used=active_risk_patterns,
            intervention_candidates=candidates
        )
