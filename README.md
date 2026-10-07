# IronMind AI

IronMind AI is an autonomous cyber-defense prototype built around
machine-learning anomaly detection and automated response workflows.

## Architecture

```text
Endpoint ─────────────┐
                      │
Network ──────────────┼──> Feature Extraction
                      │
USB Agent ────────────┘
                            │
                            ▼
                    ML Anomaly Detection
                       IsolationForest
                            │
                            ▼
                      Anomaly Score
                            │
                            ▼
                    Threat Classification
                            │
                            ▼
                    Autonomous Response
                       /           \
                      /             \
               Quarantine        Isolation
                      \             /
                       \           /
                         ▼         ▼
                       Forensic Report
