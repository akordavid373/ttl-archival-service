import json
import hashlib
import time
import logging
from typing import Optional, Dict, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Request

from ..models.audit_log import AuditLog, AuditAction, AuditSeverity

# Configure audit logger
audit_logger = logging.getLogger("audit")

class AuditEvent:
    """
    Represents an audit event before it's written to the database
    """
    def __init__(
        self,
        action: Union[AuditAction, str],
        description: str,
        user_id: Optional[str] = None,
        severity: Union[AuditSeverity, str] = AuditSeverity.MEDIUM,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        status_code: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        compliance_category: Optional[str] = None,
        retention_days: Optional[int] = None,
        legal_hold: bool = False,
        service_name: str = "ttl-archival-service"
    ):
        self.action = action if isinstance(action, AuditAction) else AuditAction(action)
        self.description = description
        self.user_id = user_id
        self.severity = severity if isinstance(severity, AuditSeverity) else AuditSeverity(severity)
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.resource_name = resource_name
        self.details = details
        self.old_values = old_values
        self.new_values = new_values
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.session_id = session_id
        self.endpoint = endpoint
        self.method = method
        self.status_code = status_code
        self.success = success
        self.error_message = error_message
        self.duration_ms = duration_ms
        self.compliance_category = compliance_category
        self.retention_days = retention_days
        self.legal_hold = legal_hold
        self.service_name = service_name
        self.timestamp = datetime.utcnow()

    def to_audit_log(self) -> AuditLog:
        """Convert AuditEvent to AuditLog model instance"""
        # Generate unique hash for integrity
        hash_data = {
            'action': self.action.value,
            'description': self.description,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat(),
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'success': self.success
        }
        event_hash = hashlib.sha256(json.dumps(hash_data, sort_keys=True).encode()).hexdigest()
        
        return AuditLog(
            action=self.action,
            severity=self.severity,
            user_id=self.user_id,
            user_agent=self.user_agent,
            ip_address=self.ip_address,
            session_id=self.session_id,
            resource_type=self.resource_type,
            resource_id=self.resource_id,
            resource_name=self.resource_name,
            description=self.description,
            details=json.dumps(self.details) if self.details else None,
            old_values=json.dumps(self.old_values) if self.old_values else None,
            new_values=json.dumps(self.new_values) if self.new_values else None,
            service_name=self.service_name,
            endpoint=self.endpoint,
            method=self.method,
            status_code=self.status_code,
            success=self.success,
            error_message=self.error_message,
            duration_ms=self.duration_ms,
            compliance_category=self.compliance_category,
            retention_days=self.retention_days or 2555,  # Default 7 years
            legal_hold=self.legal_hold,
            timestamp=self.timestamp,
            event_hash=event_hash
        )

