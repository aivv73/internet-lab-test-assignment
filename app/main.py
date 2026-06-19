from typing import Any, cast

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app.api.routes import contact, health, metrics
from app.core.config import Settings, get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings)

    app = FastAPI(
        title=resolved_settings.app_name,
        description="Backend API for a developer landing contact form with AI integration.",
        version=resolved_settings.app_version,
        middleware=[
            Middleware(
                cast(Any, CORSMiddleware),
                allow_origins=resolved_settings.cors_origins,
                allow_credentials=False,
                allow_methods=["GET", "POST", "OPTIONS"],
                allow_headers=["*"],
            )
        ],
    )

    app.include_router(health.router, prefix="/api")
    app.include_router(contact.router, prefix="/api")
    app.include_router(metrics.router, prefix="/api")
    register_exception_handlers(app)
    register_frontend_routes(app, resolved_settings)

    return app


def register_frontend_routes(app: FastAPI, settings: Settings) -> None:
    """Serve the Angular build without intercepting backend API routes."""
    frontend_dir = settings.frontend_dist_dir
    index_file = frontend_dir / "index.html"

    @app.api_route("/{requested_path:path}", methods=["GET", "HEAD"], include_in_schema=False)
    async def serve_frontend(requested_path: str) -> FileResponse:
        if requested_path == "api" or requested_path.startswith("api/"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        if not index_file.is_file():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        if requested_path:
            requested_file = (frontend_dir / requested_path).resolve()
            frontend_root = frontend_dir.resolve()
            if requested_file.is_file() and requested_file.is_relative_to(frontend_root):
                return FileResponse(requested_file)

        return FileResponse(index_file)


app = create_app()
