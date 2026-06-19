# ADR-0004: Serve Angular from FastAPI and deploy as one Dockerized Railway service

## Status

Accepted

## Context

The vacancy values API/frontend-backend interaction, async frontend calls, error handling, and Angular as a plus. The assignment is still backend-focused, so frontend complexity must not dominate implementation time. The deployment target is Railway.

## Decision

Build a small Angular frontend for the contact form and serve its production build from FastAPI. Keep backend API routes under `/api/...`.

Runtime shape:

```text
/                 → Angular app
/assets/...       → Angular static assets
/api/contact      → FastAPI
/api/health       → FastAPI
/api/metrics      → FastAPI
```

Deploy as a single Railway service using a Dockerfile with a frontend build stage and a Python runtime stage.

## Consequences

- Reviewers get one public URL for both UI and API.
- Same-origin frontend/backend calls reduce CORS complexity in production.
- The Angular app demonstrates frontend-backend interaction without requiring a separate hosting target.
- Docker adds one infrastructure file but makes Railway deployment predictable for a Python + Angular repository.
