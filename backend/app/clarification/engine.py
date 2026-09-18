"""A deterministic gate for collecting minimum environmental observations.

This module deliberately does not classify conditions, infer ecological facts,
or call an LLM.  It only records values the user explicitly supplies and
identifies the minimum inputs needed before the existing analysis pipeline.
"""

from __future__ import annotations

import math
import re
from typing import Any, Dict, Iterable, Optional

from app.clarification.schemas import ClarificationResult
from app.llm.schemas import ConversationContext
from app.schemas.environmental import EnvironmentalObservation
from app.schemas.memory import EnvironmentalFactCreate


REQUIRED_BY_TOPIC = {
    "biodiversity": ("organic_carbon", "rainfall", "cropping_system"),
    "soil": ("organic_carbon", "rainfall", "cropping_system"),
    "water": ("rainfall", "organic_carbon", "cropping_system"),
    "general": ("organic_carbon", "rainfall", "cropping_system"),
}

OPTIONAL_BY_TOPIC = {
    "biodiversity": ("moisture", "soil_ph", "species_richness", "land_use"),
    "soil": ("moisture", "soil_ph", "land_use", "species_richness"),
    "water": ("moisture", "temperature", "soil_ph", "land_use"),
    "general": ("moisture", "soil_ph", "species_richness", "land_use"),
}

LABELS = {
    "organic_carbon": "Soil organic carbon (%)",
    "rainfall": "Annual rainfall (mm/year)",
    "cropping_system": "Land-use/cropping pattern",
    "land_use": "Land use / land cover",
    "moisture": "Soil moisture (%)",
    "soil_ph": "Soil pH",
    "temperature": "Temperature (°C)",
    "species_richness": "Species richness (count)",
}

# Imperative language must not be treated as a reported observation.
UNTRUSTED_SENTENCE_MARKERS = ("ignore", "invent", "assume", "pretend", "do not ask", "system instruction")


