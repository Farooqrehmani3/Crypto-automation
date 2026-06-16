"""
User and UserPreference Pydantic schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# ── User (from Supabase JWT) ─────────────────────────────────────────────────


class UserInfo(BaseModel):
    """Information about the authenticated user, extracted from their JWT."""

    id: str = Field(..., description="Supabase user ID (sub claim)")
    email: str | None = Field(default=None, description="User email address")
    role: str = Field(default="authenticated", description="User role")
    metadata: dict[str, Any] = Field(default_factory=dict, description="User metadata from JWT")

    model_config = {"from_attributes": True}


# ── User Preferences ──────────────────────────────────────────────────────────


class UserPreferenceBase(BaseModel):
    """Shared preference fields."""

    display_name: str | None = Field(default=None, max_length=100)
    timezone: str = Field(default="UTC", max_length=50)
    currency: str = Field(default="USD", max_length=10)
    language: str = Field(default="en", max_length=10)
    email_notifications: bool = True
    push_notifications: bool = True
    price_alert_threshold_percent: float = Field(default=5.0, ge=0.0, le=100.0)
    breaking_news_alerts: bool = True
    ai_analysis_alerts: bool = True
    theme: str = Field(default="system", max_length=20)
    dashboard_layout: dict[str, Any] = Field(default_factory=dict)
    chart_preferences: dict[str, Any] = Field(default_factory=dict)
    favorite_coins: list[str] | None = None


class UserPreferenceCreate(UserPreferenceBase):
    """Schema for creating user preferences."""

    user_id: str = Field(..., max_length=100, description="Supabase user ID")


class UserPreferenceUpdate(BaseModel):
    """Schema for updating user preferences — all fields optional."""

    display_name: str | None = Field(default=None, max_length=100)
    timezone: str | None = Field(default=None, max_length=50)
    currency: str | None = Field(default=None, max_length=10)
    language: str | None = Field(default=None, max_length=10)
    email_notifications: bool | None = None
    push_notifications: bool | None = None
    price_alert_threshold_percent: float | None = Field(default=None, ge=0.0, le=100.0)
    breaking_news_alerts: bool | None = None
    ai_analysis_alerts: bool | None = None
    theme: str | None = Field(default=None, max_length=20)
    dashboard_layout: dict[str, Any] | None = None
    chart_preferences: dict[str, Any] | None = None
    favorite_coins: list[str] | None = None
    default_watchlist_id: str | None = Field(default=None, max_length=36)
    default_portfolio_id: str | None = Field(default=None, max_length=36)


class UserPreferenceResponse(UserPreferenceBase):
    """Schema for returning user preferences to the client."""

    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
