import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from app.rag.store.chroma_store import ChromaKnowledgeStore
import argparse

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def load_chunks(file_path: str) -> List[Dict[str, Any]]:
    chunks = []
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Chunks file not found: {file_path}")
        
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    chunks.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipping invalid JSON line: {e}")
                    
    return chunks

def index_knowledge(embeddings_file: str, persist_directory: str, collection_name: str):
    logger.info("Loading knowledge embeddings...")
    chunks = load_chunks(embeddings_file)
    logger.info(f"Found {len(chunks)} chunks with embeddings")
    
    if not chunks:
        logger.info("No chunks to index. Exiting.")
        return
        
    logger.info("Indexing ChromaDB...")
    store = ChromaKnowledgeStore(persist_directory=persist_directory, collection_name=collection_name)
    store.upsert_chunks(chunks)
    
    logger.info(f"Indexed {len(chunks)} chunks")
    logger.info(f"Collection: {store.collection_name}")
    
    status = store.get_status()
    logger.info(f"Store status: {status}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index knowledge embeddings into ChromaDB")
    parser.add_argument("--input", type=str, default="knowledge_base/processed/embeddings/knowledge_embeddings.jsonl")
    parser.add_argument("--persist", type=str, default="knowledge_base/chroma")
    parser.add_argument("--collection", type=str, default="ecomind_scientific_knowledge")
    args = parser.parse_args()
    
    index_knowledge(args.input, args.persist, args.collection)