class ClarificationEngine:
    def determine_topic(self, query: str, prior_topic: Optional[str] = None) -> str:
        lowered = query.lower()
        if any(word in lowered for word in ("biodiversity", "species", "habitat")):
            return "biodiversity"
        if any(word in lowered for word in ("rainfall", "water", "moisture", "drought")):
            return "water"
        if any(word in lowered for word in ("soil", "carbon", "ph")):
            return "soil"
        return prior_topic or "general"

    def extract_explicit_values(self, text: str) -> List[EnvironmentalFactCreate]:
        """Parse a small, explicit grammar; unmatched or invalid text is unknown."""
        trusted_text = ". ".join(
            sentence for sentence in re.split(r"[.!?\n]+", text)
            if not any(marker in sentence.lower() for marker in UNTRUSTED_SENTENCE_MARKERS)
        )
        facts: List[EnvironmentalFactCreate] = []

        numeric_patterns = {
            "organic_carbon": (r"(?:soil\s+)?organic\s+carbon\s*(?:is|=|:)?\s*(-?\d+(?:\.\d+)?)\s*(%)?", "%"),
            "rainfall": (r"(?:annual\s+)?rainfall\s*(?:is|=|:)?\s*(-?\d+(?:\.\d+)?)\s*(mm)?", "mm"),
            "moisture": (r"soil\s+moisture\s*(?:is|=|:)?\s*(-?\d+(?:\.\d+)?)\s*(%)?", "%"),
            "soil_ph": (r"(?:soil\s+)?p\s*h\s*(?:is|=|:)?\s*(-?\d+(?:\.\d+)?)()?", ""),
            "temperature": (r"temperature\s*(?:is|=|:)?\s*(-?\d+(?:\.\d+)?)\s*(°?c)?", "C"),
            "species_richness": (r"(?:species\s+richness|richness)\s*(?:is|=|:)?\s*(\d+)\s*(species)?", "count"),
        }
        for variable, (pattern, default_unit) in numeric_patterns.items():
            match = re.search(pattern, trusted_text, flags=re.IGNORECASE)
            if not match:
                continue
            value = float(match.group(1))
            unit_match = match.group(2)
            if math.isfinite(value) and value >= 0 and (variable != "soil_ph" or value <= 14):
                val = int(value) if variable == "species_richness" else value
                facts.append(EnvironmentalFactCreate(
                    variable=variable,
                    value=val,
                    unit=unit_match.strip() if unit_match else default_unit
                ))

        crop_match = re.search(r"(?:cropping\s+system|cropping\s+pattern)\s*(?:is|=|:)?\s*([a-z][a-z -]+)", trusted_text, re.I)
        if crop_match:
            facts.append(EnvironmentalFactCreate(variable="cropping_system", value=crop_match.group(1).strip().rstrip(".,")))
        elif re.search(r"\bmonoculture\b", trusted_text, re.I):
            facts.append(EnvironmentalFactCreate(variable="cropping_system", value="monoculture"))

        land_match = re.search(r"land\s+use\s*(?:is|=|:)?\s*([a-z][a-z -]+)", trusted_text, re.I)
        if land_match:
            facts.append(EnvironmentalFactCreate(variable="land_use", value=land_match.group(1).strip().rstrip(".,")))
            
        return facts

    def evaluate(
        self,
        query: str,
        profile: Optional[Any] = None,
        conversation_context: Optional[ConversationContext] = None,
    ) -> tuple[ClarificationResult, List[EnvironmentalFactCreate], str]:
        topic = self.determine_topic(query, conversation_context.last_topic if conversation_context else None)
        known = self._profile_values(profile)
        if conversation_context:
            known.update(conversation_context.clarification_values)
        extracted = self.extract_explicit_values(query)
        known.update({fact.variable: fact.value for fact in extracted})

        required = REQUIRED_BY_TOPIC[topic]
        missing = [variable for variable in required if not self._is_valid(variable, known.get(variable))]
        optional = [variable for variable in OPTIONAL_BY_TOPIC[topic] if variable not in known]
        if not missing:
            return ClarificationResult(needs_clarification=False), extracted, topic

        required_lines = "\n".join(f"{index}. {LABELS[variable]}" for index, variable in enumerate(missing, start=1))
        optional_lines = "\n".join(f"• {LABELS[variable]}" for variable in optional)
        question = f"To assess the likely environmental drivers, please provide:\n\n{required_lines}"
        if optional_lines:
            question += f"\n\nOptional:\n{optional_lines}"
        return ClarificationResult(
            needs_clarification=True,
            missing_required=missing,
            optional_variables=optional,
            question=question,
            reason="The available observations do not yet contain the minimum inputs for multi-metric environmental reasoning.",
        ), extracted, topic

    def overlay_profile(self, profile: Any, values: Dict[str, Any]) -> EnvironmentalObservation:
        """Use explicit conversation values for this request without persisting or inventing data."""
        payload = EnvironmentalObservation.model_validate(profile).model_dump(by_alias=True)
        for variable, value in values.items():
            section, field = {
                "organic_carbon": ("soil", "organic_carbon"),
                "moisture": ("soil", "moisture"),
                "soil_ph": ("soil", "ph"),
                "rainfall": ("climate", "rainfall"),
                "temperature": ("climate", "temperature"),
                "cropping_system": ("land", "cropping_system"),
                "land_use": ("land", "use"),
                "species_richness": ("biodiversity", "species_richness"),
            }.get(variable, (None, None))
            if section:
                payload[section] = payload.get(section) or {}
                payload[section][field] = value
        return EnvironmentalObservation.model_validate(payload)

    def _profile_values(self, profile: Optional[Any]) -> Dict[str, Any]:
        if profile is None:
            return {}
        values: Dict[str, Any] = {}
        for section, fields in {
            "soil": ("organic_carbon", "moisture", "soil_ph"),
            "climate": ("rainfall", "temperature"),
            "land": ("cropping_system", "land_use"),
            "biodiversity": ("species_richness",),
        }.items():
            group = getattr(profile, section, None) if not isinstance(profile, dict) else profile.get(section)
            for field in fields:
                if isinstance(group, dict):
                    value = group.get(field, group.get("ph") if field == "soil_ph" else group.get("use") if field == "land_use" else None)
                else:
                    value = getattr(group, field, None) if group is not None else None
                canonical = "soil_ph" if field == "soil_ph" else field
                if self._is_valid(canonical, value):
                    values[canonical] = value
        return values

    @staticmethod
    def _is_valid(variable: str, value: Any) -> bool:
        if value is None or isinstance(value, bool):
            return False
        if variable in {"cropping_system", "land_use"}:
            return isinstance(value, str) and bool(value.strip())
        return isinstance(value, (int, float)) and math.isfinite(value) and value >= 0 and (variable != "soil_ph" or value <= 14)
