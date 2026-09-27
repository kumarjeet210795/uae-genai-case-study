from typing import Any
from mcp import Client

from ..config import MCP_URLS
from .opa import authorize
from .audit import audit

RISK = {
    "get_invoice_status": "LOW",
    "get_it_case_status": "LOW",
    "get_employee_profile": "LOW",
    "get_d365_case": "LOW",
    "create_it_request": "MEDIUM",
    "create_purchase_request": "HIGH",
}


class MCPGateway:
    async def list_tools(self):
        result = {}
        for name, url in MCP_URLS.items():
            try:
                async with Client(url) as client:
                    page = await client.list_tools()
                    result[name] = [t.name for t in page.tools]
            except Exception as exc:
                result[name] = [f"unavailable: {exc}"]
        return result

    async def call(self, user: dict, server: str, tool: str, arguments: dict[str, Any], approved: bool = False):
        if server not in MCP_URLS:
            raise PermissionError("Unknown MCP server")
        risk = RISK.get(tool, "HIGH")
        action = "read" if risk == "LOW" else "write"
        if action == "write" and not approved:
            raise PermissionError("Write tool requires an application-level approval")
        if not await authorize(user, action, tool, risk):
            raise PermissionError(f"Policy denied {action} on {tool}")
        audit("mcp_tool_call", user=user["user_id"], server=server, tool=tool, arguments=arguments, risk=risk, approved=approved)
        async with Client(MCP_URLS[server]) as client:
            return await client.call_tool(tool, arguments)

    @staticmethod
    def result_to_json(result: Any):
        if getattr(result, "structured_content", None):
            return result.structured_content
        parts = getattr(result, "content", []) or []
        values = []
        for p in parts:
            values.append(getattr(p, "text", str(p)))
        return values
