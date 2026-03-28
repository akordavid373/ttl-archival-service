import csv
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import zipfile
import io
from typing import List, Dict, Any, Optional, Union, BinaryIO
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
import logging
from enum import Enum

from ..models import ArchiveRecord, ArchivePolicy
from ..schemas import ArchiveRecordResponse, ArchivePolicyResponse

logger = logging.getLogger(__name__)

class ExportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    XML = "xml"

class CompressionType(str, Enum):
    NONE = "none"
    ZIP = "zip"
    GZIP = "gzip"

class DataProcessor:
    """Utility class for processing data in different formats"""
    
    @staticmethod
    def validate_record_data(record_data: Dict[str, Any]) -> bool:
        """Validate record data structure"""
        required_fields = ['original_data_id', 'data_type', 'policy_id']
        return all(field in record_data for field in required_fields)
    
    @staticmethod
    def sanitize_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data for export"""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                sanitized[key] = value.isoformat()
            elif isinstance(value, (dict, list)):
                sanitized[key] = json.dumps(value)
            else:
                sanitized[key] = str(value) if value is not None else ""
        return sanitized
    
    @staticmethod
    def deserialize_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize data after import"""
        deserialized = {}
        for key, value in data.items():
            try:
                # Try to parse as JSON first
                if isinstance(value, str) and value.startswith(('{', '[')):
                    deserialized[key] = json.loads(value)
                elif isinstance(value, str):
                    # Try to parse as datetime
                    try:
                        deserialized[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except ValueError:
                        deserialized[key] = value
                else:
                    deserialized[key] = value
            except Exception:
                deserialized[key] = value
        return deserialized

class ExportService:
    """Service for exporting archival data"""
    
    def __init__(self):
        self.processor = DataProcessor()
    
    async def export_records(
        self,
        db: Session,
        format: ExportFormat,
        policy_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        compression: CompressionType = CompressionType.NONE,
        include_metadata: bool = True
    ) -> Union[str, bytes]:
        """Export archive records in specified format"""
        try:
            # Query records
            query = db.query(ArchiveRecord)
            
            if policy_id:
                query = query.filter(ArchiveRecord.policy_id == policy_id)
            
            if date_from:
                query = query.filter(ArchiveRecord.archived_at >= date_from)
            
            if date_to:
                query = query.filter(ArchiveRecord.archived_at <= date_to)
            
            records = query.all()
            
            # Convert to response format
            record_data = []
            for record in records:
                record_dict = {
                    'id': record.id,
                    'policy_id': record.policy_id,
                    'original_data_id': record.original_data_id,
                    'data_type': record.data_type,
                    'file_path': record.file_path,
                    'file_size_bytes': record.file_size_bytes,
                    'checksum': record.checksum,
                    'metadata': record.metadata,
                    'status': record.status,
                    'expires_at': record.expires_at.isoformat() if record.expires_at else None,
                    'archived_at': record.archived_at.isoformat() if record.archived_at else None,
                    'deleted_at': record.deleted_at.isoformat() if record.deleted_at else None
                }
                
                if include_metadata and record.policy:
                    record_dict['policy_name'] = record.policy.name
                    record_dict['policy_ttl_days'] = record.policy.ttl_days
                
                record_data.append(record_dict)
            
            # Generate export based on format
            if format == ExportFormat.CSV:
                content = self._export_csv(record_data)
            elif format == ExportFormat.JSON:
                content = self._export_json(record_data)
            elif format == ExportFormat.XML:
                content = self._export_xml(record_data)
            
            # Apply compression if needed
            if compression == CompressionType.ZIP:
                return self._compress_zip(content, f"archive_export.{format.value}")
            elif compression == CompressionType.GZIP:
                return self._compress_gzip(content.encode() if isinstance(content, str) else content)
            
            return content
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
    
    def _export_csv(self, records: List[Dict[str, Any]]) -> str:
        """Export records to CSV format"""
        if not records:
            return ""
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=records[0].keys())
        writer.writeheader()
        
        for record in records:
            sanitized = self.processor.sanitize_data(record)
            writer.writerow(sanitized)
        
        return output.getvalue()
    
    def _export_json(self, records: List[Dict[str, Any]]) -> str:
        """Export records to JSON format"""
        export_data = {
            'export_timestamp': datetime.utcnow().isoformat(),
            'total_records': len(records),
            'records': [self.processor.sanitize_data(record) for record in records]
        }
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def _export_xml(self, records: List[Dict[str, Any]]) -> str:
        """Export records to XML format"""
        root = ET.Element("archive_export")
        root.set("timestamp", datetime.utcnow().isoformat())
        root.set("total_records", str(len(records)))
        
        for record in records:
            record_elem = ET.SubElement(root, "record")
            sanitized = self.processor.sanitize_data(record)
            
            for key, value in sanitized.items():
                elem = ET.SubElement(record_elem, key)
                elem.text = str(value)
        
        # Pretty print XML
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def _compress_zip(self, content: str, filename: str) -> bytes:
        """Compress content to ZIP format"""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(filename, content)
        return zip_buffer.getvalue()
    
    def _compress_gzip(self, content: bytes) -> bytes:
        """Compress content using GZIP"""
        import gzip
        return gzip.compress(content)
    
    async def get_export_progress(self, export_id: str) -> Dict[str, Any]:
        """Get progress of an export operation"""
        # This would typically use a cache or database to track progress
        # For now, return a placeholder
        return {
            'export_id': export_id,
            'status': 'completed',
            'progress_percentage': 100,
            'records_processed': 0,
            'total_records': 0,
            'start_time': datetime.utcnow().isoformat(),
            'end_time': datetime.utcnow().isoformat()
        }

