"""Application configuration using pydantic-settings.

All values are sourced from environment variables (see .env.example at the repo
root). Sensible local-dev defaults are provided so the app can boot without a
.env file (e.g. when running the test suite).
"""
import json
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    PROJECT_NAME: str = "Bug Hunter Arena"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    POSTGRES_USER: str = "bughunter"
    POSTGRES_PASSWORD: str = "bughunter"
    POSTGRES_DB: str = "bughunter"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str | None = None

    # Redis / Celery
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    # JWT
    JWT_SECRET_KEY: str = "CHANGE_ME_super_secret_dev_key_only"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    # Typed as a raw string (not List[str]) because pydantic-settings
    # auto-JSON-decodes list-typed env vars *before* any validator runs,
    # so a non-JSON value (a bare URL, a comma-separated list) would
    # crash the app on startup with a SettingsError. CORS_ORIGINS below
    # parses this leniently instead.
    CORS_ORIGINS_RAW: str = Field(
        default='["http://localhost:5173", "http://127.0.0.1:5173"]',
        validation_alias="CORS_ORIGINS",
    )

    @property
    def CORS_ORIGINS(self) -> List[str]:
        # Accepts a JSON array ('["https://a","https://b"]'), a
        # comma-separated list ("https://a,https://b"), or a single bare
        # URL ("https://a") so a formatting slip in a hosting provider's
        # env var UI can't take the whole app down.
        stripped = self.CORS_ORIGINS_RAW.strip()
        if stripped.startswith("["):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                pass
        return [origin.strip() for origin in stripped.split(",") if origin.strip()]

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            # Managed Postgres providers (e.g. Render) hand out
            # postgres:// or postgresql:// URLs; SQLAlchemy's psycopg2
            # dialect requires the postgresql+psycopg2:// scheme.
            if url.startswith("postgres://"):
                url = "postgresql+psycopg2://" + url[len("postgres://"):]
            elif url.startswith("postgresql://"):
                url = "postgresql+psycopg2://" + url[len("postgresql://"):]
            return url
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def celery_broker(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL

    @property
    def celery_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
