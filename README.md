Live demo:
https://api.giraffedev.ru/

API docs:
https://api.giraffedev.ru/docs

# InternetLab backend test assignment

Backend-oriented developer landing service for the InternetLab test assignment. The project demonstrates a complete contact-form request lifecycle with FastAPI, AI enrichment, email delivery/fallback, file persistence, metrics, rate limiting, logging, an Angular frontend, and single-service Docker/Railway deployment.

```text
request → validation → rate limiting → AI analysis → persistence → email delivery/fallback → metrics → 202 response
```

## What is implemented

- **FastAPI API** with OpenAPI/Swagger docs.
- **Angular contact landing page** that calls the backend API asynchronously.
- **Strict request validation** using Pydantic schemas.
- **Combined rate limiting** by client IP and email address.
- **OpenAI-compatible AI integration** for category, sentiment, priority, confidence, and summary.
- **Deterministic AI fallback** when the provider is not configured or fails.
- **Email delivery via Resend HTTPS API or SMTP** to the owner and user.
- **File outbox fallback** when the configured email provider is unavailable or delivery fails.
- **JSON file storage** for submissions, metrics, rate-limit state, logs, and outbox messages.
- **Metrics endpoint** with optional `X-API-Key` protection.
- **FastAPI-served Angular build** for single-origin production deployment.
- **Dockerfile + Railway config** for one-service deployment.
- **Tests and quality tooling** via pytest, Ruff, and ty.

## Repository layout

```text
app/
  api/routes/          FastAPI route modules
  core/                settings, logging, errors, security helpers
  handlers/            AI, Resend, and SMTP integration clients
  repositories/        JSON file persistence boundaries
  schemas/             Pydantic API contracts
  services/            workflow/business logic
frontend/              Angular client
storage/               local runtime data, ignored by git
docs/adr/              architecture decision records
docs/deployment.md     Docker/Railway deployment notes
tests/                 pytest suite
```

## Requirements

For local development:

- Python 3.12+
- Poetry 2.x
- Node.js/npm compatible with Angular 22
- Docker, only if you want to test the production container

## Local setup

Install backend dependencies:

```bash
make install
```

Install frontend dependencies:

```bash
make frontend-install
```

Create a local env file if you want to override defaults:

```bash
cp .env.example .env
```

The app works without AI or email provider credentials. In that mode, contact submissions still return `202 Accepted`, AI analysis uses fallback values, and emails are written to the local outbox.

## Running locally

### Option A: backend + Angular dev server

Terminal 1:

```bash
make dev
```

Backend:

- API: <http://localhost:8000/api/health>
- Swagger: <http://localhost:8000/docs>
- OpenAPI: <http://localhost:8000/openapi.json>

Terminal 2:

```bash
make frontend-dev
```

Frontend:

- Angular dev server: <http://localhost:4200/>

Angular uses `frontend/proxy.conf.json` so `/api`, `/docs`, and `/openapi.json` are proxied to FastAPI during local development.

### Option B: FastAPI serves the built Angular app

```bash
make frontend-build
make dev
```

Then open:

- Landing page: <http://localhost:8000/>
- API docs: <http://localhost:8000/docs>

FastAPI serves the build from `FRONTEND_DIST_DIR`, which defaults to `frontend/dist/frontend/browser`.

## Environment variables

See `.env.example` for the full list.

### Application

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_NAME` | `developer-landing-api` | FastAPI app title/service name. |
| `APP_ENV` | `development` | Environment label for logs/config. |
| `APP_VERSION` | `0.1.0` | Version reported by `/api/health`. |
| `STORAGE_DIR` | `storage` | JSON persistence root. |
| `LOG_FILE` | `storage/logs/app.log` | Application log file. |
| `FRONTEND_DIST_DIR` | `frontend/dist/frontend/browser` | Angular browser build served by FastAPI. |
| `CORS_ORIGINS` | `http://localhost:4200,http://localhost:8000` in example | Comma-separated allowed frontend origins. |

### AI provider

| Variable | Default | Purpose |
| --- | --- | --- |
| `AI_API_KEY` | empty | Enables provider calls when set. |
| `AI_BASE_URL` | `https://api.openai.com/v1` | OpenAI-compatible base URL. |
| `AI_MODEL` | `gpt-5.4-nano` | Chat completion model name. |
| `AI_TIMEOUT_SECONDS` | `10` | Provider request timeout. |

### Email / Resend / SMTP

