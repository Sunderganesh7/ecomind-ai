import pytest
from app.context_engine.engine import ContextEngine
from app.llm.schemas import ConversationContext

def test_intent_follow_up():
    engine = ContextEngine()
    context = ConversationContext(conversation_id="123", last_recommendation_id="legume_intercropping")
    profile = {}
    
    q = engine.resolve_query("Why does it help?", context, profile)
    assert q.query_intent == "recommendation_explanation"
    assert q.context_confidence == "high"
    assert "legume_intercropping" in q.resolved_query

def test_ambiguous_reference():
    engine = ContextEngine()
    context = ConversationContext(conversation_id="123", last_recommendation_id="legume_intercropping", last_topic="soil moisture")
    profile = {}
    
    q = engine.resolve_query("What about that?", context, profile)
    assert q.clarification_required is True
    assert "legume_intercropping" in q.clarification_question
    assert "soil moisture" in q.clarification_question

def test_contextual_analysis_with_vars():
    engine = ContextEngine()
    context = ConversationContext(conversation_id="123")
    profile = {
        "soil": {"organic_carbon": 0.3},
        "climate": {"rainfall": 500},
        "land": {"cropping_system": "monoculture"}
    }
    
    q = engine.resolve_query("What about biodiversity?", context, profile)
    assert q.query_intent == "biodiversity_analysis"
    assert "organic_carbon" in q.referenced_variables
    assert "rainfall" in q.referenced_variables
    assert "organic_carbon" in q.retrieval_query
    assert "biodiversity" in q.retrieval_query
    assert q.context_confidence == "high"

def test_general_query():
    engine = ContextEngine()
    context = ConversationContext(conversation_id="123")
    profile = {}
    
    q = engine.resolve_query("What is biodiversity?", context, profile)
    assert q.query_intent == "general_information"
    assert q.retrieval_query == "What is biodiversity?"
