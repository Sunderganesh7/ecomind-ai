import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path

from .loader import DocumentLoader
from .extractor import DocumentExtractor
from .cleaner import TextCleaner
from .chunker import TextChunker
from .metadata import MetadataAttacher

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class IngestionPipeline:
    def __init__(self, sources_dir: str, metadata_dir: str, output_dir: str):
        self.sources_dir = Path(sources_dir)
        self.metadata_dir = Path(metadata_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.loader = DocumentLoader(sources_dir, metadata_dir)
        self.extractor = DocumentExtractor()
        self.cleaner = TextCleaner()
        self.chunker = TextChunker(chunk_size_words=200, chunk_overlap_words=50)
        self.metadata_attacher = MetadataAttacher(self.loader)
        
        self.manifest = {
            "generated_at": None,
            "documents_discovered": 0,
            "documents_processed": 0,
            "failed_documents": [],
            "pages_processed": 0,
            "chunks_generated": 0,
            "pipeline_version": "1.0"
        }
        
    def run(self):
        logger.info("Discovering documents...")
        documents = self.loader.discover_documents()
        self.manifest["documents_discovered"] = len(documents)
        logger.info(f"Found {len(documents)} documents")
        
        output_file = self.output_dir / "knowledge_chunks.jsonl"
        
        # We will write in append mode for incremental but let's clear it if running full ingestion
        # For idempotency, we should ideally track existing chunks, but for now we overwrite if running the whole pipeline.
        if output_file.exists():
            output_file.unlink()
            
        all_chunks_count = 0
        pages_processed = 0
        
        with open(output_file, "a", encoding="utf-8") as f:
            for doc in documents:
                doc_name = doc['file_name']
                logger.info(f"Processing document... {doc_name}")
                try:
                    # 1. Extraction
                    doc_with_pages = self.extractor.extract(doc)
                    page_count = len(doc_with_pages.get("pages", []))
                    if page_count == 0:
                        raise ValueError("No extractable text found")
                    
                    # 2. Cleaning
                    doc_cleaned = self.cleaner.clean_document(doc_with_pages)
                    
                    # 3. Chunking
                    raw_chunks = self.chunker.chunk_document(doc_cleaned)
                    
                    # 4. Metadata Attachment
                    final_chunks = self.metadata_attacher.attach(raw_chunks, doc_cleaned)
                    
                    # Save chunks
                    for chunk in final_chunks:
                        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                        
                    all_chunks_count += len(final_chunks)
                    pages_processed += page_count
                    self.manifest["documents_processed"] += 1
                    
                    logger.info(f"Extracted {page_count} pages")
                    logger.info(f"Generated {len(final_chunks)} chunks")
                    
                except Exception as e:
                    logger.warning(f"Failed document: {doc_name}. Reason: {str(e)}")
                    self.manifest["failed_documents"].append({
                        "file": doc_name,
                        "status": "failed",
                        "reason": str(e)
                    })
                    
        self.manifest["chunks_generated"] = all_chunks_count
        self.manifest["pages_processed"] = pages_processed
        self.manifest["generated_at"] = datetime.utcnow().isoformat()
        
        # Save manifest
        manifest_path = self.output_dir.parent / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as mf:
            json.dump(self.manifest, mf, indent=2)
            
        logger.info("Ingestion completed")
        logger.info(f"Documents processed: {self.manifest['documents_processed']}")
        logger.info(f"Chunks generated: {all_chunks_count}")
        if self.manifest["failed_documents"]:
            logger.warning(f"Failed documents: {len(self.manifest['failed_documents'])}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scientific Document Ingestion Pipeline")
    parser.add_argument("--input", type=str, default="knowledge_base/sources", help="Directory containing source documents")
    parser.add_argument("--metadata", type=str, default="knowledge_base/metadata", help="Directory containing metadata JSONs")
    parser.add_argument("--output", type=str, default="knowledge_base/processed/chunks", help="Directory to save chunks")
    args = parser.parse_args()
    
    pipeline = IngestionPipeline(args.input, args.metadata, args.output)
    pipeline.run()
