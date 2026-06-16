"""
Watchlist Pydantic schemas.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ── Watchlist Item ────────────────────────────────────────────────────────────


class WatchlistItemCreate(BaseModel):
    """Schema for adding a coin to a watchlist."""

    coin_id: UUID = Field(..., description="Coin UUID to add")
    added_price_usd: float | None = Field(default=None, description="Price when added")
    notes: str | None = Field(default=None, max_length=500)


class WatchlistItemUpdate(BaseModel):
    """Schema for updating a watchlist item."""

    added_price_usd: float | None = None
    notes: str | None = Field(default=None, max_length=500)


class WatchlistItemResponse(BaseModel):
    """A single watchlist item returned to clients."""

    id: UUID
    watchlist_id: UUID
    coin_id: UUID
    added_price_usd: float | None = None
    notes: str | None = None
    coin: dict | None = None  # abbreviated coin info

    model_config = {"from_attributes": True}


# ── Watchlist ─────────────────────────────────────────────────────────────────


class WatchlistCreate(BaseModel):
    """Schema for creating a new watchlist."""

    name: str = Field(..., max_length=200, min_length=1)
    description: str | None = Field(default=None, max_length=1000)
    is_default: bool = False
    sort_order: int = Field(default=0)


class WatchlistUpdate(BaseModel):
    """Schema for updating an existing watchlist."""

    name: str | None = Field(default=None, max_length=200, min_length=1)
    description: str | None = Field(default=None, max_length=1000)
    is_default: bool | None = None
    sort_order: int | None = None


class WatchlistResponse(BaseModel):
    """Full watchlist response including items."""

    id: UUID
    user_id: str
    name: str
    description: str | None = None
    is_default: bool
    sort_order: int
    items: list[WatchlistItemResponse] = Field(default_factory=list)
    item_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WatchlistSummary(BaseModel):
    """Abbreviated watchlist for list views (no items)."""

    id: UUID
    user_id: str
    name: str
    description: str | None = None
    is_default: bool
    sort_order: int
    item_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
