import json
import os
import numpy as np

def verify():
    chunks_file = "knowledge_base/processed/chunks/knowledge_chunks.jsonl"
    embeds_file = "knowledge_base/processed/embeddings/knowledge_embeddings.jsonl"
    
    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = [json.loads(line) for line in f if line.strip()]
        
    with open(embeds_file, "r", encoding="utf-8") as f:
        embeds = [json.loads(line) for line in f if line.strip()]
        
    chunk_ids = {c["chunk_id"] for c in chunks}
    embed_chunk_ids = {e["chunk_id"] for e in embeds}
    
    missing = chunk_ids - embed_chunk_ids
    orphan = embed_chunk_ids - chunk_ids
    
    # duplicate check
    all_embed_ids = [e["chunk_id"] for e in embeds]
    duplicates = len(all_embed_ids) - len(embed_chunk_ids)
    
    # provenance validation
    prov_pass = True
    meta_pass = True
    for c in chunks:
        cid = c["chunk_id"]
        # find matching embed
        match = next((e for e in embeds if e["chunk_id"] == cid), None)
        if match:
            # check meta
            if c.get("source_id") != match.get("source_id"): meta_pass = False
            if c.get("title") != match.get("title"): meta_pass = False
            if c.get("topics") != match.get("topics"): meta_pass = False
            if c.get("page_number") != match.get("page_number"): meta_pass = False
            if c.get("text") != match.get("text"): prov_pass = False
            
    # dimension validation
    embed_val_pass = True
    for e in embeds:
        emb = e.get("embedding")
        if not emb: embed_val_pass = False
        elif len(emb) != 384: embed_val_pass = False
        elif not all(isinstance(v, (int, float)) and np.isfinite(v) for v in emb): embed_val_pass = False

    sources_present = list({c["source_id"] for c in chunks})

    print(f"Knowledge chunks: {len(chunks)}")
    print(f"Embedding records: {len(embeds)}")
    print(f"Unique chunk IDs: {len(chunk_ids)} -> {len(embed_chunk_ids)}")
    print(f"Missing embeddings: {len(missing)}")
    print(f"Orphan embeddings: {len(orphan)}")
    print(f"Duplicate embeddings: {duplicates}")
    print(f"Scientific sources represented: {sources_present}")
    print(f"Provenance: {'PASS' if prov_pass else 'FAIL'}")
    print(f"Metadata preservation: {'PASS' if meta_pass else 'FAIL'}")
    print(f"Embedding validation: {'PASS' if embed_val_pass else 'FAIL'}")

if __name__ == "__main__":
    verify()
