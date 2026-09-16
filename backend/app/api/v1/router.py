from fastapi import APIRouter
from app.api.v1 import health, profiles

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
# Future endpoints will be registered here, e.g.:
# api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
