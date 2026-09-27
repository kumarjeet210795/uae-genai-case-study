#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -x "$ROOT_DIR/qdrant/qdrant" ]]; then
  echo "Missing Qdrant binary: qdrant/qdrant" >&2
  exit 1
fi
if [[ ! -x "$ROOT_DIR/opa" ]]; then
  echo "Missing OPA binary: ./opa" >&2
  exit 1
fi
if [[ ! -x "$ROOT_DIR/ollama/runtime/bin/ollama" ]]; then
  echo "Missing Ollama runtime: ollama/runtime/bin/ollama" >&2
  exit 1
fi
if [[ ! -x "$ROOT_DIR/.venv/bin/python" || ! -x "$ROOT_DIR/.venv/bin/uvicorn" ]]; then
  echo "Missing backend environment: .venv" >&2
  exit 1
fi
if [[ ! -x "$ROOT_DIR/frontend/node_modules/.bin/vite" ]]; then
  echo "Missing frontend dependencies: run npm install in frontend/" >&2
  exit 1
fi

PIDS=()
port_is_open() {
  python3 -c 'import socket,sys; s=socket.socket(); s.settimeout(.25); result=s.connect_ex(("127.0.0.1", int(sys.argv[1]))); s.close(); sys.exit(0 if result == 0 else 1)' "$1"
}
start_or_reuse() {
  local name="$1"
  local port="$2"
  shift 2
  if port_is_open "$port"; then
    echo "$name already listening on port $port; reusing it"
  else
    echo "Starting $name on port $port"
    "$@" &
    PIDS+=("$!")
  fi
}
cleanup() {
  trap - INT TERM EXIT
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
  for pid in "${PIDS[@]}"; do
    wait "$pid" 2>/dev/null || true
  done
}
trap cleanup INT TERM EXIT

mkdir -p "$ROOT_DIR/qdrant/storage"
start_or_reuse "Qdrant" 6333 env QDRANT__STORAGE__STORAGE_PATH="$ROOT_DIR/qdrant/storage" "$ROOT_DIR/qdrant/qdrant"
start_or_reuse "OPA" 8181 "$ROOT_DIR/opa" run --server --addr=0.0.0.0:8181 "$ROOT_DIR/backend/policies"
start_or_reuse "Ollama" 11434 env OLLAMA_MODELS="$ROOT_DIR/ollama/models" "$ROOT_DIR/ollama/runtime/bin/ollama" serve
start_or_reuse "SAP MCP" 8001 env PYTHONPATH="$ROOT_DIR/backend" MCP_PORT=8001 "$ROOT_DIR/.venv/bin/python" -m app.mcp_servers.sap_server
start_or_reuse "ServiceNow MCP" 8002 env PYTHONPATH="$ROOT_DIR/backend" MCP_PORT=8002 "$ROOT_DIR/.venv/bin/python" -m app.mcp_servers.servicenow_server
start_or_reuse "Dynamics 365 MCP" 8003 env PYTHONPATH="$ROOT_DIR/backend" MCP_PORT=8003 "$ROOT_DIR/.venv/bin/python" -m app.mcp_servers.d365_server
start_or_reuse "REST MCP" 8004 env PYTHONPATH="$ROOT_DIR/backend" MCP_PORT=8004 "$ROOT_DIR/.venv/bin/python" -m app.mcp_servers.rest_server
start_or_reuse "Backend" 8000 env QDRANT_URL=http://localhost:6333 OPA_URL=http://localhost:8181 OLLAMA_URL=http://localhost:11434 MCP_SAP_URL=http://localhost:8001/mcp MCP_SERVICENOW_URL=http://localhost:8002/mcp MCP_D365_URL=http://localhost:8003/mcp MCP_REST_URL=http://localhost:8004/mcp "$ROOT_DIR/.venv/bin/uvicorn" app.main:app --app-dir "$ROOT_DIR/backend" --host 0.0.0.0 --port 8000
start_or_reuse "Frontend" 5173 env VITE_API_URL=http://localhost:8000 "$ROOT_DIR/frontend/node_modules/.bin/vite" --host 0.0.0.0

echo "Local stack is up. Frontend: http://localhost:5173  Backend: http://localhost:8000/docs  Qdrant: http://localhost:6333"
echo "Press Ctrl+C to stop the processes started by this script."
wait
