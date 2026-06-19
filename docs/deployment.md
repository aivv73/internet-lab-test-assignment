# Docker and Railway deployment

This project deploys as a single service: Angular is built during the Docker build and FastAPI serves the compiled browser bundle plus `/api/...` routes.

## Local Docker build

```bash
docker build -t internet-lab-test-assignment .
docker run --rm -p 8000:8000 --env-file .env internet-lab-test-assignment
```

If you do not have a local `.env`, omit `--env-file .env`; the app will run with fallback AI analysis and queued email delivery.

## Railway

Railway uses `railway.json` to build the repository with the root `Dockerfile`. The container command uses Railway's `PORT` variable:

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

The health check path is `/api/health`.

### Required / recommended variables

Required for a demo deployment: none. Without provider credentials, the API still accepts contact submissions using fallback AI analysis and file outbox delivery.

Recommended production/demo variables:

- `APP_ENV=production`
- `CORS_ORIGINS=https://<your-railway-domain>`
- `CONTACT_OWNER_EMAIL=<owner email>`
- `EMAIL_FROM=<verified sender>`
- `AI_API_KEY=<provider key>` when AI enrichment should call the provider
- `AI_BASE_URL=https://api.openai.com/v1` or another OpenAI-compatible base URL
- `AI_MODEL=gpt-5.4-nano` or your chosen model
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_USE_TLS` when email should send through SMTP
- `METRICS_API_KEY=<secret>` to protect `/api/metrics`

The Docker image sets these defaults:

- `FRONTEND_DIST_DIR=/app/frontend/dist/frontend/browser`
- `STORAGE_DIR=/app/storage`
- `LOG_FILE=/app/storage/logs/app.log`

### Filesystem persistence caveat

Runtime storage is JSON files under `STORAGE_DIR`: submissions, metrics, rate-limit state, logs, and queued outbox messages. Railway container filesystems are ephemeral unless you attach a Railway Volume and point `STORAGE_DIR` at the mounted path. For a real production service, replace JSON storage with a database/object storage, add retention rules, and treat email outbox retry as a background job.
