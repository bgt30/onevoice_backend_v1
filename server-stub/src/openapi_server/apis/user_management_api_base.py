# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

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

class BaseUserManagementApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseUserManagementApi.subclasses = BaseUserManagementApi.subclasses + (cls,)
    async def api_users_activity_get(
        self,
        page: Optional[StrictInt],
        per_page: Optional[StrictInt],
    ) -> ApiUsersActivityGet200Response:
        ...


    async def api_users_avatar_delete(
        self,
    ) -> ApiAuthForgotPasswordPost200Response:
        ...


    async def api_users_avatar_post(
        self,
        avatar: Optional[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]]],
    ) -> ApiUsersAvatarPost200Response:
        ...


    async def api_users_credits_usage_get(
        self,
    ) -> ApiUsersCreditsUsageGet200Response:
        ...


    async def api_users_dashboard_stats_get(
        self,
    ) -> ApiUsersDashboardStatsGet200Response:
        ...


    async def api_users_delete_account_post(
        self,
        api_users_delete_account_post_request: ApiUsersDeleteAccountPostRequest,
    ) -> ApiAuthForgotPasswordPost200Response:
        ...


    async def api_users_notifications_preferences_get(
        self,
    ) -> ApiUsersNotificationsPreferencesGet200Response:
        ...


    async def api_users_notifications_preferences_put(
        self,
        api_users_notifications_preferences_get200_response: ApiUsersNotificationsPreferencesGet200Response,
    ) -> ApiAuthForgotPasswordPost200Response:
        ...


    async def api_users_password_put(
        self,
        api_users_password_put_request: ApiUsersPasswordPutRequest,
    ) -> ApiAuthForgotPasswordPost200Response:
        ...


    async def api_users_profile_get(
        self,
    ) -> User:
        ...


    async def api_users_profile_put(
        self,
        api_users_profile_put_request: ApiUsersProfilePutRequest,
    ) -> User:
        ...


    async def api_users_subscription_get(
        self,
    ) -> Subscription:
        ...
