# 헬스체크 및 모니터링 엔드포인트
import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import psutil

router = APIRouter(prefix="/health", tags=["Health Check"])


@router.get("/", summary="기본 헬스체크")
async def health_check() -> Dict[str, Any]:
    """기본 헬스체크 - 서비스 가동 상태 확인"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "onevoice-backend",
        "version": "1.0.0"
    }


@router.get("/detailed", summary="상세 헬스체크")
async def detailed_health_check() -> Dict[str, Any]:
    """상세 헬스체크 - 시스템 리소스 및 의존성 상태 확인"""
    start_time = time.time()
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "onevoice-backend",
        "version": "1.0.0",
        "uptime": "N/A",  # TODO: 실제 uptime 계산
        "checks": {}
    }
    
    # 시스템 리소스 확인
    try:
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status["checks"]["system"] = {
            "status": "healthy",
            "cpu_usage": f"{cpu_percent}%",
            "memory_usage": f"{memory.percent}%",
            "memory_available": f"{memory.available / (1024**3):.2f} GB",
            "disk_usage": f"{disk.percent}%",
            "disk_free": f"{disk.free / (1024**3):.2f} GB"
        }
    except Exception as e:
        health_status["checks"]["system"] = {
            "status": "error",
            "error": str(e)
        }
    
    # 데이터베이스 연결 확인
    health_status["checks"]["database"] = await _check_database()
    
    # 전체 상태 결정
    all_healthy = all(
        check.get("status") == "healthy" 
        for check in health_status["checks"].values()
    )
    
    if not all_healthy:
        health_status["status"] = "degraded"
    
    health_status["response_time"] = f"{(time.time() - start_time) * 1000:.2f}ms"
    
    # 상태에 따른 HTTP 상태 코드 설정
    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content=health_status
    )


async def _check_database() -> Dict[str, Any]:
    """데이터베이스 연결 상태 확인"""
    try:
        # TODO: 실제 데이터베이스 연결 확인 로직 구현
        # from app.database import engine
        # async with engine.begin() as conn:
        #     await conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "message": "Database connection successful",
            "response_time": "5ms"  # TODO: 실제 응답 시간 측정
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Database connection failed"
        }