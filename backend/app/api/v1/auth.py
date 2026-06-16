"""
Authentication endpoints.

All authentication is delegated to Supabase Auth. This module provides
a token-verification endpoint so the frontend can validate JWTs.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header

from app.core.dependencies import CurrentUser
from app.core.security import verify_supabase_jwt
from app.schemas.common import ErrorResponse, SuccessResponse
from app.schemas.user import UserInfo

router = APIRouter()


@router.get(
    "/auth/verify",
    response_model=SuccessResponse[UserInfo],
    responses={401: {"model": ErrorResponse}},
    summary="Verify JWT token",
    description="Validate the Supabase-issued JWT from the Authorization header "
    "and return the authenticated user's profile.",
)
async def verify_auth(
    user: CurrentUser,
) -> SuccessResponse[UserInfo]:
    user_info = UserInfo(
        id=user["sub"],
        email=user.get("email"),
        role=user.get("role", "authenticated"),
        metadata=user.get("user_metadata", {}),
    )
    return SuccessResponse(data=user_info, message="Token is valid")


@router.get(
    "/auth/session",
    response_model=SuccessResponse[UserInfo],
    responses={401: {"model": ErrorResponse}},
    summary="Get current session",
    description="Return the current user session info from the JWT.",
)
async def get_session(
    user: CurrentUser,
) -> SuccessResponse[UserInfo]:
    user_info = UserInfo(
        id=user["sub"],
        email=user.get("email"),
        role=user.get("role", "authenticated"),
        metadata=user.get("user_metadata", {}),
    )
    return SuccessResponse(data=user_info, message="Session active")
