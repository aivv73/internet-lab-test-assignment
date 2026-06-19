# Implementation Plan

This plan implements the InternetLab backend-oriented test assignment using the decisions captured in `CONTEXT.md` and `docs/adr/`.

## Phase 1 — Scaffold and tooling

- Create Poetry project: `pyproject.toml`, `poetry.lock`.
- Add backend dependencies: FastAPI, Uvicorn, Pydantic Settings, httpx, email/SMTP helper library if needed.
- Add dev tooling: Ruff, ty, pytest, pytest-asyncio/httpx.
- Add `Makefile` wrappers:
  - `make install`
  - `make dev`
  - `make test`
  - `make lint`
  - `make format`
  - `make typecheck`
  - `make check`
- Add `.env.example` with AI, SMTP, storage, CORS, rate-limit, and metrics settings.

## Phase 2 — Backend skeleton

Target structure:

```text
app/
├── main.py
├── core/
│   ├── config.py
│   ├── errors.py
│   ├── logging.py
│   └── security.py
├── api/routes/
│   ├── contact.py
│   ├── health.py
│   └── metrics.py
├── schemas/
│   ├── ai.py
│   ├── contact.py
│   ├── error.py
│   └── metrics.py
├── services/
│   ├── ai_service.py
│   ├── contact_service.py
│   ├── email_service.py
│   ├── metrics_service.py
│   └── rate_limit_service.py
├── repositories/
│   ├── json_file.py
│   ├── metrics_repository.py
│   ├── outbox_repository.py
│   ├── rate_limit_repository.py
│   └── submission_repository.py
├── handlers/
│   ├── ai_client.py
│   └── smtp_client.py
└── templates/
    ├── owner_email.txt
    └── user_email.txt
```

## Phase 3 — API contracts

- `POST /api/contact` returns `202 Accepted`.
- Request fields:
  - `name`: required, 2–100 chars.
  - `email`: required, valid email.
  - `phone`: required, 7–32 chars, phone-safe characters.
  - `comment`: required, 10–2000 chars.
- Unknown fields are forbidden.
- Successful response includes:
  - `id`
  - `status = accepted`
  - `email_delivery = sent | queued`
  - `ai` analysis object.
- `GET /api/health` is public.
- `GET /api/metrics` is public only when `METRICS_API_KEY` is unset; otherwise it requires `X-API-Key`.

## Phase 4 — JSON storage

Use `storage/`:

```text
storage/
├── submissions/
├── outbox/
├── logs/app.log
├── metrics.json
└── rate-limit.json
```

Implement repositories before services so business logic never writes files directly.

## Phase 5 — Rate limiting

- Combined IP + email limits.
- Defaults:
  - `RATE_LIMIT_IP_REQUESTS=5`
  - `RATE_LIMIT_IP_WINDOW_SECONDS=600`
  - `RATE_LIMIT_EMAIL_REQUESTS=3`
  - `RATE_LIMIT_EMAIL_WINDOW_SECONDS=3600`
- Rate-limit check happens before AI and email work.
- Exceeded limit returns `429` with `retry_after_seconds`.

## Phase 6 — AI integration

- Use OpenAI-compatible chat-completion client.
- Config:
  - `AI_API_KEY`
  - `AI_BASE_URL`
  - `AI_MODEL=gpt-4o-mini`
- AI returns category, sentiment, summary, priority, confidence.
- Missing key, timeout, invalid response, or provider error returns deterministic fallback.
- Fallback does not fail the contact request.

## Phase 7 — Email and outbox fallback

- Send owner notification and user copy/confirmation.
- Use SMTP when configured.
- If SMTP is missing or fails, write both messages to `storage/outbox/`.
- Contact submission remains successful with `email_delivery = queued`.

## Phase 8 — Contact workflow

Workflow order:

```text
Pydantic validation
→ rate limit
→ AI analysis or fallback
→ persist submission
→ send email or queue outbox
→ update metrics
→ return 202 response
```

Storage failures are critical and return `500`.

## Phase 9 — Tests

Minimum required tests:

- valid contact submission returns `202`;
- invalid email/comment returns `422`;
- rate limit returns `429` and skips AI/email;
- missing/failing AI uses fallback;
- missing/failing SMTP writes outbox and returns `queued`;
- metrics aggregate submissions correctly;
- metrics API requires `X-API-Key` when configured.

## Phase 10 — Angular frontend

- Create small Angular app under `frontend/`.
- Implement contact form using `HttpClient`.
- Show loading/success/error states.
- Handle `422`, `429`, and `5xx` responses.
- Display submission id, email delivery status, and AI analysis after success.

## Phase 11 — Serve frontend from FastAPI

- Keep all API routes under `/api/...`.
- Serve Angular build at `/`.
- Do not intercept `/api/...` with frontend fallback.

## Phase 12 — Docker and Railway

- Add multi-stage `Dockerfile`:
  - Node stage builds Angular.
  - Python stage installs Poetry dependencies and runs Uvicorn.
- Use Railway `PORT` env var:
  - `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`
- Document Railway env vars and filesystem persistence caveat.

## Phase 13 — README

README must include:

- local installation and run commands;
- env var setup;
- API docs and curl examples;
- AI integration and fallback behavior;
- email delivery and outbox behavior;
- storage/rate-limit/metrics explanation;
- testing and quality commands;
- Docker/Railway deployment instructions;
- what was implemented with AI assistance and what was corrected manually.

## Acceptance criteria

- `POST /api/contact` implements the full lifecycle and returns `202`.
- AI integration exists and has graceful fallback.
- Email sends via SMTP or queues to outbox.
- Rate limiting works by IP and email.
- Requests are logged to file.
- OpenAPI/Swagger is available.
- Angular frontend successfully calls backend API.
- Docker image builds and runs.
- `make check` passes.
- README is sufficient for a reviewer to run and evaluate the project.
