# Security Audit Module

Comprehensive security auditing and vulnerability scanning for the TTL Archival Service API.

## Overview

The Security Audit Module provides a complete framework for testing and validating the security posture of API endpoints. It includes:

- **Vulnerability Scanning**: Automated detection of common security vulnerabilities (OWASP Top 10)
- **Authentication Testing**: Validation of authentication mechanisms and session management
- **Authorization Testing**: Verification of access control and permission enforcement
- **Input Validation Testing**: Testing of input sanitization and validation mechanisms
- **Security Reporting**: Comprehensive reporting in multiple formats (JSON, HTML, Markdown, CSV)

## Components

### 1. SecurityScanner (`scanner.py`)

Performs automated vulnerability scanning on API endpoints.

**Features:**
- Security header validation
- Sensitive data exposure detection
- SQL injection pattern detection
- XSS vulnerability detection
- Authentication requirement verification
- CORS configuration analysis
- Information disclosure detection

**Usage:**
```python
from backend.security_audit import SecurityScanner

scanner = SecurityScanner()

vulnerabilities = scanner.scan_endpoint(
    endpoint="/api/v2/archives",
    method="GET",
    headers={"Authorization": "Bearer token"},
    response_headers={"X-Frame-Options": "DENY"},
    status_code=200,
    response_body='{"data": "..."}'
)

summary = scanner.get_scan_summary()
```

### 2. AuthenticationTester (`auth_tester.py`)

Tests authentication mechanisms for security vulnerabilities.

**Features:**
- Endpoint authentication requirement testing
- Token validation testing
- Session management validation
- Password policy strength assessment
- Brute force protection verification
- Multi-factor authentication testing

**Usage:**
```python
from backend.security_audit import AuthenticationTester

auth_tester = AuthenticationTester()

# Test endpoint authentication
result = auth_tester.test_endpoint_authentication(
    endpoint="/api/v2/archives",
    method="GET",
    requires_auth=True,
    auth_header="Bearer valid_token",
    status_code=200
)

# Test session management
session_result = auth_tester.test_session_management({
    "timeout_minutes": 30,
    "secure_flag": True,
    "httponly_flag": True,
    "samesite": "Strict"
})

summary = auth_tester.get_test_summary()
```

### 3. AuthorizationTester (`authz_tester.py`)

Tests authorization mechanisms and access control.

**Features:**
- Role-based access control (RBAC) testing
- Resource ownership validation
- Permission-based access control testing
- Multi-tenant isolation verification
- Horizontal privilege escalation detection
- Vertical privilege escalation detection
- API key scope validation
- Insecure Direct Object Reference (IDOR) detection
- Rate limiting verification

**Usage:**
```python
from backend.security_audit import AuthorizationTester, AccessLevel

authz_tester = AuthorizationTester()

# Test RBAC
result = authz_tester.test_role_based_access(
    endpoint="/api/v2/archives",
    method="GET",
    required_role=AccessLevel.AUTHENTICATED,
    user_role=AccessLevel.USER,
    status_code=200
)

# Test resource ownership
ownership_result = authz_tester.test_resource_ownership(
    endpoint="/api/v2/archives/123",
    method="GET",
    resource_owner_id="user_123",
    requesting_user_id="user_123",
    status_code=200
)

summary = authz_tester.get_test_summary()
```

### 4. InputValidationTester (`input_validator.py`)

Tests input validation and sanitization mechanisms.

**Features:**
- SQL injection prevention testing
- XSS prevention testing
- Command injection prevention testing
- Path traversal prevention testing
- Input type validation
- Input length validation
- Input format validation (email, URL, phone, date, etc.)
- File upload validation

**Usage:**
```python
from backend.security_audit import InputValidationTester, InputType

validator = InputValidationTester()

# Test SQL injection prevention
result = validator.test_sql_injection_prevention(
    endpoint="/api/v2/archives",
    parameter_name="id",
    malicious_inputs=["1' OR '1'='1", "1; DROP TABLE archives--"],
    responses=[
        {"status_code": 400, "body": "Invalid input"},
        {"status_code": 400, "body": "Invalid input"}
    ]
)

# Test input type validation
type_result = validator.test_input_type_validation(
    endpoint="/api/v2/archives",
    parameter_name="id",
    expected_type=InputType.INTEGER,
    test_inputs=[
        {"value": "123", "should_pass": True, "status_code": 200},
        {"value": "abc", "should_pass": False, "status_code": 400}
    ]
)

summary = validator.get_test_summary()
```

