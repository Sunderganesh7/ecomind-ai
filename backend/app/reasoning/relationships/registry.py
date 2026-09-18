import json
from pathlib import Path
from typing import List
import logging
from app.reasoning.relationships.schemas import RelationshipDefinition

logger = logging.getLogger(__name__)

class RelationshipRegistry:
    def __init__(self, registry_path: str = "app/reasoning/relationships/definitions/environmental_relationships.json"):
        self.registry_path = Path(registry_path)
        self.definitions: List[RelationshipDefinition] = []
        self._load_registry()

    def _load_registry(self):
        if not self.registry_path.exists():
            fallback = Path(__file__).parent / "definitions" / "environmental_relationships.json"
            if fallback.exists():
                self.registry_path = fallback
            else:
                logger.warning(f"Relationship registry not found at {self.registry_path}")
                return
            
        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.definitions = [RelationshipDefinition(**d) for d in data]
            logger.info(f"Loaded {len(self.definitions)} relationship definitions.")
        except Exception as e:
            logger.error(f"Failed to load relationship registry: {e}")
            self.definitions = []

    def get_all(self) -> List[RelationshipDefinition]:
        return self.definitions
