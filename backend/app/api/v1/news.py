"""
News endpoints.

Phase 1 provides stub endpoints with database-backed listing.
Full news aggregation and sentiment analysis comes in Phase 2.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.dependencies import DB
from app.core.exceptions import NotFoundException
from app.models.news import News, NewsSentiment
from app.schemas.common import ErrorResponse, PaginatedResponse, SuccessResponse
from app.schemas.news import (
    NewsDetailResponse,
    NewsQueryParams,
    NewsResponse,
    NewsSentimentResponse,
)

router = APIRouter()


@router.get(
    "/news",
    response_model=PaginatedResponse[NewsResponse],
    summary="List news articles",
    description="Paginated list of news articles with filtering.",
)
async def list_news(
    db: DB,
    params: NewsQueryParams = Depends(),
) -> PaginatedResponse[NewsResponse]:
    query = select(News).where(News.deleted_at.is_(None))

    if params.source:
        query = query.where(News.source == params.source)
    if params.is_breaking is not None:
        query = query.where(News.is_breaking == params.is_breaking)
    if params.language:
        query = query.where(News.language == params.language)
    if params.coin_id:
        # Join through news_coins to filter by related coin
        from app.models.news import NewsCoin
        query = query.join(NewsCoin, NewsCoin.news_id == News.id).where(
            NewsCoin.coin_id == params.coin_id
        )
    if params.sentiment:
        query = query.join(NewsSentiment, NewsSentiment.news_id == News.id).where(
            NewsSentiment.overall_sentiment == params.sentiment
        )

    # Sort
    if params.sort_by == "published_at":
        query = query.order_by(
            News.published_at.desc()
            if params.sort_order == "desc"
            else News.published_at.asc()
        )
    elif params.sort_by == "relevance_score":
        query = query.order_by(
            News.relevance_score.desc().nullslast()
            if params.sort_order == "desc"
            else News.relevance_score.asc().nullslast()
        )
    else:
        query = query.order_by(News.created_at.desc())

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (params.page - 1) * params.page_size
    query = query.offset(offset).limit(params.page_size)

    result = await db.execute(query)
    articles = result.scalars().all()

    items = [NewsResponse.model_validate(a) for a in articles]
    return PaginatedResponse.create(
        items=items, total=total, page=params.page, page_size=params.page_size
    )


@router.get(
    "/news/{news_id}",
    response_model=SuccessResponse[NewsDetailResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Get a news article with full details",
)
async def get_news_article(
    news_id: UUID,
    db: DB,
) -> SuccessResponse[NewsDetailResponse]:
    result = await db.execute(
        select(News)
        .where(News.id == news_id, News.deleted_at.is_(None))
        .options(
            selectinload(News.coins),
            selectinload(News.sentiments),
        )
    )
    article = result.scalar_one_or_none()

    if article is None:
        raise NotFoundException(message="News article not found")

    # Extract related coins
    coins_data = []
    for nc in (article.coins or []):
        if nc.coin:
            coins_data.append({
                "id": str(nc.coin.id),
                "symbol": nc.coin.symbol,
                "name": nc.coin.name,
                "mention_count": nc.mention_count,
            })

    # Extract sentiment
    sentiment_data = None
    if article.sentiments:
        s = article.sentiments[0]  # One-to-one relationship
        sentiment_data = {
            "id": str(s.id),
            "overall_sentiment": s.overall_sentiment,
            "sentiment_score": s.sentiment_score,
            "confidence": s.confidence,
            "summary": s.summary,
        }

    detail = NewsDetailResponse(
        id=article.id,
        source=article.source,
        title=article.title,
        url=article.url,
        summary=article.summary,
        content=article.content,
        author=article.author,
        image_url=article.image_url,
        published_at=article.published_at,
        language=article.language,
        categories=article.categories,
        relevance_score=article.relevance_score,
        is_breaking=article.is_breaking,
        created_at=article.created_at,
        coins=coins_data,
        sentiment=sentiment_data,
    )

    return SuccessResponse(data=detail)


@router.get(
    "/news/{news_id}/sentiment",
    response_model=SuccessResponse[NewsSentimentResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Get sentiment analysis for a news article",
)
async def get_news_sentiment(
    news_id: UUID,
    db: DB,
) -> SuccessResponse[NewsSentimentResponse]:
    result = await db.execute(
        select(NewsSentiment).where(NewsSentiment.news_id == news_id)
    )
    sentiment = result.scalar_one_or_none()

    if sentiment is None:
        raise NotFoundException(message="Sentiment analysis not found for this article")

    return SuccessResponse(data=NewsSentimentResponse.model_validate(sentiment))
