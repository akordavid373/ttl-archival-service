from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Request
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
class WebhookCreate(BaseModel):
    """Webhook creation schema for v2"""
    name: str = Field(..., description="Webhook name")
    url: str = Field(..., description="Webhook URL")
    events: List[str] = Field(..., description="Events to trigger webhook")
    secret: Optional[str] = Field(None, description="Webhook secret for validation")
    active: bool = Field(True, description="Webhook active status")
    retry_config: Optional[Dict[str, Any]] = Field(None, description="Retry configuration")
    headers: Optional[Dict[str, str]] = Field(None, description="Custom headers")
    timeout: int = Field(30, ge=1, le=300, description="Timeout in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Archive Creation Webhook",
                "url": "https://example.com/webhook",
                "events": ["archive.created", "archive.expired"],
                "secret": "webhook_secret",
                "active": True,
                "retry_config": {"max_retries": 3, "backoff": "exponential"},
                "headers": {"Authorization": "Bearer token"},
                "timeout": 30
            }
        }

class WebhookResponse(BaseModel):
    """Webhook response schema for v2"""
    id: int
    name: str
    url: str
    events: List[str]
    active: bool
    timeout: int
    headers: Optional[Dict[str, str]]
    retry_config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    last_triggered: Optional[datetime]
    success_count: int
    failure_count: int
    last_success: Optional[datetime]
    last_failure: Optional[datetime]

class WebhookDelivery(BaseModel):
    """Webhook delivery information"""
    id: int
    webhook_id: int
    event_type: str
    payload: Dict[str, Any]
    status: str
    response_code: Optional[int]
    response_body: Optional[str]
    attempt_count: int
    created_at: datetime
    delivered_at: Optional[datetime]
    error_message: Optional[str]

class WebhookTestRequest(BaseModel):
    """Webhook test request"""
    event_type: str = Field(..., description="Event type to test")
    test_payload: Optional[Dict[str, Any]] = Field(None, description="Custom test payload")

class WebhookStats(BaseModel):
    """Webhook statistics"""
    total_webhooks: int
    active_webhooks: int
    total_deliveries: int
    successful_deliveries: int
    failed_deliveries: int
    average_delivery_time: float
    most_common_events: List[Dict[str, Any]]

# Initialize webhook service (placeholder)
webhook_service = None

