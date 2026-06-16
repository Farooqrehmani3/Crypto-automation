"""
News Pydantic schemas.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ── News ──────────────────────────────────────────────────────────────────────


class NewsResponse(BaseModel):
    """A single news article."""

    id: UUID
    source: str
    title: str
    url: str
    summary: str | None = None
    author: str | None = None
    image_url: str | None = None
    published_at: str
    language: str = "en"
    categories: str | None = None
    relevance_score: float | None = None
    is_breaking: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class NewsDetailResponse(NewsResponse):
    """News article with full content, sentiment, and related coins."""

    content: str | None = None
    coins: list[dict] = Field(default_factory=list, description="Related coins")
    sentiment: dict | None = Field(default=None, description="Sentiment analysis result")


class NewsSentimentResponse(BaseModel):
    """Sentiment analysis response for a news article."""

    id: UUID
    news_id: UUID
    overall_sentiment: str
    sentiment_score: float
    confidence: float
    summary: str | None = None
    key_points: list[str] | None = None
    model_used: str
    processing_time_ms: int | None = None

    model_config = {"from_attributes": True}


class NewsQueryParams(BaseModel):
    """Query parameters for listing news."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    source: str | None = None
    coin_id: UUID | None = None
    is_breaking: bool | None = None
    sentiment: str | None = Field(default=None, description="positive | negative | neutral")
    language: str | None = None
    sort_by: str = Field(
        default="published_at", description="published_at | relevance_score | created_at"
    )
    sort_order: str = Field(default="desc", description="asc | desc")
