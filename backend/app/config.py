"""
Application configuration using Pydantic Settings.
All config is loaded from environment variables / .env file.
Uses SQLite by default for easy local development (no PostgreSQL needed).
Set DATABASE_URL to a PostgreSQL URL for production.
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # ── App ──
    APP_NAME: str = "AI Resume Intelligence"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ── Database (SQLite for dev, PostgreSQL for production) ──
    DATABASE_URL: str = "sqlite+aiosqlite:///./resume_intel.db"
    DATABASE_SYNC_URL: str = "sqlite:///./resume_intel.db"

    # ── Redis ──
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Security ──
    SECRET_KEY: str = "dev-secret-key-change-in-production-abc123def456"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ──
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ── File Upload ──
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx"]

    # ── Celery ──
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── Rate Limiting ──
    RATE_LIMIT_PER_MINUTE: int = 60

    # ── ML Model ──
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    SPACY_MODEL: str = "en_core_web_sm"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
