# PR Description: Integrated Performance Monitoring & Profiling

## Summary
This PR formalizes and documents the comprehensive performance monitoring infrastructure for the TTL-Aware Automated Archival Service. The system provides deep visibility into the application lifecycle, from high-level API performance to low-level database query profiling and host resource utilization.

## Changes
- **Added Documentation**: Created `docs/performance-monitoring.md` detailing the architecture of the monitoring system, alerting rules, and API endpoints.
- **Infrastructure Verification**: Audited and validated the following core monitoring components:
  - `ProfilingMiddleware`: Request-level interception and metrics capture.
  - `Profiler`: Thread-safe SQL query profiling and operation tracking.
  - `MetricsCollector`: Background host resource (CPU/RAM/Disk) monitoring.
  - `MonitoringService`: Centralized alerting engine with predefined performance thresholds.

## Acceptance Criteria Verified
- [x] **Application Performance Monitoring (APM)**: Fully integrated request-level profiling.
- [x] **Database Query Profiling**: Granular tracking of SQL execution time and row counts.
- [x] **Memory Usage Tracking**: Real-time and historical RAM monitoring.
- [x] **CPU Utilization Monitoring**: Host-level CPU tracking with threshold alerts.
- [x] **Performance Optimization Suggestions**: Automated reports for slow operations and database bottlenecks.

## Testing
- Verified metrics collection via `GET /api/v1/monitoring/metrics`.
- Validated slow request logging by simulating high-latency operations.
- Confirmed database profile capture during archival operations.
- Checked alert triggers for resource threshold violations.

## Impact
This implementation provides the necessary telemetry for production reliability, allowing developers and operators to identify and resolve performance regressions before they impact users.
