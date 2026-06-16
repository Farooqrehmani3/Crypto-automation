"""
Market Service — Market overview, trending coins, search functionality.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.models.coin import Coin
from app.models.analysis import MarketSnapshot
from app.integrations.coingecko import coingecko_client

logger = get_logger(__name__)


class MarketService:
    """Service for market-wide data and overviews."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_market_overview(self) -> dict:
        """Get global market overview with Fear & Greed Index."""
        try:
            # Try cached snapshot first
            result = await self.db.execute(
                select(MarketSnapshot)
                .where(MarketSnapshot.snapshot_type == "global")
                .order_by(desc(MarketSnapshot.captured_at))
                .limit(1)
            )
            cached = result.scalar_one_or_none()

            if cached and (datetime.utcnow() - cached.captured_at).seconds < 300:
                return cached.data

            # Fetch fresh data
            global_data = await coingecko_client.get_global_data()
            fear_greed = await coingecko_client.get_fear_greed_index()

            overview = {
                "total_market_cap": global_data.get("data", {}).get("total_market_cap", {}).get("usd", 0),
                "total_volume_24h": global_data.get("data", {}).get("total_volume", {}).get("usd", 0),
                "btc_dominance": global_data.get("data", {}).get("market_cap_percentage", {}).get("btc", 0),
                "eth_dominance": global_data.get("data", {}).get("market_cap_percentage", {}).get("eth", 0),
                "market_cap_change_pct_24h": global_data.get("data", {}).get("market_cap_change_percentage_24h_usd", 0),
                "active_cryptocurrencies": global_data.get("data", {}).get("active_cryptocurrencies", 0),
            }

            if fear_greed and fear_greed.get("data"):
                fg = fear_greed["data"][0]
                overview["fear_greed_index"] = int(fg.get("value", 50))
                overview["fear_greed_label"] = fg.get("value_classification", "Neutral")

            # Cache the snapshot
            snapshot = MarketSnapshot(
                snapshot_type="global",
                data=overview,
            )
            self.db.add(snapshot)
            await self.db.commit()

            return overview

        except Exception as e:
            logger.error("Failed to get market overview", error=str(e))
            return {
                "total_market_cap": 0,
                "total_volume_24h": 0,
                "btc_dominance": 0,
                "eth_dominance": 0,
                "market_cap_change_pct_24h": 0,
                "fear_greed_index": 50,
                "fear_greed_label": "Neutral",
            }

    async def get_top_movers(
        self, direction: str = "gainers", limit: int = 10
    ) -> list[Coin]:
        """Get top gainers or losers from database."""
        order = (
            Coin.price_change_pct_24h.desc()
            if direction == "gainers"
            else Coin.price_change_pct_24h.asc()
        )

        result = await self.db.execute(
            select(Coin)
            .where(Coin.price_change_pct_24h.isnot(None))
            .order_by(order)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_coins(self, query: str, limit: int = 20) -> list[Coin]:
        """Search coins by name or symbol."""
        result = await self.db.execute(
            select(Coin)
            .where(
                Coin.name.ilike(f"%{query}%") | Coin.symbol.ilike(f"%{query}%")
            )
            .order_by(Coin.market_cap_rank.asc().nullslast())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_coin_count(self) -> int:
        """Get total number of tracked coins."""
        result = await self.db.execute(select(func.count()).select_from(Coin))
        return result.scalar() or 0

    async def get_bullish_count(self) -> int:
        """Count coins with positive 24h change."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Coin)
            .where(Coin.price_change_pct_24h > 0)
        )
        return result.scalar() or 0
