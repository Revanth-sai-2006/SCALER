from __future__ import annotations

from fastapi import FastAPI

from .env import EmailTriageEnv
from .models import Action, ResetRequest, State, StepResult

app = FastAPI(title="Email Triage OpenEnv", version="1.0.0")
env = EmailTriageEnv(task_id="easy")


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "message": "Email Triage OpenEnv"}


@app.post("/reset")
def reset(payload: ResetRequest | None = None):
    task_id = payload.task_id if payload else None
    return env.reset(task_id=task_id)


@app.post("/step", response_model=StepResult)
def step(action: Action) -> StepResult:
    return env.step(action)


@app.get("/state", response_model=State)
def state() -> State:
    return env.state()


@app.get("/tasks")
def tasks() -> dict[str, list[str]]:
    return {"tasks": ["easy", "medium", "hard"]}
