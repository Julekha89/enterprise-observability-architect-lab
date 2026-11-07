# Enterprise Observability Architect Lab - Low-Level Design

## Runtime

Operating System: Windows
Python: 3.14
Project Root: D:\Enterprise-Observability-Architect-Lab

## Application

Health Endpoint:
http://127.0.0.1:8765/health

## HTTP Monitoring

Source: probes/http_monitor.py
Target: Local application health endpoint
Interval: 30 seconds
Storage: data/http_metrics.csv

Recorded Fields:
- timestamp_utc
- status
- latency_ms
- error

## DNS Monitoring

Source: probes/dns_monitor.py
Target Domain: example.com
Interval: 30 seconds
Storage: data/dns_metrics.csv

## Dashboard V4

Source: dashboard/dashboard_server_v4.py
Local URL: http://127.0.0.1:8769
REST Endpoint: /api/status
Browser Refresh: 10 seconds

Dashboard Features:
- HTTP and DNS health
- Success-rate calculations
- Latest response and resolution times
- Collection freshness
- Incident counts and history
- Recent monitoring checks
- Response-time trend charts

## Incident Detection

Threshold: 3 consecutive DOWN checks
Severity: CRITICAL
Recovery: Subsequent UP check
Freshness Threshold: 90 seconds

Dashboard V4 calculates incident history from CSV records.

Standalone incident_engine.py analyzes HTTP incidents separately.

## Failure Correlation

Source: incidents/correlation_engine.py

Inputs:
- data/http_metrics.csv
- data/dns_metrics.csv

Analysis:
- Identify failure windows
- Compare overlapping failures
- Distinguish HTTP-only and DNS-only failure periods
- Produce diagnostic hypotheses

The correlation engine is standalone and is not currently integrated into Dashboard V4.

## Data Storage

HTTP Metrics: data/http_metrics.csv
DNS Metrics: data/dns_metrics.csv

Both files are local historical records and excluded from Git.

## Safety Controls

- Preserve historical monitoring data
- Do not overwrite CSV files
- Do not modify Docker or WSL2
- Do not modify other applications
- Avoid production credentials
- Keep the environment local

## Validation

- Verify application health endpoint
- Verify HTTP and DNS probes
- Verify CSV metrics collection
- Verify dashboard REST API
- Verify incident detection and recovery
- Verify failure correlation
