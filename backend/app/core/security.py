"""
JWT verification against Supabase auth.

The application delegates authentication to Supabase Auth.  Clients
pass the Supabase-issued JWT in the Authorization header and we verify
it using the Supabase client and/or the JWT secret.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from supabase import create_client as create_supabase_client

from app.core.config import get_settings

settings = get_settings()


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
            from jose import jwt

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


# Re-export for cleaner imports
__all__ = [
    "verify_supabase_jwt",
    "get_current_user",
    "get_current_user_id",
]
