# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

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

class BaseVideoManagementApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseVideoManagementApi.subclasses = BaseVideoManagementApi.subclasses + (cls,)
    async def api_videos_get(
        self,
        page: Optional[StrictInt],
        per_page: Optional[StrictInt],
        status: Optional[StrictStr],
    ) -> ApiVideosGet200Response:
        ...


    async def api_videos_id_cancel_post(
        self,
        id: StrictStr,
    ) -> ApiAuthForgotPasswordPost200Response:
        ...


    async def api_videos_id_delete(
        self,
        id: StrictStr,
    ) -> ApiAuthForgotPasswordPost200Response:
        ...


    async def api_videos_id_download_get(
        self,
        id: StrictStr,
        language: Optional[StrictStr],
    ) -> ApiVideosIdDownloadGet200Response:
        ...


    async def api_videos_id_dub_post(
        self,
        id: StrictStr,
        dub_request: DubRequest,
    ) -> ApiVideosIdDubPost202Response:
        ...


    async def api_videos_id_duplicate_post(
        self,
        id: StrictStr,
    ) -> Video:
        ...


    async def api_videos_id_get(
        self,
        id: StrictStr,
    ) -> Video:
        ...


    async def api_videos_id_put(
        self,
        id: StrictStr,
        api_videos_id_put_request: ApiVideosIdPutRequest,
    ) -> Video:
        ...





    async def api_videos_id_status_get(
        self,
        id: StrictStr,
    ) -> JobStatus:
        ...


    async def api_videos_id_thumbnail_post(
        self,
        id: StrictStr,
        thumbnail: Optional[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]]],
        timestamp: Annotated[Optional[Union[StrictFloat, StrictInt]], Field(description="Time in seconds to extract thumbnail from video")],
    ) -> ApiVideosIdThumbnailPost200Response:
        ...


    async def api_videos_languages_get(
        self,
    ) -> List[Language]:
        ...


    async def api_videos_post(
        self,
        api_videos_post_request: ApiVideosPostRequest,
    ) -> Video:
        ...





    async def api_videos_upload_post(
        self,
        file: Optional[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]]],
        title: Optional[StrictStr],
        description: Optional[StrictStr],
    ) -> Video:
        ...


    async def api_videos_upload_url_post(
        self,
        api_videos_upload_url_post_request: ApiVideosUploadUrlPostRequest,
    ) -> ApiVideosUploadUrlPost200Response:
        ...


    async def api_videos_voices_get(
        self,
        language: StrictStr,
    ) -> List[Voice]:
        ...
