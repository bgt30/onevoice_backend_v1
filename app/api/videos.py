# Video Management API endpoints
# Endpoints:
# - GET /api/videos
# - GET /api/videos/{id}
# - PUT /api/videos/{id}
# - DELETE /api/videos/{id}
# - POST /api/videos
# - POST /api/videos/upload-url
# - GET /api/videos/{id}/download
# - POST /api/videos/{id}/dub
# - POST /api/videos/{id}/duplicate

# - POST /api/videos/{id}/thumbnail
# - GET /api/videos/languages
# - GET /api/videos/voices


from fastapi import APIRouter, Body, Depends, Form, HTTPException, Path, Query, status, UploadFile, File, BackgroundTasks
from pydantic import Field, StrictBytes, StrictFloat, StrictInt, StrictStr
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple, Union
from typing_extensions import Annotated

from app.dependecies import get_db, get_current_active_user, check_credits
from app.models.user import User as UserModel
from app.services.video_service import VideoService
from app.services.dubbing_service import DubbingService
from app.schemas import (
    ForgotPasswordResponse,
    VideosResponse,
    DownloadResponse,
    DubResponse,
    VideoUpdateRequest,
    ThumbnailUploadResponse,
    VideoCreateRequest,
    UploadUrlRequest,
    UploadUrlResponse,
    DubRequest,
    Language,
    Video,
    Voice,
    FileType,
)

router = APIRouter(prefix="/api/videos", tags=["Video Management"])


