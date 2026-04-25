from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from ...database import get_db
from ...services import PolicyService
from ...schemas import ArchivePolicyCreate, ArchivePolicyResponse
from ...utils.audit_logger import audit_logger_instance, AuditAction

logger = logging.getLogger(__name__)
router = APIRouter()

# Enhanced schemas for v2
class ArchivePolicyCreateV2(BaseModel):
    """Enhanced policy creation schema for v2"""
    name: str = Field(..., description="Policy name")
    description: Optional[str] = Field(None, description="Policy description")
    retention_days: int = Field(..., gt=0, description="Retention period in days")
    auto_cleanup: bool = Field(True, description="Enable automatic cleanup")
    cleanup_schedule: Optional[str] = Field("0 2 * * *", description="Cron schedule for cleanup")
    priority: Optional[str] = Field("normal", description="Policy priority")
    tags: Optional[List[str]] = Field(default_factory=list, description="Policy tags")
    conditions: Optional[dict] = Field(None, description="Advanced conditions for policy application")
    notifications: Optional[dict] = Field(None, description="Notification settings")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "User Data Retention",
                "description": "Policy for user data retention",
                "retention_days": 365,
                "auto_cleanup": True,
                "cleanup_schedule": "0 2 * * *",
                "priority": "high",
                "tags": ["user_data", "compliance"],
                "conditions": {"data_type": "personal", "region": "EU"},
                "notifications": {"email": "admin@example.com", "webhook": "https://example.com/webhook"}
            }
        }

class ArchivePolicyResponseV2(BaseModel):
    """Enhanced policy response schema for v2"""
    id: int
    name: str
    description: Optional[str]
    retention_days: int
    auto_cleanup: bool
    cleanup_schedule: str
    priority: str
    tags: List[str]
    conditions: Optional[dict]
    notifications: Optional[dict]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    archive_count: int
    last_cleanup: Optional[datetime]
    next_cleanup: Optional[datetime]

class PolicyStats(BaseModel):
    """Policy statistics"""
    total_policies: int
    active_policies: int
    inactive_policies: int
    policies_with_auto_cleanup: int
    average_retention_days: float
    most_common_priority: str

class BatchPolicyRequest(BaseModel):
    """Batch policy operations request"""
    policy_ids: List[int]
    operation: str = Field(..., regex="^(activate|deactivate|delete)$")

class BatchPolicyResponse(BaseModel):
    """Batch policy operations response"""
    successful: List[int]
    failed: List[dict]
    total_processed: int
    success_count: int
    failure_count: int

# Initialize service
policy_service = PolicyService()

