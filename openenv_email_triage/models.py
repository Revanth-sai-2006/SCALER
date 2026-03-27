from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class EmailItem(BaseModel):
    email_id: str
    from_address: str
    subject: str
    body: str


class Observation(BaseModel):
    task_id: str
    step_count: int
    max_steps: int
    inbox: list[EmailItem]
    processed_email_ids: list[str]
    done: bool


class Action(BaseModel):
    action_type: Literal["classify_email", "draft_reply", "close_email"]
    email_id: str = Field(min_length=1)
    predicted_queue: Literal["support", "sales", "security", "spam"] | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    message: str | None = None


class Reward(BaseModel):
    value: float = Field(ge=-1.0, le=1.0)
    components: dict[str, float]


class StepInfo(BaseModel):
    valid_action: bool
    message: str
    score_so_far: float = Field(ge=0.0, le=1.0)


class StepResult(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: StepInfo


class State(BaseModel):
    task_id: str
    step_count: int
    max_steps: int
    done: bool
    processed: dict[str, dict[str, Any]]
    cumulative_reward: float
    score: float = Field(ge=0.0, le=1.0)


class ResetRequest(BaseModel):
    task_id: Literal["easy", "medium", "hard"] | None = None


class GraderResult(BaseModel):
    task_id: str
    score: float = Field(ge=0.0, le=1.0)
    detail: dict[str, float]
