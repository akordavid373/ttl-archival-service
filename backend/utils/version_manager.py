from typing import Dict, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)


class VersionStatus(Enum):
    """API version status"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"
    DEVELOPMENT = "development"


@dataclass
class VersionInfo:
    """Information about an API version"""
    version: str
    status: VersionStatus
    release_date: date
    deprecation_date: Optional[date] = None
    sunset_date: Optional[date] = None
    recommended_version: Optional[str] = None
    migration_guide: Optional[str] = None
    breaking_changes: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    backward_compatible: bool = True
    supported_until: Optional[date] = None
    
    @property
    def deprecated(self) -> bool:
        """Check if version is deprecated"""
        return self.status == VersionStatus.DEPRECATED
    
    @property
    def sunset(self) -> bool:
        """Check if version is sunset"""
        return self.status == VersionStatus.SUNSET
    
    def is_supported(self, current_date: Optional[date] = None) -> bool:
        """Check if version is currently supported"""
        if current_date is None:
            current_date = date.today()
        
        if self.status == VersionStatus.SUNSET:
            return False
        
        if self.supported_until:
            return current_date <= self.supported_until
        
        if self.sunset_date:
            return current_date < self.sunset_date
        
        return True


class VersionManager:
    """
    Manages API versioning information and operations.
    """
    
    def __init__(self):
        self.versions: Dict[str, VersionInfo] = {}
        self._initialize_default_versions()
    
    def _initialize_default_versions(self):
        """Initialize default API versions"""
        today = date.today()
        
        # Version 1.0 (current stable version)
        self.register_version(VersionInfo(
            version="v1",
            status=VersionStatus.ACTIVE,
            release_date=date(2024, 1, 1),
            backward_compatible=True,
            features=[
                "Basic CRUD operations for archives and policies",
                "Audit logging",
                "Search functionality",
                "Configuration management",
                "Performance monitoring"
            ]
        ))
        
        # Version 2.0 (latest version with new features)
        self.register_version(VersionInfo(
            version="v2",
            status=VersionStatus.ACTIVE,
            release_date=today,
            recommended_version="v2",
            backward_compatible=False,
            breaking_changes=[
                "Changed response format for archive records",
                "Modified authentication requirements",
                "Updated pagination parameters"
            ],
            features=[
                "Enhanced search with filters",
                "Batch operations",
                "Real-time notifications",
                "Advanced analytics",
                "Improved error handling",
                "Rate limiting",
                "Webhook support"
            ],
            migration_guide="/docs/migration/v1-to-v2"
        ))
    
    def register_version(self, version_info: VersionInfo):
        """Register a new API version"""
        self.versions[version_info.version] = version_info
        logger.info(f"Registered API version: {version_info.version}")
    
    def get_version_info(self, version: str) -> Optional[VersionInfo]:
        """Get information about a specific version"""
        return self.versions.get(version)
    
    def get_supported_versions(self, current_date: Optional[date] = None) -> Dict[str, VersionInfo]:
        """Get all currently supported versions"""
        supported = {}
        for version, info in self.versions.items():
            if info.is_supported(current_date):
                supported[version] = info
        return supported
    
    def get_latest_version(self) -> str:
        """Get the latest stable version"""
        active_versions = [
            version for version, info in self.versions.items()
            if info.status == VersionStatus.ACTIVE
        ]
        
        if not active_versions:
            # Fallback to highest version number
            return max(self.versions.keys(), key=self._version_key)
        
        # Return the most recent active version
        return max(active_versions, key=self._version_key)
    
    def get_recommended_version(self, current_version: Optional[str] = None) -> str:
        """Get the recommended version for users"""
        if current_version:
            version_info = self.get_version_info(current_version)
            if version_info and version_info.recommended_version:
                return version_info.recommended_version
        
        return self.get_latest_version()
    
    def is_version_supported(self, version: str, current_date: Optional[date] = None) -> bool:
        """Check if a specific version is supported"""
        version_info = self.get_version_info(version)
        if not version_info:
            return False
        return version_info.is_supported(current_date)
    
    def get_deprecated_versions(self, current_date: Optional[date] = None) -> Dict[str, VersionInfo]:
        """Get all deprecated versions"""
        deprecated = {}
        for version, info in self.versions.items():
            if info.deprecated and info.is_supported(current_date):
                deprecated[version] = info
        return deprecated
    
    def get_versions_needing_migration(self, days_ahead: int = 30) -> Dict[str, VersionInfo]:
        """Get versions that will be deprecated soon"""
        target_date = date.today()
        target_date = date.fromordinal(target_date.toordinal() + days_ahead)
        
        upcoming = {}
        for version, info in self.versions.items():
            if (info.deprecation_date and 
                info.deprecation_date <= target_date and 
                info.deprecation_date > date.today()):
                upcoming[version] = info
        
        return upcoming
    
    def validate_version_compatibility(
        self, 
        requested_version: str, 
        client_version: Optional[str] = None
    ) -> Dict[str, any]:
        """Validate version compatibility and return recommendations"""
        result = {
            "compatible": False,
            "requested_version": requested_version,
            "recommended_version": self.get_recommended_version(requested_version),
            "latest_version": self.get_latest_version(),
            "warnings": [],
            "errors": []
        }
        
        version_info = self.get_version_info(requested_version)
        if not version_info:
            result["errors"].append(f"Version '{requested_version}' is not supported")
            return result
        
        if not version_info.is_supported():
            result["errors"].append(f"Version '{requested_version}' is no longer supported")
            return result
        
        result["compatible"] = True
        
        # Add warnings for deprecated versions
        if version_info.deprecated:
            result["warnings"].append(
                f"Version '{requested_version}' is deprecated. "
                f"Please migrate to {result['recommended_version']}"
            )
            
            if version_info.deprecation_date:
                days_until = (version_info.deprecation_date - date.today()).days
                if days_until <= 30:
                    result["warnings"].append(
                        f"Version '{requested_version}' will be deprecated in {days_until} days"
                    )
        
        return result
    
    def _version_key(self, version: str) -> tuple:
        """Extract version key for sorting (e.g., 'v1' -> (1,), 'v2.1' -> (2, 1))"""
        # Remove 'v' prefix and split by dots
        version_num = version.lstrip('v')
        parts = version_num.split('.')
        return tuple(int(part) for part in parts)
    
    def get_migration_path(self, from_version: str, to_version: str) -> Optional[List[str]]:
        """Get migration path between versions"""
        if from_version == to_version:
            return []
        
        from_info = self.get_version_info(from_version)
        to_info = self.get_version_info(to_version)
        
        if not from_info or not to_info:
            return None
        
        # For now, return direct migration path
        # In the future, this could include intermediate versions
        return [from_version, to_version]
    
    def get_version_statistics(self) -> Dict[str, any]:
        """Get statistics about API versions"""
        today = date.today()
        
        stats = {
            "total_versions": len(self.versions),
            "active_versions": 0,
            "deprecated_versions": 0,
            "sunset_versions": 0,
            "development_versions": 0,
            "supported_versions": 0,
            "latest_version": self.get_latest_version(),
            "versions": {}
        }
        
        for version, info in self.versions.items():
            # Count by status
            if info.status == VersionStatus.ACTIVE:
                stats["active_versions"] += 1
            elif info.status == VersionStatus.DEPRECATED:
                stats["deprecated_versions"] += 1
            elif info.status == VersionStatus.SUNSET:
                stats["sunset_versions"] += 1
            elif info.status == VersionStatus.DEVELOPMENT:
                stats["development_versions"] += 1
            
            if info.is_supported():
                stats["supported_versions"] += 1
            
            # Add version-specific stats
            stats["versions"][version] = {
                "status": info.status.value,
                "release_date": info.release_date.isoformat(),
                "deprecation_date": info.deprecation_date.isoformat() if info.deprecation_date else None,
                "sunset_date": info.sunset_date.isoformat() if info.sunset_date else None,
                "backward_compatible": info.backward_compatible,
                "features_count": len(info.features),
                "breaking_changes_count": len(info.breaking_changes)
            }
        
        return stats


# Global version manager instance
version_manager = VersionManager()
