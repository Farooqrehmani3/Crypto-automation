"""
Coin Service — Business logic for coin data, prices, and statistics.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.models.coin import Coin, CoinPrice
from app.integrations.coingecko import coingecko_client

logger = get_logger(__name__)


class CoinService:
    """Service for coin-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_coin_by_id(self, coin_id: str) -> Optional[Coin]:
        """Get a coin by its CoinGecko ID (e.g., 'bitcoin')."""
        result = await self.db.execute(
            select(Coin).where(Coin.coin_id == coin_id)
        )
        return result.scalar_one_or_none()

    async def get_coin_by_uuid(self, uuid: UUID) -> Optional[Coin]:
        """Get a coin by its database UUID."""
        result = await self.db.execute(select(Coin).where(Coin.id == uuid))
        return result.scalar_one_or_none()

    async def list_coins(
        self,
        page: int = 1,
        per_page: int = 50,
        sort_by: str = "market_cap_rank",
        search: Optional[str] = None,
    ) -> tuple[list[Coin], int]:
        """Get paginated list of coins."""
        query = select(Coin)

        if search:
            query = query.where(
                Coin.name.ilike(f"%{search}%") | Coin.symbol.ilike(f"%{search}%")
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Sort
        sort_map = {
            "market_cap_rank": Coin.market_cap_rank.asc(),
            "name": Coin.name.asc(),
            "price_change_pct_24h": Coin.price_change_pct_24h.desc(),
            "market_cap": Coin.market_cap.desc(),
        }
        order_by = sort_map.get(sort_by, Coin.market_cap_rank.asc())
        query = query.order_by(order_by)

        # Paginate
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

        result = await self.db.execute(query)
        coins = result.scalars().all()

        return list(coins), total

    async def get_coin_prices(
        self,
        coin_id: str,
        timeframe: str = "1d",
        limit: int = 100,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> list[CoinPrice]:
        """Get OHLCV price data for a coin."""
        coin = await self.get_coin_by_id(coin_id)
        if not coin:
            return []

        query = select(CoinPrice).where(
            and_(
                CoinPrice.coin_id == coin.id,
                CoinPrice.timeframe == timeframe,
            )
        )

        if from_date:
            query = query.where(CoinPrice.timestamp >= from_date)
        if to_date:
            query = query.where(CoinPrice.timestamp <= to_date)

        query = query.order_by(CoinPrice.timestamp.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def sync_coin_from_coingecko(self, coin_id: str) -> Optional[Coin]:
        """Sync coin data from CoinGecko API into the database."""
        try:
            data = await coingecko_client.get_coin_detail(coin_id)
            market_data = data.get("market_data", {})

            coin = await self.get_coin_by_id(coin_id)
            if not coin:
                coin = Coin(coin_id=coin_id)

            # Update fields
            coin.symbol = data.get("symbol", "").lower()
            coin.name = data.get("name", "")
            coin.image_url = data.get("image", {}).get("large")
            coin.market_cap_rank = data.get("market_cap_rank")
            coin.current_price = market_data.get("current_price", {}).get("usd")
            coin.market_cap = market_data.get("market_cap", {}).get("usd")
            coin.total_volume = market_data.get("total_volume", {}).get("usd")
            coin.price_change_24h = market_data.get("price_change_24h")
            coin.price_change_pct_24h = market_data.get("price_change_percentage_24h")
            coin.price_change_pct_7d = market_data.get("price_change_percentage_7d")
            coin.price_change_pct_30d = market_data.get("price_change_percentage_30d")
            coin.circulating_supply = market_data.get("circulating_supply")
            coin.total_supply = market_data.get("total_supply")
            coin.max_supply = market_data.get("max_supply")
            coin.ath = market_data.get("ath", {}).get("usd")
            coin.ath_date = market_data.get("ath_date", {}).get("usd")
            coin.atl = market_data.get("atl", {}).get("usd")
            coin.atl_date = market_data.get("atl_date", {}).get("usd")
            coin.last_updated = datetime.utcnow()

            self.db.add(coin)
            await self.db.commit()
            await self.db.refresh(coin)

            logger.info("Coin synced from CoinGecko", coin_id=coin_id)
            return coin

        except Exception as e:
            logger.error("Failed to sync coin", coin_id=coin_id, error=str(e))
            await self.db.rollback()
            return None

    async def sync_coin_prices(
        self, coin_id: str, days: str = "30"
    ) -> list[CoinPrice]:
        """Sync OHLCV data from CoinGecko."""
        coin = await self.get_coin_by_id(coin_id)
        if not coin:
            return []

        try:
            ohlc_data = await coingecko_client.get_coin_ohlc(coin_id, days=days)
            prices = []

            for candle in ohlc_data:
                timestamp = datetime.fromtimestamp(candle[0] / 1000)
                price = CoinPrice(
                    coin_id=coin.id,
                    timestamp=timestamp,
                    timeframe="1d",
                    open=candle[1],
                    high=candle[2],
                    low=candle[3],
                    close=candle[4],
                    volume=0,
                )
                self.db.add(price)
                prices.append(price)

            await self.db.commit()
            logger.info(
                "Prices synced",
                coin_id=coin_id,
                count=len(prices),
            )
            return prices

        except Exception as e:
            logger.error("Failed to sync prices", coin_id=coin_id, error=str(e))
            await self.db.rollback()
            return []
