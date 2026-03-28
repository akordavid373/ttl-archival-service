from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import logging
import uuid
import asyncio
import io

from ..database import get_db
from ..services.export_service import ExportService, ImportService, ExportFormat, CompressionType
from ..utils.data_processor import BulkDataProcessor
from ..utils.audit_logger import audit_logger_instance, AuditAction

router = APIRouter(prefix="/api/v1/data", tags=["data-export-import"])

# Initialize services
export_service = ExportService()
import_service = ImportService()
bulk_processor = BulkDataProcessor()

logger = logging.getLogger(__name__)

@router.get("/export")
async def export_data(
    format: ExportFormat = Query(..., description="Export format"),
    policy_id: Optional[int] = Query(None, description="Filter by policy ID"),
    date_from: Optional[datetime] = Query(None, description="Filter by date from"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to"),
    compression: CompressionType = Query(CompressionType.NONE, description="Compression type"),
    include_metadata: bool = Query(True, description="Include policy metadata"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Export archive data in specified format"""
    try:
        # Generate export ID for progress tracking
        export_id = str(uuid.uuid4())
        
        # Export data
        content = await export_service.export_records(
            db=db,
            format=format,
            policy_id=policy_id,
            date_from=date_from,
            date_to=date_to,
            compression=compression,
            include_metadata=include_metadata
        )
        
        # Determine content type and filename
        content_type = _get_content_type(format, compression)
        filename = _generate_filename(format, compression)
        
        # Log export operation
        await audit_logger_instance.log_user_action(
            db=db,
            user_id="system",
            action="EXPORT_DATA",
            description=f"Data export initiated - format: {format}, compression: {compression}",
            resource_type="data_export",
            resource_id=export_id,
            new_values={
                "format": format,
                "compression": compression,
                "policy_id": policy_id,
                "date_from": date_from.isoformat() if date_from else None,
                "date_to": date_to.isoformat() if date_to else None
            }
        )
        
        # Return response
        if isinstance(content, bytes):
            return Response(
                content=content,
                media_type=content_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:
            return StreamingResponse(
                io.StringIO(content),
                media_type=content_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_data(
    file: UploadFile = File(..., description="Data file to import"),
    format: ExportFormat = Query(..., description="Import format"),
    validate_data: bool = Query(True, description="Validate data during import"),
    skip_errors: bool = Query(False, description="Skip errors and continue processing"),
    update_existing: bool = Query(False, description="Update existing records"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Import archive data from uploaded file"""
    try:
        # Generate import ID for progress tracking
        import_id = str(uuid.uuid4())
        
        # Read file content
        content = await file.read()
        
        # Decode if needed
        if isinstance(content, bytes):
            try:
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                # Keep as bytes if it's binary data
                pass
        
        # Import data
        result = await import_service.import_records(
            db=db,
            content=content,
            format=format,
            validate_data=validate_data,
            skip_errors=skip_errors,
            update_existing=update_existing
        )
        
        # Log import operation
        await audit_logger_instance.log_user_action(
            db=db,
            user_id="system",
            action="IMPORT_DATA",
            description=f"Data import completed - format: {format}, file: {file.filename}",
            resource_type="data_import",
            resource_id=import_id,
            new_values={
                "format": format,
                "filename": file.filename,
                "validate_data": validate_data,
                "skip_errors": skip_errors,
                "update_existing": update_existing,
                "imported_count": result['imported_count'],
                "error_count": result['error_count']
            }
        )
        
        return {
            "import_id": import_id,
            "status": "completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Import error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/{export_id}/progress")
async def get_export_progress(export_id: str):
    """Get export operation progress"""
    try:
        progress = await export_service.get_export_progress(export_id)
        return progress
    except Exception as e:
        logger.error(f"Progress tracking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/import/{import_id}/progress")
async def get_import_progress(import_id: str):
    """Get import operation progress"""
    try:
        progress = await import_service.get_import_progress(import_id)
        return progress
    except Exception as e:
        logger.error(f"Progress tracking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_import_data(
    file: UploadFile = File(..., description="Data file to validate"),
    format: ExportFormat = Query(..., description="File format"),
    db: Session = Depends(get_db)
):
    """Validate import data without actually importing"""
    try:
        # Read file content
        content = await file.read()
        
        # Decode if needed
        if isinstance(content, bytes):
            try:
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                pass
        
        # Parse content based on format
        if format == ExportFormat.CSV:
            records = import_service._import_csv(content)
        elif format == ExportFormat.JSON:
            records = import_service._import_json(content)
        elif format == ExportFormat.XML:
            records = import_service._import_xml(content)
        
        # Validate bulk data
        validation_result = bulk_processor.validate_bulk_data(records)
        
        # Estimate processing time
        time_estimate = bulk_processor.estimate_processing_time(len(records))
        
        return {
            "validation_result": validation_result,
            "time_estimate": time_estimate,
            "sample_records": records[:3] if records else []  # Return first 3 records as sample
        }
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/formats")
async def get_supported_formats():
    """Get supported export/import formats and options"""
    return {
        "export_formats": [format.value for format in ExportFormat],
        "compression_types": [comp.value for comp in CompressionType],
        "max_file_size": "100MB",
        "supported_features": {
            "filtered_export": True,
            "bulk_operations": True,
            "data_validation": True,
            "progress_tracking": True,
            "error_recovery": True,
            "compression": True,
            "metadata_inclusion": True
        }
    }

def _get_content_type(format: ExportFormat, compression: CompressionType) -> str:
    """Get appropriate content type based on format and compression"""
    if compression == CompressionType.ZIP:
        return "application/zip"
    elif compression == CompressionType.GZIP:
        return "application/gzip"
    elif format == ExportFormat.JSON:
        return "application/json"
    elif format == ExportFormat.CSV:
        return "text/csv"
    elif format == ExportFormat.XML:
        return "application/xml"
    else:
        return "text/plain"

def _generate_filename(format: ExportFormat, compression: CompressionType) -> str:
    """Generate filename for export"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    base_filename = f"archive_export_{timestamp}.{format.value}"
    
    if compression == CompressionType.ZIP:
        return f"{base_filename}.zip"
    elif compression == CompressionType.GZIP:
        return f"{base_filename}.gz"
    else:
        return base_filename
