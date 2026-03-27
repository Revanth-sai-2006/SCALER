from __future__ import annotations

from .models import GraderResult
from .tasks import TASKS


def grade_task(task_id: str, processed: dict[str, dict]) -> GraderResult:
    spec = TASKS[task_id]

    classification_total = 0.0
    priority_total = 0.0
    reply_total = 0.0
    close_total = 0.0

    for email in spec.emails:
        gold = spec.labels[email.email_id]
        got = processed.get(email.email_id, {})

        if got.get("queue") == gold.queue:
            classification_total += 1.0

        prio = got.get("priority")
        if isinstance(prio, int):
            priority_total += max(0.0, 1.0 - (abs(prio - gold.priority) / 4.0))

        msg = (got.get("reply") or "").lower()
        match_count = sum(1 for kw in gold.reply_keywords if kw in msg)
        reply_total += match_count / max(1, len(gold.reply_keywords))

        if got.get("closed", False):
            close_total += 1.0

    n = len(spec.emails)
    detail = {
        "classification": classification_total / n,
        "priority": priority_total / n,
        "reply_quality": reply_total / n,
        "closure": close_total / n,
    }
    score = (
        0.45 * detail["classification"]
        + 0.20 * detail["priority"]
        + 0.25 * detail["reply_quality"]
        + 0.10 * detail["closure"]
    )
    score = max(0.0, min(1.0, score))

    return GraderResult(task_id=task_id, score=score, detail=detail)
