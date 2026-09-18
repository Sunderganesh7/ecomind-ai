from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import setup_exception_handlers
from app.api.v1.router import api_router
from app.api.v1.health import health_check

from app.database.base import Base
from app.database.connection import engine

setup_logging()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for the EcoMind Environmental Intelligence System"
)

from fastapi import Request
from starlette.responses import JSONResponse

@app.middleware("http")
async def security_headers_and_limits_middleware(request: Request, call_next):
    # Request size limit check (if Content-Length is provided)
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > settings.MAX_REQUEST_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={"error": {"code": 413, "message": "Request entity too large"}}
                )
        except ValueError:
            pass
            
    response = await call_next(request)
    
    # Add Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response

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
