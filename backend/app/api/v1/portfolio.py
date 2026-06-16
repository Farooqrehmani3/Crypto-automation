"""
Portfolio CRUD endpoints.

Phase 1 provides stub implementations with basic CRUD.
Full portfolio tracking comes in Phase 2.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.dependencies import CurrentUserId, DB
from app.core.exceptions import BadRequestException, NotFoundException
from app.models.coin import Coin
from app.models.portfolio import Portfolio, PortfolioAsset, PortfolioTransaction
from app.schemas.common import (
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    SuccessResponse,
)
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioResponse,
    PortfolioSummary,
    PortfolioTransactionCreate,
    PortfolioTransactionResponse,
    PortfolioUpdate,
)

router = APIRouter()


# ── Portfolio CRUD ────────────────────────────────────────────────────────────


@router.get(
    "/portfolios",
    response_model=PaginatedResponse[PortfolioSummary],
    summary="List user portfolios",
)
async def list_portfolios(
    db: DB,
    user_id: CurrentUserId,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[PortfolioSummary]:
    query = (
        select(Portfolio)
        .where(Portfolio.user_id == user_id, Portfolio.deleted_at.is_(None))
        .order_by(Portfolio.created_at.desc())
    )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    portfolios = result.scalars().all()

    items = [
        PortfolioSummary(
            id=p.id,
            user_id=p.user_id,
            name=p.name,
            description=p.description,
            is_default=p.is_default,
            total_value_usd=p.total_value_usd,
            total_pnl_usd=p.total_pnl_usd,
            asset_count=0,  # Phase 2: count assets
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in portfolios
    ]

    return PaginatedResponse.create(
        items=items, total=total, page=page, page_size=page_size
    )


@router.post(
    "/portfolios",
    response_model=SuccessResponse[PortfolioResponse],
    status_code=201,
    summary="Create a portfolio",
)
async def create_portfolio(
    body: PortfolioCreate,
    db: DB,
    user_id: CurrentUserId,
) -> SuccessResponse[PortfolioResponse]:
    if body.is_default:
        result = await db.execute(
            select(Portfolio).where(
                Portfolio.user_id == user_id,
                Portfolio.is_default == True,
                Portfolio.deleted_at.is_(None),
            )
        )
        for existing in result.scalars().all():
            existing.is_default = False

    portfolio = Portfolio(user_id=user_id, **body.model_dump())
    db.add(portfolio)
    await db.commit()
    await db.refresh(portfolio)

    return SuccessResponse(
        data=PortfolioResponse.model_validate(portfolio),
        message="Portfolio created",
    )


@router.get(
    "/portfolios/{portfolio_id}",
    response_model=SuccessResponse[PortfolioResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Get a portfolio with assets",
)
async def get_portfolio(
    portfolio_id: UUID,
    db: DB,
    user_id: CurrentUserId,
) -> SuccessResponse[PortfolioResponse]:
    result = await db.execute(
        select(Portfolio)
        .where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user_id,
            Portfolio.deleted_at.is_(None),
        )
        .options(selectinload(Portfolio.assets))
    )
    portfolio = result.scalar_one_or_none()

    if portfolio is None:
        raise NotFoundException(message="Portfolio not found")

    return SuccessResponse(data=PortfolioResponse.model_validate(portfolio))


@router.patch(
    "/portfolios/{portfolio_id}",
    response_model=SuccessResponse[PortfolioResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Update a portfolio",
)
async def update_portfolio(
    portfolio_id: UUID,
    body: PortfolioUpdate,
    db: DB,
    user_id: CurrentUserId,
) -> SuccessResponse[PortfolioResponse]:
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user_id,
            Portfolio.deleted_at.is_(None),
        )
    )
    portfolio = result.scalar_one_or_none()

    if portfolio is None:
        raise NotFoundException(message="Portfolio not found")

    if body.is_default and not portfolio.is_default:
        existing = await db.execute(
            select(Portfolio).where(
                Portfolio.user_id == user_id,
                Portfolio.is_default == True,
                Portfolio.deleted_at.is_(None),
            )
        )
        for p in existing.scalars().all():
            p.is_default = False

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(portfolio, key, value)

    await db.commit()
    await db.refresh(portfolio)

    return SuccessResponse(
        data=PortfolioResponse.model_validate(portfolio),
        message="Portfolio updated",
    )


@router.delete(
    "/portfolios/{portfolio_id}",
    response_model=SuccessResponse[MessageResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Delete a portfolio (soft delete)",
)
async def delete_portfolio(
    portfolio_id: UUID,
    db: DB,
    user_id: CurrentUserId,
) -> SuccessResponse[MessageResponse]:
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user_id,
            Portfolio.deleted_at.is_(None),
        )
    )
    portfolio = result.scalar_one_or_none()

    if portfolio is None:
        raise NotFoundException(message="Portfolio not found")

    from datetime import datetime, timezone
    portfolio.deleted_at = datetime.now(timezone.utc)
    await db.commit()

    return SuccessResponse(
        data=MessageResponse(message=f"Portfolio '{portfolio.name}' deleted"),
        message="Portfolio deleted",
    )


# ── Transactions (Stub) ──────────────────────────────────────────────────────


@router.post(
    "/portfolios/{portfolio_id}/transactions",
    response_model=SuccessResponse[PortfolioTransactionResponse],
    status_code=201,
    summary="Record a portfolio transaction",
    description="Phase 2: Full transaction recording with portfolio rebalancing.",
)
async def record_transaction(
    portfolio_id: UUID,
    body: PortfolioTransactionCreate,
    db: DB,
    user_id: CurrentUserId,
) -> SuccessResponse[PortfolioTransactionResponse]:
    # Verify portfolio exists and belongs to user
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user_id,
            Portfolio.deleted_at.is_(None),
        )
    )
    portfolio = result.scalar_one_or_none()
    if portfolio is None:
        raise NotFoundException(message="Portfolio not found")

    total_value = body.quantity * body.price_per_coin_usd

    txn = PortfolioTransaction(
        portfolio_id=portfolio_id,
        coin_id=body.coin_id,
        transaction_type=body.transaction_type,
        quantity=body.quantity,
        price_per_coin_usd=body.price_per_coin_usd,
        total_value_usd=total_value,
        fee_usd=body.fee_usd,
        notes=body.notes,
        transaction_date=body.transaction_date,
    )
    db.add(txn)
    await db.commit()
    await db.refresh(txn)

    return SuccessResponse(
        data=PortfolioTransactionResponse.model_validate(txn),
        message="Transaction recorded",
    )


@router.get(
    "/portfolios/{portfolio_id}/transactions",
    response_model=PaginatedResponse[PortfolioTransactionResponse],
    summary="List portfolio transactions",
)
async def list_transactions(
    portfolio_id: UUID,
    db: DB,
    user_id: CurrentUserId,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[PortfolioTransactionResponse]:
    query = (
        select(PortfolioTransaction)
        .where(PortfolioTransaction.portfolio_id == portfolio_id)
        .order_by(PortfolioTransaction.transaction_date.desc())
    )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    txns = result.scalars().all()

    items = [PortfolioTransactionResponse.model_validate(t) for t in txns]
    return PaginatedResponse.create(
        items=items, total=total, page=page, page_size=page_size
    )
