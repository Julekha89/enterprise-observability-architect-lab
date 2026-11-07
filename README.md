# Enterprise Observability Architect Lab

A Python-based synthetic observability project for HTTP and DNS monitoring, incident detection, failure correlation, and dashboard visualization.

## Features

- HTTP availability and response-time monitoring
- DNS resolution monitoring
- HTTP and DNS success-rate calculations
- Monitoring freshness detection
- Incident detection and recovery tracking
- HTTP and DNS failure correlation
- HTTP response-time trend visualization
- Local REST API and Dashboard V4

## Technologies

- Python 3
- Windows PowerShell
- HTML, CSS, and JavaScript
- CSV metrics storage
- Git and GitHub

## Project Structure

- dashboard/ - Dashboard V4
- probes/ - HTTP, DNS, and application probes
- incidents/ - Incident detection and correlation
- docs/ - Architecture documentation
- data/ - Local metrics excluded from Git

## Failure Correlation

The correlation engine analyzes HTTP and DNS failure windows.

It identifies HTTP-only, DNS-only, and overlapping failures.

Correlation results provide diagnostic hypotheses rather than definitive root-cause conclusions.

## Validation

- Six Python source files passed syntax validation
- Dashboard V4 REST API returned HTTP 200
- HTTP and DNS monitoring verified
- Four correlation edge-case tests passed

## Safety

- Local synthetic monitoring environment
- No production credentials
- Monitoring CSV files excluded from Git
- Older dashboard versions preserved locally
- Not an official ThousandEyes deployment

## Future Improvements

- Automated regression tests
- Structured incident reports
- Alert notifications
- Additional monitoring signals
