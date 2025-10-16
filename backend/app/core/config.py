"""Application configuration and settings."""

from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    environment: str = Field("development", env="AGENTICAI_ENV")
    cors_allow_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8501"],
        env="AGENTICAI_CORS_ALLOW_ORIGINS",
    )
    ollama_base_url: str = Field("http://localhost:11434", env="OLLAMA_BASE_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Cached access to application settings."""

    return Settings()


settings = get_settings()
