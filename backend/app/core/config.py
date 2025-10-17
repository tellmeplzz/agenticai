"""Application configuration and settings."""

from functools import lru_cache
from typing import List

from pathlib import Path
from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    environment: str = Field("development", env="AGENTICAI_ENV")
    cors_allow_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8501"],
        env="AGENTICAI_CORS_ALLOW_ORIGINS",
    )
    ollama_base_url: str = Field("http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field("deepseek-r1:70b", env="OLLAMA_MODEL")

    ocr_provider: str = Field("paddleocr", env="OCR_PROVIDER")
    ocr_lang: str = Field("ch", env="OCR_LANG")
    ocr_use_gpu: bool = Field(False, env="OCR_USE_GPU")

    data_dir: str = Field("storage", env="AGENTICAI_DATA_DIR")

    @validator("data_dir")
    def _expand_data_dir(cls, value: str) -> str:  # noqa: D401 - short validator
        """Ensure the data directory path is absolute and expanded."""

        expanded = Path(value).expanduser()
        if not expanded.is_absolute():
            expanded = Path.cwd() / expanded
        return str(expanded)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Cached access to application settings."""

    return Settings()


settings = get_settings()
