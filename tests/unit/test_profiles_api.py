import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.base import Base
from app.database.connection import get_db

# Create in-memory SQLite DB for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Sample JSON payload
SAMPLE_JSON = {
  "soil": {
    "ph": 6.2,
    "organic_carbon": 0.3,
    "moisture": 18
  },
  "climate": {
    "temperature": 29,
    "rainfall": 500
  },
  "land": {
    "land_use": "agriculture",
    "crop": "wheat",
    "cropping_system": "monoculture"
  },
  "biodiversity": {
    "species_richness": 12,
    "habitat_diversity": "low"
  },
  "human_impact": {
    "pollution": "moderate",
    "deforestation": "low"
  }
}

def test_create_profile():
    # Test 1 — Create profile
    response = client.post("/api/v1/profiles", json=SAMPLE_JSON)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["soil"]["ph"] == 6.2
    assert data["climate"]["rainfall"] == 500
    assert data["land"]["crop"] == "wheat"
    assert data["human_impact"]["pollution"] == "moderate"

def test_retrieve_profile():
    # Setup: Create profile
    create_response = client.post("/api/v1/profiles", json=SAMPLE_JSON)
    profile_id = create_response.json()["id"]

    # Test 2 — Retrieve profile
    response = client.get(f"/api/v1/profiles/{profile_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == profile_id
    assert data["biodiversity"]["species_richness"] == 12

def test_update_profile():
    # Setup: Create profile
    create_response = client.post("/api/v1/profiles", json=SAMPLE_JSON)
    profile_id = create_response.json()["id"]

    # Test 3 — Update profile
    updated_payload = SAMPLE_JSON.copy()
    updated_payload["soil"] = {
        "ph": 6.5,
        "organic_carbon": 0.4,
        "moisture": 20
    }
    
    response = client.put(f"/api/v1/profiles/{profile_id}", json=updated_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["soil"]["ph"] == 6.5
    assert data["soil"]["moisture"] == 20
    # Make sure other things are untouched/updated correctly
    assert data["climate"]["temperature"] == 29

def test_nonexistent_profile():
    # Test 4 — Nonexistent profile
    response = client.get("/api/v1/profiles/999999")
    assert response.status_code == 404
    
    response = client.put("/api/v1/profiles/999999", json=SAMPLE_JSON)
    assert response.status_code == 404

def test_invalid_data():
    # Test 5 — Invalid data
    invalid_json = {
        "soil": {
            "ph": -5,  # Invalid
            "organic_carbon": -1, # Valid conceptually but not logically, let's test pH
            "moisture": -10 # Valid conceptually in schema
        }
    }
    response = client.post("/api/v1/profiles", json=invalid_json)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == 422

def test_missing_required_structure():
    # Test 6 — Missing required structure
    # Wait, in the schema we made everything Optional except None.
    # To test missing required, we can send fundamentally wrong structure like lists instead of dicts.
    invalid_json = {
        "soil": [1, 2, 3] # Expected dict, got list
    }
    response = client.post("/api/v1/profiles", json=invalid_json)
    assert response.status_code == 422
