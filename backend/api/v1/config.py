"""
Configuration API endpoints for TTL archival service.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging

from ..database import get_db
from ..services.config_service import config_service
from ..config.validators import validate_config_update
from ..utils.secret_manager import secret_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/config", tags=["configuration"])


class ConfigUpdateRequest(BaseModel):
    """Request model for configuration updates."""
    updates: Dict[str, Any] = Field(..., description="Configuration updates to apply")
    validate_first: bool = Field(True, description="Whether to validate before applying")


class ConfigResponse(BaseModel):
    """Response model for configuration data."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None


class SecretRequest(BaseModel):
    """Request model for secret operations."""
    key: str = Field(..., description="Secret key")
    value: str = Field(..., description="Secret value")
    description: Optional[str] = Field(None, description="Secret description")


class SecretResponse(BaseModel):
    """Response model for secret operations."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


@router.get("/current", response_model=Dict[str, Any])
async def get_current_config(
    include_secrets: bool = False,
    request: Request = None
):
    """Get current configuration."""
    user_id = request.headers.get("x-user-id") if request else "anonymous"
    
    try:
        config = config_service.get_current_config(include_secrets=include_secrets)
        
        logger.info(f"Configuration retrieved by user: {user_id}")
        
        return {
            "success": True,
            "config": config,
            "timestamp": config_service.settings.last_updated.isoformat() if config_service.settings.last_updated else None,
            "version": config_service.settings.config_version
        }
        
    except Exception as e:
        logger.error(f"Failed to get configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/section/{section_name}", response_model=Dict[str, Any])
async def get_config_section(
    section_name: str,
    include_secrets: bool = False,
    request: Request = None
):
    """Get a specific configuration section."""
    user_id = request.headers.get("x-user-id") if request else "anonymous"
    
    try:
        section = config_service.get_config_section(section_name, include_secrets=include_secrets)
        
        if section is None:
            raise HTTPException(status_code=404, detail=f"Configuration section '{section_name}' not found")
        
        logger.info(f"Configuration section '{section_name}' retrieved by user: {user_id}")
        
        return {
            "success": True,
            "section": section_name,
            "data": section
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get configuration section '{section_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update", response_model=Dict[str, Any])
async def update_configuration(
    request: ConfigUpdateRequest,
    http_request: Request = None,
    db: Session = Depends(get_db)
):
    """Update configuration dynamically."""
    user_id = http_request.headers.get("x-user-id") if http_request else "anonymous"
    
    try:
        result = config_service.update_config(
            updates=request.updates,
            source="api",
            user_id=user_id,
            validate_first=request.validate_first
        )
        
        if result["success"]:
            logger.info(f"Configuration updated by user: {user_id}")
            return {
                "success": True,
                "message": "Configuration updated successfully",
                "previous_config": result.get("previous_config"),
                "current_config": result.get("current_config"),
                "validation": result.get("validation"),
                "warnings": result.get("warnings", [])
            }
        else:
            logger.warning(f"Configuration update failed for user {user_id}: {result.get('error')}")
            raise HTTPException(
                status_code=400, 
                detail={
                    "error": result.get("error"),
                    "errors": result.get("errors"),
                    "warnings": result.get("warnings", [])
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset/{section_name}", response_model=Dict[str, Any])
async def reset_config_section(
    section_name: str,
    http_request: Request = None,
    db: Session = Depends(get_db)
):
    """Reset a configuration section to defaults."""
    user_id = http_request.headers.get("x-user-id") if http_request else "anonymous"
    
    try:
        result = config_service.reset_config_section(section_name, source="api", user_id=user_id)
        
        if result["success"]:
            logger.info(f"Configuration section '{section_name}' reset by user: {user_id}")
            return {
                "success": True,
                "message": f"Configuration section '{section_name}' reset to defaults",
                "current_config": result.get("current_config")
            }
        else:
            logger.warning(f"Configuration reset failed for user {user_id}: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset configuration section '{section_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rollback", response_model=Dict[str, Any])
async def rollback_configuration(
    version: Optional[str] = None,
    steps_back: int = 1,
    http_request: Request = None,
    db: Session = Depends(get_db)
):
    """Rollback configuration to a previous version."""
    user_id = http_request.headers.get("x-user-id") if http_request else "anonymous"
    
    try:
        result = config_service.rollback_config(
            version=version,
            steps_back=steps_back,
            source="api",
            user_id=user_id
        )
        
        if result["success"]:
            logger.info(f"Configuration rollback performed by user: {user_id}")
            return {
                "success": True,
                "message": "Configuration rolled back successfully",
                "rollback_version": result.get("rollback_version"),
                "rollback_timestamp": result.get("rollback_timestamp"),
                "current_config": result.get("current_config")
            }
        else:
            logger.warning(f"Configuration rollback failed for user {user_id}: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to rollback configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=Dict[str, Any])
async def get_config_history(
    limit: int = 50,
    include_details: bool = False,
    request: Request = None
):
    """Get configuration change history."""
    user_id = request.headers.get("x-user-id") if request else "anonymous"
    
    try:
        history = config_service.get_config_history(limit=limit, include_details=include_details)
        
        logger.info(f"Configuration history retrieved by user: {user_id}")
        
        return {
            "success": True,
            "history": history,
            "count": len(history)
        }
        
    except Exception as e:
        logger.error(f"Failed to get configuration history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate", response_model=Dict[str, Any])
async def validate_configuration_updates(
    updates: Dict[str, Any],
    request: Request = None
):
    """Validate configuration updates without applying them."""
    user_id = request.headers.get("x-user-id") if request else "anonymous"
    
    try:
        validation_result = validate_config_update(updates)
        
        logger.info(f"Configuration validation performed by user: {user_id}")
        
        return {
            "success": True,
            "validation": validation_result.get_summary()
        }
        
    except Exception as e:
        logger.error(f"Failed to validate configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/features", response_model=Dict[str, Any])
async def get_feature_flags(request: Request = None):
    """Get current feature flags."""
    user_id = request.headers.get("x-user-id") if request else "anonymous"
    
    try:
        flags = config_service.get_feature_flags()
        
        logger.info(f"Feature flags retrieved by user: {user_id}")
        
        return {
            "success": True,
            "flags": flags
        }
        
    except Exception as e:
        logger.error(f"Failed to get feature flags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/features", response_model=Dict[str, Any])
async def update_feature_flags(
    flags: Dict[str, bool],
    http_request: Request = None,
    db: Session = Depends(get_db)
):
    """Update feature flags."""
    user_id = http_request.headers.get("x-user-id") if http_request else "anonymous"
    
    try:
        result = config_service.update_feature_flags(flags, source="api", user_id=user_id)
        
        if result["success"]:
            logger.info(f"Feature flags updated by user: {user_id}")
            return {
                "success": True,
                "message": "Feature flags updated successfully",
                "flags": config_service.get_feature_flags(),
                "warnings": result.get("warnings", [])
            }
        else:
            logger.warning(f"Feature flags update failed for user {user_id}: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update feature flags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export", response_model=Dict[str, Any])
async def export_configuration(
    include_secrets: bool = False,
    request: Request = None
):
    """Export configuration."""
    user_id = request.headers.get("x-user-id") if request else "anonymous"
    
    try:
        config = config_service.export_config(include_secrets=include_secrets)
        
        logger.info(f"Configuration exported by user: {user_id}")
        
        return {
            "success": True,
            "config": config,
            "exported_at": config_service.settings.last_updated.isoformat() if config_service.settings.last_updated else None,
            "version": config_service.settings.config_version
        }
        
    except Exception as e:
        logger.error(f"Failed to export configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=Dict[str, Any])
async def get_config_metrics(request: Request = None):
    """Get configuration service metrics."""
    user_id = request.headers.get("x-user-id") if request else "anonymous"
    
    try:
        metrics = config_service.get_runtime_metrics()
        
        logger.info(f"Configuration metrics retrieved by user: {user_id}")
        
        return {
            "success": True,
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Failed to get configuration metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Secret management endpoints
@router.post("/secrets", response_model=SecretResponse)
async def store_secret(
    secret_request: SecretRequest,
    http_request: Request = None
):
    """Store a secret securely."""
    user_id = http_request.headers.get("x-user-id") if http_request else "anonymous"
    
    try:
        success = secret_manager.store_secret(
            key=secret_request.key,
            value=secret_request.value,
            description=secret_request.description
        )
        
        if success:
            logger.info(f"Secret '{secret_request.key}' stored by user: {user_id}")
            return SecretResponse(
                success=True,
                message=f"Secret '{secret_request.key}' stored successfully"
            )
        else:
            logger.warning(f"Failed to store secret '{secret_request.key}' for user {user_id}")
            return SecretResponse(
                success=False,
                message=f"Failed to store secret '{secret_request.key}'"
            )
            
    except Exception as e:
        logger.error(f"Failed to store secret: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/secrets", response_model=Dict[str, Any])
async def list_secrets(
    include_values: bool = False,
    request: Request = None
):
    """List all secrets (metadata only unless include_values=True)."""
    user_id = request.headers.get("x-user-id") if request else "anonymous"
    
    try:
        secrets = secret_manager.list_secrets(include_values=include_values)
        
        logger.info(f"Secrets listed by user: {user_id}")
        
        return {
            "success": True,
            "secrets": secrets,
            "count": len(secrets)
        }
        
    except Exception as e:
        logger.error(f"Failed to list secrets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/secrets/{key}", response_model=SecretResponse)
async def get_secret(
    key: str,
    request: Request = None
):
    """Retrieve a secret."""
    user_id = request.headers.get("x-user-id") if request else "anonymous"
    
    try:
        value = secret_manager.get_secret(key)
        
        if value is not None:
            logger.info(f"Secret '{key}' retrieved by user: {user_id}")
            return SecretResponse(
                success=True,
                message=f"Secret '{key}' retrieved successfully",
                data={"value": value}
            )
        else:
            logger.warning(f"Secret '{key}' not found for user {user_id}")
            raise HTTPException(status_code=404, detail=f"Secret '{key}' not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve secret '{key}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/secrets/{key}", response_model=SecretResponse)
async def delete_secret(
    key: str,
    http_request: Request = None
):
    """Delete a secret."""
    user_id = http_request.headers.get("x-user-id") if http_request else "anonymous"
    
    try:
        success = secret_manager.delete_secret(key)
        
        if success:
            logger.info(f"Secret '{key}' deleted by user: {user_id}")
            return SecretResponse(
                success=True,
                message=f"Secret '{key}' deleted successfully"
            )
        else:
            logger.warning(f"Secret '{key}' not found for deletion by user {user_id}")
            raise HTTPException(status_code=404, detail=f"Secret '{key}' not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete secret '{key}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=Dict[str, Any])
async def config_health_check():
    """Health check for configuration system."""
    try:
        config_health = config_service.health_check()
        secret_health = secret_manager.health_check()
        
        overall_status = "healthy" if (
            config_health["status"] == "healthy" and 
            secret_health["status"] == "healthy"
        ) else "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": config_service.settings.last_updated.isoformat() if config_service.settings.last_updated else None,
            "config_service": config_health,
            "secret_manager": secret_health
        }
        
    except Exception as e:
        logger.error(f"Configuration health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": None
        }
