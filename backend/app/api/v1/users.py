"""
User profile and preferences endpoints.

User profiles are managed by Supabase Auth; this module handles
application-level preferences and metadata.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, CurrentUserId, DB
from app.core.exceptions import NotFoundException
from app.models.user import UserPreference
from app.schemas.common import ErrorResponse, SuccessResponse
from app.schemas.user import (
    UserInfo,
    UserPreferenceCreate,
    UserPreferenceResponse,
    UserPreferenceUpdate,
)

router = APIRouter()


@router.get(
    "/users/me",
    response_model=SuccessResponse[UserInfo],
    summary="Get current user profile",
)
async def get_current_user_profile(
    user: CurrentUser,
) -> SuccessResponse[UserInfo]:
    """Return the authenticated user's profile from their JWT."""
    user_info = UserInfo(
        id=user["sub"],
        email=user.get("email"),
        role=user.get("role", "authenticated"),
        metadata=user.get("user_metadata", {}),
    )
    return SuccessResponse(data=user_info)


@router.patch(
    "/users/me",
    response_model=SuccessResponse[dict],
    summary="Update current user metadata",
    description="Update user metadata in Supabase (e.g. display name, avatar).",
)
async def update_current_user(
    user: CurrentUser,
) -> SuccessResponse[dict]:
    """Placeholder for updating user metadata in Supabase Auth."""
    return SuccessResponse(
        data={"id": user["sub"], "message": "Profile update endpoint"},
        message="This endpoint will update the Supabase user profile via the Admin API.",
    )


@router.get(
    "/users/preferences",
    response_model=SuccessResponse[UserPreferenceResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Get user preferences",
)
async def get_user_preferences(
    db: DB,
    user_id: CurrentUserId,
) -> SuccessResponse[UserPreferenceResponse]:
    """Return the application preferences for the current user."""
    result = await db.execute(
        select(UserPreference).where(
            UserPreference.user_id == user_id,
            UserPreference.deleted_at.is_(None),
        )
    )
    prefs = result.scalar_one_or_none()

    if prefs is None:
        # Return defaults if no preferences exist yet
        default_prefs = UserPreferenceResponse(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            user_id=user_id,
            display_name=None,
            timezone="UTC",
            currency="USD",
            language="en",
            email_notifications=True,
            push_notifications=True,
            price_alert_threshold_percent=5.0,
            breaking_news_alerts=True,
            ai_analysis_alerts=True,
            theme="system",
            dashboard_layout={},
            chart_preferences={},
            favorite_coins=None,
        )
        return SuccessResponse(
            data=default_prefs,
            message="Default preferences (not yet saved)",
        )

    return SuccessResponse(data=UserPreferenceResponse.model_validate(prefs))


@router.patch(
    "/users/preferences",
    response_model=SuccessResponse[UserPreferenceResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Update user preferences",
)
async def update_user_preferences(
    body: UserPreferenceUpdate,
    db: DB,
    user_id: CurrentUserId,
) -> SuccessResponse[UserPreferenceResponse]:
    """Create or update the current user's application preferences."""
    result = await db.execute(
        select(UserPreference).where(
            UserPreference.user_id == user_id,
            UserPreference.deleted_at.is_(None),
        )
    )
    prefs = result.scalar_one_or_none()

    if prefs is None:
        # Create new preferences
        create_data = body.model_dump(exclude_unset=True)
        create_data["user_id"] = user_id
        prefs = UserPreference(**create_data)
        db.add(prefs)
        await db.flush()
    else:
        # Update existing
        update_data = body.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(prefs, key, value)

    await db.commit()
    await db.refresh(prefs)

    return SuccessResponse(
        data=UserPreferenceResponse.model_validate(prefs),
        message="Preferences updated",
    )
