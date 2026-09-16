import json
import os

KB_DIR = os.path.join(os.path.dirname(__file__), "../../knowledge_base/metadata")
SOURCES_PATH = os.path.join(KB_DIR, "sources.json")
COVERAGE_PATH = os.path.join(KB_DIR, "coverage_matrix.json")
RELATIONSHIP_PATH = os.path.join(KB_DIR, "relationship_matrix.json")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_sources_completeness_and_fabrication():
    sources = load_json(SOURCES_PATH)
    assert len(sources) >= 12, "Curated corpus should have a reasonable number of sources"
    
    source_ids = set()
    for s in sources:
        # Check required fields
        assert "source_id" in s
        assert "title" in s
        assert "organization" in s
        assert "source_type" in s
        assert "url" in s
        assert "topics" in s
        assert isinstance(s["topics"], list)
        
        # Check no duplicates
        assert s["source_id"] not in source_ids, f"Duplicate source ID: {s['source_id']}"
        source_ids.add(s["source_id"])
        
        # Check no placeholder URLs
        assert s["url"] and s["url"].startswith("http"), f"Invalid or missing URL for {s['source_id']}"
        assert "OFFICIAL_SOURCE_URL" not in s["url"], "Placeholder URL detected"

def test_coverage_matrix_valid_sources():
    sources = load_json(SOURCES_PATH)
    coverage = load_json(COVERAGE_PATH)
    
    valid_source_ids = {s["source_id"] for s in sources}
    
    # Check that required concepts exist
    required_concepts = ["soil_health", "organic_carbon", "biodiversity", "species_richness", "temperature", "rainfall", "deforestation"]
    for concept in required_concepts:
        assert concept in coverage, f"Missing required concept in coverage matrix: {concept}"
        
    for concept, source_list in coverage.items():
        for source_id in source_list:
            assert source_id in valid_source_ids, f"Coverage matrix references unknown source ID: {source_id}"

def test_relationship_matrix_valid_sources():
    sources = load_json(SOURCES_PATH)
    relationships = load_json(RELATIONSHIP_PATH)
    
    valid_source_ids = {s["source_id"] for s in sources}
    
    for rel in relationships:
        assert "relationship" in rel
        assert "supported" in rel
        assert "source_ids" in rel
        assert "notes" in rel
        
        assert rel["supported"] is True, "Only supported relationships should be listed based on corpus"
        assert len(rel["source_ids"]) > 0, f"Relationship '{rel['relationship']}' has no source IDs"
        
        for source_id in rel["source_ids"]:
            assert source_id in valid_source_ids, f"Relationship matrix references unknown source ID: {source_id}"
