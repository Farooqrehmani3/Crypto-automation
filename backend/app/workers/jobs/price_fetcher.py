"""
ARQ Worker Job: Price Fetcher

Periodically fetches latest cryptocurrency prices from CoinGecko
and stores them in the database. Runs every 60 seconds for top 100 coins.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from structlog import get_logger

from app.core.config import settings
from app.models.coin import Coin, CoinPrice
from app.integrations.coingecko import coingecko_client

logger = get_logger(__name__)


async def fetch_prices_job(ctx: dict) -> dict:
    """Fetch latest prices for all tracked coins and store them.

    This job:
    1. Fetches top 100 coins from CoinGecko
    2. Updates coin metadata (price, market cap, volume, change %)
    3. Stores new OHLCV candles for 1d timeframe
    """
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as db:
            # Fetch from CoinGecko
            logger.info("Fetching coin prices from CoinGecko...")
            coins_data = await coingecko_client.get_coins_markets(
                per_page=100,
                sparkline=True,
            )

            updated_count = 0
            for data in coins_data:
                coin_id = data.get("id")
                if not coin_id:
                    continue

                # Find or create coin
                result = await db.execute(
                    select(Coin).where(Coin.coin_id == coin_id)
                )
                coin = result.scalar_one_or_none()

                if not coin:
                    coin = Coin(coin_id=coin_id)

                # Update metadata
                coin.symbol = data.get("symbol", "").lower()
                coin.name = data.get("name", "")
                coin.image_url = data.get("image")
                coin.market_cap_rank = data.get("market_cap_rank")
                coin.current_price = data.get("current_price")
                coin.market_cap = data.get("market_cap")
                coin.total_volume = data.get("total_volume")
                coin.price_change_24h = data.get("price_change_24h")
                coin.price_change_pct_24h = data.get("price_change_percentage_24h_in_currency") or data.get("price_change_percentage_24h")
                coin.price_change_pct_7d = data.get("price_change_percentage_7d_in_currency")
                coin.price_change_pct_30d = data.get("price_change_percentage_30d_in_currency")
                coin.circulating_supply = data.get("circulating_supply")
                coin.total_supply = data.get("total_supply")
                coin.max_supply = data.get("max_supply")
                coin.ath = data.get("ath")
                coin.ath_date = data.get("ath_date")
                coin.atl = data.get("atl")
                coin.atl_date = data.get("atl_date")

                # Sparkline data
                sparkline = data.get("sparkline_7d", {}).get("price", [])
                if sparkline:
                    coin.sparkline_7d = sparkline

                coin.last_updated = datetime.utcnow()
                db.add(coin)

                # Store price candle if we have OHLC data
                if all(k in data for k in ["high_24h", "low_24h"]):
                    price = CoinPrice(
                        coin_id=coin.id,
                        timestamp=datetime.utcnow(),
                        timeframe="1d",
                        open=coin.current_price - (coin.price_change_24h or 0),
                        high=data.get("high_24h", coin.current_price),
                        low=data.get("low_24h", coin.current_price),
                        close=coin.current_price,
                        volume=data.get("total_volume", 0),
                    )
                    db.add(price)

                updated_count += 1

            await db.commit()
            logger.info("Price fetch completed", coins_updated=updated_count)

            return {
                "status": "success",
                "coins_updated": updated_count,
                "timestamp": datetime.utcnow().isoformat(),
            }

    except Exception as e:
        logger.error("Price fetch failed", error=str(e))
        return {"status": "error", "error": str(e)}

    finally:
        await engine.dispose()
