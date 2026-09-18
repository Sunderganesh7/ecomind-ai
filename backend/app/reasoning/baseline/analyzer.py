from typing import Dict
from app.schemas.environmental import EnvironmentalObservation
from app.reasoning.baseline.schemas import BaselineProfileResponse, MetricAssessment, AggregatedBaseline, BaselineAggregateStatus
from app.reasoning.baseline.reference_service import ReferenceService
from app.reasoning.baseline.classifiers import classify_metric

class BaselineAnalyzer:
    def __init__(self, reference_service: ReferenceService = None):
        self.reference_service = reference_service or ReferenceService()
        
    def analyze_profile(self, profile) -> BaselineProfileResponse:
        metrics: Dict[str, MetricAssessment] = {}
        
        # Helper to process a group of metrics
        def _process_group(group_obj, group_name: str):
            if not group_obj:
                return
            
            data = {}
            if hasattr(group_obj, "__table__"):
                for c in group_obj.__table__.columns:
                    if c.name not in ["id", "observation_id"]:
                        data[c.name] = getattr(group_obj, c.name)
            else:
                data = group_obj.model_dump()
                
            for field, value in data.items():
                ref_data = self.reference_service.get_reference(field)
                assessment = classify_metric(field, value, ref_data)
                metrics[field] = assessment
                
        _process_group(profile.soil, "soil")
        _process_group(profile.climate, "climate")
        _process_group(profile.land, "land")
        _process_group(profile.biodiversity, "biodiversity")
        _process_group(profile.human_impact, "human_impact")

        summary = self._aggregate_baseline(metrics)
        
        return BaselineProfileResponse(
            profile_id=profile.id,
            metrics=metrics,
            summary=summary
        )
        
    def _aggregate_baseline(self, metrics: Dict[str, MetricAssessment]) -> AggregatedBaseline:
        # Rules for aggregation: pick the most severe status in the category
        
        def _aggregate_category(metric_names):
            active_metrics = [m for k, m in metrics.items() if k in metric_names and m.status not in ("unknown", "normal", "context_dependent")]
            if not active_metrics:
                return None
            
            # Simple priority: degraded > simplified/constrained/low/high > elevated
            # In a real app this would use a defined severity scale. For now, we return the first problematic status
            status = active_metrics[0].status
            for m in active_metrics:
                if m.status == "degraded":
                    status = "degraded"
                    break
                    
            supporting = [m.metric for m in active_metrics]
            return BaselineAggregateStatus(status=status, supporting_metrics=supporting)

        soil_status = _aggregate_category(["organic_carbon", "soil_ph", "moisture"])
        water_status = _aggregate_category(["rainfall"])
        habitat_status = _aggregate_category(["cropping_system", "land_use", "species_richness", "habitat_diversity", "pollution", "deforestation"])
        
        return AggregatedBaseline(
            soil_status=soil_status,
            water_status=water_status,
            habitat_status=habitat_status
        )
