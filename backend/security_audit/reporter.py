"""
Security Audit Reporter
Generates comprehensive security audit reports
"""
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ReportFormat(str, Enum):
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"
    CSV = "csv"


class ReportSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SecurityReporter:
    """Generate comprehensive security audit reports"""

    def __init__(self):
        self.report_data: Dict[str, Any] = {
            "metadata": {},
            "vulnerabilities": [],
            "authentication_tests": [],
            "authorization_tests": [],
            "input_validation_tests": [],
            "summary": {},
        }
        self.report_timestamp = None

    def add_vulnerability_scan_results(
        self,
        vulnerabilities: List[Dict[str, Any]],
    ) -> None:
        """
        Add vulnerability scan results to report
        
        Args:
            vulnerabilities: List of vulnerability findings
        """
        self.report_data["vulnerabilities"].extend(vulnerabilities)

    def add_authentication_test_results(
        self,
        test_results: List[Dict[str, Any]],
    ) -> None:
        """
        Add authentication test results to report
        
        Args:
            test_results: List of authentication test results
        """
        self.report_data["authentication_tests"].extend(test_results)

    def add_authorization_test_results(
        self,
        test_results: List[Dict[str, Any]],
    ) -> None:
        """
        Add authorization test results to report
        
        Args:
            test_results: List of authorization test results
        """
        self.report_data["authorization_tests"].extend(test_results)

    def add_input_validation_test_results(
        self,
        test_results: List[Dict[str, Any]],
    ) -> None:
        """
        Add input validation test results to report
        
        Args:
            test_results: List of input validation test results
        """
        self.report_data["input_validation_tests"].extend(test_results)

    def set_metadata(
        self,
        application_name: str,
        version: str,
        audit_date: Optional[str] = None,
        auditor: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> None:
        """
        Set report metadata
        
        Args:
            application_name: Name of the application
            version: Application version
            audit_date: Date of audit
            auditor: Name of auditor
            environment: Environment being audited
        """
        self.report_data["metadata"] = {
            "application_name": application_name,
            "version": version,
            "audit_date": audit_date or datetime.utcnow().isoformat(),
            "auditor": auditor or "Security Audit System",
            "environment": environment or "production",
            "report_generated": datetime.utcnow().isoformat(),
        }

    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate report summary
        
        Returns:
            Summary dictionary
        """
        summary = {
            "total_findings": 0,
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            },
            "by_category": {
                "vulnerabilities": 0,
                "authentication": 0,
                "authorization": 0,
                "input_validation": 0,
            },
            "test_results": {
                "passed": 0,
                "failed": 0,
                "warnings": 0,
                "skipped": 0,
            },
            "risk_score": 0,
            "compliance_status": "unknown",
        }

        # Count vulnerabilities by severity
        for vuln in self.report_data["vulnerabilities"]:
            severity = vuln.get("level", "info").lower()
            if severity in summary["by_severity"]:
                summary["by_severity"][severity] += 1
            summary["by_category"]["vulnerabilities"] += 1
            summary["total_findings"] += 1

        # Count authentication test results
        for test in self.report_data["authentication_tests"]:
            result = test.get("result", "skip").lower()
            if result == "pass":
                summary["test_results"]["passed"] += 1
            elif result == "fail":
                summary["test_results"]["failed"] += 1
            elif result == "warning":
                summary["test_results"]["warnings"] += 1
            else:
                summary["test_results"]["skipped"] += 1
            summary["by_category"]["authentication"] += 1

        # Count authorization test results
        for test in self.report_data["authorization_tests"]:
            result = test.get("result", "skip").lower()
            if result == "pass":
                summary["test_results"]["passed"] += 1
            elif result == "fail":
                summary["test_results"]["failed"] += 1
            elif result == "warning":
                summary["test_results"]["warnings"] += 1
            else:
                summary["test_results"]["skipped"] += 1
            summary["by_category"]["authorization"] += 1

        # Count input validation test results
        for test in self.report_data["input_validation_tests"]:
            result = test.get("result", "skip").lower()
            if result == "pass":
                summary["test_results"]["passed"] += 1
            elif result == "fail":
                summary["test_results"]["failed"] += 1
            elif result == "warning":
                summary["test_results"]["warnings"] += 1
            else:
                summary["test_results"]["skipped"] += 1
            summary["by_category"]["input_validation"] += 1

        # Calculate risk score (0-100)
        critical_weight = summary["by_severity"]["critical"] * 25
        high_weight = summary["by_severity"]["high"] * 15
        medium_weight = summary["by_severity"]["medium"] * 5
        low_weight = summary["by_severity"]["low"] * 1

        total_weight = critical_weight + high_weight + medium_weight + low_weight
        summary["risk_score"] = min(100, total_weight)

        # Determine compliance status
        if summary["by_severity"]["critical"] > 0:
            summary["compliance_status"] = "non-compliant"
        elif summary["by_severity"]["high"] > 2:
            summary["compliance_status"] = "at-risk"
        elif summary["test_results"]["failed"] > 0:
            summary["compliance_status"] = "needs-review"
        else:
            summary["compliance_status"] = "compliant"

        self.report_data["summary"] = summary
        return summary

    def generate_json_report(self) -> str:
        """
        Generate JSON format report
        
        Returns:
            JSON formatted report string
        """
        self.generate_summary()
        return json.dumps(self.report_data, indent=2, default=str)

    def generate_markdown_report(self) -> str:
        """
        Generate Markdown format report
        
        Returns:
            Markdown formatted report string
        """
        self.generate_summary()
        
        report = []
        report.append("# Security Audit Report\n")

        # Metadata section
        metadata = self.report_data["metadata"]
        report.append("## Report Information\n")
        report.append(f"- **Application**: {metadata.get('application_name', 'N/A')}\n")
        report.append(f"- **Version**: {metadata.get('version', 'N/A')}\n")
        report.append(f"- **Environment**: {metadata.get('environment', 'N/A')}\n")
        report.append(f"- **Audit Date**: {metadata.get('audit_date', 'N/A')}\n")
        report.append(f"- **Report Generated**: {metadata.get('report_generated', 'N/A')}\n")
        report.append(f"- **Auditor**: {metadata.get('auditor', 'N/A')}\n\n")

        # Summary section
        summary = self.report_data["summary"]
        report.append("## Executive Summary\n")
        report.append(f"- **Total Findings**: {summary.get('total_findings', 0)}\n")
        report.append(f"- **Risk Score**: {summary.get('risk_score', 0)}/100\n")
        report.append(f"- **Compliance Status**: {summary.get('compliance_status', 'unknown').upper()}\n\n")

        # Severity breakdown
        report.append("### Findings by Severity\n")
        by_severity = summary.get("by_severity", {})
        report.append(f"- **Critical**: {by_severity.get('critical', 0)}\n")
        report.append(f"- **High**: {by_severity.get('high', 0)}\n")
        report.append(f"- **Medium**: {by_severity.get('medium', 0)}\n")
        report.append(f"- **Low**: {by_severity.get('low', 0)}\n")
        report.append(f"- **Info**: {by_severity.get('info', 0)}\n\n")

        # Test results
        report.append("### Test Results\n")
        test_results = summary.get("test_results", {})
        report.append(f"- **Passed**: {test_results.get('passed', 0)}\n")
        report.append(f"- **Failed**: {test_results.get('failed', 0)}\n")
        report.append(f"- **Warnings**: {test_results.get('warnings', 0)}\n")
        report.append(f"- **Skipped**: {test_results.get('skipped', 0)}\n\n")

        # Vulnerabilities section
        if self.report_data["vulnerabilities"]:
            report.append("## Vulnerabilities\n\n")
            for vuln in self.report_data["vulnerabilities"]:
                report.append(f"### {vuln.get('title', 'Unknown Vulnerability')}\n")
                report.append(f"- **Severity**: {vuln.get('level', 'unknown').upper()}\n")
                report.append(f"- **Type**: {vuln.get('type', 'unknown')}\n")
                report.append(f"- **Endpoint**: {vuln.get('endpoint', 'N/A')}\n")
                report.append(f"- **Description**: {vuln.get('description', 'N/A')}\n")
                report.append(f"- **Recommendation**: {vuln.get('recommendation', 'N/A')}\n")
                report.append(f"- **CWE**: {vuln.get('cwe', 'N/A')}\n\n")

        # Authentication tests section
        if self.report_data["authentication_tests"]:
            report.append("## Authentication Tests\n\n")
            for test in self.report_data["authentication_tests"]:
                report.append(f"### {test.get('test', 'Unknown Test')}\n")
                report.append(f"- **Result**: {test.get('result', 'unknown').upper()}\n")
                report.append(f"- **Message**: {test.get('message', 'N/A')}\n")
                if test.get("severity"):
                    report.append(f"- **Severity**: {test.get('severity').upper()}\n")
                if test.get("recommendation"):
                    report.append(f"- **Recommendation**: {test.get('recommendation')}\n")
                report.append("\n")

        # Authorization tests section
        if self.report_data["authorization_tests"]:
            report.append("## Authorization Tests\n\n")
            for test in self.report_data["authorization_tests"]:
                report.append(f"### {test.get('test', 'Unknown Test')}\n")
                report.append(f"- **Result**: {test.get('result', 'unknown').upper()}\n")
                report.append(f"- **Message**: {test.get('message', 'N/A')}\n")
                if test.get("severity"):
                    report.append(f"- **Severity**: {test.get('severity').upper()}\n")
                if test.get("recommendation"):
                    report.append(f"- **Recommendation**: {test.get('recommendation')}\n")
                report.append("\n")

        # Input validation tests section
        if self.report_data["input_validation_tests"]:
            report.append("## Input Validation Tests\n\n")
            for test in self.report_data["input_validation_tests"]:
                report.append(f"### {test.get('test', 'Unknown Test')}\n")
                report.append(f"- **Result**: {test.get('result', 'unknown').upper()}\n")
                report.append(f"- **Message**: {test.get('message', 'N/A')}\n")
                if test.get("severity"):
                    report.append(f"- **Severity**: {test.get('severity').upper()}\n")
                if test.get("recommendation"):
                    report.append(f"- **Recommendation**: {test.get('recommendation')}\n")
                report.append("\n")

        # Recommendations section
        report.append("## Recommendations\n\n")
        report.append("### Critical Priority\n")
        critical_issues = [v for v in self.report_data["vulnerabilities"] if v.get("level") == "critical"]
        if critical_issues:
            for issue in critical_issues:
                report.append(f"- {issue.get('recommendation', 'N/A')}\n")
        else:
            report.append("- No critical issues found\n")

        report.append("\n### High Priority\n")
        high_issues = [v for v in self.report_data["vulnerabilities"] if v.get("level") == "high"]
        if high_issues:
            for issue in high_issues[:5]:  # Limit to 5
                report.append(f"- {issue.get('recommendation', 'N/A')}\n")
        else:
            report.append("- No high priority issues found\n")

        return "".join(report)

    def generate_html_report(self) -> str:
        """
        Generate HTML format report
        
        Returns:
            HTML formatted report string
        """
        self.generate_summary()
        
        html = []
        html.append("<!DOCTYPE html>\n")
        html.append("<html>\n")
        html.append("<head>\n")
        html.append("<meta charset='UTF-8'>\n")
        html.append("<title>Security Audit Report</title>\n")
        html.append("<style>\n")
        html.append("body { font-family: Arial, sans-serif; margin: 20px; }\n")
        html.append("h1 { color: #333; }\n")
        html.append("h2 { color: #666; border-bottom: 2px solid #ddd; padding-bottom: 10px; }\n")
        html.append(".critical { color: #d32f2f; font-weight: bold; }\n")
        html.append(".high { color: #f57c00; font-weight: bold; }\n")
        html.append(".medium { color: #fbc02d; font-weight: bold; }\n")
        html.append(".low { color: #388e3c; font-weight: bold; }\n")
        html.append("table { border-collapse: collapse; width: 100%; margin: 20px 0; }\n")
        html.append("th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }\n")
        html.append("th { background-color: #f5f5f5; }\n")
        html.append(".summary-box { background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0; }\n")
        html.append("</style>\n")
        html.append("</head>\n")
        html.append("<body>\n")

        # Header
        html.append("<h1>Security Audit Report</h1>\n")

        # Metadata
        metadata = self.report_data["metadata"]
        html.append("<div class='summary-box'>\n")
        html.append(f"<p><strong>Application:</strong> {metadata.get('application_name', 'N/A')}</p>\n")
        html.append(f"<p><strong>Version:</strong> {metadata.get('version', 'N/A')}</p>\n")
        html.append(f"<p><strong>Environment:</strong> {metadata.get('environment', 'N/A')}</p>\n")
        html.append(f"<p><strong>Audit Date:</strong> {metadata.get('audit_date', 'N/A')}</p>\n")
        html.append(f"<p><strong>Report Generated:</strong> {metadata.get('report_generated', 'N/A')}</p>\n")
        html.append("</div>\n")

        # Summary
        summary = self.report_data["summary"]
        html.append("<h2>Executive Summary</h2>\n")
        html.append("<div class='summary-box'>\n")
        html.append(f"<p><strong>Total Findings:</strong> {summary.get('total_findings', 0)}</p>\n")
        html.append(f"<p><strong>Risk Score:</strong> {summary.get('risk_score', 0)}/100</p>\n")
        html.append(f"<p><strong>Compliance Status:</strong> <span class='{summary.get('compliance_status', 'unknown')}'>{summary.get('compliance_status', 'unknown').upper()}</span></p>\n")
        html.append("</div>\n")

        # Severity breakdown
        html.append("<h2>Findings by Severity</h2>\n")
        html.append("<table>\n")
        html.append("<tr><th>Severity</th><th>Count</th></tr>\n")
        by_severity = summary.get("by_severity", {})
        for severity in ["critical", "high", "medium", "low", "info"]:
            count = by_severity.get(severity, 0)
            html.append(f"<tr><td class='{severity}'>{severity.upper()}</td><td>{count}</td></tr>\n")
        html.append("</table>\n")

        # Vulnerabilities
        if self.report_data["vulnerabilities"]:
            html.append("<h2>Vulnerabilities</h2>\n")
            html.append("<table>\n")
            html.append("<tr><th>Title</th><th>Severity</th><th>Type</th><th>Endpoint</th></tr>\n")
            for vuln in self.report_data["vulnerabilities"]:
                severity = vuln.get("level", "info").lower()
                html.append(f"<tr>\n")
                html.append(f"<td>{vuln.get('title', 'Unknown')}</td>\n")
                html.append(f"<td class='{severity}'>{severity.upper()}</td>\n")
                html.append(f"<td>{vuln.get('type', 'N/A')}</td>\n")
                html.append(f"<td>{vuln.get('endpoint', 'N/A')}</td>\n")
                html.append(f"</tr>\n")
            html.append("</table>\n")

        html.append("</body>\n")
        html.append("</html>\n")

        return "".join(html)

    def generate_csv_report(self) -> str:
        """
        Generate CSV format report
        
        Returns:
            CSV formatted report string
        """
        self.generate_summary()
        
        csv_lines = []
        
        # Header
        csv_lines.append("Security Audit Report\n")
        metadata = self.report_data["metadata"]
        csv_lines.append(f"Application,{metadata.get('application_name', 'N/A')}\n")
        csv_lines.append(f"Version,{metadata.get('version', 'N/A')}\n")
        csv_lines.append(f"Environment,{metadata.get('environment', 'N/A')}\n")
        csv_lines.append(f"Audit Date,{metadata.get('audit_date', 'N/A')}\n")
        csv_lines.append(f"Report Generated,{metadata.get('report_generated', 'N/A')}\n\n")

        # Summary
        summary = self.report_data["summary"]
        csv_lines.append("Summary\n")
        csv_lines.append(f"Total Findings,{summary.get('total_findings', 0)}\n")
        csv_lines.append(f"Risk Score,{summary.get('risk_score', 0)}\n")
        csv_lines.append(f"Compliance Status,{summary.get('compliance_status', 'unknown')}\n\n")

        # Vulnerabilities
        if self.report_data["vulnerabilities"]:
            csv_lines.append("Vulnerabilities\n")
            csv_lines.append("Title,Severity,Type,Endpoint,Description,Recommendation,CWE\n")
            for vuln in self.report_data["vulnerabilities"]:
                csv_lines.append(
                    f"\"{vuln.get('title', 'N/A')}\","
                    f"\"{vuln.get('level', 'N/A')}\","
                    f"\"{vuln.get('type', 'N/A')}\","
                    f"\"{vuln.get('endpoint', 'N/A')}\","
                    f"\"{vuln.get('description', 'N/A')}\","
                    f"\"{vuln.get('recommendation', 'N/A')}\","
                    f"\"{vuln.get('cwe', 'N/A')}\"\n"
                )
            csv_lines.append("\n")

        return "".join(csv_lines)

    def export_report(
        self,
        format: ReportFormat = ReportFormat.JSON,
        filepath: Optional[str] = None,
    ) -> str:
        """
        Export report in specified format
        
        Args:
            format: Report format (json, html, markdown, csv)
            filepath: Optional file path to save report
            
        Returns:
            Report content as string
        """
        if format == ReportFormat.JSON:
            report_content = self.generate_json_report()
        elif format == ReportFormat.HTML:
            report_content = self.generate_html_report()
        elif format == ReportFormat.MARKDOWN:
            report_content = self.generate_markdown_report()
        elif format == ReportFormat.CSV:
            report_content = self.generate_csv_report()
        else:
            report_content = self.generate_json_report()

        if filepath:
            try:
                with open(filepath, "w") as f:
                    f.write(report_content)
                logger.info(f"Report exported to {filepath}")
            except Exception as e:
                logger.error(f"Failed to export report: {e}")

        return report_content

    def clear_report(self):
        """Clear all report data"""
        self.report_data = {
            "metadata": {},
            "vulnerabilities": [],
            "authentication_tests": [],
            "authorization_tests": [],
            "input_validation_tests": [],
            "summary": {},
        }
        self.report_timestamp = None
