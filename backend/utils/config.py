"""
Configuration settings using Pydantic
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

# Resolve absolute path to .env file in project root
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
env_path = ROOT_DIR / ".env"


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "AI Code Reviewer"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ai_code_reviewer.db")

    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Gemini settings
    GEMINI_MODEL: str = "gemini-1.5-pro"
    MAX_CODE_LENGTH: int = 50000  # Max characters for code input

    class Config:
        env_file = str(env_path)
        case_sensitive = True


settings = Settings()


# Trigger reload again