@router.get(
    "",
    responses={
        200: {"model": VideosResponse, "description": "Videos retrieved"},
    },
    summary="Get user videos",
    response_model_by_alias=True,
)
async def get_videos(
    page: Optional[StrictInt] = Query(1, description=""),
    per_page: Optional[StrictInt] = Query(20, description=""),
    status: Optional[StrictStr] = Query(None, description=""),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> VideosResponse:
    """Get user videos with pagination and filtering"""
    return await VideoService.get_videos(db, current_user, page or 1, per_page or 20, status)


@router.post(
    "",
    responses={
        201: {"model": Video, "description": "Video created successfully"},
    },
    summary="Create new video",
    response_model_by_alias=True,
)
async def create_video(
    request: VideoCreateRequest = Body(..., description=""),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Video:
    """Create new video entry"""
    return await VideoService.create_video(db, current_user, request)


@router.get(
    "/{id}",
    responses={
        200: {"model": Video, "description": "Video retrieved"},
    },
    summary="Get video by ID",
    response_model_by_alias=True,
)
async def get_video(
    id: StrictStr = Path(..., description=""),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Video:
    """Get video details by ID"""
    return await VideoService.get_video(db, current_user, id)


@router.put(
    "/{id}",
    responses={
        200: {"model": Video, "description": "Video updated successfully"},
    },
    summary="Update video",
    response_model_by_alias=True,
)
async def update_video(
    id: StrictStr = Path(..., description=""),
    request: VideoUpdateRequest = Body(..., description=""),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Video:
    """Update video metadata"""
    return await VideoService.update_video(db, current_user, id, request)


@router.delete(
    "/{id}",
    responses={
        200: {"model": ForgotPasswordResponse, "description": "Video deleted successfully"},
    },
    summary="Delete video",
    response_model_by_alias=True,
)
async def delete_video(
    id: StrictStr = Path(..., description=""),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ForgotPasswordResponse:
    """Delete video permanently"""
    return await VideoService.delete_video(db, current_user, id)





@router.post(
    "/upload-url",
    responses={
        200: {"model": UploadUrlResponse, "description": "Upload URL generated"},
    },
    summary="Get pre-signed upload URL",
    response_model_by_alias=True,
)
async def get_upload_url(
    request: UploadUrlRequest = Body(..., description=""),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> UploadUrlResponse:
    """Get pre-signed URL for direct S3 upload"""
    return await VideoService.get_upload_url(db, current_user, request)


@router.get(
    "/{id}/download",
    responses={
        200: {"model": DownloadResponse, "description": "Download URL generated"},
    },
    summary="Download processed video or dubbed outputs",
    response_model_by_alias=True,
)
async def download_video(
    id: StrictStr = Path(..., description=""),
    language: Optional[StrictStr] = Query(None, description="Target language code for dubbed outputs (e.g., 'en', 'ja')"),
    file_type: Optional[FileType] = Query(
        None,
        description=(
            "File type to download: 'dubbed_video' | 'subtitle_video' | 'dub_subtitles' | "
            "'translation_subtitles' | 'source_subtitles' | 'original'. Defaults to 'dubbed_video'."
        ),
    ),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> DownloadResponse:
    """Return a presigned URL for the requested output."""
    # Convert Enum to raw value for service layer
    file_type_value = file_type.value if file_type is not None else None
    return await VideoService.get_download_url(db, current_user, id, language, file_type_value)


@router.post(
    "/{id}/dub",
    responses={
        202: {"model": DubResponse, "description": "Dubbing process started"},
    },
    summary="Start video dubbing process",
    response_model_by_alias=True,
)
async def start_dubbing(
    background_tasks: BackgroundTasks,
    id: StrictStr = Path(..., description=""),
    dub_request: DubRequest = Body(..., description=""),
    current_user: UserModel = Depends(check_credits),  # 크레딧 체크 필요
    db: AsyncSession = Depends(get_db)
) -> DubResponse:
    """Start video dubbing process"""
    # 1. DubbingService로 Job 생성/과금/상태 전이
    dub_response = await DubbingService.start_dubbing_job(db, current_user, id, dub_request)
    
    # 2. DubbingService를 BackgroundTasks로 실행
    background_tasks.add_task(
        DubbingService.execute_dubbing_pipeline,
        dub_response.job_id
    )
    
    return dub_response


@router.post(
    "/{id}/duplicate",
    responses={
        201: {"model": Video, "description": "Video duplicated successfully"},
    },
    summary="Duplicate video",
    response_model_by_alias=True,
)
async def duplicate_video(
    id: StrictStr = Path(..., description=""),
    current_user: UserModel = Depends(check_credits),  # 크레딧 체크 필요
    db: AsyncSession = Depends(get_db)
) -> Video:
    """Create a copy of existing video"""
    return await VideoService.duplicate_video(db, current_user, id)



@router.post(
    "/{id}/thumbnail",
    responses={
        200: {"model": ThumbnailUploadResponse, "description": "Thumbnail generated successfully"},
    },
    summary="Generate or update video thumbnail",
    response_model_by_alias=True,
)
async def update_thumbnail(
    id: StrictStr = Path(..., description=""),
    thumbnail: Optional[UploadFile] = File(None, description="Thumbnail image file"),
    timestamp: Annotated[Optional[Union[StrictFloat, StrictInt]], Field(description="Time in seconds to extract thumbnail from video")] = Form(None, description="Time in seconds to extract thumbnail from video"),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ThumbnailUploadResponse:
    """Generate or update video thumbnail"""
    return await VideoService.update_thumbnail(db, current_user, id, thumbnail, timestamp)


@router.get(
    "/languages",
    responses={
        200: {"model": List[Language], "description": "Supported languages retrieved"},
    },
    summary="Get supported languages",
    response_model_by_alias=True,
)
async def get_languages(
    # 공개 엔드포인트 - 인증 불필요
) -> List[Language]:
    """Get list of supported languages for dubbing"""
    return await VideoService.get_supported_languages()


@router.get(
    "/voices",
    responses={
        200: {"model": List[Voice], "description": "Available voices retrieved"},
    },
    summary="Get available voices for language",
    response_model_by_alias=True,
)
async def get_voices(
    language: StrictStr = Query(..., description=""),
    # 공개 엔드포인트 - 인증 불필요
) -> List[Voice]:
    """Get available voices for specified language"""
    return await VideoService.get_available_voices(language)


 