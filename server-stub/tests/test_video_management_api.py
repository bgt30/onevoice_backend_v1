# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictBytes, StrictFloat, StrictInt, StrictStr, field_validator  # noqa: F401
from typing import List, Optional, Tuple, Union  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from openapi_server.models.api_auth_forgot_password_post200_response import ApiAuthForgotPasswordPost200Response  # noqa: F401
from openapi_server.models.api_videos_get200_response import ApiVideosGet200Response  # noqa: F401
from openapi_server.models.api_videos_id_download_get200_response import ApiVideosIdDownloadGet200Response  # noqa: F401
from openapi_server.models.api_videos_id_dub_post202_response import ApiVideosIdDubPost202Response  # noqa: F401
from openapi_server.models.api_videos_id_put_request import ApiVideosIdPutRequest  # noqa: F401

from openapi_server.models.api_videos_id_thumbnail_post200_response import ApiVideosIdThumbnailPost200Response  # noqa: F401
from openapi_server.models.api_videos_post_request import ApiVideosPostRequest  # noqa: F401

from openapi_server.models.api_videos_upload_url_post200_response import ApiVideosUploadUrlPost200Response  # noqa: F401
from openapi_server.models.api_videos_upload_url_post_request import ApiVideosUploadUrlPostRequest  # noqa: F401
from openapi_server.models.dub_request import DubRequest  # noqa: F401
from openapi_server.models.job_status import JobStatus  # noqa: F401
from openapi_server.models.language import Language  # noqa: F401
from openapi_server.models.video import Video  # noqa: F401
from openapi_server.models.voice import Voice  # noqa: F401


def test_api_videos_get(client: TestClient):
    """Test case for api_videos_get

    Get user videos
    """
    params = [("page", 1),     ("per_page", 20),     ("status", 'status_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/videos",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_videos_id_cancel_post(client: TestClient):
    """Test case for api_videos_id_cancel_post

    Cancel video processing
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/videos/{id}/cancel".format(id='id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_videos_id_delete(client: TestClient):
    """Test case for api_videos_id_delete

    Delete video
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/api/videos/{id}".format(id='id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_videos_id_download_get(client: TestClient):
    """Test case for api_videos_id_download_get

    Download processed video
    """
    params = [("language", 'language_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/videos/{id}/download".format(id='id_example'),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_videos_id_dub_post(client: TestClient):
    """Test case for api_videos_id_dub_post

    Start video dubbing process
    """
    dub_request = {"voice_id":"voice_id","target_language":"target_language","preserve_background_music":1}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/videos/{id}/dub".format(id='id_example'),
    #    headers=headers,
    #    json=dub_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_videos_id_duplicate_post(client: TestClient):
    """Test case for api_videos_id_duplicate_post

    Duplicate video
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/videos/{id}/duplicate".format(id='id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_videos_id_get(client: TestClient):
    """Test case for api_videos_id_get

    Get video by ID
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/videos/{id}".format(id='id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_videos_id_put(client: TestClient):
    """Test case for api_videos_id_put

    Update video
    """
    api_videos_id_put_request = openapi_server.ApiVideosIdPutRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PUT",
    #    "/api/videos/{id}".format(id='id_example'),
    #    headers=headers,
    #    json=api_videos_id_put_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200





def test_api_videos_id_status_get(client: TestClient):
    """Test case for api_videos_id_status_get

    Get video processing status
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/videos/{id}/status".format(id='id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_videos_id_thumbnail_post(client: TestClient):
    """Test case for api_videos_id_thumbnail_post

    Generate or update video thumbnail
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    data = {
        "thumbnail": '/path/to/file',
        "timestamp": 3.4
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/videos/{id}/thumbnail".format(id='id_example'),
    #    headers=headers,
    #    data=data,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_videos_languages_get(client: TestClient):
    """Test case for api_videos_languages_get

    Get supported languages
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/videos/languages",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_videos_post(client: TestClient):
    """Test case for api_videos_post

    Create new video
    """
    api_videos_post_request = openapi_server.ApiVideosPostRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/videos",
    #    headers=headers,
    #    json=api_videos_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200





def test_api_videos_upload_post(client: TestClient):
    """Test case for api_videos_upload_post

    Upload video file
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    data = {
        "file": '/path/to/file',
        "title": 'title_example',
        "description": 'description_example'
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/videos/upload",
    #    headers=headers,
    #    data=data,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_videos_upload_url_post(client: TestClient):
    """Test case for api_videos_upload_url_post

    Get pre-signed upload URL
    """
    api_videos_upload_url_post_request = openapi_server.ApiVideosUploadUrlPostRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/videos/upload-url",
    #    headers=headers,
    #    json=api_videos_upload_url_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_videos_voices_get(client: TestClient):
    """Test case for api_videos_voices_get

    Get available voices for language
    """
    params = [("language", 'language_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/videos/voices",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

