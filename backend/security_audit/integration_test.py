"""
Integration test for the complete security audit workflow
Demonstrates how to use all security audit modules together
"""
import sys
from datetime import datetime
from scanner import SecurityScanner
from auth_tester import AuthenticationTester
from authz_tester import AuthorizationTester, AccessLevel
from input_validator import InputValidationTester, InputType
from reporter import SecurityReporter, ReportFormat


def run_security_audit_demo():
    """Run a complete security audit demonstration"""
    
    print("=" * 80)
    print("TTL Archival Service - Comprehensive Security Audit")
    print("=" * 80)
    print()

    # Initialize all audit components
    scanner = SecurityScanner()
    auth_tester = AuthenticationTester()
    authz_tester = AuthorizationTester()
    input_validator = InputValidationTester()
    reporter = SecurityReporter()

    # Set report metadata
    reporter.set_metadata(
        application_name="TTL Archival Service",
        version="2.0.0",
        environment="production",
        auditor="Security Audit System",
    )

    print("[1/5] Running Vulnerability Scan...")
    print("-" * 80)
    
    # Simulate vulnerability scanning
    vulnerabilities = scanner.scan_endpoint(
        endpoint="/api/v2/archives",
        method="GET",
        headers={"Authorization": "Bearer token123"},
        response_headers={
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
        },
        status_code=200,
        response_body='{"data": "archive_data"}',
    )
    
    print(f"✓ Scanned endpoint: /api/v2/archives")
    print(f"✓ Found {len(vulnerabilities)} potential vulnerabilities")
    reporter.add_vulnerability_scan_results(vulnerabilities)
    print()

    print("[2/5] Running Authentication Tests...")
    print("-" * 80)
    
    # Test authentication
    auth_result = auth_tester.test_endpoint_authentication(
        endpoint="/api/v2/archives",
        method="GET",
        requires_auth=True,
        auth_header="Bearer valid_token",
        status_code=200,
    )
    print(f"✓ Authentication test: {auth_result['result'].upper()}")
    print(f"  Message: {auth_result['message']}")
    
    # Test session management
    session_result = auth_tester.test_session_management({
        "timeout_minutes": 30,
        "secure_flag": True,
        "httponly_flag": True,
        "samesite": "Strict",
    })
    print(f"✓ Session management test: {session_result['result'].upper()}")
    
    # Test password policy
    password_result = auth_tester.test_password_policy({
        "min_length": 12,
        "requires_uppercase": True,
        "requires_lowercase": True,
        "requires_numbers": True,
        "requires_special": True,
        "history_count": 5,
    })
    print(f"✓ Password policy test: {password_result['result'].upper()}")
    
    reporter.add_authentication_test_results(auth_tester.test_results)
    print()

    print("[3/5] Running Authorization Tests...")
    print("-" * 80)
    
    # Test role-based access
    rbac_result = authz_tester.test_role_based_access(
        endpoint="/api/v2/archives",
        method="GET",
        required_role=AccessLevel.AUTHENTICATED,
        user_role=AccessLevel.USER,
        status_code=200,
    )
    print(f"✓ RBAC test: {rbac_result['result'].upper()}")
    print(f"  Message: {rbac_result['message']}")
    
    # Test resource ownership
    ownership_result = authz_tester.test_resource_ownership(
        endpoint="/api/v2/archives/123",
        method="GET",
        resource_owner_id="user_123",
        requesting_user_id="user_123",
        status_code=200,
    )
    print(f"✓ Resource ownership test: {ownership_result['result'].upper()}")
    
    # Test tenant isolation
    tenant_result = authz_tester.test_tenant_isolation(
        endpoint="/api/v2/archives",
        method="GET",
        resource_tenant_id="tenant_1",
        user_tenant_id="tenant_1",
        status_code=200,
    )
    print(f"✓ Tenant isolation test: {tenant_result['result'].upper()}")
    
    reporter.add_authorization_test_results(authz_tester.test_results)
    print()

    print("[4/5] Running Input Validation Tests...")
    print("-" * 80)
    
    # Test SQL injection prevention
    sql_result = input_validator.test_sql_injection_prevention(
        endpoint="/api/v2/archives",
        parameter_name="id",
        malicious_inputs=["1' OR '1'='1", "1; DROP TABLE archives--"],
        responses=[
            {"status_code": 400, "body": "Invalid input"},
            {"status_code": 400, "body": "Invalid input"},
        ],
    )
    print(f"✓ SQL injection prevention: {sql_result['result'].upper()}")
    
    # Test XSS prevention
    xss_result = input_validator.test_xss_prevention(
        endpoint="/api/v2/archives",
        parameter_name="name",
        xss_payloads=["<script>alert('xss')</script>", "javascript:alert('xss')"],
        responses=[
            {"status_code": 400, "body": "Invalid input"},
            {"status_code": 400, "body": "Invalid input"},
        ],
    )
    print(f"✓ XSS prevention: {xss_result['result'].upper()}")
    
    # Test input format validation
    format_result = input_validator.test_input_format_validation(
        endpoint="/api/v2/archives",
        parameter_name="email",
        format_type="email",
        test_inputs=[
            {"value": "user@example.com", "should_pass": True, "status_code": 200},
            {"value": "invalid-email", "should_pass": False, "status_code": 400},
        ],
    )
    print(f"✓ Email format validation: {format_result['result'].upper()}")
    
    reporter.add_input_validation_test_results(input_validator.test_results)
    print()

    print("[5/5] Generating Security Report...")
    print("-" * 80)
    
    # Generate summary
    summary = reporter.generate_summary()
    
    print(f"✓ Total Findings: {summary['total_findings']}")
    print(f"✓ Risk Score: {summary['risk_score']}/100")
    print(f"✓ Compliance Status: {summary['compliance_status'].upper()}")
    print()
    print("Findings by Severity:")
    print(f"  - Critical: {summary['by_severity']['critical']}")
    print(f"  - High: {summary['by_severity']['high']}")
    print(f"  - Medium: {summary['by_severity']['medium']}")
    print(f"  - Low: {summary['by_severity']['low']}")
    print()
    print("Test Results:")
    print(f"  - Passed: {summary['test_results']['passed']}")
    print(f"  - Failed: {summary['test_results']['failed']}")
    print(f"  - Warnings: {summary['test_results']['warnings']}")
    print()

    # Export reports in different formats
    print("Exporting reports...")
    
    json_report = reporter.export_report(ReportFormat.JSON)
    print(f"✓ JSON report generated ({len(json_report)} bytes)")
    
    markdown_report = reporter.export_report(ReportFormat.MARKDOWN)
    print(f"✓ Markdown report generated ({len(markdown_report)} bytes)")
    
    html_report = reporter.export_report(ReportFormat.HTML)
    print(f"✓ HTML report generated ({len(html_report)} bytes)")
    
    csv_report = reporter.export_report(ReportFormat.CSV)
    print(f"✓ CSV report generated ({len(csv_report)} bytes)")
    
    print()
    print("=" * 80)
    print("Security Audit Complete!")
    print("=" * 80)
    print()
    
    return {
        "scanner": scanner,
        "auth_tester": auth_tester,
        "authz_tester": authz_tester,
        "input_validator": input_validator,
        "reporter": reporter,
        "summary": summary,
    }


if __name__ == "__main__":
    try:
        results = run_security_audit_demo()
        print("✓ All security audit components working correctly!")
        sys.exit(0)
    except Exception as e:
        print(f"✗ Error during security audit: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
