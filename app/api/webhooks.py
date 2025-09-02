# Paddle 웹훅 처리 API
import json
import hmac
import hashlib
from typing import Dict, Any
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Request, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.dependecies import get_db
from app.models.user import User, Subscription
from app.models.billing import BillingHistory
from app.config import get_settings

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])
settings = get_settings()


def verify_paddle_webhook(body: bytes, signature: str) -> bool:
    """Paddle 웹훅 서명 검증"""
    if not settings.PADDLE_WEBHOOK_SECRET:
        # 개발 환경에서는 서명 검증을 건너뛸 수 있음
        return True
    
    try:
        # Paddle 웹훅 서명 검증 로직
        expected_signature = hmac.new(
            settings.PADDLE_WEBHOOK_SECRET.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, f"sha256={expected_signature}")
    except Exception:
        return False


@router.post("/paddle")
async def handle_paddle_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Paddle 웹훅 처리"""
    try:
        # 요청 본문과 서명 읽기
        body = await request.body()
        signature = request.headers.get("paddle-signature", "")
        
        # 서명 검증
        if not verify_paddle_webhook(body, signature):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook signature"
            )
        
        # JSON 파싱
        try:
            event_data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        
        # 이벤트 처리
        await process_paddle_event(db, event_data)
        
        return {"status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing error: {str(e)}"
        )


async def process_paddle_event(db: AsyncSession, event_data: Dict[str, Any]):
    """Paddle 이벤트 처리"""
    event_type = event_data.get("event_type")
    data = event_data.get("data", {})
    
    if event_type == "subscription.created":
        await handle_subscription_created(db, data)
    elif event_type == "subscription.updated":
        await handle_subscription_updated(db, data)
    elif event_type == "subscription.cancelled":
        await handle_subscription_cancelled(db, data)
    elif event_type == "subscription.resumed":
        await handle_subscription_resumed(db, data)
    elif event_type == "transaction.completed":
        await handle_transaction_completed(db, data)
    elif event_type == "transaction.payment_failed":
        await handle_transaction_failed(db, data)
    else:
        # 지원하지 않는 이벤트 타입은 무시
        pass


async def handle_subscription_created(db: AsyncSession, data: Dict[str, Any]):
    """구독 생성 이벤트 처리"""
    paddle_subscription_id = data.get("id")
    customer_id = data.get("customer_id")
    status = data.get("status")
    
    # Customer 정보로 사용자 조회
    customer_email = data.get("customer", {}).get("email")
    if not customer_email:
        return
    
    result = await db.execute(
        select(User).where(User.email == customer_email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return
    
    # 구독 정보 업데이트 또는 생성
    result = await db.execute(
        select(Subscription).where(
            Subscription.paddle_subscription_id == paddle_subscription_id
        )
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        # 새 구독 생성 (이미 BillingService에서 생성된 경우가 많음)
        pass
    else:
        # 기존 구독 상태 업데이트
        subscription.status = status
        subscription.updated_at = datetime.now(timezone.utc)
    
    await db.commit()


async def handle_subscription_updated(db: AsyncSession, data: Dict[str, Any]):
    """구독 업데이트 이벤트 처리"""
    paddle_subscription_id = data.get("id")
    status = data.get("status")
    
    result = await db.execute(
        select(Subscription).where(
            Subscription.paddle_subscription_id == paddle_subscription_id
        )
    )
    subscription = result.scalar_one_or_none()
    
    if subscription:
        subscription.status = status
        subscription.updated_at = datetime.now(timezone.utc)
        
        # 기간 정보 업데이트
        current_billing_period = data.get("current_billing_period", {})
        if current_billing_period:
            subscription.current_period_start = datetime.fromisoformat(
                current_billing_period.get("starts_at").replace('Z', '+00:00')
            )
            subscription.current_period_end = datetime.fromisoformat(
                current_billing_period.get("ends_at").replace('Z', '+00:00')
            )
        
        await db.commit()


async def handle_subscription_cancelled(db: AsyncSession, data: Dict[str, Any]):
    """구독 취소 이벤트 처리"""
    paddle_subscription_id = data.get("id")
    
    result = await db.execute(
        select(Subscription).where(
            Subscription.paddle_subscription_id == paddle_subscription_id
        )
    )
    subscription = result.scalar_one_or_none()
    
    if subscription:
        subscription.status = "cancelled"
        subscription.cancel_at_period_end = True
        subscription.cancelled_at = datetime.now(timezone.utc)
        subscription.updated_at = datetime.now(timezone.utc)
        
        await db.commit()


async def handle_subscription_resumed(db: AsyncSession, data: Dict[str, Any]):
    """구독 재시작 이벤트 처리"""
    paddle_subscription_id = data.get("id")
    
    result = await db.execute(
        select(Subscription).where(
            Subscription.paddle_subscription_id == paddle_subscription_id
        )
    )
    subscription = result.scalar_one_or_none()
    
    if subscription:
        subscription.status = "active"
        subscription.cancel_at_period_end = False
        subscription.cancelled_at = None
        subscription.updated_at = datetime.now(timezone.utc)
        
        await db.commit()


async def handle_transaction_completed(db: AsyncSession, data: Dict[str, Any]):
    """거래 완료 이벤트 처리"""
    transaction_id = data.get("id")
    customer_id = data.get("customer_id")
    
    # Customer로 사용자 조회
    customer_email = data.get("customer", {}).get("email")
    if not customer_email:
        return
    
    result = await db.execute(
        select(User).where(User.email == customer_email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return
    
    # 기존 결제 기록 확인
    existing_record = await db.execute(
        select(BillingHistory).where(
            BillingHistory.paddle_transaction_id == transaction_id
        )
    )
    
    if existing_record.scalar_one_or_none():
        return  # 이미 처리된 거래
    
    # 결제 기록 생성
    billing_record = BillingHistory(
        user_id=user.id,
        paddle_transaction_id=transaction_id,
        paddle_subscription_id=data.get("subscription_id"),
        amount=Decimal(str(data.get("details", {}).get("totals", {}).get("total", "0"))) / 100,
        currency=data.get("currency_code", "USD"),
        status="completed",
        payment_type="subscription" if data.get("subscription_id") else "one_time",
        payment_provider="paddle",
        description=f"Payment for transaction {transaction_id}",
        paid_at=datetime.now(timezone.utc)
    )
    
    db.add(billing_record)
    await db.commit()


async def handle_transaction_failed(db: AsyncSession, data: Dict[str, Any]):
    """거래 실패 이벤트 처리"""
    transaction_id = data.get("id")
    customer_id = data.get("customer_id")
    
    # Customer로 사용자 조회
    customer_email = data.get("customer", {}).get("email")
    if not customer_email:
        return
    
    result = await db.execute(
        select(User).where(User.email == customer_email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return
    
    # 실패한 결제 기록 생성
    billing_record = BillingHistory(
        user_id=user.id,
        paddle_transaction_id=transaction_id,
        paddle_subscription_id=data.get("subscription_id"),
        amount=Decimal(str(data.get("details", {}).get("totals", {}).get("total", "0"))) / 100,
        currency=data.get("currency_code", "USD"),
        status="failed",
        payment_type="subscription" if data.get("subscription_id") else "one_time",
        payment_provider="paddle",
        description=f"Failed payment for transaction {transaction_id}",
        failure_code=data.get("failure_reason", {}).get("code"),
        failure_message=data.get("failure_reason", {}).get("message")
    )
    
    db.add(billing_record)
    
    # 구독 상태 업데이트 (결제 실패)
    if data.get("subscription_id"):
        result = await db.execute(
            select(Subscription).where(
                Subscription.paddle_subscription_id == data.get("subscription_id")
            )
        )
        subscription = result.scalar_one_or_none()
        
        if subscription:
            subscription.status = "past_due"
            subscription.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
