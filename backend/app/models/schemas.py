from typing import Any, Literal
from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: str
    name: str
    department: str
    groups: list[str] = []


class LoginRequest(BaseModel):
    username: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class Citation(BaseModel):
    document_id: str
    title: str
    department: str
    source: str
    chunk_id: str


class GuardrailDecision(BaseModel):
    allowed: bool
    reason: str
    checks: list[str] = []


class ToolCall(BaseModel):
    server: str
    tool: str
    arguments: dict[str, Any] = {}


class Approval(BaseModel):
    approval_id: str
    action: str
    tool: ToolCall
    status: Literal["PENDING", "APPROVED", "REJECTED"]
    requester: str


class ChatResponse(BaseModel):
    answer: str
    grounded: bool
    citations: list[Citation] = []
    guardrails: list[GuardrailDecision] = []
    tool_calls: list[ToolCall] = []
    approval: Approval | None = None
    trace_id: str



class ApprovalDecision(BaseModel):
    decision: Literal["approve", "reject"]
