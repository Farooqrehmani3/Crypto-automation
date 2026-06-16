"""
Coin and CoinPrice Pydantic schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# ── Coin Price ────────────────────────────────────────────────────────────────


class CoinPriceResponse(BaseModel):
    """A single price data point."""

    id: int
    coin_id: UUID
    timestamp: datetime
    price_usd: float
    market_cap_usd: float | None = None
    volume_usd: float | None = None
    source: str

    model_config = {"from_attributes": True}


class CoinPriceQueryParams(BaseModel):
    """Query parameters for fetching historical prices."""

    vs_currency: str = Field(default="usd", max_length=10)
    days: int = Field(default=7, ge=1, le=365, description="Number of days of data")
    interval: str = Field(default="daily", description="daily | hourly | minutely")


# ── Coin ──────────────────────────────────────────────────────────────────────


class CoinBase(BaseModel):
    """Shared coin fields."""

    coingecko_id: str = Field(..., max_length=100)
    symbol: str = Field(..., max_length=20)
    name: str = Field(..., max_length=100)
    image_url: str | None = Field(default=None, max_length=500)
    market_cap_rank: int | None = None
    description: str | None = None
    is_active: bool = True


class CoinResponse(CoinBase):
    """Full coin response with market data."""

    id: UUID
    current_price_usd: float | None = None
    market_cap_usd: float | None = None
    total_volume_usd: float | None = None
    circulating_supply: float | None = None
    total_supply: float | None = None
    max_supply: float | None = None
    ath_usd: float | None = None
    atl_usd: float | None = None
    high_24h_usd: float | None = None
    low_24h_usd: float | None = None
    price_change_24h_percent: float | None = None
    price_change_7d_percent: float | None = None
    price_change_30d_percent: float | None = None
    genesis_date: datetime | None = None
    homepage_url: str | None = None
    last_synced_at: datetime | None = None

    model_config = {"from_attributes": True}


class CoinListResponse(CoinBase):
    """Abbreviated coin response for list views."""

    id: UUID
    current_price_usd: float | None = None
    market_cap_usd: float | None = None
    market_cap_rank: int | None = None
    price_change_24h_percent: float | None = None
    image_url: str | None = None

    model_config = {"from_attributes": True}


class CoinStatsResponse(BaseModel):
    """Aggregated statistics for a coin."""

    coin_id: UUID
    symbol: str
    name: str
    current_price_usd: float | None = None
    market_cap_usd: float | None = None
    market_cap_rank: int | None = None
    price_change_24h_percent: float | None = None
    price_change_7d_percent: float | None = None
    price_change_30d_percent: float | None = None
    high_24h_usd: float | None = None
    low_24h_usd: float | None = None
    ath_usd: float | None = None
    atl_usd: float | None = None
    total_volume_usd: float | None = None
    circulating_supply: float | None = None
    total_supply: float | None = None
    max_supply: float | None = None

    model_config = {"from_attributes": True}


class CoinSearchResult(BaseModel):
    """A single search result."""

    id: UUID
    symbol: str
    name: str
    coingecko_id: str
    market_cap_rank: int | None = None
    image_url: str | None = None


class CoinQueryParams(BaseModel):
    """Query parameters for listing coins."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=250)
    sort_by: str = Field(default="market_cap_rank", description="market_cap_rank | name | price_change_24h_percent")
    sort_order: str = Field(default="asc", description="asc | desc")
    search: str | None = Field(default=None, max_length=100, description="Search by name or symbol")
    is_active: bool | None = None
