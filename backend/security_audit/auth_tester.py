"""
Authentication Testing Module
Tests authentication mechanisms for security vulnerabilities
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AuthTestResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"


class AuthenticationTester:
    """Test authentication mechanisms for security vulnerabilities"""

    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []

    def test_endpoint_authentication(
        self,
        endpoint: str,
        method: str,
        requires_auth: bool = True,
        auth_header: Optional[str] = None,
        status_code: int = 200,
    ) -> Dict[str, Any]:
        """
        Test authentication requirements for an endpoint
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            requires_auth: Whether endpoint should require authentication
            auth_header: Authentication header value
            status_code: Response status code
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "endpoint_authentication",
            "endpoint": endpoint,
            "method": method,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if requires_auth:
            if not auth_header:
                if status_code == 401 or status_code == 403:
                    result["result"] = AuthTestResult.PASS
                    result["message"] = "Endpoint correctly rejects unauthenticated requests"
                else:
                    result["result"] = AuthTestResult.FAIL
                    result["message"] = "Endpoint accessible without authentication"
                    result["severity"] = "critical"
                    result["recommendation"] = "Implement authentication middleware"
            else:
                if status_code < 400:
                    result["result"] = AuthTestResult.PASS
                    result["message"] = "Endpoint accepts valid authentication"
                else:
                    result["result"] = AuthTestResult.WARNING
                    result["message"] = "Endpoint rejects provided authentication"
        else:
            result["result"] = AuthTestResult.SKIP
            result["message"] = "Endpoint does not require authentication"

        self.test_results.append(result)
        return result

    def test_token_validation(
        self,
        endpoint: str,
        valid_token: Optional[str],
        invalid_tokens: List[str],
        status_codes: Dict[str, int],
    ) -> List[Dict[str, Any]]:
        """
        Test token validation mechanisms
        
        Args:
            endpoint: API endpoint path
            valid_token: Valid authentication token
            invalid_tokens: List of invalid tokens to test
            status_codes: Dictionary mapping token to status code
            
        Returns:
            List of test results
        """
        results = []

        # Test valid token
        if valid_token:
            valid_status = status_codes.get("valid", 200)
            result = {
                "test": "valid_token",
                "endpoint": endpoint,
                "timestamp": datetime.utcnow().isoformat(),
            }

            if valid_status < 400:
                result["result"] = AuthTestResult.PASS
                result["message"] = "Valid token accepted"
            else:
                result["result"] = AuthTestResult.FAIL
                result["message"] = "Valid token rejected"
                result["severity"] = "high"

            results.append(result)
            self.test_results.append(result)

        # Test invalid tokens
        for token_type in invalid_tokens:
            invalid_status = status_codes.get(token_type, 200)
            result = {
                "test": f"invalid_token_{token_type}",
                "endpoint": endpoint,
                "timestamp": datetime.utcnow().isoformat(),
            }

            if invalid_status == 401 or invalid_status == 403:
                result["result"] = AuthTestResult.PASS
                result["message"] = f"Invalid token ({token_type}) correctly rejected"
            else:
                result["result"] = AuthTestResult.FAIL
                result["message"] = f"Invalid token ({token_type}) accepted"
                result["severity"] = "critical"
                result["recommendation"] = "Implement proper token validation"

            results.append(result)
            self.test_results.append(result)

        return results

    def test_session_management(
        self,
        session_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Test session management security
        
        Args:
            session_data: Session configuration and behavior data
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "session_management",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": [],
        }

        # Check session timeout
        timeout = session_data.get("timeout_minutes", 0)
        if timeout > 0 and timeout <= 30:
            result["checks"].append({
                "check": "session_timeout",
                "result": AuthTestResult.PASS,
                "message": f"Session timeout configured: {timeout} minutes",
            })
        elif timeout > 30:
            result["checks"].append({
                "check": "session_timeout",
                "result": AuthTestResult.WARNING,
                "message": f"Session timeout too long: {timeout} minutes",
                "recommendation": "Consider reducing session timeout to 30 minutes or less",
            })
        else:
            result["checks"].append({
                "check": "session_timeout",
                "result": AuthTestResult.FAIL,
                "message": "No session timeout configured",
                "severity": "high",
                "recommendation": "Implement session timeout mechanism",
            })

        # Check secure cookie flags
        secure_flag = session_data.get("secure_flag", False)
        if secure_flag:
            result["checks"].append({
                "check": "secure_cookie_flag",
                "result": AuthTestResult.PASS,
                "message": "Secure flag set on session cookies",
            })
        else:
            result["checks"].append({
                "check": "secure_cookie_flag",
                "result": AuthTestResult.FAIL,
                "message": "Secure flag not set on session cookies",
                "severity": "high",
                "recommendation": "Set Secure flag on all session cookies",
            })

        # Check HttpOnly flag
        httponly_flag = session_data.get("httponly_flag", False)
        if httponly_flag:
            result["checks"].append({
                "check": "httponly_flag",
                "result": AuthTestResult.PASS,
                "message": "HttpOnly flag set on session cookies",
            })
        else:
            result["checks"].append({
                "check": "httponly_flag",
                "result": AuthTestResult.FAIL,
                "message": "HttpOnly flag not set on session cookies",
                "severity": "medium",
                "recommendation": "Set HttpOnly flag to prevent XSS attacks",
            })

        # Check SameSite attribute
        samesite = session_data.get("samesite", None)
        if samesite in ["Strict", "Lax"]:
            result["checks"].append({
                "check": "samesite_attribute",
                "result": AuthTestResult.PASS,
                "message": f"SameSite attribute set: {samesite}",
            })
        else:
            result["checks"].append({
                "check": "samesite_attribute",
                "result": AuthTestResult.WARNING,
                "message": "SameSite attribute not properly configured",
                "recommendation": "Set SameSite=Strict or SameSite=Lax",
            })

        # Determine overall result
        failed_checks = [c for c in result["checks"] if c["result"] == AuthTestResult.FAIL]
        if failed_checks:
            result["result"] = AuthTestResult.FAIL
            result["severity"] = "high"
        else:
            warning_checks = [c for c in result["checks"] if c["result"] == AuthTestResult.WARNING]
            if warning_checks:
                result["result"] = AuthTestResult.WARNING
            else:
                result["result"] = AuthTestResult.PASS

        self.test_results.append(result)
        return result

    def test_password_policy(
        self,
        policy: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Test password policy strength
        
        Args:
            policy: Password policy configuration
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "password_policy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": [],
        }

        # Check minimum length
        min_length = policy.get("min_length", 0)
        if min_length >= 12:
            result["checks"].append({
                "check": "min_length",
                "result": AuthTestResult.PASS,
                "message": f"Minimum password length: {min_length}",
            })
        elif min_length >= 8:
            result["checks"].append({
                "check": "min_length",
                "result": AuthTestResult.WARNING,
                "message": f"Minimum password length: {min_length} (recommended: 12+)",
            })
        else:
            result["checks"].append({
                "check": "min_length",
                "result": AuthTestResult.FAIL,
                "message": f"Weak minimum password length: {min_length}",
                "severity": "high",
                "recommendation": "Set minimum password length to at least 12 characters",
            })

        # Check complexity requirements
        requires_uppercase = policy.get("requires_uppercase", False)
        requires_lowercase = policy.get("requires_lowercase", False)
        requires_numbers = policy.get("requires_numbers", False)
        requires_special = policy.get("requires_special", False)

        complexity_score = sum([
            requires_uppercase,
            requires_lowercase,
            requires_numbers,
            requires_special,
        ])

        if complexity_score >= 3:
            result["checks"].append({
                "check": "complexity",
                "result": AuthTestResult.PASS,
                "message": "Strong password complexity requirements",
            })
        elif complexity_score >= 2:
            result["checks"].append({
                "check": "complexity",
                "result": AuthTestResult.WARNING,
                "message": "Moderate password complexity requirements",
                "recommendation": "Require at least 3 character types",
            })
        else:
            result["checks"].append({
                "check": "complexity",
                "result": AuthTestResult.FAIL,
                "message": "Weak password complexity requirements",
                "severity": "medium",
                "recommendation": "Require uppercase, lowercase, numbers, and special characters",
            })

        # Check password history
        history_count = policy.get("history_count", 0)
        if history_count >= 5:
            result["checks"].append({
                "check": "password_history",
                "result": AuthTestResult.PASS,
                "message": f"Password history enabled: {history_count} passwords",
            })
        else:
            result["checks"].append({
                "check": "password_history",
                "result": AuthTestResult.WARNING,
                "message": "Password history not configured",
                "recommendation": "Prevent reuse of last 5 passwords",
            })

        # Determine overall result
        failed_checks = [c for c in result["checks"] if c["result"] == AuthTestResult.FAIL]
        if failed_checks:
            result["result"] = AuthTestResult.FAIL
            result["severity"] = "medium"
        else:
            warning_checks = [c for c in result["checks"] if c["result"] == AuthTestResult.WARNING]
            if warning_checks:
                result["result"] = AuthTestResult.WARNING
            else:
                result["result"] = AuthTestResult.PASS

        self.test_results.append(result)
        return result

    def test_brute_force_protection(
        self,
        endpoint: str,
        failed_attempts: int,
        lockout_triggered: bool,
        lockout_duration: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Test brute force protection mechanisms
        
        Args:
            endpoint: Login endpoint
            failed_attempts: Number of failed login attempts
            lockout_triggered: Whether account lockout was triggered
            lockout_duration: Lockout duration in minutes
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "brute_force_protection",
            "endpoint": endpoint,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if failed_attempts >= 5 and lockout_triggered:
            result["result"] = AuthTestResult.PASS
            result["message"] = f"Account lockout triggered after {failed_attempts} attempts"
            if lockout_duration:
                result["lockout_duration"] = lockout_duration
        elif failed_attempts >= 10 and not lockout_triggered:
            result["result"] = AuthTestResult.FAIL
            result["message"] = "No brute force protection detected"
            result["severity"] = "critical"
            result["recommendation"] = "Implement account lockout after 5 failed attempts"
        else:
            result["result"] = AuthTestResult.WARNING
            result["message"] = "Brute force protection may be insufficient"
            result["recommendation"] = "Implement rate limiting and account lockout"

        self.test_results.append(result)
        return result

    def test_multi_factor_authentication(
        self,
        mfa_enabled: bool,
        mfa_methods: List[str],
    ) -> Dict[str, Any]:
        """
        Test multi-factor authentication implementation
        
        Args:
            mfa_enabled: Whether MFA is enabled
            mfa_methods: List of available MFA methods
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "multi_factor_authentication",
            "timestamp": datetime.utcnow().isoformat(),
        }

        if mfa_enabled and mfa_methods:
            result["result"] = AuthTestResult.PASS
            result["message"] = f"MFA enabled with methods: {', '.join(mfa_methods)}"
            result["methods"] = mfa_methods
        elif mfa_enabled and not mfa_methods:
            result["result"] = AuthTestResult.WARNING
            result["message"] = "MFA enabled but no methods configured"
        else:
            result["result"] = AuthTestResult.WARNING
            result["message"] = "MFA not implemented"
            result["recommendation"] = "Consider implementing multi-factor authentication"

        self.test_results.append(result)
        return result

    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of all authentication tests"""
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
            result = test.get("result", AuthTestResult.SKIP)
            
            if result == AuthTestResult.PASS:
                summary["passed"] += 1
            elif result == AuthTestResult.FAIL:
                summary["failed"] += 1
                severity = test.get("severity", "medium")
                if severity == "critical":
                    summary["critical_issues"].append(test)
                elif severity == "high":
                    summary["high_issues"].append(test)
            elif result == AuthTestResult.WARNING:
                summary["warnings"] += 1
            else:
                summary["skipped"] += 1

        return summary

    def clear_results(self):
        """Clear all test results"""
        self.test_results = []
