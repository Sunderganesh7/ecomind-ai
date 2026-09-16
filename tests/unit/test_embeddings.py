import os
import json
import pytest
import math
from pathlib import Path
from backend.app.rag.embeddings.embedding_service import EmbeddingService
from backend.app.rag.embeddings.generator import EmbeddingGenerator

# Use a small test fixture to prevent hitting the real files during isolated unit tests,
# but we will also verify real behavior.

@pytest.fixture(scope="module")
def embedding_service():
    service = EmbeddingService()
    # Loading might take a moment if it needs to download, but usually cached
    service.load_model()
    return service

def test_service_initializes(embedding_service):
    assert embedding_service is not None
    assert embedding_service._model is not None

def test_embedding_dimension(embedding_service):
    dim = embedding_service.dimension
    assert dim == 384

def test_embed_one_chunk(embedding_service):
    text = "Soil organic carbon increases with agroforestry."
    embedding = embedding_service.embed_chunk(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) == 384
    assert all(isinstance(v, float) for v in embedding)
    assert all(math.isfinite(v) for v in embedding)

def test_embed_multiple_chunks(embedding_service):
    texts = [
        "Soil organic carbon increases with agroforestry.",
        "Rainfall dictates water stress levels."
    ]
    embeddings = embedding_service.embed_chunks(texts)
    
    assert isinstance(embeddings, list)
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384

def test_reproducibility(embedding_service):
    text = "Consistent input yields consistent output."
    emb1 = embedding_service.embed_chunk(text)
    emb2 = embedding_service.embed_chunk(text)
    
    # Should be identical
    for v1, v2 in zip(emb1, emb2):
        assert math.isclose(v1, v2, rel_tol=1e-5)

def test_generator_preserves_metadata_and_provenance(tmp_path):
    # Create dummy JSONL chunks
    chunks_file = tmp_path / "test_chunks.jsonl"
    output_dir = tmp_path / "embeddings"
    
    dummy_chunk = {
        "chunk_id": "test_doc_null_c000_abc123",
        "source_id": "test_doc",
        "title": "Test Title",
        "year": 2024,
        "url": "http://test",
        "page_number": None,
        "topic": "soil_health",
        "topics": ["soil_health"],
        "relationships": ["test_rel"],
        "text": "This is a test chunk."
    }
    
    with open(chunks_file, "w") as f:
        f.write(json.dumps(dummy_chunk) + "\n")
        
    generator = EmbeddingGenerator(str(chunks_file), str(output_dir))
    generator.generate()
    
    emb_file = output_dir / "knowledge_embeddings.jsonl"
    assert emb_file.exists()
    
    with open(emb_file, "r") as f:
        records = [json.loads(line) for line in f]
        
    assert len(records) == 1
    record = records[0]
    
    # Verify provenance and metadata is 100% intact
    assert record["chunk_id"] == dummy_chunk["chunk_id"]
    assert record["source_id"] == dummy_chunk["source_id"]
    assert record["title"] == dummy_chunk["title"]
    assert record["year"] == dummy_chunk["year"]
    assert record["url"] == dummy_chunk["url"]
    assert record["page_number"] == dummy_chunk["page_number"]
    assert record["topic"] == dummy_chunk["topic"]
    assert record["relationships"] == dummy_chunk["relationships"]
    assert record["text"] == dummy_chunk["text"]
    
    # Verify embedding properties
    assert "embedding" in record
    assert len(record["embedding"]) == 384
    assert record["dimension"] == 384
