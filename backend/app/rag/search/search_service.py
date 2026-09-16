import logging
from typing import List, Dict, Any
from app.rag.embeddings.embedding_service import EmbeddingService
from app.rag.store.chroma_store import ChromaKnowledgeStore

logger = logging.getLogger(__name__)

class KnowledgeSearchService:
    def __init__(self, embedding_service: EmbeddingService = None, store: ChromaKnowledgeStore = None):
        self.embedding_service = embedding_service or EmbeddingService()
        self.store = store or ChromaKnowledgeStore()
        
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search using query string."""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
            
        if top_k <= 0 or top_k > 20:
            raise ValueError("top_k must be between 1 and 20.")
            
        # 1. Embed Query
        query_embedding = self.embedding_service.embed_chunk(query.strip())
        
        # 2. Search ChromaDB
        results = self.store.search(query_embedding, top_k)
        
        return results
