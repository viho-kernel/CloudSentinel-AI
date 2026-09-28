import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Enterprise Application Configuration with multi-environment support."""
    APP_NAME: str = "CloudSentinel AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "dev")  # dev, staging, prod, local
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # GCP & AI Configuration
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "cloudsentinel-dev")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Security & CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "https://staging.cloudsentinel.io",
        "https://app.cloudsentinel.io"
    ]
    RATE_LIMIT_REQUESTS: int = 120
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Observability
    ENABLE_PROMETHEUS: bool = True

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
