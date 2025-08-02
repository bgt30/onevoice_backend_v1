# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

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

class BaseBillingSubscriptionsApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseBillingSubscriptionsApi.subclasses = BaseBillingSubscriptionsApi.subclasses + (cls,)
    async def api_billing_history_get(
        self,
        page: Optional[StrictInt],
        per_page: Optional[StrictInt],
    ) -> ApiBillingHistoryGet200Response:
        ...


    async def api_billing_payment_method_put(
        self,
        api_billing_payment_method_put_request: ApiBillingPaymentMethodPutRequest,
    ) -> ApiAuthForgotPasswordPost200Response:
        ...


    async def api_billing_payment_methods_get(
        self,
    ) -> List[ApiBillingPaymentMethodsGet200ResponseInner]:
        ...


    async def api_billing_payment_methods_id_delete(
        self,
        id: StrictStr,
    ) -> ApiAuthForgotPasswordPost200Response:
        ...


    async def api_billing_plans_get(
        self,
    ) -> List[BillingPlan]:
        ...


    async def api_billing_setup_intent_post(
        self,
    ) -> ApiBillingSetupIntentPost200Response:
        ...


    async def api_billing_subscribe_post(
        self,
        api_billing_subscribe_post_request: ApiBillingSubscribePostRequest,
    ) -> Subscription:
        ...


    async def api_billing_subscription_cancel_post(
        self,
    ) -> ApiAuthForgotPasswordPost200Response:
        ...


    async def api_billing_subscription_get(
        self,
    ) -> Subscription:
        ...


    async def api_billing_subscription_put(
        self,
        api_billing_subscription_put_request: ApiBillingSubscriptionPutRequest,
    ) -> Subscription:
        ...


    async def api_billing_subscription_resume_post(
        self,
    ) -> Subscription:
        ...


    async def api_billing_upcoming_invoice_get(
        self,
    ) -> ApiBillingUpcomingInvoiceGet200Response:
        ...


    async def api_billing_usage_get(
        self,
    ) -> ApiBillingUsageGet200Response:
        ...
