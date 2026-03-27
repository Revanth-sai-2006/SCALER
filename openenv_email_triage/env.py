from __future__ import annotations

from copy import deepcopy

from .grading import grade_task
from .models import Action, Observation, Reward, State, StepInfo, StepResult
from .tasks import TASKS, TaskSpec


class EmailTriageEnv:
    def __init__(self, task_id: str = "easy") -> None:
        self._task: TaskSpec = TASKS[task_id]
        self._step_count = 0
        self._done = False
        self._processed: dict[str, dict] = {}
        self._cumulative_reward = 0.0

    def reset(self, task_id: str | None = None) -> Observation:
        if task_id is not None:
            self._task = TASKS[task_id]
        self._step_count = 0
        self._done = False
        self._processed = {}
        self._cumulative_reward = 0.0
        return self._observation()

    def step(self, action: Action) -> StepResult:
        if self._done:
            return StepResult(
                observation=self._observation(),
                reward=Reward(value=0.0, components={"episode_done": 0.0}),
                done=True,
                info=StepInfo(valid_action=False, message="Episode already complete.", score_so_far=self.score()),
            )

        reward = 0.0
        components: dict[str, float] = {}
        valid = True
        msg = "ok"

        if action.email_id not in self._labels:
            valid = False
            reward -= 0.2
            components["invalid_email"] = -0.2
            msg = f"Unknown email_id={action.email_id}"
        else:
            item = self._processed.setdefault(action.email_id, {})
            gold = self._labels[action.email_id]

            if action.action_type == "classify_email":
                if action.predicted_queue is None or action.priority is None:
                    valid = False
                    reward -= 0.15
                    components["missing_fields"] = -0.15
                    msg = "classify_email requires predicted_queue and priority"
                else:
                    item["queue"] = action.predicted_queue
                    item["priority"] = action.priority

                    q_reward = 0.25 if action.predicted_queue == gold.queue else -0.10
                    p_reward = 0.15 * max(0.0, 1.0 - (abs(action.priority - gold.priority) / 4.0))
                    reward += q_reward + p_reward
                    components["queue"] = q_reward
                    components["priority"] = p_reward

            elif action.action_type == "draft_reply":
                if not action.message:
                    valid = False
                    reward -= 0.10
                    components["missing_message"] = -0.10
                    msg = "draft_reply requires non-empty message"
                else:
                    lower = action.message.lower()
                    item["reply"] = action.message
                    keyword_hits = sum(1 for kw in gold.reply_keywords if kw in lower)
                    reply_reward = 0.2 * (keyword_hits / max(1, len(gold.reply_keywords)))
                    if "password" in lower and gold.queue == "security":
                        reply_reward -= 0.1
                    reward += reply_reward
                    components["reply"] = reply_reward

            elif action.action_type == "close_email":
                item["closed"] = True
                close_reward = 0.08
                reward += close_reward
                components["close"] = close_reward

        self._step_count += 1

        if self._step_count >= self._task.max_steps:
            self._done = True
            final_score = self.score()
            terminal_bonus = final_score - 0.5
            reward += terminal_bonus
            components["terminal_bonus"] = terminal_bonus
            msg = f"max_steps reached, final_score={final_score:.3f}"

        self._cumulative_reward += reward

        return StepResult(
            observation=self._observation(),
            reward=Reward(value=max(-1.0, min(1.0, reward)), components=components),
            done=self._done,
            info=StepInfo(valid_action=valid, message=msg, score_so_far=self.score()),
        )

    def state(self) -> State:
        return State(
            task_id=self._task.task_id,
            step_count=self._step_count,
            max_steps=self._task.max_steps,
            done=self._done,
            processed=deepcopy(self._processed),
            cumulative_reward=self._cumulative_reward,
            score=self.score(),
        )

    def score(self) -> float:
        return grade_task(self._task.task_id, self._processed).score

    @property
    def _labels(self):
        return self._task.labels

    def _observation(self) -> Observation:
        return Observation(
            task_id=self._task.task_id,
            step_count=self._step_count,
            max_steps=self._task.max_steps,
            inbox=list(self._task.emails),
            processed_email_ids=sorted(self._processed.keys()),
            done=self._done,
        )
