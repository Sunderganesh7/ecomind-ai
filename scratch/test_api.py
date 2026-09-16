from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
response = client.post("/api/v1/knowledge/search", json={"query": "relationship between soil carbon and biodiversity", "top_k": 5})
import json
print(json.dumps(response.json(), indent=2))
