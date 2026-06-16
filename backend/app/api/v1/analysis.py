"""
AI Analysis endpoints.

Phase 1 provides stub endpoints. Full AI analysis integration
(OpenAI, ML models) comes in Phase 2.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select

from app.core.dependencies import DB
from app.core.exceptions import NotFoundException
from app.models.analysis import AnalysisLog, AIPrediction
from app.schemas.analysis import (
    AnalysisLogQueryParams,
    AnalysisLogResponse,
    AIPredictionResponse,
    AIPredictionSummary,
)
from app.schemas.common import ErrorResponse, PaginatedResponse, SuccessResponse

router = APIRouter()


@router.get(
    "/analysis/logs",
    response_model=PaginatedResponse[AnalysisLogResponse],
    summary="List AI analysis logs",
    description="History of AI analysis runs with filtering by coin and type.",
)
async def list_analysis_logs(
    db: DB,
    params: AnalysisLogQueryParams = Depends(),
) -> PaginatedResponse[AnalysisLogResponse]:
    query = select(AnalysisLog)

    if params.coin_id:
        query = query.where(AnalysisLog.coin_id == params.coin_id)
    if params.analysis_type:
        query = query.where(AnalysisLog.analysis_type == params.analysis_type)

    query = query.order_by(AnalysisLog.created_at.desc())

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (params.page - 1) * params.page_size
    query = query.offset(offset).limit(params.page_size)

    result = await db.execute(query)
    logs = result.scalars().all()

    items = [AnalysisLogResponse.model_validate(log) for log in logs]
    return PaginatedResponse.create(
        items=items, total=total, page=params.page, page_size=params.page_size
    )


@router.get(
    "/analysis/logs/{log_id}",
    response_model=SuccessResponse[AnalysisLogResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Get an analysis log",
)
async def get_analysis_log(
    log_id: UUID,
    db: DB,
) -> SuccessResponse[AnalysisLogResponse]:
    result = await db.execute(
        select(AnalysisLog).where(AnalysisLog.id == log_id)
    )
    log = result.scalar_one_or_none()

    if log is None:
        raise NotFoundException(message="Analysis log not found")

    return SuccessResponse(data=AnalysisLogResponse.model_validate(log))


@router.get(
    "/analysis/predictions",
    response_model=PaginatedResponse[AIPredictionResponse],
    summary="List AI predictions",
    description="AI-generated predictions with filtering by coin and timeframe.",
)
async def list_predictions(
    db: DB,
    coin_id: UUID | None = Query(default=None),
    target_timeframe: str | None = Query(default=None, description="1h | 4h | 24h | 7d | 30d"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[AIPredictionResponse]:
    query = select(AIPrediction)

    if coin_id:
        query = query.where(AIPrediction.coin_id == coin_id)
    if target_timeframe:
        query = query.where(AIPrediction.target_timeframe == target_timeframe)

    query = query.order_by(AIPrediction.created_at.desc())

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    predictions = result.scalars().all()

    items = [AIPredictionResponse.model_validate(p) for p in predictions]
    return PaginatedResponse.create(
        items=items, total=total, page=page, page_size=page_size
    )


@router.get(
    "/analysis/predictions/{coin_id}/latest",
    response_model=SuccessResponse[AIPredictionResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Get latest prediction for a coin",
)
async def get_latest_prediction(
    coin_id: UUID,
    db: DB,
    target_timeframe: str = Query(default="24h", description="1h | 4h | 24h | 7d | 30d"),
) -> SuccessResponse[AIPredictionResponse]:
    result = await db.execute(
        select(AIPrediction)
        .where(
            AIPrediction.coin_id == coin_id,
            AIPrediction.target_timeframe == target_timeframe,
        )
        .order_by(AIPrediction.created_at.desc())
        .limit(1)
    )
    prediction = result.scalar_one_or_none()

    if prediction is None:
        raise NotFoundException(message="No prediction found for this coin and timeframe")

    return SuccessResponse(data=AIPredictionResponse.model_validate(prediction))


# Placeholder for triggering a new analysis (Phase 2)
@router.post(
    "/analysis/run/{coin_id}",
    response_model=SuccessResponse[dict],
    status_code=202,
    summary="Trigger AI analysis for a coin",
    description="Phase 2: Trigger an AI analysis run for the given coin.",
)
async def trigger_analysis(
    coin_id: UUID,
) -> SuccessResponse[dict]:
    return SuccessResponse(
        data={"coin_id": str(coin_id), "status": "queued"},
        message="Analysis job queued (Phase 2 implementation pending)",
    )
