# Observability

The demo emits structured audit events through `backend/app/services/audit.py`.

For production:

- instrument FastAPI, Qdrant calls, Ollama/model calls and MCP calls with OpenTelemetry
- export traces to an OTLP collector
- metrics to Prometheus
- dashboards in Grafana
- logs to Loki or Elasticsearch
- security events to the organization's SIEM

Important trace attributes:

- trace_id
- user_id
- department
- request_id
- model
- prompt_hash
- retrieval_count
- document_ids
- tool_server
- tool_name
- tool_risk
- approval_id
- approval_status
- latency_ms

