from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Location(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    region: Optional[str] = Field(None, min_length=1, description="Geographic region name")

class Soil(BaseModel):
    soil_ph: Optional[float] = Field(None, ge=0.0, le=14.0, description="Soil pH scale")
    organic_carbon: Optional[float] = Field(None, description="Soil organic carbon (percentage)")
    moisture: Optional[float] = Field(None, description="Soil moisture (unit preserved from source)")

class Climate(BaseModel):
    temperature: Optional[float] = Field(None, description="Temperature in °C")
    rainfall: Optional[float] = Field(None, ge=0.0, description="Rainfall in mm")

class Land(BaseModel):
    land_use: Optional[str] = Field(None, description="Descriptive land use category")
    crop: Optional[str] = Field(None, description="Crop type if applicable")
    cropping_system: Optional[str] = Field(None, description="Cropping system description")

class Biodiversity(BaseModel):
    species_richness: Optional[int] = Field(None, ge=0, description="Count of species")
    habitat_diversity: Optional[float] = Field(None, ge=0.0, description="Habitat diversity index")

class HumanImpact(BaseModel):
    pollution: Optional[float] = Field(None, description="Pollution metric (unit preserved from source)")
    deforestation: Optional[float] = Field(None, description="Deforestation metric (unit preserved from source)")

class EnvironmentalObservationCreate(BaseModel):
    location: Location
    soil: Optional[Soil] = None
    climate: Optional[Climate] = None
    land: Optional[Land] = None
    biodiversity: Optional[Biodiversity] = None
    human_impact: Optional[HumanImpact] = None
    
    observed_at: datetime = Field(..., description="Date and time of the observation")
    source_name: Optional[str] = Field(None, description="Name of the data source")
    source_type: Optional[str] = Field(None, description="Type of the data source (e.g., satellite, field survey)")
    source_reference: Optional[str] = Field(None, description="Reference link or citation")
    data_quality: Optional[str] = Field(None, description="Quality indicator of the data")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")

class EnvironmentalObservation(EnvironmentalObservationCreate):
    id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}
