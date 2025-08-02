# 사용자 관련 ORM 모델
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class User(BaseModel):
    """사용자 모델"""
    __tablename__ = "users"
    
    # 기본 정보
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    
    # 인증 정보
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # 프로필 정보
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    
    # 설정
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    processing_complete: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    billing_updates: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    marketing_emails: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # 마지막 로그인
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # 관계
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    videos: Mapped[List["Video"]] = relationship(
        "Video", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    billing_history: Mapped[List["BillingHistory"]] = relationship(
        "BillingHistory", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    credit_usage: Mapped[List["CreditUsage"]] = relationship(
        "CreditUsage", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    notifications: Mapped[List["UserNotification"]] = relationship(
        "UserNotification", 
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"

class Subscription(BaseModel):
    """구독 모델"""
    __tablename__ = "subscriptions"
    
    # 외래키
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 구독 정보
    plan_id: Mapped[str] = mapped_column(String(100), nullable=False)  # Stripe plan ID
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    
    # 상태
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="active"
    )  # active, cancelled, past_due, unpaid
    
    # 기간
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # 취소 설정
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # 크레딧
    credits_included: Mapped[int] = mapped_column(default=0, nullable=False)
    credits_used: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # 관계
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, user_id={self.user_id}, status={self.status})>"
    
    @property
    def credits_remaining(self) -> int:
        """남은 크레딧 계산"""
        return max(0, self.credits_included - self.credits_used) 