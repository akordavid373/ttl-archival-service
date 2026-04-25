from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from enum import Enum
from .database import Base

class AuditAction(str, Enum):
    """Audit action types"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"
    DATA_CREATE = "data_create"
    DATA_READ = "data_read"
    DATA_UPDATE = "data_update"
    DATA_DELETE = "data_delete"
    POLICY_CREATE = "policy_create"
    POLICY_UPDATE = "policy_update"
    POLICY_DELETE = "policy_delete"
    ARCHIVE_CREATE = "archive_create"
    ARCHIVE_DELETE = "archive_delete"
    ARCHIVE_RESTORE = "archive_restore"
    CLEANUP_TRIGGER = "cleanup_trigger"
    SETTINGS_UPDATE = "settings_update"
    ADMIN_ACTION = "admin_action"
    SYSTEM_EVENT = "system_event"
    SECURITY_EVENT = "security_event"
    API_ACCESS = "api_access"
    EXPORT_DATA = "export_data"
    IMPORT_DATA = "import_data"

class AuditSeverity(str, Enum):
    """Audit severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditLog(Base):
    """
    Immutable audit log model for tracking all system events
    """
    __tablename__ = "audit_logs"
    
    # Primary identifier
    id = Column(Integer, primary_key=True, index=True)
    
    # Event information
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    severity = Column(SQLEnum(AuditSeverity), nullable=False, default=AuditSeverity.MEDIUM, index=True)
    
    # User information
    user_id = Column(String(255), index=True)  # User identifier (can be email, username, or UUID)
    user_agent = Column(Text)  # Browser/client user agent
    ip_address = Column(String(45), index=True)  # IPv4 or IPv6 address
    session_id = Column(String(255), index=True)  # Session identifier for correlation
    
    # Resource information
    resource_type = Column(String(100), index=True)  # Type of resource (policy, archive, user, etc.)
    resource_id = Column(String(255), index=True)  # ID of the affected resource
    resource_name = Column(String(255))  # Human-readable name of resource
    
    # Event details
    description = Column(Text, nullable=False)  # Human-readable description of the event
    details = Column(Text)  # JSON string with additional event details
    old_values = Column(Text)  # JSON string with previous values (for updates)
    new_values = Column(Text)  # JSON string with new values (for updates)
    
    # System information
    service_name = Column(String(100), default="ttl-archival-service", index=True)
    endpoint = Column(String(255))  # API endpoint that triggered the event
    method = Column(String(10))  # HTTP method (GET, POST, PUT, DELETE, etc.)
    status_code = Column(Integer)  # HTTP status code
    
    # Result information
    success = Column(Boolean, nullable=False, default=True, index=True)
    error_message = Column(Text)  # Error message if the action failed
    duration_ms = Column(Integer)  # Duration of the operation in milliseconds
    
    # Compliance and retention
    compliance_category = Column(String(100), index=True)  # Compliance category (SOX, GDPR, HIPAA, etc.)
    retention_days = Column(Integer, default=2555)  # Default 7 years retention
    legal_hold = Column(Boolean, default=False)  # Legal hold flag to prevent deletion
    
    # Timestamps (immutable)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Hash for integrity verification
    event_hash = Column(String(64), unique=True, nullable=False, index=True)  # SHA-256 hash
    
    # Indexes for performance and compliance
    __table_args__ = (
        Index('idx_action_timestamp', 'action', 'timestamp'),
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_resource_timestamp', 'resource_type', 'resource_id', 'timestamp'),
        Index('idx_severity_timestamp', 'severity', 'timestamp'),
        Index('idx_success_timestamp', 'success', 'timestamp'),
        Index('idx_compliance_timestamp', 'compliance_category', 'timestamp'),
        Index('idx_session_timestamp', 'session_id', 'timestamp'),
        Index('idx_ip_timestamp', 'ip_address', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id='{self.user_id}', timestamp={self.timestamp})>"
    
    @property
    def is_expired(self):
        """Check if the audit log has exceeded its retention period"""
        if self.legal_hold:
            return False
        expiry_date = self.timestamp + timedelta(days=self.retention_days)
        return datetime.utcnow() > expiry_date
    
    @property
    def days_until_expiry(self):
        """Calculate days until the audit log expires"""
        if self.legal_hold or self.is_expired:
            return 0
        expiry_date = self.timestamp + timedelta(days=self.retention_days)
        delta = expiry_date - datetime.utcnow()
        return max(0, delta.days)
    
    def to_dict(self):
        """Convert audit log to dictionary for API responses"""
        return {
            'id': self.id,
            'action': self.action.value,
            'severity': self.severity.value,
            'user_id': self.user_id,
            'user_agent': self.user_agent,
            'ip_address': self.ip_address,
            'session_id': self.session_id,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'description': self.description,
            'details': self.details,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'service_name': self.service_name,
            'endpoint': self.endpoint,
            'method': self.method,
            'status_code': self.status_code,
            'success': self.success,
            'error_message': self.error_message,
            'duration_ms': self.duration_ms,
            'compliance_category': self.compliance_category,
            'retention_days': self.retention_days,
            'legal_hold': self.legal_hold,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'event_hash': self.event_hash,
            'is_expired': self.is_expired,
            'days_until_expiry': self.days_until_expiry
        }

class AuditRetentionPolicy(Base):
    """
    Audit log retention policies for different categories of events
    """
    __tablename__ = "audit_retention_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # Policy configuration
    action_types = Column(Text)  # JSON array of action types this policy applies to
    severity_levels = Column(Text)  # JSON array of severity levels
    compliance_categories = Column(Text)  # JSON array of compliance categories
    
    # Retention settings
    retention_days = Column(Integer, nullable=False, default=2555)  # Default 7 years
    legal_hold_enabled = Column(Boolean, default=False)
    auto_archive = Column(Boolean, default=True)  # Archive instead of delete
    archive_location = Column(String(500))  # Where to archive old logs
    
    # Policy status
    is_active = Column(Boolean, default=True, index=True)
    priority = Column(Integer, default=0)  # Higher priority policies override lower ones
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<AuditRetentionPolicy(id={self.id}, name='{self.name}', retention_days={self.retention_days})>"
