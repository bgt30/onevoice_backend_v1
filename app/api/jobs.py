# Job Status & Management API endpoints
# Endpoints:
# - GET /api/videos/{id}/status (job status polling)
# - POST /api/videos/{id}/cancel (cancel processing job)
# - POST /api/videos/{id}/resume (resume/restart failed or pending/processing dubbing job)

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import StrictStr, StrictInt
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependecies import get_db, get_current_active_user
from app.models.user import User as UserModel
from app.services.job_service import JobService
from app.services.dubbing_service import DubbingService
from app.schemas import (
    ForgotPasswordResponse,
    JobStatus,
    Job,
    JobsResponse,
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


@router.post(
    "/{id}/resume",
    responses={
        200: {"model": ForgotPasswordResponse, "description": "Processing resumed/restarted"},
    },
    summary="Resume or restart video processing",
    response_model_by_alias=True,
)
async def resume_job(
    id: StrictStr = Path(..., description="Video ID"),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ForgotPasswordResponse:
    """Resume or restart dubbing job for the given video.
 
    Behavior:
    - If there is a failed job for this video, reset and resume from failed steps.
    - If there is a pending job, start execution.
    - If there is a processing job, attempt to resume to ensure progress continues.
    - If there is a completed job, returns 400.
    - If no job exists, returns 404.
    """
    # 관련 작업 모두 조회 (최신순 반환이라고 가정)
    jobs = await JobService.get_jobs_by_video(db, id, current_user.id)
 
    if not jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="작업을 찾을 수 없습니다.",
        )
 
    # 우선순위: failed > processing > pending > completed
    failed_job = next((j for j in jobs if j.status == "failed" and j.job_type == "dubbing"), None)
    processing_job = next((j for j in jobs if j.status == "processing" and j.job_type == "dubbing"), None)
    pending_job = next((j for j in jobs if j.status == "pending" and j.job_type == "dubbing"), None)
    completed_job = next((j for j in jobs if j.status == "completed" and j.job_type == "dubbing"), None)
 
    import asyncio
 
    if failed_job:
        # 실패한 더빙 작업 재개
        asyncio.create_task(DubbingService.resume_dubbing_pipeline(failed_job.id))
        return ForgotPasswordResponse(message="실패한 더빙 작업을 재개했습니다.")
 
    if processing_job:
        # 진행 중 작업의 안전한 재개 트리거
        asyncio.create_task(DubbingService.resume_dubbing_pipeline(processing_job.id))
        return ForgotPasswordResponse(message="진행 중 더빙 작업 재개를 트리거했습니다.")
 
    if pending_job:
        # 아직 미시작 상태면 파이프라인 시작
        asyncio.create_task(DubbingService.execute_dubbing_pipeline(pending_job.id))
        return ForgotPasswordResponse(message="대기 중 더빙 작업을 시작했습니다.")
 
    if completed_job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 완료된 작업입니다. 새 더빙을 시작해 주세요.",
        )
 
    # 기타 타입의 작업은 현재 지원하지 않음
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="더빙 작업만 재개할 수 있습니다.",
    )

# ===== Jobs API (User's jobs listing and detail) =====
jobs_router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@jobs_router.get(
    "",
    responses={
        200: {"model": JobsResponse, "description": "Jobs list retrieved"},
    },
    summary="List jobs for current user",
    response_model_by_alias=True,
)
async def list_jobs(
    job_type: StrictStr | None = Query(None, description="Filter by job type"),
    status_filter: StrictStr | None = Query(None, alias="status", description="Filter by status"),
    limit: StrictInt = Query(50, ge=1, le=100),
    offset: StrictInt = Query(0, ge=0),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> JobsResponse:
    jobs = await JobService.get_jobs_by_user(
        db=db,
        user_id=current_user.id,
        job_type=job_type,
        status=status_filter,
        limit=int(limit),
        offset=int(offset),
    )

    return JobsResponse(
        jobs=jobs,
        pagination={
            "limit": int(limit),
            "offset": int(offset),
            "count": len(jobs),
        },
    )


@jobs_router.get(
    "/{id}",
    responses={
        200: {"model": Job, "description": "Job detail retrieved"},
    },
    summary="Get job detail",
    response_model_by_alias=True,
)
async def get_job_detail(
    id: StrictStr = Path(..., description="Job ID"),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Job:
    job = await JobService.get_job(db=db, job_id=id, user_id=current_user.id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="작업을 찾을 수 없습니다.",
        )
    return job