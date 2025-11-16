from __future__ import annotations

import asyncio
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel

from browser_use import Agent, Browser, ChatBrowserUse

BROWSER_ENDPOINTS: Dict[str, str] = {
    "a": "ws://localhost:9223",  # browseruse_a (docker-compose.multi.yml)
    "b": "ws://localhost:9224",  # browseruse_b
    "c": "ws://localhost:9225",  # browseruse_c
    # Fallback single-browser setup (docker-compose.yml) could be:
    # "default": "ws://localhost:9222",
}

VALID_API_KEYS: set[str] = set()
BROWSER_QUEUE: deque[str] = deque(BROWSER_ENDPOINTS.keys())


def is_api_key_valid(api_key: str | None) -> bool:
    # If no keys configured, treat all keys as valid (dev mode).
    if not VALID_API_KEYS:
        return api_key is not None and api_key != ""
    return api_key in VALID_API_KEYS


class CreateTaskRequest(BaseModel):
    task: str
    llm: Optional[str] = None
    sessionId: Optional[str] = None
    maxSteps: Optional[int] = 100


class SessionCreateRequest(BaseModel):
    browserId: Optional[str] = None


class SessionUpdateRequest(BaseModel):
    action: str


class TaskCreatedResponse(BaseModel):
    id: str
    sessionId: str


class TaskStatus(str):
    STARTED = "started"
    FINISHED = "finished"
    ERROR = "error"


class TaskStepView(BaseModel):
    number: int
    memory: str
    url: str = ""


class TaskView(BaseModel):
    id: str
    sessionId: str
    task: str
    status: str
    output: Optional[str] = None
    steps: List[TaskStepView] = []


class SessionView(BaseModel):
    id: str
    browserId: str
    status: str


@dataclass
class Session:
    id: str
    browser_id: str
    cdp_url: str
    status: str = "active"


@dataclass
class Task:
    id: str
    session_id: str
    task: str
    status: str = TaskStatus.STARTED
    output: Optional[str] = None
    steps: List[TaskStepView] = field(default_factory=list)


# Simple in-memory registries. Replace with DB/Redis for production.
SESSIONS: Dict[str, Session] = {}
TASKS: Dict[str, Task] = {}


app = FastAPI(title="Self-Hosted Browser Use Cloud", version="0.1.0")


async def require_api_key(
    x_browser_use_api_key: Optional[str] = Header(None, alias="X-Browser-Use-API-Key"),
) -> str:
    if not is_api_key_valid(x_browser_use_api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
    return x_browser_use_api_key  # noqa: B008


def _pick_browser_id() -> str:
    if not BROWSER_QUEUE:
        if not BROWSER_ENDPOINTS:
            raise RuntimeError("No BROWSER_ENDPOINTS configured")
        BROWSER_QUEUE.extend(BROWSER_ENDPOINTS.keys())
    browser_id = BROWSER_QUEUE[0]
    BROWSER_QUEUE.rotate(-1)
    return browser_id


def _create_session(preferred_browser: Optional[str] = None) -> Session:
    browser_id = preferred_browser or _pick_browser_id()
    cdp_url = BROWSER_ENDPOINTS.get(browser_id)
    if not cdp_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown browserId")
    session_id = str(uuid.uuid4())
    session = Session(id=session_id, browser_id=browser_id, cdp_url=cdp_url)
    SESSIONS[session_id] = session
    return session


def _get_session(session_id: str) -> Session:
    session = SESSIONS.get(session_id)
    if not session or session.status != "active":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found or inactive")
    return session


@app.get("/api/v2/sessions", response_model=List[SessionView])
async def list_sessions(api_key: str = Depends(require_api_key)) -> List[SessionView]:
    return [SessionView(id=s.id, browserId=s.browser_id, status=s.status) for s in SESSIONS.values()]


@app.post("/api/v2/sessions", response_model=SessionView, status_code=status.HTTP_201_CREATED)
async def create_session(
    body: SessionCreateRequest,
    api_key: str = Depends(require_api_key),
) -> SessionView:
    session = _create_session(body.browserId)
    return SessionView(id=session.id, browserId=session.browser_id, status=session.status)


@app.patch("/api/v2/sessions/{session_id}", response_model=SessionView)
async def update_session(
    session_id: str,
    body: SessionUpdateRequest,
    api_key: str = Depends(require_api_key),
) -> SessionView:
    session = _get_session(session_id)
    if body.action == "stop":
        session.status = "stopped"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported action")
    return SessionView(id=session.id, browserId=session.browser_id, status=session.status)


@app.post("/api/v2/tasks", response_model=TaskCreatedResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_task(
    body: CreateTaskRequest,
    api_key: str = Depends(require_api_key),
) -> TaskCreatedResponse:
    # Resolve or create session
    if body.sessionId:
        session = _get_session(body.sessionId)
    else:
        session = _create_session()

    task_id = str(uuid.uuid4())
    task = Task(id=task_id, session_id=session.id, task=body.task)
    TASKS[task_id] = task

    # Kick off background job
    asyncio.create_task(_run_agent_task(task, session, body))

    return TaskCreatedResponse(id=task.id, sessionId=session.id)


@app.get("/api/v2/tasks/{task_id}", response_model=TaskView)
async def get_task(
    task_id: str,
    api_key: str = Depends(require_api_key),
) -> TaskView:
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return TaskView(
        id=task.id,
        sessionId=task.session_id,
        task=task.task,
        status=task.status,
        output=task.output,
        steps=task.steps,
    )


# ---------------------------------------------------------------------------
# Agent runner
# ---------------------------------------------------------------------------


async def _run_agent_task(task: Task, session: Session, body: CreateTaskRequest) -> None:
    try:
        browser = Browser(cdp_url=session.cdp_url)
        # For now, always use ChatBrowserUse(). You can switch on body.llm if needed.
        llm = ChatBrowserUse()
        agent = Agent(task=task.task, browser=browser, llm=llm)

        history = await agent.run(max_steps=body.maxSteps or 100)

        # Very minimal: just store final_result() as output.
        task.output = history.final_result() if hasattr(history, "final_result") else None
        task.status = TaskStatus.FINISHED
    except Exception as exc:  # noqa: BLE001
        task.status = TaskStatus.ERROR
        task.output = f"error: {type(exc).__name__}: {exc}"


# ---------------------------------------------------------------------------
# Local dev entrypoint (optional)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "examples.api.self_hosted_cloud:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
