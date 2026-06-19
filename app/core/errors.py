from typing import cast

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.applications import ExceptionHandler

from app.schemas.error import ErrorDetail, ErrorResponse


class AppError(Exception):
    """Base exception for expected application errors."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, object] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.http_status = http_status
        self.details = details or {}
        super().__init__(message)


class StorageError(AppError):
    """Raised when file storage is unavailable or corrupted."""

    def __init__(self, message: str = "Storage operation failed") -> None:
        super().__init__(
            "storage_error",
            message,
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class RateLimitExceededError(AppError):
    """Raised when a client exceeds the configured rate limit."""

    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__(
            "rate_limit_exceeded",
            "Too many contact requests. Please try again later.",
            http_status=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after_seconds": retry_after_seconds},
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        payload = ErrorResponse(
            error=ErrorDetail(code=exc.code, message=exc.message, details=exc.details)
        )
        return JSONResponse(status_code=exc.http_status, content=payload.model_dump())

    app.add_exception_handler(AppError, cast(ExceptionHandler, app_error_handler))
