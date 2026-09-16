import pytest
import os
import shutil
from backend.app.rag.store.chroma_store import ChromaKnowledgeStore
from backend.app.rag.embeddings.embedding_service import EmbeddingService

@pytest.fixture(scope="module")
def chroma_store(tmp_path_factory):
    # Use a temporary directory for tests
    temp_dir = tmp_path_factory.mktemp("chroma_test")
    store = ChromaKnowledgeStore(persist_directory=str(temp_dir), collection_name="test_collection")
    yield store
    # Cleanup after tests
    shutil.rmtree(str(temp_dir), ignore_errors=True)

@pytest.fixture(scope="module")
def embedding_service():
    return EmbeddingService()

def test_store_initializes(chroma_store):
    assert chroma_store is not None
    assert chroma_store.collection is not None
    assert chroma_store.collection_name == "test_collection"

def test_metadata_preservation(chroma_store):
    chunk = {
        "chunk_id": "test_chunk_001",
        "source_id": "test_doc",
        "title": "Test Document",
        "year": 2024,
        "topic": "soil_health",
        "variables": ["organic_carbon", "biodiversity"],
        "document_id": "doc_001",
        "text": "Soil organic carbon influences biological processes.",
        "embedding": [0.1] * 384
    }
    
    chroma_store.upsert_chunks([chunk])
    
    # Verify status
    status = chroma_store.get_status()
    assert status["count"] >= 1
    
    # Retrieve and verify metadata
    results = chroma_store.collection.get(ids=["test_chunk_001"], include=["metadatas"])
    assert len(results["ids"]) == 1
    meta = results["metadatas"][0]
    
    assert meta["source_id"] == "test_doc"
    assert meta["title"] == "Test Document"
    assert meta["year"] == 2024
    assert meta["topic"] == "soil_health"
    assert meta["variables"] == "organic_carbon|biodiversity" # Joined list
    assert meta["document_id"] == "doc_001"
    
def test_idempotent_indexing(chroma_store):
    chunk = {
        "chunk_id": "test_chunk_002",
        "text": "Rainfall influences water availability.",
        "embedding": [0.2] * 384
    }
    
    initial_count = chroma_store.get_status()["count"]
    
    # Insert once
    chroma_store.upsert_chunks([chunk])
    count_after_first = chroma_store.get_status()["count"]
    assert count_after_first == initial_count + 1
    
    # Insert twice
    chroma_store.upsert_chunks([chunk])
    count_after_second = chroma_store.get_status()["count"]
    assert count_after_second == count_after_first # Should not increase

def test_semantic_search(chroma_store, embedding_service):
    # Add controlled documents
    docs = [
        {"chunk_id": "doc_a", "text": "Soil organic carbon contributes to soil biological activity...", "topic": "soil_health"},
        {"chunk_id": "doc_b", "text": "Rainfall influences water availability...", "topic": "water_cycle"},
        {"chunk_id": "doc_c", "text": "Habitat fragmentation can affect species richness...", "topic": "biodiversity"}
    ]
    
    # Generate real embeddings for search test
    for doc in docs:
        doc["embedding"] = embedding_service.embed_chunk(doc["text"])
        
    chroma_store.upsert_chunks(docs)
    
    query = "soil carbon and biodiversity"
    query_emb = embedding_service.embed_chunk(query)
    
    results = chroma_store.search(query_emb, top_k=2)
    
    assert len(results) == 2
    # The first result should logically be the soil organic carbon one given the query
    assert "Soil organic carbon" in results[0]["text"]
    assert results[0]["chunk_id"] == "doc_a"
    assert results[0]["topic"] == "soil_health"
    
    # Ensure relevance is calculated
    assert "relevance" in results[0]
    assert isinstance(results[0]["relevance"], float)

def test_provenance(chroma_store):
    chunk = {
        "chunk_id": "prov_chunk_001",
        "source": "FAO",
        "document_id": "doc_prov",
        "page_number": 42,
        "section": "Methods",
        "text": "Provenance test text",
        "embedding": [0.3] * 384
    }
    
    chroma_store.upsert_chunks([chunk])
    
    results = chroma_store.search([0.3] * 384, top_k=10)
    
    match = next((r for r in results if r.get("chunk_id") == "prov_chunk_001"), None)
    assert match is not None
    assert match["source"] == "FAO"
    assert match["document_id"] == "doc_prov"
    assert match["page_number"] == 42
    assert match["section"] == "Methods"
