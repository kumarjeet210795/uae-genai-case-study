"""
Minimal smoke test.

Run after docker compose up:
    python scripts/test_api.py
"""
import requests

BASE = "http://localhost:8000"

r = requests.post(f"{BASE}/auth/login", json={"username": "alice"})
r.raise_for_status()
data = r.json()
token = data["access_token"]

r = requests.post(
    f"{BASE}/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={"message": "What is the procurement policy for purchases above AED 10000?"},
)
r.raise_for_status()
print(r.json())

