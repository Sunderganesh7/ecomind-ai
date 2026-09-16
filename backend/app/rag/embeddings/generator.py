import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from .embedding_service import EmbeddingService

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self, chunks_file: str, output_dir: str):
        self.chunks_file = Path(chunks_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.service = EmbeddingService()
        
    def generate(self):
        if not self.chunks_file.exists():
            logger.error(f"Chunks file not found: {self.chunks_file}")
            return
            
        output_file = self.output_dir / "knowledge_embeddings.jsonl"
        
        # Clear previous embeddings
        if output_file.exists():
            output_file.unlink()
            
        logger.info("Initializing Embedding Service...")
        # Verify model loads
        self.service.load_model()
        dim = self.service.dimension
        logger.info(f"Model loaded successfully. Dimension: {dim}")
        
        processed_count = 0
        failed_count = 0
        
        with open(self.chunks_file, "r", encoding="utf-8") as infile, open(output_file, "a", encoding="utf-8") as outfile:
            for line in infile:
                if not line.strip():
                    continue
                try:
                    chunk = json.loads(line)
                    text = chunk.get("text")
                    if not text:
                        raise ValueError("Chunk has no text.")
                        
                    embedding = self.service.embed_chunk(text)
                    
                    # Create the output record preserving all metadata
                    record = {
                        "chunk_id": chunk["chunk_id"],
                        "source_id": chunk["source_id"],
                        "title": chunk.get("title"),
                        "year": chunk.get("year"),
                        "url": chunk.get("url"),
                        "page_number": chunk.get("page_number"),
                        "topic": chunk.get("topic"),
                        "topics": chunk.get("topics", []),
                        "relationships": chunk.get("relationships", []),
                        "text": text,
                        "embedding": embedding,
                        "dimension": dim
                    }
                    
                    outfile.write(json.dumps(record, ensure_ascii=False) + "\n")
                    processed_count += 1
                except Exception as e:
                    logger.error(f"Failed to process chunk: {e}")
                    failed_count += 1
                    
        logger.info(f"Embedding generation completed.")
        logger.info(f"Successfully embedded {processed_count} chunks.")
        if failed_count > 0:
            logger.warning(f"Failed to embed {failed_count} chunks.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate embeddings for knowledge chunks")
    parser.add_argument("--input", type=str, default="knowledge_base/processed/chunks/knowledge_chunks.jsonl")
    parser.add_argument("--output", type=str, default="knowledge_base/processed/embeddings")
    args = parser.parse_args()
    
    generator = EmbeddingGenerator(args.input, args.output)
    generator.generate()
