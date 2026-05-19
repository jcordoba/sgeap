"""Configuration module."""
import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings."""

    # App
    app_name: str = "SGEAP"
    app_version: str = "0.1.0"
    debug: bool = True

    # Database
    database_url: str = "postgresql+pg8000://user:password@localhost:5432/sgeap"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "user"
    postgres_password: str = "password"
    postgres_db: str = "sgeap"

    # JWT
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Storage
    upload_dir: Path = BASE_DIR / "uploads"
    max_file_size_mb: int = 50

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()