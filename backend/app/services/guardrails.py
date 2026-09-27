import re
from dataclasses import dataclass
from typing import Any

try:
    from presidio_analyzer import AnalyzerEngine
except Exception:
    AnalyzerEngine = None


INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?system\s+messages",
    r"reveal\s+(your|the)\s+(system|developer)\s+prompt",
    r"developer\s+message",
    r"jailbreak",
    r"do\s+anything\s+now",
    r"act\s+as\s+an?\s+unrestricted",
    r"disable\s+(your\s+)?safety",
    r"bypass\s+(security|policy|authorization)",
    r"follow\s+these\s+instructions\s+instead",
]

SECRET_PATTERNS = [
    r"(?i)api[_-]?key\s*[:=]\s*[A-Za-z0-9_\-]{12,}",
    r"(?i)bearer\s+[A-Za-z0-9\-_\.]{20,}",
    r"(?i)password\s*[:=]\s*\S+",
]


@dataclass
class Decision:
    allowed: bool
    reason: str
    checks: list[str]


def detect_direct_injection(text: str) -> list[str]:
    hits = []
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            hits.append(pattern)
    return hits


def detect_secrets(text: str) -> list[str]:
    return [p for p in SECRET_PATTERNS if re.search(p, text)]


def scan_user_input(text: str) -> Decision:
    checks = ["length", "unicode-normalization", "direct-injection", "secret-scan"]
    if len(text) > 8000:
        return Decision(False, "Input exceeds 8,000 characters", checks)

    injection_hits = detect_direct_injection(text)
    if injection_hits:
        return Decision(False, "Potential direct prompt injection detected", checks)

    if detect_secrets(text):
        return Decision(False, "Potential secret material detected in input", checks)

    return Decision(True, "Input accepted", checks)


def scan_untrusted_context(text: str) -> Decision:
    checks = ["indirect-injection", "context-isolation", "secret-scan"]
    if detect_direct_injection(text):
        return Decision(
            False,
            "Potential indirect prompt injection found in retrieved content",
            checks,
        )
    if detect_secrets(text):
        return Decision(False, "Potential secret material found in retrieved content", checks)
    return Decision(True, "Retrieved context accepted as data", checks)


def scan_output(text: str) -> Decision:
    checks = ["output-secret-scan", "basic-safety"]
    if detect_secrets(text):
        return Decision(False, "Potential secret material detected in model output", checks)
    return Decision(True, "Output accepted", checks)

