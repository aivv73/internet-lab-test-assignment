# Angular frontend

Small Angular client for the InternetLab backend assignment.

## Local development

Run the FastAPI backend from the repository root:

```bash
make dev
```

Then run Angular with the local API proxy:

```bash
make frontend-dev
```

The frontend posts to `/api/contact`; `frontend/proxy.conf.json` forwards `/api`, `/docs`, and `/openapi.json` to `http://localhost:8000` during local development.

## Production build

```bash
make frontend-build
```

The build output is generated under `frontend/dist/frontend` and will be served by FastAPI in the deployment phase.
FastAPI reads the browser bundle from `FRONTEND_DIST_DIR`, which defaults to
`frontend/dist/frontend/browser`.
