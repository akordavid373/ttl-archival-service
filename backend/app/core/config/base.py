from __future__ import annotations

from typing import Literal
from pydantic import BaseSettings, SecretStr, field_validator, ConfigDict


class BaseConfig(BaseSettings):
    """Shared application configuration settings."""

    APP_ENV: Literal["development", "staging", "production"] = "development"
    DATABASE_URL: SecretStr
    REDIS_URL: str = "redis://localhost:6379"
    STELLAR_NETWORK: Literal["standalone", "futurenet", "public"] = "futurenet"
    CONTRACT_ID: str = ""
    TTL_DEFAULT_SECONDS: int = 86400
    CONFIG_HOT_RELOAD: bool = False
    CONFIG_RELOAD_INTERVAL_SECONDS: int = 30
    SECRET_BACKEND: Literal["env", "vault", "ssm"] = "env"

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore",
        frozen=False,
        str_strip_whitespace=True,
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, value: SecretStr) -> SecretStr:
        from .validators import validate_database_url

        validate_database_url(str(value.get_secret_value()))
        return value

    @field_validator("SECRET_BACKEND")
    @classmethod
    def validate_secret_backend(cls, value: str) -> str:
        from .validators import validate_secret_backend

        validate_secret_backend(value)
        return value


class DevelopmentConfig(BaseConfig):
    """Development environment settings."""

    CONFIG_HOT_RELOAD: bool = True
    SECRET_BACKEND: Literal["env", "vault", "ssm"] = "env"


class StagingConfig(BaseConfig):
    """Staging environment settings."""

    CONFIG_HOT_RELOAD: bool = False
    SECRET_BACKEND: Literal["env", "vault", "ssm"] = "env"


class ProductionConfig(BaseConfig):
    """Production environment settings."""

    CONFIG_HOT_RELOAD: bool = False
    SECRET_BACKEND: Literal["env", "vault", "ssm"] = "env"
