# Enterprise Observability Architect Lab - High-Level Design

## Business Objective

Build a local synthetic observability environment to monitor HTTP application availability, DNS resolution, response times, and incidents.

## Implemented Architecture

1. Local HTTP application provides a health endpoint.
2. HTTP probe checks application availability and latency.
3. DNS probe measures domain resolution and latency.
4. Monitoring results are stored in local CSV files.
5. Dashboard V4 reads CSV metrics and calculates health, availability, freshness, and incident history.
6. Standalone incident and correlation engines support additional investigation.

## Data Flow

HTTP Application -> HTTP Probe -> HTTP CSV
DNS Resolution -> DNS Probe -> DNS CSV

HTTP CSV + DNS CSV -> Dashboard V4
HTTP CSV -> Standalone Incident Engine
HTTP CSV + DNS CSV -> Standalone Correlation Engine

## Monitoring Capabilities

- HTTP availability and response-time monitoring
- DNS resolution monitoring
- Success-rate calculations
- Collection freshness detection
- Incident detection after three consecutive failures
- Incident recovery tracking
- HTTP and DNS failure-window correlation
- Dashboard charts and recent monitoring results

## Technology Stack

- Python 3
- Windows PowerShell
- HTML, CSS, JavaScript
- CSV metrics storage
- Git and GitHub

## Security and Safety

- Local synthetic monitoring environment
- No production credentials
- Historical monitoring CSV files excluded from Git
- No Docker or WSL2 modifications
- No modifications to unrelated projects

## Architecture Limitations

- Monitoring does not represent actual remote enterprise branches.
- CSV storage is used instead of a production metrics database.
- Failure correlation provides diagnostic hypotheses, not definitive root-cause conclusions.
- The dashboard does not currently integrate the standalone correlation engine.
- This is not an official ThousandEyes deployment.

## Future Improvements

- Automated regression tests
- Structured incident reports
- Alert notifications
- Additional monitoring signals
- Optional centralized metrics storage
