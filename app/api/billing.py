# Billing & Subscriptions API endpoints
# Endpoints:
# - GET /api/billing/history
# - PUT /api/billing/payment-method
# - GET /api/billing/payment-methods
# - DELETE /api/billing/payment-methods/{id}
# - GET /api/billing/plans
# - POST /api/billing/setup-intent
# - POST /api/billing/subscribe
# - POST /api/billing/subscription/cancel
# - GET /api/billing/subscription
# - PUT /api/billing/subscription
# - POST /api/billing/subscription/resume
# - GET /api/billing/upcoming-invoice
# - GET /api/billing/usage

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from pydantic import StrictInt, StrictStr
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.dependecies import get_db, get_current_active_user
from app.models.user import User as UserModel
from app.services.billing_service import BillingService
from app.schemas import (
    ForgotPasswordResponse,
    BillingHistoryResponse,
    PaymentMethodUpdateRequest,
    PaymentMethod,
    SetupIntentResponse,
    SubscribeRequest,
    SubscriptionUpdateRequest,
    UpcomingInvoiceResponse,
    UsageResponse,
    BillingPlan,
    Subscription
)

router = APIRouter(prefix="/api/billing", tags=["Billing & Subscriptions"])


@router.get(
    "/history",
    responses={
        200: {"model": BillingHistoryResponse, "description": "Billing history retrieved"},
    },
    summary="Get billing history",
    response_model_by_alias=True,
)
async def get_billing_history(
    page: Optional[StrictInt] = Query(1, description=""),
    per_page: Optional[StrictInt] = Query(20, description="", alias="perPage"),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> BillingHistoryResponse:
    """Get billing history with pagination"""
    return await BillingService.get_billing_history(db, current_user, page or 1, per_page or 20)


@router.put(
    "/payment-method",
    responses={
        200: {"model": ForgotPasswordResponse, "description": "Payment method updated successfully"},
    },
    summary="Update default payment method",
    response_model_by_alias=True,
)
async def update_payment_method(
    request: PaymentMethodUpdateRequest = Body(..., description=""),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ForgotPasswordResponse:
    """Update default payment method"""
    return await BillingService.update_payment_method(current_user, request)


@router.get(
    "/payment-methods",
    responses={
        200: {"model": List[PaymentMethod], "description": "Payment methods retrieved"},
    },
    summary="Get all payment methods",
    response_model_by_alias=True,
)
async def get_payment_methods(
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> List[PaymentMethod]:
    """Get all user payment methods"""
    return await BillingService.get_payment_methods(current_user)


@router.delete(
    "/payment-methods/{id}",
    responses={
        200: {"model": ForgotPasswordResponse, "description": "Payment method deleted successfully"},
    },
    summary="Delete payment method",
    response_model_by_alias=True,
)
async def delete_payment_method(
    id: StrictStr = Path(..., description=""),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ForgotPasswordResponse:
    """Delete a payment method"""
    return await BillingService.delete_payment_method(current_user, id)


@router.get(
    "/plans",
    responses={
        200: {"model": List[BillingPlan], "description": "Billing plans retrieved"},
    },
    summary="Get available billing plans",
    response_model_by_alias=True,
)
async def get_billing_plans(
    current_user: UserModel = Depends(get_current_active_user)
) -> List[BillingPlan]:
    """Get all available billing plans"""
    return await BillingService.get_billing_plans()


@router.post(
    "/setup-intent",
    responses={
        200: {"model": SetupIntentResponse, "description": "Setup intent created"},
    },
    summary="Create setup intent for payment method",
    response_model_by_alias=True,
)
async def create_setup_intent(
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> SetupIntentResponse:
    """Create Stripe setup intent for adding payment method"""
    return await BillingService.create_setup_intent(current_user)


@router.post(
    "/subscribe",
    responses={
        201: {"model": Subscription, "description": "Subscription created successfully"},
    },
    summary="Create new subscription",
    response_model_by_alias=True,
)
async def create_subscription(
    request: SubscribeRequest = Body(..., description=""),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Subscription:
    """Create new subscription"""
    return await BillingService.create_subscription(db, current_user, request)


@router.post(
    "/subscription/cancel",
    responses={
        200: {"model": ForgotPasswordResponse, "description": "Subscription cancelled successfully"},
    },
    summary="Cancel subscription",
    response_model_by_alias=True,
)
async def cancel_subscription(
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ForgotPasswordResponse:
    """Cancel current subscription"""
    return await BillingService.cancel_subscription(db, current_user)


@router.get(
    "/subscription",
    responses={
        200: {"model": Subscription, "description": "Current subscription retrieved"},
    },
    summary="Get current subscription",
    response_model_by_alias=True,
)
async def get_subscription(
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Subscription:
    """Get current subscription details"""
    return await BillingService.get_subscription(db, current_user)


@router.put(
    "/subscription",
    responses={
        200: {"model": Subscription, "description": "Subscription updated successfully"},
    },
    summary="Update subscription",
    response_model_by_alias=True,
)
async def update_subscription(
    request: SubscriptionUpdateRequest = Body(..., description=""),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Subscription:
    """Update subscription plan"""
    return await BillingService.update_subscription(db, current_user, request)


@router.post(
    "/subscription/resume",
    responses={
        200: {"model": Subscription, "description": "Subscription resumed successfully"},
    },
    summary="Resume cancelled subscription",
    response_model_by_alias=True,
)
async def resume_subscription(
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Subscription:
    """Resume a cancelled subscription"""
    return await BillingService.resume_subscription(db, current_user)


@router.get(
    "/upcoming-invoice",
    responses={
        200: {"model": UpcomingInvoiceResponse, "description": "Upcoming invoice retrieved"},
    },
    summary="Get upcoming invoice",
    response_model_by_alias=True,
)
async def get_upcoming_invoice(
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> UpcomingInvoiceResponse:
    """Get upcoming invoice preview"""
    return await BillingService.get_upcoming_invoice(current_user)


@router.get(
    "/usage",
    responses={
        200: {"model": UsageResponse, "description": "Usage details retrieved"},
    },
    summary="Get billing usage details",
    response_model_by_alias=True,
)
async def get_usage(
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> UsageResponse:
    """Get billing usage details and metering"""
    return await BillingService.get_usage(db, current_user) 