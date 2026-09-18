from fastapi import APIRouter
from app.api.v1 import health, profiles, knowledge, chat, memory

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(memory.router, prefix="/conversations", tags=["memory"])
# api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
