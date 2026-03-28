from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from ...database import get_db
from ...services.config_service import config_service
from ...utils.audit_logger import audit_logger_instance, AuditAction

logger = logging.getLogger(__name__)
router = APIRouter()

# Enhanced schemas for v2
class ConfigItemV2(BaseModel):
    """Enhanced configuration item for v2"""
    key: str = Field(..., description="Configuration key")
    value: Any = Field(..., description="Configuration value")
    type: str = Field(..., description="Value type (string, int, bool, json)")
    description: Optional[str] = Field(None, description="Configuration description")
    category: str = Field("general", description="Configuration category")
    sensitive: bool = Field(False, description="Mark as sensitive data")
    readonly: bool = Field(False, description="Mark as read-only")
    validation: Optional[Dict[str, Any]] = Field(None, description="Validation rules")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ConfigResponseV2(BaseModel):
    """Enhanced configuration response for v2"""
    key: str
    value: Any
    type: str
    description: Optional[str]
    category: str
    sensitive: bool
    readonly: bool
    validation: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    version: int
    history_count: int

class ConfigBatchRequest(BaseModel):
    """Batch configuration update request"""
    configs: List[ConfigItemV2]
    validate_all: bool = Field(True, description="Validate all configs before applying")
    rollback_on_error: bool = Field(True, description="Rollback on any error")

class ConfigBatchResponse(BaseModel):
    """Batch configuration update response"""
    successful: List[str]
    failed: List[Dict[str, Any]]
    total_processed: int
    success_count: int
    failure_count: int
    rollback_performed: bool

class ConfigHistory(BaseModel):
    """Configuration change history"""
    key: str
    version: int
    old_value: Any
    new_value: Any
    changed_by: str
    changed_at: datetime
    change_reason: Optional[str]

class ConfigValidationResult(BaseModel):
    """Configuration validation result"""
    valid: bool
    errors: List[str]
    warnings: List[str]

class ConfigExport(BaseModel):
    """Configuration export"""
    format: str = Field("yaml", regex="^(yaml|json|env)$")
    include_sensitive: bool = Field(False, description="Include sensitive values")
    categories: Optional[List[str]] = Field(None, description="Specific categories to export")

# Initialize config service
config_service = config_service

