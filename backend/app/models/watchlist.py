"""
Watchlist and WatchlistItem ORM models.

Users can create multiple watchlists, each containing a set of coins.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AllMixins, Base, UUIDPrimaryKeyMixin


class Watchlist(Base, AllMixins):
    """A named watchlist belonging to a user."""

    __tablename__ = "watchlists"

    user_id: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, doc="Supabase auth.users ID"
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    items: Mapped[list["WatchlistItem"]] = relationship(
        "WatchlistItem",
        back_populates="watchlist",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_watchlist_user_name"),
        Index("ix_watchlists_user_default", "user_id", "is_default"),
    )

    def __repr__(self) -> str:
        return f"<Watchlist '{self.name}' user={self.user_id}>"


class WatchlistItem(Base, UUIDPrimaryKeyMixin):
    """An individual coin entry within a watchlist."""

    __tablename__ = "watchlist_items"

    watchlist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("watchlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    coin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("coins.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    added_price_usd: Mapped[float | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    watchlist: Mapped["Watchlist"] = relationship("Watchlist", back_populates="items")
    coin: Mapped["Coin"] = relationship("Coin", foreign_keys=[coin_id], lazy="joined")

    __table_args__ = (
        UniqueConstraint("watchlist_id", "coin_id", name="uq_watchlist_item_coin"),
    )

    def __repr__(self) -> str:
        return f"<WatchlistItem watchlist={self.watchlist_id} coin={self.coin_id}>"
