# 기본 SQLAlchemy 모델 클래스
from datetime import datetime
from typing import Any
from sqlalchemy import DateTime, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """모든 ORM 모델의 기본 클래스"""
    pass

class TimestampMixin:
    """타임스탬프 필드를 제공하는 Mixin"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

class BaseModel(Base, TimestampMixin):
    """공통 필드가 포함된 기본 모델"""
    __abstract__ = True
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    def to_dict(self) -> dict[str, Any]:
        """모델을 딕셔너리로 변환"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        } 