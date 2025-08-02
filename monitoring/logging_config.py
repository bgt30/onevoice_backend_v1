# 구조화된 로깅 설정
import logging
import logging.config
import logging.handlers
import sys
import time
from pathlib import Path
from typing import Any, Dict

import structlog
from structlog.stdlib import LoggerFactory


def setup_logging() -> None:
    """간소화된 로깅 설정"""
    
    # 로그 디렉토리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 기본 로깅 설정 (간소화)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.handlers.RotatingFileHandler(
                'logs/onevoice.log',
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
        ]
    )
    
    # 특정 로거들의 레벨 조정
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """로거 인스턴스 반환"""
    return logging.getLogger(name)


class StructlogFormatter(logging.Formatter):
    """Structlog을 위한 커스텀 포맷터"""
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.processor = structlog.processors.JSONRenderer()
    
    def format(self, record: logging.LogRecord) -> str:
        """로그 레코드를 JSON 형태로 포맷팅"""
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
            
        if hasattr(record, "video_id"):
            log_data["video_id"] = record.video_id
            
        if hasattr(record, "job_id"):
            log_data["job_id"] = record.job_id
        
        return self.processor(None, None, log_data)


def setup_request_logging_middleware():
    """요청 로깅 미들웨어 설정"""
    import uuid
    from fastapi import Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware
    
    class RequestLoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            # 요청 ID 생성
            request_id = str(uuid.uuid4())
            
            # 요청 로그
            logger = get_logger("request")
            logger.info(
                "Request started",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                user_agent=request.headers.get("user-agent"),
                client_ip=request.client.host if request.client else None,
            )
            
            # 요청 처리
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 응답 로그
            logger.info(
                "Request completed",
                request_id=request_id,
                status_code=response.status_code,
                process_time=f"{process_time:.4f}s",
            )
            
            # 응답 헤더에 요청 ID 추가
            response.headers["X-Request-ID"] = request_id
            
            return response
    
    return RequestLoggingMiddleware 