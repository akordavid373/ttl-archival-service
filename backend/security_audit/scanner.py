"""
Security Vulnerability Scanner for API Endpoints
Scans for common security vulnerabilities including OWASP Top 10
"""
import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class VulnerabilityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityType(str, Enum):
    SQL_INJECTION = "sql_injection"
    XSS = "cross_site_scripting"
    CSRF = "cross_site_request_forgery"
    BROKEN_AUTH = "broken_authentication"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"
    BROKEN_ACCESS_CONTROL = "broken_access_control"
    SECURITY_MISCONFIGURATION = "security_misconfiguration"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    INSUFFICIENT_LOGGING = "insufficient_logging"
    INJECTION = "injection"
    WEAK_CRYPTO = "weak_cryptography"


class SecurityScanner:
    """Comprehensive security vulnerability scanner for API endpoints"""

    def __init__(self):
        self.vulnerabilities: List[Dict[str, Any]] = []
        self.scan_timestamp = None

    def scan_endpoint(
        self,
        endpoint: str,
        method: str,
        headers: Dict[str, str],
        response_headers: Dict[str, str],
        status_code: int,
        response_body: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Scan a single endpoint for vulnerabilities
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            headers: Request headers
            response_headers: Response headers
            status_code: HTTP status code
            response_body: Response body content
            
        Returns:
            List of detected vulnerabilities
        """
        endpoint_vulnerabilities = []

        # Check security headers
        endpoint_vulnerabilities.extend(
            self._check_security_headers(endpoint, response_headers)
        )

        # Check for sensitive data exposure
        endpoint_vulnerabilities.extend(
            self._check_sensitive_data_exposure(endpoint, response_body)
        )

        # Check for SQL injection patterns
        endpoint_vulnerabilities.extend(
            self._check_sql_injection_patterns(endpoint)
        )

        # Check for XSS vulnerabilities
        endpoint_vulnerabilities.extend(
            self._check_xss_vulnerabilities(endpoint, response_body)
        )

        # Check authentication requirements
        endpoint_vulnerabilities.extend(
            self._check_authentication_requirements(endpoint, headers, status_code)
        )

        # Check CORS configuration
        endpoint_vulnerabilities.extend(
            self._check_cors_configuration(response_headers)
        )

        # Check for information disclosure
        endpoint_vulnerabilities.extend(
            self._check_information_disclosure(endpoint, response_headers, response_body)
        )

        self.vulnerabilities.extend(endpoint_vulnerabilities)
        return endpoint_vulnerabilities

    def _check_security_headers(
        self, endpoint: str, headers: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Check for missing or misconfigured security headers"""
        vulnerabilities = []
        required_headers = {
            "X-Frame-Options": VulnerabilityLevel.MEDIUM,
            "X-Content-Type-Options": VulnerabilityLevel.MEDIUM,
            "Strict-Transport-Security": VulnerabilityLevel.HIGH,
            "Content-Security-Policy": VulnerabilityLevel.MEDIUM,
            "X-XSS-Protection": VulnerabilityLevel.LOW,
        }

        for header, severity in required_headers.items():
            if header.lower() not in [h.lower() for h in headers.keys()]:
                vulnerabilities.append({
                    "endpoint": endpoint,
                    "type": VulnerabilityType.SECURITY_MISCONFIGURATION,
                    "level": severity,
                    "title": f"Missing Security Header: {header}",
                    "description": f"The endpoint does not set the {header} security header",
                    "recommendation": f"Add {header} header to prevent security vulnerabilities",
                    "cwe": "CWE-693",
                    "timestamp": datetime.utcnow().isoformat(),
                })

        return vulnerabilities

    def _check_sensitive_data_exposure(
        self, endpoint: str, response_body: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Check for sensitive data in responses"""
        vulnerabilities = []

        if not response_body:
            return vulnerabilities

        # Patterns for sensitive data
        sensitive_patterns = {
            "password": r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?[\w@#$%^&*]+",
            "api_key": r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?[\w-]+",
            "secret": r"(?i)(secret|token)\s*[:=]\s*['\"]?[\w-]+",
            "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "private_key": r"-----BEGIN (RSA |EC )?PRIVATE KEY-----",
        }

        for data_type, pattern in sensitive_patterns.items():
            if re.search(pattern, response_body):
                vulnerabilities.append({
                    "endpoint": endpoint,
                    "type": VulnerabilityType.SENSITIVE_DATA_EXPOSURE,
                    "level": VulnerabilityLevel.CRITICAL,
                    "title": f"Sensitive Data Exposure: {data_type}",
                    "description": f"Response may contain {data_type} in plain text",
                    "recommendation": "Remove or mask sensitive data from API responses",
                    "cwe": "CWE-200",
                    "timestamp": datetime.utcnow().isoformat(),
                })

        return vulnerabilities

    def _check_sql_injection_patterns(self, endpoint: str) -> List[Dict[str, Any]]:
        """Check endpoint for SQL injection vulnerability patterns"""
        vulnerabilities = []

        # Check if endpoint accepts parameters that could be vulnerable
        sql_vulnerable_patterns = [
            r"/\{[^}]*id[^}]*\}",
            r"/\{[^}]*user[^}]*\}",
            r"/\{[^}]*name[^}]*\}",
        ]

        for pattern in sql_vulnerable_patterns:
            if re.search(pattern, endpoint):
                vulnerabilities.append({
                    "endpoint": endpoint,
                    "type": VulnerabilityType.SQL_INJECTION,
                    "level": VulnerabilityLevel.HIGH,
                    "title": "Potential SQL Injection Vector",
                    "description": "Endpoint accepts parameters that may be vulnerable to SQL injection",
                    "recommendation": "Use parameterized queries and input validation",
                    "cwe": "CWE-89",
                    "timestamp": datetime.utcnow().isoformat(),
                })
                break

        return vulnerabilities

    def _check_xss_vulnerabilities(
        self, endpoint: str, response_body: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Check for XSS vulnerabilities"""
        vulnerabilities = []

        if not response_body:
            return vulnerabilities

        # Check for unescaped user input patterns
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"onerror\s*=",
            r"onload\s*=",
        ]

        for pattern in xss_patterns:
            if re.search(pattern, response_body, re.IGNORECASE):
                vulnerabilities.append({
                    "endpoint": endpoint,
                    "type": VulnerabilityType.XSS,
                    "level": VulnerabilityLevel.HIGH,
                    "title": "Potential Cross-Site Scripting (XSS)",
                    "description": "Response contains potentially dangerous script content",
                    "recommendation": "Sanitize and escape all user input before rendering",
                    "cwe": "CWE-79",
                    "timestamp": datetime.utcnow().isoformat(),
                })
                break

        return vulnerabilities

    def _check_authentication_requirements(
        self, endpoint: str, headers: Dict[str, str], status_code: int
    ) -> List[Dict[str, Any]]:
        """Check if endpoints properly require authentication"""
        vulnerabilities = []

        # Endpoints that should require authentication
        protected_patterns = [
            r"/api/v[12]/archives",
            r"/api/v[12]/policies",
            r"/api/v[12]/settings",
            r"/api/v[12]/audit",
        ]

        # Check if endpoint should be protected
        should_be_protected = any(
            re.search(pattern, endpoint) for pattern in protected_patterns
        )

        if should_be_protected:
            # Check for authentication headers
            auth_headers = ["authorization", "x-api-key", "x-auth-token"]
            has_auth = any(h.lower() in [k.lower() for k in headers.keys()] for h in auth_headers)

            if not has_auth and status_code != 401:
                vulnerabilities.append({
                    "endpoint": endpoint,
                    "type": VulnerabilityType.BROKEN_AUTH,
                    "level": VulnerabilityLevel.CRITICAL,
                    "title": "Missing Authentication",
                    "description": "Protected endpoint accessible without authentication",
                    "recommendation": "Implement proper authentication checks",
                    "cwe": "CWE-306",
                    "timestamp": datetime.utcnow().isoformat(),
                })

        return vulnerabilities

    def _check_cors_configuration(
        self, headers: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Check CORS configuration for security issues"""
        vulnerabilities = []

        cors_header = None
        for key, value in headers.items():
            if key.lower() == "access-control-allow-origin":
                cors_header = value
                break

        if cors_header == "*":
            vulnerabilities.append({
                "endpoint": "global",
                "type": VulnerabilityType.SECURITY_MISCONFIGURATION,
                "level": VulnerabilityLevel.MEDIUM,
                "title": "Overly Permissive CORS Policy",
                "description": "CORS policy allows requests from any origin (*)",
                "recommendation": "Restrict CORS to specific trusted origins",
                "cwe": "CWE-942",
                "timestamp": datetime.utcnow().isoformat(),
            })

        return vulnerabilities

    def _check_information_disclosure(
        self, endpoint: str, headers: Dict[str, str], response_body: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Check for information disclosure vulnerabilities"""
        vulnerabilities = []

        # Check for verbose error messages
        if response_body:
            error_patterns = [
                r"Traceback \(most recent call last\)",
                r"Exception in thread",
                r"at line \d+",
                r"File \"[^\"]+\", line \d+",
                r"sqlalchemy\.",
                r"psycopg2\.",
            ]

            for pattern in error_patterns:
                if re.search(pattern, response_body):
                    vulnerabilities.append({
                        "endpoint": endpoint,
                        "type": VulnerabilityType.INSUFFICIENT_LOGGING,
                        "level": VulnerabilityLevel.MEDIUM,
                        "title": "Information Disclosure via Error Messages",
                        "description": "Detailed error messages expose internal system information",
                        "recommendation": "Use generic error messages for production",
                        "cwe": "CWE-209",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                    break

        # Check for server version disclosure
        server_header = headers.get("server", "")
        if server_header and any(
            tech in server_header.lower() for tech in ["apache", "nginx", "uvicorn", "python"]
        ):
            vulnerabilities.append({
                "endpoint": "global",
                "type": VulnerabilityType.SECURITY_MISCONFIGURATION,
                "level": VulnerabilityLevel.LOW,
                "title": "Server Version Disclosure",
                "description": f"Server header reveals technology: {server_header}",
                "recommendation": "Remove or obfuscate server version information",
                "cwe": "CWE-200",
                "timestamp": datetime.utcnow().isoformat(),
            })

        return vulnerabilities

    def get_scan_summary(self) -> Dict[str, Any]:
        """Get summary of all detected vulnerabilities"""
        summary = {
            "total_vulnerabilities": len(self.vulnerabilities),
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            },
            "by_type": {},
            "scan_timestamp": self.scan_timestamp or datetime.utcnow().isoformat(),
        }

        for vuln in self.vulnerabilities:
            # Count by severity
            severity = vuln.get("level", VulnerabilityLevel.INFO)
            summary["by_severity"][severity] += 1

            # Count by type
            vuln_type = vuln.get("type", "unknown")
            summary["by_type"][vuln_type] = summary["by_type"].get(vuln_type, 0) + 1

        return summary

    def clear_results(self):
        """Clear all scan results"""
        self.vulnerabilities = []
        self.scan_timestamp = None
