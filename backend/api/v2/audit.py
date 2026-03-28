from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from ...database import get_db
from ...models.audit_log import AuditAction, AuditSeverity
from ...services.audit_service import AuditService
from ...utils.audit_logger import audit_logger_instance, AuditEvent

logger = logging.getLogger(__name__)
router = APIRouter()

# Enhanced schemas for v2
class AuditLogResponseV2(BaseModel):
    """Enhanced audit log response model for v2"""
    id: int
    action: str
    severity: str
    user_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    session_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    description: str
    details: Optional[str] = None
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    service_name: str
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    success: bool
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    compliance_category: Optional[str] = None
    retention_days: int
    legal_hold: bool
    timestamp: datetime
    created_at: datetime
    event_hash: str
    is_expired: bool
    days_until_expiry: int
    # Enhanced v2 fields
    geo_location: Optional[str] = None
    device_fingerprint: Optional[str] = None
    risk_score: Optional[float] = None
    correlation_id: Optional[str] = None
    parent_event_id: Optional[int] = None
    child_events: List[int] = []
    tags: List[str] = []

class AuditSearchParams(BaseModel):
    """Enhanced audit search parameters for v2"""
    action: Optional[str] = None
    severity: Optional[str] = None
    user_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    compliance_category: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    success: Optional[bool] = None
    legal_hold: Optional[bool] = None
    geo_location: Optional[str] = None
    risk_score_min: Optional[float] = None
    risk_score_max: Optional[float] = None
    tags: Optional[List[str]] = None
    correlation_id: Optional[str] = None
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    sort_by: str = Field("timestamp", description="Field to sort by")
    sort_order: str = Field("desc", regex="^(asc|desc)$")

class AuditStats(BaseModel):
    """Audit statistics"""
    total_events: int
    events_by_action: dict
    events_by_severity: dict
    events_by_user: dict
    success_rate: float
    average_duration_ms: float
    compliance_breakdown: dict
    risk_score_distribution: dict
    geo_location_distribution: dict

class AuditExportRequest(BaseModel):
    """Audit export request"""
    format: str = Field("csv", regex="^(csv|json|xlsx)$")
    filters: Optional[AuditSearchParams] = None
    include_sensitive: bool = Field(False, description="Include sensitive data")
    compress: bool = Field(True, description="Compress the export")

class ComplianceReport(BaseModel):
    """Compliance report"""
    report_id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    total_events: int
    compliance_score: float
    violations: List[dict]
    recommendations: List[str]
    summary: dict

# Initialize service
audit_service = AuditService()

@router.get("/", response_model=dict)
async def list_audit_logs(
    params: AuditSearchParams = Depends(),
    db: Session = Depends(get_db)
):
    """List audit logs with enhanced filtering and search"""
    try:
        # Convert search parameters to service format
        search_params = {
            "action": params.action,
            "severity": params.severity,
            "user_id": params.user_id,
            "resource_type": params.resource_type,
            "resource_id": params.resource_id,
            "compliance_category": params.compliance_category,
            "date_from": params.date_from,
            "date_to": params.date_to,
            "success": params.success,
            "legal_hold": params.legal_hold,
            "skip": (params.page - 1) * params.limit,
            "limit": params.limit,
            "sort_by": params.sort_by,
            "sort_order": params.sort_order
        }
        
        # Get audit logs
        logs, total = await audit_service.get_audit_logs(db, **search_params)
        
        # Convert to v2 response format
        items = [_to_v2_response(log) for log in logs]
        
        # Apply additional filtering for v2 specific fields
        if params.geo_location:
            items = [item for item in items if item.geo_location == params.geo_location]
        
        if params.risk_score_min is not None:
            items = [item for item in items if item.risk_score and item.risk_score >= params.risk_score_min]
        
        if params.risk_score_max is not None:
            items = [item for item in items if item.risk_score and item.risk_score <= params.risk_score_max]
        
        if params.tags:
            items = [item for item in items if any(tag in item.tags for tag in params.tags)]
        
        if params.correlation_id:
            items = [item for item in items if item.correlation_id == params.correlation_id]
        
        return {
            'items': items,
            'total': total,
            'page': params.page,
            'limit': params.limit,
            'total_pages': (total + params.limit - 1) // params.limit,
            'filters': {
                'action': params.action,
                'severity': params.severity,
                'user_id': params.user_id,
                'resource_type': params.resource_type,
                'compliance_category': params.compliance_category,
                'date_from': params.date_from,
                'date_to': params.date_to,
                'success': params.success,
                'legal_hold': params.legal_hold,
                'geo_location': params.geo_location,
                'risk_score_min': params.risk_score_min,
                'risk_score_max': params.risk_score_max,
                'tags': params.tags,
                'correlation_id': params.correlation_id
            }
        }
        
    except Exception as e:
        logger.error(f"Error listing audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{log_id}", response_model=AuditLogResponseV2)
async def get_audit_log(
    log_id: int,
    include_related: bool = Query(False, description="Include related events"),
    db: Session = Depends(get_db)
):
    """Get a specific audit log with enhanced information"""
    try:
        log = await audit_service.get_audit_log(db, log_id)
        if not log:
            raise HTTPException(status_code=404, detail="Audit log not found")
        
        response = _to_v2_response(log)
        
        # Include related events if requested
        if include_related:
            response.child_events = await _get_related_events(db, log_id)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit log: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary", response_model=AuditStats)
