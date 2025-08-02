# Job Status & Management API endpoints
# Endpoints:
# - GET /api/videos/{id}/status (job status polling)
# - POST /api/videos/{id}/cancel (cancel processing job)

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import StrictStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependecies import get_db, get_current_active_user
from app.models.user import User as UserModel
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
    # TODO: Implement get job status logic
    raise HTTPException(status_code=501, detail="Not implemented")


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
    # TODO: Implement cancel job logic
    raise HTTPException(status_code=501, detail="Not implemented") 