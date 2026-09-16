from typing import List, Union
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        if SentenceTransformer is None:
            raise ImportError("sentence-transformers is not installed.")
        self.model_name = model_name
        self._model = None
        
    def load_model(self):
        """Lazy loads the model to avoid blocking on initialization unless needed."""
        if self._model is None:
            # This will automatically download the model from HF if not cached.
            try:
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                raise RuntimeError(f"Failed to load or download the model '{self.model_name}'. Ensure internet connectivity or check model cache. Error: {e}")

    @property
    def dimension(self) -> int:
        self.load_model()
        # all-MiniLM-L6-v2 outputs 384-dimensional embeddings
        return self._model.get_embedding_dimension()

    def embed_chunk(self, text: str) -> List[float]:
        self.load_model()
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_chunks(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        self.load_model()
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
