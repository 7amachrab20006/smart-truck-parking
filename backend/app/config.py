"""Application Configuration Module.

Loads configuration from environment variables and .env files using Pydantic Settings.
"""

from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and environment variable bindings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # General App Settings
    APP_NAME: str = "Smart Truck & Parking Assistant API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # CORS Settings
    CORS_ORIGINS: Union[List[str], str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse comma-separated string to list if necessary."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

    # Database Settings
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/smart_truck_db",
        description="Async PostgreSQL connection string using asyncpg driver",
    )
    SYNC_DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/smart_truck_db",
        description="Sync PostgreSQL connection string for Alembic migrations",
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30

    # JWT Authentication Settings
    SECRET_KEY: str = Field(
        default="super-secret-key-change-in-production-smart-truck-assistant-2025-token-secret",
        description="Secret key used for signing JWT tokens",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30    # 30 days

    # NYC Open Data API Settings
    NYC_OPEN_DATA_APP_TOKEN: str = Field(
        default="",
        description="Socrata Open Data API (SODA) application token for NYC data feeds",
    )
    NYC_OPEN_DATA_SECRET_TOKEN: str = Field(
        default="",
        description="Socrata Open Data API secret token",
    )
    NYC_OPEN_DATA_BASE_URL: str = "https://data.cityofnewyork.us/resource"

    # Mapbox Settings
    MAPBOX_ACCESS_TOKEN: str = Field(
        default="",
        description="Mapbox public or secret API token for geocoding and routing",
    )

    @property
    def nyc_open_data_base_url(self) -> str:
        return self.NYC_OPEN_DATA_BASE_URL

    @property
    def nyc_open_data_app_token(self) -> str:
        return self.NYC_OPEN_DATA_APP_TOKEN


settings = Settings()
