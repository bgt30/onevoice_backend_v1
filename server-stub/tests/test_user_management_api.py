# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictBytes, StrictInt, StrictStr  # noqa: F401
from typing import Optional, Tuple, Union  # noqa: F401
from openapi_server.models.api_auth_forgot_password_post200_response import ApiAuthForgotPasswordPost200Response  # noqa: F401
from openapi_server.models.api_users_activity_get200_response import ApiUsersActivityGet200Response  # noqa: F401
from openapi_server.models.api_users_avatar_post200_response import ApiUsersAvatarPost200Response  # noqa: F401
from openapi_server.models.api_users_credits_usage_get200_response import ApiUsersCreditsUsageGet200Response  # noqa: F401
from openapi_server.models.api_users_dashboard_stats_get200_response import ApiUsersDashboardStatsGet200Response  # noqa: F401
from openapi_server.models.api_users_delete_account_post_request import ApiUsersDeleteAccountPostRequest  # noqa: F401
from openapi_server.models.api_users_notifications_preferences_get200_response import ApiUsersNotificationsPreferencesGet200Response  # noqa: F401
from openapi_server.models.api_users_password_put_request import ApiUsersPasswordPutRequest  # noqa: F401
from openapi_server.models.api_users_profile_put_request import ApiUsersProfilePutRequest  # noqa: F401
from openapi_server.models.subscription import Subscription  # noqa: F401
from openapi_server.models.user import User  # noqa: F401


def test_api_users_activity_get(client: TestClient):
    """Test case for api_users_activity_get

    Get user activity log
    """
    params = [("page", 1),     ("per_page", 20)]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/users/activity",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_users_avatar_delete(client: TestClient):
    """Test case for api_users_avatar_delete

    Delete user avatar
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/api/users/avatar",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_users_avatar_post(client: TestClient):
    """Test case for api_users_avatar_post

    Upload user avatar
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    data = {
        "avatar": '/path/to/file'
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/users/avatar",
    #    headers=headers,
    #    data=data,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_users_credits_usage_get(client: TestClient):
    """Test case for api_users_credits_usage_get

    Get user credits usage
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/users/credits/usage",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_users_dashboard_stats_get(client: TestClient):
    """Test case for api_users_dashboard_stats_get

    Get dashboard statistics
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/users/dashboard/stats",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_users_delete_account_post(client: TestClient):
    """Test case for api_users_delete_account_post

    Delete user account
    """
    api_users_delete_account_post_request = openapi_server.ApiUsersDeleteAccountPostRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/users/delete-account",
    #    headers=headers,
    #    json=api_users_delete_account_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_users_notifications_preferences_get(client: TestClient):
    """Test case for api_users_notifications_preferences_get

    Get notification preferences
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/users/notifications/preferences",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_users_notifications_preferences_put(client: TestClient):
    """Test case for api_users_notifications_preferences_put

    Update notification preferences
    """
    api_users_notifications_preferences_get200_response = openapi_server.ApiUsersNotificationsPreferencesGet200Response()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PUT",
    #    "/api/users/notifications/preferences",
    #    headers=headers,
    #    json=api_users_notifications_preferences_get200_response,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_users_password_put(client: TestClient):
    """Test case for api_users_password_put

    Change user password
    """
    api_users_password_put_request = openapi_server.ApiUsersPasswordPutRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PUT",
    #    "/api/users/password",
    #    headers=headers,
    #    json=api_users_password_put_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_users_profile_get(client: TestClient):
    """Test case for api_users_profile_get

    Get user profile
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/users/profile",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_users_profile_put(client: TestClient):
    """Test case for api_users_profile_put

    Update user profile
    """
    api_users_profile_put_request = openapi_server.ApiUsersProfilePutRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PUT",
    #    "/api/users/profile",
    #    headers=headers,
    #    json=api_users_profile_put_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_users_subscription_get(client: TestClient):
    """Test case for api_users_subscription_get

    Get user subscription details
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/users/subscription",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

