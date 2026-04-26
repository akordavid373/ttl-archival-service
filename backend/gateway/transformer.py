"""
API Gateway Transformer Module

Handles request and response transformation including
header manipulation, body transformation, and protocol adaptation.
"""

import json
import logging
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import base64
import hashlib
import hmac
from urllib.parse import urlparse, parse_qs
from fastapi import Request, Response
from starlette.responses import StreamingResponse
import httpx

logger = logging.getLogger(__name__)


class TransformationType(Enum):
    """Types of transformations"""
    REQUEST = "request"
    RESPONSE = "response"
    BOTH = "both"


class DataType(Enum):
    """Data types for transformation"""
    JSON = "json"
    XML = "xml"
    FORM = "form"
    TEXT = "text"
    BINARY = "binary"


@dataclass
class TransformationRule:
    """Transformation rule configuration"""
    name: str
    transformation_type: TransformationType
    data_type: DataType
    conditions: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    priority: int = 0


@dataclass
class HeaderTransformation:
    """Header transformation rule"""
    add_headers: Dict[str, str] = field(default_factory=dict)
    remove_headers: List[str] = field(default_factory=list)
    replace_headers: Dict[str, str] = field(default_factory=dict)
    prefix_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class BodyTransformation:
    """Body transformation rule"""
    json_path_operations: Dict[str, Any] = field(default_factory=dict)
    xpath_operations: Dict[str, Any] = field(default_factory=dict)
    regex_operations: Dict[str, str] = field(default_factory=dict)
    template_operations: Dict[str, str] = field(default_factory=dict)
    script_operations: List[str] = field(default_factory=list)


@dataclass
class QueryTransformation:
    """Query parameter transformation rule"""
    add_params: Dict[str, str] = field(default_factory=dict)
    remove_params: List[str] = field(default_factory=list)
    rename_params: Dict[str, str] = field(default_factory=dict)


class Transformer(ABC):
    """Abstract base class for transformers"""
    
    @abstractmethod
    async def transform(self, data: Any, context: Dict[str, Any]) -> Any:
        """Transform data"""
        pass


