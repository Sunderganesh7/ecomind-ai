from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union

class Settings(BaseSettings):
    APP_NAME: str = "EcoMind AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    API_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "sqlite:///./ecomind.db" # Default placeholder
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
