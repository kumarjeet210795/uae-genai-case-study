"""Small persistence layer for demo approvals and session metadata.

PostgreSQL is used when DATABASE_URL is available. The service retries on startup
and falls back to in-memory state for a laptop demo so the application remains easy
 to run. Production should use managed PostgreSQL/HA and Redis as shown in the
reference architecture.
"""
import json
import os
import time
from typing import Any

APPROVALS: dict[str, dict[str, Any]] = {}

DATABASE_URL = os.getenv("DATABASE_URL", "")

try:
    import psycopg
    from psycopg.types.json import Json
except Exception:  # pragma: no cover
    psycopg = None


def init_db() -> None:
    if not DATABASE_URL or psycopg is None:
        return
    for _ in range(20):
        try:
            with psycopg.connect(DATABASE_URL) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS approvals (
                        approval_id TEXT PRIMARY KEY,
                        requester TEXT NOT NULL,
                        status TEXT NOT NULL,
                        tool_json JSONB NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT now(),
                        decided_at TIMESTAMPTZ
                    )
                """)
                conn.commit()
            return
        except Exception:
            time.sleep(1)


def save_approval(approval: dict[str, Any]) -> None:
    APPROVALS[approval["approval_id"]] = approval
    if not DATABASE_URL or psycopg is None:
        return
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            conn.execute(
                """INSERT INTO approvals(approval_id, requester, status, tool_json)
                   VALUES (%s,%s,%s,%s)
                   ON CONFLICT (approval_id) DO UPDATE SET status=EXCLUDED.status, tool_json=EXCLUDED.tool_json""",
                (approval["approval_id"], approval["requester"], approval["status"], Json(approval["tool"])),
            )
            conn.commit()
    except Exception:
        pass


def get_approval(approval_id: str) -> dict[str, Any] | None:
    if approval_id in APPROVALS:
        return APPROVALS[approval_id]
    if not DATABASE_URL or psycopg is None:
        return None
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            row = conn.execute(
                "SELECT approval_id, requester, status, tool_json FROM approvals WHERE approval_id=%s",
                (approval_id,),
            ).fetchone()
        if not row:
            return None
        value = {"approval_id": row[0], "requester": row[1], "status": row[2], "tool": row[3]}
        APPROVALS[approval_id] = value
        return value
    except Exception:
        return None


def update_approval(approval_id: str, status: str) -> dict[str, Any] | None:
    value = get_approval(approval_id)
    if not value:
        return None
    value["status"] = status
    APPROVALS[approval_id] = value
    if DATABASE_URL and psycopg is not None:
        try:
            with psycopg.connect(DATABASE_URL) as conn:
                conn.execute("UPDATE approvals SET status=%s, decided_at=now() WHERE approval_id=%s", (status, approval_id))
                conn.commit()
        except Exception:
            pass
    return value
