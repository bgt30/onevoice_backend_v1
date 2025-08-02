# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.user_management_api_base import BaseUserManagementApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from pydantic import StrictBytes, StrictInt, StrictStr
from typing import Optional, Tuple, Union
from openapi_server.models.api_auth_forgot_password_post200_response import ApiAuthForgotPasswordPost200Response
from openapi_server.models.api_users_activity_get200_response import ApiUsersActivityGet200Response
from openapi_server.models.api_users_avatar_post200_response import ApiUsersAvatarPost200Response
from openapi_server.models.api_users_credits_usage_get200_response import ApiUsersCreditsUsageGet200Response
from openapi_server.models.api_users_dashboard_stats_get200_response import ApiUsersDashboardStatsGet200Response
from openapi_server.models.api_users_delete_account_post_request import ApiUsersDeleteAccountPostRequest
from openapi_server.models.api_users_notifications_preferences_get200_response import ApiUsersNotificationsPreferencesGet200Response
from openapi_server.models.api_users_password_put_request import ApiUsersPasswordPutRequest
from openapi_server.models.api_users_profile_put_request import ApiUsersProfilePutRequest
from openapi_server.models.subscription import Subscription
from openapi_server.models.user import User
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/api/users/activity",
    responses={
        200: {"model": ApiUsersActivityGet200Response, "description": "Activity log retrieved"},
    },
    tags=["User Management"],
    summary="Get user activity log",
    response_model_by_alias=True,
)
async def api_users_activity_get(
    page: Optional[StrictInt] = Query(1, description="", alias="page"),
    per_page: Optional[StrictInt] = Query(20, description="", alias="per_page"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiUsersActivityGet200Response:
    if not BaseUserManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUserManagementApi.subclasses[0]().api_users_activity_get(page, per_page)


@router.delete(
    "/api/users/avatar",
    responses={
        200: {"model": ApiAuthForgotPasswordPost200Response, "description": "Avatar deleted successfully"},
    },
    tags=["User Management"],
    summary="Delete user avatar",
    response_model_by_alias=True,
)
async def api_users_avatar_delete(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiAuthForgotPasswordPost200Response:
    if not BaseUserManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUserManagementApi.subclasses[0]().api_users_avatar_delete()


@router.post(
    "/api/users/avatar",
    responses={
        200: {"model": ApiUsersAvatarPost200Response, "description": "Avatar uploaded successfully"},
    },
    tags=["User Management"],
    summary="Upload user avatar",
    response_model_by_alias=True,
)
async def api_users_avatar_post(
    avatar: Optional[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]]] = Form(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiUsersAvatarPost200Response:
    if not BaseUserManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUserManagementApi.subclasses[0]().api_users_avatar_post(avatar)


@router.get(
    "/api/users/credits/usage",
    responses={
        200: {"model": ApiUsersCreditsUsageGet200Response, "description": "Credits usage retrieved"},
    },
    tags=["User Management"],
    summary="Get user credits usage",
    response_model_by_alias=True,
)
async def api_users_credits_usage_get(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiUsersCreditsUsageGet200Response:
    if not BaseUserManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUserManagementApi.subclasses[0]().api_users_credits_usage_get()


@router.get(
    "/api/users/dashboard/stats",
    responses={
        200: {"model": ApiUsersDashboardStatsGet200Response, "description": "Dashboard stats retrieved"},
    },
    tags=["User Management"],
    summary="Get dashboard statistics",
    response_model_by_alias=True,
)
async def api_users_dashboard_stats_get(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiUsersDashboardStatsGet200Response:
    if not BaseUserManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUserManagementApi.subclasses[0]().api_users_dashboard_stats_get()


@router.post(
    "/api/users/delete-account",
    responses={
        200: {"model": ApiAuthForgotPasswordPost200Response, "description": "Account deleted successfully"},
    },
    tags=["User Management"],
    summary="Delete user account",
    response_model_by_alias=True,
)
async def api_users_delete_account_post(
    api_users_delete_account_post_request: ApiUsersDeleteAccountPostRequest = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiAuthForgotPasswordPost200Response:
    if not BaseUserManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUserManagementApi.subclasses[0]().api_users_delete_account_post(api_users_delete_account_post_request)


@router.get(
    "/api/users/notifications/preferences",
    responses={
        200: {"model": ApiUsersNotificationsPreferencesGet200Response, "description": "Notification preferences retrieved"},
    },
    tags=["User Management"],
    summary="Get notification preferences",
    response_model_by_alias=True,
)
async def api_users_notifications_preferences_get(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiUsersNotificationsPreferencesGet200Response:
    if not BaseUserManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUserManagementApi.subclasses[0]().api_users_notifications_preferences_get()


@router.put(
    "/api/users/notifications/preferences",
    responses={
        200: {"model": ApiAuthForgotPasswordPost200Response, "description": "Preferences updated successfully"},
    },
    tags=["User Management"],
    summary="Update notification preferences",
    response_model_by_alias=True,
)
async def api_users_notifications_preferences_put(
    api_users_notifications_preferences_get200_response: ApiUsersNotificationsPreferencesGet200Response = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiAuthForgotPasswordPost200Response:
    if not BaseUserManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUserManagementApi.subclasses[0]().api_users_notifications_preferences_put(api_users_notifications_preferences_get200_response)


@router.put(
    "/api/users/password",
    responses={
        200: {"model": ApiAuthForgotPasswordPost200Response, "description": "Password changed successfully"},
    },
    tags=["User Management"],
    summary="Change user password",
    response_model_by_alias=True,
)
async def api_users_password_put(
    api_users_password_put_request: ApiUsersPasswordPutRequest = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiAuthForgotPasswordPost200Response:
    if not BaseUserManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUserManagementApi.subclasses[0]().api_users_password_put(api_users_password_put_request)


@router.get(
    "/api/users/profile",
    responses={
        200: {"model": User, "description": "User profile retrieved"},
    },
    tags=["User Management"],
    summary="Get user profile",
    response_model_by_alias=True,
)
async def api_users_profile_get(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> User:
    if not BaseUserManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUserManagementApi.subclasses[0]().api_users_profile_get()


@router.put(
    "/api/users/profile",
    responses={
        200: {"model": User, "description": "Profile updated successfully"},
    },
    tags=["User Management"],
    summary="Update user profile",
    response_model_by_alias=True,
)
async def api_users_profile_put(
    api_users_profile_put_request: ApiUsersProfilePutRequest = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> User:
    if not BaseUserManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUserManagementApi.subclasses[0]().api_users_profile_put(api_users_profile_put_request)


@router.get(
    "/api/users/subscription",
    responses={
        200: {"model": Subscription, "description": "Subscription details retrieved"},
    },
    tags=["User Management"],
    summary="Get user subscription details",
    response_model_by_alias=True,
)
async def api_users_subscription_get(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Subscription:
    if not BaseUserManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUserManagementApi.subclasses[0]().api_users_subscription_get()
