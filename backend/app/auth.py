from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .config import DEMO_JWT_SECRET
from .models.schemas import User

USERS = {
    "alice": User(user_id="alice", name="Alice Finance", department="finance",
                  groups=["finance", "employees"]),
    "bob": User(user_id="bob", name="Bob IT", department="it",
                groups=["it", "employees"]),
    "carol": User(user_id="carol", name="Carol Procurement", department="procurement",
                  groups=["procurement", "employees"]),
    "dave": User(user_id="dave", name="Dave HR", department="hr",
                 groups=["hr", "employees"]),
    "erin": User(user_id="erin", name="Erin Platform Admin", department="platform",
                 groups=["admins", "employees"]),
}

security = HTTPBearer(auto_error=False)


def issue_token(user: User) -> str:
    payload = {
        "sub": user.user_id,
        "name": user.name,
        "department": user.department,
        "groups": user.groups,
        "exp": datetime.now(timezone.utc) + timedelta(hours=2),
    }
    return jwt.encode(payload, DEMO_JWT_SECRET, algorithm="HS256")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Bearer token required")
    try:
        payload = jwt.decode(
            credentials.credentials,
            DEMO_JWT_SECRET,
            algorithms=["HS256"],
        )
        return User(
            user_id=payload["sub"],
            name=payload["name"],
            department=payload["department"],
            groups=payload.get("groups", []),
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

