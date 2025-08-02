# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.billing_subscriptions_api_base import BaseBillingSubscriptionsApi
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
from pydantic import StrictInt, StrictStr
from typing import List, Optional
from openapi_server.models.api_auth_forgot_password_post200_response import ApiAuthForgotPasswordPost200Response
from openapi_server.models.api_billing_history_get200_response import ApiBillingHistoryGet200Response
from openapi_server.models.api_billing_payment_method_put_request import ApiBillingPaymentMethodPutRequest
from openapi_server.models.api_billing_payment_methods_get200_response_inner import ApiBillingPaymentMethodsGet200ResponseInner
from openapi_server.models.api_billing_setup_intent_post200_response import ApiBillingSetupIntentPost200Response
from openapi_server.models.api_billing_subscribe_post_request import ApiBillingSubscribePostRequest
from openapi_server.models.api_billing_subscription_put_request import ApiBillingSubscriptionPutRequest
from openapi_server.models.api_billing_upcoming_invoice_get200_response import ApiBillingUpcomingInvoiceGet200Response
from openapi_server.models.api_billing_usage_get200_response import ApiBillingUsageGet200Response
from openapi_server.models.billing_plan import BillingPlan
from openapi_server.models.subscription import Subscription
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/api/billing/history",
    responses={
        200: {"model": ApiBillingHistoryGet200Response, "description": "Billing history retrieved"},
    },
    tags=["Billing &amp; Subscriptions"],
    summary="Get billing history",
    response_model_by_alias=True,
)
async def api_billing_history_get(
    page: Optional[StrictInt] = Query(1, description="", alias="page"),
    per_page: Optional[StrictInt] = Query(20, description="", alias="perPage"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiBillingHistoryGet200Response:
    if not BaseBillingSubscriptionsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBillingSubscriptionsApi.subclasses[0]().api_billing_history_get(page, per_page)


@router.put(
    "/api/billing/payment-method",
    responses={
        200: {"model": ApiAuthForgotPasswordPost200Response, "description": "Payment method updated successfully"},
    },
    tags=["Billing &amp; Subscriptions"],
    summary="Update default payment method",
    response_model_by_alias=True,
)
async def api_billing_payment_method_put(
    api_billing_payment_method_put_request: ApiBillingPaymentMethodPutRequest = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiAuthForgotPasswordPost200Response:
    if not BaseBillingSubscriptionsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBillingSubscriptionsApi.subclasses[0]().api_billing_payment_method_put(api_billing_payment_method_put_request)


@router.get(
    "/api/billing/payment-methods",
    responses={
        200: {"model": List[ApiBillingPaymentMethodsGet200ResponseInner], "description": "Payment methods retrieved"},
    },
    tags=["Billing &amp; Subscriptions"],
    summary="Get all payment methods",
    response_model_by_alias=True,
)
async def api_billing_payment_methods_get(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[ApiBillingPaymentMethodsGet200ResponseInner]:
    if not BaseBillingSubscriptionsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBillingSubscriptionsApi.subclasses[0]().api_billing_payment_methods_get()


@router.delete(
    "/api/billing/payment-methods/{id}",
    responses={
        200: {"model": ApiAuthForgotPasswordPost200Response, "description": "Payment method deleted successfully"},
    },
    tags=["Billing &amp; Subscriptions"],
    summary="Delete payment method",
    response_model_by_alias=True,
)
async def api_billing_payment_methods_id_delete(
    id: StrictStr = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiAuthForgotPasswordPost200Response:
    if not BaseBillingSubscriptionsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBillingSubscriptionsApi.subclasses[0]().api_billing_payment_methods_id_delete(id)


@router.get(
    "/api/billing/plans",
    responses={
        200: {"model": List[BillingPlan], "description": "Billing plans retrieved"},
    },
    tags=["Billing &amp; Subscriptions"],
    summary="Get available billing plans",
    response_model_by_alias=True,
)
async def api_billing_plans_get(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[BillingPlan]:
    if not BaseBillingSubscriptionsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBillingSubscriptionsApi.subclasses[0]().api_billing_plans_get()


@router.post(
    "/api/billing/setup-intent",
    responses={
        200: {"model": ApiBillingSetupIntentPost200Response, "description": "Setup intent created"},
    },
    tags=["Billing &amp; Subscriptions"],
    summary="Create setup intent for payment method",
    response_model_by_alias=True,
)
async def api_billing_setup_intent_post(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiBillingSetupIntentPost200Response:
    if not BaseBillingSubscriptionsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBillingSubscriptionsApi.subclasses[0]().api_billing_setup_intent_post()


@router.post(
    "/api/billing/subscribe",
    responses={
        201: {"model": Subscription, "description": "Subscription created successfully"},
    },
    tags=["Billing &amp; Subscriptions"],
    summary="Create new subscription",
    response_model_by_alias=True,
)
async def api_billing_subscribe_post(
    api_billing_subscribe_post_request: ApiBillingSubscribePostRequest = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Subscription:
    if not BaseBillingSubscriptionsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBillingSubscriptionsApi.subclasses[0]().api_billing_subscribe_post(api_billing_subscribe_post_request)


@router.post(
    "/api/billing/subscription/cancel",
    responses={
        200: {"model": ApiAuthForgotPasswordPost200Response, "description": "Subscription cancelled successfully"},
    },
    tags=["Billing &amp; Subscriptions"],
    summary="Cancel subscription",
    response_model_by_alias=True,
)
async def api_billing_subscription_cancel_post(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiAuthForgotPasswordPost200Response:
    if not BaseBillingSubscriptionsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBillingSubscriptionsApi.subclasses[0]().api_billing_subscription_cancel_post()


@router.get(
    "/api/billing/subscription",
    responses={
        200: {"model": Subscription, "description": "Current subscription retrieved"},
    },
    tags=["Billing &amp; Subscriptions"],
    summary="Get current subscription",
    response_model_by_alias=True,
)
async def api_billing_subscription_get(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Subscription:
    if not BaseBillingSubscriptionsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBillingSubscriptionsApi.subclasses[0]().api_billing_subscription_get()


@router.put(
    "/api/billing/subscription",
    responses={
        200: {"model": Subscription, "description": "Subscription updated successfully"},
    },
    tags=["Billing &amp; Subscriptions"],
    summary="Update subscription",
    response_model_by_alias=True,
)
async def api_billing_subscription_put(
    api_billing_subscription_put_request: ApiBillingSubscriptionPutRequest = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Subscription:
    if not BaseBillingSubscriptionsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBillingSubscriptionsApi.subclasses[0]().api_billing_subscription_put(api_billing_subscription_put_request)


@router.post(
    "/api/billing/subscription/resume",
    responses={
        200: {"model": Subscription, "description": "Subscription resumed successfully"},
    },
    tags=["Billing &amp; Subscriptions"],
    summary="Resume cancelled subscription",
    response_model_by_alias=True,
)
async def api_billing_subscription_resume_post(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Subscription:
    if not BaseBillingSubscriptionsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBillingSubscriptionsApi.subclasses[0]().api_billing_subscription_resume_post()


@router.get(
    "/api/billing/upcoming-invoice",
    responses={
        200: {"model": ApiBillingUpcomingInvoiceGet200Response, "description": "Upcoming invoice retrieved"},
    },
    tags=["Billing &amp; Subscriptions"],
    summary="Get upcoming invoice",
    response_model_by_alias=True,
)
async def api_billing_upcoming_invoice_get(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiBillingUpcomingInvoiceGet200Response:
    if not BaseBillingSubscriptionsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBillingSubscriptionsApi.subclasses[0]().api_billing_upcoming_invoice_get()


@router.get(
    "/api/billing/usage",
    responses={
        200: {"model": ApiBillingUsageGet200Response, "description": "Usage details retrieved"},
    },
    tags=["Billing &amp; Subscriptions"],
    summary="Get billing usage details",
    response_model_by_alias=True,
)
async def api_billing_usage_get(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiBillingUsageGet200Response:
    if not BaseBillingSubscriptionsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseBillingSubscriptionsApi.subclasses[0]().api_billing_usage_get()
