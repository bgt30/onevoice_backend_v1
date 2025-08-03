# Job Status & Management API endpoints
# Endpoints:
# - GET /api/videos/{id}/status (job status polling)
# - POST /api/videos/{id}/cancel (cancel processing job)

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import StrictStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependecies import get_db, get_current_active_user
from app.models.user import User as UserModel
from app.services.job_service import JobService
from app.services.dubbing_service import DubbingService
from app.schemas import (
    ForgotPasswordResponse,
    JobStatus
)

router = APIRouter(prefix="/api/videos", tags=["Job Management"])


@router.get(
    "/{id}/status",
    responses={
        200: {"model": JobStatus, "description": "Processing status retrieved"},
    },
    summary="Get video processing status",
    response_model_by_alias=True,
)
async def get_job_status(
    id: StrictStr = Path(..., description=""),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> JobStatus:
    """Get video processing job status"""
    job_status = await JobService.get_job_status_for_video(db, id, current_user.id)
    
    if not job_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="작업을 찾을 수 없습니다."
        )
    
    return job_status


@router.post(
    "/{id}/cancel",
    responses={
        200: {"model": ForgotPasswordResponse, "description": "Processing cancelled"},
    },
    summary="Cancel video processing",
    response_model_by_alias=True,
)
async def cancel_job(
    id: StrictStr = Path(..., description=""),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ForgotPasswordResponse:
    """Cancel video processing job"""
    # 비디오의 최신 작업 찾기
    jobs = await JobService.get_jobs_by_video(db, id, current_user.id)
    
    if not jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="작업을 찾을 수 없습니다."
        )
    
    # 가장 최근 진행 중인 작업 찾기
    active_job = None
    for job in jobs:
        if job.status in ["pending", "processing"]:
            active_job = job
            break
    
    if not active_job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="취소할 수 있는 진행 중인 작업이 없습니다."
        )
    
    # 더빙 작업인 경우 DubbingService 사용
    if active_job.job_type == "dubbing":
        success = await DubbingService.cancel_dubbing_job(db, active_job.id, current_user.id)
    else:
        success = await JobService.cancel_job(db, active_job.id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="작업 취소 중 오류가 발생했습니다."
        )
    
    return ForgotPasswordResponse(message="작업이 성공적으로 취소되었습니다.") 