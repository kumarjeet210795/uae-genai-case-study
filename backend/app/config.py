import os

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OPA_URL = os.getenv("OPA_URL", "http://localhost:8181")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
DEMO_JWT_SECRET = os.getenv("DEMO_JWT_SECRET", "change-me-demo-only")
DATABASE_URL = os.getenv("DATABASE_URL", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
MCP_URLS = {
    "sap": os.getenv("MCP_SAP_URL", "http://localhost:8001/mcp"),
    "servicenow": os.getenv("MCP_SERVICENOW_URL", "http://localhost:8002/mcp"),
    "d365": os.getenv("MCP_D365_URL", "http://localhost:8003/mcp"),
    "rest": os.getenv("MCP_REST_URL", "http://localhost:8004/mcp"),
}
COLLECTION = "enterprise_policies"
# Multilingual open model: useful for English + Arabic demo traffic.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
