"""Application settings via pydantic-settings."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Workflow Automation Hub"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    database_url: str = "postgresql://workflowuser:workflowpass@postgres:5432/workflowdb"
    google_api_key: str = ""
    n8n_url: str = "http://n8n:5678"
    n8n_user: str = "admin"
    n8n_password: str = "admin123"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5678"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
