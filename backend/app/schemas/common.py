"""
Common Pydantic schemas shared across the API.

Includes pagination, error responses, success envelopes, and utility types.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Reusable pagination query parameters."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response envelope."""

    items: list[T] = Field(default_factory=list, description="List of items for the current page")
    total: int = Field(..., ge=0, description="Total number of items across all pages")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    pages: int = Field(..., ge=0, description="Total number of pages")

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        pages = max(1, (total + page_size - 1) // page_size) if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )


class ErrorDetail(BaseModel):
    """A single field-level validation error."""

    field: str | None = Field(default=None, description="Field name that caused the error")
    message: str = Field(..., description="Human-readable error message")
    code: str = Field(default="invalid_value", description="Machine-readable error code")


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    error_code: str = Field(default="UNKNOWN", description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    detail: dict[str, Any] = Field(default_factory=dict, description="Additional error context")
    errors: list[ErrorDetail] = Field(
        default_factory=list, description="Field-level validation errors, if any"
    )


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response envelope for single-item operations."""

    success: bool = Field(default=True, description="Always true")
    data: T | None = Field(default=None, description="Response payload")
    message: str = Field(default="OK", description="Human-readable success message")


class MessageResponse(BaseModel):
    """Lightweight message-only response."""

    message: str = Field(..., description="Response message")
