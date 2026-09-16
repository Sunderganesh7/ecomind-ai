import os
import json
from pathlib import Path
from typing import List, Dict, Any

class DocumentLoader:
    def __init__(self, sources_dir: str, metadata_dir: str):
        self.sources_dir = Path(sources_dir)
        self.metadata_dir = Path(metadata_dir)
        
        self.sources = self._load_json("sources.json")
        self.coverage_matrix = self._load_json("coverage_matrix.json")
        self.relationship_matrix = self._load_json("relationship_matrix.json")

    def _load_json(self, filename: str) -> Any:
        path = self.metadata_dir / filename
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def discover_documents(self) -> List[Dict[str, Any]]:
        documents = []
        for ext in ["*.pdf", "*.txt"]:
            for file_path in self.sources_dir.rglob(ext):
                source_id = file_path.stem
                
                # Retrieve source metadata if it exists
                metadata = None
                if isinstance(self.sources, list):
                    metadata = next((s for s in self.sources if s.get("source_id") == source_id), None)
                
                documents.append({
                    "file_path": str(file_path),
                    "file_name": file_path.name,
                    "file_type": file_path.suffix.lower(),
                    "source_id": source_id,
                    "metadata": metadata
                })
        return documents