| Variable | Default | Purpose |
| --- | --- | --- |
| `CONTACT_OWNER_EMAIL` | `owner@example.com` | Owner notification recipient. |
| `EMAIL_FROM` | `no-reply@example.com` | Sender address. For Resend, use a verified sender/domain. |
| `EMAIL_PROVIDER` | `smtp` | Email provider: `smtp` or `resend`. |
| `RESEND_API_KEY` | empty | Enables Resend HTTPS API delivery when `EMAIL_PROVIDER=resend`. |
| `RESEND_BASE_URL` | `https://api.resend.com` | Resend API base URL. |
| `SMTP_HOST` | empty | Enables SMTP delivery when `EMAIL_PROVIDER=smtp` and host is set. |
| `SMTP_PORT` | `587` | SMTP port. |
| `SMTP_USERNAME` | empty | SMTP username. |
| `SMTP_PASSWORD` | empty | SMTP password. |
| `SMTP_USE_TLS` | `true` | Use STARTTLS/TLS. |

### Rate limiting and metrics

| Variable | Default | Purpose |
| --- | --- | --- |
| `RATE_LIMIT_IP_REQUESTS` | `5` | Max requests per IP window. |
| `RATE_LIMIT_IP_WINDOW_SECONDS` | `600` | IP window length. |
| `RATE_LIMIT_EMAIL_REQUESTS` | `3` | Max requests per email window. |
| `RATE_LIMIT_EMAIL_WINDOW_SECONDS` | `3600` | Email window length. |
| `METRICS_API_KEY` | empty | If set, `/api/metrics` requires `X-API-Key`. |

## API docs and curl examples

Swagger UI is available at:

```text
http://localhost:8000/docs
```

OpenAPI JSON is available at:

```text
http://localhost:8000/openapi.json
```

### Health

```bash
curl http://localhost:8000/api/health
```

Example response:

```json
{
  "status": "ok",
  "service": "developer-landing-api",
  "version": "0.1.0"
}
```

### Submit contact request

```bash
curl -i -X POST http://localhost:8000/api/contact \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Ada Lovelace",
    "email": "ada@example.com",
    "phone": "+1 555 0123",
    "comment": "I would like to discuss a backend API project with Angular and FastAPI."
  }'
```

Success returns `202 Accepted`:

```json
{
  "id": "95bac64c-aed4-434c-86f4-df9de392cb53",
  "status": "accepted",
  "email_delivery": "queued",
  "ai": {
    "category": "unknown",
    "sentiment": "unknown",
    "summary": "AI analysis unavailable",
    "priority": "normal",
    "confidence": 0.0,
    "fallback_used": true
  },
  "created_at": "2026-06-19T20:18:10.557343Z"
}
```

Expected error statuses:

- `422 Unprocessable Entity` for invalid payloads.
- `429 Too Many Requests` when IP/email rate limits are exceeded.
- `500 Internal Server Error` for critical backend/storage failures.

### Metrics

Open metrics when `METRICS_API_KEY` is empty:

```bash
curl http://localhost:8000/api/metrics
```

Protected metrics when `METRICS_API_KEY` is set:

```bash
curl http://localhost:8000/api/metrics \
  -H 'X-API-Key: your-secret'
```

Example response:

```json
{
  "total_submissions": 1,
  "by_category": { "unknown": 1 },
  "by_sentiment": { "unknown": 1 },
  "email_delivery": { "queued": 1 },
  "ai_fallbacks": 1
}
```

## Contact workflow details

`POST /api/contact` runs through these layers:

1. FastAPI route receives the request under `/api/contact`.
2. Pydantic validates `name`, `email`, `phone`, and `comment` and rejects unknown fields.
3. Rate limiter checks combined IP and email windows.
4. AI service calls an OpenAI-compatible chat completion provider when configured.
5. If AI is missing or fails, deterministic fallback analysis is used.
6. Submission is saved to JSON storage.
7. Email service sends owner/user emails through Resend or SMTP when configured.
8. If the selected email provider is missing or fails, both messages are saved to the outbox.
9. Metrics are updated.
10. API returns `202 Accepted` with submission id, email delivery status, and AI analysis.

## AI behavior and fallback

The AI integration is intentionally backend-oriented rather than decorative. It enriches submissions with:

- `category`: `project_inquiry`, `job_offer`, `support`, `spam`, `other`, or `unknown`
- `sentiment`: `positive`, `neutral`, `negative`, or `unknown`
- `summary`: short owner-facing summary
- `priority`: `low`, `normal`, or `high`
- `confidence`: `0.0` to `1.0`
- `fallback_used`: whether deterministic fallback was used

When `AI_API_KEY` is not set, the provider fails, or the provider returns unusable content, the request still succeeds with:

