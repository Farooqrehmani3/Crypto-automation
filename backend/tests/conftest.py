"""
Pytest fixtures for the Crypto Intelligence API test suite.

Provides:
- A fully-configured async HTTPX test client (AsyncClient)
- Database session management with automatic rollback
- A test application override fixture
- Mock user authentication tokens
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.main import create_app
from app.models.base import Base

settings = get_settings()

# ── Test Database Engine ──────────────────────────────────────────────────────
# Use a separate test database (append _test to the DB name).
# Falls back to an in-memory SQLite if PostgreSQL is unavailable for CI.

_test_url = settings.DATABASE_URL
if "crypto_intelligence" in _test_url:
    _test_url = _test_url.replace("crypto_intelligence", "crypto_intelligence_test")

test_engine = create_async_engine(
    _test_url,
    echo=False,
    poolclass=NullPool,
)

TestSessionFactory = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(loop_scope="session")
async def _test_db_setup():
    """Create all tables before tests and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(_test_db_setup) -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session that rolls back after each test."""
    async with TestSessionFactory() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest_asyncio.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP test client for the FastAPI app."""
    app = create_app()

    # Override the get_db dependency to use the test session
    from app.core.dependencies import get_db

    async def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_user_id() -> str:
    """Return a consistent test user ID."""
    return str(uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"))


@pytest.fixture
def mock_jwt_payload(test_user_id: str) -> dict[str, Any]:
    """Return a mock Supabase JWT payload for testing."""
    return {
        "sub": test_user_id,
        "email": "test@example.com",
        "role": "authenticated",
        "aud": "authenticated",
        "user_metadata": {
            "display_name": "Test User",
        },
    }


@pytest.fixture
def auth_headers(mock_jwt_payload: dict[str, Any]) -> dict[str, str]:
    """Return authorization headers with a mock token.

    In integration tests, the security dependency should be overridden
    to return mock_jwt_payload rather than verifying a real token.
    """
    return {"Authorization": "Bearer test-mock-token"}


@pytest_asyncio.fixture
async def override_auth(client, mock_jwt_payload):
    """Override the get_current_user dependency for authenticated test requests."""
    from app.core.dependencies import get_current_user

    async def _get_mock_user():
        return mock_jwt_payload

    client._transport.app.dependency_overrides[get_current_user] = _get_mock_user
    yield
    client._transport.app.dependency_overrides.pop(get_current_user, None)


# ── Model Factories ───────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def seed_coin(db_session) -> dict:
    """Insert a test coin and return its data."""
    from app.models.coin import Coin

    coin = Coin(
        coingecko_id="bitcoin",
        symbol="btc",
        name="Bitcoin",
        image_url="https://example.com/btc.png",
        market_cap_rank=1,
        current_price_usd=50000.0,
        market_cap_usd=1_000_000_000_000.0,
        total_volume_usd=30_000_000_000.0,
        price_change_24h_percent=2.5,
        is_active=True,
    )
    db_session.add(coin)
    await db_session.flush()
    return {"id": coin.id, "symbol": coin.symbol, "name": coin.name}
