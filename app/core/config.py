from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "developer-landing-api"
    app_env: str = "development"
    app_version: str = "0.1.0"
    storage_dir: Path = Path("storage")
    log_file: Path = Path("storage/logs/app.log")

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:4200"])

    ai_api_key: str | None = None
    ai_base_url: str = "https://api.openai.com/v1"
    ai_model: str = "gpt-4o-mini"
    ai_timeout_seconds: int = 10

    contact_owner_email: str = "owner@example.com"
    email_from: str = "no-reply@example.com"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True

    rate_limit_ip_requests: int = 5
    rate_limit_ip_window_seconds: int = 600
    rate_limit_email_requests: int = 3
    rate_limit_email_window_seconds: int = 3600

    metrics_api_key: str | None = None

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
