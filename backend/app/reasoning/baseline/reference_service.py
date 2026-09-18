import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ReferenceService:
    def __init__(self, references_path: str = "../knowledge_base/references/environmental_references.json"):
        self.references_path = Path(references_path)
        self.references: Dict[str, Any] = {}
        self._load_references()

    def _load_references(self):
        if not self.references_path.exists():
            # Fallback to repo root knowledge_base/references
            fallback = Path(__file__).resolve().parents[4] / "knowledge_base" / "references" / "environmental_references.json"
            if fallback.exists():
                self.references_path = fallback
            else:
                logger.warning(f"Reference data not found at {self.references_path}")
                return
            
        try:
            with open(self.references_path, "r", encoding="utf-8") as f:
                self.references = json.load(f)
            logger.info(f"Loaded {len(self.references)} environmental references.")
        except Exception as e:
            logger.error(f"Failed to load references: {e}")
            self.references = {}

    def get_reference(self, metric_name: str) -> Optional[Dict[str, Any]]:
        return self.references.get(metric_name)