async def get_audit_stats(
    period_days: int = Query(30, description="Period in days for statistics"),
    db: Session = Depends(get_db)
):
    """Get audit statistics and analytics"""
    try:
        # This would implement actual statistics calculation
        return AuditStats(
            total_events=0,
            events_by_action={},
            events_by_severity={},
            events_by_user={},
            success_rate=0.0,
            average_duration_ms=0.0,
            compliance_breakdown={},
            risk_score_distribution={},
            geo_location_distribution={}
        )
        
    except Exception as e:
        logger.error(f"Error getting audit stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export")
async def export_audit_logs(
    request: AuditExportRequest,
    db: Session = Depends(get_db)
):
    """Export audit logs in various formats"""
    try:
        # This would implement export functionality
        export_id = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "export_id": export_id,
            "status": "processing",
            "format": request.format,
            "estimated_completion": datetime.now(),
            "download_url": f"/api/v2/audit/exports/{export_id}/download"
        }
        
    except Exception as e:
        logger.error(f"Error exporting audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/exports/{export_id}/download")
async def download_export(
    export_id: str,
    db: Session = Depends(get_db)
):
    """Download exported audit logs"""
    try:
        # This would implement file download
        raise HTTPException(status_code=404, detail="Export not found or expired")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading export: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compliance/report")
async def generate_compliance_report(
    period_start: datetime,
    period_end: datetime,
    categories: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """Generate compliance report"""
    try:
        report_id = f"compliance_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # This would implement compliance report generation
        return ComplianceReport(
            report_id=report_id,
            generated_at=datetime.now(),
            period_start=period_start,
            period_end=period_end,
            total_events=0,
            compliance_score=0.0,
            violations=[],
            recommendations=[],
            summary={}
        )
        
    except Exception as e:
        logger.error(f"Error generating compliance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{log_id}/legal-hold")
async def set_legal_hold(
    log_id: int,
    hold_reason: str = Field(..., description="Reason for legal hold"),
    db: Session = Depends(get_db)
):
    """Place legal hold on audit log"""
    try:
        log = await audit_service.get_audit_log(db, log_id)
        if not log:
            raise HTTPException(status_code=404, detail="Audit log not found")
        
        # This would implement legal hold logic
        return {
            "message": "Legal hold placed successfully",
            "log_id": log_id,
            "hold_reason": hold_reason,
            "placed_at": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting legal hold: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{log_id}/legal-hold")
async def remove_legal_hold(
    log_id: int,
    db: Session = Depends(get_db)
):
    """Remove legal hold from audit log"""
    try:
        log = await audit_service.get_audit_log(db, log_id)
        if not log:
            raise HTTPException(status_code=404, detail="Audit log not found")
        
        # This would implement legal hold removal
        return {
            "message": "Legal hold removed successfully",
            "log_id": log_id,
            "removed_at": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing legal hold: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/advanced")
async def advanced_search(
    query: str = Field(..., description="Search query"),
    search_type: str = Field("fulltext", regex="^(fulltext|fuzzy|regex)$"),
    highlight: bool = Field(True, description="Highlight matches"),
    db: Session = Depends(get_db)
):
    """Advanced audit log search"""
    try:
        # This would implement advanced search
        return {
            "query": query,
            "search_type": search_type,
            "results": [],
            "total": 0,
            "search_time": 0.0
        }
        
    except Exception as e:
        logger.error(f"Error in advanced search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def _to_v2_response(log) -> AuditLogResponseV2:
    """Convert internal audit log to v2 response format"""
    return AuditLogResponseV2(
        id=log.id,
        action=log.action.value if hasattr(log.action, 'value') else str(log.action),
        severity=log.severity.value if hasattr(log.severity, 'value') else str(log.severity),
        user_id=log.user_id,
        user_agent=log.user_agent,
        ip_address=log.ip_address,
        session_id=log.session_id,
        resource_type=log.resource_type,
        resource_id=log.resource_id,
        resource_name=log.resource_name,
        description=log.description,
        details=log.details,
        old_values=log.old_values,
        new_values=log.new_values,
        service_name=log.service_name,
        endpoint=log.endpoint,
        method=log.method,
        status_code=log.status_code,
        success=log.success,
        error_message=log.error_message,
        duration_ms=log.duration_ms,
        compliance_category=log.compliance_category,
        retention_days=log.retention_days,
        legal_hold=log.legal_hold,
        timestamp=log.timestamp,
        created_at=log.created_at,
        event_hash=log.event_hash,
        is_expired=log.is_expired,
        days_until_expiry=log.days_until_expiry,
        # Enhanced v2 fields
        geo_location=getattr(log, 'geo_location', None),
        device_fingerprint=getattr(log, 'device_fingerprint', None),
        risk_score=getattr(log, 'risk_score', None),
        correlation_id=getattr(log, 'correlation_id', None),
        parent_event_id=getattr(log, 'parent_event_id', None),
        child_events=getattr(log, 'child_events', []),
        tags=getattr(log, 'tags', [])
    )

async def _get_related_events(db: Session, log_id: int) -> List[int]:
    """Get related events for a log entry"""
    # This would implement related events lookup
    return []
