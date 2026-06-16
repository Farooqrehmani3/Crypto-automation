"""
AnalysisLog, AIPrediction, CoinForecast, and MarketSnapshot ORM models.

Tracks AI-driven analysis, predictions, forecasts, and periodic market snapshots.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AnalysisLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Log of an AI analysis run against a coin or the overall market."""

    __tablename__ = "analysis_logs"

    coin_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("coins.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    analysis_type: Mapped[str] = mapped_column(
        String(50), nullable=False, doc="technical | fundamental | sentiment | onchain | composite"
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    input_data_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    output_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_cached: Mapped[bool] = mapped_column(default=False, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_analysis_logs_coin_type", "coin_id", "analysis_type"),
        Index("ix_analysis_logs_created_at", "created_at"),
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0.0 AND confidence_score <= 1.0)",
            name="ck_analysis_confidence_range",
        ),
    )

    def __repr__(self) -> str:
        return f"<AnalysisLog coin={self.coin_id} type={self.analysis_type}>"


class AIPrediction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """An AI-generated price prediction for a specific coin."""

    __tablename__ = "ai_predictions"

    coin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("coins.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    analysis_log_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_logs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    prediction_type: Mapped[str] = mapped_column(
        String(50), nullable=False, doc="price | direction | volatility | trend"
    )
    target_timeframe: Mapped[str] = mapped_column(
        String(20), nullable=False, doc="1h | 4h | 24h | 7d | 30d"
    )
    predicted_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    predicted_direction: Mapped[str | None] = mapped_column(
        String(10), nullable=True, doc="up | down | sideways"
    )
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    prediction_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    prediction_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_predictions_coin_timeframe", "coin_id", "target_timeframe"),
        Index("ix_predictions_created_at", "created_at"),
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_prediction_confidence_range",
        ),
    )

    def __repr__(self) -> str:
        return f"<AIPrediction coin={self.coin_id} {self.prediction_type} {self.target_timeframe}>"


class CoinForecast(Base, UUIDPrimaryKeyMixin):
    """A multi-point time-series forecast for a coin's price."""

    __tablename__ = "coin_forecasts"

    coin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("coins.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    forecast_type: Mapped[str] = mapped_column(
        String(50), nullable=False, doc="price | volume | volatility | market_cap"
    )
    horizon_days: Mapped[int] = mapped_column(Integer, nullable=False)
    forecast_points: Mapped[dict] = mapped_column(
        JSONB, nullable=False, doc="[{timestamp, value, lower_bound, upper_bound}, ...]"
    )
    confidence_interval: Mapped[float] = mapped_column(
        Float, default=0.95, nullable=False, doc="e.g. 0.95 for 95% CI"
    )
    metrics: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict, doc="MAE, RMSE, MAPE, etc."
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    valid_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        Index("ix_forecasts_coin_horizon", "coin_id", "horizon_days"),
        Index("ix_forecasts_generated_at", "generated_at"),
    )

    def __repr__(self) -> str:
        return f"<CoinForecast coin={self.coin_id} horizon={self.horizon_days}d>"


class MarketSnapshot(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A periodic snapshot of overall market conditions."""

    __tablename__ = "market_snapshots"

    snapshot_type: Mapped[str] = mapped_column(
        String(50), nullable=False, doc="hourly | daily | weekly"
    )
    total_market_cap_usd: Mapped[float] = mapped_column(Float, nullable=False)
    total_volume_24h_usd: Mapped[float] = mapped_column(Float, nullable=False)
    btc_dominance_percent: Mapped[float] = mapped_column(Float, nullable=False)
    eth_dominance_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    active_cryptocurrencies: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fear_greed_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fear_greed_classification: Mapped[str | None] = mapped_column(String(50), nullable=True)
    top_gainers: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    top_losers: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    snapshot_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    __table_args__ = (
        Index("ix_snapshots_type_created", "snapshot_type", "created_at"),
        CheckConstraint(
            "fear_greed_index IS NULL OR (fear_greed_index >= 0 AND fear_greed_index <= 100)",
            name="ck_fear_greed_range",
        ),
    )

    def __repr__(self) -> str:
        return f"<MarketSnapshot {self.snapshot_type} mcap=${self.total_market_cap_usd:,.0f}>"
