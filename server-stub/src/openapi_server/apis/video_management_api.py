# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.video_management_api_base import BaseVideoManagementApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from pydantic import Field, StrictBytes, StrictFloat, StrictInt, StrictStr, field_validator
from typing import List, Optional, Tuple, Union
from typing_extensions import Annotated
from openapi_server.models.api_auth_forgot_password_post200_response import ApiAuthForgotPasswordPost200Response
from openapi_server.models.api_videos_get200_response import ApiVideosGet200Response
from openapi_server.models.api_videos_id_download_get200_response import ApiVideosIdDownloadGet200Response
from openapi_server.models.api_videos_id_dub_post202_response import ApiVideosIdDubPost202Response
from openapi_server.models.api_videos_id_put_request import ApiVideosIdPutRequest

from openapi_server.models.api_videos_id_thumbnail_post200_response import ApiVideosIdThumbnailPost200Response
from openapi_server.models.api_videos_post_request import ApiVideosPostRequest

from openapi_server.models.api_videos_upload_url_post200_response import ApiVideosUploadUrlPost200Response
from openapi_server.models.api_videos_upload_url_post_request import ApiVideosUploadUrlPostRequest
from openapi_server.models.dub_request import DubRequest
from openapi_server.models.job_status import JobStatus
from openapi_server.models.language import Language
from openapi_server.models.video import Video
from openapi_server.models.voice import Voice
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/api/videos",
    responses={
        200: {"model": ApiVideosGet200Response, "description": "Videos retrieved"},
    },
    tags=["Video Management"],
    summary="Get user videos",
    response_model_by_alias=True,
)
async def api_videos_get(
    page: Optional[StrictInt] = Query(1, description="", alias="page"),
    per_page: Optional[StrictInt] = Query(20, description="", alias="per_page"),
    status: Optional[StrictStr] = Query(None, description="", alias="status"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiVideosGet200Response:
    if not BaseVideoManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseVideoManagementApi.subclasses[0]().api_videos_get(page, per_page, status)


@router.post(
    "/api/videos/{id}/cancel",
    responses={
        200: {"model": ApiAuthForgotPasswordPost200Response, "description": "Processing cancelled"},
    },
    tags=["Video Management"],
    summary="Cancel video processing",
    response_model_by_alias=True,
)
async def api_videos_id_cancel_post(
    id: StrictStr = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiAuthForgotPasswordPost200Response:
    if not BaseVideoManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseVideoManagementApi.subclasses[0]().api_videos_id_cancel_post(id)


@router.delete(
    "/api/videos/{id}",
    responses={
        200: {"model": ApiAuthForgotPasswordPost200Response, "description": "Video deleted successfully"},
    },
    tags=["Video Management"],
    summary="Delete video",
    response_model_by_alias=True,
)
async def api_videos_id_delete(
    id: StrictStr = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiAuthForgotPasswordPost200Response:
    if not BaseVideoManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseVideoManagementApi.subclasses[0]().api_videos_id_delete(id)


@router.get(
    "/api/videos/{id}/download",
    responses={
        200: {"model": ApiVideosIdDownloadGet200Response, "description": "Download URL generated"},
    },
    tags=["Video Management"],
    summary="Download processed video",
    response_model_by_alias=True,
)
async def api_videos_id_download_get(
    id: StrictStr = Path(..., description=""),
    language: Optional[StrictStr] = Query(None, description="", alias="language"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiVideosIdDownloadGet200Response:
    if not BaseVideoManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseVideoManagementApi.subclasses[0]().api_videos_id_download_get(id, language)


@router.post(
    "/api/videos/{id}/dub",
    responses={
        202: {"model": ApiVideosIdDubPost202Response, "description": "Dubbing process started"},
    },
    tags=["Video Management"],
    summary="Start video dubbing process",
    response_model_by_alias=True,
)
async def api_videos_id_dub_post(
    id: StrictStr = Path(..., description=""),
    dub_request: DubRequest = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiVideosIdDubPost202Response:
    if not BaseVideoManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseVideoManagementApi.subclasses[0]().api_videos_id_dub_post(id, dub_request)


@router.post(
    "/api/videos/{id}/duplicate",
    responses={
        201: {"model": Video, "description": "Video duplicated successfully"},
    },
    tags=["Video Management"],
    summary="Duplicate video",
    response_model_by_alias=True,
)
async def api_videos_id_duplicate_post(
    id: StrictStr = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Video:
    if not BaseVideoManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseVideoManagementApi.subclasses[0]().api_videos_id_duplicate_post(id)


@router.get(
    "/api/videos/{id}",
    responses={
        200: {"model": Video, "description": "Video retrieved"},
    },
    tags=["Video Management"],
    summary="Get video by ID",
    response_model_by_alias=True,
)
async def api_videos_id_get(
    id: StrictStr = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Video:
    if not BaseVideoManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseVideoManagementApi.subclasses[0]().api_videos_id_get(id)


@router.put(
    "/api/videos/{id}",
    responses={
        200: {"model": Video, "description": "Video updated successfully"},
    },
    tags=["Video Management"],
    summary="Update video",
    response_model_by_alias=True,
)
async def api_videos_id_put(
    id: StrictStr = Path(..., description=""),
    api_videos_id_put_request: ApiVideosIdPutRequest = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Video:
    if not BaseVideoManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseVideoManagementApi.subclasses[0]().api_videos_id_put(id, api_videos_id_put_request)




@router.get(
    "/api/videos/{id}/status",
    responses={
        200: {"model": JobStatus, "description": "Processing status retrieved"},
    },
    tags=["Video Management"],
    summary="Get video processing status",
    response_model_by_alias=True,
)
async def api_videos_id_status_get(
    id: StrictStr = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> JobStatus:
    if not BaseVideoManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseVideoManagementApi.subclasses[0]().api_videos_id_status_get(id)


@router.post(
    "/api/videos/{id}/thumbnail",
    responses={
        200: {"model": ApiVideosIdThumbnailPost200Response, "description": "Thumbnail generated successfully"},
    },
    tags=["Video Management"],
    summary="Generate or update video thumbnail",
    response_model_by_alias=True,
)
async def api_videos_id_thumbnail_post(
    id: StrictStr = Path(..., description=""),
    thumbnail: Optional[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]]] = Form(None, description=""),
    timestamp: Annotated[Optional[Union[StrictFloat, StrictInt]], Field(description="Time in seconds to extract thumbnail from video")] = Form(None, description="Time in seconds to extract thumbnail from video"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiVideosIdThumbnailPost200Response:
    if not BaseVideoManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseVideoManagementApi.subclasses[0]().api_videos_id_thumbnail_post(id, thumbnail, timestamp)


@router.get(
    "/api/videos/languages",
    responses={
        200: {"model": List[Language], "description": "Supported languages retrieved"},
    },
    tags=["Video Management"],
    summary="Get supported languages",
    response_model_by_alias=True,
)
async def api_videos_languages_get(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[Language]:
    if not BaseVideoManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseVideoManagementApi.subclasses[0]().api_videos_languages_get()


@router.post(
    "/api/videos",
    responses={
        201: {"model": Video, "description": "Video created successfully"},
    },
    tags=["Video Management"],
    summary="Create new video",
    response_model_by_alias=True,
)
async def api_videos_post(
    api_videos_post_request: ApiVideosPostRequest = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Video:
    if not BaseVideoManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseVideoManagementApi.subclasses[0]().api_videos_post(api_videos_post_request)




@router.post(
    "/api/videos/upload",
    responses={
        201: {"model": Video, "description": "Video uploaded successfully"},
    },
    tags=["Video Management"],
    summary="Upload video file",
    response_model_by_alias=True,
)
async def api_videos_upload_post(
    file: Optional[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]]] = Form(None, description=""),
    title: Optional[StrictStr] = Form(None, description=""),
    description: Optional[StrictStr] = Form(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Video:
    if not BaseVideoManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseVideoManagementApi.subclasses[0]().api_videos_upload_post(file, title, description)


@router.post(
    "/api/videos/upload-url",
    responses={
        200: {"model": ApiVideosUploadUrlPost200Response, "description": "Upload URL generated"},
    },
    tags=["Video Management"],
    summary="Get pre-signed upload URL",
    response_model_by_alias=True,
)
async def api_videos_upload_url_post(
    api_videos_upload_url_post_request: ApiVideosUploadUrlPostRequest = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ApiVideosUploadUrlPost200Response:
    if not BaseVideoManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseVideoManagementApi.subclasses[0]().api_videos_upload_url_post(api_videos_upload_url_post_request)


@router.get(
    "/api/videos/voices",
    responses={
        200: {"model": List[Voice], "description": "Available voices retrieved"},
    },
    tags=["Video Management"],
    summary="Get available voices for language",
    response_model_by_alias=True,
)
async def api_videos_voices_get(
    language: StrictStr = Query(None, description="", alias="language"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> List[Voice]:
    if not BaseVideoManagementApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseVideoManagementApi.subclasses[0]().api_videos_voices_get(language)
