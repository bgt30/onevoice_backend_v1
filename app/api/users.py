# User Management API endpoints
# Endpoints:
# - GET /api/users/activity
# - DELETE /api/users/avatar
# - POST /api/users/avatar
# - GET /api/users/credits/usage
# - GET /api/users/dashboard/stats
# - POST /api/users/delete-account
# - GET /api/users/notifications/preferences
# - PUT /api/users/notifications/preferences
# - PUT /api/users/password
# - GET /api/users/profile
# - PUT /api/users/profile
# - GET /api/users/subscription

from fastapi import APIRouter, Body, Depends, Form, HTTPException, Query, status, UploadFile, File
from pydantic import StrictBytes, StrictInt, StrictStr
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Tuple, Union

from app.dependecies import get_db, get_current_active_user
from app.models.user import User as UserModel
from app.services.user_service import UserService
from app.schemas import (
    ForgotPasswordResponse,
    UserActivityResponse,
    AvatarUploadResponse,
    CreditsUsageResponse,
    DashboardStatsResponse,
    DeleteAccountRequest,
    NotificationPreferencesResponse,
    PasswordUpdateRequest,
    UserProfileUpdateRequest,
    Subscription,
    User
)

router = APIRouter(prefix="/api/users", tags=["User Management"])


@router.get(
    "/activity",
    responses={
        200: {"model": UserActivityResponse, "description": "Activity log retrieved"},
    },
    summary="Get user activity log",
    response_model_by_alias=True,
)
async def get_activity(
    page: Optional[StrictInt] = Query(1, description=""),
    per_page: Optional[StrictInt] = Query(20, description=""),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> UserActivityResponse:
    """Get user activity log with pagination"""
    return await UserService.get_user_activity(db, current_user, page or 1, per_page or 20)


@router.delete(
    "/avatar",
    responses={
        200: {"model": ForgotPasswordResponse, "description": "Avatar deleted successfully"},
    },
    summary="Delete user avatar",
    response_model_by_alias=True,
)
async def delete_avatar(
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ForgotPasswordResponse:
    """Delete user avatar"""
    return await UserService.delete_avatar(db, current_user)


@router.post(
    "/avatar",
    responses={
        200: {"model": AvatarUploadResponse, "description": "Avatar uploaded successfully"},
    },
    summary="Upload user avatar",
    response_model_by_alias=True,
)
async def upload_avatar(
    avatar: UploadFile = File(..., description="Avatar image file"),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> AvatarUploadResponse:
    """Upload user avatar image"""
    return await UserService.upload_avatar(db, current_user, avatar)


@router.get(
    "/credits/usage",
    responses={
        200: {"model": CreditsUsageResponse, "description": "Credits usage retrieved"},
    },
    summary="Get user credits usage",
    response_model_by_alias=True,
)
async def get_credits_usage(
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> CreditsUsageResponse:
    """Get user credits usage statistics"""
    return await UserService.get_credits_usage(db, current_user)


@router.get(
    "/dashboard/stats",
    responses={
        200: {"model": DashboardStatsResponse, "description": "Dashboard stats retrieved"},
    },
    summary="Get dashboard statistics",
    response_model_by_alias=True,
)
async def get_dashboard_stats(
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> DashboardStatsResponse:
    """Get dashboard statistics for user"""
    return await UserService.get_dashboard_stats(db, current_user)


@router.post(
    "/delete-account",
    responses={
        200: {"model": ForgotPasswordResponse, "description": "Account deleted successfully"},
    },
    summary="Delete user account",
    response_model_by_alias=True,
)
async def delete_account(
    request: DeleteAccountRequest = Body(..., description=""),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ForgotPasswordResponse:
    """Delete user account permanently"""
    return await UserService.delete_user_account(db, current_user, request)


@router.get(
    "/notifications/preferences",
    responses={
        200: {"model": NotificationPreferencesResponse, "description": "Notification preferences retrieved"},
    },
    summary="Get notification preferences",
    response_model_by_alias=True,
)
async def get_notification_preferences(
    current_user: UserModel = Depends(get_current_active_user)
) -> NotificationPreferencesResponse:
    """Get user notification preferences"""
    return await UserService.get_notification_preferences(current_user)


@router.put(
    "/notifications/preferences",
    responses={
        200: {"model": ForgotPasswordResponse, "description": "Preferences updated successfully"},
    },
    summary="Update notification preferences",
    response_model_by_alias=True,
)
async def update_notification_preferences(
    preferences: NotificationPreferencesResponse = Body(..., description=""),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ForgotPasswordResponse:
    """Update user notification preferences"""
    return await UserService.update_notification_preferences(db, current_user, preferences)


@router.put(
    "/password",
    responses={
        200: {"model": ForgotPasswordResponse, "description": "Password changed successfully"},
    },
    summary="Change user password",
    response_model_by_alias=True,
)
async def change_password(
    request: PasswordUpdateRequest = Body(..., description=""),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ForgotPasswordResponse:
    """Change user password"""
    return await UserService.change_password(db, current_user, request)


@router.get(
    "/profile",
    responses={
        200: {"model": User, "description": "User profile retrieved"},
    },
    summary="Get user profile",
    response_model_by_alias=True,
)
async def get_profile(
    current_user: UserModel = Depends(get_current_active_user)
) -> User:
    """Get user profile information"""
    return await UserService.get_user_profile(current_user)


@router.put(
    "/profile",
    responses={
        200: {"model": User, "description": "Profile updated successfully"},
    },
    summary="Update user profile",
    response_model_by_alias=True,
)
async def update_profile(
    request: UserProfileUpdateRequest = Body(..., description=""),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Update user profile information"""
    return await UserService.update_user_profile(db, current_user, request)


@router.get(
    "/subscription",
    responses={
        200: {"model": Subscription, "description": "Subscription details retrieved"},
    },
    summary="Get user subscription details",
    response_model_by_alias=True,
)
async def get_subscription(
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Subscription:
    """Get user subscription details"""
    return await UserService.get_user_subscription(db, current_user) 