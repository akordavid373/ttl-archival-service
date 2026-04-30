from __future__ import annotations

import os
import time
from typing import Any, Callable, Dict, List, Optional
from pydantic import ValidationError

from .base import BaseConfig, DevelopmentConfig, StagingConfig, ProductionConfig
from .validators import mask_secret_value


class ConfigValidationError(ValueError):
    """Raised when configuration validation fails."""

    def __init__(self, errors: List[Dict[str, Any]]):
        self.errors = errors
        message = "; ".join(
            f"{err.get('loc')}: {err.get('msg')}" for err in errors
        )
        super().__init__(message)


class ConfigManager:
    """Singleton manager for centralized environment-aware configuration."""

    _instance: Optional["ConfigManager"] = None

    def __new__(cls) -> "ConfigManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self._settings = self._load_settings()
        self._callbacks: List[Callable[[BaseConfig, BaseConfig], None]] = []
        self._last_reload = time.monotonic()
        self._initialized = True

    @classmethod
    def reset(cls) -> None:
        """Reset singleton state to allow tests to reload configuration."""
        cls._instance = None

    def _settings_class(self) -> type[BaseConfig]:
        env = os.getenv("APP_ENV", "development").lower()
        if env == "staging":
            return StagingConfig
        if env == "production":
            return ProductionConfig
        return DevelopmentConfig

    def _load_settings(self) -> BaseConfig:
        try:
            settings_class = self._settings_class()
            settings = settings_class()
            settings = self._validate_instance(settings)
            return settings
        except ValidationError as exc:
            raise ConfigValidationError(exc.errors()) from exc

    def _validate_instance(self, settings: BaseConfig) -> BaseConfig:
        try:
            return settings.__class__(**settings.model_dump(mode="json"))
        except ValidationError as exc:
            raise ConfigValidationError(exc.errors()) from exc

    def get_settings(self) -> BaseConfig:
        """Return the current configuration settings."""
        self.reload_if_needed()
        return self._settings

    def reload_if_needed(self) -> BaseConfig:
        """Reload settings from environment if hot reload is enabled and interval elapsed."""
        if self._settings.CONFIG_HOT_RELOAD:
            elapsed = time.monotonic() - self._last_reload
            if elapsed >= self._settings.CONFIG_RELOAD_INTERVAL_SECONDS:
                self._reload()
        return self._settings

    def _reload(self) -> None:
        old_settings = self._settings
        self._settings = self._load_settings()
        self._last_reload = time.monotonic()
        self._notify_change(old_settings, self._settings)

    def validate_settings(self) -> BaseConfig:
        """Validate current settings and raise ConfigValidationError on failure."""
        try:
            self._settings = self._validate_instance(self._settings)
            return self._settings
        except ConfigValidationError:
            raise

    def on_change(self, callback: Callable[[BaseConfig, BaseConfig], None]) -> None:
        """Register an observer callback for configuration changes."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def _notify_change(self, old_settings: BaseConfig, new_settings: BaseConfig) -> None:
        for callback in self._callbacks:
            try:
                callback(old_settings, new_settings)
            except Exception:
                continue

    def apply_updates(self, updates: Dict[str, Any]) -> BaseConfig:
        """Apply runtime updates to the current configuration."""
        settings_data = self._settings.model_dump(mode="json")

        for key, value in updates.items():
            if key not in settings_data:
                raise KeyError(f"Unknown configuration key: {key}")
            settings_data[key] = value

        updated = self._settings.__class__(**settings_data)
        updated = self._validate_instance(updated)
        old_settings = self._settings
        self._settings = updated
        self._last_reload = time.monotonic()
        self._notify_change(old_settings, self._settings)
        return self._settings

    def get_public_settings(self) -> Dict[str, Any]:
        """Return settings suitable for non-secret API responses."""
        settings = self.get_settings()
        data = settings.model_dump(mode="json")
        for key, value in data.items():
            if key.upper() in {"DATABASE_URL", "SECRET_BACKEND"} or any(token in key.upper() for token in ["SECRET", "KEY", "PASSWORD", "TOKEN"]):
                data[key] = "***"
        return data


config_manager = ConfigManager()


def get_settings() -> BaseConfig:
    """Module-level helper for external imports."""
    return config_manager.get_settings()


settings = config_manager.get_settings()
