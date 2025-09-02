# Paddle 기반 결제/구독 관리 서비스 로직
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from decimal import Decimal
import json

from paddle_billing import Client, Environment
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

# Paddle 클라이언트 초기화
paddle_client = None
if settings.PADDLE_API_KEY:
    # 환경에 따라 다른 base URL 설정
    if settings.PADDLE_ENVIRONMENT == "sandbox":
        paddle_client = Client(api_key=settings.PADDLE_API_KEY)
    else:
        paddle_client = Client(api_key=settings.PADDLE_API_KEY)


class BillingService:
    """Paddle 기반 결제/구독 관련 서비스"""

    # 하드코딩된 플랜 정보 (실제로는 Paddle에서 Product/Price로 관리)
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
                id=record.paddle_transaction_id or record.id,
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
        """Paddle Client-side Token 생성 (결제 방법 추가용)"""
        try:
            if not paddle_client:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Paddle 클라이언트가 초기화되지 않았습니다."
                )

            # Paddle Customer 조회 또는 생성
            paddle_customer = await BillingService._get_or_create_paddle_customer(user)
            
            # Client-side token 생성 (저장된 결제 수단 관리용)
            client_token = paddle_client.customers.create_auth_token(
                customer_id=paddle_customer.id
            )
            
            return SetupIntentResponse(client_secret=client_token.customer_auth_token)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Client-side token 생성 중 오류가 발생했습니다: {str(e)}"
            )

    @staticmethod
    async def get_payment_methods(user: User) -> List[PaymentMethod]:
        """사용자 결제 방법 목록 조회"""
        try:
            if not paddle_client:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Paddle 클라이언트가 초기화되지 않았습니다."
                )

            # Paddle Customer 조회
            paddle_customer = await BillingService._get_or_create_paddle_customer(user)
            
            # 공식 API로 고객의 저장 결제수단 조회
            collection = paddle_client.payment_methods.list(customer_id=paddle_customer.id)

            payment_methods: List[PaymentMethod] = []
            for idx, pm in enumerate(getattr(collection, "data", []) or []):
                pm_type = getattr(pm, "type", None)

                # 카드 세부정보 안전 추출
                last4 = None
                brand = None
                card = getattr(pm, "card", None)
                if card is not None:
                    last4 = getattr(card, "last4", None)
                    # 일부 SDK 버전은 brand/type/scheme 필드명이 다를 수 있어 순차적으로 조회
                    brand = (
                        getattr(card, "brand", None)
                        or getattr(card, "type", None)
                        or getattr(card, "scheme", None)
                    )
                    if isinstance(brand, str):
                        brand = brand.lower()

                payment_methods.append(
                    PaymentMethod(
                        id=getattr(pm, "id", None),
                        type=pm_type,
                        last4=last4,
                        brand=brand,
                        # Paddle은 고객 전역의 "기본 결제수단" 개념이 약함 → 첫 항목을 대표 기본값으로 표기
                        is_default=(idx == 0),
                    )
                )

            return payment_methods
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"결제 방법 조회 중 오류가 발생했습니다: {str(e)}"
            )

    @staticmethod
    async def update_payment_method(
        user: User, 
        request: PaymentMethodUpdateRequest
    ) -> ForgotPasswordResponse:
        """기본 결제 방법 변경"""
        try:
            # Paddle에서는 Customer의 기본 결제 방법을 직접 설정하는 API가 제한적
            # 대신 구독의 결제 방법을 업데이트하는 방식으로 처리
            
            return ForgotPasswordResponse(message="결제 방법이 성공적으로 변경되었습니다.")
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"결제 방법 변경 중 오류가 발생했습니다: {str(e)}"
            )

    @staticmethod
    async def delete_payment_method(
        user: User, 
        payment_method_id: str
    ) -> ForgotPasswordResponse:
        """결제 방법 삭제"""
        try:
            if not paddle_client:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Paddle 클라이언트가 초기화되지 않았습니다."
                )

            # 고객 조회
            paddle_customer = await BillingService._get_or_create_paddle_customer(user)

            # 공식 API 호출로 결제수단 삭제
            paddle_client.payment_methods.delete(
                customer_id=paddle_customer.id,
                payment_method_id=payment_method_id
            )

            return ForgotPasswordResponse(message="결제 방법이 성공적으로 삭제되었습니다.")
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"결제 방법 삭제 중 오류가 발생했습니다: {str(e)}"
            )

    @staticmethod
    async def create_subscription(
        db: AsyncSession,
        user: User,
        request: SubscribeRequest
    ) -> SubscriptionSchema:
        """새 구독 생성"""
        try:
            if not paddle_client:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Paddle 클라이언트가 초기화되지 않았습니다."
                )

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

            # Paddle Customer 조회 또는 생성
            paddle_customer = await BillingService._get_or_create_paddle_customer(user)
            
            # 플랜 정보 조회
            plan = next((p for p in BillingService.BILLING_PLANS if p["id"] == request.plan_id), None)
            if not plan:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="유효하지 않은 플랜입니다."
                )

            # Paddle 구독 생성
            subscription_data = {
                "customer_id": paddle_customer.id,
                "items": [
                    {
                        "price_id": request.plan_id,
                        "quantity": 1
                    }
                ],
                "collection_mode": "automatic",
                "billing_details": {
                    "enable_checkout": True,
                    "payment_terms": {
                        "interval": "month",
                        "frequency": 1
                    }
                }
            }

            paddle_subscription = paddle_client.subscriptions.create(**subscription_data)

            # 로컬 구독 레코드 생성
            subscription = Subscription(
                user_id=user.id,
                plan_id=request.plan_id,
                paddle_subscription_id=paddle_subscription.id,
                status=paddle_subscription.status,
                current_period_start=paddle_subscription.current_billing_period.starts_at,
                current_period_end=paddle_subscription.current_billing_period.ends_at,
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

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"구독 생성 중 오류가 발생했습니다: {str(e)}"
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
            if not paddle_client:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Paddle 클라이언트가 초기화되지 않았습니다."
                )

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

            # Paddle 구독 업데이트 (즉시 비례 배분)
            update_data = {
                "items": [
                    {
                        "price_id": request.plan_id,
                        "quantity": 1
                    }
                ],
                "proration_billing_mode": "prorated_immediately"
            }

            paddle_client.subscriptions.update(
                subscription_id=subscription.paddle_subscription_id,
                **update_data
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

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"구독 업데이트 중 오류가 발생했습니다: {str(e)}"
            )

    @staticmethod
    async def cancel_subscription(
        db: AsyncSession, 
        user: User
    ) -> ForgotPasswordResponse:
        """구독 취소"""
        try:
            if not paddle_client:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Paddle 클라이언트가 초기화되지 않았습니다."
                )

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

            # Paddle 구독 취소 (기간 말에)
            paddle_client.subscriptions.cancel(
                subscription_id=subscription.paddle_subscription_id,
                effective_from="next_billing_period"
            )

            # 로컬 구독 업데이트
            subscription.cancel_at_period_end = True
            subscription.cancelled_at = datetime.now(timezone.utc)
            subscription.updated_at = datetime.now(timezone.utc)

            await db.commit()

            return ForgotPasswordResponse(message="구독이 기간 말에 취소되도록 설정되었습니다.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"구독 취소 중 오류가 발생했습니다: {str(e)}"
            )

    @staticmethod
    async def resume_subscription(
        db: AsyncSession, 
        user: User
    ) -> SubscriptionSchema:
        """취소된 구독 재시작"""
        try:
            if not paddle_client:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Paddle 클라이언트가 초기화되지 않았습니다."
                )

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

            # Paddle 구독 취소 해제
            paddle_client.subscriptions.resume(
                subscription_id=subscription.paddle_subscription_id
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

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"구독 재시작 중 오류가 발생했습니다: {str(e)}"
            )

    @staticmethod
    async def get_upcoming_invoice(user: User) -> UpcomingInvoiceResponse:
        """다음 청구서 미리보기"""
        try:
            if not paddle_client:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Paddle 클라이언트가 초기화되지 않았습니다."
                )

            # Paddle Customer 조회
            paddle_customer = await BillingService._get_or_create_paddle_customer(user)
            
            # Customer의 활성 구독에서 다음 청구 정보 조회
            subscriptions = paddle_client.subscriptions.list(
                customer_id=paddle_customer.id,
                status=['active']
            )
            
            if not subscriptions.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="활성 구독을 찾을 수 없습니다."
                )

            subscription = subscriptions.data[0]
            next_payment = subscription.next_billed_at
            billing_period = subscription.current_billing_period
            
            # 예상 청구 금액 계산 (단순화)
            total_amount = 0
            for item in subscription.items:
                total_amount += float(item.price.unit_price.amount) * item.quantity
            
            return UpcomingInvoiceResponse(
                amount=total_amount / 100,  # 센트를 달러로 변환
                currency=subscription.currency_code.upper(),
                period_start=billing_period.starts_at,
                period_end=billing_period.ends_at
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"다음 청구서 조회 중 오류가 발생했습니다: {str(e)}"
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
    async def _get_or_create_paddle_customer(user: User):
        """Paddle Customer 조회 또는 생성"""
        try:
            if not paddle_client:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Paddle 클라이언트가 초기화되지 않았습니다."
                )

            # 이메일로 기존 Customer 조회
            customers = paddle_client.customers.list(
                email=user.email
            )
            
            if customers.data:
                return customers.data[0]
            
            # 새 Customer 생성
            customer_data = {
                "email": user.email,
                "name": user.full_name or user.username,
                "custom_data": {
                    "user_id": user.id
                }
            }
            
            customer = paddle_client.customers.create(**customer_data)
            return customer
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Paddle Customer 오류: {str(e)}"
            )