class ImportService:
    """Service for importing archival data"""
    
    def __init__(self):
        self.processor = DataProcessor()
    
    async def import_records(
        self,
        db: Session,
        content: Union[str, bytes],
        format: ExportFormat,
        validate_data: bool = True,
        skip_errors: bool = False,
        update_existing: bool = False
    ) -> Dict[str, Any]:
        """Import archive records from specified format"""
        try:
            # Parse content based on format
            if format == ExportFormat.CSV:
                records = self._import_csv(content)
            elif format == ExportFormat.JSON:
                records = self._import_json(content)
            elif format == ExportFormat.XML:
                records = self._import_xml(content)
            
            # Validate and process records
            imported_count = 0
            error_count = 0
            errors = []
            
            for record_data in records:
                try:
                    # Validate data if requested
                    if validate_data and not self.processor.validate_record_data(record_data):
                        raise ValueError("Invalid record data structure")
                    
                    # Deserialize data
                    processed_data = self.processor.deserialize_data(record_data)
                    
                    # Check if record already exists
                    existing_record = None
                    if 'id' in processed_data:
                        existing_record = db.query(ArchiveRecord).filter(
                            ArchiveRecord.id == processed_data['id']
                        ).first()
                    
                    if existing_record and not update_existing:
                        errors.append(f"Record {processed_data.get('id')} already exists")
                        error_count += 1
                        continue
                    
                    # Create or update record
                    if existing_record:
                        # Update existing record
                        for key, value in processed_data.items():
                            if hasattr(existing_record, key) and key not in ['id']:
                                setattr(existing_record, key, value)
                    else:
                        # Create new record
                        record = ArchiveRecord(**processed_data)
                        db.add(record)
                    
                    imported_count += 1
                    
                except Exception as e:
                    error_msg = f"Error processing record: {str(e)}"
                    errors.append(error_msg)
                    error_count += 1
                    
                    if not skip_errors:
                        raise HTTPException(status_code=400, detail=error_msg)
            
            # Commit changes
            db.commit()
            
            return {
                'imported_count': imported_count,
                'error_count': error_count,
                'errors': errors[:10],  # Limit errors to first 10
                'total_processed': len(records)
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Import failed: {e}")
            raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
    
    def _import_csv(self, content: str) -> List[Dict[str, Any]]:
        """Import records from CSV format"""
        records = []
        reader = csv.DictReader(io.StringIO(content))
        
        for row in reader:
            records.append(dict(row))
        
        return records
    
    def _import_json(self, content: Union[str, bytes]) -> List[Dict[str, Any]]:
        """Import records from JSON format"""
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        
        data = json.loads(content)
        
        # Handle both wrapped and unwrapped formats
        if isinstance(data, dict) and 'records' in data:
            return data['records']
        elif isinstance(data, list):
            return data
        else:
            raise ValueError("Invalid JSON format")
    
    def _import_xml(self, content: Union[str, bytes]) -> List[Dict[str, Any]]:
        """Import records from XML format"""
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        
        root = ET.fromstring(content)
        records = []
        
        for record_elem in root.findall('record'):
            record_data = {}
            for child in record_elem:
                record_data[child.tag] = child.text
            records.append(record_data)
        
        return records
    
    async def get_import_progress(self, import_id: str) -> Dict[str, Any]:
        """Get progress of an import operation"""
        # This would typically use a cache or database to track progress
        # For now, return a placeholder
        return {
            'import_id': import_id,
            'status': 'completed',
            'progress_percentage': 100,
            'records_processed': 0,
            'total_records': 0,
            'start_time': datetime.utcnow().isoformat(),
            'end_time': datetime.utcnow().isoformat()
        }
