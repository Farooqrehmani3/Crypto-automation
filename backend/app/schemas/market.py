"""
Market data Pydantic schemas.

Covers market overview, trending coins, top movers, and search.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ── Market Overview ───────────────────────────────────────────────────────────


class MarketOverviewResponse(BaseModel):
    """Top-level market summary."""

    total_market_cap_usd: float
    total_volume_24h_usd: float
    btc_dominance_percent: float
    eth_dominance_percent: float | None = None
    active_cryptocurrencies: int | None = None
    fear_greed_index: int | None = Field(default=None, ge=0, le=100)
    fear_greed_classification: str | None = None
    last_updated: datetime | None = None


class MarketGlobalStats(BaseModel):
    """Global cryptocurrency market statistics."""

    total_market_cap_usd: float
    total_volume_24h_usd: float
    market_cap_change_percentage_24h_usd: float | None = None
    btc_dominance_percent: float
    active_cryptocurrencies: int
    upcoming_icos: int | None = None
    ongoing_icos: int | None = None
    ended_icos: int | None = None
    markets: int | None = None
    last_updated: datetime | None = None


# ── Trending ──────────────────────────────────────────────────────────────────


class TrendingCoin(BaseModel):
    """A trending coin entry."""

    coin_id: str
    symbol: str
    name: str
    market_cap_rank: int | None = None
    image_url: str | None = None
    current_price_usd: float | None = None
    price_change_24h_percent: float | None = None
    market_cap_usd: float | None = None
    sparkline_7d: list[float] | None = None


class TrendingResponse(BaseModel):
    """Response for trending coins endpoint."""

    coins: list[TrendingCoin] = Field(default_factory=list)
    last_updated: datetime | None = None


# ── Top Movers ────────────────────────────────────────────────────────────────


class TopMover(BaseModel):
    """A single top mover (gainer or loser)."""

    coin_id: str
    symbol: str
    name: str
    image_url: str | None = None
    current_price_usd: float | None = None
    price_change_24h_percent: float | None = None
    market_cap_usd: float | None = None
    market_cap_rank: int | None = None


class TopMoversResponse(BaseModel):
    """Response for top movers endpoint."""

    gainers: list[TopMover] = Field(default_factory=list)
    losers: list[TopMover] = Field(default_factory=list)
    last_updated: datetime | None = None


# ── Search ────────────────────────────────────────────────────────────────────


class MarketSearchResult(BaseModel):
    """A single market search result."""

    id: str
    name: str
    symbol: str
    market_cap_rank: int | None = None
    image_url: str | None = None
    type: str = Field(default="coin", description="coin | category | exchange")


class MarketSearchResponse(BaseModel):
    """Response for market search endpoint."""

    results: list[MarketSearchResult] = Field(default_factory=list)
    query: str
    total: int = 0
