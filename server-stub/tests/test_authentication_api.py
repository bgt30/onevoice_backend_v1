# coding: utf-8

from fastapi.testclient import TestClient


from openapi_server.models.api_auth_forgot_password_post200_response import ApiAuthForgotPasswordPost200Response  # noqa: F401
from openapi_server.models.api_auth_forgot_password_post_request import ApiAuthForgotPasswordPostRequest  # noqa: F401
from openapi_server.models.api_auth_reset_password_post_request import ApiAuthResetPasswordPostRequest  # noqa: F401
from openapi_server.models.auth_response import AuthResponse  # noqa: F401
from openapi_server.models.error import Error  # noqa: F401
from openapi_server.models.login_request import LoginRequest  # noqa: F401
from openapi_server.models.signup_request import SignupRequest  # noqa: F401


def test_api_auth_forgot_password_post(client: TestClient):
    """Test case for api_auth_forgot_password_post

    Request password reset
    """
    api_auth_forgot_password_post_request = openapi_server.ApiAuthForgotPasswordPostRequest()

    headers = {
    }
    # uncomment below to make a request
    response = client.request(
       "POST",
       "/api/auth/forgot-password",
       headers=headers,
       json=api_auth_forgot_password_post_request,
    )

    # uncomment below to assert the status code of the HTTP response
    assert response.status_code == 200


def test_api_auth_login_post(client: TestClient):
    """Test case for api_auth_login_post

    User login
    """
    login_request = {"password":"password","email":"email"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/auth/login",
    #    headers=headers,
    #    json=login_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_auth_logout_post(client: TestClient):
    """Test case for api_auth_logout_post

    User logout
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/auth/logout",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_auth_reset_password_post(client: TestClient):
    """Test case for api_auth_reset_password_post

    Reset password with token
    """
    api_auth_reset_password_post_request = openapi_server.ApiAuthResetPasswordPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/auth/reset-password",
    #    headers=headers,
    #    json=api_auth_reset_password_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_auth_signup_post(client: TestClient):
    """Test case for api_auth_signup_post

    User registration
    """
    signup_request = {"password":"password","full_name":"full_name","email":"email","username":"username"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/auth/signup",
    #    headers=headers,
    #    json=signup_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

