import os
import chromadb
from typing import List, Dict, Any
from chromadb.config import Settings
import logging

logger = logging.getLogger(__name__)

class ChromaKnowledgeStore:
    def __init__(self, persist_directory: str = "knowledge_base/chroma", collection_name: str = "ecomind_scientific_knowledge"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Ensure directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"} # Use cosine similarity for sentence transformers
        )
        logger.info(f"Initialized ChromaDB store at {self.persist_directory}, collection: {self.collection_name}")

    def _prepare_metadata(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Convert complex metadata types to ChromaDB supported primitives (str, int, float, bool)"""
        meta = {}
        for key in ["chunk_id", "source_id", "source", "title", "year", "topic", "document_id", "url", "page_number", "section", "source_type"]:
            val = chunk.get(key)
            if val is not None:
                meta[key] = val
                
        # Handle lists
        for list_key in ["variables", "topics", "relationships", "interventions"]:
            val = chunk.get(list_key)
            if val and isinstance(val, list):
                meta[list_key] = "|".join(str(v) for v in val)
                
        # Ensure all types are valid
        valid_meta = {}
        for k, v in meta.items():
            if isinstance(v, (str, int, float, bool)):
                valid_meta[k] = v
            else:
                valid_meta[k] = str(v)
                
        return valid_meta

    def upsert_chunks(self, chunks: List[Dict[str, Any]]):
        """Upsert chunks into ChromaDB idempotently."""
        if not chunks:
            return

        ids = []
        embeddings = []
        metadatas = []
        documents = []

        for chunk in chunks:
            chunk_id = chunk.get("chunk_id")
            if not chunk_id:
                raise ValueError("Chunk is missing chunk_id")
                
            ids.append(chunk_id)
            documents.append(chunk.get("text", ""))
            embeddings.append(chunk.get("embedding"))
            metadatas.append(self._prepare_metadata(chunk))

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search the collection using the query embedding."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results["ids"] or not results["ids"][0]:
            return []
            
        formatted_results = []
        # results structure has lists of lists because of batch querying
        ids = results["ids"][0]
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0]
        
        for i in range(len(ids)):
            meta = metas[i] if metas else {}
            
            # Convert arrays back if necessary
            for list_key in ["variables", "topics", "relationships", "interventions"]:
                if list_key in meta and isinstance(meta[list_key], str):
                    meta[list_key] = meta[list_key].split("|")
            
            # Convert cosine distance to similarity score
            # ChromaDB cosine distance: 1 - cosine_similarity
            # So relevance = 1 - distance
            relevance = 1.0 - distances[i] if distances else 0.0
            
            result = {
                "text": docs[i],
                "relevance": round(relevance, 4),
                **meta
            }
            formatted_results.append(result)
            
        return formatted_results

    def get_status(self) -> Dict[str, Any]:
        """Return collection status."""
        return {
            "collection_name": self.collection_name,
            "count": self.collection.count(),
            "persist_directory": self.persist_directory
        }
