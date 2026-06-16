"""
Coin endpoints.

Phase 1 provides stub implementations. Full implementation with
CoinGecko integration comes in Phase 2.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select

from app.core.dependencies import DB
from app.core.exceptions import NotFoundException
from app.models.coin import Coin, CoinPrice
from app.schemas.coin import (
    CoinListResponse,
    CoinPriceQueryParams,
    CoinPriceResponse,
    CoinQueryParams,
    CoinResponse,
    CoinStatsResponse,
)
from app.schemas.common import ErrorResponse, PaginatedResponse, SuccessResponse

router = APIRouter()


@router.get(
    "/coins",
    response_model=PaginatedResponse[CoinListResponse],
    summary="List all coins",
    description="Paginated list of tracked cryptocurrencies with filtering and sorting.",
)
async def list_coins(
    db: DB,
    params: CoinQueryParams = Depends(),
) -> PaginatedResponse[CoinListResponse]:
    query = select(Coin).where(Coin.deleted_at.is_(None))

    if params.is_active is not None:
        query = query.where(Coin.is_active == params.is_active)

    if params.search:
        search_term = f"%{params.search}%"
        query = query.where(
            (Coin.name.ilike(search_term)) | (Coin.symbol.ilike(search_term))
        )

    # Count total
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Sort
    sort_col = getattr(Coin, params.sort_by, Coin.market_cap_rank)
    if params.sort_order == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc().nullslast())

    # Paginate
    offset = (params.page - 1) * params.page_size
    query = query.offset(offset).limit(params.page_size)

    result = await db.execute(query)
    coins = result.scalars().all()

    items = [CoinListResponse.model_validate(c) for c in coins]
    return PaginatedResponse.create(
        items=items, total=total, page=params.page, page_size=params.page_size
    )


@router.get(
    "/coins/{coin_id}",
    response_model=SuccessResponse[CoinResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Get coin details",
)
async def get_coin(
    coin_id: UUID,
    db: DB,
) -> SuccessResponse[CoinResponse]:
    result = await db.execute(
        select(Coin).where(Coin.id == coin_id, Coin.deleted_at.is_(None))
    )
    coin = result.scalar_one_or_none()

    if coin is None:
        raise NotFoundException(message=f"Coin with id {coin_id} not found")

    return SuccessResponse(data=CoinResponse.model_validate(coin))


@router.get(
    "/coins/{coin_id}/prices",
    response_model=PaginatedResponse[CoinPriceResponse],
    summary="Get coin price history",
)
async def get_coin_prices(
    coin_id: UUID,
    db: DB,
    params: CoinPriceQueryParams = Depends(),
) -> PaginatedResponse[CoinPriceResponse]:
    # Verify coin exists
    exists = await db.execute(
        select(Coin.id).where(Coin.id == coin_id, Coin.deleted_at.is_(None))
    )
    if exists.scalar_one_or_none() is None:
        raise NotFoundException(message=f"Coin with id {coin_id} not found")

    query = (
        select(CoinPrice)
        .where(CoinPrice.coin_id == coin_id)
        .order_by(CoinPrice.timestamp.desc())
    )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (params.page - 1) * params.page_size
    query = query.offset(offset).limit(params.page_size)

    result = await db.execute(query)
    prices = result.scalars().all()

    items = [CoinPriceResponse.model_validate(p) for p in prices]
    return PaginatedResponse.create(
        items=items, total=total, page=params.page, page_size=params.page_size
    )


@router.get(
    "/coins/{coin_id}/stats",
    response_model=SuccessResponse[CoinStatsResponse],
    summary="Get coin statistics",
)
async def get_coin_stats(
    coin_id: UUID,
    db: DB,
) -> SuccessResponse[CoinStatsResponse]:
    result = await db.execute(
        select(Coin).where(Coin.id == coin_id, Coin.deleted_at.is_(None))
    )
    coin = result.scalar_one_or_none()

    if coin is None:
        raise NotFoundException(message=f"Coin with id {coin_id} not found")

    stats = CoinStatsResponse.model_validate(coin)
    return SuccessResponse(data=stats)
