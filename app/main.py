from typing import Any, cast

from fastapi import FastAPI
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

    return app


app = create_app()
