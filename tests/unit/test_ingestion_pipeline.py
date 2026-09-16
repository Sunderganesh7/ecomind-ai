import os
import json
import pytest
from pathlib import Path
from backend.app.rag.ingestion.extractor import DocumentExtractor
from backend.app.rag.ingestion.cleaner import TextCleaner
from backend.app.rag.ingestion.chunker import TextChunker
from backend.app.rag.ingestion.metadata import MetadataAttacher
from backend.app.rag.ingestion.pipeline import IngestionPipeline

# Test Data
DUMMY_DOC = {
    "file_path": "dummy.txt",
    "file_type": ".txt",
    "source_id": "fao_soil_001",
    "metadata": {
        "organization": "FAO",
        "title": "Soil Report",
        "publication_year": 2024,
        "topics": ["soil_health"],
        "variables": ["organic_carbon"]
    }
}

class DummyLoader:
    def __init__(self):
        self.relationship_matrix = []

def test_extraction_and_page_provenance(tmp_path):
    # Test 1 & 5: Text extraction & Page provenance
    test_txt = tmp_path / "fao_soil_001.txt"
    test_txt.write_text("Page 1 text\n\nPage 2 text", encoding="utf-8")
    
    extractor = DocumentExtractor()
    doc_info = dict(DUMMY_DOC)
    doc_info["file_path"] = str(test_txt)
    
    result = extractor.extract(doc_info)
    assert len(result["pages"]) == 2
    assert result["pages"][0]["page_number"] is None
    assert result["pages"][0]["text"] == "Page 1 text"
    assert result["pages"][1]["page_number"] is None
    assert result["pages"][1]["text"] == "Page 2 text"

def test_cleaning():
    # Test 2: Cleaning
    cleaner = TextCleaner()
    raw = "Scientific   text   with \n multiple \n\n spaces."
    cleaned = cleaner.clean(raw)
    assert cleaned == "Scientific text with multiple\n\nspaces."

def test_chunking():
    # Test 3: Chunking
    chunker = TextChunker(chunk_size_words=10, chunk_overlap_words=2)
    doc_cleaned = {
        "source_id": "test_id",
        "pages": [
            {"page_number": 1, "section": None, "text": "This is a very long paragraph that needs to be chunked properly to preserve context."}
        ]
    }
    chunks = chunker.chunk_document(doc_cleaned)
    assert len(chunks) > 1
    assert chunks[0]["page_number"] == 1
    
def test_metadata_and_coverage_preservation():
    # Test 4, 6, 9: Metadata, Source integration, Coverage preservation
    attacher = MetadataAttacher(DummyLoader())
    raw_chunks = [{"chunk_index": 0, "page_number": 1, "section": None, "text": "Sample text"}]
    
    final_chunks = attacher.attach(raw_chunks, DUMMY_DOC)
    chunk = final_chunks[0]
    
    assert "chunk_id" in chunk
    assert chunk["document_id"] == "fao_soil_001"
    assert chunk["source"] == "FAO"
    assert chunk["title"] == "Soil Report"
    assert "soil_health" in chunk["topics"]
    assert "organic_carbon" in chunk["variables"]
    assert chunk["text"] == "Sample text"

def test_duplicate_detection_and_idempotency(tmp_path):
    # Test 7: Duplicate detection (running twice replaces or is deterministic)
    sources_dir = tmp_path / "sources"
    metadata_dir = tmp_path / "metadata"
    output_dir = tmp_path / "processed" / "chunks"
    
    sources_dir.mkdir()
    metadata_dir.mkdir(parents=True)
    
    # create dummy sources.json
    (metadata_dir / "sources.json").write_text("[]", encoding="utf-8")
    (metadata_dir / "coverage_matrix.json").write_text("{}", encoding="utf-8")
    (metadata_dir / "relationship_matrix.json").write_text("[]", encoding="utf-8")
    
    (sources_dir / "fao_test.txt").write_text("Test content", encoding="utf-8")
    
    pipeline = IngestionPipeline(str(sources_dir), str(metadata_dir), str(output_dir))
    
    # Run once
    pipeline.run()
    first_run_chunks = len(open(output_dir / "knowledge_chunks.jsonl").readlines())
    
    # Run twice
    pipeline.run()
    second_run_chunks = len(open(output_dir / "knowledge_chunks.jsonl").readlines())
    
    assert first_run_chunks == second_run_chunks

def test_failure_handling(tmp_path):
    # Test 8: Failure handling
    sources_dir = tmp_path / "sources"
    metadata_dir = tmp_path / "metadata"
    output_dir = tmp_path / "processed" / "chunks"
    
    sources_dir.mkdir()
    metadata_dir.mkdir(parents=True)
    
    # Empty TXT file
    (sources_dir / "empty.txt").write_text("", encoding="utf-8")
    
    pipeline = IngestionPipeline(str(sources_dir), str(metadata_dir), str(output_dir))
    pipeline.run()
    
    manifest_path = tmp_path / "processed" / "manifest.json"
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    
    assert len(manifest["failed_documents"]) == 1
    assert manifest["failed_documents"][0]["file"] == "empty.txt"
    assert manifest["failed_documents"][0]["reason"] == "No extractable text found"
