import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

from app.database.base import Base
from app.models.conversation import ConversationModel, MessageModel, EnvironmentalFactModel
from app.memory.manager import MemoryManager
from app.schemas.memory import EnvironmentalFactCreate
from app.llm.schemas import ConversationContext

# Setup In-Memory DB
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def memory_manager():
    return MemoryManager()

def test_memory_storage_and_retrieval(db, memory_manager):
    conv_id = "test-conv-1"
    
    # Storage
    context = memory_manager.get_or_create_context(db, conv_id)
    assert context.conversation_id == conv_id
    
    # Message Storage
    memory_manager.add_message(db, conv_id, "user", "Hello")
    memory_manager.add_message(db, conv_id, "assistant", "Hi there")
    
    # Retrieval
    context = memory_manager.get_or_create_context(db, conv_id)
    assert len(context.messages) == 2
    assert context.messages[0].role == "user"
    assert context.messages[1].role == "assistant"

def test_variable_extraction_and_reconstruction(db, memory_manager):
    conv_id = "test-conv-2"
    memory_manager.get_or_create_context(db, conv_id)
    msg = memory_manager.add_message(db, conv_id, "user", "Soil carbon is 1.5%")
    
    facts = [
        EnvironmentalFactCreate(variable="organic_carbon", value=1.5, unit="%")
    ]
    
    memory_manager.update_clarification(db, conv_id, msg.id, facts, "soil")
    
    context = memory_manager.get_or_create_context(db, conv_id)
    assert context.clarification_values["organic_carbon"] == 1.5
    assert context.last_topic == "soil"

def test_updates_and_conflicts(db, memory_manager):
    conv_id = "test-conv-3"
    memory_manager.get_or_create_context(db, conv_id)
    
    # Turn 1
    msg1 = memory_manager.add_message(db, conv_id, "user", "Rainfall is 400mm")
    facts1 = [EnvironmentalFactCreate(variable="rainfall", value=400, unit="mm")]
    memory_manager.update_clarification(db, conv_id, msg1.id, facts1, "water")
    
    context = memory_manager.get_or_create_context(db, conv_id)
    assert context.clarification_values["rainfall"] == 400
    
    # Turn 2: User corrects the value
    msg2 = memory_manager.add_message(db, conv_id, "user", "Actually rainfall is 500mm")
    facts2 = [EnvironmentalFactCreate(variable="rainfall", value=500, unit="mm")]
    memory_manager.update_clarification(db, conv_id, msg2.id, facts2, "water")
    
    # Reconstruction
    context2 = memory_manager.get_or_create_context(db, conv_id)
    assert context2.clarification_values["rainfall"] == 500
    
    # Verify provenance (both records exist, but one is historical)
    all_facts = db.query(EnvironmentalFactModel).filter_by(conversation_id=conv_id).all()
    assert len(all_facts) == 2
    active = [f for f in all_facts if f.status == "active"]
    assert len(active) == 1
    assert active[0].value == "500"

def test_profile_integration(db, memory_manager):
    conv_id = "test-conv-4"
    
    memory_manager.get_or_create_context(db, conv_id)
    memory_manager.set_active_profile(db, conv_id, "99")
    
    context = memory_manager.get_or_create_context(db, conv_id)
    assert context.active_profile_id == "99"
    
    memory_manager.switch_profile(db, conv_id, "100")
    context2 = memory_manager.get_or_create_context(db, conv_id)
    assert context2.active_profile_id == "100"

def test_memory_is_bounded_and_profile_scoped(db, memory_manager):
    from app.memory.manager import MAX_CONVERSATION_MESSAGES
    
    conv_id = "bounded-conv"
    context = memory_manager.get_or_create_context(db, conv_id)
    memory_manager.switch_profile(db, conv_id, "profile-a")
    for index in range(MAX_CONVERSATION_MESSAGES + 3):
        memory_manager.add_message(db, conv_id, "user", f"turn {index}")
        
    context_after = memory_manager.get_or_create_context(db, conv_id)
    assert len(context_after.messages) == MAX_CONVERSATION_MESSAGES
    
    memory_manager.switch_profile(db, conv_id, "profile-b")
    switched = memory_manager.get_or_create_context(db, conv_id)
    assert switched.active_profile_id == "profile-b"
    assert switched.messages == []