class JSONTransformer(Transformer):
    """JSON data transformer"""
    
    def __init__(self, operations: Dict[str, Any]):
        self.operations = operations
    
    async def transform(self, data: Union[str, dict], context: Dict[str, Any]) -> Union[str, dict]:
        """Transform JSON data"""
        if isinstance(data, str):
            try:
                json_data = json.loads(data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return data
        else:
            json_data = data.copy()
        
        # Apply operations
        for path, operation in self.operations.items():
            try:
                json_data = self._apply_json_operation(json_data, path, operation, context)
            except Exception as e:
                logger.error(f"JSON operation failed for path {path}: {e}")
        
        return json_data if isinstance(data, dict) else json.dumps(json_data)
    
    def _apply_json_operation(self, data: dict, path: str, operation: Any, context: Dict[str, Any]) -> dict:
        """Apply a single JSON operation"""
        parts = path.split('.')
        current = data
        
        # Navigate to the target location
        for part in parts[:-1]:
            if part not in current:
                if operation.get('create_missing', False):
                    current[part] = {}
                else:
                    return data
            current = current[part]
        
        target_key = parts[-1]
        
        if operation['type'] == 'set':
            value = self._resolve_value(operation['value'], context)
            current[target_key] = value
        elif operation['type'] == 'remove':
            current.pop(target_key, None)
        elif operation['type'] == 'rename':
            if target_key in current:
                new_name = self._resolve_value(operation['new_name'], context)
                current[new_name] = current.pop(target_key)
        elif operation['type'] == 'copy':
            if target_key in current:
                new_name = self._resolve_value(operation['new_name'], context)
                current[new_name] = current[target_key]
        elif operation['type'] == 'transform':
            if target_key in current:
                current[target_key] = self._apply_value_transform(
                    current[target_key], operation['transform'], context
                )
        
        return data
    
    def _resolve_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """Resolve value with context substitution"""
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            key = value[2:-1]
            return context.get(key, value)
        return value
    
    def _apply_value_transform(self, value: Any, transform: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Apply value transformation"""
        transform_type = transform['type']
        
        if transform_type == 'uppercase' and isinstance(value, str):
            return value.upper()
        elif transform_type == 'lowercase' and isinstance(value, str):
            return value.lower()
        elif transform_type == 'hash':
            return hashlib.sha256(str(value).encode()).hexdigest()
        elif transform_type == 'base64_encode':
            return base64.b64encode(str(value).encode()).decode()
        elif transform_type == 'base64_decode':
            try:
                return base64.b64decode(str(value)).decode()
            except Exception:
                return value
        elif transform_type == 'template':
            template = transform['template']
            return template.format(value=value, **context)
        
        return value


class XMLTransformer(Transformer):
    """XML data transformer"""
    
    def __init__(self, operations: Dict[str, Any]):
        self.operations = operations
    
    async def transform(self, data: str, context: Dict[str, Any]) -> str:
        """Transform XML data"""
        try:
            root = ET.fromstring(data)
            
            for xpath, operation in self.operations.items():
                try:
                    self._apply_xml_operation(root, xpath, operation, context)
                except Exception as e:
                    logger.error(f"XML operation failed for xpath {xpath}: {e}")
            
            return ET.tostring(root, encoding='unicode')
        
        except ET.ParseError as e:
            logger.error(f"XML parse error: {e}")
            return data
    
    def _apply_xml_operation(self, root: ET.Element, xpath: str, operation: Any, context: Dict[str, Any]):
        """Apply XML operation"""
        # Simple XPath implementation (in production, use lxml for full XPath support)
        elements = root.findall(xpath)
        
        for element in elements:
            if operation['type'] == 'set_text':
                value = self._resolve_value(operation['value'], context)
                element.text = str(value)
            elif operation['type'] == 'set_attribute':
                attr_name = operation['attribute']
                value = self._resolve_value(operation['value'], context)
                element.set(attr_name, str(value))
            elif operation['type'] == 'remove':
                root.remove(element)
    
    def _resolve_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """Resolve value with context substitution"""
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            key = value[2:-1]
            return context.get(key, value)
        return value


class RegexTransformer(Transformer):
    """Regex-based text transformer"""
    
    def __init__(self, operations: Dict[str, str]):
        self.operations = {pattern: re.compile(regex) for pattern, regex in operations.items()}
    
    async def transform(self, data: str, context: Dict[str, Any]) -> str:
        """Transform text using regex operations"""
        result = data
        
        for pattern, regex in self.operations.items():
            try:
                # Simple replacement - in production, support more complex operations
                result = regex.sub(pattern, result)
            except Exception as e:
                logger.error(f"Regex operation failed: {e}")
        
        return result


class TemplateTransformer(Transformer):
    """Template-based transformer"""
    
    def __init__(self, templates: Dict[str, str]):
        self.templates = templates
    
    async def transform(self, data: Any, context: Dict[str, Any]) -> str:
        """Transform using templates"""
        template_name = context.get('template', 'default')
        template = self.templates.get(template_name, self.templates.get('default', ''))
        
        try:
            return template.format(data=data, **context)
        except Exception as e:
            logger.error(f"Template transformation failed: {e}")
            return str(data)


class RequestTransformer:
    """Request transformer implementation"""
    
    def __init__(self):
        self.header_transformations: List[HeaderTransformation] = []
        self.body_transformations: List[BodyTransformation] = []
        self.query_transformations: List[QueryTransformation] = []
        self.json_transformers: List[JSONTransformer] = []
        self.xml_transformers: List[XMLTransformer] = []
        self.regex_transformers: List[RegexTransformer] = []
        self.template_transformers: List[TemplateTransformer] = []
    
    async def transform_request(self, request: Request, context: Dict[str, Any]) -> Request:
        """Transform an incoming request"""
        # Transform headers
        await self._transform_headers(request, context)
        
        # Transform query parameters
        await self._transform_query_params(request, context)
        
        # Transform body if present
        if request.method in ['POST', 'PUT', 'PATCH']:
            await self._transform_request_body(request, context)
        
        return request
    
    async def _transform_headers(self, request: Request, context: Dict[str, Any]):
        """Transform request headers"""
        headers = dict(request.headers)
        
        for header_transform in self.header_transformations:
            # Add headers
            for key, value in header_transform.add_headers.items():
                resolved_value = self._resolve_template(value, context)
                headers[key] = resolved_value
            
            # Remove headers
            for key in header_transform.remove_headers:
                headers.pop(key, None)
            
            # Replace headers
            for key, value in header_transform.replace_headers.items():
                resolved_value = self._resolve_template(value, context)
                headers[key] = resolved_value
            
            # Prefix headers
            for key, prefix in header_transform.prefix_headers.items():
                if key in headers:
                    headers[key] = prefix + headers[key]
        
        # Update request headers (this is conceptual - in practice, you'd need to create a new request)
        context['transformed_headers'] = headers
    
    async def _transform_query_params(self, request: Request, context: Dict[str, Any]):
        """Transform query parameters"""
        query_params = dict(request.query_params)
        
        for query_transform in self.query_transformations:
            # Add parameters
            for key, value in query_transform.add_params.items():
                resolved_value = self._resolve_template(value, context)
                query_params[key] = resolved_value
            
            # Remove parameters
            for key in query_transform.remove_params:
                query_params.pop(key, None)
            
            # Rename parameters
            for old_key, new_key in query_transform.rename_params.items():
                if old_key in query_params:
                    query_params[new_key] = query_params.pop(old_key)
        
        context['transformed_query_params'] = query_params
    
    async def _transform_request_body(self, request: Request, context: Dict[str, Any]):
        """Transform request body"""
        body = await request.body()
        content_type = request.headers.get('content-type', '')
        
        if not body:
            return
        
        # Transform based on content type
        if 'application/json' in content_type:
            transformed_body = await self._transform_json_body(body, context)
        elif 'application/xml' in content_type or 'text/xml' in content_type:
            transformed_body = await self._transform_xml_body(body, context)
        elif 'application/x-www-form-urlencoded' in content_type:
            transformed_body = await self._transform_form_body(body, context)
        else:
            transformed_body = await self._transform_text_body(body, context)
        
        context['transformed_body'] = transformed_body
    
    async def _transform_json_body(self, body: bytes, context: Dict[str, Any]) -> bytes:
        """Transform JSON body"""
        try:
            json_data = json.loads(body.decode())
            
            for transformer in self.json_transformers:
                json_data = await transformer.transform(json_data, context)
            
            return json.dumps(json_data).encode()
        
        except Exception as e:
            logger.error(f"JSON body transformation failed: {e}")
            return body
    
    async def _transform_xml_body(self, body: bytes, context: Dict[str, Any]) -> bytes:
        """Transform XML body"""
        try:
            xml_text = body.decode()
            
            for transformer in self.xml_transformers:
                xml_text = await transformer.transform(xml_text, context)
            
            return xml_text.encode()
        
        except Exception as e:
            logger.error(f"XML body transformation failed: {e}")
            return body
    
    async def _transform_form_body(self, body: bytes, context: Dict[str, Any]) -> bytes:
        """Transform form body"""
        try:
            form_data = parse_qs(body.decode())
            
            # Flatten form data
            flattened_data = {k: v[0] if len(v) == 1 else v for k, v in form_data.items()}
            
            # Apply transformations (convert to JSON, transform, convert back)
            for transformer in self.json_transformers:
                flattened_data = await transformer.transform(flattened_data, context)
            
            # Convert back to form encoding
            form_string = '&'.join([f"{k}={v}" for k, v in flattened_data.items()])
            return form_string.encode()
        
        except Exception as e:
            logger.error(f"Form body transformation failed: {e}")
            return body
    
    async def _transform_text_body(self, body: bytes, context: Dict[str, Any]) -> bytes:
        """Transform text body"""
        try:
            text = body.decode()
            
            for transformer in self.regex_transformers:
                text = await transformer.transform(text, context)
            
            for transformer in self.template_transformers:
                text = await transformer.transform(text, context)
            
            return text.encode()
        
        except Exception as e:
            logger.error(f"Text body transformation failed: {e}")
            return body
    
    def _resolve_template(self, template: str, context: Dict[str, Any]) -> str:
        """Resolve template variables"""
        try:
            return template.format(**context)
        except KeyError:
            return template


class ResponseTransformer:
    """Response transformer implementation"""
    
    def __init__(self):
        self.header_transformations: List[HeaderTransformation] = []
        self.body_transformations: List[BodyTransformation] = []
        self.json_transformers: List[JSONTransformer] = []
        self.xml_transformers: List[XMLTransformer] = []
        self.regex_transformers: List[RegexTransformer] = []
        self.template_transformers: List[TemplateTransformer] = []
    
    async def transform_response(self, response: Response, context: Dict[str, Any]) -> Response:
        """Transform a response"""
        # Transform headers
        await self._transform_response_headers(response, context)
        
        # Transform body if present
        if hasattr(response, 'body') and response.body:
            await self._transform_response_body(response, context)
        
        return response
    
    async def _transform_response_headers(self, response: Response, context: Dict[str, Any]):
        """Transform response headers"""
        headers = dict(response.headers)
        
        for header_transform in self.header_transformations:
            # Add headers
            for key, value in header_transform.add_headers.items():
                resolved_value = self._resolve_template(value, context)
                headers[key] = resolved_value
            
            # Remove headers
            for key in header_transform.remove_headers:
                headers.pop(key, None)
            
            # Replace headers
            for key, value in header_transform.replace_headers.items():
                resolved_value = self._resolve_template(value, context)
                headers[key] = resolved_value
        
        # Update response headers
        for key, value in headers.items():
            response.headers[key] = value
    
    async def _transform_response_body(self, response: Response, context: Dict[str, Any]):
        """Transform response body"""
        content_type = response.headers.get('content-type', '')
        
        if 'application/json' in content_type:
            transformed_body = await self._transform_json_response(response, context)
        elif 'application/xml' in content_type or 'text/xml' in content_type:
            transformed_body = await self._transform_xml_response(response, context)
        else:
            transformed_body = await self._transform_text_response(response, context)
        
        # Update response body (this is conceptual - implementation depends on response type)
        context['transformed_response_body'] = transformed_body
    
    async def _transform_json_response(self, response: Response, context: Dict[str, Any]) -> bytes:
        """Transform JSON response"""
        try:
            if hasattr(response, 'body'):
                json_data = json.loads(response.body.decode())
                
                for transformer in self.json_transformers:
                    json_data = await transformer.transform(json_data, context)
                
                return json.dumps(json_data).encode()
        
        except Exception as e:
            logger.error(f"JSON response transformation failed: {e}")
        
        return getattr(response, 'body', b'')
    
    async def _transform_xml_response(self, response: Response, context: Dict[str, Any]) -> bytes:
        """Transform XML response"""
        try:
            if hasattr(response, 'body'):
                xml_text = response.body.decode()
                
                for transformer in self.xml_transformers:
                    xml_text = await transformer.transform(xml_text, context)
                
                return xml_text.encode()
        
        except Exception as e:
            logger.error(f"XML response transformation failed: {e}")
        
        return getattr(response, 'body', b'')
    
    async def _transform_text_response(self, response: Response, context: Dict[str, Any]) -> bytes:
        """Transform text response"""
        try:
            if hasattr(response, 'body'):
                text = response.body.decode()
                
                for transformer in self.regex_transformers:
                    text = await transformer.transform(text, context)
                
                for transformer in self.template_transformers:
                    text = await transformer.transform(text, context)
                
                return text.encode()
        
        except Exception as e:
            logger.error(f"Text response transformation failed: {e}")
        
        return getattr(response, 'body', b'')
    
    def _resolve_template(self, template: str, context: Dict[str, Any]) -> str:
        """Resolve template variables"""
        try:
            return template.format(**context)
        except KeyError:
            return template


class GatewayTransformer:
    """
    Main gateway transformer class that orchestrates all transformations
    """
    
    def __init__(self):
        self.request_transformer = RequestTransformer()
        self.response_transformer = ResponseTransformer()
        self.transformation_rules: List[TransformationRule] = []
    
    def add_transformation_rule(self, rule: TransformationRule):
        """Add a transformation rule"""
        self.transformation_rules.append(rule)
        # Sort by priority
        self.transformation_rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info(f"Transformation rule added: {rule.name}")
    
    def remove_transformation_rule(self, rule_name: str):
        """Remove a transformation rule"""
        self.transformation_rules = [r for r in self.transformation_rules if r.name != rule_name]
        logger.info(f"Transformation rule removed: {rule_name}")
    
    async def transform_request(self, request: Request, context: Dict[str, Any]) -> Request:
        """Transform an incoming request"""
        # Apply applicable transformation rules
        applicable_rules = [r for r in self.transformation_rules 
                          if r.transformation_type in [TransformationType.REQUEST, TransformationType.BOTH]]
        
        for rule in applicable_rules:
            if self._rule_applies(rule, request, context):
                await self._apply_request_transformation(rule, request, context)
        
        # Apply transformations
        return await self.request_transformer.transform_request(request, context)
    
    async def transform_response(self, response: Response, context: Dict[str, Any]) -> Response:
        """Transform an outgoing response"""
        # Apply applicable transformation rules
        applicable_rules = [r for r in self.transformation_rules 
                          if r.transformation_type in [TransformationType.RESPONSE, TransformationType.BOTH]]
        
        for rule in applicable_rules:
            if self._rule_applies(rule, None, context):
                await self._apply_response_transformation(rule, response, context)
        
        # Apply transformations
        return await self.response_transformer.transform_response(response, context)
    
    def _rule_applies(self, rule: TransformationRule, request: Optional[Request], context: Dict[str, Any]) -> bool:
        """Check if a transformation rule applies"""
        if not rule.enabled:
            return False
        
        conditions = rule.conditions
        
        # Check path condition
        if request and 'path' in conditions:
            path_pattern = conditions['path']
            if not request.url.path.startswith(path_pattern):
                return False
        
        # Check method condition
        if request and 'method' in conditions:
            if request.method not in conditions['method']:
                return False
        
        # Check header conditions
        if request and 'headers' in conditions:
            headers = dict(request.headers)
            for key, value in conditions['headers'].items():
                if headers.get(key) != value:
                    return False
        
        # Check content type condition
        if request and 'content_type' in conditions:
            content_type = request.headers.get('content-type', '')
            if conditions['content_type'] not in content_type:
                return False
        
        return True
    
    async def _apply_request_transformation(self, rule: TransformationRule, request: Request, context: Dict[str, Any]):
        """Apply request transformation rule"""
        # This would contain the specific logic for each rule
        # For now, it's a placeholder for rule-specific transformations
        pass
    
    async def _apply_response_transformation(self, rule: TransformationRule, response: Response, context: Dict[str, Any]):
        """Apply response transformation rule"""
        # This would contain the specific logic for each rule
        # For now, it's a placeholder for rule-specific transformations
        pass
    
    def get_transformation_stats(self) -> Dict[str, Any]:
        """Get transformation statistics"""
        return {
            'total_rules': len(self.transformation_rules),
            'request_transformers': len(self.request_transformer.json_transformers) + 
                                 len(self.request_transformer.xml_transformers) +
                                 len(self.request_transformer.regex_transformers) +
                                 len(self.request_transformer.template_transformers),
            'response_transformers': len(self.response_transformer.json_transformers) + 
                                   len(self.response_transformer.xml_transformers) +
                                   len(self.response_transformer.regex_transformers) +
                                   len(self.response_transformer.template_transformers),
            'rules': [
                {
                    'name': rule.name,
                    'type': rule.transformation_type.value,
                    'data_type': rule.data_type.value,
                    'enabled': rule.enabled,
                    'priority': rule.priority
                }
                for rule in self.transformation_rules
            ]
        }


# Global transformer instance
gateway_transformer = GatewayTransformer()
