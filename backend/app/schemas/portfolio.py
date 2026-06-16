"""
Portfolio Pydantic schemas.
"""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ── Portfolio Transaction ─────────────────────────────────────────────────────


class PortfolioTransactionCreate(BaseModel):
    """Schema for recording a new transaction."""

    coin_id: UUID
    transaction_type: str = Field(..., description="buy | sell | transfer_in | transfer_out")
    quantity: float = Field(..., gt=0)
    price_per_coin_usd: float = Field(..., gt=0)
    fee_usd: float = Field(default=0.0, ge=0.0)
    notes: str | None = Field(default=None, max_length=500)
    transaction_date: date = Field(default_factory=lambda: datetime.now().date())


class PortfolioTransactionResponse(BaseModel):
    """Response schema for a portfolio transaction."""

    id: UUID
    portfolio_id: UUID
    coin_id: UUID
    transaction_type: str
    quantity: float
    price_per_coin_usd: float
    total_value_usd: float
    fee_usd: float
    notes: str | None = None
    transaction_date: date

    model_config = {"from_attributes": True}


# ── Portfolio Asset ───────────────────────────────────────────────────────────


class PortfolioAssetResponse(BaseModel):
    """A single asset holding within a portfolio."""

    id: UUID
    portfolio_id: UUID
    coin_id: UUID
    quantity: float
    average_cost_basis_usd: float
    current_value_usd: float
    pnl_usd: float
    pnl_percent: float
    coin: dict | None = None  # abbreviated coin info

    model_config = {"from_attributes": True}


# ── Portfolio ─────────────────────────────────────────────────────────────────


class PortfolioCreate(BaseModel):
    """Schema for creating a new portfolio."""

    name: str = Field(..., max_length=200, min_length=1)
    description: str | None = Field(default=None, max_length=1000)
    is_default: bool = False


class PortfolioUpdate(BaseModel):
    """Schema for updating an existing portfolio."""

    name: str | None = Field(default=None, max_length=200, min_length=1)
    description: str | None = Field(default=None, max_length=1000)
    is_default: bool | None = None


class PortfolioResponse(BaseModel):
    """Full portfolio response."""

    id: UUID
    user_id: str
    name: str
    description: str | None = None
    is_default: bool
    total_value_usd: float = 0.0
    total_cost_basis_usd: float = 0.0
    total_pnl_usd: float = 0.0
    assets: list[PortfolioAssetResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PortfolioSummary(BaseModel):
    """Abbreviated portfolio for list views."""

    id: UUID
    user_id: str
    name: str
    description: str | None = None
    is_default: bool
    total_value_usd: float = 0.0
    total_pnl_usd: float = 0.0
    asset_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
