"""Baseline inference script for the Email Triage OpenEnv.

Uses OpenAI client when API credentials are available and falls back to
heuristics to remain runnable in offline validation.
"""

from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

from openenv_email_triage.env import EmailTriageEnv
from openenv_email_triage.grading import grade_task
from openenv_email_triage.models import Action, EmailItem


def _build_client() -> OpenAI | None:
    api_base = os.getenv("API_BASE_URL")
    api_key = os.getenv("HF_TOKEN")
    if not api_base or not api_key:
        return None
    return OpenAI(base_url=api_base, api_key=api_key)


def _heuristic_plan(email: EmailItem) -> tuple[str, int, str]:
    text = (email.subject + " " + email.body).lower()
    if any(k in text for k in ["oauth", "exfiltration", "unknown ip", "suspicious"]):
        return "security", 5, "We escalated this to security incident investigation immediately."
    if any(k in text for k in ["pricing", "enterprise", "evaluation", "sso", "soc2", "demo"]):
        return "sales", 3, "Thanks for interest in enterprise pricing; we can schedule a demo."
    if any(k in text for k in ["win crypto", "followers instantly", "guaranteed"]):
        return "spam", 1, "This sender is blocked as unsafe spam content."
    if "refund" in text:
        return "support", 4, "Support will process the refund and follow up quickly."
    if "invoice" in text:
        return "support", 3, "Support is checking invoice access and will share an update."
    return "support", 4, "We can help with this login issue today."


def _llm_or_heuristic(client: OpenAI | None, model: str, email: EmailItem) -> tuple[str, int, str]:
    if client is None:
        return _heuristic_plan(email)

    prompt = {
        "subject": email.subject,
        "body": email.body,
        "allowed_queues": ["support", "sales", "security", "spam"],
        "priority_scale": "1(low)-5(critical)",
        "return_json": {"queue": "str", "priority": "int", "reply": "str"},
    }
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {"role": "system", "content": "You are an email triage assistant. Output strict JSON only."},
                {"role": "user", "content": json.dumps(prompt)},
            ],
        )
        content = response.choices[0].message.content or "{}"
        parsed: dict[str, Any] = json.loads(content)
        queue = str(parsed.get("queue", "support"))
        priority = int(parsed.get("priority", 3))
        reply = str(parsed.get("reply", "We are reviewing your request."))
        if queue not in {"support", "sales", "security", "spam"}:
            return _heuristic_plan(email)
        return queue, min(5, max(1, priority)), reply
    except Exception:
        return _heuristic_plan(email)


def run_task(task_id: str, client: OpenAI | None, model: str) -> dict[str, Any]:
    env = EmailTriageEnv(task_id=task_id)
    obs = env.reset(task_id=task_id)

    for email in obs.inbox:
        queue, priority, reply = _llm_or_heuristic(client, model, email)
        env.step(Action(action_type="classify_email", email_id=email.email_id, predicted_queue=queue, priority=priority))
        env.step(Action(action_type="draft_reply", email_id=email.email_id, message=reply))
        env.step(Action(action_type="close_email", email_id=email.email_id))

    grader = grade_task(task_id, env.state().processed)
    return {"task": task_id, "score": grader.score, "detail": grader.detail}


def main() -> None:
    client = _build_client()
    model = os.getenv("MODEL_NAME", "gpt-4o-mini")

    results = [run_task(task, client, model) for task in ["easy", "medium", "hard"]]
    avg = sum(item["score"] for item in results) / len(results)

    print(json.dumps({"results": results, "average_score": avg}, indent=2))


if __name__ == "__main__":
    main()
