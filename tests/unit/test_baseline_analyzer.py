import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.reasoning.baseline.analyzer import BaselineAnalyzer
from app.schemas.environmental import EnvironmentalObservation
from app.reasoning.baseline.reference_service import ReferenceService

@pytest.fixture
def mock_profile():
    return EnvironmentalObservation(
        id=1,
        created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": 0.3, "ph": None},
        climate={"rainfall": 500},
        land={"cropping_system": "monoculture"},
        biodiversity={},
        human_impact={"pollution": "high"}
    )

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database.base import Base
from app.database.connection import get_db
import app.models.environmental  # Ensure models are registered

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

fastapi_app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(fastapi_app)

@pytest.fixture
def analyzer():
    return BaselineAnalyzer()

def test_soil_metric_classification(analyzer, mock_profile):
    """TEST 1 — Soil metric. Provide a controlled organic-carbon value and a test reference."""
    response = analyzer.analyze_profile(mock_profile)
    oc = response.metrics.get("organic_carbon")
    assert oc is not None
    assert oc.observed_value == 0.3
    assert oc.status == "low"
    assert oc.risk == "potential_soil_constraint"
    assert oc.reference is not None
    assert oc.reference.type == "range"

def test_reference_boundary(analyzer):
    """TEST 2 — Reference boundary. Test values: below, within, above reference."""
    def _test_val(val, expected_status):
        p = EnvironmentalObservation(
            id=1, created_at="2026-01-01T00:00:00Z",
            soil={"organic_carbon": val}
        )
        res = analyzer.analyze_profile(p)
        assert res.metrics["organic_carbon"].status == expected_status

    _test_val(0.5, "low")
    _test_val(2.0, "normal")
    _test_val(6.0, "high")

def test_missing_value(analyzer):
    """TEST 3 — Missing value. Expected: status = unknown"""
    p = EnvironmentalObservation(
        id=1, created_at="2026-01-01T00:00:00Z",
        soil={"organic_carbon": None}
    )
    res = analyzer.analyze_profile(p)
    oc = res.metrics["organic_carbon"]
    assert oc.status == "unknown"
    assert oc.observed_value is None

def test_context_dependent_metric(analyzer, mock_profile):
    """TEST 4 — Context-dependent metric. Verify the analyzer does not invent a universal risk classification."""
    response = analyzer.analyze_profile(mock_profile)
    rf = response.metrics["rainfall"]
    assert rf.status == "context_dependent"
    assert rf.risk == "undetermined"

def test_categorical_land_metric(analyzer, mock_profile):
    """TEST 5 — Categorical land metric."""
    response = analyzer.analyze_profile(mock_profile)
    cs = response.metrics["cropping_system"]
    assert cs.status == "simplified"
    assert cs.risk == "potential_habitat_pressure"
    assert cs.reference.type == "categorical"

def test_multiple_variables(analyzer, mock_profile):
    """TEST 6 — Multiple variables. Verify all three signals are independently returned."""
    response = analyzer.analyze_profile(mock_profile)
    metrics = response.metrics
    assert "organic_carbon" in metrics
    assert "rainfall" in metrics
    assert "cropping_system" in metrics
    assert "pollution" in metrics

def test_invalid_values(analyzer):
    """TEST 7 — Invalid values. Verify invalid environmental values are rejected by existing validation."""
    with pytest.raises(ValueError):
        EnvironmentalObservation(
            id=1, created_at="2026-01-01T00:00:00Z",
            soil={"organic_carbon": "invalid_string"}
        )

def test_provenance(analyzer, mock_profile):
    """TEST 8 — Provenance. Verify reference-based classifications preserve source information."""
    response = analyzer.analyze_profile(mock_profile)
    oc = response.metrics["organic_carbon"]
    assert oc.evidence is not None
    assert oc.evidence.source == "FAO"
    assert oc.evidence.year == 2020

def test_reproducibility(analyzer, mock_profile):
    """TEST 9 — Reproducibility. No random behavior."""
    res1 = analyzer.analyze_profile(mock_profile)
    res2 = analyzer.analyze_profile(mock_profile)
    assert res1.model_dump() == res2.model_dump()

def test_api_endpoint(client):
    """Test the POST /api/v1/profiles/{id}/baseline API endpoint."""
    # First create a profile
    create_response = client.post("/api/v1/profiles", json={
        "soil": {"organic_carbon": 0.3},
        "land": {"cropping_system": "monoculture"},
        "climate": {"rainfall": 500}
    })
    assert create_response.status_code == 201
    profile_id = create_response.json()["id"]

    # Now run baseline analysis
    baseline_response = client.post(f"/api/v1/profiles/{profile_id}/baseline")
    assert baseline_response.status_code == 200
    data = baseline_response.json()
    assert data["profile_id"] == profile_id
    assert "metrics" in data
    assert "summary" in data
    assert data["metrics"]["organic_carbon"]["status"] == "low"
    assert data["metrics"]["cropping_system"]["status"] == "simplified"
    assert data["metrics"]["rainfall"]["status"] == "context_dependent"

    # Aggregated summary check
    summary = data["summary"]
    assert summary["soil_status"]["status"] == "low"
    assert "organic_carbon" in summary["soil_status"]["supporting_metrics"]
    assert summary["habitat_status"]["status"] == "simplified"
