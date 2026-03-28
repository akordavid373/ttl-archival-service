"""
Test script for the configuration management system.
Validates all components work together correctly.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import Settings, get_settings, reload_settings
from config.validators import validate_configuration, validate_config_update
from services.config_service import config_service
from utils.secret_manager import secret_manager


def test_settings_initialization():
    """Test settings initialization from environment."""
    print("Testing Settings Initialization...")
    
    # Test default settings
    settings = Settings()
    assert settings.environment.value in ["development", "testing", "staging", "production"]
    assert settings.port == 8000
    assert settings.database.url is not None
    assert settings.storage.archive_path is not None
    assert settings.security.secret_key is not None
    
    print("✓ Settings initialization works correctly")


def test_configuration_validation():
    """Test configuration validation."""
    print("Testing Configuration Validation...")
    
    settings = Settings()
    
    # Test valid configuration
    validation_result = validate_configuration(settings)
    assert validation_result.is_valid(), f"Valid configuration failed validation: {validation_result.errors}"
    
    # Test invalid configuration
    settings.port = 99999  # Invalid port
    validation_result = validate_configuration(settings)
    assert not validation_result.is_valid(), "Invalid configuration passed validation"
    assert any("port" in error.field.lower() for error in validation_result.errors)
    
    print("✓ Configuration validation works correctly")


def test_config_updates():
    """Test dynamic configuration updates."""
    print("Testing Configuration Updates...")
    
    # Test valid update
    updates = {
        "features": {
            "enable_search": False,
            "enable_analytics": True
        }
    }
    
    result = config_service.update_config(updates, source="test")
    assert result["success"], f"Config update failed: {result.get('error')}"
    
    # Verify the update was applied
    current_config = config_service.get_current_config()
    assert current_config["features"]["enable_search"] == False
    assert current_config["features"]["enable_analytics"] == True
    
    # Test invalid update
    invalid_updates = {
        "database": {
            "pool_size": -1  # Invalid value
        }
    }
    
    result = config_service.update_config(invalid_updates, source="test")
    assert not result["success"], "Invalid config update should have failed"
    
    print("✓ Configuration updates work correctly")


def test_secret_manager():
    """Test secret manager functionality."""
    print("Testing Secret Manager...")
    
    # Test storing and retrieving secrets
    test_key = "test_api_key"
    test_value = "super_secret_value_123"
    
    success = secret_manager.store_secret(test_key, test_value, description="Test API key")
    assert success, "Failed to store secret"
    
    retrieved_value = secret_manager.get_secret(test_key)
    assert retrieved_value == test_value, "Retrieved secret doesn't match stored value"
    
    # Test secret info (without value)
    secret_info = secret_manager.get_secret_info(test_key)
    assert secret_info is not None, "Failed to get secret info"
    assert "value" not in secret_info, "Secret info should not contain actual value"
    assert secret_info["description"] == "Test API key", "Secret info description mismatch"
    
    # Test listing secrets
    secrets = secret_manager.list_secrets(include_values=False)
    assert test_key in secrets, "Secret not found in list"
    assert "value" not in secrets[test_key], "Secret list should not contain actual values"
    
    # Test deleting secret
    success = secret_manager.delete_secret(test_key)
    assert success, "Failed to delete secret"
    
    retrieved_value = secret_manager.get_secret(test_key)
    assert retrieved_value is None, "Deleted secret should not be retrievable"
    
    print("✓ Secret manager works correctly")


def test_config_history():
    """Test configuration history tracking."""
    print("Testing Configuration History...")
    
    # Make several configuration changes
    changes = [
        {"features": {"enable_search": False}},
        {"features": {"enable_analytics": False}},
        {"security": {"access_token_expire_minutes": 60}}
    ]
    
    for i, change in enumerate(changes):
        result = config_service.update_config(change, source=f"history_test_{i}")
        assert result["success"], f"Config change {i} failed"
    
    # Get history
    history = config_service.get_config_history(limit=10)
    assert len(history) >= 3, "Not enough history entries"
    
    # Check that our changes are in history
    our_changes = [h for h in history if h["source"].startswith("history_test_")]
    assert len(our_changes) == 3, "Our changes not found in history"
    
    print("✓ Configuration history works correctly")


def test_feature_flags():
    """Test feature flag management."""
    print("Testing Feature Flags...")
    
    # Get current flags
    flags = config_service.get_feature_flags()
    assert isinstance(flags, dict), "Feature flags should be a dictionary"
    assert "enable_search" in flags, "Expected feature flag not found"
    
    # Update feature flags
    new_flags = {
        "enable_search": False,
        "enable_notifications": True
    }
    
    result = config_service.update_feature_flags(new_flags, source="test")
    assert result["success"], "Feature flag update failed"
    
    # Verify updates
    updated_flags = config_service.get_feature_flags()
    assert updated_flags["enable_search"] == False, "Feature flag not updated"
    assert updated_flags["enable_notifications"] == True, "Feature flag not updated"
    
    print("✓ Feature flags work correctly")


def test_config_export_import():
    """Test configuration export and import."""
    print("Testing Configuration Export/Import...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        export_file = Path(temp_dir) / "test_config.json"
        
        # Export configuration
        exported_config = config_service.export_config(str(export_file))
        assert export_file.exists(), "Export file was not created"
        assert isinstance(exported_config, dict), "Export should return a dictionary"
        
        # Modify configuration
        config_service.update_config({"features": {"enable_search": False}}, source="test_export")
        
        # Import configuration
        result = config_service.import_config(str(export_file), merge=False, source="test_import")
        assert result["success"], f"Config import failed: {result.get('error')}"
        
        # Verify configuration was restored
        current_config = config_service.get_current_config()
        assert current_config["features"]["enable_search"] == True, "Configuration not restored correctly"
    
    print("✓ Configuration export/import works correctly")


def test_health_checks():
    """Test health check functionality."""
    print("Testing Health Checks...")
    
    # Test config service health
    config_health = config_service.health_check()
    assert config_health["status"] == "healthy", f"Config service unhealthy: {config_health.get('error')}"
    
    # Test secret manager health
    secret_health = secret_manager.health_check()
    assert secret_health["status"] == "healthy", f"Secret manager unhealthy: {secret_health.get('error')}"
    
    print("✓ Health checks work correctly")


def test_error_handling():
    """Test error handling in configuration system."""
    print("Testing Error Handling...")
    
    # Test invalid configuration updates
    invalid_updates = {
        "invalid_section": {
            "some_value": "test"
        }
    }
    
    result = config_service.update_config(invalid_updates, source="test")
    # Should succeed but with warnings about unknown section
    
    # Test secret manager with invalid key
    success = secret_manager.store_secret("", "value")  # Empty key
    assert not success, "Should not accept empty key"
    
    success = secret_manager.store_secret("invalid key!", "value")  # Invalid characters
    assert not success, "Should not accept invalid key format"
    
    print("✓ Error handling works correctly")


def run_all_tests():
    """Run all configuration system tests."""
    print("=" * 60)
    print("Running Configuration System Tests")
    print("=" * 60)
    
    tests = [
        test_settings_initialization,
        test_configuration_validation,
        test_config_updates,
        test_secret_manager,
        test_config_history,
        test_feature_flags,
        test_config_export_import,
        test_health_checks,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All tests passed! Configuration system is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    # Set test environment
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["SECRET_MASTER_KEY"] = "test_master_key_for_validation_only"
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
