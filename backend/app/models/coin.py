"""
Coin and CoinPrice ORM models.

Represents supported cryptocurrencies and their historical price data.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AllMixins, Base, UUIDPrimaryKeyMixin


class Coin(Base, UUIDPrimaryKeyMixin):
    """A supported cryptocurrency tracked by the platform."""

    __tablename__ = "coins"

    coingecko_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True, doc="CoinGecko API coin ID"
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    market_cap_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_price_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    market_cap_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_volume_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    circulating_supply: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_supply: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_supply: Mapped[float | None] = mapped_column(Float, nullable=True)
    ath_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    atl_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    high_24h_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    low_24h_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_change_24h_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_change_7d_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_change_30d_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    genesis_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    homepage_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    last_synced_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationships
    prices: Mapped[list["CoinPrice"]] = relationship(
        "CoinPrice", back_populates="coin", cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_coins_market_cap_rank", "market_cap_rank"),
        Index("ix_coins_symbol_name", "symbol", "name"),
        CheckConstraint("market_cap_rank IS NULL OR market_cap_rank > 0", name="ck_coins_market_cap_rank_positive"),
    )

    def __repr__(self) -> str:
        return f"<Coin {self.symbol.upper()} ({self.name}) rank={self.market_cap_rank}>"


class CoinPrice(Base):
    """Historical price data point for a coin."""

    __tablename__ = "coin_prices"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    coin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("coins.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(nullable=False, index=True)
    price_usd: Mapped[float] = mapped_column(Float, nullable=False)
    market_cap_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="coingecko", nullable=False)

    # Relationships
    coin: Mapped["Coin"] = relationship("Coin", back_populates="prices")

    __table_args__ = (
        UniqueConstraint("coin_id", "timestamp", name="uq_coin_price_timestamp"),
        Index("ix_coin_prices_coin_timestamp", "coin_id", "timestamp"),
        Index("ix_coin_prices_timestamp_btree", timestamp.desc()),
    )

    def __repr__(self) -> str:
        return f"<CoinPrice coin={self.coin_id} ts={self.timestamp} price=${self.price_usd:.2f}>"
