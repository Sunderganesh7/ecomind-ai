from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

class LocationModel(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    region = Column(String, nullable=True)
    observation_id = Column(Integer, ForeignKey("environmental_observations.id", ondelete="CASCADE"), unique=True)
    observation = relationship("EnvironmentalObservation", back_populates="location")

class SoilModel(Base):
    __tablename__ = "soil_observations"
    id = Column(Integer, primary_key=True, index=True)
    soil_ph = Column(Float, nullable=True)
    organic_carbon = Column(Float, nullable=True)
    moisture = Column(Float, nullable=True)
    observation_id = Column(Integer, ForeignKey("environmental_observations.id", ondelete="CASCADE"), unique=True)
    observation = relationship("EnvironmentalObservation", back_populates="soil")

class ClimateModel(Base):
    __tablename__ = "climate_observations"
    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float, nullable=True)
    rainfall = Column(Float, nullable=True)
    observation_id = Column(Integer, ForeignKey("environmental_observations.id", ondelete="CASCADE"), unique=True)
    observation = relationship("EnvironmentalObservation", back_populates="climate")

class LandModel(Base):
    __tablename__ = "land_observations"
    id = Column(Integer, primary_key=True, index=True)
    land_use = Column(String, nullable=True)
    crop = Column(String, nullable=True)
    cropping_system = Column(String, nullable=True)
    observation_id = Column(Integer, ForeignKey("environmental_observations.id", ondelete="CASCADE"), unique=True)
    observation = relationship("EnvironmentalObservation", back_populates="land")

class BiodiversityModel(Base):
    __tablename__ = "biodiversity_observations"
    id = Column(Integer, primary_key=True, index=True)
    species_richness = Column(Integer, nullable=True)
    habitat_diversity = Column(String, nullable=True)
    observation_id = Column(Integer, ForeignKey("environmental_observations.id", ondelete="CASCADE"), unique=True)
    observation = relationship("EnvironmentalObservation", back_populates="biodiversity")

class HumanImpactModel(Base):
    __tablename__ = "human_impact_observations"
    id = Column(Integer, primary_key=True, index=True)
    pollution = Column(String, nullable=True)
    deforestation = Column(String, nullable=True)
    observation_id = Column(Integer, ForeignKey("environmental_observations.id", ondelete="CASCADE"), unique=True)
    observation = relationship("EnvironmentalObservation", back_populates="human_impact")

class EnvironmentalObservation(Base):
    __tablename__ = "environmental_observations"
    id = Column(Integer, primary_key=True, index=True)
    
    # Temporal & Traceability
    observed_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    source_name = Column(String, nullable=True)
    source_type = Column(String, nullable=True)
    source_reference = Column(String, nullable=True)
    data_quality = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)

    # 1:1 Relationships to categories
    location = relationship("LocationModel", uselist=False, back_populates="observation", cascade="all, delete-orphan")
    soil = relationship("SoilModel", uselist=False, back_populates="observation", cascade="all, delete-orphan")
    climate = relationship("ClimateModel", uselist=False, back_populates="observation", cascade="all, delete-orphan")
    land = relationship("LandModel", uselist=False, back_populates="observation", cascade="all, delete-orphan")
    biodiversity = relationship("BiodiversityModel", uselist=False, back_populates="observation", cascade="all, delete-orphan")
    human_impact = relationship("HumanImpactModel", uselist=False, back_populates="observation", cascade="all, delete-orphan")
