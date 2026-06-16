"""
News, NewsCoin, and NewsSentiment ORM models.

Tracks crypto-related news articles and their sentiment analysis results.
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AllMixins, Base, UUIDPrimaryKeyMixin


class News(Base, AllMixins):
    """A news article fetched from external sources."""

    __tablename__ = "news_articles"

    external_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=True, index=True, doc="ID from source API"
    )
    source: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, doc="newsapi | cryptopanic | rss"
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(2000), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(String(200), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    published_at: Mapped[str] = mapped_column(nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    categories: Mapped[str | None] = mapped_column(String(500), nullable=True, doc="Comma-separated")
    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True, doc="0-1 relevance to crypto")
    is_breaking: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    coins: Mapped[list["NewsCoin"]] = relationship(
        "NewsCoin", back_populates="news", cascade="all, delete-orphan", lazy="selectin"
    )
    sentiments: Mapped[list["NewsSentiment"]] = relationship(
        "NewsSentiment", back_populates="news", cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_news_published_source", "published_at", "source"),
        Index("ix_news_is_breaking", "is_breaking", postgresql_where="is_breaking = true"),
    )

    def __repr__(self) -> str:
        return f"<News source={self.source} title='{self.title[:60]}...'>"


class NewsCoin(Base, UUIDPrimaryKeyMixin):
    """Junction linking a news article to the coins it mentions."""

    __tablename__ = "news_coins"

    news_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("news_articles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    coin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("coins.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mention_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    news: Mapped["News"] = relationship("News", back_populates="coins")
    coin: Mapped["Coin"] = relationship("Coin", foreign_keys=[coin_id], lazy="joined")

    __table_args__ = (
        UniqueConstraint("news_id", "coin_id", name="uq_news_coin"),
    )

    def __repr__(self) -> str:
        return f"<NewsCoin news={self.news_id} coin={self.coin_id}>"


class NewsSentiment(Base, UUIDPrimaryKeyMixin):
    """Sentiment analysis result for a news article."""

    __tablename__ = "news_sentiments"

    news_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("news_articles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    overall_sentiment: Mapped[str] = mapped_column(
        String(20), nullable=False, doc="positive | negative | neutral"
    )
    sentiment_score: Mapped[float] = mapped_column(
        Float, nullable=False, doc="-1.0 (negative) to 1.0 (positive)"
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False, doc="0-1 confidence")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True, doc="AI-generated summary")
    key_points: Mapped[str | None] = mapped_column(
        Text, nullable=True, doc="JSON array of key points"
    )
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    news: Mapped["News"] = relationship("News", back_populates="sentiments")

    __table_args__ = (
        CheckConstraint(
            "sentiment_score >= -1.0 AND sentiment_score <= 1.0",
            name="ck_sentiment_score_range",
        ),
        CheckConstraint(
            "overall_sentiment IN ('positive', 'negative', 'neutral')",
            name="ck_sentiment_valid",
        ),
    )

    def __repr__(self) -> str:
        return f"<NewsSentiment {self.overall_sentiment} score={self.sentiment_score:.2f}>"

