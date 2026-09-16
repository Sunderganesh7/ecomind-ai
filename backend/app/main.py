from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import setup_exception_handlers
from app.api.v1.router import api_router
from app.api.v1.health import health_check

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for the EcoMind Environmental Intelligence System"
)

# CORS configuration
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Exception handlers
setup_exception_handlers(app)

# Include v1 API router
app.include_router(api_router, prefix=settings.API_PREFIX)

# Compatibility route that delegates to v1 health check
@app.get("/api/health", summary="Compatibility Health Check", tags=["compatibility"])
def legacy_health_check():
    return health_check()
