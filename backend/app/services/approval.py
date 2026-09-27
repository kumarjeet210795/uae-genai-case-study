from typing import Any
from .storage import save_approval, get_approval, update_approval
from .audit import audit
from .mcp_gateway import MCPGateway


def create_pending(approval: dict[str, Any], trace_id: str) -> None:
    save_approval(approval)
    audit("approval_created", trace_id=trace_id, approval_id=approval["approval_id"], requester=approval["requester"])


async def decide(approval_id: str, user: dict[str, Any], decision: str) -> dict[str, Any]:
    approval = get_approval(approval_id)
    if not approval:
        raise KeyError("Approval not found")
    if approval["requester"] != user["user_id"] and "admins" not in user.get("groups", []):
        raise PermissionError("Only the requester or an admin can decide this approval")
    if approval["status"] != "PENDING":
        raise ValueError("Approval is already decided")

    if decision == "reject":
        update_approval(approval_id, "REJECTED")
        audit("approval_rejected", approval_id=approval_id, user=user["user_id"])
        return {**approval, "status": "REJECTED"}

    gateway = MCPGateway()
    tool = approval["tool"]
    result = await gateway.call(user, tool["server"], tool["tool"], tool["arguments"], approved=True)
    update_approval(approval_id, "APPROVED")
    audit("approval_approved_and_executed", approval_id=approval_id, user=user["user_id"], result=str(result))
    return {**approval, "status": "APPROVED", "result": gateway.result_to_json(result)}
