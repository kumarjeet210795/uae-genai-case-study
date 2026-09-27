from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from .auth import USERS, issue_token, get_current_user
from .models.schemas import LoginRequest, TokenResponse, ChatRequest, ChatResponse, User, ApprovalDecision
from .services.orchestrator import AgentOrchestrator
from .services.rag import RAGService
from .services.audit import audit
from .services.storage import init_db, get_approval
from .services.approval import decide

app = FastAPI(
    title="UAE Enterprise GenAI Assistant — Open Source Demo",
    version="1.0.0",
    description="Production-shaped open-source reference implementation of the UAE enterprise GenAI case study.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

orchestrator: AgentOrchestrator | None = None

@app.on_event("startup")
async def startup():
    global orchestrator
    init_db()
    orchestrator = AgentOrchestrator()
    documents_dir = Path(__file__).resolve().parent.parent / "data" / "documents"
    count = orchestrator.rag.ingest_seed_documents(str(documents_dir))
    audit("service_started", indexed_chunks=count)

@app.get("/health")
async def health():
    return {"status": "ok", "architecture": "open-source enterprise GenAI reference demo"}

@app.post("/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    user = USERS.get(req.username.lower())
    if not user:
        raise HTTPException(status_code=401, detail="Unknown demo user")
    return TokenResponse(access_token=issue_token(user), user=user)

@app.get("/me", response_model=User)
async def me(user: User = Depends(get_current_user)):
    return user

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, user: User = Depends(get_current_user)):
    return await orchestrator.run(user, req.message, req.conversation_id)  # type: ignore[union-attr]

@app.get("/mcp/tools")
async def mcp_tools(user: User = Depends(get_current_user)):
    return await orchestrator.mcp.list_tools()  # type: ignore[union-attr]

@app.get("/approvals/{approval_id}")
async def approval_status(approval_id: str, user: User = Depends(get_current_user)):
    approval = get_approval(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    if approval["requester"] != user.user_id and "admins" not in user.groups:
        raise HTTPException(status_code=403, detail="Not allowed to view this approval")
    return approval

@app.post("/approvals/{approval_id}/decision")
async def approval_decision(approval_id: str, req: ApprovalDecision, user: User = Depends(get_current_user)):
    try:
        return await decide(approval_id, user.model_dump(), req.decision)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

@app.post("/admin/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    department: str = Form("general"),
    sensitivity: str = Form("internal"),
    allowed_groups: str = Form("employees"),
    user: User = Depends(get_current_user),
):
    if "admins" not in user.groups:
        raise HTTPException(status_code=403, detail="Admin group required")
    allowed = [x.strip() for x in allowed_groups.split(",") if x.strip()]
    tmp = Path("/tmp") / file.filename
    tmp.write_bytes(await file.read())
    try:
        count = orchestrator.rag.ingest_file(tmp, {"department": department, "sensitivity": sensitivity, "allowed_groups": allowed})  # type: ignore[union-attr]
    finally:
        tmp.unlink(missing_ok=True)
    audit("document_ingested", user=user.user_id, filename=file.filename, chunks=count)
    return {"filename": file.filename, "chunks": count, "allowed_groups": allowed}
