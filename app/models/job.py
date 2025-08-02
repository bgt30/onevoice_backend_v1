# 작업 관련 ORM 모델
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class Job(BaseModel):
    """작업 모델"""
    __tablename__ = "jobs"
    
    # 외래키
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    video_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey("videos.id", ondelete="CASCADE"),
        index=True
    )
    
    # 작업 정보
    job_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False
    )  # dubbing, transcription, translation, etc.
    
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="pending"
    )  # pending, processing, completed, failed, cancelled
    
    # 진행률
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0.0 ~ 100.0
    
    # 작업 설정
    target_language: Mapped[Optional[str]] = mapped_column(String(10))  # ISO 639-1 코드
    voice_id: Mapped[Optional[str]] = mapped_column(String(100))
    preserve_background_music: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # 타이밍
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    estimated_completion: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # 에러 정보
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_code: Mapped[Optional[str]] = mapped_column(String(50))
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    
    # 우선순위
    priority: Mapped[int] = mapped_column(Integer, default=5, nullable=False)  # 1(높음) ~ 10(낮음)
    
    # 비용 정보
    credits_cost: Mapped[Optional[int]] = mapped_column(Integer)
    
    # 작업 설정 및 결과 (JSON 형태)
    job_config: Mapped[Optional[dict]] = mapped_column(JSON)  # 작업 설정
    job_result: Mapped[Optional[dict]] = mapped_column(JSON)  # 작업 결과
    
    # Celery 작업 ID
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    
    # 관계
    user: Mapped["User"] = relationship("User")
    video: Mapped[Optional["Video"]] = relationship("Video", back_populates="jobs")
    job_steps: Mapped[List["JobStep"]] = relationship(
        "JobStep", 
        back_populates="job",
        cascade="all, delete-orphan",
        order_by="JobStep.step_order"
    )
    credit_usage: Mapped[List["CreditUsage"]] = relationship(
        "CreditUsage", 
        back_populates="job",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, job_type={self.job_type}, status={self.status}, progress={self.progress})>"
    
    @property
    def duration(self) -> Optional[float]:
        """작업 수행 시간 (초)"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

class JobStep(BaseModel):
    """작업 단계 모델"""
    __tablename__ = "job_steps"
    
    # 외래키
    job_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 단계 정보
    step_name: Mapped[str] = mapped_column(String(100), nullable=False)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="pending"
    )  # pending, processing, completed, failed, skipped
    
    # 진행률
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0.0 ~ 100.0
    
    # 타이밍
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # 에러 정보
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_code: Mapped[Optional[str]] = mapped_column(String(50))
    
    # 단계별 입력/출력
    input_data: Mapped[Optional[dict]] = mapped_column(JSON)
    output_data: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # 로그 및 메타데이터
    logs: Mapped[Optional[str]] = mapped_column(Text)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # 관계
    job: Mapped["Job"] = relationship("Job", back_populates="job_steps")

    def __repr__(self) -> str:
        return f"<JobStep(id={self.id}, job_id={self.job_id}, step_name={self.step_name}, status={self.status})>"
    
    @property
    def duration(self) -> Optional[float]:
        """단계 수행 시간 (초)"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None 