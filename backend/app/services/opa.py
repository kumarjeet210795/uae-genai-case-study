import httpx
from ..config import OPA_URL


async def authorize(user: dict, action: str, resource: str, risk: str = "LOW") -> bool:
    payload = {
        "input": {
            "user": user,
            "action": action,
            "resource": resource,
            "risk": risk,
        }
    }
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.post(
                f"{OPA_URL}/v1/data/enterprise/authz",
                json=payload,
            )
            r.raise_for_status()
            return bool(r.json().get("result", {}).get("allow", False))
    except Exception:
        # Secure failure mode: deny if policy engine is unavailable.
        return False

