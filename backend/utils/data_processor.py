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

class BulkDataProcessor:
    """Utility class for bulk data operations"""
    
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
    
    def process_in_batches(self, data: List[Dict[str, Any]], processor_func) -> List[Any]:
        """Process data in batches to avoid memory issues"""
        results = []
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]
            batch_results = processor_func(batch)
            results.extend(batch_results)
        return results
    
    def validate_bulk_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate bulk data and return validation results"""
        validation_results = {
            'total_records': len(data),
            'valid_records': 0,
            'invalid_records': 0,
            'errors': []
        }
        
        for i, record in enumerate(data):
            if DataProcessor.validate_record_data(record):
                validation_results['valid_records'] += 1
            else:
                validation_results['invalid_records'] += 1
                validation_results['errors'].append(f"Record {i}: Missing required fields")
        
        return validation_results
    
    def estimate_processing_time(self, record_count: int) -> Dict[str, Any]:
        """Estimate processing time based on record count"""
        # Simple estimation based on typical processing rates
        records_per_second = 100  # Adjust based on actual performance
        estimated_seconds = record_count / records_per_second
        
        return {
            'estimated_seconds': estimated_seconds,
            'estimated_minutes': estimated_seconds / 60,
            'estimated_hours': estimated_seconds / 3600
        }
