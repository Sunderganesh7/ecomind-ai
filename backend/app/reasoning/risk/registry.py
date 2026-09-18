import json
from pathlib import Path
from typing import List
import logging
from app.reasoning.risk.schemas import RiskPatternDefinition

logger = logging.getLogger(__name__)

class RiskRegistry:
    def __init__(self, registry_path: str = "app/reasoning/risk/definitions/risk_patterns.json"):
        self.registry_path = Path(registry_path)
        self.definitions: List[RiskPatternDefinition] = []
        self._load_registry()

    def _load_registry(self):
        if not self.registry_path.exists():
            fallback = Path(__file__).parent / "definitions" / "risk_patterns.json"
            if fallback.exists():
                self.registry_path = fallback
            else:
                logger.warning(f"Risk registry not found at {self.registry_path}")
                return
            
        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.definitions = [RiskPatternDefinition(**d) for d in data]
            logger.info(f"Loaded {len(self.definitions)} risk pattern definitions.")
        except Exception as e:
            logger.error(f"Failed to load risk registry: {e}")
            self.definitions = []

    def get_all(self) -> List[RiskPatternDefinition]:
        return self.definitions
