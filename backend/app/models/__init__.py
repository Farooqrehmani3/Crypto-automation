"""
SQLAlchemy ORM models — central import point.

Importing all models here ensures Alembic autogenerate can detect them.
"""

from app.models.base import (
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    AllMixins,
    engine,
    async_session_factory,
    NAMING_CONVENTION,
)
from app.models.coin import Coin, CoinPrice
from app.models.watchlist import Watchlist, WatchlistItem
from app.models.portfolio import Portfolio, PortfolioAsset, PortfolioTransaction
from app.models.news import News, NewsCoin, NewsSentiment
from app.models.analysis import AnalysisLog, AIPrediction, CoinForecast, MarketSnapshot
from app.models.user import UserPreference

__all__ = [
    # Base
    "Base",
    "UUIDPrimaryKeyMixin",
    "TimestampMixin",
    "SoftDeleteMixin",
    "AllMixins",
    "engine",
    "async_session_factory",
    "NAMING_CONVENTION",
    # Core models
    "Coin",
    "CoinPrice",
    # User models
    "Watchlist",
    "WatchlistItem",
    "Portfolio",
    "PortfolioAsset",
    "PortfolioTransaction",
    "UserPreference",
    # Content models
    "News",
    "NewsCoin",
    "NewsSentiment",
    # Analysis models
    "AnalysisLog",
    "AIPrediction",
    "CoinForecast",
    "MarketSnapshot",
]
