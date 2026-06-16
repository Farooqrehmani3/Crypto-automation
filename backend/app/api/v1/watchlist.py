"""
Watchlist CRUD endpoints.

Full implementation for managing user watchlists and their items.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.dependencies import CurrentUserId, DB
from app.core.exceptions import BadRequestException, NotFoundException
from app.models.coin import Coin
from app.models.watchlist import Watchlist, WatchlistItem
from app.schemas.common import (
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    SuccessResponse,
)
from app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistItemCreate,
    WatchlistItemResponse,
    WatchlistItemUpdate,
    WatchlistResponse,
    WatchlistSummary,
    WatchlistUpdate,
)

router = APIRouter()

# ── Watchlist CRUD ────────────────────────────────────────────────────────────


@router.get(
    "/watchlists",
    response_model=PaginatedResponse[WatchlistSummary],
    summary="List user watchlists",
)
async def list_watchlists(
    db: DB,
    user_id: CurrentUserId,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[WatchlistSummary]:
    query = (
        select(Watchlist)
        .where(Watchlist.user_id == user_id, Watchlist.deleted_at.is_(None))
        .order_by(Watchlist.sort_order.asc(), Watchlist.created_at.desc())
    )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    watchlists = result.scalars().all()

    items = []
    for wl in watchlists:
        # Count items per watchlist
        item_count = (await db.execute(
            select(func.count()).where(
                WatchlistItem.watchlist_id == wl.id,
            )
        )).scalar() or 0
        items.append(
            WatchlistSummary(
                id=wl.id,
                user_id=wl.user_id,
                name=wl.name,
                description=wl.description,
                is_default=wl.is_default,
                sort_order=wl.sort_order,
                item_count=item_count,
                created_at=wl.created_at,
                updated_at=wl.updated_at,
            )
        )

    return PaginatedResponse.create(
        items=items, total=total, page=page, page_size=page_size
    )


@router.post(
    "/watchlists",
    response_model=SuccessResponse[WatchlistResponse],
    status_code=201,
    summary="Create a watchlist",
)
async def create_watchlist(
    body: WatchlistCreate,
    db: DB,
    user_id: CurrentUserId,
) -> SuccessResponse[WatchlistResponse]:
    # If setting as default, unset previous defaults
    if body.is_default:
        await db.execute(
            select(Watchlist).where(
                Watchlist.user_id == user_id,
                Watchlist.is_default == True,
                Watchlist.deleted_at.is_(None),
            )
        )
        # Update existing defaults
        defaults_result = await db.execute(
            select(Watchlist).where(
                Watchlist.user_id == user_id,
                Watchlist.is_default == True,
                Watchlist.deleted_at.is_(None),
            )
        )
        for existing in defaults_result.scalars().all():
            existing.is_default = False

    wl = Watchlist(user_id=user_id, **body.model_dump())
    db.add(wl)
    await db.commit()
    await db.refresh(wl)

    return SuccessResponse(
        data=WatchlistResponse.model_validate(wl),
        message="Watchlist created",
    )


@router.get(
    "/watchlists/{watchlist_id}",
    response_model=SuccessResponse[WatchlistResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Get a watchlist with items",
)
async def get_watchlist(
    watchlist_id: UUID,
    db: DB,
    user_id: CurrentUserId,
) -> SuccessResponse[WatchlistResponse]:
    result = await db.execute(
        select(Watchlist)
        .where(
            Watchlist.id == watchlist_id,
            Watchlist.user_id == user_id,
            Watchlist.deleted_at.is_(None),
        )
        .options(selectinload(Watchlist.items))
    )
    wl = result.scalar_one_or_none()

    if wl is None:
        raise NotFoundException(message="Watchlist not found")

    data = WatchlistResponse.model_validate(wl)
    data.item_count = len(wl.items)
    return SuccessResponse(data=data)


@router.patch(
    "/watchlists/{watchlist_id}",
    response_model=SuccessResponse[WatchlistResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Update a watchlist",
)
async def update_watchlist(
    watchlist_id: UUID,
    body: WatchlistUpdate,
    db: DB,
    user_id: CurrentUserId,
) -> SuccessResponse[WatchlistResponse]:
    result = await db.execute(
        select(Watchlist).where(
            Watchlist.id == watchlist_id,
            Watchlist.user_id == user_id,
            Watchlist.deleted_at.is_(None),
        )
    )
    wl = result.scalar_one_or_none()

    if wl is None:
        raise NotFoundException(message="Watchlist not found")

    if body.is_default and not wl.is_default:
        # Unset other defaults
        existing_defaults = await db.execute(
            select(Watchlist).where(
                Watchlist.user_id == user_id,
                Watchlist.is_default == True,
                Watchlist.deleted_at.is_(None),
            )
        )
        for existing in existing_defaults.scalars().all():
            existing.is_default = False

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(wl, key, value)

    await db.commit()
    await db.refresh(wl)

    return SuccessResponse(
        data=WatchlistResponse.model_validate(wl),
        message="Watchlist updated",
    )


@router.delete(
    "/watchlists/{watchlist_id}",
    response_model=SuccessResponse[MessageResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Delete a watchlist (soft delete)",
)
async def delete_watchlist(
    watchlist_id: UUID,
    db: DB,
    user_id: CurrentUserId,
) -> SuccessResponse[MessageResponse]:
    result = await db.execute(
        select(Watchlist).where(
            Watchlist.id == watchlist_id,
            Watchlist.user_id == user_id,
            Watchlist.deleted_at.is_(None),
        )
    )
    wl = result.scalar_one_or_none()

    if wl is None:
        raise NotFoundException(message="Watchlist not found")

    from datetime import datetime, timezone
    wl.deleted_at = datetime.now(timezone.utc)
    await db.commit()

    return SuccessResponse(
        data=MessageResponse(message=f"Watchlist '{wl.name}' deleted"),
        message="Watchlist deleted",
    )


# ── Watchlist Item CRUD ──────────────────────────────────────────────────────


@router.post(
    "/watchlists/{watchlist_id}/items",
    response_model=SuccessResponse[WatchlistItemResponse],
    status_code=201,
    summary="Add a coin to a watchlist",
)
async def add_watchlist_item(
    watchlist_id: UUID,
    body: WatchlistItemCreate,
    db: DB,
    user_id: CurrentUserId,
) -> SuccessResponse[WatchlistItemResponse]:
    # Verify watchlist ownership
    wl_result = await db.execute(
        select(Watchlist).where(
            Watchlist.id == watchlist_id,
            Watchlist.user_id == user_id,
            Watchlist.deleted_at.is_(None),
        )
    )
    wl = wl_result.scalar_one_or_none()
    if wl is None:
        raise NotFoundException(message="Watchlist not found")

    # Verify coin exists
    coin_result = await db.execute(
        select(Coin).where(Coin.id == body.coin_id, Coin.deleted_at.is_(None))
    )
    if coin_result.scalar_one_or_none() is None:
        raise NotFoundException(message=f"Coin with id {body.coin_id} not found")

    # Check for duplicate
    existing = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.watchlist_id == watchlist_id,
            WatchlistItem.coin_id == body.coin_id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise BadRequestException(message="Coin is already in this watchlist")

    item = WatchlistItem(watchlist_id=watchlist_id, **body.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)

    return SuccessResponse(
        data=WatchlistItemResponse.model_validate(item),
        message="Coin added to watchlist",
    )


@router.patch(
    "/watchlists/{watchlist_id}/items/{item_id}",
    response_model=SuccessResponse[WatchlistItemResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Update a watchlist item",
)
async def update_watchlist_item(
    watchlist_id: UUID,
    item_id: UUID,
    body: WatchlistItemUpdate,
    db: DB,
    user_id: CurrentUserId,
) -> SuccessResponse[WatchlistItemResponse]:
    result = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.id == item_id,
            WatchlistItem.watchlist_id == watchlist_id,
        )
    )
    item = result.scalar_one_or_none()

    if item is None:
        raise NotFoundException(message="Watchlist item not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)

    return SuccessResponse(
        data=WatchlistItemResponse.model_validate(item),
        message="Item updated",
    )


@router.delete(
    "/watchlists/{watchlist_id}/items/{item_id}",
    response_model=SuccessResponse[MessageResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Remove a coin from a watchlist",
)
async def remove_watchlist_item(
    watchlist_id: UUID,
    item_id: UUID,
    db: DB,
    user_id: CurrentUserId,
) -> SuccessResponse[MessageResponse]:
    result = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.id == item_id,
            WatchlistItem.watchlist_id == watchlist_id,
        )
    )
    item = result.scalar_one_or_none()

    if item is None:
        raise NotFoundException(message="Watchlist item not found")

    # Hard-delete watchlist items (they're join-table entities)
    await db.delete(item)
    await db.commit()

    return SuccessResponse(
        data=MessageResponse(message="Coin removed from watchlist"),
        message="Item removed",
    )
