import os
import sys
import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.database import SessionLocal
from backend.app.core.config.manager import ConfigManager, ConfigValidationError
from backend.app.core.config.audit import AuditEntry, ConfigAuditLog, write_audit_entry


client = TestClient(app)


def test_environment_specific_settings_load_correctly(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test_dev.db")
    ConfigManager.reset()
    manager = ConfigManager()
    settings = manager.get_settings()
    assert settings.APP_ENV == "development"
    assert settings.CONFIG_HOT_RELOAD is True

    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test_staging.db")
    ConfigManager.reset()
    manager = ConfigManager()
    settings = manager.get_settings()
    assert settings.APP_ENV == "staging"
    assert settings.CONFIG_HOT_RELOAD is False

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test_prod.db")
    ConfigManager.reset()
    manager = ConfigManager()
    settings = manager.get_settings()
    assert settings.APP_ENV == "production"
    assert settings.CONFIG_HOT_RELOAD is False


def test_validation_rejects_invalid_database_url(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "not-a-valid-url")
    ConfigManager.reset()

    with pytest.raises(ConfigValidationError):
        ConfigManager()


def test_patch_config_writes_audit_entry(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test_audit.db")
    monkeypatch.setenv("CONFIG_HOT_RELOAD", "false")
    ConfigManager.reset()

    response = client.patch("/api/v1/config", json={"updates": {"TTL_DEFAULT_SECONDS": 12345}})
    assert response.status_code == 200
    assert response.json()["success"] is True

    db = SessionLocal()
    try:
        entry = db.query(ConfigAuditLog).filter_by(field="TTL_DEFAULT_SECONDS").order_by(ConfigAuditLog.id.desc()).first()
        assert entry is not None
        assert entry.old_value is not None
        assert entry.new_value == "12345"
    finally:
        db.close()


def test_secrets_are_masked_in_audit_log(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test_secret.db")
    ConfigManager.reset()

    entry = AuditEntry(
        field="DATABASE_URL",
        old_value="sqlite:///./old.db",
        new_value="sqlite:///./new.db",
        changed_by="test_user",
    )
    asyncio.run(write_audit_entry(entry))

    db = SessionLocal()
    try:
        record = db.query(ConfigAuditLog).filter_by(field="DATABASE_URL").order_by(ConfigAuditLog.id.desc()).first()
        assert record is not None
        assert record.old_value == "***"
        assert record.new_value == "***"
    finally:
        db.close()


def test_hot_reload_triggers_on_interval(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test_reload.db")
    monkeypatch.setenv("CONFIG_HOT_RELOAD", "true")
    monkeypatch.setenv("CONFIG_RELOAD_INTERVAL_SECONDS", "0")
    monkeypatch.setenv("TTL_DEFAULT_SECONDS", "100")
    ConfigManager.reset()
    manager = ConfigManager()
    assert manager.get_settings().TTL_DEFAULT_SECONDS == 100

    monkeypatch.setenv("TTL_DEFAULT_SECONDS", "200")
    manager._last_reload = 0.0
    updated = manager.reload_if_needed()
    assert updated.TTL_DEFAULT_SECONDS == 200
