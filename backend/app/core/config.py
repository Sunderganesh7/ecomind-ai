from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union

from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB = (BACKEND_DIR / "ecomind.db").as_posix()

class Settings(BaseSettings):
    APP_NAME: str = "EcoMind AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    API_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB}"
    
    # Security
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    MAX_REQUEST_SIZE: int = 2097152 # 2 MB
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # LLM Settings
    LLM_PROVIDER: str = "openai"
    LLM_BASE_URL: str | None = None
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_API_KEY: str = ""
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 1500
    LLM_TIMEOUT: int = 30
    LLM_MAX_RETRIES: int = 1

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
