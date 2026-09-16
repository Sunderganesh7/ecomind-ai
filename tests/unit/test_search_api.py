import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.rag.search.search_service import KnowledgeSearchService
from app.api.v1.knowledge import get_search_service

class MockSearchService:
    def __init__(self):
        self.store = type('obj', (object,), {'get_status': lambda self: {"collection_name": "mock", "count": 1}})()
        
    def search(self, query: str, top_k: int = 5):
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if top_k <= 0 or top_k > 20:
            raise ValueError("Invalid top_k")
            
        return [
            {
                "text": "Mock search result about soil",
                "relevance": 0.95,
                "source": "FAO",
                "document_id": "doc123"
            }
        ]

@pytest.fixture
def test_client():
    app.dependency_overrides[get_search_service] = lambda: MockSearchService()
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_search_api_valid(test_client):
    response = test_client.post(
        "/api/v1/knowledge/search",
        json={"query": "soil health", "top_k": 3}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["source"] == "FAO"
    assert data["results"][0]["relevance"] == 0.95

def test_search_api_invalid_query_empty(test_client):
    response = test_client.post(
        "/api/v1/knowledge/search",
        json={"query": "   ", "top_k": 3}
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert "Query cannot be empty" in str(data["error"])

def test_search_api_invalid_query_missing(test_client):
    response = test_client.post(
        "/api/v1/knowledge/search",
        json={"top_k": 3}
    )
    
    assert response.status_code == 422 # Pydantic validation error

def test_search_api_invalid_top_k_high(test_client):
    response = test_client.post(
        "/api/v1/knowledge/search",
        json={"query": "soil", "top_k": 1000}
    )
    
    assert response.status_code == 422

def test_search_api_invalid_top_k_low(test_client):
    response = test_client.post(
        "/api/v1/knowledge/search",
        json={"query": "soil", "top_k": 0}
    )
    
    assert response.status_code == 422

def test_search_api_status(test_client):
    response = test_client.get("/api/v1/knowledge/status")
    
    assert response.status_code == 200
    data = response.json()
    assert data["collection_name"] == "mock"
    assert data["count"] == 1
