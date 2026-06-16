"""
Aggregate all v1 API routers under a single prefix with proper tags.

Each sub-module defines its own APIRouter; this module includes them all.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.coins import router as coins_router
from app.api.v1.market import router as market_router
from app.api.v1.watchlist import router as watchlist_router
from app.api.v1.portfolio import router as portfolio_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.forecasts import router as forecasts_router
from app.api.v1.news import router as news_router

api_v1_router = APIRouter(prefix="/api/v1")

# Auth & Users
api_v1_router.include_router(auth_router, tags=["Auth"])
api_v1_router.include_router(users_router, tags=["Users"])

# Market Data
api_v1_router.include_router(coins_router, tags=["Coins"])
api_v1_router.include_router(market_router, tags=["Market"])

# User Content
api_v1_router.include_router(watchlist_router, tags=["Watchlists"])
api_v1_router.include_router(portfolio_router, tags=["Portfolio"])

# AI & Analysis
api_v1_router.include_router(analysis_router, tags=["Analysis"])
api_v1_router.include_router(forecasts_router, tags=["Forecasts"])

# News
api_v1_router.include_router(news_router, tags=["News"])
