from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import logging
import time

from .database import get_db, engine
from .models import Base, UserSettings
from .models.audit_log import AuditLog, AuditRetentionPolicy
from .schemas import (
    ArchiveRecordCreate, ArchiveRecordResponse, 
    ArchivePolicyCreate, ArchivePolicyResponse,
    UserSettingsUpdate, UserSettingsResponse,
    ArchiveListParams, ArchiveListResponse
)
from .services import ArchiveService, PolicyService, SettingsService
from .services.audit_service import AuditService
from .services.search_service import search_service
from .scheduler import ArchiveScheduler
from .utils.audit_logger import (
    log_user_login, log_user_logout, log_policy_change, 
    log_archive_operation, audit_logger_instance, AuditEvent,
    AuditAction, AuditSeverity
)
from .config.settings import get_settings
from .services.config_service import config_service
from .middleware.profiling_middleware import ProfilingMiddleware
from .services.monitoring_service import monitoring_service
from .utils.metrics_collector import metrics_collector
from .middleware.version_middleware import VersioningMiddleware, VersionNegotiationMiddleware
from .utils.version_manager import version_manager

# Configure logging
settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.logging.level.value))
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TTL-Aware Automated Archival Service",
    description="A service for automated data archival with TTL-based cleanup with API versioning support",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add versioning middleware
app.add_middleware(VersioningMiddleware, version_manager=version_manager)
app.add_middleware(VersionNegotiationMiddleware, version_manager=version_manager)

# Add profiling middleware
app.add_middleware(ProfilingMiddleware)

# Initialize services
archive_service = ArchiveService()
policy_service = PolicyService()
settings_service = SettingsService()
audit_service = AuditService()
scheduler = ArchiveScheduler()

# Include v1 routers (legacy)
from .api.v1.audit import audit_router as v1_audit_router
from .api.v1.search import router as v1_search_router
from .api.v1.config import router as v1_config_router
from .api.v1.data import router as v1_data_router

# Include v2 routers (current)
from .api.v2 import v2_router

app.include_router(v1_audit_router)
app.include_router(v1_search_router)
app.include_router(v1_config_router)
app.include_router(v1_data_router)
app.include_router(v2_router)

# Audit middleware for logging all API requests
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Get request information
    method = request.method
    url = str(request.url)
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    session_id = request.headers.get("x-session-id")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Get user ID from headers if available
    user_id = request.headers.get("x-user-id")
    
    # Skip audit logging for health check and audit endpoints to avoid infinite loops
    if not (url.endswith("/health") or url.startswith("/api/v1/audit")):
        try:
            # Create audit event for API access
            event = AuditEvent(
                action=AuditAction.API_ACCESS,
                description=f"{method} {url}",
                user_id=user_id,
                ip_address=client_ip,
                user_agent=user_agent,
                session_id=session_id,
                endpoint=url,
                method=method,
                status_code=response.status_code,
                success=response.status_code < 400,
                duration_ms=duration_ms,
                severity=AuditSeverity.LOW
            )
            
            # Log asynchronously (don't wait for it)
            db = next(get_db())
            try:
                audit_logger_instance.log_event(db, event)
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to log audit middleware: {e}")
    
    return response

@app.on_event("startup")
async def startup_event():
    """Initialize the archive scheduler and search service on startup"""
    await scheduler.start()
    logger.info("Archive scheduler started")
    
    # Initialize search service
    db = next(get_db())
    try:
        search_initialized = await search_service.initialize_search(db)
        if search_initialized:
            logger.info("Search service initialized successfully")
        else:
            logger.error("Failed to initialize search service")
    finally:
        db.close()
    
    # Start monitoring services
    metrics_collector.start_collection()
    monitoring_service.enable_monitoring()
    logger.info("Performance monitoring started")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    await scheduler.stop()
    logger.info("Archive scheduler stopped")
    
    # Stop monitoring services
    metrics_collector.stop_collection()
    monitoring_service.disable_monitoring()
    logger.info("Performance monitoring stopped")

