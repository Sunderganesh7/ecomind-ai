import re
from typing import Dict, Any, List, Optional
from app.llm.schemas import ConversationContext
from app.context_engine.schemas import ContextualizedQuery

class ContextEngine:
    def __init__(self):
        # Deterministic intent detection heuristics
        self.intent_patterns = {
            "biodiversity": re.compile(r"\b(biodiversity|species|habitat|wildlife)\b", re.IGNORECASE),
            "soil": re.compile(r"\b(soil|carbon|soc|ph|moisture|earth|dirt|organic carbon)\b", re.IGNORECASE),
            "climate": re.compile(r"\b(climate|temperature|rainfall|weather|heat)\b", re.IGNORECASE),
            "water": re.compile(r"\b(water|moisture|rainfall|drought|irrigation)\b", re.IGNORECASE),
            "land_use": re.compile(r"\b(land\s*use|agriculture|forest|urban|pasture)\b", re.IGNORECASE),
            "cropping_system": re.compile(r"\b(crop|monocropping|monoculture|intercropping|rotation|farming)\b", re.IGNORECASE),
            "pollution": re.compile(r"\b(pollution|chemicals|fertilizer|pesticides|toxic)\b", re.IGNORECASE),
            "deforestation": re.compile(r"\b(deforestation|logging|tree\s*loss|clearing|trees)\b", re.IGNORECASE),
            "intervention": re.compile(r"\b(recommendation|intervention|action|solution|should\s+i\s+do|fix|mitigate)\b", re.IGNORECASE),
            "evidence": re.compile(r"\b(evidence|scientific|research|study|studies|papers|prove|literature|support)\b", re.IGNORECASE),
            "risk": re.compile(r"\b(risk|threat|danger|vulnerability|pressure)\b", re.IGNORECASE),
            "metrics": re.compile(r"\b(metric|metrics|measurement|measure|indicator)\b", re.IGNORECASE),
            "reasoning": re.compile(r"\b(reasoning|trace|logic|why\b.*\b(this|important|low|high))\b", re.IGNORECASE),
            "follow_up_context": re.compile(r"\b(what\s+about\b|how\s+does\b.*affect|and\b)\b", re.IGNORECASE),
        }

    def _extract_active_variables(self, profile: Any) -> List[str]:
        variables = []
        if not profile:
            return variables
            
        if isinstance(profile, dict):
            for category, data in profile.items():
                if isinstance(data, dict):
                    for key, val in data.items():
                        if val is not None and key not in ["id", "latitude", "longitude"]:
                            variables.append(key)
        elif hasattr(profile, "id"):
            for section in ["soil", "climate", "land", "biodiversity", "human_impact"]:
                value = getattr(profile, section, None)
                if value is None:
                    continue
                fields = {
                    "soil": ("soil_ph", "organic_carbon", "moisture"),
                    "climate": ("rainfall", "temperature"),
                    "land": ("land_use", "crop", "cropping_system"),
                    "biodiversity": ("species_richness", "habitat_diversity"),
                    "human_impact": ("pollution", "deforestation"),
                }.get(section, ())
                for field in fields:
                    if getattr(value, field, None) is not None:
                        variables.append(field)
        return variables

    def resolve_query(self, query: str, context: ConversationContext, profile: Any) -> ContextualizedQuery:
        intent = "general_environment"
        resolved_query = query
        retrieval_query = query
        clarification_req = False
        clarification_msg = None
        referenced_topics = []
        confidence = "medium"
        
        lower_query = query.lower().strip().rstrip('?')
        
        # Determine all matching intents
        matched_intents = []
        for int_name, pattern in self.intent_patterns.items():
            if pattern.search(lower_query):
                matched_intents.append(int_name)
                
        if not matched_intents:
            intent = "general_environment"
        else:
            # Priority resolution
            if "intervention" in matched_intents:
                intent = "intervention"
            elif "evidence" in matched_intents:
                intent = "evidence"
            elif "reasoning" in matched_intents:
                intent = "reasoning"
            elif "metrics" in matched_intents:
                intent = "metrics"
            elif "follow_up_context" in matched_intents:
                intent = "follow_up_context"
                # If they asked "what about biodiversity", we should also capture the topical intent
                topical = [i for i in matched_intents if i not in ["follow_up_context", "intervention", "evidence", "reasoning", "metrics"]]
                if topical:
                    intent = topical[0] # Promote the topical intent so the filter knows what to focus on
            else:
                # Just take the first topical match
                intent = matched_intents[0]
                
            # Keep track of all topics for filtering
            topical_intents = [i for i in matched_intents if i not in ["follow_up_context", "intervention", "evidence", "reasoning", "metrics"]]
            for t in topical_intents:
                referenced_topics.append(t)
                
        # If it's an intervention query, but they also mentioned a topic (e.g. monocropping), add it to referenced topics
        if intent == "intervention":
            for t in [i for i in matched_intents if i not in ["intervention", "evidence", "reasoning", "metrics", "follow_up_context"]]:
                if t not in referenced_topics:
                    referenced_topics.append(t)

        # 2. Variable Preservation
        active_vars = self.extract_active_variables(profile)
        
        # 3. Contextual Resolution
        messages_used = []
        previous_entities = []
        
        last_rec = context.last_recommendation_id
        last_topic = context.last_topic
        
        if last_rec:
            previous_entities.append(last_rec)
        if last_topic:
            previous_entities.append(last_topic)
            
        # Refine retrieval query and confidence based on intent
        if intent == "follow_up_context":
            if active_vars and referenced_topics:
                var_str = ", ".join(active_vars)
                resolved_query = f"How does {referenced_topics[0]} relate to the current environmental conditions ({var_str})?"
                retrieval_query = f"relationship between {var_str} and {referenced_topics[0]}"
                confidence = "high"
            elif last_topic and not referenced_topics:
                if last_rec and not active_vars:
                    # Ambiguous reference (like "What about that?")
                    clarification_req = True
                    clarification_msg = f"Are you asking about the recommendation ({last_rec}) or the topic ({last_topic})?"
                else:
                    resolved_query = f"What about {last_topic}?"
                    retrieval_query = f"{last_topic} analysis"
                    confidence = "medium"
            else:
                clarification_req = True
                clarification_msg = "I'm not sure what you're referring to. Could you clarify?"
                
        elif intent == "evidence":
            retrieval_query = f"scientific evidence for {', '.join(referenced_topics) if referenced_topics else 'environmental conditions'}"
            confidence = "high"
            
        elif intent == "reasoning":
            if last_rec and not referenced_topics:
                intent = "recommendation_explanation"
                resolved_query = f"Why does {last_rec} help?"
                confidence = "high"
            else:
                retrieval_query = f"ecological mechanism for {', '.join(referenced_topics) if referenced_topics else 'current conditions'}"
                confidence = "high"
            
        elif intent == "intervention":
            topic_str = referenced_topics[0] if referenced_topics else "current profile"
            resolved_query = f"What intervention is recommended for {topic_str}?"
            retrieval_query = f"interventions and solutions for {topic_str}"
            confidence = "high"
            
        elif referenced_topics:
            retrieval_query = f"environmental impact of {', '.join(referenced_topics)}"
            confidence = "high"
            if active_vars:
                intent = f"{intent}_analysis"
            else:
                intent = "general_information"
                
        if intent == "general_environment":
            if active_vars:
                resolved_query = f"{query} (Context: {', '.join(active_vars)})"
            else:
                intent = "general_information"
            retrieval_query = query
            confidence = "medium"

        return ContextualizedQuery(
            original_query=query,
            resolved_query=resolved_query,
            query_intent=intent,
            referenced_topics=referenced_topics,
            referenced_variables=active_vars,
            conversation_context={
                "messages_used": messages_used,
                "previous_entities": previous_entities
            },
            retrieval_query=retrieval_query,
            context_confidence=confidence,
            clarification_required=clarification_req,
            clarification_question=clarification_msg
        )

    def extract_active_variables(self, profile: Any) -> List[str]:
        return self._extract_active_variables(profile)
