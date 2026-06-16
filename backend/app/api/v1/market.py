"""
Market data endpoints.

Phase 1 provides stub implementations with placeholder responses.
Full CoinGecko integration comes in Phase 2.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func

from app.core.dependencies import DB
from app.models.analysis import MarketSnapshot
from app.models.coin import Coin
from app.schemas.common import ErrorResponse, PaginatedResponse, SuccessResponse
from app.schemas.market import (
    MarketGlobalStats,
    MarketOverviewResponse,
    MarketSearchResponse,
    MarketSearchResult,
    TopMover,
    TopMoversResponse,
    TrendingCoin,
    TrendingResponse,
)
from app.schemas.coin import CoinSearchResult

router = APIRouter()


@router.get(
    "/market/overview",
    response_model=SuccessResponse[MarketOverviewResponse],
    summary="Get market overview",
    description="Current global crypto market summary including fear & greed index.",
)
async def get_market_overview(
    db: DB,
) -> SuccessResponse[MarketOverviewResponse]:
    # Try to get the latest market snapshot
    result = await db.execute(
        select(MarketSnapshot)
        .order_by(MarketSnapshot.created_at.desc())
        .limit(1)
    )
    snapshot = result.scalar_one_or_none()

    if snapshot is not None:
        overview = MarketOverviewResponse(
            total_market_cap_usd=snapshot.total_market_cap_usd,
            total_volume_24h_usd=snapshot.total_volume_24h_usd,
            btc_dominance_percent=snapshot.btc_dominance_percent,
            eth_dominance_percent=snapshot.eth_dominance_percent,
            active_cryptocurrencies=snapshot.active_cryptocurrencies,
            fear_greed_index=snapshot.fear_greed_index,
            fear_greed_classification=snapshot.fear_greed_classification,
            last_updated=snapshot.created_at,
        )
        return SuccessResponse(data=overview)

    # Return placeholder data when no snapshot exists
    placeholder = MarketOverviewResponse(
        total_market_cap_usd=0.0,
        total_volume_24h_usd=0.0,
        btc_dominance_percent=0.0,
        last_updated=datetime.now(timezone.utc),
    )
    return SuccessResponse(
        data=placeholder,
        message="Market data not yet synced. Data pipeline will populate soon.",
    )


@router.get(
    "/market/trending",
    response_model=SuccessResponse[TrendingResponse],
    summary="Get trending coins",
    description="Top-15 trending cryptocurrencies (placeholder in Phase 1).",
)
async def get_trending(
    db: DB,
) -> SuccessResponse[TrendingResponse]:
    # Return top coins by market cap as a proxy for "trending" in Phase 1
    result = await db.execute(
        select(Coin)
        .where(Coin.is_active == True, Coin.deleted_at.is_(None))
        .order_by(Coin.market_cap_rank.asc().nullslast())
        .limit(15)
    )
    coins = result.scalars().all()

    trending = [
        TrendingCoin(
            coin_id=str(c.id),
            symbol=c.symbol,
            name=c.name,
            market_cap_rank=c.market_cap_rank,
            image_url=c.image_url,
            current_price_usd=c.current_price_usd,
            price_change_24h_percent=c.price_change_24h_percent,
            market_cap_usd=c.market_cap_usd,
        )
        for c in coins
    ]

    return SuccessResponse(
        data=TrendingResponse(
            coins=trending,
            last_updated=datetime.now(timezone.utc),
        )
    )


@router.get(
    "/market/top-movers",
    response_model=SuccessResponse[TopMoversResponse],
    summary="Get top movers",
    description="Top gainers and losers by 24h price change.",
)
async def get_top_movers(
    db: DB,
    limit: int = Query(default=10, ge=1, le=50),
) -> SuccessResponse[TopMoversResponse]:
    # Top gainers
    gainers_result = await db.execute(
        select(Coin)
        .where(
            Coin.is_active == True,
            Coin.deleted_at.is_(None),
            Coin.price_change_24h_percent > 0,
        )
        .order_by(Coin.price_change_24h_percent.desc().nullslast())
        .limit(limit)
    )
    gainers = gainers_result.scalars().all()

    # Top losers
    losers_result = await db.execute(
        select(Coin)
        .where(
            Coin.is_active == True,
            Coin.deleted_at.is_(None),
            Coin.price_change_24h_percent < 0,
        )
        .order_by(Coin.price_change_24h_percent.asc().nullslast())
        .limit(limit)
    )
    losers = losers_result.scalars().all()

    def _to_mover(c: Coin) -> TopMover:
        return TopMover(
            coin_id=str(c.id),
            symbol=c.symbol,
            name=c.name,
            image_url=c.image_url,
            current_price_usd=c.current_price_usd,
            price_change_24h_percent=c.price_change_24h_percent,
            market_cap_usd=c.market_cap_usd,
            market_cap_rank=c.market_cap_rank,
        )

    return SuccessResponse(
        data=TopMoversResponse(
            gainers=[_to_mover(c) for c in gainers],
            losers=[_to_mover(c) for c in losers],
            last_updated=datetime.now(timezone.utc),
        )
    )


@router.get(
    "/market/search",
    response_model=SuccessResponse[MarketSearchResponse],
    summary="Search coins",
    description="Search for coins by name or symbol.",
)
async def search_market(
    db: DB,
    query: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
) -> SuccessResponse[MarketSearchResponse]:
    search_term = f"%{query}%"
    result = await db.execute(
        select(Coin)
        .where(
            Coin.deleted_at.is_(None),
            Coin.is_active == True,
            (Coin.name.ilike(search_term)) | (Coin.symbol.ilike(search_term)),
        )
        .order_by(Coin.market_cap_rank.asc().nullslast())
        .limit(limit)
    )
    coins = result.scalars().all()

    results = [
        MarketSearchResult(
            id=str(c.id),
            name=c.name,
            symbol=c.symbol,
            market_cap_rank=c.market_cap_rank,
            image_url=c.image_url,
        )
        for c in coins
    ]

    return SuccessResponse(
        data=MarketSearchResponse(
            results=results,
            query=query,
            total=len(results),
        )
    )
