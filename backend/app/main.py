from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="EcoMind AI API",
    description="Backend API for the EcoMind Environmental Intelligence System",
    version="1.0.0",
)

@app.get("/health", summary="Health Check Endpoint")
def health_check():
    return JSONResponse(content={"status": "ok", "service": "ecomind-ai"})

# Note: Business logic and AI reasoning should NOT be in main.py.
# They will be implemented in the respective modules under the app directory.
