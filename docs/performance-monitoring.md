# Performance Monitoring System

This document outlines the performance monitoring, profiling, and resource tracking infrastructure implemented in the TTL-Aware Automated Archival Service.

## Overview

The service includes a comprehensive, built-in monitoring suite designed to ensure high availability, resource efficiency, and actionable performance insights without relying on heavy external APM tools.

## Key Components

### 1. Application Performance Monitoring (APM)
Implemented via a custom ASGI middleware that intercepts all incoming HTTP requests.
- **Location**: `backend/middleware/profiling_middleware.py`
- **Features**:
  - Automated tracking of request duration (ms).
  - Memory consumption delta per request.
  - CPU utilization delta per request.
  - Slow request identification with automated logging.
  - Performance metadata injected into response headers (`X-Profiler-Duration-Ms`).

### 2. Database Query Profiling
A thread-safe profiling utility that captures low-level SQL execution metrics.
- **Location**: `backend/utils/profiler.py`
- **Features**:
  - Captures full SQL query text.
  - Measures execution time and rows affected.
  - Identifies "Slow Queries" based on configurable thresholds.
  - Aggregates database performance statistics for reporting.

### 3. Resource Tracking
A background collection system for host-level resource utilization.
- **Location**: `backend/utils/metrics_collector.py`
- **Features**:
  - Real-time CPU usage (%) monitoring.
  - Memory (RAM) usage and availability tracking.
  - Disk I/O and storage capacity monitoring.
  - Metrics persistence via `MetricsService` for historical analysis.

### 4. Alerting & Optimization Suggestions
An intelligent service that evaluates metrics against predefined rules to provide actionable feedback.
- **Location**: `backend/services/monitoring_service.py`
- **Rules Engine**:
  - **High CPU**: Alerts when usage exceeds 80%.
  - **High Memory**: Alerts when usage exceeds 85%.
  - **Slow API**: Alerts on average response times > 2000ms.
  - **Slow DB**: Alerts on average query durations > 1000ms.
  - **High Error Rate**: Critical alerts when errors exceed 10% of total traffic.

## API Reference

The monitoring system is exposed via the following endpoints:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/monitoring/metrics` | `GET` | Current real-time performance metrics. |
| `/api/v1/monitoring/summary` | `GET` | Aggregated performance summary and stats. |
| `/api/v1/monitoring/alerts` | `GET` | List of active performance alerts. |
| `/api/v1/monitoring/slow-operations` | `GET` | Detailed report on the slowest API operations. |
| `/api/v1/monitoring/database-performance` | `GET` | Deep dive into SQL query performance. |
| `/api/v1/monitoring/system-usage` | `GET` | Host-level resource utilization summary. |

## Configuration

Monitoring can be toggled or configured via the following environment variables or the configuration API:
- `PROFILING_ENABLED`: Enable/disable request profiling.
- `SLOW_REQUEST_THRESHOLD_MS`: Threshold for logging slow requests (Default: 1000ms).
- `METRICS_COLLECTION_INTERVAL`: Frequency of background resource polling.
