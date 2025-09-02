# FastAPI 메인 애플리케이션
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# API 라우터 임포트
from app.api import auth, billing, jobs, users, videos, webhooks

# 모니터링 및 설정 임포트
from monitoring.health_check import router as health_router
from monitoring.logging_config import setup_logging
from app.config import get_settings

# 데이터베이스 임포트
from app.core.database import close_db_connections

# 스키마 임포트 
from app.schemas import Error

import datetime
from datetime import timezone

# 설정 로드
settings = get_settings()

# 로깅 설정
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시 실행
    logger.info("🚀 OneVoice Backend API 서버가 시작됩니다...")
    logger.info(f"환경: {settings.ENVIRONMENT}")
    logger.info(f"디버그 모드: {settings.DEBUG}")
    logger.info(f"데이터베이스: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'local'}")
    
    # 데이터베이스 연결 확인
    try:
        from app.core.database import async_engine
        from sqlalchemy import text
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ 데이터베이스 연결 성공")
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 실패: {e}")
        logger.warning("⚠️  일부 기능이 제한될 수 있습니다.")
    
    # 개발환경에서 테이블 생성 확인
    if settings.ENVIRONMENT == "development":
        try:
            from app.core.database import create_tables
            # await create_tables()  # 필요시 주석 해제
            logger.info("📊 개발환경 데이터베이스 준비 완료")
        except Exception as e:
            logger.warning(f"⚠️  테이블 생성 확인 실패: {e}")
    
    # 중단된 더빙 작업 복구
    try:
        from app.services.job_service import JobService
        from app.services.dubbing_service import DubbingService
        from app.core.database import get_async_session
        
        async for db in get_async_session():
            # 진행 중 또는 대기 중인 더빙 작업 조회
            active_jobs = await JobService.get_active_jobs(db, job_type="dubbing")

            if active_jobs:
                processing_jobs = [job for job in active_jobs if job.status == "processing"]
                pending_jobs = [job for job in active_jobs if job.status == "pending"]

                total_to_handle = len(processing_jobs) + len(pending_jobs)
                logger.info(f"🔄 복구 대상 더빙 작업: processing={len(processing_jobs)}, pending={len(pending_jobs)}, total={total_to_handle}")

                import asyncio
                # processing은 재개, pending은 새 실행
                for job in processing_jobs:
                    asyncio.create_task(DubbingService.resume_dubbing_pipeline(job.id))
                for job in pending_jobs:
                    asyncio.create_task(DubbingService.execute_dubbing_pipeline(job.id))

                logger.info("✅ 더빙 작업 복구 트리거 완료")
            else:
                logger.info("ℹ️  복구할 더빙 작업이 없습니다.")
            break
            
    except Exception as e:
        logger.warning(f"⚠️  더빙 작업 복구 실패: {e}")
    
    # 만료된 임시 회원가입 정보 정리
    try:
        from app.services.auth_service import AuthService
        from app.core.database import get_async_session
        
        async for db in get_async_session():
            cleaned_count = await AuthService.cleanup_expired_pending_users(db)
            if cleaned_count > 0:
                logger.info(f"🧹 만료된 임시 회원가입 정보 {cleaned_count}개를 정리했습니다.")
            else:
                logger.info("ℹ️  정리할 만료된 임시 회원가입 정보가 없습니다.")
            break
            
    except Exception as e:
        logger.warning(f"⚠️  임시 회원가입 정보 정리 실패: {e}")
    
    yield
    
    # 종료 시 실행
    logger.info("💤 OneVoice Backend API 서버가 종료됩니다...")
    
    # 데이터베이스 연결 정리
    try:
        await close_db_connections()
        logger.info("✅ 데이터베이스 연결 정리 완료")
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 정리 실패: {e}")
    
    # TODO: Redis 연결 정리
    logger.info("🎉 서버 종료 완료")


# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="OneVoice Backend API",
    description="""
    ## OneVoice - AI 기반 다국어 음성 더빙 서비스

    OneVoice는 AI 기술을 활용하여 비디오 콘텐츠를 다양한 언어로 자동 더빙하는 서비스입니다.
    """,
    version="1.0.0",
    contact={
        "name": "OneVoice Team",
        "email": "support@onevoice.ai",
    },
    license_info={
        "name": "Proprietary",
    },
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Gzip 압축 미들웨어
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 전역 예외 처리기
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """HTTP 예외 처리"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=Error(
            error=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
            details={"path": str(request.url.path), "method": request.method}
        ).model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """요청 유효성 검사 예외 처리"""
    logger.error(f"Validation Error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=Error(
            error="VALIDATION_ERROR", 
            message="요청 데이터가 올바르지 않습니다.",
            details={
                "errors": exc.errors(),
                "path": str(request.url.path),
                "method": request.method
            }
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """일반 예외 처리"""
    logger.exception(f"Unexpected error: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=Error(
            error="INTERNAL_SERVER_ERROR",
            message="서버 내부 오류가 발생했습니다." if not settings.DEBUG else str(exc),
            details={"path": str(request.url.path), "method": request.method} if settings.DEBUG else None
        ).model_dump()
    )


# 루트 엔드포인트
@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """서비스 정보 반환"""
    return {
        "service": "OneVoice Backend API",
        "version": "1.0.0",
        "status": "healthy",
        "message": "AI 기반 다국어 음성 더빙 서비스 API에 오신 것을 환영합니다!",
        "docs_url": "/docs" if settings.DEBUG else "문서는 프로덕션 환경에서 비활성화됩니다.",
        "timestamp": datetime.datetime.now(timezone.utc).isoformat() + "Z"
    }


# API 라우터 등록
# 인증 관련
app.include_router(auth.router)

# 사용자 관리
app.include_router(users.router)

# 비디오 관리 
app.include_router(videos.router)

# 작업 관리
app.include_router(jobs.router)
app.include_router(jobs.jobs_router)

# 결제/구독
app.include_router(billing.router)

# 웹훅
app.include_router(webhooks.router)

# 알림은 이메일로만 처리 (NotificationService)


# 헬스체크 및 모니터링
app.include_router(health_router)

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL
    )
