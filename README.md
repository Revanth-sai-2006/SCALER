# Email Triage OpenEnv (Scaler Hackathon Submission)

This project implements a **real-world customer support email triage environment** compatible with the required OpenEnv workflow (`step()`, `reset()`, `state()`) and designed for agent evaluation.

## Why this is real-world

Support teams triage inbound emails every day: detect spam/phishing, route tickets (support/sales/security), assign priority, draft safe responses, and close resolved items. This environment models that workflow with deterministic graders.

## Environment design

### Observation space (`Observation`)
- `task_id`: current task (`easy`, `medium`, `hard`)
- `step_count`, `max_steps`
- `inbox`: list of emails (`email_id`, sender, subject, body)
- `processed_email_ids`
- `done`

### Action space (`Action`)
- `classify_email(email_id, predicted_queue, priority)`
- `draft_reply(email_id, message)`
- `close_email(email_id)`

### Reward shaping
Per-step rewards include:
- queue classification correctness
- priority accuracy (distance-based)
- reply keyword quality
- closure completion
- penalties for invalid/missing actions
- terminal bonus based on grader score

This gives continuous learning signal and avoids binary-only terminal rewards.

## Tasks and grader

There are **3 deterministic tasks** with increasing difficulty:
1. **easy**: obvious support/sales/spam triage
2. **medium**: includes security incident handling
3. **hard**: mixed ambiguous intents + spam

Programmatic grader returns score in `[0.0, 1.0]` for each task using weighted components:
- classification: 45%
- priority: 20%
- reply quality: 25%
- closure: 10%

## OpenEnv API

When server is running:
- `POST /reset` with optional `{"task_id": "easy|medium|hard"}`
- `POST /step` with typed `Action`
- `GET /state` returns complete state
- `GET /tasks` lists available tasks

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run locally:

```bash
uvicorn app:app --host 0.0.0.0 --port 7860
```

## Baseline inference (required `inference.py`)

```bash
python inference.py
```

Expected behavior:
- Runs all tasks (`easy`, `medium`, `hard`)
- Outputs per-task score and average score
- Uses OpenAI client for LLM calls if env vars are present
- Falls back to deterministic heuristics if env vars are missing

### Optional environment variables
- `API_BASE_URL`: model API endpoint
- `MODEL_NAME`: model ID (default: `gpt-4o-mini`)
- `HF_TOKEN`: API key/token

## Docker / Hugging Face Space compatibility

Build and run:

```bash
docker build -t email-triage-openenv .
docker run --rm -p 7860:7860 email-triage-openenv
```

The container serves FastAPI on port `7860`, compatible with HF Spaces container deployment.

## Validation checklist mapping

- ✅ real-world task (email triage)
- ✅ typed models for observation/action/reward
- ✅ `step/reset/state` endpoints
- ✅ `openenv.yaml`
- ✅ 3 tasks + graders with `[0.0, 1.0]` scores
- ✅ meaningful reward shaping
- ✅ baseline inference script (`inference.py`)
- ✅ Dockerfile and README documentation
