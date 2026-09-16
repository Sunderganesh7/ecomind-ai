from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.rag.search.search_service import KnowledgeSearchService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get the search service
# In a real app, this might be a singleton or tied to application state
_search_service = None

def get_search_service() -> KnowledgeSearchService:
    global _search_service
    if _search_service is None:
        _search_service = KnowledgeSearchService()
    return _search_service

class SearchRequest(BaseModel):
    query: str = Field(..., description="The semantic search query")
    top_k: int = Field(5, gt=0, le=20, description="Number of results to retrieve")

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]

@router.post("/search", response_model=SearchResponse)
def search_knowledge(request: SearchRequest, service: KnowledgeSearchService = Depends(get_search_service)):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=422, detail="Query cannot be empty or just whitespace.")
        
    try:
        results = service.search(query=query, top_k=request.top_k)
        return SearchResponse(results=results)
    except Exception as e:
        logger.error(f"Error during semantic search: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during semantic search.")

@router.get("/status")
def get_store_status(service: KnowledgeSearchService = Depends(get_search_service)):
    try:
        return service.store.get_status()
    except Exception as e:
        logger.error(f"Error retrieving knowledge store status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve store status.")