@app.post("/api/v1/policies", response_model=ArchivePolicyResponse)
async def create_policy(
    policy: ArchivePolicyCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new archival policy"""
    start_time = time.time()
    user_id = request.headers.get("x-user-id")
    
    try:
        result = await policy_service.create_policy(db, policy)
        
        # Log policy creation
        await log_policy_change(
            db=db,
            user_id=user_id or "anonymous",
            policy_id=str(result.id),
            policy_name=policy.name,
            new_values=policy.dict()
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating policy: {e}")
        
        # Log failed policy creation
        await audit_logger_instance.log_user_action(
            db=db,
            user_id=user_id or "anonymous",
            action=AuditAction.POLICY_CREATE,
            description=f"Failed to create policy: {policy.name}",
            resource_type="policy",
            resource_name=policy.name,
            success=False,
            error_message=str(e),
            ip_address=request.client.host if request.client else "unknown"
        )
        
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/policies", response_model=List[ArchivePolicyResponse])
async def list_policies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all archival policies"""
    return await policy_service.list_policies(db, skip, limit)

@app.get("/api/v1/policies/{policy_id}", response_model=ArchivePolicyResponse)
async def get_policy(
    policy_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific archival policy"""
    policy = await policy_service.get_policy(db, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@app.post("/api/v1/archives", response_model=ArchiveRecordResponse)
async def create_archive_record(
    record: ArchiveRecordCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new archive record"""
    user_id = request.headers.get("x-user-id")
    
    try:
        result = await archive_service.create_record(db, record)
        
        # Log archive creation
        await log_archive_operation(
            db=db,
            user_id=user_id or "anonymous",
            action=AuditAction.ARCHIVE_CREATE,
            archive_id=str(result.id),
            archive_name=record.original_data_id,
            resource_type="archive",
            resource_id=str(result.id),
            resource_name=record.original_data_id,
            new_values=record.dict()
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating archive record: {e}")
        
        # Log failed archive creation
        await audit_logger_instance.log_user_action(
            db=db,
            user_id=user_id or "anonymous",
            action=AuditAction.ARCHIVE_CREATE,
            description=f"Failed to create archive record: {record.original_data_id}",
            resource_type="archive",
            resource_name=record.original_data_id,
            success=False,
            error_message=str(e),
            ip_address=request.client.host if request.client else "unknown"
        )
        
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/archives", response_model=ArchiveListResponse)
async def list_archives(
    params: ArchiveListParams = None,
    db: Session = Depends(get_db)
):
    """List archive records with advanced filtering, sorting, and pagination"""
    # Handle query params manually if not using Pydantic params
    page = int(params.page) if params and hasattr(params, 'page') else 1
    limit = int(params.limit) if params and hasattr(params, 'limit') else 10
    policy_id = int(params.policy_id) if params and hasattr(params, 'policy_id') and params.policy_id else None
    status = params.status if params and hasattr(params, 'status') else None
    date_from = params.date_from if params and hasattr(params, 'date_from') else None
    date_to = params.date_to if params and hasattr(params, 'date_to') else None
    search = params.search if params and hasattr(params, 'search') else None
    min_size = int(params.min_size) if params and hasattr(params, 'min_size') and params.min_size else None
    max_size = int(params.max_size) if params and hasattr(params, 'max_size') and params.max_size else None
    sort_field = params.sort_field if params and hasattr(params, 'sort_field') else 'created_at'
    sort_order = params.sort_order if params and hasattr(params, 'sort_order') else 'desc'
    
    records, total = await archive_service.list_records_advanced(
        db=db,
        page=page,
        limit=limit,
        policy_id=policy_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        search=search,
        min_size=min_size,
        max_size=max_size,
        sort_field=sort_field,
        sort_order=sort_order
    )
    
    # Convert to detailed format
    items = [archive_service._to_detailed_record(record) for record in records]
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'size': limit,
        'total_pages': (total + limit - 1) // limit
    }

@app.get("/api/v1/archives/{record_id}", response_model=ArchiveRecordResponse)
async def get_archive_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific archive record"""
    record = await archive_service.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Archive record not found")
    return record

@app.delete("/api/v1/archives/{record_id}")
async def delete_archive_record(
    record_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Manually delete an archive record"""
    user_id = request.headers.get("x-user-id")
    
    # Get the record before deletion for audit logging
    record = await archive_service.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Archive record not found")
    
    try:
        success = await archive_service.delete_record(db, record_id)
        
        if success:
            # Log successful archive deletion
            await log_archive_operation(
                db=db,
                user_id=user_id or "anonymous",
                action=AuditAction.ARCHIVE_DELETE,
                archive_id=str(record_id),
                archive_name=record.original_data_id,
                resource_type="archive",
                resource_id=str(record_id),
                resource_name=record.original_data_id,
                old_values={"original_data_id": record.original_data_id, "status": record.status}
            )
        
        return {"message": "Archive record deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting archive record: {e}")
        
        # Log failed archive deletion
        await audit_logger_instance.log_user_action(
            db=db,
            user_id=user_id or "anonymous",
            action=AuditAction.ARCHIVE_DELETE,
            description=f"Failed to delete archive record: {record_id}",
            resource_type="archive",
            resource_id=str(record_id),
            resource_name=record.original_data_id,
            success=False,
            error_message=str(e),
            ip_address=request.client.host if request.client else "unknown"
        )
        
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/archives/cleanup")
async def trigger_cleanup(
    policy_id: Optional[int] = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Manually trigger cleanup for expired records"""
    user_id = request.headers.get("x-user-id") if request else "system"
    
    try:
        deleted_count = await archive_service.cleanup_expired_records(db, policy_id)
        
        # Log cleanup operation
        await audit_logger_instance.log_user_action(
            db=db,
            user_id=user_id,
            action=AuditAction.CLEANUP_TRIGGER,
            description=f"Manual cleanup triggered - deleted {deleted_count} expired records",
            resource_type="system",
            resource_id=str(policy_id) if policy_id else "all",
            new_values={"deleted_count": deleted_count, "policy_id": policy_id},
            compliance_category="SYSTEM"
        )
        
        return {"message": f"Cleaned up {deleted_count} expired records"}
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        
        # Log failed cleanup
        await audit_logger_instance.log_user_action(
            db=db,
            user_id=user_id,
            action=AuditAction.CLEANUP_TRIGGER,
            description=f"Failed manual cleanup",
            resource_type="system",
            success=False,
            error_message=str(e),
            compliance_category="SYSTEM"
        )
        
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/api/v1/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get archival service statistics"""
    return await archive_service.get_stats(db)

@app.get("/api/v1/settings", response_model=UserSettingsResponse)
async def get_settings(db: Session = Depends(get_db)):
    """Get archival service settings"""
    return await settings_service.get_settings(db)

@app.patch("/api/v1/settings", response_model=UserSettingsResponse)
async def update_settings(
    settings_update: UserSettingsUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update archival service settings"""
    user_id = request.headers.get("x-user-id")
    
    try:
        result = await settings_service.update_settings(db, settings_update.dict(exclude_unset=True))
        
        # Log settings update
        await audit_logger_instance.log_user_action(
            db=db,
            user_id=user_id or "anonymous",
            action=AuditAction.SETTINGS_UPDATE,
            description="Application settings updated",
            resource_type="settings",
            resource_id="app_settings",
            new_values=settings_update.dict(exclude_unset=True),
            compliance_category="ADMINISTRATION"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        
        # Log failed settings update
        await audit_logger_instance.log_user_action(
            db=db,
            user_id=user_id or "anonymous",
            action=AuditAction.SETTINGS_UPDATE,
            description="Failed to update application settings",
            resource_type="settings",
            resource_id="app_settings",
            success=False,
            error_message=str(e),
            compliance_category="ADMINISTRATION"
        )
        
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/monitoring/metrics")
async def get_performance_metrics():
    """Get current performance metrics"""
    return await monitoring_service.collect_metrics()

@app.get("/api/v1/monitoring/summary")
async def get_performance_summary():
    """Get performance summary"""
    return monitoring_service.get_performance_summary()

@app.get("/api/v1/monitoring/alerts")
async def get_alerts(active_only: bool = True):
    """Get performance alerts"""
    if active_only:
        return monitoring_service.get_active_alerts()
    return monitoring_service.get_all_alerts()

@app.get("/api/v1/monitoring/slow-operations")
async def get_slow_operations(limit: int = 10):
    """Get slow operations report"""
    return monitoring_service.get_slow_operations_report(limit)

@app.get("/api/v1/monitoring/database-performance")
async def get_database_performance():
    """Get database performance report"""
    return monitoring_service.get_database_performance_report()

@app.get("/api/v1/monitoring/system-usage")
async def get_system_usage():
    """Get system resource usage"""
    return metrics_collector.get_resource_usage_summary()

@app.delete("/api/v1/monitoring/alerts")
async def clear_alerts():
    """Clear all alerts"""
    monitoring_service.clear_alerts()
    return {"message": "Alerts cleared successfully"}

@app.post("/api/v1/monitoring/toggle")
async def toggle_monitoring(enabled: bool):
    """Toggle monitoring on/off"""
    if enabled:
        monitoring_service.enable_monitoring()
        metrics_collector.start_collection()
    else:
        monitoring_service.disable_monitoring()
        metrics_collector.stop_collection()
    
    return {"monitoring_enabled": enabled}

# Version information endpoints
@app.get("/version")
async def get_version_info():
    """Get API version information"""
    return {
        "current_version": version_manager.get_latest_version(),
        "supported_versions": list(version_manager.get_supported_versions().keys()),
        "deprecated_versions": list(version_manager.get_deprecated_versions().keys()),
        "recommended_version": version_manager.get_recommended_version(),
        "version_info": {
            version: {
                "status": info.status.value,
                "release_date": info.release_date.isoformat(),
                "deprecation_date": info.deprecation_date.isoformat() if info.deprecation_date else None,
                "backward_compatible": info.backward_compatible,
                "features": info.features,
                "breaking_changes": info.breaking_changes
            }
            for version, info in version_manager.versions.items()
        }
    }

@app.get("/api/version")
async def get_api_version():
    """Get API version for current request"""
    return {
        "version": version_manager.get_latest_version(),
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with version info"""
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow(),
        "version": version_manager.get_latest_version(),
        "supported_versions": list(version_manager.get_supported_versions().keys())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
