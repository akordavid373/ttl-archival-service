"""
Configuration service for TTL archival service.
Provides dynamic configuration management with validation, history tracking, and runtime updates.
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from pathlib import Path
import threading
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

from ..config.settings import get_settings, Settings
from ..config.validators import validate_configuration, validate_config_update, ValidationResult
from ..utils.secret_manager import secret_manager

logger = logging.getLogger(__name__)

Base = declarative_base()


class ConfigHistory(Base):
    """Configuration history model."""
    __tablename__ = "config_history"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), nullable=False)
    changes = Column(Text, nullable=False)  # JSON string of changes
    source = Column(String(100), nullable=False)
    user_id = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    applied = Column(Boolean, default=False)
    rollback_available = Column(Boolean, default=True)


class ConfigSubscription:
    """Configuration change subscription."""
    def __init__(self, callback: Callable[[str, Dict[str, Any]], None], filter_sections: Optional[List[str]] = None):
        self.callback = callback
        self.filter_sections = filter_sections or []
        self.active = True


class ConfigService:
    """Configuration management service."""
    
    def __init__(self):
        self.settings = get_settings()
        self.subscriptions: List[ConfigSubscription] = []
        self._lock = threading.RLock()
        self._config_cache: Dict[str, Any] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)
        
        # Initialize configuration history table
        self._ensure_history_table()
    
    def _ensure_history_table(self):
        """Ensure configuration history table exists."""
        try:
            from ..database import engine
            Base.metadata.create_all(bind=engine)
            logger.info("Configuration history table ensured")
        except Exception as e:
            logger.error(f"Failed to create config history table: {e}")
    
    def get_current_config(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Get current configuration."""
        with self._lock:
            if (self._cache_timestamp and 
                datetime.utcnow() - self._cache_timestamp < self._cache_ttl and 
                self._config_cache):
                config = self._config_cache.copy()
            else:
                config = self.settings.to_dict() if include_secrets else self.settings.get_masked_dict()
                self._config_cache = config.copy()
                self._cache_timestamp = datetime.utcnow()
            
            return config
    
    def get_config_section(self, section: str, include_secrets: bool = False) -> Optional[Dict[str, Any]]:
        """Get a specific configuration section."""
        config = self.get_current_config(include_secrets=include_secrets)
        return config.get(section)
    
    def update_config(self, updates: Dict[str, Any], source: str = "manual", 
                     user_id: Optional[str] = None, validate_first: bool = True) -> Dict[str, Any]:
        """Update configuration dynamically."""
        with self._lock:
            try:
                # Validate updates first
                if validate_first:
                    validation_result = validate_config_update(updates)
                    if not validation_result.is_valid():
                        return {
                            "success": False,
                            "errors": validation_result.errors,
                            "warnings": validation_result.warnings
                        }
                
                # Store current config for history
                previous_config = self.settings.get_masked_dict()
                
                # Apply updates
                success = self.settings.update_config(updates, source)
                
                if success:
                    # Clear cache
                    self._config_cache.clear()
                    self._cache_timestamp = None
                    
                    # Store in history
                    self._store_config_change(updates, source, user_id)
                    
                    # Notify subscribers
                    self._notify_subscribers(source, updates)
                    
                    # Re-validate complete configuration
                    validation_result = validate_configuration(self.settings)
                    
                    logger.info(f"Configuration updated successfully from {source}")
                    
                    return {
                        "success": True,
                        "previous_config": previous_config,
                        "current_config": self.settings.get_masked_dict(),
                        "validation": validation_result.get_summary(),
                        "warnings": validation_result.warnings
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to apply configuration updates"
                    }
                    
            except Exception as e:
                logger.error(f"Failed to update configuration: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
    
    def reset_config_section(self, section: str, source: str = "manual", 
                           user_id: Optional[str] = None) -> Dict[str, Any]:
        """Reset a configuration section to defaults."""
        try:
            # Get default configuration
            default_settings = Settings()
            default_section = getattr(default_settings, section)
            
            # Extract default values
            updates = {section: default_section.__dict__}
            
            return self.update_config(updates, source, user_id)
            
        except Exception as e:
            logger.error(f"Failed to reset config section {section}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def rollback_config(self, version: Optional[str] = None, steps_back: int = 1,
                       source: str = "manual", user_id: Optional[str] = None) -> Dict[str, Any]:
        """Rollback configuration to a previous version."""
        try:
            from ..database import get_db
            
            db = next(get_db())
            try:
                if version:
                    # Rollback to specific version
                    history_entry = db.query(ConfigHistory).filter(
                        ConfigHistory.version == version,
                        ConfigHistory.rollback_available == True
                    ).first()
                else:
                    # Rollback N steps back
                    history_entries = db.query(ConfigHistory).filter(
                        ConfigHistory.rollback_available == True
                    ).order_by(ConfigHistory.timestamp.desc()).limit(steps_back + 1).all()
                    
                    if len(history_entries) <= steps_back:
                        return {
                            "success": False,
                            "error": f"Cannot rollback {steps_back} steps - not enough history"
                        }
                    
                    history_entry = history_entries[-1]
                
                if not history_entry:
                    return {
                        "success": False,
                        "error": "Configuration version not found or not available for rollback"
                    }
                
                # Parse and apply the configuration
                changes = json.loads(history_entry.changes)
                result = self.update_config(changes, f"{source}:rollback", user_id, validate_first=False)
                
                if result["success"]:
                    # Mark this version as used for rollback
                    history_entry.rollback_available = False
                    db.commit()
                    
                    result["rollback_version"] = history_entry.version
                    result["rollback_timestamp"] = history_entry.timestamp.isoformat()
                
                return result
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to rollback configuration: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_config_history(self, limit: int = 50, include_details: bool = False) -> List[Dict[str, Any]]:
        """Get configuration change history."""
        try:
            from ..database import get_db
            
            db = next(get_db())
            try:
                query = db.query(ConfigHistory).order_by(ConfigHistory.timestamp.desc()).limit(limit)
                history = []
                
                for entry in query.all():
                    item = {
                        "id": entry.id,
                        "version": entry.version,
                        "source": entry.source,
                        "user_id": entry.user_id,
                        "timestamp": entry.timestamp.isoformat(),
                        "applied": entry.applied,
                        "rollback_available": entry.rollback_available
                    }
                    
                    if include_details:
                        try:
                            item["changes"] = json.loads(entry.changes)
                        except json.JSONDecodeError:
                            item["changes"] = {"error": "Invalid JSON in changes"}
                    
                    history.append(item)
                
                return history
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to get config history: {e}")
            return []
    
    def validate_current_config(self) -> ValidationResult:
        """Validate the current configuration."""
        return validate_configuration(self.settings)
    
    def subscribe_to_changes(self, callback: Callable[[str, Dict[str, Any]], None], 
                           filter_sections: Optional[List[str]] = None) -> str:
        """Subscribe to configuration changes."""
        subscription_id = f"sub_{len(self.subscriptions)}_{datetime.utcnow().timestamp()}"
        subscription = ConfigSubscription(callback, filter_sections)
        self.subscriptions.append(subscription)
        
        logger.debug(f"Added configuration subscription: {subscription_id}")
        return subscription_id
    
    def unsubscribe_from_changes(self, subscription_id: str) -> bool:
        """Unsubscribe from configuration changes."""
        # Note: This is a simplified implementation
        # In practice, you'd want to store subscription IDs
        for i, sub in enumerate(self.subscriptions):
            if hasattr(sub, 'id') and sub.id == subscription_id:
                self.subscriptions.pop(i)
                logger.debug(f"Removed configuration subscription: {subscription_id}")
                return True
        
        return False
    
    def export_config(self, file_path: Optional[str] = None, include_secrets: bool = False) -> Dict[str, Any]:
        """Export configuration to file or return as dict."""
        config = self.get_current_config(include_secrets=include_secrets)
        
        if file_path:
            try:
                path = Path(file_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(path, 'w') as f:
                    json.dump(config, f, indent=2, default=str)
                
                logger.info(f"Configuration exported to: {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to export configuration: {e}")
                raise
        
        return config
    
    def import_config(self, file_path: str, merge: bool = False, 
                     source: str = "import", user_id: Optional[str] = None) -> Dict[str, Any]:
        """Import configuration from file."""
        try:
            path = Path(file_path)
            if not path.exists():
                return {
                    "success": False,
                    "error": f"Configuration file not found: {file_path}"
                }
            
            with open(path, 'r') as f:
                imported_config = json.load(f)
            
            if merge:
                # Merge with existing configuration
                current_config = self.get_current_config(include_secrets=True)
                for section, values in imported_config.items():
                    if section in current_config and isinstance(values, dict):
                        current_config[section].update(values)
                    else:
                        current_config[section] = values
                updates = current_config
            else:
                # Replace entire configuration
                updates = imported_config
            
            return self.update_config(updates, source, user_id)
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON in configuration file: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get current feature flags."""
        return self.settings.features.__dict__
    
    def update_feature_flags(self, flags: Dict[str, bool], source: str = "manual",
                           user_id: Optional[str] = None) -> Dict[str, Any]:
        """Update feature flags."""
        return self.update_config({"features": flags}, source, user_id)
    
    def get_runtime_metrics(self) -> Dict[str, Any]:
        """Get configuration service runtime metrics."""
        return {
            "cache_hits": len(self._config_cache) > 0,
            "cache_timestamp": self._cache_timestamp.isoformat() if self._cache_timestamp else None,
            "subscription_count": len(self.subscriptions),
            "config_version": self.settings.config_version,
            "last_updated": self.settings.last_updated.isoformat() if self.settings.last_updated else None,
            "history_entries": len(self.get_config_history(limit=1)),
            "validation_status": self.validate_current_config().get_summary()
        }
    
    def _store_config_change(self, changes: Dict[str, Any], source: str, user_id: Optional[str]):
        """Store configuration change in history."""
        try:
            from ..database import get_db
            
            db = next(get_db())
            try:
                # Generate version
                version = f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                
                history_entry = ConfigHistory(
                    version=version,
                    changes=json.dumps(changes, default=str),
                    source=source,
                    user_id=user_id,
                    applied=True
                )
                
                db.add(history_entry)
                db.commit()
                
                logger.debug(f"Stored configuration change: {version}")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to store config change: {e}")
    
    def _notify_subscribers(self, source: str, changes: Dict[str, Any]):
        """Notify subscribers of configuration changes."""
        for subscription in self.subscriptions:
            if not subscription.active:
                continue
            
            # Check if this subscription is interested in these changes
            if subscription.filter_sections:
                if not any(section in subscription.filter_sections for section in changes.keys()):
                    continue
            
            try:
                # Call the callback
                subscription.callback(source, changes)
            except Exception as e:
                logger.error(f"Error in configuration subscription callback: {e}")
    
    @contextmanager
    def transaction(self):
        """Context manager for configuration transactions."""
        # Store original state
        original_config = self.settings.get_masked_dict()
        
        try:
            yield self
        except Exception:
            # Rollback on error
            self.settings.update_config(original_config, "rollback")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on configuration service."""
        try:
            # Test configuration validation
            validation_result = self.validate_current_config()
            
            # Test cache functionality
            config = self.get_current_config()
            
            # Test history functionality
            history = self.get_config_history(limit=1)
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "validation": {
                    "valid": validation_result.is_valid(),
                    "error_count": len(validation_result.errors),
                    "warning_count": len(validation_result.warnings)
                },
                "cache": {
                    "working": len(config) > 0,
                    "timestamp": self._cache_timestamp.isoformat() if self._cache_timestamp else None
                },
                "history": {
                    "working": isinstance(history, list),
                    "entry_count": len(history)
                },
                "subscriptions": len(self.subscriptions)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }


# Global configuration service instance
config_service = ConfigService()
