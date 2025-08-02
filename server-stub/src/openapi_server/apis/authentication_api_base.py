# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from openapi_server.models.api_auth_forgot_password_post200_response import ApiAuthForgotPasswordPost200Response
from openapi_server.models.api_auth_forgot_password_post_request import ApiAuthForgotPasswordPostRequest
from openapi_server.models.api_auth_reset_password_post_request import ApiAuthResetPasswordPostRequest
from openapi_server.models.auth_response import AuthResponse
from openapi_server.models.error import Error
from openapi_server.models.login_request import LoginRequest
from openapi_server.models.signup_request import SignupRequest
from openapi_server.security_api import get_token_bearerAuth

class BaseAuthenticationApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAuthenticationApi.subclasses = BaseAuthenticationApi.subclasses + (cls,)
    async def api_auth_forgot_password_post(
        self,
        api_auth_forgot_password_post_request: ApiAuthForgotPasswordPostRequest,
    ) -> ApiAuthForgotPasswordPost200Response:
        ...


    async def api_auth_login_post(
        self,
        login_request: LoginRequest,
    ) -> AuthResponse:
        ...


    async def api_auth_logout_post(
        self,
    ) -> ApiAuthForgotPasswordPost200Response:
        ...


    async def api_auth_reset_password_post(
        self,
        api_auth_reset_password_post_request: ApiAuthResetPasswordPostRequest,
    ) -> ApiAuthForgotPasswordPost200Response:
        ...


    async def api_auth_signup_post(
        self,
        signup_request: SignupRequest,
    ) -> AuthResponse:
        ...
