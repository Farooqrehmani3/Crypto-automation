"""
Custom application exceptions with associated HTTP status codes and error codes.

Every exception maps cleanly to an HTTP response via the global exception
handlers registered in `app.main`.
"""

from __future__ import annotations

from typing import Any


class AppException(Exception):
    """Base exception for all application-level errors."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred"

    def __init__(
        self,
        message: str | None = None,
        error_code: str | None = None,
        status_code: int | None = None,
        detail: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.message
        self.error_code = error_code or self.error_code
        self.status_code = status_code or self.status_code
        self.detail = detail or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "detail": self.detail,
        }


class NotFoundException(AppException):
    """Resource not found (404)."""

    status_code = 404
    error_code = "NOT_FOUND"
    message = "The requested resource was not found"


class UnauthorizedException(AppException):
    """Authentication required (401)."""

    status_code = 401
    error_code = "UNAUTHORIZED"
    message = "Authentication is required to access this resource"


class ForbiddenException(AppException):
    """Insufficient permissions (403)."""

    status_code = 403
    error_code = "FORBIDDEN"
    message = "You do not have permission to perform this action"


class BadRequestException(AppException):
    """Invalid client request (400)."""

    status_code = 400
    error_code = "BAD_REQUEST"
    message = "The request was invalid or cannot be processed"


class ConflictException(AppException):
    """Resource conflict (409)."""

    status_code = 409
    error_code = "CONFLICT"
    message = "The request conflicts with the current state of the resource"


class ServiceException(AppException):
    """Upstream or internal service failure (502)."""

    status_code = 502
    error_code = "SERVICE_ERROR"
    message = "An external service failed to respond"


class RateLimitException(AppException):
    """Too many requests (429)."""

    status_code = 429
    error_code = "RATE_LIMITED"
    message = "Too many requests; please slow down"


class AIServiceException(AppException):
    """AI / LLM service error (502)."""

    status_code = 502
    error_code = "AI_SERVICE_ERROR"
    message = "The AI service encountered an error"


class DataPipelineException(AppException):
    """Data ingestion / processing failure (500)."""

    status_code = 500
    error_code = "DATA_PIPELINE_ERROR"
    message = "Data pipeline processing failed"


__all__ = [
    "AppException",
    "NotFoundException",
    "UnauthorizedException",
    "ForbiddenException",
    "BadRequestException",
    "ConflictException",
    "ServiceException",
    "RateLimitException",
    "AIServiceException",
    "DataPipelineException",
]
