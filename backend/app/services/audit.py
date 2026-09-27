import json
import logging
import time
from pathlib import Path

logger = logging.getLogger("audit")
logging.basicConfig(level=logging.INFO)

AUDIT_FILE = Path("/app/data/audit.log")


def audit(event: str, **fields):
    record = {
        "timestamp": time.time(),
        "event": event,
        **fields,
    }
    logger.info("AUDIT %s", json.dumps(record, default=str))
    try:
        AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
    except OSError:
        pass

