# ADR-0003: Use JSON file storage for submissions, rate limiting, outbox, and metrics

## Status

Accepted

## Context

The assignment permits file-system storage and does not require a database. The project should still demonstrate repositories, persistence boundaries, logging, metrics, and spam protection.

## Decision

Use JSON files under `storage/`:

```text
storage/
├── submissions/
├── outbox/
├── logs/app.log
├── metrics.json
└── rate-limit.json
```

Persist each contact submission as a separate JSON file. Store aggregate metrics in `metrics.json`. Store rate-limit counters/windows in `rate-limit.json`.

Rate limiting is combined:

- IP limit: default `5` requests per `600` seconds.
- Email limit: default `3` requests per `3600` seconds.

The settings are configurable through environment variables:

```env
RATE_LIMIT_IP_REQUESTS=5
RATE_LIMIT_IP_WINDOW_SECONDS=600
RATE_LIMIT_EMAIL_REQUESTS=3
RATE_LIMIT_EMAIL_WINDOW_SECONDS=3600
```

## Consequences

- The project avoids database setup and remains easy to run locally.
- File repositories still demonstrate persistence design and error handling.
- This is demo storage, not production-grade personal-data handling; README must mention that production would need a database, retention policy, encryption, and stronger concurrency guarantees.
