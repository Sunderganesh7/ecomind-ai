import json
import os
import hashlib
from pathlib import Path

CHUNKS_FILE = "knowledge_base/processed/chunks/knowledge_chunks.jsonl"
SOURCES_DIR = "knowledge_base/sources"
METADATA_DIR = "knowledge_base/metadata"

def audit():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = [json.loads(line) for line in f]
        
    for i, c in enumerate(chunks):
        print(f"Chunk {i}:")
        print(f"  ID: {c.get('chunk_id')}")
        print(f"  Source: {c.get('source_id')} -> {c.get('url')}")
        print(f"  Page: {c.get('page_number')}")
        print(f"  Text: {c.get('text')[:50]}...")
        
    # Check determinism
    # Run the pipeline again to a temp directory and compare
    # Actually, we can just hash the chunk text + metadata as per pipeline and see if it matches
    c = chunks[0]
    unique_string = f"{c['document_id']}_{c['page_number']}_0_{c['text'][:50]}"
    expected_hash = hashlib.sha256(unique_string.encode('utf-8')).hexdigest()[:12]
    expected_id = f"{c['document_id']}_p{c['page_number']:03d}_c000_{expected_hash}"
    
    print(f"\nExpected ID: {expected_id}")
    print(f"Actual ID:   {c['chunk_id']}")
    print(f"Deterministic: {expected_id == c['chunk_id']}")

if __name__ == "__main__":
    audit()
