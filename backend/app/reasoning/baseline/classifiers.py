from typing import Any, Dict, Tuple
from app.reasoning.baseline.schemas import ReferenceContext, ReferenceSource, MetricAssessment

def _build_evidence(ref_data: Dict[str, Any]) -> ReferenceSource:
    return ReferenceSource(
        source=ref_data.get("source"),
        title=ref_data.get("title"),
        year=ref_data.get("year"),
        url=ref_data.get("source_url")
    )

def _build_reference_context(ref_data: Dict[str, Any]) -> ReferenceContext:
    ref_type = ref_data.get("reference_type", "unknown")
    ref_values = ref_data.get("reference_values") or {}
    
    return ReferenceContext(
        type=ref_type,
        minimum=ref_values.get("minimum") if ref_type == "range" else None,
        maximum=ref_values.get("maximum") if ref_type == "range" else None,
        unit=ref_data.get("unit"),
        context=ref_data.get("context"),
        source=_build_evidence(ref_data) if ref_data.get("source") else None
    )

def classify_metric(metric_name: str, observed_value: Any, ref_data: Dict[str, Any]) -> MetricAssessment:
    if observed_value is None:
        return MetricAssessment(
            metric=metric_name,
            observed_value=None,
            status="unknown",
            risk="undetermined",
            reason="Value is missing.",
            reference=None,
            evidence=None
        )

    if not ref_data:
        return MetricAssessment(
            metric=metric_name,
            observed_value=observed_value,
            status="context_dependent",
            risk="undetermined",
            reason="No authoritative reference available.",
            reference=None,
            evidence=None
        )

    ref_type = ref_data.get("reference_type")
    unit = ref_data.get("unit")
    evidence = _build_evidence(ref_data) if ref_data.get("source") else None
    ref_context = _build_reference_context(ref_data)

    if metric_name == "moisture":
        try:
            m_val = float(observed_value)
            if m_val < 0.0 or m_val > 100.0:
                return MetricAssessment(
                    metric=metric_name,
                    observed_value=None,
                    unit="%",
                    status="unknown",
                    risk="undetermined",
                    reason="Invalid soil moisture observation (must be between 0% and 100%).",
                    reference=ref_context,
                    evidence=evidence
                )
        except (ValueError, TypeError):
            pass

    if ref_type == "context_dependent":
        return MetricAssessment(
            metric=metric_name,
            observed_value=observed_value,
            unit=unit,
            status="context_dependent",
            risk="undetermined",
            reason="A meaningful interpretation requires local contextual information.",
            reference=ref_context,
            evidence=evidence
        )

    if ref_type == "categorical":
        ref_values = ref_data.get("reference_values", {})
        val_key = str(observed_value).lower().strip()
        
        match = ref_values.get(val_key)
        if not match:
            for k, v in ref_values.items():
                if val_key in k or k in val_key:
                    match = v
                    break
                    
        if match:
            return MetricAssessment(
                metric=metric_name,
                observed_value=observed_value,
                unit=unit,
                status=match.get("status", "unknown"),
                risk=match.get("risk", "undetermined"),
                reason=match.get("reason"),
                reference=ref_context,
                evidence=evidence
            )
        elif observed_value is not None and str(observed_value).strip() != "":
            return MetricAssessment(
                metric=metric_name,
                observed_value=observed_value,
                unit=unit,
                status="context_dependent",
                risk="undetermined",
                reason="Observed value requires local contextual evaluation.",
                reference=ref_context,
                evidence=evidence
            )
        else:
            return MetricAssessment(
                metric=metric_name,
                observed_value=observed_value,
                unit=unit,
                status="unknown",
                risk="undetermined",
                reason="Value is missing.",
                reference=ref_context,
                evidence=evidence
            )

    if ref_type == "range":
        try:
            val = float(observed_value)
            ref_values = ref_data.get("reference_values", {})
            min_val = ref_values.get("minimum")
            max_val = ref_values.get("maximum")
            
            status = "normal"
            reason = "Observed value is within the configured reference range."
            risk = "none_identified"
            
            if min_val is not None and val < min_val:
                status = "low"
                reason = "Observed value is below the selected reference range."
                risk = "potential_constraint"
                if "soil" in metric_name or "carbon" in metric_name:
                    risk = "potential_soil_constraint"
                    
            elif max_val is not None and val > max_val:
                status = "high"
                reason = "Observed value is above the selected reference range."
                risk = "potential_constraint"

            return MetricAssessment(
                metric=metric_name,
                observed_value=observed_value,
                unit=unit,
                status=status,
                risk=risk,
                reason=reason,
                reference=ref_context,
                evidence=evidence
            )
        except (ValueError, TypeError):
            return MetricAssessment(
                metric=metric_name,
                observed_value=observed_value,
                unit=unit,
                status="unknown",
                risk="undetermined",
                reason="Invalid numeric value for range evaluation.",
                reference=ref_context,
                evidence=evidence
            )

    # Fallback
    return MetricAssessment(
        metric=metric_name,
        observed_value=observed_value,
        unit=unit,
        status="unknown",
        risk="undetermined",
        reason="Unsupported reference type.",
        reference=ref_context,
        evidence=evidence
    )