class AuditLogger:
    """
    Comprehensive audit logging utility for tracking all system events
    """
    
    def __init__(self):
        self.logger = audit_logger
        
    def log_event(
        self,
        db: Session,
        event: AuditEvent,
        async_logging: bool = True
    ) -> Optional[AuditLog]:
        """
        Log an audit event to the database
        
        Args:
            db: Database session
            event: AuditEvent to log
            async_logging: Whether to log asynchronously (if implemented)
            
        Returns:
            Created AuditLog instance or None if failed
        """
        try:
            audit_log = event.to_audit_log()
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            
            # Also log to standard logger for immediate visibility
            log_level = {
                AuditSeverity.LOW: logging.INFO,
                AuditSeverity.MEDIUM: logging.INFO,
                AuditSeverity.HIGH: logging.WARNING,
                AuditSeverity.CRITICAL: logging.ERROR
            }.get(event.severity, logging.INFO)
            
            self.logger.log(
                log_level,
                f"Audit: {event.action.value} - {event.description} - User: {event.user_id} - Success: {event.success}"
            )
            
            return audit_log
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {e}")
            db.rollback()
            return None
    
    def log_from_request(
        self,
        db: Session,
        request: Request,
        action: Union[AuditAction, str],
        description: str,
        user_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        **kwargs
    ) -> Optional[AuditLog]:
        """
        Log an audit event from an HTTP request
        
        Args:
            db: Database session
            request: FastAPI Request object
            action: Audit action
            description: Event description
            user_id: User identifier
            success: Whether the operation succeeded
            error_message: Error message if failed
            duration_ms: Operation duration in milliseconds
            **kwargs: Additional event parameters
            
        Returns:
            Created AuditLog instance or None if failed
        """
        # Extract request information
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent")
        session_id = request.headers.get("x-session-id")
        
        event = AuditEvent(
            action=action,
            description=description,
            user_id=user_id,
            ip_address=client_ip,
            user_agent=user_agent,
            session_id=session_id,
            endpoint=str(request.url),
            method=request.method,
            success=success,
            error_message=error_message,
            duration_ms=duration_ms,
            **kwargs
        )
        
        return self.log_event(db, event)
    
    def log_user_action(
        self,
        db: Session,
        user_id: str,
        action: Union[AuditAction, str],
        description: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        **kwargs
    ) -> Optional[AuditLog]:
        """
        Log a user action for compliance tracking
        
        Args:
            db: Database session
            user_id: User identifier
            action: Action performed
            description: Description of the action
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            resource_name: Name of resource affected
            old_values: Previous values (for updates)
            new_values: New values (for updates)
            ip_address: User's IP address
            **kwargs: Additional parameters
            
        Returns:
            Created AuditLog instance or None if failed
        """
        event = AuditEvent(
            action=action,
            description=description,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            compliance_category="USER_ACTIVITY",
            **kwargs
        )
        
        return self.log_event(db, event)
    
    def log_data_change(
        self,
        db: Session,
        user_id: str,
        action: Union[AuditAction, str],
        resource_type: str,
        resource_id: str,
        resource_name: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[AuditLog]:
        """
        Log data modifications for audit trail
        
        Args:
            db: Database session
            user_id: User identifier
            action: Data action (create, update, delete)
            resource_type: Type of data modified
            resource_id: ID of data modified
            resource_name: Name of data modified
            old_values: Previous values
            new_values: New values
            **kwargs: Additional parameters
            
        Returns:
            Created AuditLog instance or None if failed
        """
        event = AuditEvent(
            action=action,
            description=f"{action.value} on {resource_type} '{resource_name}'",
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            old_values=old_values,
            new_values=new_values,
            compliance_category="DATA_INTEGRITY",
            severity=AuditSeverity.HIGH,
            **kwargs
        )
        
        return self.log_event(db, event)
    
    def log_security_event(
        self,
        db: Session,
        event_type: str,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[AuditLog]:
        """
        Log security-related events
        
        Args:
            db: Database session
            event_type: Type of security event
            description: Description of the security event
            user_id: User identifier if applicable
            ip_address: IP address involved
            details: Additional security event details
            **kwargs: Additional parameters
            
        Returns:
            Created AuditLog instance or None if failed
        """
        event = AuditEvent(
            action=AuditAction.SECURITY_EVENT,
            description=f"Security Event: {description}",
            user_id=user_id,
            ip_address=ip_address,
            details=details,
            compliance_category="SECURITY",
            severity=AuditSeverity.CRITICAL,
            **kwargs
        )
        
        return self.log_event(db, event)
    
    def log_system_event(
        self,
        db: Session,
        event_type: str,
        description: str,
        details: Optional[Dict[str, Any]] = None,
        severity: Union[AuditSeverity, str] = AuditSeverity.LOW,
        **kwargs
    ) -> Optional[AuditLog]:
        """
        Log system-level events
        
        Args:
            db: Database session
            event_type: Type of system event
            description: Description of the system event
            details: Additional system event details
            severity: Severity level
            **kwargs: Additional parameters
            
        Returns:
            Created AuditLog instance or None if failed
        """
        event = AuditEvent(
            action=AuditAction.SYSTEM_EVENT,
            description=f"System Event: {description}",
            details=details,
            severity=severity,
            compliance_category="SYSTEM",
            **kwargs
        )
        
        return self.log_event(db, event)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to client IP
        return request.client.host if request.client else "unknown"

# Global audit logger instance
audit_logger_instance = AuditLogger()

# Convenience functions for common audit operations
def log_user_login(db: Session, user_id: str, ip_address: str, user_agent: str = None, success: bool = True) -> Optional[AuditLog]:
    """Log user login attempt"""
    return audit_logger_instance.log_user_action(
        db=db,
        user_id=user_id,
        action=AuditAction.USER_LOGIN,
        description=f"User login {'successful' if success else 'failed'}",
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        severity=AuditSeverity.MEDIUM if success else AuditSeverity.HIGH
    )

def log_user_logout(db: Session, user_id: str, ip_address: str) -> Optional[AuditLog]:
    """Log user logout"""
    return audit_logger_instance.log_user_action(
        db=db,
        user_id=user_id,
        action=AuditAction.USER_LOGOUT,
        description="User logout",
        ip_address=ip_address
    )

def log_policy_change(db: Session, user_id: str, policy_id: str, policy_name: str, 
                     old_values: Dict[str, Any] = None, new_values: Dict[str, Any] = None) -> Optional[AuditLog]:
    """Log policy changes"""
    return audit_logger_instance.log_data_change(
        db=db,
        user_id=user_id,
        action=AuditAction.POLICY_UPDATE,
        resource_type="policy",
        resource_id=policy_id,
        resource_name=policy_name,
        old_values=old_values,
        new_values=new_values
    )

def log_archive_operation(db: Session, user_id: str, action: AuditAction, 
                         archive_id: str, archive_name: str, **kwargs) -> Optional[AuditLog]:
    """Log archive operations"""
    return audit_logger_instance.log_user_action(
        db=db,
        user_id=user_id,
        action=action,
        description=f"{action.value} archive '{archive_name}'",
        resource_type="archive",
        resource_id=archive_id,
        resource_name=archive_name,
        **kwargs
    )
