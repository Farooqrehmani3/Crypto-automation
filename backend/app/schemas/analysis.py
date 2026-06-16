"""
AI Analysis and Prediction Pydantic schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# ── Analysis Log ──────────────────────────────────────────────────────────────


class AnalysisLogResponse(BaseModel):
    """A single analysis log entry."""

    id: UUID
    coin_id: UUID | None = None
    analysis_type: str
    model_name: str
    model_version: str
    output_data: dict[str, Any] = Field(default_factory=dict)
    confidence_score: float | None = None
    processing_time_ms: int | None = None
    is_cached: bool = False
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisLogQueryParams(BaseModel):
    """Query parameters for listing analysis logs."""

    coin_id: UUID | None = None
    analysis_type: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ── AI Prediction ─────────────────────────────────────────────────────────────


class AIPredictionResponse(BaseModel):
    """A single AI-generated prediction."""

    id: UUID
    coin_id: UUID
    model_name: str
    prediction_type: str
    target_timeframe: str
    predicted_value: float | None = None
    predicted_direction: str | None = None
    confidence_score: float
    prediction_metadata: dict[str, Any] = Field(default_factory=dict)
    prediction_at: datetime
    expires_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AIPredictionSummary(BaseModel):
    """Abbreviated prediction for dashboard cards."""

    id: UUID
    coin_symbol: str
    coin_name: str
    prediction_type: str
    target_timeframe: str
    predicted_value: float | None = None
    predicted_direction: str | None = None
    confidence_score: float
    prediction_at: datetime


# ── Coin Forecast ─────────────────────────────────────────────────────────────


class ForecastPoint(BaseModel):
    """A single point in a forecast series."""

    timestamp: datetime
    value: float
    lower_bound: float | None = None
    upper_bound: float | None = None


class CoinForecastResponse(BaseModel):
    """A time-series forecast for a coin."""

    id: UUID
    coin_id: UUID
    model_name: str
    forecast_type: str
    horizon_days: int
    forecast_points: list[ForecastPoint] = Field(default_factory=list)
    confidence_interval: float = 0.95
    metrics: dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime
    valid_until: datetime

    model_config = {"from_attributes": True}


# ── Market Snapshot ───────────────────────────────────────────────────────────


class MarketSnapshotResponse(BaseModel):
    """A single market snapshot."""

    id: UUID
    snapshot_type: str
    total_market_cap_usd: float
    total_volume_24h_usd: float
    btc_dominance_percent: float
    eth_dominance_percent: float | None = None
    active_cryptocurrencies: int | None = None
    fear_greed_index: int | None = None
    fear_greed_classification: str | None = None
    top_gainers: list[dict[str, Any]] = Field(default_factory=list)
    top_losers: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}
