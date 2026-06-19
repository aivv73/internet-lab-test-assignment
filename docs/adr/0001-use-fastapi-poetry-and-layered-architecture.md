# ADR-0001: Use FastAPI, Poetry, and layered backend architecture

## Status

Accepted

## Context

The assignment is backend-oriented and evaluates API design, code organization, error handling, logging, AI integration, and deployability. The service must expose REST endpoints, validate contact form data, document the API, and remain easy to run locally and on Railway.

## Decision

Use Python with FastAPI for the backend, Poetry for dependency management, and a layered architecture:

```text
Controllers / API routes → Services → Repositories / Handlers
```

The expected backend structure is:

```text
app/
├── main.py
├── core/
├── api/routes/
├── schemas/
├── services/
├── repositories/
└── templates/
```

Quality tooling will use Ruff, ty, and pytest, exposed through Makefile wrappers such as `make check`.

## Consequences

- FastAPI provides OpenAPI/Swagger documentation out of the box.
- Pydantic models make validation explicit and reviewable.
- The layered structure demonstrates backend design without requiring a database.
- Poetry is slightly more setup than `requirements.txt`, but it matches the assignment's suggested tooling and cleanly separates runtime/dev dependencies.
