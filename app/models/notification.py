# 알림 관련 ORM 모델
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class UserNotification(BaseModel):
    """사용자 알림 모델"""
    __tablename__ = "user_notifications"
    
    # 외래키
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 알림 정보
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 알림 타입
    notification_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False
    )  # system, processing_complete, billing, marketing, etc.
    
    # 중요도
    priority: Mapped[str] = mapped_column(
        String(10), 
        default="medium", 
        nullable=False
    )  # low, medium, high, urgent
    
    # 상태
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # 액션 정보
    action_url: Mapped[Optional[str]] = mapped_column(String(500))  # 클릭 시 이동할 URL
    action_label: Mapped[Optional[str]] = mapped_column(String(100))  # 액션 버튼 라벨
    
    # 관련 엔티티
    related_entity_type: Mapped[Optional[str]] = mapped_column(String(50))  # video, job, billing, etc.
    related_entity_id: Mapped[Optional[str]] = mapped_column(String(36))
    
    # 발송 채널
    channels: Mapped[Optional[str]] = mapped_column(Text)  # JSON 배열: ["web", "email", "push"]
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # 만료
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # 추가 데이터 (JSON 형태)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # 관계
    user: Mapped["User"] = relationship("User", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<UserNotification(id={self.id}, user_id={self.user_id}, title={self.title}, is_read={self.is_read})>"
    
    def mark_as_read(self) -> None:
        """알림을 읽음으로 표시"""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    @property
    def is_expired(self) -> bool:
        """알림이 만료되었는지 확인"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False 