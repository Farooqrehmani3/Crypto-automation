"""
FastAPI dependency callables.

Provides reusable dependencies for database sessions, Redis connections,
and the current authenticated user.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import get_current_user, get_current_user_id
from app.models.base import async_session_factory

settings = get_settings()

# ── Database ──────────────────────────────────────────────────────────────────


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async SQLAlchemy session.  The session is closed automatically
    when the request scope ends."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Redis ─────────────────────────────────────────────────────────────────────

_redis_pool: Redis | None = None


async def get_redis() -> Redis:
    """Return a Redis connection from the shared connection pool.

    The pool is created once and reused across requests.
    """
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
        )
    return _redis_pool


async def close_redis() -> None:
    """Close the Redis connection pool.  Called during application shutdown."""
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.close()
        _redis_pool = None


# ── Type aliases for convenient injection ─────────────────────────────────────

DB = Annotated[AsyncSession, Depends(get_db)]
RedisDep = Annotated[Redis, Depends(get_redis)]
CurrentUser = Annotated[dict, Depends(get_current_user)]
CurrentUserId = Annotated[str, Depends(get_current_user_id)]


__all__ = [
    "get_db",
    "get_redis",
    "close_redis",
    "DB",
    "RedisDep",
    "CurrentUser",
    "CurrentUserId",
]
