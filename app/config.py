# FastAPI 애플리케이션 설정
import os
from typing import List, Optional
from functools import lru_cache

from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Pydantic 설정
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore'  # 정의되지 않은 환경변수 무시
    )
    
    # 기본 설정
    ENVIRONMENT: str = Field(default="development", description="실행 환경")
    DEBUG: bool = Field(default=True, description="디버그 모드")
    API_V1_STR: str = Field(default="/api", description="API 버전 1 prefix")
    APP_NAME: str = Field(default="OneVoice Backend API", description="프로젝트 명")
    
    # 서버 설정
    HOST: str = Field(default="0.0.0.0", description="서버 호스트")
    PORT: int = Field(default=8000, description="서버 포트")
    
    # 보안 설정
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", description="JWT 시크릿 키")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="액세스 토큰 만료 시간 (분)")
    ALGORITHM: str = Field(default="HS256", description="JWT 알고리즘")
    
    # CORS 설정
    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://127.0.0.1:3000",
            "https://onevoice.ai",
            "https://app.onevoice.ai"
        ],
        description="허용된 CORS origin 목록"
    )
    
    # 데이터베이스 설정
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/onevoice_db",
        description="PostgreSQL 데이터베이스 URL"
    )
    
    # AWS 설정
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, description="AWS Access Key ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, description="AWS Secret Access Key")
    AWS_REGION: str = Field(default="us-west-2", description="AWS 리전")
    S3_BUCKET_NAME: str = Field(default="onevoice-videos", description="S3 버킷 이름")
    AWS_USE_IAM_ROLE: bool = Field(default=True, description="인스턴스/역할 자격증명 사용 여부 (기본 True)")

    # Task Queue (SQS)
    USE_SQS_TASK_QUEUE: bool = Field(default=False, description="SQS 기반 작업 큐 사용 (로컬 기본 False)")
    SQS_QUEUE_URL: Optional[str] = Field(default=None, description="기본 SQS 큐 URL")
    SQS_DLQ_URL: Optional[str] = Field(default=None, description="Dead Letter Queue URL")
    SQS_WAIT_TIME_SECONDS: int = Field(default=20, description="SQS 롱폴링 대기 시간(초)")
    SQS_VISIBILITY_TIMEOUT: int = Field(default=900, description="SQS 메시지 가시성 타임아웃(초)")
    
    # Stripe 설정  
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None, description="Stripe Secret Key")
    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(default=None, description="Stripe Publishable Key")
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None, description="Stripe Webhook Secret")
    
    # 외부 API 설정
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API 키")
    ELEVENLABS_API_KEY: Optional[str] = Field(default=None, description="ElevenLabs API 키")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="Anthropic API 키")
    
    # 이메일/알림 설정 (SES/SNS)
    SES_ENABLED: bool = Field(default=True, description="Amazon SES 사용 여부")
    EMAILS_FROM_EMAIL: Optional[str] = Field(default="noreply@onevoice.ai", description="발신 이메일 주소")
    EMAILS_FROM_NAME: str = Field(default="OneVoice", description="발신자 이름")
    SNS_ALERTS_TOPIC_ARN: Optional[str] = Field(default=None, description="운영 알림용 SNS 토픽 ARN")
    
    # 파일 업로드 설정
    MAX_FILE_SIZE: int = Field(default=500 * 1024 * 1024, description="최대 업로드 파일 크기 (바이트)")  # 500MB
    ALLOWED_VIDEO_EXTENSIONS: List[str] = Field(
        default=[".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v"],
        description="허용된 비디오 파일 확장자"
    )
    
    # 로깅 설정
    LOG_LEVEL: str = Field(default="INFO", description="로그 레벨")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="로그 포맷"
    )
    
    # 모니터링 설정
    # SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN")
    # ENABLE_METRICS: bool = Field(default=True, description="메트릭 수집 활성화")
    
    # 크레딧 시스템 설정
    DEFAULT_FREE_CREDITS: int = Field(default=100, description="신규 사용자 기본 무료 크레딧")
    CREDIT_COST_PER_MINUTE: int = Field(default=10, description="분당 크레딧 비용")
    
    # 프론트엔드 URL (이메일 링크용)
    FRONTEND_URL: str = Field(default="http://localhost:3000", env="FRONTEND_URL", description="프론트엔드 URL")
    
    # 언어 및 음성 설정
    SUPPORTED_LANGUAGES: List[dict] = Field(
        default=[
            {"code": "en", "name": "English", "native_name": "English"},
            {"code": "ko", "name": "Korean", "native_name": "한국어"},
            {"code": "ja", "name": "Japanese", "native_name": "日本語"},
            {"code": "zh", "name": "Chinese", "native_name": "中文"},
            {"code": "es", "name": "Spanish", "native_name": "Español"},
            {"code": "fr", "name": "French", "native_name": "Français"},
            {"code": "de", "name": "German", "native_name": "Deutsch"},
            {"code": "it", "name": "Italian", "native_name": "Italiano"},
            {"code": "pt", "name": "Portuguese", "native_name": "Português"},
            {"code": "ru", "name": "Russian", "native_name": "Русский"},
        ],
        description="지원 언어 목록"
    )
    
    AVAILABLE_VOICES: dict = Field(
        default={
            "en": [
                {"id": "en_voice_1", "name": "Sarah", "language": "en", "gender": "female", "style": "professional"},
                {"id": "en_voice_2", "name": "John", "language": "en", "gender": "male", "style": "casual"},
                {"id": "en_voice_3", "name": "Emma", "language": "en", "gender": "female", "style": "warm"},
            ],
            "ko": [
                {"id": "ko_voice_1", "name": "지민", "language": "ko", "gender": "female", "style": "professional"},
                {"id": "ko_voice_2", "name": "태형", "language": "ko", "gender": "male", "style": "casual"},
                {"id": "ko_voice_3", "name": "아이유", "language": "ko", "gender": "female", "style": "warm"},
            ],
            "ja": [
                {"id": "ja_voice_1", "name": "Yuki", "language": "ja", "gender": "female", "style": "professional"},
                {"id": "ja_voice_2", "name": "Hiroshi", "language": "ja", "gender": "male", "style": "casual"},
            ],
        },
        description="언어별 사용 가능한 음성 목록"
    )
    



@lru_cache()
def get_settings() -> Settings:
    """설정 인스턴스 반환 (캐시됨)"""
    return Settings()


# 전역 설정 인스턴스
settings = get_settings()
