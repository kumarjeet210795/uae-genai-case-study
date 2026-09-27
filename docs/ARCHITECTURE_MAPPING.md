# Architecture-to-Code Mapping

This demo intentionally follows the supplied client target architecture but swaps licensed Azure services for open-source components.

| Diagram block | Demo component | Runtime boundary |
|---|---|---|
| Employee Experience | `frontend/` | Browser |
| Identity / SSO | `backend/app/auth.py` | API security |
| API Management | `backend/app/main.py` | FastAPI gateway |
| AI Security & Guardrails | `backend/app/services/guardrails.py` | Input/context/output |
| Agent Orchestrator | `backend/app/services/orchestrator.py` | Intent/workflow routing |
| LLM Gateway | `backend/app/services/llm.py` | Model abstraction |
| RAG Service | `backend/app/services/rag.py` | Retrieval |
| Qdrant | `qdrant` Compose service | Vector + ACL payload |
| MCP Tool Gateway | `backend/app/services/mcp_gateway.py` | Tool security |
| OPA | `opa` Compose service | Authorization policy |
| MCP Servers | `backend/app/mcp_servers/` | Enterprise adapters |
| Human Approval | `backend/app/services/approval.py` + frontend | Transaction control |
| PostgreSQL | `postgres` Compose service | Approval metadata |
| Redis | `redis` Compose service | Reserved for session/cache extension |
| Audit / Observability | `backend/app/services/audit.py` | Trace/audit events |
| CI/CD / Containerization | Docker Compose + Dockerfiles | Local deployment |

## Trust boundaries

1. Browser → API: authenticated request.
2. API → Agent: normalized user identity and policy context.
3. Agent → RAG: query + user groups; no unrestricted document access.
4. RAG → model: only ACL-approved context.
5. Agent → MCP: tool request; gateway applies allowlist/risk/OPA.
6. Write tool → enterprise system: only after application-level approval.
7. Every sensitive path → audit event.

## Open-source substitutions

- Microsoft Entra ID → local demo JWT / Keycloak-compatible OIDC boundary
- Azure API Management → FastAPI gateway; Kong/Traefik can be added at the edge
- Azure AI Search → Qdrant + application lexical/RRF layer
- Azure OpenAI / Foundry → Ollama + Qwen2.5 3B; vLLM is the recommended GPU-scale replacement
- Microsoft Agent Framework → Python orchestrator; LangGraph can be introduced without changing the surrounding boundaries
- Key Vault → Vault in a production OSS deployment
- Azure Monitor / App Insights → OpenTelemetry + Prometheus/Grafana/Loki/Tempo/SIEM
- Azure DevOps → GitHub Actions/GitLab/Jenkins
- Azure Container Apps/AKS → Kubernetes/K3s or a managed Kubernetes platform
