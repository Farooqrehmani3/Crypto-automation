"""
UserPreference ORM model.

User authentication profiles are managed by Supabase Auth (auth.users table).
This table stores additional application-specific preferences and metadata.
"""

from __future__ import annotations

from sqlalchemy import Float, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UserPreference(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Per-user application preferences and settings.

    The `user_id` corresponds to `auth.users.id` in Supabase.
    Application-level fields only; auth is handled externally.
    """

    __tablename__ = "user_preferences"

    user_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True, doc="Supabase auth.users ID"
    )
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)

    # Notification preferences
    email_notifications: Mapped[bool] = mapped_column(default=True, nullable=False)
    push_notifications: Mapped[bool] = mapped_column(default=True, nullable=False)
    price_alert_threshold_percent: Mapped[float] = mapped_column(
        Float, default=5.0, nullable=False, doc="Alert when price moves by this % in 24h"
    )
    breaking_news_alerts: Mapped[bool] = mapped_column(default=True, nullable=False)
    ai_analysis_alerts: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Dashboard preferences
    default_watchlist_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True, doc="UUID of the default watchlist"
    )
    default_portfolio_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True, doc="UUID of the default portfolio"
    )
    dashboard_layout: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict, doc="User-customized dashboard widget layout"
    )
    favorite_coins: Mapped[list | None] = mapped_column(
        JSONB, nullable=True, doc="List of favorite coin IDs for quick access"
    )

    # Theme
    theme: Mapped[str] = mapped_column(String(20), default="system", nullable=False, doc="light | dark | system")
    chart_preferences: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict, doc="Charting defaults (timeframe, indicators, etc.)"
    )

    __table_args__ = (
        Index("ix_user_prefs_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<UserPreference user={self.user_id} currency={self.currency}>"
