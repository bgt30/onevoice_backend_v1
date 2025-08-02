# 비디오 관련 ORM 모델
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class Video(BaseModel):
    """비디오 모델"""
    __tablename__ = "videos"
    
    # 외래키
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 기본 정보
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # 비디오 메타데이터
    duration: Mapped[Optional[float]] = mapped_column(Float)  # 초 단위
    file_size: Mapped[Optional[int]] = mapped_column(Integer)  # 바이트 단위
    format: Mapped[Optional[str]] = mapped_column(String(10))  # mp4, avi, etc.
    resolution: Mapped[Optional[str]] = mapped_column(String(20))  # 1920x1080, etc.
    fps: Mapped[Optional[float]] = mapped_column(Float)  # frames per second
    
    # 언어 정보
    original_language: Mapped[Optional[str]] = mapped_column(String(10))  # ISO 639-1 코드
    target_languages: Mapped[Optional[str]] = mapped_column(Text)  # JSON 배열 형태
    
    # 상태
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="uploaded"
    )  # uploaded, processing, completed, failed
    
    # 파일 경로
    original_file_path: Mapped[Optional[str]] = mapped_column(String(500))
    processed_file_path: Mapped[Optional[str]] = mapped_column(String(500))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # S3 정보
    s3_bucket: Mapped[Optional[str]] = mapped_column(String(100))
    s3_key: Mapped[Optional[str]] = mapped_column(String(500))
    
    # 공유 설정
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    share_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    share_password: Mapped[Optional[str]] = mapped_column(String(255))  # 해시된 비밀번호
    
    # 처리 통계
    processing_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    processing_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    processing_error: Mapped[Optional[str]] = mapped_column(Text)
    
    # 추가 메타데이터 (JSON 형태)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # 관계
    user: Mapped["User"] = relationship("User", back_populates="videos")
    media_files: Mapped[List["MediaFile"]] = relationship(
        "MediaFile", 
        back_populates="video",
        cascade="all, delete-orphan"
    )
    jobs: Mapped[List["Job"]] = relationship(
        "Job", 
        back_populates="video",
        cascade="all, delete-orphan"
    )
    credit_usage: Mapped[List["CreditUsage"]] = relationship(
        "CreditUsage", 
        back_populates="video",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Video(id={self.id}, title={self.title}, status={self.status})>"

class MediaFile(BaseModel):
    """미디어 파일 모델"""
    __tablename__ = "media_files"
    
    # 외래키
    video_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 파일 정보
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(
        String(20), 
        nullable=False
    )  # original, dubbed, subtitle, thumbnail, etc.
    
    file_format: Mapped[str] = mapped_column(String(10), nullable=False)  # mp4, srt, jpg, etc.
    file_size: Mapped[Optional[int]] = mapped_column(Integer)  # 바이트 단위
    
    # 저장 경로
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    s3_bucket: Mapped[Optional[str]] = mapped_column(String(100))
    s3_key: Mapped[Optional[str]] = mapped_column(String(500))
    
    # URL
    public_url: Mapped[Optional[str]] = mapped_column(String(500))
    signed_url: Mapped[Optional[str]] = mapped_column(String(500))
    signed_url_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # 언어/버전 정보
    language_code: Mapped[Optional[str]] = mapped_column(String(10))  # 더빙된 언어
    voice_id: Mapped[Optional[str]] = mapped_column(String(100))  # 사용된 음성 ID
    
    # 상태
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # 추가 메타데이터
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # 관계
    video: Mapped["Video"] = relationship("Video", back_populates="media_files")

    def __repr__(self) -> str:
        return f"<MediaFile(id={self.id}, filename={self.filename}, file_type={self.file_type})>" 