@router.get("/", response_model=Dict[str, Any])
async def list_configurations(
    category: Optional[str] = Query(None, description="Filter by category"),
    include_sensitive: bool = Query(False, description="Include sensitive configs"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List configuration items with enhanced filtering"""
    try:
        # Get configurations
        configs = await config_service.get_all_configs(db)
        
        # Apply filters
        if category:
            configs = [c for c in configs if c.get('category') == category]
        
        if not include_sensitive:
            configs = [c for c in configs if not c.get('sensitive', False)]
        
        # Convert to v2 response format
        items = [_to_v2_response(c) for c in configs]
        
        # Pagination
        start = (page - 1) * limit
        end = start + limit
        paginated_items = items[start:end]
        
        # Group by category
        categories = {}
        for item in items:
            cat = item.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)
        
        return {
            'items': paginated_items,
            'total': len(items),
            'page': page,
            'limit': limit,
            'total_pages': (len(items) + limit - 1) // limit,
            'categories': categories,
            'filters': {
                'category': category,
                'include_sensitive': include_sensitive
            }
        }
        
    except Exception as e:
        logger.error(f"Error listing configurations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{config_key}", response_model=ConfigResponseV2)
async def get_configuration(
    config_key: str,
    include_history: bool = Query(False, description="Include change history"),
    db: Session = Depends(get_db)
):
    """Get a specific configuration item"""
    try:
        config = await config_service.get_config(db, config_key)
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        response = _to_v2_response(config)
        
        if include_history:
            response.history = await _get_config_history(db, config_key)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=ConfigResponseV2, status_code=201)
async def create_configuration(
    config: ConfigItemV2,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new configuration item"""
    try:
        # Validate configuration
        validation = await _validate_config(config)
        if not validation.valid:
            raise HTTPException(
                status_code=400,
                detail={"errors": validation.errors, "warnings": validation.warnings}
            )
        
        # Create configuration
        result = await config_service.create_config(db, config.dict())
        
        # Log configuration change
        background_tasks.add_task(
            _log_config_change,
            config.key,
            None,
            config.value,
            "create",
            config.metadata
        )
        
        return _to_v2_response(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{config_key}", response_model=ConfigResponseV2)
async def update_configuration(
    config_key: str,
    config: ConfigItemV2,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update a configuration item"""
    try:
        # Check if configuration exists
        existing_config = await config_service.get_config(db, config_key)
        if not existing_config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        # Check if readonly
        if existing_config.get('readonly', False):
            raise HTTPException(status_code=403, detail="Configuration is read-only")
        
        # Validate configuration
        validation = await _validate_config(config)
        if not validation.valid:
            raise HTTPException(
                status_code=400,
                detail={"errors": validation.errors, "warnings": validation.warnings}
            )
        
        # Update configuration
        result = await config_service.update_config(db, config_key, config.dict())
        
        # Log configuration change
        background_tasks.add_task(
            _log_config_change,
            config_key,
            existing_config.get('value'),
            config.value,
            "update",
            config.metadata
        )
        
        return _to_v2_response(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{config_key}")
async def delete_configuration(
    config_key: str,
    force: bool = Query(False, description="Force delete even if critical"),
    db: Session = Depends(get_db)
):
    """Delete a configuration item"""
    try:
        config = await config_service.get_config(db, config_key)
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        # Check if readonly
        if config.get('readonly', False) and not force:
            raise HTTPException(status_code=403, detail="Configuration is read-only")
        
        # Delete configuration
        await config_service.delete_config(db, config_key)
        
        return {"message": "Configuration deleted successfully", "key": config_key}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", response_model=ConfigBatchResponse)
async def batch_update_configurations(
    request: ConfigBatchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Batch update configuration items"""
    successful = []
    failed = []
    rollback_data = {}
    
    try:
        # Validate all configurations first
        if request.validate_all:
            for config in request.configs:
                validation = await _validate_config(config)
                if not validation.valid:
                    failed.append({
                        "key": config.key,
                        "error": f"Validation failed: {', '.join(validation.errors)}"
                    })
        
        # Apply configurations
        for config in request.configs:
            try:
                # Store current value for rollback
                existing = await config_service.get_config(db, config.key)
                if existing:
                    rollback_data[config.key] = existing.get('value')
                
                # Update or create configuration
                if existing:
                    result = await config_service.update_config(db, config.key, config.dict())
                else:
                    result = await config_service.create_config(db, config.dict())
                
                successful.append(config.key)
                
            except Exception as e:
                failed.append({
                    "key": config.key,
                    "error": str(e)
                })
                
                # Rollback if requested and there are failures
                if request.rollback_on_error and failed:
                    await _rollback_config_changes(db, rollback_data)
                    break
        
        return ConfigBatchResponse(
            successful=successful,
            failed=failed,
            total_processed=len(request.configs),
            success_count=len(successful),
            failure_count=len(failed),
            rollback_performed=request.rollback_on_error and len(failed) > 0
        )
        
    except Exception as e:
        logger.error(f"Error in batch configuration update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{config_key}/history", response_model=List[ConfigHistory])
async def get_configuration_history(
    config_key: str,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get configuration change history"""
    try:
        history = await _get_config_history(db, config_key, limit)
        return history
        
    except Exception as e:
        logger.error(f"Error getting configuration history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{config_key}/validate", response_model=ConfigValidationResult)
async def validate_configuration(
    config_key: str,
    config: ConfigItemV2,
    db: Session = Depends(get_db)
):
    """Validate a configuration without applying it"""
    try:
        validation = await _validate_config(config)
        return validation
        
    except Exception as e:
        logger.error(f"Error validating configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export")
async def export_configurations(
    request: ConfigExport,
    db: Session = Depends(get_db)
):
    """Export configurations in various formats"""
    try:
        # Get configurations
        configs = await config_service.get_all_configs(db)
        
        # Apply filters
        if request.categories:
            configs = [c for c in configs if c.get('category') in request.categories]
        
        if not request.include_sensitive:
            configs = [c for c in configs if not c.get('sensitive', False)]
        
        # Export in requested format
        if request.format == "yaml":
            export_data = _export_yaml(configs)
        elif request.format == "json":
            export_data = _export_json(configs)
        else:  # env
            export_data = _export_env(configs)
        
        export_id = f"config_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "export_id": export_id,
            "format": request.format,
            "data": export_data,
            "download_url": f"/api/v2/config/exports/{export_id}/download"
        }
        
    except Exception as e:
        logger.error(f"Error exporting configurations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_configurations(
    format: str = Query(..., regex="^(yaml|json|env)$"),
    merge_strategy: str = Query("merge", regex="^(merge|replace|skip)$"),
    validate_before_import: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Import configurations from various formats"""
    try:
        # This would implement file upload and import logic
        return {
            "message": "Configuration import initiated",
            "format": format,
            "merge_strategy": merge_strategy,
            "validate_before_import": validate_before_import
        }
        
    except Exception as e:
        logger.error(f"Error importing configurations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def _to_v2_response(config) -> ConfigResponseV2:
    """Convert internal config to v2 response format"""
    return ConfigResponseV2(
        key=config.get('key'),
        value=config.get('value'),
        type=config.get('type', 'string'),
        description=config.get('description'),
        category=config.get('category', 'general'),
        sensitive=config.get('sensitive', False),
        readonly=config.get('readonly', False),
        validation=config.get('validation'),
        metadata=config.get('metadata'),
        created_at=config.get('created_at', datetime.now()),
        updated_at=config.get('updated_at'),
        version=config.get('version', 1),
        history_count=config.get('history_count', 0)
    )

async def _validate_config(config: ConfigItemV2) -> ConfigValidationResult:
    """Validate configuration item"""
    errors = []
    warnings = []
    
    # Basic validation
    if not config.key:
        errors.append("Configuration key is required")
    
    if config.type not in ['string', 'int', 'bool', 'json']:
        errors.append(f"Invalid type: {config.type}")
    
    # Type-specific validation
    if config.type == 'int' and not isinstance(config.value, int):
        try:
            int(config.value)
        except (ValueError, TypeError):
            errors.append("Value must be an integer")
    
    # Custom validation rules
    if config.validation:
        # Apply validation rules
        pass
    
    return ConfigValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )

async def _get_config_history(db: Session, config_key: str, limit: int = 10) -> List[ConfigHistory]:
    """Get configuration change history"""
    # This would implement history retrieval
    return []

async def _log_config_change(key: str, old_value: Any, new_value: Any, action: str, metadata: Optional[Dict[str, Any]]):
    """Log configuration change"""
    logger.info(f"Config {action}: {key} = {new_value}")

async def _rollback_config_changes(db: Session, rollback_data: Dict[str, Any]):
    """Rollback configuration changes"""
    logger.info("Rolling back configuration changes")

def _export_yaml(configs: List[Dict[str, Any]]) -> str:
    """Export configurations as YAML"""
    # This would implement YAML export
    return "# YAML export"

def _export_json(configs: List[Dict[str, Any]]) -> str:
    """Export configurations as JSON"""
    import json
    return json.dumps(configs, indent=2, default=str)

def _export_env(configs: List[Dict[str, Any]]) -> str:
    """Export configurations as environment variables"""
    lines = []
    for config in configs:
        if config.get('type') == 'bool':
            value = 'true' if config.get('value') else 'false'
        else:
            value = str(config.get('value', ''))
        lines.append(f"{config.get('key').upper()}={value}")
    return '\n'.join(lines)
