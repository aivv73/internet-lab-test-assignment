# Project Context

## Project

This repository contains a backend-oriented test assignment for InternetLab: a developer landing presentation service with a complete API, AI integration, email notifications, logging, rate limiting, documentation, and deployability.

The main product goal is to demonstrate a full backend request lifecycle:

```text
contact form request → validation → rate limiting → business logic → AI analysis → persistence → email delivery → API response
```

## Audience

- **Hiring reviewers** — evaluate backend code quality, API design, architecture, error handling, AI integration, and project organization.
- **Landing page visitor** — submits a contact form.
- **Site owner/developer** — receives the enriched contact notification.

## Core domain terms

### Contact submission

A validated contact form request from a visitor. It contains `name`, `email`, `phone`, and `comment`, plus system-generated metadata such as `id`, timestamps, AI analysis, and email delivery status.

### AI analysis

A backend-generated enrichment for a contact submission. It classifies the request, estimates sentiment, produces a short owner-facing summary, assigns priority, and includes confidence/fallback metadata.

Expected categories:

- `project_inquiry`
- `job_offer`
- `support`
- `spam`
- `other`
- `unknown`

Expected sentiments:

- `positive`
- `neutral`
- `negative`
- `unknown`

### Graceful fallback

The service must continue accepting contact submissions when an optional integration is unavailable.

- If AI is unavailable or not configured, use deterministic fallback AI analysis.
- If SMTP is unavailable, write email messages to the local outbox.
- If storage is unavailable, treat it as a critical backend error.

### Email delivery status

The contact workflow sends two email messages: one to the site owner and one copy/confirmation to the user.

- `sent` — SMTP delivery succeeded.
- `queued` — SMTP was unavailable or disabled, so messages were saved to the file outbox.

### File storage

Demo persistence based on JSON files. It stores submissions, metrics, rate-limit state, logs, and queued email messages. It is intentionally simple for the assignment and is not production-grade personal-data storage.

### Rate limit

Spam protection applied before AI and email work. The service uses combined IP-based and email-based limits, with values configured through environment variables.

### Metrics

Aggregated service statistics, including total submissions, AI categories/sentiments, email delivery counts, and AI fallback count.

## API shape

### `POST /api/contact`

Accepts a contact submission and returns `202 Accepted` when the request is valid and accepted for processing.

The response includes the created submission id, email delivery status, and AI analysis for demo transparency.

### `GET /api/health`

Public service health endpoint.

### `GET /api/metrics`

Metrics endpoint. If `METRICS_API_KEY` is configured, callers must provide it in the `X-API-Key` header. If no key is configured, the endpoint is open for local/demo use.

## Architecture vocabulary

Use a layered architecture:

```text
Controllers / API routes → Services → Repositories / Handlers
```

- **Routes/controllers** handle HTTP concerns and dependency wiring.
- **Schemas** define request/response contracts and validation.
- **Services** implement workflow/business logic.
- **Repositories** handle file persistence.
- **Handlers/clients** integrate with external systems such as AI and SMTP.

## Technology decisions

- Backend: Python + FastAPI.
- Dependency management: Poetry.
- Quality tools: Ruff, ty, pytest.
- AI: OpenAI-compatible chat-completion client with fallback when not configured/unavailable.
- Frontend: small Angular client for the contact form and API interaction.
- Deployment: single Railway service built with Docker; FastAPI serves the Angular build and exposes `/api/...` endpoints.
