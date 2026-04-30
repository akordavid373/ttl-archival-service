from urllib.parse import urlparse
from typing import Literal


def validate_database_url(value: str) -> None:
    """Validate that DATABASE_URL is a supported connection string."""
    if not value:
        raise ValueError("DATABASE_URL is required")

    parsed = urlparse(value)
    if parsed.scheme not in {"sqlite", "postgresql", "mysql", "oracle"}:
        raise ValueError(f"Unsupported database scheme: {parsed.scheme}")

    if parsed.scheme != "sqlite" and not parsed.hostname:
        raise ValueError("DATABASE_URL must include a host for non-sqlite databases")


def validate_secret_backend(value: str) -> str:
    """Validate that the secret backend enum is supported."""
    allowed = {"env", "vault", "ssm"}
    if value not in allowed:
        raise ValueError(f"SECRET_BACKEND must be one of {sorted(allowed)}")
    return value


def mask_secret_value(field_name: str, value: str) -> str:
    """Mask secret values based on field naming conventions."""
    secret_tokens = {"SECRET", "KEY", "PASSWORD", "TOKEN"}
    if any(token in field_name.upper() for token in secret_tokens):
        return "***"
    return value
