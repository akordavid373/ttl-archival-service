"""Thin compatibility shim for centralized configuration management."""

from .config.manager import ConfigManager, config_manager, get_settings, settings

__all__ = ["ConfigManager", "config_manager", "get_settings", "settings"]
