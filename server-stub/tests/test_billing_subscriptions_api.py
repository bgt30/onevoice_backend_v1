# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictInt, StrictStr  # noqa: F401
from typing import List, Optional  # noqa: F401
from openapi_server.models.api_auth_forgot_password_post200_response import ApiAuthForgotPasswordPost200Response  # noqa: F401
from openapi_server.models.api_billing_history_get200_response import ApiBillingHistoryGet200Response  # noqa: F401
from openapi_server.models.api_billing_payment_method_put_request import ApiBillingPaymentMethodPutRequest  # noqa: F401
from openapi_server.models.api_billing_payment_methods_get200_response_inner import ApiBillingPaymentMethodsGet200ResponseInner  # noqa: F401
from openapi_server.models.api_billing_setup_intent_post200_response import ApiBillingSetupIntentPost200Response  # noqa: F401
from openapi_server.models.api_billing_subscribe_post_request import ApiBillingSubscribePostRequest  # noqa: F401
from openapi_server.models.api_billing_subscription_put_request import ApiBillingSubscriptionPutRequest  # noqa: F401
from openapi_server.models.api_billing_upcoming_invoice_get200_response import ApiBillingUpcomingInvoiceGet200Response  # noqa: F401
from openapi_server.models.api_billing_usage_get200_response import ApiBillingUsageGet200Response  # noqa: F401
from openapi_server.models.billing_plan import BillingPlan  # noqa: F401
from openapi_server.models.subscription import Subscription  # noqa: F401


def test_api_billing_history_get(client: TestClient):
    """Test case for api_billing_history_get

    Get billing history
    """
    params = [("page", 1),     ("per_page", 20)]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/billing/history",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_billing_payment_method_put(client: TestClient):
    """Test case for api_billing_payment_method_put

    Update default payment method
    """
    api_billing_payment_method_put_request = openapi_server.ApiBillingPaymentMethodPutRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PUT",
    #    "/api/billing/payment-method",
    #    headers=headers,
    #    json=api_billing_payment_method_put_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_billing_payment_methods_get(client: TestClient):
    """Test case for api_billing_payment_methods_get

    Get all payment methods
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/billing/payment-methods",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_billing_payment_methods_id_delete(client: TestClient):
    """Test case for api_billing_payment_methods_id_delete

    Delete payment method
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/api/billing/payment-methods/{id}".format(id='id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_billing_plans_get(client: TestClient):
    """Test case for api_billing_plans_get

    Get available billing plans
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/billing/plans",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_billing_setup_intent_post(client: TestClient):
    """Test case for api_billing_setup_intent_post

    Create setup intent for payment method
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/billing/setup-intent",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_billing_subscribe_post(client: TestClient):
    """Test case for api_billing_subscribe_post

    Create new subscription
    """
    api_billing_subscribe_post_request = openapi_server.ApiBillingSubscribePostRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/billing/subscribe",
    #    headers=headers,
    #    json=api_billing_subscribe_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_billing_subscription_cancel_post(client: TestClient):
    """Test case for api_billing_subscription_cancel_post

    Cancel subscription
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/billing/subscription/cancel",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_billing_subscription_get(client: TestClient):
    """Test case for api_billing_subscription_get

    Get current subscription
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/billing/subscription",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_billing_subscription_put(client: TestClient):
    """Test case for api_billing_subscription_put

    Update subscription
    """
    api_billing_subscription_put_request = openapi_server.ApiBillingSubscriptionPutRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PUT",
    #    "/api/billing/subscription",
    #    headers=headers,
    #    json=api_billing_subscription_put_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_billing_subscription_resume_post(client: TestClient):
    """Test case for api_billing_subscription_resume_post

    Resume cancelled subscription
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/billing/subscription/resume",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_billing_upcoming_invoice_get(client: TestClient):
    """Test case for api_billing_upcoming_invoice_get

    Get upcoming invoice
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/billing/upcoming-invoice",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_billing_usage_get(client: TestClient):
    """Test case for api_billing_usage_get

    Get billing usage details
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/billing/usage",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

