from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.environmental import EnvironmentalObservationCreate, EnvironmentalObservation
from app.services import profile_service

router = APIRouter()

@router.post("", response_model=EnvironmentalObservation, status_code=status.HTTP_201_CREATED, summary="Create a new environmental profile")
def create_profile(profile_data: EnvironmentalObservationCreate, db: Session = Depends(get_db)):
    """
    Creates a new environmental profile using the provided structured observations.
    """
    return profile_service.create_profile(db, profile_data)

@router.get("/{id}", response_model=EnvironmentalObservation, summary="Retrieve an environmental profile")
def get_profile(id: int, db: Session = Depends(get_db)):
    """
    Retrieves an environmental profile by its ID.
    """
    db_obs = profile_service.get_profile(db, id)
    if not db_obs:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_obs

@router.put("/{id}", response_model=EnvironmentalObservation, summary="Update an existing environmental profile")
def update_profile(id: int, profile_data: EnvironmentalObservationCreate, db: Session = Depends(get_db)):
    """
    Updates an environmental profile by its ID.
    Returns 404 if the profile does not exist.
    """
    db_obs = profile_service.update_profile(db, id, profile_data)
    if not db_obs:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_obs
