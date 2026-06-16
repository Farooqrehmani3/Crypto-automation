"""
Forecast endpoints.

Phase 1 provides stub endpoints. Full time-series forecasting
(Prophet, ML models) integration comes in Phase 2.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select

from app.core.dependencies import DB
from app.core.exceptions import NotFoundException
from app.models.analysis import CoinForecast
from app.schemas.analysis import CoinForecastResponse, ForecastPoint
from app.schemas.common import ErrorResponse, PaginatedResponse, SuccessResponse

router = APIRouter()


@router.get(
    "/forecasts",
    response_model=PaginatedResponse[CoinForecastResponse],
    summary="List all forecasts",
    description="Returns time-series forecasts for tracked coins.",
)
async def list_forecasts(
    db: DB,
    coin_id: UUID | None = Query(default=None),
    forecast_type: str | None = Query(default=None, description="price | volume | volatility"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[CoinForecastResponse]:
    query = select(CoinForecast)

    if coin_id:
        query = query.where(CoinForecast.coin_id == coin_id)
    if forecast_type:
        query = query.where(CoinForecast.forecast_type == forecast_type)

    query = query.order_by(CoinForecast.generated_at.desc())

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    forecasts = result.scalars().all()

    items: list[CoinForecastResponse] = []
    for fc in forecasts:
        points = [
            ForecastPoint.model_validate(p) if isinstance(p, dict) else p
            for p in (fc.forecast_points or [])
        ]
        items.append(
            CoinForecastResponse(
                id=fc.id,
                coin_id=fc.coin_id,
                model_name=fc.model_name,
                forecast_type=fc.forecast_type,
                horizon_days=fc.horizon_days,
                forecast_points=points,
                confidence_interval=fc.confidence_interval,
                metrics=fc.metrics or {},
                generated_at=fc.generated_at,
                valid_until=fc.valid_until,
            )
        )

    return PaginatedResponse.create(
        items=items, total=total, page=page, page_size=page_size
    )


@router.get(
    "/forecasts/{coin_id}",
    response_model=SuccessResponse[CoinForecastResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Get the latest forecast for a coin",
)
async def get_coin_forecast(
    coin_id: UUID,
    db: DB,
    forecast_type: str = Query(default="price"),
    horizon_days: int = Query(default=7, ge=1, le=365),
) -> SuccessResponse[CoinForecastResponse]:
    result = await db.execute(
        select(CoinForecast)
        .where(
            CoinForecast.coin_id == coin_id,
            CoinForecast.forecast_type == forecast_type,
            CoinForecast.horizon_days == horizon_days,
        )
        .order_by(CoinForecast.generated_at.desc())
        .limit(1)
    )
    forecast = result.scalar_one_or_none()

    if forecast is None:
        raise NotFoundException(
            message=f"No {forecast_type} forecast found for this coin "
            f"with {horizon_days}-day horizon"
        )

    points = [
        ForecastPoint.model_validate(p) if isinstance(p, dict) else p
        for p in (forecast.forecast_points or [])
    ]
    response = CoinForecastResponse(
        id=forecast.id,
        coin_id=forecast.coin_id,
        model_name=forecast.model_name,
        forecast_type=forecast.forecast_type,
        horizon_days=forecast.horizon_days,
        forecast_points=points,
        confidence_interval=forecast.confidence_interval,
        metrics=forecast.metrics or {},
        generated_at=forecast.generated_at,
        valid_until=forecast.valid_until,
    )

    return SuccessResponse(data=response)


# Placeholder: trigger forecast generation (Phase 2)
@router.post(
    "/forecasts/generate/{coin_id}",
    response_model=SuccessResponse[dict],
    status_code=202,
    summary="Generate a new forecast for a coin",
    description="Phase 2: Trigger AI/ML forecast generation.",
)
async def generate_forecast(
    coin_id: UUID,
    horizon_days: int = Query(default=7, ge=1, le=365),
) -> SuccessResponse[dict]:
    return SuccessResponse(
        data={
            "coin_id": str(coin_id),
            "horizon_days": horizon_days,
            "status": "queued",
        },
        message="Forecast generation queued (Phase 2 implementation pending)",
    )
