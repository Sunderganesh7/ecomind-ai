import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.environmental import (
    EnvironmentalObservationCreate, 
    Location, 
    Soil, 
    Climate, 
    Biodiversity
)

def test_valid_environmental_observation():
    # 1. Valid environmental observation & 7. Nested model validation
    obs = EnvironmentalObservationCreate(
        location=Location(latitude=45.0, longitude=-90.0, region="Test Region"),
        soil=Soil(soil_ph=6.5, organic_carbon=2.1, moisture=15.0),
        climate=Climate(temperature=22.5, rainfall=120.0),
        biodiversity=Biodiversity(species_richness=42, habitat_diversity="high"),
        observed_at=datetime(2023, 1, 1, 12, 0, 0),
        source_name="Synthetic Test Data",
        confidence=0.95
    )
    assert obs.location.latitude == 45.0
    assert obs.soil.soil_ph == 6.5
    assert obs.climate.rainfall == 120.0
    assert obs.biodiversity.species_richness == 42

def test_invalid_latitude():
    # 2. Invalid latitude
    with pytest.raises(ValidationError) as exc_info:
        Location(latitude=91.0, longitude=0.0)
    assert "latitude" in str(exc_info.value)

def test_invalid_longitude():
    # 3. Invalid longitude
    with pytest.raises(ValidationError) as exc_info:
        Location(latitude=0.0, longitude=-181.0)
    assert "longitude" in str(exc_info.value)

def test_invalid_soil_ph():
    # 4. Invalid soil pH format/range
    with pytest.raises(ValidationError) as exc_info:
        Soil(soil_ph=15.0) # > 14.0
    assert "soil_ph" in str(exc_info.value)
    
    with pytest.raises(ValidationError) as exc_info:
        Soil(soil_ph=-1.0) # < 0.0
    assert "soil_ph" in str(exc_info.value)

def test_missing_optional_variables():
    # 5. Missing optional environmental variables
    obs = EnvironmentalObservationCreate(
        location=Location(latitude=0.0, longitude=0.0),
        observed_at=datetime.utcnow()
    )
    # Soil, climate, etc., should be None
    assert obs.soil is None
    assert obs.climate is None
    assert obs.biodiversity is None

def test_distinguish_null_from_zero():
    # 6. Distinguishing null from zero
    soil_null = Soil(soil_ph=None)
    soil_zero = Soil(soil_ph=0.0)
    
    assert soil_null.soil_ph is None
    assert soil_zero.soil_ph == 0.0
    assert soil_null.soil_ph != soil_zero.soil_ph

def test_serialization():
    # 8. Environmental observation serialization
    obs = EnvironmentalObservationCreate(
        location=Location(latitude=10.0, longitude=20.0),
        soil=Soil(soil_ph=7.0),
        observed_at=datetime(2023, 1, 1, 12, 0, 0)
    )
    obs_dict = obs.model_dump()
    assert obs_dict["location"]["latitude"] == 10.0
    assert obs_dict["soil"]["soil_ph"] == 7.0
    assert "climate" in obs_dict
    assert obs_dict["climate"] is None
