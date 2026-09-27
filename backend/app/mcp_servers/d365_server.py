import os
from mcp.server import MCPServer

mcp = MCPServer("dynamics365-demo", instructions="Mock Dynamics 365 tools for the enterprise demo.")

@mcp.tool()
def get_d365_case(case_id: str) -> dict:
    """Return a mock Dynamics 365 case."""
    return {
        "case_id": case_id,
        "status": "Open",
        "owner": "Corporate Services",
        "last_update": "2026-09-25",
    }

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.getenv("MCP_PORT", "8003")),
    )

