"""
FastAPI application factory for the Crypto Intelligence AI Platform.

Provides `create_app()` which returns a fully-configured FastAPI instance.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.dependencies import close_redis
from app.core.exceptions import AppException
from app.core.logging_config import get_logger, setup_logging

settings = get_settings()
logger = get_logger(__name__)

# ── Rate Limiter ──────────────────────────────────────────────────────────────
# Falls back to in-memory storage if Redis is unavailable
try:
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[settings.RATE_LIMIT_DEFAULT],
        storage_uri=settings.REDIS_URL,
    )
except Exception:
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[settings.RATE_LIMIT_DEFAULT],
    )


# ── Lifespan ──────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle for the application.

    On startup:
    - Initialize structured logging
    - Verify database connectivity
    - Warm Redis connection pool

    On shutdown:
    - Close Redis connection pool
    - (DB engine is garbage-collected)
    """
    # ── Startup ───────────────────────────────────────────────────────────
    setup_logging()
    logger.info(
        "application_starting",
        env=settings.APP_ENV,
        debug=settings.DEBUG,
        log_level=settings.LOG_LEVEL,
    )

    # Verify database connectivity (best-effort — the app can start without DB)
    try:
        from sqlalchemy import text
        from app.models.base import get_engine

        async with get_engine().begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("database_connected", url=settings.DATABASE_URL.split("@")[-1])
    except Exception as exc:
        logger.warning("database_connection_failed", error=str(exc))

    # Pre-warm Redis (best-effort)
    try:
        from app.core.dependencies import get_redis

        redis = await get_redis()
        await redis.ping()
        logger.info("redis_connected", url=settings.REDIS_URL)
    except Exception as exc:
        logger.warning("redis_connection_failed", error=str(exc))

    yield  # Application runs here

    # ── Shutdown ──────────────────────────────────────────────────────────
    logger.info("application_shutting_down")
    await close_redis()
    logger.info("application_stopped")


# ── Application Factory ───────────────────────────────────────────────────────


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns a fully-configured FastAPI instance ready to be served by uvicorn:

        uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="AI-powered cryptocurrency intelligence and prediction platform",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG or settings.is_development else None,
        redoc_url="/redoc" if settings.DEBUG or settings.is_development else None,
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS Middleware ───────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-Client-Version",
        ],
        expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
    )

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(api_v1_router)

    # ── Health Check ──────────────────────────────────────────────────────────
    @app.get("/health", include_in_schema=False)
    async def health_check():
        return {"status": "healthy", "version": "1.0.0", "environment": settings.APP_ENV}

    # ── Exception Handlers ────────────────────────────────────────────────────
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """Handle all custom application exceptions."""
        logger.warning(
            "app_exception",
            error_code=exc.error_code,
            message=exc.message,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Catch-all for unexpected errors."""
        logger.error(
            "unhandled_exception",
            error=str(exc),
            error_type=type(exc).__name__,
            path=request.url.path,
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "detail": {"error": str(exc)} if settings.DEBUG else {},
            },
        )

    return app
