"""
Input Validation Testing Module
Tests input validation mechanisms for security vulnerabilities
"""
import re
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationTestResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"


class InputType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    DATE = "date"
    JSON = "json"
    FILE = "file"
    CUSTOM = "custom"


class InputValidationTester:
    """Test input validation mechanisms for security vulnerabilities"""

    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.validation_patterns = {
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "url": r"^https?://[^\s/$.?#].[^\s]*$",
            "phone": r"^\+?1?\d{9,15}$",
            "date": r"^\d{4}-\d{2}-\d{2}$",
            "ipv4": r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
            "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        }

    def test_sql_injection_prevention(
        self,
        endpoint: str,
        parameter_name: str,
        malicious_inputs: List[str],
        responses: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Test SQL injection prevention
        
        Args:
            endpoint: API endpoint path
            parameter_name: Name of the parameter being tested
            malicious_inputs: List of SQL injection payloads
            responses: List of response data for each payload
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "sql_injection_prevention",
            "endpoint": endpoint,
            "parameter": parameter_name,
            "timestamp": datetime.utcnow().isoformat(),
            "payloads_tested": len(malicious_inputs),
            "checks": [],
        }

        sql_injection_patterns = [
            r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)",
            r"(--|#|/\*|\*/)",
            r"(\bOR\b.*=.*)",
            r"(;\s*DROP)",
        ]

        vulnerable_payloads = []

        for i, payload in enumerate(malicious_inputs):
            response = responses[i] if i < len(responses) else {}
            status_code = response.get("status_code", 200)
            response_body = response.get("body", "")

            # Check if payload was executed
            payload_executed = False
            for pattern in sql_injection_patterns:
                if re.search(pattern, response_body, re.IGNORECASE):
                    payload_executed = True
                    break

            if status_code == 400 or status_code == 422:
                result["checks"].append({
                    "payload": payload[:50],
                    "result": ValidationTestResult.PASS,
                    "message": "Malicious input rejected",
                })
            elif payload_executed:
                vulnerable_payloads.append(payload)
                result["checks"].append({
                    "payload": payload[:50],
                    "result": ValidationTestResult.FAIL,
                    "message": "SQL injection payload executed",
                    "severity": "critical",
                })
            else:
                result["checks"].append({
                    "payload": payload[:50],
                    "result": ValidationTestResult.PASS,
                    "message": "Malicious input safely handled",
                })

        if vulnerable_payloads:
            result["result"] = ValidationTestResult.FAIL
            result["severity"] = "critical"
            result["message"] = f"SQL injection vulnerability detected with {len(vulnerable_payloads)} payloads"
            result["recommendation"] = "Use parameterized queries and prepared statements"
        else:
            result["result"] = ValidationTestResult.PASS
            result["message"] = "SQL injection prevention working correctly"

        self.test_results.append(result)
        return result

    def test_xss_prevention(
        self,
        endpoint: str,
        parameter_name: str,
        xss_payloads: List[str],
        responses: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Test XSS prevention
        
        Args:
            endpoint: API endpoint path
            parameter_name: Name of the parameter being tested
            xss_payloads: List of XSS payloads
            responses: List of response data for each payload
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "xss_prevention",
            "endpoint": endpoint,
            "parameter": parameter_name,
            "timestamp": datetime.utcnow().isoformat(),
            "payloads_tested": len(xss_payloads),
            "checks": [],
        }

        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
        ]

        vulnerable_payloads = []

        for i, payload in enumerate(xss_payloads):
            response = responses[i] if i < len(responses) else {}
            status_code = response.get("status_code", 200)
            response_body = response.get("body", "")

            # Check if payload was reflected unescaped
            payload_reflected = False
            for pattern in xss_patterns:
                if re.search(pattern, response_body, re.IGNORECASE):
                    payload_reflected = True
                    break

            if status_code == 400 or status_code == 422:
                result["checks"].append({
                    "payload": payload[:50],
                    "result": ValidationTestResult.PASS,
                    "message": "XSS payload rejected",
                })
            elif payload_reflected:
                vulnerable_payloads.append(payload)
                result["checks"].append({
                    "payload": payload[:50],
                    "result": ValidationTestResult.FAIL,
                    "message": "XSS payload reflected in response",
                    "severity": "high",
                })
            else:
                result["checks"].append({
                    "payload": payload[:50],
                    "result": ValidationTestResult.PASS,
                    "message": "XSS payload safely handled",
                })

        if vulnerable_payloads:
            result["result"] = ValidationTestResult.FAIL
            result["severity"] = "high"
            result["message"] = f"XSS vulnerability detected with {len(vulnerable_payloads)} payloads"
            result["recommendation"] = "Sanitize and escape all user input before rendering"
        else:
            result["result"] = ValidationTestResult.PASS
            result["message"] = "XSS prevention working correctly"

        self.test_results.append(result)
        return result

    def test_command_injection_prevention(
        self,
        endpoint: str,
        parameter_name: str,
        command_payloads: List[str],
        responses: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Test command injection prevention
        
        Args:
            endpoint: API endpoint path
            parameter_name: Name of the parameter being tested
            command_payloads: List of command injection payloads
            responses: List of response data for each payload
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "command_injection_prevention",
            "endpoint": endpoint,
            "parameter": parameter_name,
            "timestamp": datetime.utcnow().isoformat(),
            "payloads_tested": len(command_payloads),
            "checks": [],
        }

        command_patterns = [
            r"(;|&&|\||`|\$\()",
            r"(cat|ls|rm|wget|curl|nc|bash|sh)",
        ]

        vulnerable_payloads = []

        for i, payload in enumerate(command_payloads):
            response = responses[i] if i < len(responses) else {}
            status_code = response.get("status_code", 200)
            response_body = response.get("body", "")

            # Check if command was executed
            command_executed = False
            for pattern in command_patterns:
                if re.search(pattern, response_body, re.IGNORECASE):
                    command_executed = True
                    break

            if status_code == 400 or status_code == 422:
                result["checks"].append({
                    "payload": payload[:50],
                    "result": ValidationTestResult.PASS,
                    "message": "Command injection payload rejected",
                })
            elif command_executed:
                vulnerable_payloads.append(payload)
                result["checks"].append({
                    "payload": payload[:50],
                    "result": ValidationTestResult.FAIL,
                    "message": "Command injection payload executed",
                    "severity": "critical",
                })
            else:
                result["checks"].append({
                    "payload": payload[:50],
                    "result": ValidationTestResult.PASS,
                    "message": "Command injection payload safely handled",
                })

        if vulnerable_payloads:
            result["result"] = ValidationTestResult.FAIL
            result["severity"] = "critical"
            result["message"] = f"Command injection vulnerability detected with {len(vulnerable_payloads)} payloads"
            result["recommendation"] = "Avoid executing system commands with user input; use safe APIs"
        else:
            result["result"] = ValidationTestResult.PASS
            result["message"] = "Command injection prevention working correctly"

        self.test_results.append(result)
        return result

    def test_path_traversal_prevention(
        self,
        endpoint: str,
        parameter_name: str,
        traversal_payloads: List[str],
        responses: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Test path traversal prevention
        
        Args:
            endpoint: API endpoint path
            parameter_name: Name of the parameter being tested
            traversal_payloads: List of path traversal payloads
            responses: List of response data for each payload
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "path_traversal_prevention",
            "endpoint": endpoint,
            "parameter": parameter_name,
            "timestamp": datetime.utcnow().isoformat(),
            "payloads_tested": len(traversal_payloads),
            "checks": [],
        }

        traversal_patterns = [
            r"\.\./",
            r"\.\.",
            r"%2e%2e",
            r"\.\.\\",
        ]

        vulnerable_payloads = []

        for i, payload in enumerate(traversal_payloads):
            response = responses[i] if i < len(responses) else {}
            status_code = response.get("status_code", 200)
            response_body = response.get("body", "")

            # Check if traversal was successful
            traversal_successful = False
            if status_code == 200 and response_body:
                traversal_successful = True

            if status_code == 400 or status_code == 403 or status_code == 404:
                result["checks"].append({
                    "payload": payload[:50],
                    "result": ValidationTestResult.PASS,
                    "message": "Path traversal payload rejected",
                })
            elif traversal_successful:
                vulnerable_payloads.append(payload)
                result["checks"].append({
                    "payload": payload[:50],
                    "result": ValidationTestResult.FAIL,
                    "message": "Path traversal vulnerability detected",
                    "severity": "high",
                })
            else:
                result["checks"].append({
                    "payload": payload[:50],
                    "result": ValidationTestResult.PASS,
                    "message": "Path traversal payload safely handled",
                })

        if vulnerable_payloads:
            result["result"] = ValidationTestResult.FAIL
            result["severity"] = "high"
            result["message"] = f"Path traversal vulnerability detected with {len(vulnerable_payloads)} payloads"
            result["recommendation"] = "Validate and sanitize file paths; use allowlists"
        else:
            result["result"] = ValidationTestResult.PASS
            result["message"] = "Path traversal prevention working correctly"

        self.test_results.append(result)
        return result

    def test_input_type_validation(
        self,
        endpoint: str,
        parameter_name: str,
        expected_type: InputType,
        test_inputs: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Test input type validation
        
        Args:
            endpoint: API endpoint path
            parameter_name: Name of the parameter being tested
            expected_type: Expected input type
            test_inputs: List of test inputs with expected results
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "input_type_validation",
            "endpoint": endpoint,
            "parameter": parameter_name,
            "expected_type": expected_type,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": [],
        }

        passed = 0
        failed = 0

        for test_input in test_inputs:
            value = test_input.get("value")
            should_pass = test_input.get("should_pass", True)
            status_code = test_input.get("status_code", 200)

            is_valid = self._validate_input_type(value, expected_type)

            if should_pass:
                if status_code < 400:
                    result["checks"].append({
                        "value": str(value)[:50],
                        "result": ValidationTestResult.PASS,
                        "message": f"Valid {expected_type} input accepted",
                    })
                    passed += 1
                else:
                    result["checks"].append({
                        "value": str(value)[:50],
                        "result": ValidationTestResult.FAIL,
                        "message": f"Valid {expected_type} input rejected",
                    })
                    failed += 1
            else:
                if status_code >= 400:
                    result["checks"].append({
                        "value": str(value)[:50],
                        "result": ValidationTestResult.PASS,
                        "message": f"Invalid {expected_type} input rejected",
                    })
                    passed += 1
                else:
                    result["checks"].append({
                        "value": str(value)[:50],
                        "result": ValidationTestResult.FAIL,
                        "message": f"Invalid {expected_type} input accepted",
                    })
                    failed += 1

        if failed > 0:
            result["result"] = ValidationTestResult.FAIL
            result["severity"] = "medium"
            result["message"] = f"Input type validation failed for {failed} test cases"
            result["recommendation"] = f"Implement strict type validation for {expected_type}"
        else:
            result["result"] = ValidationTestResult.PASS
            result["message"] = f"Input type validation working correctly for {expected_type}"

        result["passed"] = passed
        result["failed"] = failed

        self.test_results.append(result)
        return result

    def test_input_length_validation(
        self,
        endpoint: str,
        parameter_name: str,
        max_length: int,
        test_inputs: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Test input length validation
        
        Args:
            endpoint: API endpoint path
            parameter_name: Name of the parameter being tested
            max_length: Maximum allowed input length
            test_inputs: List of test inputs with expected results
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "input_length_validation",
            "endpoint": endpoint,
            "parameter": parameter_name,
            "max_length": max_length,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": [],
        }

        passed = 0
        failed = 0

        for test_input in test_inputs:
            value = test_input.get("value", "")
            should_pass = test_input.get("should_pass", True)
            status_code = test_input.get("status_code", 200)

            input_length = len(str(value))
            is_within_limit = input_length <= max_length

            if should_pass:
                if status_code < 400:
                    result["checks"].append({
                        "length": input_length,
                        "result": ValidationTestResult.PASS,
                        "message": f"Input within limit ({input_length}/{max_length}) accepted",
                    })
                    passed += 1
                else:
                    result["checks"].append({
                        "length": input_length,
                        "result": ValidationTestResult.FAIL,
                        "message": f"Input within limit rejected",
                    })
                    failed += 1
            else:
                if status_code >= 400:
                    result["checks"].append({
                        "length": input_length,
                        "result": ValidationTestResult.PASS,
                        "message": f"Input exceeding limit ({input_length}/{max_length}) rejected",
                    })
                    passed += 1
                else:
                    result["checks"].append({
                        "length": input_length,
                        "result": ValidationTestResult.FAIL,
                        "message": f"Input exceeding limit accepted",
                    })
                    failed += 1

        if failed > 0:
            result["result"] = ValidationTestResult.FAIL
            result["severity"] = "medium"
            result["message"] = f"Input length validation failed for {failed} test cases"
            result["recommendation"] = f"Enforce maximum length of {max_length} characters"
        else:
            result["result"] = ValidationTestResult.PASS
            result["message"] = f"Input length validation working correctly"

        result["passed"] = passed
        result["failed"] = failed

        self.test_results.append(result)
        return result

    def test_input_format_validation(
        self,
        endpoint: str,
        parameter_name: str,
        format_type: str,
        test_inputs: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Test input format validation (email, URL, phone, etc.)
        
        Args:
            endpoint: API endpoint path
            parameter_name: Name of the parameter being tested
            format_type: Type of format to validate (email, url, phone, date, etc.)
            test_inputs: List of test inputs with expected results
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "input_format_validation",
            "endpoint": endpoint,
            "parameter": parameter_name,
            "format_type": format_type,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": [],
        }

        pattern = self.validation_patterns.get(format_type)
        if not pattern:
            result["result"] = ValidationTestResult.SKIP
            result["message"] = f"Unknown format type: {format_type}"
            self.test_results.append(result)
            return result

        passed = 0
        failed = 0

        for test_input in test_inputs:
            value = test_input.get("value", "")
            should_pass = test_input.get("should_pass", True)
            status_code = test_input.get("status_code", 200)

            is_valid = bool(re.match(pattern, str(value)))

            if should_pass:
                if status_code < 400:
                    result["checks"].append({
                        "value": str(value)[:50],
                        "result": ValidationTestResult.PASS,
                        "message": f"Valid {format_type} format accepted",
                    })
                    passed += 1
                else:
                    result["checks"].append({
                        "value": str(value)[:50],
                        "result": ValidationTestResult.FAIL,
                        "message": f"Valid {format_type} format rejected",
                    })
                    failed += 1
            else:
                if status_code >= 400:
                    result["checks"].append({
                        "value": str(value)[:50],
                        "result": ValidationTestResult.PASS,
                        "message": f"Invalid {format_type} format rejected",
                    })
                    passed += 1
                else:
                    result["checks"].append({
                        "value": str(value)[:50],
                        "result": ValidationTestResult.FAIL,
                        "message": f"Invalid {format_type} format accepted",
                    })
                    failed += 1

        if failed > 0:
            result["result"] = ValidationTestResult.FAIL
            result["severity"] = "medium"
            result["message"] = f"Input format validation failed for {failed} test cases"
            result["recommendation"] = f"Implement strict format validation for {format_type}"
        else:
            result["result"] = ValidationTestResult.PASS
            result["message"] = f"Input format validation working correctly for {format_type}"

        result["passed"] = passed
        result["failed"] = failed

        self.test_results.append(result)
        return result

    def test_file_upload_validation(
        self,
        endpoint: str,
        allowed_extensions: List[str],
        max_file_size: int,
        test_files: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Test file upload validation
        
        Args:
            endpoint: API endpoint path
            allowed_extensions: List of allowed file extensions
            max_file_size: Maximum allowed file size in bytes
            test_files: List of test files with expected results
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "file_upload_validation",
            "endpoint": endpoint,
            "allowed_extensions": allowed_extensions,
            "max_file_size": max_file_size,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": [],
        }

        passed = 0
        failed = 0

        for test_file in test_files:
            filename = test_file.get("filename", "")
            file_size = test_file.get("size", 0)
            should_pass = test_file.get("should_pass", True)
            status_code = test_file.get("status_code", 200)

            # Check extension
            file_ext = filename.split(".")[-1].lower() if "." in filename else ""
            ext_allowed = file_ext in allowed_extensions
            size_allowed = file_size <= max_file_size

            is_valid = ext_allowed and size_allowed

            if should_pass:
                if status_code < 400:
                    result["checks"].append({
                        "filename": filename,
                        "size": file_size,
                        "result": ValidationTestResult.PASS,
                        "message": "Valid file upload accepted",
                    })
                    passed += 1
                else:
                    result["checks"].append({
                        "filename": filename,
                        "size": file_size,
                        "result": ValidationTestResult.FAIL,
                        "message": "Valid file upload rejected",
                    })
                    failed += 1
            else:
                if status_code >= 400:
                    result["checks"].append({
                        "filename": filename,
                        "size": file_size,
                        "result": ValidationTestResult.PASS,
                        "message": "Invalid file upload rejected",
                    })
                    passed += 1
                else:
                    result["checks"].append({
                        "filename": filename,
                        "size": file_size,
                        "result": ValidationTestResult.FAIL,
                        "message": "Invalid file upload accepted",
                    })
                    failed += 1

        if failed > 0:
            result["result"] = ValidationTestResult.FAIL
            result["severity"] = "high"
            result["message"] = f"File upload validation failed for {failed} test cases"
            result["recommendation"] = "Implement strict file type and size validation"
        else:
            result["result"] = ValidationTestResult.PASS
            result["message"] = "File upload validation working correctly"

        result["passed"] = passed
        result["failed"] = failed

        self.test_results.append(result)
        return result

    def _validate_input_type(self, value: Any, input_type: InputType) -> bool:
        """Validate input against expected type"""
        try:
            if input_type == InputType.STRING:
                return isinstance(value, str)
            elif input_type == InputType.INTEGER:
                return isinstance(value, int) or (isinstance(value, str) and value.isdigit())
            elif input_type == InputType.EMAIL:
                return bool(re.match(self.validation_patterns["email"], str(value)))
            elif input_type == InputType.URL:
                return bool(re.match(self.validation_patterns["url"], str(value)))
            elif input_type == InputType.PHONE:
                return bool(re.match(self.validation_patterns["phone"], str(value)))
            elif input_type == InputType.DATE:
                return bool(re.match(self.validation_patterns["date"], str(value)))
            elif input_type == InputType.JSON:
                import json
                json.loads(str(value))
                return True
            else:
                return False
        except Exception:
            return False

    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of all input validation tests"""
        summary = {
            "total_tests": len(self.test_results),
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "skipped": 0,
            "critical_issues": [],
            "high_issues": [],
        }

        for test in self.test_results:
            result = test.get("result", ValidationTestResult.SKIP)
            
            if result == ValidationTestResult.PASS:
                summary["passed"] += 1
            elif result == ValidationTestResult.FAIL:
                summary["failed"] += 1
                severity = test.get("severity", "medium")
                if severity == "critical":
                    summary["critical_issues"].append(test)
                elif severity == "high":
                    summary["high_issues"].append(test)
            elif result == ValidationTestResult.WARNING:
                summary["warnings"] += 1
            else:
                summary["skipped"] += 1

        return summary

    def clear_results(self):
        """Clear all test results"""
        self.test_results = []