@router.post("/", response_model=WebhookResponse, status_code=201)
async def create_webhook(
    webhook: WebhookCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new webhook"""
    try:
        # Validate webhook URL
        validation = await _validate_webhook_url(webhook.url)
        if not validation.valid:
            raise HTTPException(status_code=400, detail=validation.errors)
        
        # Create webhook
        webhook_id = await _create_webhook(db, webhook.dict())
        
        # Log webhook creation
        background_tasks.add_task(
            _log_webhook_event,
            "webhook.created",
            {"webhook_id": webhook_id, "name": webhook.name}
        )
        
        return await _get_webhook_response(db, webhook_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    active_only: bool = Query(False, description="Filter active webhooks only"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List webhooks with filtering"""
    try:
        webhooks = await _get_webhooks(db, active_only, event_type, page, limit)
        return webhooks
        
    except Exception as e:
        logger.error(f"Error listing webhooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific webhook"""
    try:
        webhook = await _get_webhook(db, webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        return webhook
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: int,
    webhook_update: WebhookCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update a webhook"""
    try:
        # Check if webhook exists
        existing = await _get_webhook(db, webhook_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        # Validate webhook URL
        validation = await _validate_webhook_url(webhook_update.url)
        if not validation.valid:
            raise HTTPException(status_code=400, detail=validation.errors)
        
        # Update webhook
        await _update_webhook(db, webhook_id, webhook_update.dict())
        
        # Log webhook update
        background_tasks.add_task(
            _log_webhook_event,
            "webhook.updated",
            {"webhook_id": webhook_id, "name": webhook_update.name}
        )
        
        return await _get_webhook_response(db, webhook_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Delete a webhook"""
    try:
        webhook = await _get_webhook(db, webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        # Delete webhook
        await _delete_webhook(db, webhook_id)
        
        # Log webhook deletion
        background_tasks.add_task(
            _log_webhook_event,
            "webhook.deleted",
            {"webhook_id": webhook_id, "name": webhook.name}
        )
        
        return {"message": "Webhook deleted successfully", "webhook_id": webhook_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{webhook_id}/test")
async def test_webhook(
    webhook_id: int,
    request: WebhookTestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Test a webhook"""
    try:
        webhook = await _get_webhook(db, webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        # Send test webhook
        test_result = await _send_test_webhook(webhook, request.event_type, request.test_payload)
        
        return {
            "message": "Test webhook sent",
            "webhook_id": webhook_id,
            "test_result": test_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{webhook_id}/activate")
async def activate_webhook(
    webhook_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Activate a webhook"""
    try:
        webhook = await _get_webhook(db, webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        # Activate webhook
        await _activate_webhook(db, webhook_id)
        
        # Log activation
        background_tasks.add_task(
            _log_webhook_event,
            "webhook.activated",
            {"webhook_id": webhook_id, "name": webhook.name}
        )
        
        return {"message": "Webhook activated successfully", "webhook_id": webhook_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{webhook_id}/deactivate")
async def deactivate_webhook(
    webhook_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Deactivate a webhook"""
    try:
        webhook = await _get_webhook(db, webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        # Deactivate webhook
        await _deactivate_webhook(db, webhook_id)
        
        # Log deactivation
        background_tasks.add_task(
            _log_webhook_event,
            "webhook.deactivated",
            {"webhook_id": webhook_id, "name": webhook.name}
        )
        
        return {"message": "Webhook deactivated successfully", "webhook_id": webhook_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{webhook_id}/deliveries", response_model=List[WebhookDelivery])
async def get_webhook_deliveries(
    webhook_id: int,
    status: Optional[str] = Query(None, description="Filter by delivery status"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get webhook delivery history"""
    try:
        deliveries = await _get_webhook_deliveries(db, webhook_id, status, limit)
        return deliveries
        
    except Exception as e:
        logger.error(f"Error getting webhook deliveries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{webhook_id}/redeliver")
async def redeliver_webhook(
    webhook_id: int,
    delivery_id: Optional[int] = Query(None, description="Specific delivery to redeliver"),
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Redeliver a webhook"""
    try:
        webhook = await _get_webhook(db, webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        # Redeliver webhook
        if delivery_id:
            # Redeliver specific delivery
            await _redeliver_specific_delivery(db, webhook_id, delivery_id)
        else:
            # Redeliver failed deliveries
            await _redeliver_failed_deliveries(db, webhook_id)
        
        return {"message": "Webhook redelivery initiated", "webhook_id": webhook_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error redelivering webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary", response_model=WebhookStats)
async def get_webhook_stats(
    period_days: int = Query(30, description="Period in days for statistics"),
    db: Session = Depends(get_db)
):
    """Get webhook statistics"""
    try:
        stats = await _get_webhook_stats(db, period_days)
        return stats
        
    except Exception as e:
        logger.error(f"Error getting webhook stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger")
async def trigger_webhook_event(
    event_type: str = Field(..., description="Event type"),
    payload: Dict[str, Any] = Field(..., description="Event payload"),
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger webhook event manually"""
    try:
        # Trigger webhook event
        triggered_webhooks = await _trigger_webhook_event(db, event_type, payload)
        
        return {
            "message": "Webhook event triggered",
            "event_type": event_type,
            "triggered_webhooks": len(triggered_webhooks)
        }
        
    except Exception as e:
        logger.error(f"Error triggering webhook event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
async def _validate_webhook_url(url: str) -> Dict[str, Any]:
    """Validate webhook URL"""
    errors = []
    
    if not url.startswith(('http://', 'https://')):
        errors.append("URL must start with http:// or https://")
    
    return {"valid": len(errors) == 0, "errors": errors}

async def _create_webhook(db: Session, webhook_data: Dict[str, Any]) -> int:
    """Create webhook in database"""
    # This would implement actual webhook creation
    return 1

async def _get_webhooks(db: Session, active_only: bool, event_type: Optional[str], page: int, limit: int) -> List[WebhookResponse]:
    """Get webhooks from database"""
    # This would implement actual webhook retrieval
    return []

async def _get_webhook(db: Session, webhook_id: int) -> Optional[WebhookResponse]:
    """Get specific webhook"""
    # This would implement actual webhook retrieval
    return None

async def _get_webhook_response(db: Session, webhook_id: int) -> WebhookResponse:
    """Get webhook response"""
    # This would implement actual webhook response creation
    return WebhookResponse(
        id=webhook_id,
        name="Test Webhook",
        url="https://example.com/webhook",
        events=["test.event"],
        active=True,
        timeout=30,
        headers={},
        retry_config={},
        created_at=datetime.now(),
        updated_at=None,
        last_triggered=None,
        success_count=0,
        failure_count=0,
        last_success=None,
        last_failure=None
    )

async def _update_webhook(db: Session, webhook_id: int, webhook_data: Dict[str, Any]):
    """Update webhook in database"""
    # This would implement actual webhook update

async def _delete_webhook(db: Session, webhook_id: int):
    """Delete webhook from database"""
    # This would implement actual webhook deletion

async def _send_test_webhook(webhook: WebhookResponse, event_type: str, test_payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Send test webhook"""
    # This would implement actual test webhook sending
    return {"status": "sent", "response_code": 200}

async def _activate_webhook(db: Session, webhook_id: int):
    """Activate webhook"""
    # This would implement actual webhook activation

async def _deactivate_webhook(db: Session, webhook_id: int):
    """Deactivate webhook"""
    # This would implement actual webhook deactivation

async def _get_webhook_deliveries(db: Session, webhook_id: int, status: Optional[str], limit: int) -> List[WebhookDelivery]:
    """Get webhook deliveries"""
    # This would implement actual delivery retrieval
    return []

async def _redeliver_specific_delivery(db: Session, webhook_id: int, delivery_id: int):
    """Redeliver specific delivery"""
    # This would implement actual redelivery

async def _redeliver_failed_deliveries(db: Session, webhook_id: int):
    """Redeliver failed deliveries"""
    # This would implement actual redelivery

async def _get_webhook_stats(db: Session, period_days: int) -> WebhookStats:
    """Get webhook statistics"""
    return WebhookStats(
        total_webhooks=0,
        active_webhooks=0,
        total_deliveries=0,
        successful_deliveries=0,
        failed_deliveries=0,
        average_delivery_time=0.0,
        most_common_events=[]
    )

async def _trigger_webhook_event(db: Session, event_type: str, payload: Dict[str, Any]) -> List[int]:
    """Trigger webhook event"""
    # This would implement actual webhook triggering
    return []

async def _log_webhook_event(event_type: str, data: Dict[str, Any]):
    """Log webhook event"""
    logger.info(f"Webhook event: {event_type}, data: {data}")