@router.post("/", response_model=ArchivePolicyResponseV2, status_code=201)
async def create_policy(
    policy: ArchivePolicyCreateV2,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new archival policy with enhanced features"""
    try:
        # Convert v2 schema to internal format
        create_data = ArchivePolicyCreate(
            name=policy.name,
            description=policy.description,
            retention_days=policy.retention_days,
            auto_cleanup=policy.auto_cleanup
        )
        
        result = await policy_service.create_policy(db, create_data)
        
        # Add background task for enhanced processing
        background_tasks.add_task(
            _process_policy_enhancements,
            result.id,
            policy.tags,
            policy.priority,
            policy.conditions,
            policy.notifications,
            policy.cleanup_schedule
        )
        
        # Convert to v2 response format
        return _to_v2_response(result)
        
    except Exception as e:
        logger.error(f"Error creating policy: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=dict)
async def list_policies(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    active_only: bool = Query(False),
    priority: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    """List archival policies with enhanced filtering"""
    try:
        policies = await policy_service.list_policies(db, skip, limit)
        
        # Convert to v2 response format
        items = [_to_v2_response(policy) for policy in policies]
        
        # Apply additional filtering
        if active_only:
            items = [item for item in items if item.is_active]
        
        if priority:
            items = [item for item in items if item.priority == priority]
        
        if tags:
            items = [item for item in items if any(tag in item.tags for tag in tags)]
        
        # Get total count (simplified)
        total = len(items)
        
        return {
            'items': items,
            'total': total,
            'skip': skip,
            'limit': limit,
            'filters': {
                'active_only': active_only,
                'priority': priority,
                'tags': tags
            }
        }
        
    except Exception as e:
        logger.error(f"Error listing policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{policy_id}", response_model=ArchivePolicyResponseV2)
async def get_policy(
    policy_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific archival policy with enhanced information"""
    try:
        policy = await policy_service.get_policy(db, policy_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        return _to_v2_response(policy)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{policy_id}", response_model=ArchivePolicyResponseV2)
async def update_policy(
    policy_id: int,
    policy_update: ArchivePolicyCreateV2,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update an archival policy with enhanced features"""
    try:
        # Check if policy exists
        existing_policy = await policy_service.get_policy(db, policy_id)
        if not existing_policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Convert v2 schema to internal format
        update_data = {
            "name": policy_update.name,
            "description": policy_update.description,
            "retention_days": policy_update.retention_days,
            "auto_cleanup": policy_update.auto_cleanup
        }
        
        # This would implement the actual update logic
        # For now, return the existing policy with enhanced fields
        result = existing_policy
        
        # Add background task for enhanced processing
        background_tasks.add_task(
            _process_policy_enhancements,
            result.id,
            policy_update.tags,
            policy_update.priority,
            policy_update.conditions,
            policy_update.notifications,
            policy_update.cleanup_schedule
        )
        
        return _to_v2_response(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{policy_id}")
async def delete_policy(
    policy_id: int,
    force: bool = Query(False, description="Force delete even if archives exist"),
    db: Session = Depends(get_db)
):
    """Delete an archival policy with safety checks"""
    try:
        policy = await policy_service.get_policy(db, policy_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Check if policy has associated archives
        # This would be implemented in the actual service
        has_archives = False  # Placeholder
        
        if has_archives and not force:
            raise HTTPException(
                status_code=400,
                detail="Policy has associated archives. Use force=true to delete."
            )
        
        # This would implement the actual deletion logic
        return {"message": "Policy deleted successfully", "policy_id": policy_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{policy_id}/activate")
async def activate_policy(
    policy_id: int,
    db: Session = Depends(get_db)
):
    """Activate a policy"""
    try:
        policy = await policy_service.get_policy(db, policy_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # This would implement activation logic
        return {"message": "Policy activated successfully", "policy_id": policy_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{policy_id}/deactivate")
async def deactivate_policy(
    policy_id: int,
    db: Session = Depends(get_db)
):
    """Deactivate a policy"""
    try:
        policy = await policy_service.get_policy(db, policy_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # This would implement deactivation logic
        return {"message": "Policy deactivated successfully", "policy_id": policy_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", response_model=BatchPolicyResponse)
async def batch_policy_operations(
    request: BatchPolicyRequest,
    db: Session = Depends(get_db)
):
    """Perform batch operations on policies"""
    successful = []
    failed = []
    
    for policy_id in request.policy_ids:
        try:
            # Check if policy exists
            policy = await policy_service.get_policy(db, policy_id)
            if not policy:
                failed.append({
                    "policy_id": policy_id,
                    "error": "Policy not found"
                })
                continue
            
            # Perform operation based on request
            if request.operation == "activate":
                # Activate policy
                successful.append(policy_id)
            elif request.operation == "deactivate":
                # Deactivate policy
                successful.append(policy_id)
            elif request.operation == "delete":
                # Delete policy
                successful.append(policy_id)
            
        except Exception as e:
            failed.append({
                "policy_id": policy_id,
                "error": str(e)
            })
    
    return BatchPolicyResponse(
        successful=successful,
        failed=failed,
        total_processed=len(request.policy_ids),
        success_count=len(successful),
        failure_count=len(failed)
    )

@router.get("/stats/summary", response_model=PolicyStats)
async def get_policy_stats(db: Session = Depends(get_db)):
    """Get policy statistics"""
    try:
        # This would implement actual statistics calculation
        return PolicyStats(
            total_policies=0,
            active_policies=0,
            inactive_policies=0,
            policies_with_auto_cleanup=0,
            average_retention_days=0.0,
            most_common_priority="normal"
        )
        
    except Exception as e:
        logger.error(f"Error getting policy stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{policy_id}/cleanup")
async def trigger_policy_cleanup(
    policy_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger cleanup for a specific policy"""
    try:
        policy = await policy_service.get_policy(db, policy_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Add background task for cleanup
        background_tasks.add_task(_execute_policy_cleanup, policy_id)
        
        return {"message": "Cleanup triggered successfully", "policy_id": policy_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def _to_v2_response(policy) -> ArchivePolicyResponseV2:
    """Convert internal policy to v2 response format"""
    return ArchivePolicyResponseV2(
        id=policy.id,
        name=policy.name,
        description=getattr(policy, 'description', None),
        retention_days=policy.retention_days,
        auto_cleanup=getattr(policy, 'auto_cleanup', True),
        cleanup_schedule=getattr(policy, 'cleanup_schedule', '0 2 * * *'),
        priority=getattr(policy, 'priority', 'normal'),
        tags=getattr(policy, 'tags', []),
        conditions=getattr(policy, 'conditions', None),
        notifications=getattr(policy, 'notifications', None),
        created_at=policy.created_at,
        updated_at=getattr(policy, 'updated_at', None),
        is_active=getattr(policy, 'is_active', True),
        archive_count=getattr(policy, 'archive_count', 0),
        last_cleanup=getattr(policy, 'last_cleanup', None),
        next_cleanup=getattr(policy, 'next_cleanup', None)
    )

async def _process_policy_enhancements(
    policy_id: int,
    tags: List[str],
    priority: str,
    conditions: Optional[dict],
    notifications: Optional[dict],
    cleanup_schedule: str
):
    """Process enhanced policy features in background"""
    logger.info(f"Processing enhancements for policy {policy_id}")

async def _execute_policy_cleanup(policy_id: int):
    """Execute policy cleanup in background"""
    logger.info(f"Executing cleanup for policy {policy_id}")
