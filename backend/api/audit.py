from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from ..database import get_db
from ..models.audit_log import AuditAction, AuditSeverity
from ..services.audit_service import AuditService
from ..utils.audit_logger import audit_logger_instance, AuditEvent

# Create router
router = APIRouter(prefix="/api/v1/audit", tags=["audit"])

# Initialize service
audit_service = AuditService()

# Pydantic models for API
class AuditLogResponse(BaseModel):
    """Audit log response model"""
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
    
    class Config:
        from_attributes = True

class AuditLogListResponse(BaseModel):
    """Paginated audit log list response"""
    items: List[AuditLogResponse]
    total: int
    page: int
    size: int
    total_pages: int

class ComplianceReportRequest(BaseModel):
    """Compliance report request parameters"""
    compliance_category: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    format: str = Field("json", regex="^(json|csv)$")

class RetentionPolicyCreate(BaseModel):
    """Retention policy creation request"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    retention_days: int = Field(..., gt=0)
    action_types: Optional[List[str]] = None
    severity_levels: Optional[List[str]] = None
    compliance_categories: Optional[List[str]] = None
    auto_archive: bool = False
    archive_location: Optional[str] = None
    legal_hold_enabled: bool = False
    priority: int = 0

class RetentionPolicyResponse(BaseModel):
    """Retention policy response model"""
    id: int
    name: str
    description: Optional[str] = None
    retention_days: int
    action_types: Optional[str] = None
    severity_levels: Optional[str] = None
    compliance_categories: Optional[str] = None
    auto_archive: bool
    archive_location: Optional[str] = None
    legal_hold_enabled: bool
    is_active: bool
    priority: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AuditStatisticsResponse(BaseModel):
    """Audit statistics response model"""
    period_days: int
    total_logs: int
    successful_operations: int
    failed_operations: int
    success_rate: float
    top_actions: List[dict]
    top_users: List[dict]
    security_events: int

class LogIntegrityResponse(BaseModel):
    """Log integrity verification response"""
    log_id: int
    is_valid: bool
    stored_hash: str
    calculated_hash: str
    timestamp: str

# API Endpoints

@router.get("/logs", response_model=AuditLogListResponse)
async def get_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    success: Optional[bool] = Query(None, description="Filter by success status"),
    compliance_category: Optional[str] = Query(None, description="Filter by compliance category"),
    date_from: Optional[datetime] = Query(None, description="Filter by start date"),
    date_to: Optional[datetime] = Query(None, description="Filter by end date"),
    ip_address: Optional[str] = Query(None, description="Filter by IP address"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    search: Optional[str] = Query(None, description="Search in description, resource name, or details"),
    sort_field: str = Query("timestamp", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db)
):
    """
    Get audit logs with advanced filtering and pagination
    """
    try:
        # Convert string enums to enum objects if provided
        action_enum = None
        if action:
            try:
                action_enum = AuditAction(action)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid action: {action}")
        
        severity_enum = None
        if severity:
            try:
                severity_enum = AuditSeverity(severity)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
        
        skip = (page - 1) * size
        
        logs, total = await audit_service.get_audit_logs(
            db=db,
            skip=skip,
            limit=size,
            action=action_enum,
            severity=severity_enum,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            success=success,
            compliance_category=compliance_category,
            date_from=date_from,
            date_to=date_to,
            ip_address=ip_address,
            session_id=session_id,
            search=search,
            sort_field=sort_field,
            sort_order=sort_order
        )
        
        total_pages = (total + size - 1) // size
        
        return AuditLogListResponse(
            items=[AuditLogResponse(**log.to_dict()) for log in logs],
            total=total,
            page=page,
            size=size,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific audit log by ID"""
    log = await audit_service.get_audit_log_by_id(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    
    return AuditLogResponse(**log.to_dict())

@router.get("/users/{user_id}/activity")
async def get_user_activity(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records"),
    db: Session = Depends(get_db)
):
    """Get recent activity for a specific user"""
    logs = await audit_service.get_user_activity(db, user_id, days, limit)
    return [AuditLogResponse(**log.to_dict()) for log in logs]

@router.get("/resources/{resource_type}/{resource_id}/history")
async def get_resource_history(
    resource_type: str,
    resource_id: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records"),
    db: Session = Depends(get_db)
):
    """Get audit history for a specific resource"""
    logs = await audit_service.get_resource_history(db, resource_type, resource_id, limit)
    return [AuditLogResponse(**log.to_dict()) for log in logs]

@router.post("/reports/compliance")
async def generate_compliance_report(
    request: ComplianceReportRequest,
    db: Session = Depends(get_db)
):
    """Generate compliance report for audit logs"""
    try:
        report = await audit_service.get_compliance_report(
            db=db,
            compliance_category=request.compliance_category,
            date_from=request.date_from,
            date_to=request.date_to,
            format=request.format
        )
        
        if request.format == "csv":
            return PlainTextResponse(
                content=report,
                headers={"Content-Disposition": "attachment; filename=compliance_report.csv"}
            )
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics", response_model=AuditStatisticsResponse)
async def get_audit_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    db: Session = Depends(get_db)
):
    """Get audit log statistics"""
    try:
        stats = await audit_service.get_audit_statistics(db, days)
        return AuditStatisticsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/retention-policies", response_model=RetentionPolicyResponse)
async def create_retention_policy(
    policy: RetentionPolicyCreate,
    db: Session = Depends(get_db)
):
    """Create a new audit retention policy"""
    try:
        new_policy = await audit_service.create_retention_policy(
            db=db,
            name=policy.name,
            description=policy.description,
            retention_days=policy.retention_days,
            action_types=policy.action_types,
            severity_levels=policy.severity_levels,
            compliance_categories=policy.compliance_categories,
            auto_archive=policy.auto_archive,
            archive_location=policy.archive_location,
            legal_hold_enabled=policy.legal_hold_enabled,
            priority=policy.priority
        )
        
        return RetentionPolicyResponse.from_orm(new_policy)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/retention-policies", response_model=List[RetentionPolicyResponse])
async def get_retention_policies(db: Session = Depends(get_db)):
    """Get all retention policies"""
    try:
        policies = await audit_service.get_retention_policies(db)
        return [RetentionPolicyResponse.from_orm(policy) for policy in policies]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/retention/apply")
async def apply_retention_policies(db: Session = Depends(get_db)):
    """Apply retention policies to clean up old audit logs"""
    try:
        result = await audit_service.apply_retention_policies(db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/{log_id}/integrity", response_model=LogIntegrityResponse)
async def verify_log_integrity(
    log_id: int,
    db: Session = Depends(get_db)
):
    """Verify the integrity of an audit log using its hash"""
    try:
        result = await audit_service.verify_log_integrity(db, log_id)
        return LogIntegrityResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/log")
async def create_manual_audit_log(
    action: str,
    description: str,
    user_id: Optional[str] = None,
    severity: str = "medium",
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    resource_name: Optional[str] = None,
    details: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """
    Create a manual audit log entry (for testing or manual logging)
    """
    try:
        # Convert string to enum
        action_enum = AuditAction(action)
        severity_enum = AuditSeverity(severity)
        
        event = AuditEvent(
            action=action_enum,
            description=description,
            user_id=user_id,
            severity=severity_enum,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details=details,
            compliance_category="MANUAL"
        )
        
        log = await audit_service.create_audit_log(db, event)
        if not log:
            raise HTTPException(status_code=500, detail="Failed to create audit log")
        
        return AuditLogResponse(**log.to_dict())
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
