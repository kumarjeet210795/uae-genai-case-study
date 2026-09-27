import os
from mcp.server import MCPServer

mcp = MCPServer("internal-rest-demo", instructions="Mock wrapper around internal REST APIs.")

@mcp.tool()
def get_employee_profile(user_id: str) -> dict:
    """Return a minimal employee profile from a mock internal API."""
    return {
        "user_id": user_id,
        "employment_status": "Active",
        "location": "UAE",
    }

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.getenv("MCP_PORT", "8004")),
    )

