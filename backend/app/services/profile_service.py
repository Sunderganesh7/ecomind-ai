from sqlalchemy.orm import Session
from app.models.environmental import (
    EnvironmentalObservation, 
    LocationModel, 
    SoilModel, 
    ClimateModel, 
    LandModel, 
    BiodiversityModel, 
    HumanImpactModel
)
from app.schemas.environmental import EnvironmentalObservationCreate

def create_profile(db: Session, profile_data: EnvironmentalObservationCreate) -> EnvironmentalObservation:
    db_obs = EnvironmentalObservation(
        observed_at=profile_data.observed_at,
        source_name=profile_data.source_name,
        source_type=profile_data.source_type,
        source_reference=profile_data.source_reference,
        data_quality=profile_data.data_quality,
        confidence=profile_data.confidence
    )
    
    if profile_data.location:
        db_obs.location = LocationModel(**profile_data.location.model_dump())
    if profile_data.soil:
        db_obs.soil = SoilModel(**profile_data.soil.model_dump())
    if profile_data.climate:
        db_obs.climate = ClimateModel(**profile_data.climate.model_dump())
    if profile_data.land:
        db_obs.land = LandModel(**profile_data.land.model_dump())
    if profile_data.biodiversity:
        db_obs.biodiversity = BiodiversityModel(**profile_data.biodiversity.model_dump())
    if profile_data.human_impact:
        db_obs.human_impact = HumanImpactModel(**profile_data.human_impact.model_dump())

    db.add(db_obs)
    db.commit()
    db.refresh(db_obs)
    return db_obs

def get_profile(db: Session, profile_id: int) -> EnvironmentalObservation:
    return db.query(EnvironmentalObservation).filter(EnvironmentalObservation.id == profile_id).first()

def update_profile(db: Session, profile_id: int, profile_data: EnvironmentalObservationCreate) -> EnvironmentalObservation:
    db_obs = get_profile(db, profile_id)
    if not db_obs:
        return None
        
    # Update core fields
    db_obs.observed_at = profile_data.observed_at
    db_obs.source_name = profile_data.source_name
    db_obs.source_type = profile_data.source_type
    db_obs.source_reference = profile_data.source_reference
    db_obs.data_quality = profile_data.data_quality
    db_obs.confidence = profile_data.confidence
    
    # Helper to update 1:1 nested models
    def update_nested(db_obj_attr, nested_data, model_cls):
        current_nested = getattr(db_obs, db_obj_attr)
        if nested_data:
            if current_nested:
                for key, value in nested_data.model_dump().items():
                    setattr(current_nested, key, value)
            else:
                setattr(db_obs, db_obj_attr, model_cls(**nested_data.model_dump()))
        else:
            if current_nested:
                setattr(db_obs, db_obj_attr, None)

    update_nested('location', profile_data.location, LocationModel)
    update_nested('soil', profile_data.soil, SoilModel)
    update_nested('climate', profile_data.climate, ClimateModel)
    update_nested('land', profile_data.land, LandModel)
    update_nested('biodiversity', profile_data.biodiversity, BiodiversityModel)
    update_nested('human_impact', profile_data.human_impact, HumanImpactModel)

    db.commit()
    db.refresh(db_obs)
    return db_obs
