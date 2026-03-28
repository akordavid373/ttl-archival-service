from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from ...database import get_db
from ...utils.audit_logger import audit_logger_instance, AuditAction

logger = logging.getLogger(__name__)
router = APIRouter()

# Enhanced schemas for v2
class NotificationChannel(BaseModel):
    """Notification channel configuration"""
    type: str = Field(..., regex="^(email|sms|slack|webhook|push)$")
    config: Dict[str, Any] = Field(..., description="Channel-specific configuration")
    enabled: bool = Field(True, description="Channel enabled status")

class NotificationRule(BaseModel):
    """Notification rule configuration"""
    name: str = Field(..., description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    event_types: List[str] = Field(..., description="Event types to match")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Matching conditions")
    channels: List[NotificationChannel] = Field(..., description="Notification channels")
    template: Optional[str] = Field(None, description="Message template")
    severity_filter: Optional[List[str]] = Field(None, description="Severity filter")
    rate_limit: Optional[Dict[str, Any]] = Field(None, description="Rate limiting configuration")
    active: bool = Field(True, description="Rule active status")

class NotificationMessage(BaseModel):
    """Notification message"""
    id: str
    rule_id: int
    event_type: str
    channel_type: str
    recipient: str
    subject: Optional[str]
    body: str
    metadata: Optional[Dict[str, Any]]
    status: str
    created_at: datetime
    sent_at: Optional[datetime]
    error_message: Optional[str]

class NotificationRuleResponse(BaseModel):
    """Notification rule response"""
    id: int
    name: str
    description: Optional[str]
    event_types: List[str]
    conditions: Optional[Dict[str, Any]]
    channels: List[NotificationChannel]
    template: Optional[str]
    severity_filter: Optional[List[str]]
    rate_limit: Optional[Dict[str, Any]]
    active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_triggered: Optional[datetime]
    trigger_count: int
    success_count: int
    failure_count: int

class NotificationStats(BaseModel):
    """Notification statistics"""
    total_rules: int
    active_rules: int
    total_notifications: int
    successful_notifications: int
    failed_notifications: int
    notifications_by_channel: Dict[str, int]
    notifications_by_event: Dict[str, int]
    average_delivery_time: float

class NotificationTestRequest(BaseModel):
    """Notification test request"""
    rule_id: int
    event_type: str
    test_data: Optional[Dict[str, Any]] = Field(None, description="Test event data")
    channels: Optional[List[str]] = Field(None, description="Specific channels to test")

# Initialize notification service (placeholder)
notification_service = None

@router.post("/rules", response_model=NotificationRuleResponse, status_code=201)
async def create_notification_rule(
    rule: NotificationRule,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new notification rule"""
    try:
        # Validate rule
        validation = await _validate_notification_rule(rule)
        if not validation.valid:
            raise HTTPException(
                status_code=400,
                detail={"errors": validation.errors, "warnings": validation.warnings}
            )
        
        # Create rule
        rule_id = await _create_notification_rule(db, rule.dict())
        
        # Log rule creation
        background_tasks.add_task(
            _log_notification_event,
            "rule.created",
            {"rule_id": rule_id, "name": rule.name}
        )
        
        return await _get_notification_rule_response(db, rule_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating notification rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rules", response_model=List[NotificationRuleResponse])
async def list_notification_rules(
    active_only: bool = Query(False, description="Filter active rules only"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List notification rules with filtering"""
    try:
        rules = await _get_notification_rules(db, active_only, event_type, page, limit)
        return rules
        
    except Exception as e:
        logger.error(f"Error listing notification rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rules/{rule_id}", response_model=NotificationRuleResponse)
async def get_notification_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific notification rule"""
    try:
        rule = await _get_notification_rule(db, rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Notification rule not found")
        
        return rule
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/rules/{rule_id}", response_model=NotificationRuleResponse)
async def update_notification_rule(
    rule_id: int,
    rule_update: NotificationRule,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update a notification rule"""
    try:
        # Check if rule exists
        existing = await _get_notification_rule(db, rule_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Notification rule not found")
        
        # Validate rule
        validation = await _validate_notification_rule(rule_update)
        if not validation.valid:
            raise HTTPException(
                status_code=400,
                detail={"errors": validation.errors, "warnings": validation.warnings}
            )
        
        # Update rule
        await _update_notification_rule(db, rule_id, rule_update.dict())
        
        # Log rule update
        background_tasks.add_task(
            _log_notification_event,
            "rule.updated",
            {"rule_id": rule_id, "name": rule_update.name}
        )
        
        return await _get_notification_rule_response(db, rule_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating notification rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/rules/{rule_id}")
async def delete_notification_rule(
    rule_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Delete a notification rule"""
    try:
        rule = await _get_notification_rule(db, rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Notification rule not found")
        
        # Delete rule
        await _delete_notification_rule(db, rule_id)
        
        # Log rule deletion
        background_tasks.add_task(
            _log_notification_event,
            "rule.deleted",
            {"rule_id": rule_id, "name": rule.name}
        )
        
        return {"message": "Notification rule deleted successfully", "rule_id": rule_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rules/{rule_id}/test")
async def test_notification_rule(
    rule_id: int,
    request: NotificationTestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Test a notification rule"""
    try:
        rule = await _get_notification_rule(db, rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Notification rule not found")
        
        # Send test notification
        test_result = await _send_test_notification(rule, request.event_type, request.test_data, request.channels)
        
        return {
            "message": "Test notification sent",
            "rule_id": rule_id,
            "test_result": test_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing notification rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rules/{rule_id}/activate")
async def activate_notification_rule(
    rule_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Activate a notification rule"""
    try:
        rule = await _get_notification_rule(db, rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Notification rule not found")
        
        # Activate rule
        await _activate_notification_rule(db, rule_id)
        
        # Log activation
        background_tasks.add_task(
            _log_notification_event,
            "rule.activated",
            {"rule_id": rule_id, "name": rule.name}
        )
        
        return {"message": "Notification rule activated successfully", "rule_id": rule_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating notification rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rules/{rule_id}/deactivate")
async def deactivate_notification_rule(
    rule_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Deactivate a notification rule"""
    try:
        rule = await _get_notification_rule(db, rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Notification rule not found")
        
        # Deactivate rule
        await _deactivate_notification_rule(db, rule_id)
        
        # Log deactivation
        background_tasks.add_task(
            _log_notification_event,
            "rule.deactivated",
            {"rule_id": rule_id, "name": rule.name}
        )
        
        return {"message": "Notification rule deactivated successfully", "rule_id": rule_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating notification rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages", response_model=List[NotificationMessage])
async def list_notification_messages(
    rule_id: Optional[int] = Query(None, description="Filter by rule ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    channel_type: Optional[str] = Query(None, description="Filter by channel type"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List notification messages"""
    try:
        messages = await _get_notification_messages(db, rule_id, status, channel_type, limit)
        return messages
        
    except Exception as e:
        logger.error(f"Error listing notification messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages/{message_id}", response_model=NotificationMessage)
async def get_notification_message(
    message_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific notification message"""
    try:
        message = await _get_notification_message(db, message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Notification message not found")
        
        return message
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages/{message_id}/resend")
async def resend_notification_message(
    message_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Resend a notification message"""
    try:
        message = await _get_notification_message(db, message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Notification message not found")
        
        # Resend message
        await _resend_notification_message(db, message_id)
        
        return {"message": "Notification message resent successfully", "message_id": message_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resending notification message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary", response_model=NotificationStats)
async def get_notification_stats(
    period_days: int = Query(30, description="Period in days for statistics"),
    db: Session = Depends(get_db)
):
    """Get notification statistics"""
    try:
        stats = await _get_notification_stats(db, period_days)
        return stats
        
    except Exception as e:
        logger.error(f"Error getting notification stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger")
async def trigger_notification(
    event_type: str = Field(..., description="Event type"),
    event_data: Dict[str, Any] = Field(..., description="Event data"),
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger notification for an event"""
    try:
        # Trigger notification
        triggered_rules = await _trigger_notification(db, event_type, event_data)
        
        return {
            "message": "Notification triggered",
            "event_type": event_type,
            "triggered_rules": len(triggered_rules)
        }
        
    except Exception as e:
        logger.error(f"Error triggering notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_notification_templates(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    db: Session = Depends(get_db)
):
    """Get notification message templates"""
    try:
        templates = await _get_notification_templates(db, event_type)
        return templates
        
    except Exception as e:
        logger.error(f"Error getting notification templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
async def _validate_notification_rule(rule: NotificationRule) -> Dict[str, Any]:
    """Validate notification rule"""
    errors = []
    warnings = []
    
    # Validate event types
    if not rule.event_types:
        errors.append("At least one event type is required")
    
    # Validate channels
    if not rule.channels:
        errors.append("At least one notification channel is required")
    
    for channel in rule.channels:
        if channel.type not in ['email', 'sms', 'slack', 'webhook', 'push']:
            errors.append(f"Invalid channel type: {channel.type}")
    
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

async def _create_notification_rule(db: Session, rule_data: Dict[str, Any]) -> int:
    """Create notification rule in database"""
    # This would implement actual rule creation
    return 1

async def _get_notification_rules(db: Session, active_only: bool, event_type: Optional[str], page: int, limit: int) -> List[NotificationRuleResponse]:
    """Get notification rules from database"""
    # This would implement actual rule retrieval
    return []

async def _get_notification_rule(db: Session, rule_id: int) -> Optional[NotificationRuleResponse]:
    """Get specific notification rule"""
    # This would implement actual rule retrieval
    return None

async def _get_notification_rule_response(db: Session, rule_id: int) -> NotificationRuleResponse:
    """Get notification rule response"""
    return NotificationRuleResponse(
        id=rule_id,
        name="Test Rule",
        description="Test notification rule",
        event_types=["test.event"],
        conditions={},
        channels=[],
        template=None,
        severity_filter=None,
        rate_limit=None,
        active=True,
        created_at=datetime.now(),
        updated_at=None,
        last_triggered=None,
        trigger_count=0,
        success_count=0,
        failure_count=0
    )

async def _update_notification_rule(db: Session, rule_id: int, rule_data: Dict[str, Any]):
    """Update notification rule in database"""
    # This would implement actual rule update

async def _delete_notification_rule(db: Session, rule_id: int):
    """Delete notification rule from database"""
    # This would implement actual rule deletion

async def _send_test_notification(rule: NotificationRuleResponse, event_type: str, test_data: Optional[Dict[str, Any]], channels: Optional[List[str]]) -> Dict[str, Any]:
    """Send test notification"""
    # This would implement actual test notification sending
    return {"status": "sent", "channels": ["email"]}

async def _activate_notification_rule(db: Session, rule_id: int):
    """Activate notification rule"""
    # This would implement actual rule activation

async def _deactivate_notification_rule(db: Session, rule_id: int):
    """Deactivate notification rule"""
    # This would implement actual rule deactivation

async def _get_notification_messages(db: Session, rule_id: Optional[int], status: Optional[str], channel_type: Optional[str], limit: int) -> List[NotificationMessage]:
    """Get notification messages"""
    # This would implement actual message retrieval
    return []

async def _get_notification_message(db: Session, message_id: str) -> Optional[NotificationMessage]:
    """Get specific notification message"""
    # This would implement actual message retrieval
    return None

async def _resend_notification_message(db: Session, message_id: str):
    """Resend notification message"""
    # This would implement actual message resending

async def _get_notification_stats(db: Session, period_days: int) -> NotificationStats:
    """Get notification statistics"""
    return NotificationStats(
        total_rules=0,
        active_rules=0,
        total_notifications=0,
        successful_notifications=0,
        failed_notifications=0,
        notifications_by_channel={},
        notifications_by_event={},
        average_delivery_time=0.0
    )

async def _trigger_notification(db: Session, event_type: str, event_data: Dict[str, Any]) -> List[int]:
    """Trigger notification for event"""
    # This would implement actual notification triggering
    return []

async def _get_notification_templates(db: Session, event_type: Optional[str]) -> List[Dict[str, Any]]:
    """Get notification templates"""
    # This would implement actual template retrieval
    return []

async def _log_notification_event(event_type: str, data: Dict[str, Any]):
    """Log notification event"""
    logger.info(f"Notification event: {event_type}, data: {data}")
