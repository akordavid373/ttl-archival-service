"""
Authorization Testing Module
Tests authorization mechanisms and access control for security vulnerabilities
"""
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AuthzTestResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"


class AccessLevel(str, Enum):
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class AuthorizationTester:
    """Test authorization mechanisms and access control"""

    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []

    def test_role_based_access(
        self,
        endpoint: str,
        method: str,
        required_role: str,
        user_role: str,
        status_code: int,
    ) -> Dict[str, Any]:
        """
        Test role-based access control (RBAC)
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            required_role: Role required to access endpoint
            user_role: Role of the requesting user
            status_code: Response status code
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "role_based_access",
            "endpoint": endpoint,
            "method": method,
            "required_role": required_role,
            "user_role": user_role,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Define role hierarchy
        role_hierarchy = {
            AccessLevel.PUBLIC: 0,
            AccessLevel.AUTHENTICATED: 1,
            AccessLevel.USER: 2,
            AccessLevel.ADMIN: 3,
            AccessLevel.SUPER_ADMIN: 4,
        }

        required_level = role_hierarchy.get(required_role, 0)
        user_level = role_hierarchy.get(user_role, 0)

        if user_level >= required_level:
            # User should have access
            if status_code < 400:
                result["result"] = AuthzTestResult.PASS
                result["message"] = f"User with role '{user_role}' correctly granted access"
            else:
                result["result"] = AuthzTestResult.FAIL
                result["message"] = f"User with sufficient role '{user_role}' denied access"
                result["severity"] = "high"
                result["recommendation"] = "Review role-based access control logic"
        else:
            # User should not have access
            if status_code == 403 or status_code == 401:
                result["result"] = AuthzTestResult.PASS
                result["message"] = f"User with insufficient role '{user_role}' correctly denied access"
            else:
                result["result"] = AuthzTestResult.FAIL
                result["message"] = f"User with insufficient role '{user_role}' granted access"
                result["severity"] = "critical"
                result["recommendation"] = "Implement proper role-based access control"

        self.test_results.append(result)
        return result

    def test_resource_ownership(
        self,
        endpoint: str,
        method: str,
        resource_owner_id: str,
        requesting_user_id: str,
        status_code: int,
        is_admin: bool = False,
    ) -> Dict[str, Any]:
        """
        Test resource ownership authorization
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            resource_owner_id: ID of the resource owner
            requesting_user_id: ID of the requesting user
            status_code: Response status code
            is_admin: Whether requesting user is an admin
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "resource_ownership",
            "endpoint": endpoint,
            "method": method,
            "resource_owner": resource_owner_id,
            "requesting_user": requesting_user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        is_owner = resource_owner_id == requesting_user_id
        should_have_access = is_owner or is_admin

        if should_have_access:
            if status_code < 400:
                result["result"] = AuthzTestResult.PASS
                result["message"] = "Resource owner/admin correctly granted access"
            else:
                result["result"] = AuthzTestResult.FAIL
                result["message"] = "Resource owner/admin denied access"
                result["severity"] = "high"
                result["recommendation"] = "Review resource ownership checks"
        else:
            if status_code == 403:
                result["result"] = AuthzTestResult.PASS
                result["message"] = "Non-owner correctly denied access"
            else:
                result["result"] = AuthzTestResult.FAIL
                result["message"] = "Non-owner granted access to resource"
                result["severity"] = "critical"
                result["recommendation"] = "Implement resource ownership validation"

        self.test_results.append(result)
        return result

    def test_permission_based_access(
        self,
        endpoint: str,
        method: str,
        required_permissions: Set[str],
        user_permissions: Set[str],
        status_code: int,
    ) -> Dict[str, Any]:
        """
        Test permission-based access control
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            required_permissions: Set of permissions required
            user_permissions: Set of permissions user has
            status_code: Response status code
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "permission_based_access",
            "endpoint": endpoint,
            "method": method,
            "required_permissions": list(required_permissions),
            "user_permissions": list(user_permissions),
            "timestamp": datetime.utcnow().isoformat(),
        }

        has_all_permissions = required_permissions.issubset(user_permissions)

        if has_all_permissions:
            if status_code < 400:
                result["result"] = AuthzTestResult.PASS
                result["message"] = "User with required permissions granted access"
            else:
                result["result"] = AuthzTestResult.FAIL
                result["message"] = "User with required permissions denied access"
                result["severity"] = "high"
                result["recommendation"] = "Review permission checking logic"
        else:
            missing_permissions = required_permissions - user_permissions
            if status_code == 403:
                result["result"] = AuthzTestResult.PASS
                result["message"] = "User without required permissions correctly denied access"
                result["missing_permissions"] = list(missing_permissions)
            else:
                result["result"] = AuthzTestResult.FAIL
                result["message"] = "User without required permissions granted access"
                result["severity"] = "critical"
                result["missing_permissions"] = list(missing_permissions)
                result["recommendation"] = "Implement permission-based access control"

        self.test_results.append(result)
        return result

    def test_tenant_isolation(
        self,
        endpoint: str,
        method: str,
        resource_tenant_id: str,
        user_tenant_id: str,
        status_code: int,
    ) -> Dict[str, Any]:
        """
        Test multi-tenant isolation
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            resource_tenant_id: Tenant ID of the resource
            user_tenant_id: Tenant ID of the requesting user
            status_code: Response status code
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "tenant_isolation",
            "endpoint": endpoint,
            "method": method,
            "resource_tenant": resource_tenant_id,
            "user_tenant": user_tenant_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        same_tenant = resource_tenant_id == user_tenant_id

        if same_tenant:
            if status_code < 400:
                result["result"] = AuthzTestResult.PASS
                result["message"] = "User from same tenant granted access"
            else:
                result["result"] = AuthzTestResult.FAIL
                result["message"] = "User from same tenant denied access"
                result["severity"] = "high"
                result["recommendation"] = "Review tenant isolation logic"
        else:
            if status_code == 403 or status_code == 404:
                result["result"] = AuthzTestResult.PASS
                result["message"] = "User from different tenant correctly denied access"
            else:
                result["result"] = AuthzTestResult.FAIL
                result["message"] = "Cross-tenant access vulnerability detected"
                result["severity"] = "critical"
                result["recommendation"] = "Implement strict tenant isolation"

        self.test_results.append(result)
        return result

    def test_horizontal_privilege_escalation(
        self,
        endpoint: str,
        method: str,
        target_user_id: str,
        requesting_user_id: str,
        status_code: int,
    ) -> Dict[str, Any]:
        """
        Test for horizontal privilege escalation vulnerabilities
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            target_user_id: ID of the target user
            requesting_user_id: ID of the requesting user
            status_code: Response status code
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "horizontal_privilege_escalation",
            "endpoint": endpoint,
            "method": method,
            "target_user": target_user_id,
            "requesting_user": requesting_user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        is_same_user = target_user_id == requesting_user_id

        if is_same_user:
            result["result"] = AuthzTestResult.SKIP
            result["message"] = "Same user - not applicable"
        else:
            if status_code == 403 or status_code == 404:
                result["result"] = AuthzTestResult.PASS
                result["message"] = "Horizontal privilege escalation prevented"
            else:
                result["result"] = AuthzTestResult.FAIL
                result["message"] = "Horizontal privilege escalation vulnerability detected"
                result["severity"] = "critical"
                result["recommendation"] = "Validate user can only access their own resources"

        self.test_results.append(result)
        return result

    def test_vertical_privilege_escalation(
        self,
        endpoint: str,
        method: str,
        user_role: str,
        admin_only: bool,
        status_code: int,
    ) -> Dict[str, Any]:
        """
        Test for vertical privilege escalation vulnerabilities
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            user_role: Role of the requesting user
            admin_only: Whether endpoint is admin-only
            status_code: Response status code
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "vertical_privilege_escalation",
            "endpoint": endpoint,
            "method": method,
            "user_role": user_role,
            "admin_only": admin_only,
            "timestamp": datetime.utcnow().isoformat(),
        }

        is_admin = user_role in [AccessLevel.ADMIN, AccessLevel.SUPER_ADMIN]

        if admin_only and not is_admin:
            if status_code == 403 or status_code == 401:
                result["result"] = AuthzTestResult.PASS
                result["message"] = "Non-admin correctly denied access to admin endpoint"
            else:
                result["result"] = AuthzTestResult.FAIL
                result["message"] = "Vertical privilege escalation vulnerability detected"
                result["severity"] = "critical"
                result["recommendation"] = "Implement admin role verification"
        elif admin_only and is_admin:
            if status_code < 400:
                result["result"] = AuthzTestResult.PASS
                result["message"] = "Admin correctly granted access"
            else:
                result["result"] = AuthzTestResult.FAIL
                result["message"] = "Admin denied access to admin endpoint"
                result["severity"] = "high"
        else:
            result["result"] = AuthzTestResult.SKIP
            result["message"] = "Not an admin-only endpoint"

        self.test_results.append(result)
        return result

    def test_api_key_scope(
        self,
        endpoint: str,
        method: str,
        required_scopes: Set[str],
        api_key_scopes: Set[str],
        status_code: int,
    ) -> Dict[str, Any]:
        """
        Test API key scope restrictions
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            required_scopes: Set of scopes required for endpoint
            api_key_scopes: Set of scopes granted to API key
            status_code: Response status code
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "api_key_scope",
            "endpoint": endpoint,
            "method": method,
            "required_scopes": list(required_scopes),
            "api_key_scopes": list(api_key_scopes),
            "timestamp": datetime.utcnow().isoformat(),
        }

        has_required_scopes = required_scopes.issubset(api_key_scopes)

        if has_required_scopes:
            if status_code < 400:
                result["result"] = AuthzTestResult.PASS
                result["message"] = "API key with required scopes granted access"
            else:
                result["result"] = AuthzTestResult.FAIL
                result["message"] = "API key with required scopes denied access"
                result["severity"] = "high"
        else:
            missing_scopes = required_scopes - api_key_scopes
            if status_code == 403:
                result["result"] = AuthzTestResult.PASS
                result["message"] = "API key without required scopes correctly denied access"
                result["missing_scopes"] = list(missing_scopes)
            else:
                result["result"] = AuthzTestResult.FAIL
                result["message"] = "API key without required scopes granted access"
                result["severity"] = "critical"
                result["missing_scopes"] = list(missing_scopes)
                result["recommendation"] = "Implement API key scope validation"

        self.test_results.append(result)
        return result

    def test_insecure_direct_object_reference(
        self,
        endpoint: str,
        method: str,
        resource_id: str,
        user_has_access: bool,
        status_code: int,
    ) -> Dict[str, Any]:
        """
        Test for Insecure Direct Object Reference (IDOR) vulnerabilities
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            resource_id: ID of the resource being accessed
            user_has_access: Whether user should have access
            status_code: Response status code
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "insecure_direct_object_reference",
            "endpoint": endpoint,
            "method": method,
            "resource_id": resource_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if user_has_access:
            if status_code < 400:
                result["result"] = AuthzTestResult.PASS
                result["message"] = "Authorized user granted access to resource"
            else:
                result["result"] = AuthzTestResult.FAIL
                result["message"] = "Authorized user denied access"
                result["severity"] = "high"
        else:
            if status_code == 403 or status_code == 404:
                result["result"] = AuthzTestResult.PASS
                result["message"] = "IDOR vulnerability prevented"
            else:
                result["result"] = AuthzTestResult.FAIL
                result["message"] = "IDOR vulnerability detected - unauthorized access granted"
                result["severity"] = "critical"
                result["recommendation"] = "Validate user authorization before returning resources"

        self.test_results.append(result)
        return result

    def test_rate_limiting(
        self,
        endpoint: str,
        request_count: int,
        time_window_seconds: int,
        rate_limit_triggered: bool,
        status_code: int,
    ) -> Dict[str, Any]:
        """
        Test rate limiting implementation
        
        Args:
            endpoint: API endpoint path
            request_count: Number of requests made
            time_window_seconds: Time window for rate limiting
            rate_limit_triggered: Whether rate limit was triggered
            status_code: Response status code
            
        Returns:
            Test result dictionary
        """
        result = {
            "test": "rate_limiting",
            "endpoint": endpoint,
            "request_count": request_count,
            "time_window_seconds": time_window_seconds,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if rate_limit_triggered and status_code == 429:
            result["result"] = AuthzTestResult.PASS
            result["message"] = f"Rate limiting triggered after {request_count} requests"
        elif request_count > 100 and not rate_limit_triggered:
            result["result"] = AuthzTestResult.FAIL
            result["message"] = "No rate limiting detected"
            result["severity"] = "high"
            result["recommendation"] = "Implement rate limiting to prevent abuse"
        else:
            result["result"] = AuthzTestResult.WARNING
            result["message"] = "Rate limiting may be insufficient"
            result["recommendation"] = "Review rate limiting configuration"

        self.test_results.append(result)
        return result

    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of all authorization tests"""
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
            result = test.get("result", AuthzTestResult.SKIP)
            
            if result == AuthzTestResult.PASS:
                summary["passed"] += 1
            elif result == AuthzTestResult.FAIL:
                summary["failed"] += 1
                severity = test.get("severity", "medium")
                if severity == "critical":
                    summary["critical_issues"].append(test)
                elif severity == "high":
                    summary["high_issues"].append(test)
            elif result == AuthzTestResult.WARNING:
                summary["warnings"] += 1
            else:
                summary["skipped"] += 1

        return summary

    def clear_results(self):
        """Clear all test results"""
        self.test_results = []
