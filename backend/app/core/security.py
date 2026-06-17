"""
JWT verification against Supabase auth and admin authentication.

The application delegates user authentication to Supabase Auth.  Clients
pass the Supabase-issued JWT in the Authorization header and we verify
it using the Supabase client and/or the JWT secret.

Admin authentication uses a separate hardcoded credential check with its own
JWT issuance.
"""

from __future__ import annotations

import hmac
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from jose import jwt
from supabase import create_client as create_supabase_client

from app.core.config import get_settings

settings = get_settings()

# ── Admin token helpers ───────────────────────────────────────────────────────

_ADMIN_JWT_ALGORITHM = "HS256"
_ADMIN_TOKEN_EXPIRY_HOURS = 12


def _constant_time_compare(a: str, b: str) -> bool:
    """Compare two strings in constant time to prevent timing attacks."""
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def verify_admin_credentials(username: str, password: str) -> bool:
    """Verify admin credentials using constant-time comparison.

    Returns True if the username and password match the configured admin
    credentials.
    """
    return _constant_time_compare(username, settings.ADMIN_USERNAME) and _constant_time_compare(
        password, settings.ADMIN_PASSWORD
    )


def create_admin_token(username: str) -> str:
    """Create a signed JWT for an authenticated admin session.

    The token includes role="admin" and is valid for the configured expiry.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": f"admin:{username}",
        "username": username,
        "role": "admin",
        "iat": now,
        "exp": now + timedelta(hours=_ADMIN_TOKEN_EXPIRY_HOURS),
        "type": "admin",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=_ADMIN_JWT_ALGORITHM)


def verify_admin_token(token: str) -> dict:
    """Decode and validate an admin JWT.

    Returns the decoded payload if valid.

    Raises:
        HTTPException 401: If the token is invalid, expired, or not an admin token.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing admin authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[_ADMIN_JWT_ALGORITHM])
        if payload.get("type") != "admin" or payload.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _get_supabase_client():
    """Create a Supabase client using the service-role key (server-side)."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        return None
    return create_supabase_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


async def verify_supabase_jwt(token: str) -> dict:
    """Verify a Supabase-issued JWT and return the decoded payload.

    Args:
        token: The raw JWT string.

    Returns:
        Decoded JWT payload dict containing at least `sub` (user id), `email`,
        `aud`, and `role`.

    Raises:
        HTTPException 401: If the token is invalid or expired.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    client = _get_supabase_client()
    if client is not None:
        try:
            # The Supabase Python client verifies the token via the GoTrue /auth/v1/user endpoint
            response = client.auth.get_user(token)
            if response and response.user:
                return {
                    "sub": response.user.id,
                    "email": response.user.email,
                    "role": getattr(response.user, "role", "authenticated"),
                    "aud": "authenticated",
                    "user_metadata": getattr(response.user, "user_metadata", {}),
                }
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Fallback: decode manually with JWT secret
    if settings.SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
            return payload
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication configuration error",
    )


async def get_current_user(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> dict:
    """FastAPI dependency that extracts and verifies the current user from the
    Authorization header.

    Usage:
        @router.get("/me")
        async def get_me(user: dict = Depends(get_current_user)):
            ...

    Returns:
        Decoded JWT payload with user information.

    Raises:
        HTTPException 401: If the Authorization header is missing or the token
            is invalid.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await verify_supabase_jwt(token)


async def get_current_user_id(
    user: dict = Depends(get_current_user),
) -> str:
    """Convenience dependency that returns only the user ID."""
    return user["sub"]


async def get_current_admin(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> dict:
    """FastAPI dependency that extracts and verifies an admin JWT.

    Usage:
        @router.get("/admin/dashboard")
        async def admin_dashboard(admin: dict = Depends(get_current_admin)):
            ...

    Returns:
        Decoded admin JWT payload with username and role.

    Raises:
        HTTPException 401: If the token is missing, invalid, expired, or not an
            admin token.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return verify_admin_token(token)


# Re-export for cleaner imports
__all__ = [
    "verify_supabase_jwt",
    "get_current_user",
    "get_current_user_id",
    "verify_admin_credentials",
    "create_admin_token",
    "verify_admin_token",
    "get_current_admin",
]