### 5. SecurityReporter (`reporter.py`)

Generates comprehensive security audit reports.

**Features:**
- Multi-format report generation (JSON, HTML, Markdown, CSV)
- Vulnerability aggregation and categorization
- Risk score calculation (0-100)
- Compliance status determination
- Detailed findings and recommendations
- Executive summary generation

**Usage:**
```python
from backend.security_audit import SecurityReporter, ReportFormat

reporter = SecurityReporter()

# Set metadata
reporter.set_metadata(
    application_name="TTL Archival Service",
    version="2.0.0",
    environment="production",
    auditor="Security Team"
)

# Add test results
reporter.add_vulnerability_scan_results(vulnerabilities)
reporter.add_authentication_test_results(auth_results)
reporter.add_authorization_test_results(authz_results)
reporter.add_input_validation_test_results(validation_results)

# Generate reports
json_report = reporter.export_report(ReportFormat.JSON)
html_report = reporter.export_report(ReportFormat.HTML)
markdown_report = reporter.export_report(ReportFormat.MARKDOWN)
csv_report = reporter.export_report(ReportFormat.CSV)

# Export to file
reporter.export_report(ReportFormat.JSON, filepath="audit_report.json")
```

## Running the Integration Test

To run the complete security audit demonstration:

```bash
cd backend/security_audit
python integration_test.py
```

This will:
1. Run vulnerability scanning
2. Test authentication mechanisms
3. Test authorization controls
4. Test input validation
5. Generate comprehensive reports

## Acceptance Criteria

✅ **Security vulnerability scanning** - Implemented via `SecurityScanner`
- Detects OWASP Top 10 vulnerabilities
- Checks security headers
- Identifies sensitive data exposure
- Detects SQL injection patterns
- Identifies XSS vulnerabilities
- Verifies authentication requirements
- Analyzes CORS configuration
- Detects information disclosure

✅ **Authentication testing** - Implemented via `AuthenticationTester`
- Tests endpoint authentication requirements
- Validates token handling
- Verifies session management
- Assesses password policies
- Tests brute force protection
- Validates MFA implementation

✅ **Authorization testing** - Implemented via `AuthorizationTester`
- Tests role-based access control
- Validates resource ownership
- Tests permission-based access
- Verifies tenant isolation
- Detects privilege escalation vulnerabilities
- Tests API key scopes
- Detects IDOR vulnerabilities
- Verifies rate limiting

✅ **Input validation testing** - Implemented via `InputValidationTester`
- Tests SQL injection prevention
- Tests XSS prevention
- Tests command injection prevention
- Tests path traversal prevention
- Validates input types
- Validates input length
- Validates input formats
- Tests file upload validation

✅ **Security reporting** - Implemented via `SecurityReporter`
- Generates JSON reports
- Generates HTML reports
- Generates Markdown reports
- Generates CSV reports
- Calculates risk scores
- Determines compliance status
- Provides recommendations
- Aggregates findings by severity

## Test Results

All modules have been tested and verified to work correctly:

```
✓ All modules imported successfully
✓ SecurityScanner functional
✓ AuthenticationTester functional
✓ AuthorizationTester functional
✓ InputValidationTester functional
✓ SecurityReporter functional
```

## Integration with API

To integrate security auditing into your API:

```python
from backend.security_audit import (
    SecurityScanner,
    AuthenticationTester,
    AuthorizationTester,
    InputValidationTester,
    SecurityReporter,
    ReportFormat
)

# Initialize components
scanner = SecurityScanner()
auth_tester = AuthenticationTester()
authz_tester = AuthorizationTester()
validator = InputValidationTester()
reporter = SecurityReporter()

# Run audits on your endpoints
# ... (audit code)

# Generate report
reporter.set_metadata(
    application_name="Your App",
    version="1.0.0"
)
report = reporter.export_report(ReportFormat.JSON)
```

## Best Practices

1. **Regular Audits**: Run security audits regularly (weekly/monthly)
2. **Automated Testing**: Integrate into CI/CD pipeline
3. **Baseline Comparison**: Compare reports over time to track improvements
4. **Action Items**: Create tickets for all critical and high findings
5. **Documentation**: Document all security decisions and mitigations
6. **Review**: Have security team review all audit reports

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [API Security Best Practices](https://owasp.org/www-project-api-security/)

## License

This module is part of the TTL Archival Service and follows the same license.
