# Enterprise Observability Lab — High-Level Design

## Business Objective
Design a centralized observability solution for a
simulated enterprise with two branches and one
business-critical application.

## Architecture Components
- Branch A: Healthy monitoring profile
- Branch B: Degraded monitoring profile
- Application: Local HTTP service
- Monitoring: Windows-native Python probes
- Storage: SQLite metrics and incident records
- Visualization: Local web dashboard

## Observability Objectives
- Detect application availability failures
- Measure HTTP response times
- Monitor DNS resolution
- Record connectivity test results
- Generate alerts based on defined thresholds
- Support incident investigation and reporting

## Constraints
- No Docker or WSL2 changes
- No production systems or credentials
- All services bound to localhost
- Synthetic data clearly identified
- No modification of existing projects

## Architecture Limitations
Logical branches do not represent real remote sites.
Simulated latency is not actual WAN latency.
This is not a licensed ThousandEyes deployment.
