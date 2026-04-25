"""
Secure secret management system for TTL archival service.
Provides encrypted storage and retrieval of sensitive configuration data.
"""

import os
import logging
import json
import hashlib
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from pathlib import Path
from datetime import datetime, timedelta
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class SecretManager:
    """Secure secret management with encryption."""
    
    def __init__(self, master_key: Optional[str] = None, storage_path: Optional[str] = None):
        self.storage_path = storage_path or os.getenv("SECRET_STORAGE_PATH", "./secrets")
        self._lock = threading.RLock()
        self._secrets: Dict[str, Dict[str, Any]] = {}
        self._fernet: Optional[Fernet] = None
        self._master_key_hash: Optional[str] = None
        
        # Ensure storage directory exists
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption
        self._initialize_encryption(master_key)
        
        # Load existing secrets
        self._load_secrets()
    
    def _initialize_encryption(self, master_key: Optional[str]):
        """Initialize encryption with master key."""
        try:
            if master_key:
                # Use provided master key
                self._master_key_hash = self._hash_key(master_key)
                key = self._derive_key(master_key)
            else:
                # Try to get master key from environment
                env_key = os.getenv("SECRET_MASTER_KEY")
                if env_key:
                    self._master_key_hash = self._hash_key(env_key)
                    key = self._derive_key(env_key)
                else:
                    # Generate a new key and save it
                    key = Fernet.generate_key()
                    key_file = Path(self.storage_path) / ".master_key"
                    
                    if not key_file.exists():
                        with open(key_file, 'wb') as f:
                            f.write(key)
                        logger.warning(f"Generated new master key saved to: {key_file}")
                        logger.warning("Secure this file and set SECRET_MASTER_KEY environment variable for production")
                    
                    self._master_key_hash = self._hash_key(key.decode())
            
            self._fernet = Fernet(key)
            logger.info("Secret manager encryption initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise
    
    def _hash_key(self, key: str) -> str:
        """Create a hash of the key for verification."""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def _derive_key(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        if salt is None:
            # Use a consistent salt for this instance
            salt = b'ttl_archival_salt_2024'
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _encrypt(self, data: str) -> str:
        """Encrypt data."""
        if not self._fernet:
            raise RuntimeError("Encryption not initialized")
        
        encrypted_data = self._fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt data."""
        if not self._fernet:
            raise RuntimeError("Encryption not initialized")
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise ValueError("Failed to decrypt secret")
    
    def _load_secrets(self):
        """Load secrets from storage."""
        secrets_file = Path(self.storage_path) / "secrets.enc"
        
        if not secrets_file.exists():
            logger.info("No existing secrets file found")
            return
        
        try:
            with open(secrets_file, 'r') as f:
                encrypted_data = f.read()
            
            if encrypted_data:
                decrypted_json = self._decrypt(encrypted_data)
                self._secrets = json.loads(decrypted_json)
                logger.info(f"Loaded {len(self._secrets)} secrets from storage")
            
        except Exception as e:
            logger.error(f"Failed to load secrets: {e}")
            self._secrets = {}
    
    def _save_secrets(self):
        """Save secrets to storage."""
        secrets_file = Path(self.storage_path) / "secrets.enc"
        
        try:
            secrets_json = json.dumps(self._secrets, default=str)
            encrypted_data = self._encrypt(secrets_json)
            
            # Write to temporary file first, then move
            temp_file = secrets_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                f.write(encrypted_data)
            
            # Move temporary file to final location
            temp_file.replace(secrets_file)
            
            logger.debug("Secrets saved to storage")
            
        except Exception as e:
            logger.error(f"Failed to save secrets: {e}")
            raise
    
    def store_secret(self, key: str, value: str, description: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store a secret securely."""
        with self._lock:
            try:
                if not key or not value:
                    raise ValueError("Key and value are required")
                
                # Validate key format
                if not self._validate_key(key):
                    raise ValueError("Invalid key format")
                
                secret_data = {
                    "value": value,
                    "description": description or "",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "access_count": 0,
                    "last_accessed": None,
                    "metadata": metadata or {}
                }
                
                # Update existing secret if it exists
                if key in self._secrets:
                    secret_data["created_at"] = self._secrets[key]["created_at"]
                    secret_data["access_count"] = self._secrets[key]["access_count"]
                    logger.info(f"Updating existing secret: {key}")
                else:
                    logger.info(f"Storing new secret: {key}")
                
                self._secrets[key] = secret_data
                self._save_secrets()
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to store secret {key}: {e}")
                return False
    
    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a secret."""
        with self._lock:
            try:
                if key not in self._secrets:
                    logger.warning(f"Secret not found: {key}")
                    return None
                
                secret_data = self._secrets[key]
                
                # Update access information
                secret_data["access_count"] += 1
                secret_data["last_accessed"] = datetime.utcnow().isoformat()
                self._save_secrets()
                
                logger.debug(f"Retrieved secret: {key}")
                return secret_data["value"]
                
            except Exception as e:
                logger.error(f"Failed to retrieve secret {key}: {e}")
                return None
    
    def get_secret_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get secret metadata without the value."""
        with self._lock:
            if key not in self._secrets:
                return None
            
            secret_data = self._secrets[key].copy()
            # Remove the actual value
            secret_data.pop("value", None)
            secret_data["has_value"] = True
            
            return secret_data
    
    def delete_secret(self, key: str) -> bool:
        """Delete a secret."""
        with self._lock:
            try:
                if key not in self._secrets:
                    logger.warning(f"Secret not found for deletion: {key}")
                    return False
                
                del self._secrets[key]
                self._save_secrets()
                
                logger.info(f"Deleted secret: {key}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to delete secret {key}: {e}")
                return False
    
    def list_secrets(self, include_values: bool = False) -> Dict[str, Dict[str, Any]]:
        """List all secrets."""
        with self._lock:
            result = {}
            
            for key, secret_data in self._secrets.items():
                info = secret_data.copy()
                if not include_values:
                    info.pop("value", None)
                    info["has_value"] = True
                result[key] = info
            
            return result
    
    def rotate_secret(self, key: str, new_value: str) -> bool:
        """Rotate a secret with a new value."""
        with self._lock:
            try:
                if key not in self._secrets:
                    logger.warning(f"Cannot rotate non-existent secret: {key}")
                    return False
                
                old_value = self._secrets[key]["value"]
                
                # Update with new value
                self._secrets[key]["value"] = new_value
                self._secrets[key]["updated_at"] = datetime.utcnow().isoformat()
                
                # Store rotation history
                if "rotation_history" not in self._secrets[key]:
                    self._secrets[key]["rotation_history"] = []
                
                self._secrets[key]["rotation_history"].append({
                    "rotated_at": datetime.utcnow().isoformat(),
                    "previous_value_hash": hashlib.sha256(old_value.encode()).hexdigest()
                })
                
                # Keep only last 10 rotations
                if len(self._secrets[key]["rotation_history"]) > 10:
                    self._secrets[key]["rotation_history"] = self._secrets[key]["rotation_history"][-10:]
                
                self._save_secrets()
                logger.info(f"Rotated secret: {key}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to rotate secret {key}: {e}")
                return False
    
    def backup_secrets(self, backup_path: Optional[str] = None) -> str:
        """Create a backup of all secrets."""
        with self._lock:
            if backup_path is None:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                backup_path = Path(self.storage_path) / f"secrets_backup_{timestamp}.enc"
            
            try:
                secrets_json = json.dumps(self._secrets, default=str)
                encrypted_data = self._encrypt(secrets_json)
                
                with open(backup_path, 'w') as f:
                    f.write(encrypted_data)
                
                logger.info(f"Secrets backup created: {backup_path}")
                return str(backup_path)
                
            except Exception as e:
                logger.error(f"Failed to backup secrets: {e}")
                raise
    
    def restore_secrets(self, backup_path: str, merge: bool = False) -> bool:
        """Restore secrets from backup."""
        with self._lock:
            try:
                backup_file = Path(backup_path)
                if not backup_file.exists():
                    raise FileNotFoundError(f"Backup file not found: {backup_path}")
                
                with open(backup_file, 'r') as f:
                    encrypted_data = f.read()
                
                decrypted_json = self._decrypt(encrypted_data)
                restored_secrets = json.loads(decrypted_json)
                
                if merge:
                    # Merge with existing secrets
                    self._secrets.update(restored_secrets)
                    logger.info("Merged secrets from backup")
                else:
                    # Replace all secrets
                    self._secrets = restored_secrets
                    logger.info("Restored all secrets from backup")
                
                self._save_secrets()
                return True
                
            except Exception as e:
                logger.error(f"Failed to restore secrets: {e}")
                return False
    
    def cleanup_old_secrets(self, days_unused: int = 90) -> int:
        """Clean up secrets that haven't been accessed recently."""
        with self._lock:
            cutoff_date = datetime.utcnow() - timedelta(days=days_unused)
            removed_count = 0
            
            keys_to_remove = []
            for key, secret_data in self._secrets.items():
                last_accessed = secret_data.get("last_accessed")
                if last_accessed:
                    last_accessed_date = datetime.fromisoformat(last_accessed)
                    if last_accessed_date < cutoff_date:
                        keys_to_remove.append(key)
                else:
                    # If never accessed, check creation date
                    created_date = datetime.fromisoformat(secret_data["created_at"])
                    if created_date < cutoff_date:
                        keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._secrets[key]
                removed_count += 1
                logger.info(f"Removed unused secret: {key}")
            
            if removed_count > 0:
                self._save_secrets()
                logger.info(f"Cleaned up {removed_count} unused secrets")
            
            return removed_count
    
    def validate_master_key(self, master_key: str) -> bool:
        """Validate if the provided master key matches the current one."""
        if not self._master_key_hash:
            return False
        
        provided_hash = self._hash_key(master_key)
        return provided_hash == self._master_key_hash
    
    def change_master_key(self, old_key: str, new_key: str) -> bool:
        """Change the master encryption key."""
        with self._lock:
            try:
                # Verify old key
                if not self.validate_master_key(old_key):
                    raise ValueError("Invalid old master key")
                
                # Create new encryption
                old_fernet = self._fernet
                self._initialize_encryption(new_key)
                
                # Re-encrypt all secrets with new key
                if self._secrets:
                    # Export with old key
                    secrets_json = json.dumps(self._secrets, default=str)
                    
                    # Import with new key
                    self._secrets = json.loads(secrets_json)
                    self._save_secrets()
                
                logger.info("Master key changed successfully")
                return True
                
            except Exception as e:
                logger.error(f"Failed to change master key: {e}")
                # Restore old encryption if possible
                try:
                    self._fernet = old_fernet
                except:
                    pass
                return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get secret manager statistics."""
        with self._lock:
            total_secrets = len(self._secrets)
            accessed_secrets = sum(1 for s in self._secrets.values() if s.get("last_accessed"))
            never_accessed = total_secrets - accessed_secrets
            
            # Calculate age statistics
            now = datetime.utcnow()
            ages = []
            for secret_data in self._secrets.values():
                created = datetime.fromisoformat(secret_data["created_at"])
                ages.append((now - created).days)
            
            return {
                "total_secrets": total_secrets,
                "accessed_secrets": accessed_secrets,
                "never_accessed": never_accessed,
                "average_age_days": sum(ages) / len(ages) if ages else 0,
                "oldest_secret_days": max(ages) if ages else 0,
                "newest_secret_days": min(ages) if ages else 0,
                "storage_path": self.storage_path,
                "encryption_enabled": self._fernet is not None
            }
    
    def _validate_key(self, key: str) -> bool:
        """Validate secret key format."""
        if not key:
            return False
        
        # Key should be alphanumeric with underscores and hyphens
        import re
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, key)) and len(key) <= 100
    
    @contextmanager
    def temporary_secret(self, key: str, value: str):
        """Context manager for temporary secrets."""
        original_value = self.get_secret(key)
        try:
            self.store_secret(key, value)
            yield value
        finally:
            if original_value is not None:
                self.store_secret(key, original_value)
            else:
                self.delete_secret(key)
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on secret manager."""
        try:
            # Test encryption/decryption
            test_data = "health_check_test"
            encrypted = self._encrypt(test_data)
            decrypted = self._decrypt(encrypted)
            
            encryption_working = decrypted == test_data
            
            # Test storage access
            stats = self.get_stats()
            
            return {
                "status": "healthy" if encryption_working else "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "encryption_working": encryption_working,
                "secret_count": stats["total_secrets"],
                "storage_accessible": True,
                "master_key_set": self._master_key_hash is not None
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "encryption_working": False,
                "storage_accessible": False,
                "master_key_set": self._master_key_hash is not None
            }


# Global secret manager instance
secret_manager = SecretManager()
