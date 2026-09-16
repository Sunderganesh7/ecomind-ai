import hashlib
from typing import List, Dict, Any

class MetadataAttacher:
    def __init__(self, loader_instance):
        self.loader = loader_instance

    def attach(self, raw_chunks: List[Dict[str, Any]], document_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        processed = []
        meta = document_info.get("metadata") or {}
        
        doc_id = document_info["source_id"]
        source_org = meta.get("organization")
        title = meta.get("title")
        year = meta.get("publication_year")
        source_type = meta.get("source_type")
        url = meta.get("url")
        topics = meta.get("topics", [])
        variables = meta.get("variables", [])
        interventions = meta.get("interventions", [])
        
        # Propagate relationships if they apply to this document
        relationships = []
        for rel in self.loader.relationship_matrix:
            if rel.get("supported") and doc_id in rel.get("source_ids", []):
                relationships.append(rel.get("relationship"))

        for chunk in raw_chunks:
            page_num = chunk.get('page_number')
            page_str = "null" if page_num is None else str(page_num)
            page_id_str = "null" if page_num is None else f"p{page_num:03d}"
            
            # Deterministic ID using SHA-256
            unique_string = f"{doc_id}_{page_str}_{chunk['chunk_index']}_{chunk['text'][:50]}"
            chunk_hash = hashlib.sha256(unique_string.encode('utf-8')).hexdigest()[:12]
            chunk_id = f"{doc_id}_{page_id_str}_c{chunk['chunk_index']:03d}_{chunk_hash}"
            
            processed_chunk = {
                "chunk_id": chunk_id,
                "document_id": doc_id,
                "source": source_org,
                "source_id": doc_id,
                "title": title,
                "authors": [],
                "year": year,
                "source_type": source_type,
                "url": url,
                "page_number": page_num,
                "section": chunk["section"],
                "topic": topics[0] if topics else None,  # primary topic mapping
                "topics": topics, # Keep the list for full context
                "variables": variables,
                "relationships": relationships,
                "interventions": interventions,
                "text": chunk["text"]
            }
            processed.append(processed_chunk)
            
        return processed
