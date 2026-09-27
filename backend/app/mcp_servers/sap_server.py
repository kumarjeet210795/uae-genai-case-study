import os
from mcp.server import MCPServer

mcp = MCPServer("sap-s4hana-demo", instructions="Mock SAP S/4HANA tools for the enterprise demo.")

INVOICES = {
    "INV-1001": {"invoice_id": "INV-1001", "status": "Approved", "last_update": "2026-09-25"},
    "INV-1002": {"invoice_id": "INV-1002", "status": "In Review", "last_update": "2026-09-24"},
}

@mcp.tool()
def get_invoice_status(invoice_id: str) -> dict:
    """Return the status of an invoice."""
    return INVOICES.get(
        invoice_id,
        {"invoice_id": invoice_id, "status": "Not Found", "last_update": None},
    )

@mcp.tool()
def create_purchase_request(amount: float, currency: str, description: str) -> dict:
    """Create a mock purchase request after the application approval gate."""
    return {
        "request_id": "PR-DEMO-1001",
        "status": "Submitted",
        "amount": amount,
        "currency": currency,
        "description": description,
    }

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.getenv("MCP_PORT", "8001")),
    )

