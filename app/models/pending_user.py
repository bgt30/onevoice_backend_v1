# 임시 회원가입 정보 모델
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseModel


class PendingUser(BaseModel):
    """임시 회원가입 정보 - 이메일 인증 대기 중인 사용자"""
    __tablename__ = "pending_users"
    
    # 사용자 정보
    email: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        unique=True,
        index=True
    )
    username: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        unique=True,
        index=True
    )
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 인증 정보
    verification_token: Mapped[str] = mapped_column(
        String(255), 
        nullable=False,
        unique=True,
        index=True
    )
    
    # 만료 시간 (24시간 후 자동 삭제)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc) + timedelta(hours=24)
    )
    
    def __repr__(self) -> str:
        return f"<PendingUser(id={self.id}, email={self.email}, username={self.username})>"
    
    @property
    def is_expired(self) -> bool:
        """만료 여부 확인"""
        return datetime.now(timezone.utc) > self.expires_at
    
    def extend_expiry(self, hours: int = 24) -> None:
        """만료 시간 연장"""
        self.expires_at = datetime.now(timezone.utc) + timedelta(hours=hours)