```json
{
  "category": "unknown",
  "sentiment": "unknown",
  "summary": "AI analysis unavailable",
  "priority": "normal",
  "confidence": 0.0,
  "fallback_used": true
}
```

## Email and outbox behavior

Each accepted contact submission builds two email messages:

- owner notification with contact details and AI analysis;
- user confirmation copy.

The service supports two delivery providers:

- `EMAIL_PROVIDER=resend` sends through the Resend HTTPS API. This is the recommended Railway option because many platforms restrict outbound SMTP ports.
- `EMAIL_PROVIDER=smtp` sends through SMTP when `SMTP_HOST` and sender settings are configured.

If the selected provider is configured and delivery succeeds, the API returns:

```json
"email_delivery": "sent"
```

If the provider is not configured or delivery fails, the service queues both messages under:

```text
storage/outbox/
```

and returns:

```json
"email_delivery": "queued"
```

Email failure is deliberately non-blocking; storage failure is treated as critical.

## Storage, logs, rate limiting, and metrics

Local/demo persistence uses JSON files under `STORAGE_DIR`:

```text
storage/
  submissions/       accepted contact submissions
  outbox/            queued email messages
  logs/app.log       application logs
  metrics.json       aggregate metrics
  rate-limit.json    IP/email rate-limit counters
```

This is simple review-friendly storage, not production-grade personal-data infrastructure. A production service should use a database/object storage, retention policy, encryption/secrets management, stronger concurrency guarantees, and a background retry worker for outbox delivery.

## Testing and quality commands

```bash
make test       # pytest
make lint       # ruff check
make format     # ruff format
make typecheck  # ty check
make check      # lint + typecheck + test
```

Frontend build:

```bash
make frontend-build
```

The current test suite covers API contracts, contact workflow, AI fallback, email/outbox behavior, JSON storage, rate limiting, metrics security, health checks, and FastAPI serving of the Angular build.

## Docker

Build the production image:

```bash
docker build -t internet-lab-test-assignment .
```

Run it locally:

```bash
docker run --rm -p 8000:8000 internet-lab-test-assignment
```

Or with a local `.env`:

```bash
docker run --rm -p 8000:8000 --env-file .env internet-lab-test-assignment
```

The image builds Angular in a Node stage, installs Python runtime dependencies in a Python stage, and serves the Angular bundle through FastAPI. The container command uses the Railway-compatible `PORT` variable:

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

## Railway deployment

This repository includes `railway.json`, which tells Railway to use the root `Dockerfile` and health check `/api/health`.

Deployment outline:

1. Create a Railway project from the GitHub repository.
2. Let Railway build with the Dockerfile.
3. Set recommended variables:
   - `APP_ENV=production`
   - `CORS_ORIGINS=https://<your-railway-domain>`
   - `CONTACT_OWNER_EMAIL=<owner email>`
   - `EMAIL_FROM=<verified sender>`
   - `AI_API_KEY=<provider key>` if provider AI should be enabled
   - `EMAIL_PROVIDER=resend` and `RESEND_API_KEY=<provider key>` if Resend should send mail over HTTPS
   - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_USE_TLS` if SMTP should send mail instead
   - `METRICS_API_KEY=<secret>` to protect metrics
4. Attach a Railway Volume if you want JSON storage to persist across redeploys/restarts, and set `STORAGE_DIR` to the mounted path.

More details are in [`docs/deployment.md`](docs/deployment.md).

## Architecture decisions

Architecture decision records are in [`docs/adr/`](docs/adr/):

- ADR-0001: FastAPI, Poetry, layered backend architecture.
- ADR-0002: contact workflow with AI analysis and graceful email fallback.
- ADR-0003: JSON file storage, rate limiting, and metrics.
- ADR-0004: serve Angular from FastAPI and deploy as one Dockerized Railway service.

## Notes on AI assistance

AI assistance was used to accelerate planning, code generation, UI copy/design iteration, and README drafting. The project was still reviewed and corrected manually through:

- explicit architecture decisions in `docs/adr/`;
- deterministic fallback behavior instead of assuming external AI/email-provider availability;
- typed Pydantic request/response contracts;
- pytest coverage for success, validation, rate limit, AI fallback, email-provider outbox, metrics, and frontend serving;
- Ruff and ty checks;
- local Angular build verification;
- Docker image build and container smoke testing.

Manual corrections included tightening environment/storage isolation in tests, ensuring frontend fallback does not intercept `/api/...`, documenting Railway filesystem persistence caveats, and validating the Docker image with real HTTP smoke checks.

## License

MIT. See [`LICENSE`](LICENSE).
