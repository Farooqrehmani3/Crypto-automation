"""
Application configuration loaded from environment variables.

Uses pydantic-settings for type-safe, validated settings management.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All application settings, loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── Application ───────────────────────────────────────────────────────
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    CORS_ORIGINS: str = "http://localhost:3000"
    SECRET_KEY: str = "change-me"

    PROJECT_NAME: str = "Crypto Intelligence AI"
    API_V1_PREFIX: str = "/api/v1"

    # ── Supabase ──────────────────────────────────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    # ── PostgreSQL ────────────────────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:password@localhost:5432/crypto_intelligence"
    )
    DATABASE_URL_SYNC: str = (
        "postgresql+psycopg2://postgres:password@localhost:5432/crypto_intelligence"
    )

    # Connection pool configuration
    DB_POOL_SIZE: int = Field(default=20, ge=5, le=100)
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0, le=50)
    DB_POOL_TIMEOUT: int = Field(default=30, ge=5, le=60)
    DB_POOL_RECYCLE: int = Field(default=1800, ge=300, le=3600)
    DB_ECHO: bool = False

    # ── Redis ─────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = Field(default=50, ge=10, le=500)
    REDIS_SOCKET_TIMEOUT: int = Field(default=5, ge=1, le=30)

    # ── OpenAI ────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TEMPERATURE: float = Field(default=0.7, ge=0.0, le=2.0)

    # ── CoinGecko ─────────────────────────────────────────────────────────
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"
    COINGECKO_API_KEY: str = ""
    COINGECKO_RATE_LIMIT: int = Field(default=30, description="Requests per minute")

    # ── News APIs ─────────────────────────────────────────────────────────
    NEWS_API_KEY: str = ""
    CRYPTOPANIC_API_KEY: str = ""

    # ── Rate Limiting ─────────────────────────────────────────────────────
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "20/minute"
    RATE_LIMIT_AI: str = "10/minute"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v:
            raise ValueError("DATABASE_URL must be set")
        return v


@lru_cache
def get_settings() -> Settings:
    """Return cached Settings instance. Safe to call repeatedly."""
    return Settings()
