# 결제/크레딧 관련 ORM 모델
from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class BillingHistory(BaseModel):
    """결제 내역 모델"""
    __tablename__ = "billing_history"
    
    # 외래키
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Paddle 정보
    paddle_transaction_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    paddle_subscription_id: Mapped[Optional[str]] = mapped_column(String(100))
    paddle_invoice_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # 결제 정보
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    
    # 상태 및 타입
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False
    )  # completed, pending, failed, cancelled
    
    payment_type: Mapped[str] = mapped_column(
        String(20), 
        nullable=False
    )  # subscription, one_time, refund, adjustment
    
    # 결제 제공자
    payment_provider: Mapped[str] = mapped_column(String(20), default="paddle", nullable=False)
    
    # 상세 정보
    description: Mapped[Optional[str]] = mapped_column(String(500))
    invoice_url: Mapped[Optional[str]] = mapped_column(String(500))
    receipt_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # 기간 (구독의 경우)
    period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # 결제 일시
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # 실패 정보
    failure_code: Mapped[Optional[str]] = mapped_column(String(50))
    failure_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # 관계
    user: Mapped["User"] = relationship("User", back_populates="billing_history")

    def __repr__(self) -> str:
        return f"<BillingHistory(id={self.id}, user_id={self.user_id}, amount={self.amount}, status={self.status})>"

class CreditUsage(BaseModel):
    """크레딧 사용량 모델"""
    __tablename__ = "credit_usage"
    
    # 외래키
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    video_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey("videos.id", ondelete="SET NULL"),
        index=True
    )
    
    job_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey("jobs.id", ondelete="SET NULL"),
        index=True
    )
    
    # 사용량 정보
    credits_used: Mapped[int] = mapped_column(Integer, nullable=False)
    operation_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False
    )  # dubbing, transcription, translation, etc.
    
    # 상세 정보
    description: Mapped[Optional[str]] = mapped_column(String(500))
    extra_metadata: Mapped[Optional[str]] = mapped_column(Text)  # JSON 형태의 추가 정보
    
    # 기간 정보 (월별 집계용)
    usage_month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)  # YYYY-MM 형식
    
    # 관계
    user: Mapped["User"] = relationship("User", back_populates="credit_usage")
    video: Mapped[Optional["Video"]] = relationship("Video", back_populates="credit_usage")
    job: Mapped[Optional["Job"]] = relationship("Job", back_populates="credit_usage")

    def __repr__(self) -> str:
        return f"<CreditUsage(id={self.id}, user_id={self.user_id}, credits_used={self.credits_used}, operation_type={self.operation_type})>" 