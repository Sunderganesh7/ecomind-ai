from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

@router.get("/health", response_model=HealthResponse, summary="Health Check Endpoint")
def health_check():
    return HealthResponse(
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION
    )
