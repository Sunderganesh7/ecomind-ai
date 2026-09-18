import json
from pathlib import Path
from typing import List
import logging
from app.recommendations.interventions.schemas import InterventionDefinition

logger = logging.getLogger(__name__)

class InterventionRegistry:
    def __init__(self, registry_path: str = "app/recommendations/interventions/definitions/interventions.json"):
        self.registry_path = Path(registry_path)
        self.definitions: List[InterventionDefinition] = []
        self._load_registry()

    def _load_registry(self):
        if not self.registry_path.exists():
            fallback = Path(__file__).parent / "definitions" / "interventions.json"
            if fallback.exists():
                self.registry_path = fallback
            else:
                logger.warning(f"Intervention registry not found at {self.registry_path}")
                return
            
        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.definitions = [InterventionDefinition(**d) for d in data]
            logger.info(f"Loaded {len(self.definitions)} intervention definitions.")
        except Exception as e:
            logger.error(f"Failed to load intervention registry: {e}")
            self.definitions = []

    def get_all(self) -> List[InterventionDefinition]:
        return self.definitions
