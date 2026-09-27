import os
from mcp.server import MCPServer

mcp = MCPServer("servicenow-demo", instructions="Mock ServiceNow tools for the enterprise demo.")

@mcp.tool()
def get_it_case_status(case_id: str) -> dict:
    """Return a mock ServiceNow case status."""
    return {
        "case_id": case_id,
        "status": "In Progress",
        "assignment_group": "IT Service Desk",
        "last_update": "2026-09-26",
    }

@mcp.tool()
def create_it_request(summary: str, description: str) -> dict:
    """Create a mock IT request."""
    return {
        "case_id": "INC-DEMO-2001",
        "status": "New",
        "summary": summary,
        "description": description,
        "assignment_group": "IT Service Desk",
    }

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.getenv("MCP_PORT", "8002")),
    )

