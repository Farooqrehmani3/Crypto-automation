"""
Portfolio, PortfolioAsset, and PortfolioTransaction ORM models.

Tracks user portfolios, holdings, and transaction history.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AllMixins, Base, UUIDPrimaryKeyMixin


class Portfolio(Base, AllMixins):
    """A user's portfolio, which can contain multiple assets."""

    __tablename__ = "portfolios"

    user_id: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, doc="Supabase auth.users ID"
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_default: Mapped[bool] = mapped_column(default=False, nullable=False)
    total_value_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_cost_basis_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_pnl_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_calculated_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationships
    assets: Mapped[list["PortfolioAsset"]] = relationship(
        "PortfolioAsset",
        back_populates="portfolio",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_portfolio_user_name"),
        Index("ix_portfolios_user_default", "user_id", "is_default"),
    )

    def __repr__(self) -> str:
        return f"<Portfolio '{self.name}' user={self.user_id} value=${self.total_value_usd:.2f}>"


class PortfolioAsset(Base, UUIDPrimaryKeyMixin):
    """A holding within a portfolio."""

    __tablename__ = "portfolio_assets"

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    coin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("coins.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    average_cost_basis_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    current_value_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    pnl_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    pnl_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="assets")
    coin: Mapped["Coin"] = relationship("Coin", foreign_keys=[coin_id], lazy="joined")

    __table_args__ = (
        UniqueConstraint("portfolio_id", "coin_id", name="uq_portfolio_asset_coin"),
        CheckConstraint("quantity >= 0", name="ck_portfolio_asset_quantity_nonnegative"),
    )

    def __repr__(self) -> str:
        return f"<PortfolioAsset coin={self.coin_id} qty={self.quantity:.4f}>"


class PortfolioTransaction(Base, UUIDPrimaryKeyMixin):
    """A single transaction within a portfolio (buy, sell, transfer)."""

    __tablename__ = "portfolio_transactions"

    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    coin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("coins.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    transaction_type: Mapped[str] = mapped_column(
        String(20), nullable=False, doc="buy | sell | transfer_in | transfer_out"
    )
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    price_per_coin_usd: Mapped[float] = mapped_column(Float, nullable=False)
    total_value_usd: Mapped[float] = mapped_column(Float, nullable=False)
    fee_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_transaction_quantity_positive"),
        CheckConstraint(
            "transaction_type IN ('buy', 'sell', 'transfer_in', 'transfer_out')",
            name="ck_transaction_type_valid",
        ),
        Index("ix_transactions_portfolio_date", "portfolio_id", "transaction_date"),
    )

    def __repr__(self) -> str:
        return f"<PortfolioTransaction {self.transaction_type} {self.quantity} @ ${self.price_per_coin_usd:.2f}>"
