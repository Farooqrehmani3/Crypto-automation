"""
Authentication endpoints.

User authentication is delegated to Supabase Auth. This module provides
token-verification endpoints and a separate admin login endpoint.

Admin login uses hardcoded credentials (configured via ADMIN_USERNAME /
ADMIN_PASSWORD env vars) and issues its own JWT.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from app.core.dependencies import CurrentAdmin, CurrentUser
from app.core.security import verify_admin_credentials, create_admin_token, verify_supabase_jwt
from app.schemas.common import ErrorResponse, SuccessResponse
from app.schemas.user import UserInfo

router = APIRouter()


# ── Admin request schema ──────────────────────────────────────────────────────

class AdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64, description="Admin username")
    password: str = Field(..., min_length=1, max_length=128, description="Admin password")


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str = "admin"


# ── Admin endpoints ───────────────────────────────────────────────────────────


@router.post(
    "/auth/admin/login",
    response_model=SuccessResponse[AdminLoginResponse],
    responses={401: {"model": ErrorResponse}},
    summary="Admin login",
    description="Authenticate as an admin using username and password. "
    "Returns a JWT that can be used to access admin endpoints.",
)
async def admin_login(body: AdminLoginRequest) -> SuccessResponse[AdminLoginResponse]:
    if not verify_admin_credentials(body.username, body.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
        )

    token = create_admin_token(body.username)
    return SuccessResponse(
        data=AdminLoginResponse(
            access_token=token,
            username=body.username,
        ),
        message="Admin authenticated successfully",
    )


@router.get(
    "/auth/admin/verify",
    response_model=SuccessResponse[dict],
    responses={401: {"model": ErrorResponse}},
    summary="Verify admin JWT",
    description="Validate an admin JWT and return the admin's session info.",
)
async def verify_admin(admin: CurrentAdmin) -> SuccessResponse[dict]:
    return SuccessResponse(
        data={
            "username": admin["username"],
            "role": admin["role"],
            "exp": admin["exp"],
        },
        message="Admin token is valid",
    )


# ── User (Supabase) endpoints ─────────────────────────────────────────────────


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
