"""
CoinGecko API Integration Client

Provides rate-limited, cached access to CoinGecko API v3.
Supports free tier (no API key) and pro tier (with API key).
"""

import asyncio
import time
from typing import Optional, Any
from datetime import datetime, timedelta

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from structlog import get_logger

from app.core.config import settings

logger = get_logger(__name__)

# Rate limiting: CoinGecko free tier allows ~10-30 calls/min
RATE_LIMIT_CALLS = 25  # calls per window
RATE_LIMIT_WINDOW = 60  # seconds


class CoinGeckoClient:
    """Async CoinGecko API client with rate limiting and caching."""

    def __init__(self):
        self.base_url = settings.COINGECKO_API_URL or "https://api.coingecko.com/api/v3"
        self.api_key = settings.COINGECKO_API_KEY
        self._cache: dict[str, tuple[Any, float]] = {}
        self._cache_ttl = 30  # seconds for price data
        self._long_cache_ttl = 3600  # seconds for metadata
        self._rate_limit_timestamps: list[float] = []
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            headers = {}
            if self.api_key:
                headers["x-cg-pro-api-key"] = self.api_key
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=30.0,
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _check_cache(self, key: str) -> Optional[Any]:
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return data
        return None

    def _set_cache(self, key: str, data: Any, long: bool = False):
        ttl = self._long_cache_ttl if long else self._cache_ttl
        self._cache[key] = (data, time.time() + ttl)

    async def _rate_limit(self):
        """Simple sliding window rate limiter."""
        now = time.time()
        # Remove timestamps outside window
        self._rate_limit_timestamps = [
            ts for ts in self._rate_limit_timestamps
            if now - ts < RATE_LIMIT_WINDOW
        ]
        if len(self._rate_limit_timestamps) >= RATE_LIMIT_CALLS:
            sleep_time = self._rate_limit_timestamps[0] + RATE_LIMIT_WINDOW - now + 1
            if sleep_time > 0:
                logger.debug("Rate limit: sleeping", seconds=sleep_time)
                await asyncio.sleep(sleep_time)
        self._rate_limit_timestamps.append(time.time())

    async def _request(self, endpoint: str, params: dict = None) -> dict:
        """Make a rate-limited API request with retry logic."""
        await self._rate_limit()

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError)),
        )
        async def _do_request():
            client = await self._get_client()
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()

        return await _do_request()

    # ---- Coin Data ----

    async def get_coins_markets(
        self,
        vs_currency: str = "usd",
        per_page: int = 100,
        page: int = 1,
        sparkline: bool = True,
        price_change_percentage: str = "24h,7d,30d",
        category: str = None,
    ) -> list[dict]:
        """Get list of coins with market data."""
        cache_key = f"markets:{vs_currency}:{per_page}:{page}:{sparkline}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": str(sparkline).lower(),
            "price_change_percentage": price_change_percentage,
        }
        if category:
            params["category"] = category

        data = await self._request("/coins/markets", params)
        self._set_cache(cache_key, data)
        return data

    async def get_coin_detail(self, coin_id: str) -> dict:
        """Get detailed coin information."""
        cache_key = f"coin:{coin_id}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        params = {
            "localization": "false",
            "tickers": "false",
            "community_data": "false",
            "developer_data": "false",
        }
        data = await self._request(f"/coins/{coin_id}", params)
        self._set_cache(cache_key, data, long=True)
        return data

    async def get_coin_ohlc(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: str = "30",
    ) -> list[list[float]]:
        """Get OHLC data for a coin.
        Returns: [[timestamp, open, high, low, close], ...]
        """
        cache_key = f"ohlc:{coin_id}:{days}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        data = await self._request(
            f"/coins/{coin_id}/ohlc",
            params={"vs_currency": vs_currency, "days": days},
        )
        self._set_cache(cache_key, data)
        return data

    async def get_coin_market_chart(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: str = "30",
    ) -> dict:
        """Get historical market data (prices, market caps, volumes)."""
        cache_key = f"chart:{coin_id}:{days}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        data = await self._request(
            f"/coins/{coin_id}/market_chart",
            params={"vs_currency": vs_currency, "days": days},
        )
        self._set_cache(cache_key, data)
        return data

    # ---- Market Data ----

    async def get_global_data(self) -> dict:
        """Get global cryptocurrency market data."""
        cached = self._check_cache("global")
        if cached:
            return cached

        data = await self._request("/global")
        self._set_cache("global", data)
        return data

    async def get_trending(self) -> dict:
        """Get trending coins."""
        cached = self._check_cache("trending")
        if cached:
            return cached

        data = await self._request("/search/trending")
        self._set_cache("trending", data, long=True)
        return data

    async def search(self, query: str) -> dict:
        """Search for coins, categories, and exchanges."""
        data = await self._request("/search", params={"query": query})
        return data

    async def get_fear_greed_index(self) -> Optional[dict]:
        """Get Fear & Greed Index for crypto (alternative API)."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.alternative.me/fng/",
                    params={"limit": 1},
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning("Failed to fetch Fear & Greed Index", error=str(e))
            return None

    async def get_top_gainers_losers(
        self, vs_currency: str = "usd", limit: int = 10
    ) -> dict[str, list[dict]]:
        """Get top gainers and losers by 24h price change."""
        # Fetch top 250 coins and sort by price change
        all_coins = await self.get_coins_markets(
            vs_currency=vs_currency,
            per_page=250,
            sparkline=True,
        )

        sorted_coins = sorted(
            all_coins,
            key=lambda x: x.get("price_change_percentage_24h", 0) or 0,
            reverse=True,
        )

        return {
            "gainers": sorted_coins[:limit],
            "losers": sorted_coins[-limit:][::-1],
        }


# Singleton instance
coingecko_client = CoinGeckoClient()
