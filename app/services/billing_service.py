# 결제/구독 관리 서비스 로직
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from decimal import Decimal

import stripe
from fastapi import HTTPException, status
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, Subscription
from app.models.billing import BillingHistory, CreditUsage
from app.config import get_settings
from app.schemas import (
    BillingPlan,
    Subscription as SubscriptionSchema,
    SubscribeRequest,
    SubscriptionUpdateRequest,
    PaymentMethodUpdateRequest,
    PaymentMethod,
    SetupIntentResponse,
    Invoice,
    BillingHistoryResponse,
    UpcomingInvoiceResponse,
    UsageResponse,
    ForgotPasswordResponse
)

settings = get_settings()

# Stripe 초기화
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


class BillingService:
    """결제/구독 관련 서비스"""

    # 하드코딩된 플랜 정보 (나중에 DB나 설정 파일로 이동 가능)
    BILLING_PLANS = [
        {
            "id": "starter_monthly",
            "name": "Starter (월간)",
            "price": 9.99,
            "currency": "USD",
            "billing_period": "monthly",
            "credits_included": 500,
            "features": ["HD 품질", "5개 언어", "기본 지원"]
        },
        {
            "id": "pro_monthly",
            "name": "Pro (월간)",
            "price": 29.99,
            "currency": "USD",
            "billing_period": "monthly",
            "credits_included": 2000,
            "features": ["4K 품질", "20개 언어", "우선 지원", "API 액세스"]
        },
        {
            "id": "enterprise_monthly",
            "name": "Enterprise (월간)",
            "price": 99.99,
            "currency": "USD",
            "billing_period": "monthly",
            "credits_included": 10000,
            "features": ["4K 품질", "모든 언어", "전용 지원", "API 액세스", "커스텀 통합"]
        }
    ]

    @staticmethod
    async def get_billing_history(
        db: AsyncSession, 
        user: User, 
        page: int = 1, 
        per_page: int = 20
    ) -> BillingHistoryResponse:
        """결제 내역 조회"""
        offset = (page - 1) * per_page
        
        # 결제 내역 조회
        result = await db.execute(
            select(BillingHistory)
            .where(BillingHistory.user_id == user.id)
            .order_by(desc(BillingHistory.created_at))
            .offset(offset)
            .limit(per_page)
        )
        billing_records = result.scalars().all()

        # 전체 개수 조회
        total_count = await db.execute(
            select(func.count(BillingHistory.id))
            .where(BillingHistory.user_id == user.id)
        )
        total = total_count.scalar() or 0

        # Invoice 스키마로 변환
        invoices = [
            Invoice(
                id=record.stripe_invoice_id or record.id,
                amount=float(record.amount),
                currency=record.currency,
                status=record.status,
                created_at=record.created_at
            )
            for record in billing_records
        ]

        pagination = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }

        return BillingHistoryResponse(
            invoices=invoices,
            pagination=pagination
        )

    @staticmethod
    async def get_billing_plans() -> List[BillingPlan]:
        """사용 가능한 결제 플랜 조회"""
        return [BillingPlan(**plan) for plan in BillingService.BILLING_PLANS]

    @staticmethod
    async def create_setup_intent(user: User) -> SetupIntentResponse:
        """Stripe Setup Intent 생성 (결제 방법 추가용)"""
        try:
            # Stripe Customer 조회 또는 생성
            stripe_customer = await BillingService._get_or_create_stripe_customer(user)
            
            # Setup Intent 생성
            setup_intent = stripe.SetupIntent.create(
                customer=stripe_customer.id,
                usage="off_session"
            )
            
            return SetupIntentResponse(client_secret=setup_intent.client_secret)
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe 오류: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Setup Intent 생성 중 오류가 발생했습니다."
            )

    @staticmethod
    async def get_payment_methods(user: User) -> List[PaymentMethod]:
        """사용자 결제 방법 목록 조회"""
        try:
            # Stripe Customer 조회
            stripe_customer = await BillingService._get_or_create_stripe_customer(user)
            
            # Payment Methods 조회
            payment_methods = stripe.PaymentMethod.list(
                customer=stripe_customer.id,
                type="card"
            )
            
            result = []
            for pm in payment_methods.data:
                card = pm.card
                result.append(PaymentMethod(
                    id=pm.id,
                    type=card.brand,
                    last4=card.last4,
                    brand=card.brand,
                    is_default=(pm.id == stripe_customer.invoice_settings.default_payment_method)
                ))
            
            return result
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe 오류: {str(e)}"
            )

    @staticmethod
    async def update_payment_method(
        user: User, 
        request: PaymentMethodUpdateRequest
    ) -> ForgotPasswordResponse:
        """기본 결제 방법 변경"""
        try:
            # Stripe Customer 조회
            stripe_customer = await BillingService._get_or_create_stripe_customer(user)
            
            # 기본 결제 방법 설정
            stripe.Customer.modify(
                stripe_customer.id,
                invoice_settings={
                    "default_payment_method": request.payment_method_id
                }
            )
            
            return ForgotPasswordResponse(message="기본 결제 방법이 성공적으로 변경되었습니다.")
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe 오류: {str(e)}"
            )

    @staticmethod
    async def delete_payment_method(
        user: User, 
        payment_method_id: str
    ) -> ForgotPasswordResponse:
        """결제 방법 삭제"""
        try:
            # Payment Method 삭제
            stripe.PaymentMethod.detach(payment_method_id)
            
            return ForgotPasswordResponse(message="결제 방법이 성공적으로 삭제되었습니다.")
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe 오류: {str(e)}"
            )

    @staticmethod
    async def create_subscription(
        db: AsyncSession,
        user: User,
        request: SubscribeRequest
    ) -> SubscriptionSchema:
        """새 구독 생성"""
        try:
            # 기존 활성 구독 확인
            existing_subscription = await db.execute(
                select(Subscription)
                .where(
                    and_(
                        Subscription.user_id == user.id,
                        Subscription.status.in_(["active", "past_due"])
                    )
                )
            )
            if existing_subscription.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 활성 구독이 있습니다."
                )

            # Stripe Customer 조회
            stripe_customer = await BillingService._get_or_create_stripe_customer(user)
            
            # 플랜 정보 조회
            plan = next((p for p in BillingService.BILLING_PLANS if p["id"] == request.plan_id), None)
            if not plan:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="유효하지 않은 플랜입니다."
                )

            # Stripe 구독 생성
            stripe_subscription = stripe.Subscription.create(
                customer=stripe_customer.id,
                items=[{"price": request.plan_id}],
                default_payment_method=request.payment_method_id,
                expand=["latest_invoice.payment_intent"]
            )

            # 로컬 구독 레코드 생성
            subscription = Subscription(
                user_id=user.id,
                plan_id=request.plan_id,
                stripe_subscription_id=stripe_subscription.id,
                status=stripe_subscription.status,
                current_period_start=datetime.fromtimestamp(
                    stripe_subscription.current_period_start, 
                    timezone.utc
                ),
                current_period_end=datetime.fromtimestamp(
                    stripe_subscription.current_period_end, 
                    timezone.utc
                ),
                credits_included=plan["credits_included"],
                credits_used=0
            )

            db.add(subscription)
            await db.commit()
            await db.refresh(subscription)

            return SubscriptionSchema(
                id=subscription.id,
                plan_id=subscription.plan_id,
                status=subscription.status,
                current_period_start=subscription.current_period_start,
                current_period_end=subscription.current_period_end,
                cancel_at_period_end=subscription.cancel_at_period_end
            )

        except stripe.error.StripeError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe 오류: {str(e)}"
            )
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="구독 생성 중 오류가 발생했습니다."
            )

    @staticmethod
    async def get_subscription(db: AsyncSession, user: User) -> SubscriptionSchema:
        """현재 구독 정보 조회"""
        result = await db.execute(
            select(Subscription)
            .where(
                and_(
                    Subscription.user_id == user.id,
                    Subscription.status.in_(["active", "past_due", "cancelled"])
                )
            )
            .order_by(desc(Subscription.created_at))
            .limit(1)
        )
        subscription = result.scalar_one_or_none()

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="구독 정보를 찾을 수 없습니다."
            )

        return SubscriptionSchema(
            id=subscription.id,
            plan_id=subscription.plan_id,
            status=subscription.status,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end,
            cancel_at_period_end=subscription.cancel_at_period_end
        )

    @staticmethod
    async def update_subscription(
        db: AsyncSession,
        user: User,
        request: SubscriptionUpdateRequest
    ) -> SubscriptionSchema:
        """구독 플랜 변경"""
        try:
            # 현재 구독 조회
            result = await db.execute(
                select(Subscription)
                .where(
                    and_(
                        Subscription.user_id == user.id,
                        Subscription.status == "active"
                    )
                )
            )
            subscription = result.scalar_one_or_none()

            if not subscription:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="활성 구독을 찾을 수 없습니다."
                )

            # 플랜 정보 확인
            new_plan = next((p for p in BillingService.BILLING_PLANS if p["id"] == request.plan_id), None)
            if not new_plan:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="유효하지 않은 플랜입니다."
                )

            # Stripe 구독 업데이트
            stripe_subscription = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                items=[{
                    "id": stripe_subscription["items"]["data"][0].id,
                    "price": request.plan_id,
                }]
            )

            # 로컬 구독 업데이트
            subscription.plan_id = request.plan_id
            subscription.credits_included = new_plan["credits_included"]
            subscription.updated_at = datetime.now(timezone.utc)

            await db.commit()

            return SubscriptionSchema(
                id=subscription.id,
                plan_id=subscription.plan_id,
                status=subscription.status,
                current_period_start=subscription.current_period_start,
                current_period_end=subscription.current_period_end,
                cancel_at_period_end=subscription.cancel_at_period_end
            )

        except stripe.error.StripeError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe 오류: {str(e)}"
            )

    @staticmethod
    async def cancel_subscription(
        db: AsyncSession, 
        user: User
    ) -> ForgotPasswordResponse:
        """구독 취소"""
        try:
            # 현재 구독 조회
            result = await db.execute(
                select(Subscription)
                .where(
                    and_(
                        Subscription.user_id == user.id,
                        Subscription.status == "active"
                    )
                )
            )
            subscription = result.scalar_one_or_none()

            if not subscription:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="활성 구독을 찾을 수 없습니다."
                )

            # Stripe 구독 취소 (기간 말에)
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )

            # 로컬 구독 업데이트
            subscription.cancel_at_period_end = True
            subscription.cancelled_at = datetime.now(timezone.utc)
            subscription.updated_at = datetime.now(timezone.utc)

            await db.commit()

            return ForgotPasswordResponse(message="구독이 기간 말에 취소되도록 설정되었습니다.")

        except stripe.error.StripeError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe 오류: {str(e)}"
            )

    @staticmethod
    async def resume_subscription(
        db: AsyncSession, 
        user: User
    ) -> SubscriptionSchema:
        """취소된 구독 재시작"""
        try:
            # 취소 예정 구독 조회
            result = await db.execute(
                select(Subscription)
                .where(
                    and_(
                        Subscription.user_id == user.id,
                        Subscription.status == "active",
                        Subscription.cancel_at_period_end == True
                    )
                )
            )
            subscription = result.scalar_one_or_none()

            if not subscription:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="취소 예정인 구독을 찾을 수 없습니다."
                )

            # Stripe 구독 취소 해제
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=False
            )

            # 로컬 구독 업데이트
            subscription.cancel_at_period_end = False
            subscription.cancelled_at = None
            subscription.updated_at = datetime.now(timezone.utc)

            await db.commit()

            return SubscriptionSchema(
                id=subscription.id,
                plan_id=subscription.plan_id,
                status=subscription.status,
                current_period_start=subscription.current_period_start,
                current_period_end=subscription.current_period_end,
                cancel_at_period_end=subscription.cancel_at_period_end
            )

        except stripe.error.StripeError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe 오류: {str(e)}"
            )

    @staticmethod
    async def get_upcoming_invoice(user: User) -> UpcomingInvoiceResponse:
        """다음 청구서 미리보기"""
        try:
            # Stripe Customer 조회
            stripe_customer = await BillingService._get_or_create_stripe_customer(user)
            
            # 다음 청구서 조회
            upcoming_invoice = stripe.Invoice.upcoming(customer=stripe_customer.id)
            
            return UpcomingInvoiceResponse(
                amount=upcoming_invoice.amount_due / 100,  # cents to dollars
                currency=upcoming_invoice.currency.upper(),
                period_start=datetime.fromtimestamp(upcoming_invoice.period_start, timezone.utc),
                period_end=datetime.fromtimestamp(upcoming_invoice.period_end, timezone.utc)
            )
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe 오류: {str(e)}"
            )

    @staticmethod
    async def get_usage(db: AsyncSession, user: User) -> UsageResponse:
        """사용량 정보 조회"""
        # 현재 구독 조회
        result = await db.execute(
            select(Subscription)
            .where(
                and_(
                    Subscription.user_id == user.id,
                    Subscription.status == "active"
                )
            )
        )
        subscription = result.scalar_one_or_none()

        if not subscription:
            return UsageResponse(
                current_period_usage=0,
                included_credits=0,
                overage_credits=0,
                overage_cost=0
            )

        # 현재 기간 사용량 계산
        current_month = datetime.now(timezone.utc).strftime('%Y-%m')
        usage_result = await db.execute(
            select(func.sum(CreditUsage.credits_used))
            .where(
                and_(
                    CreditUsage.user_id == user.id,
                    CreditUsage.usage_month == current_month
                )
            )
        )
        current_usage = usage_result.scalar() or 0

        # 초과 사용량 계산
        overage_credits = max(0, current_usage - subscription.credits_included)
        overage_cost = overage_credits * 0.01  # 1센트 per credit

        return UsageResponse(
            current_period_usage=current_usage,
            included_credits=subscription.credits_included,
            overage_credits=overage_credits,
            overage_cost=overage_cost
        )

    @staticmethod
    async def _get_or_create_stripe_customer(user: User) -> stripe.Customer:
        """Stripe Customer 조회 또는 생성"""
        try:
            # 이메일로 기존 Customer 조회
            customers = stripe.Customer.list(email=user.email, limit=1)
            
            if customers.data:
                return customers.data[0]
            
            # 새 Customer 생성
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name or user.username,
                metadata={"user_id": user.id}
            )
            
            return customer
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe Customer 오류: {str(e)}"
            )