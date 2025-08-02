# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.authentication_api_base import BaseAuthenticationApi
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
from openapi_server.models.api_auth_forgot_password_post200_response import ApiAuthForgotPasswordPost200Response
from openapi_server.models.api_auth_forgot_password_post_request import ApiAuthForgotPasswordPostRequest
from openapi_server.models.api_auth_reset_password_post_request import ApiAuthResetPasswordPostRequest
from openapi_server.models.auth_response import AuthResponse
from openapi_server.models.error import Error
from openapi_server.models.login_request import LoginRequest
from openapi_server.models.signup_request import SignupRequest
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/api/auth/forgot-password",
    responses={
        200: {"model": ApiAuthForgotPasswordPost200Response, "description": "Password reset email sent"},
    },
    tags=["Authentication"],
    summary="Request password reset",
    response_model_by_alias=True,
)
async def api_auth_forgot_password_post(
    api_auth_forgot_password_post_request: ApiAuthForgotPasswordPostRequest = Body(None, description=""),
) -> ApiAuthForgotPasswordPost200Response:
    if not BaseAuthenticationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthenticationApi.subclasses[0]().api_auth_forgot_password_post(api_auth_forgot_password_post_request)


@router.post(
    "/api/auth/login",
    responses={
        200: {"model": AuthResponse, "description": "Successful login"},
        401: {"model": Error, "description": "Invalid credentials"},
    },
    tags=["Authentication"],
    summary="User login",
    response_model_by_alias=True,
)
async def api_auth_login_post(
    login_request: LoginRequest = Body(None, description=""),
) -> AuthResponse:
    if not BaseAuthenticationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthenticationApi.subclasses[0]().api_auth_login_post(login_request)


@router.post(
    "/api/auth/logout",
    responses={
        200: {"model": ApiAuthForgotPasswordPost200Response, "description": "Logout successful"},
    },
    tags=["Authentication"],
    summary="User logout",
    response_model_by_alias=True,
)
async def api_auth_logout_post(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiAuthForgotPasswordPost200Response:
    if not BaseAuthenticationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthenticationApi.subclasses[0]().api_auth_logout_post()


@router.post(
    "/api/auth/reset-password",
    responses={
        200: {"model": ApiAuthForgotPasswordPost200Response, "description": "Password reset successful"},
    },
    tags=["Authentication"],
    summary="Reset password with token",
    response_model_by_alias=True,
)
async def api_auth_reset_password_post(
    api_auth_reset_password_post_request: ApiAuthResetPasswordPostRequest = Body(None, description=""),
) -> ApiAuthForgotPasswordPost200Response:
    if not BaseAuthenticationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthenticationApi.subclasses[0]().api_auth_reset_password_post(api_auth_reset_password_post_request)


@router.post(
    "/api/auth/signup",
    responses={
        201: {"model": AuthResponse, "description": "User created successfully"},
        400: {"model": Error, "description": "Invalid input data"},
    },
    tags=["Authentication"],
    summary="User registration",
    response_model_by_alias=True,
)
async def api_auth_signup_post(
    signup_request: SignupRequest = Body(None, description=""),
) -> AuthResponse:
    if not BaseAuthenticationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthenticationApi.subclasses[0]().api_auth_signup_post(signup_request)
