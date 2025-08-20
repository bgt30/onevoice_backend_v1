# S3 스토리지 관리 서비스 로직
import os
import mimetypes
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, BinaryIO
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException, status, UploadFile

from app.config import get_settings

settings = get_settings()


class StorageService:
    """S3 스토리지 관리 관련 서비스"""

    def __init__(self):
        """S3 클라이언트 초기화"""
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            self.s3_client = None
            self.use_s3 = False
        else:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
                self.use_s3 = True
            except (ClientError, NoCredentialsError):
                self.s3_client = None
                self.use_s3 = False

    async def create_presigned_upload_url(
        self,
        file_key: str,
        content_type: str,
        expires_in: int = 3600
    ) -> str:
        """S3 업로드용 프리사인드 URL 생성"""
        if not self.use_s3:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="S3가 구성되어 있지 않습니다."
            )

        try:
            url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': settings.S3_BUCKET_NAME,
                    'Key': file_key,
                    'ContentType': content_type
                },
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"프리사인드 URL 생성 실패: {str(e)}"
            )

    async def create_presigned_download_url(
        self,
        file_key: str,
        expires_in: int = 3600,
        filename: Optional[str] = None
    ) -> str:
        """S3 다운로드용 프리사인드 URL 생성"""
        if not self.use_s3:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="S3가 구성되어 있지 않습니다."
            )

        try:
            params = {
                'Bucket': settings.S3_BUCKET_NAME,
                'Key': file_key
            }
            
            # 다운로드 파일명 지정
            if filename:
                params['ResponseContentDisposition'] = f'attachment; filename="{filename}"'

            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"다운로드 URL 생성 실패: {str(e)}"
            )

    async def upload_file(
        self,
        file: UploadFile,
        file_key: str,
        content_type: Optional[str] = None
    ) -> str:
        """파일을 S3에 직접 업로드"""
        if not self.use_s3:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="S3가 구성되어 있지 않습니다."
            )

        if content_type is None:
            content_type = file.content_type or 'application/octet-stream'

        try:
            # 파일 내용을 메모리에 읽기
            file_content = await file.read()
            
            # S3에 업로드
            self.s3_client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
                ServerSideEncryption='AES256'
            )
            
            # 업로드된 파일 URL 반환
            return f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"
            
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"파일 업로드 실패: {str(e)}"
            )
        finally:
            # 파일 포인터를 처음으로 되돌리기
            await file.seek(0)

    async def upload_local_file(
        self,
        local_path: str,
        file_key: str,
        content_type: Optional[str] = None
    ) -> str:
        """로컬 경로의 파일을 S3에 업로드 (AI 파이프라인 산출물 업로드용)

        Args:
            local_path: 업로드할 로컬 파일 경로
            file_key: 스토리지에 저장할 키(경로)
            content_type: 콘텐츠 타입 (지정하지 않으면 파일 확장자 기반 추정)

        Returns:
            업로드된 파일의 공개 URL (S3)
        """
        if not os.path.exists(local_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"업로드할 파일을 찾을 수 없습니다: {local_path}"
            )

        if not self.use_s3:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="S3가 구성되어 있지 않습니다."
            )

        if content_type is None:
            content_type = mimetypes.guess_type(local_path)[0] or 'application/octet-stream'

        try:
            extra_args = { 'ServerSideEncryption': 'AES256' }
            if content_type:
                extra_args['ContentType'] = content_type
            # boto3 upload_file은 비동기가 아니지만, 내부적으로 블로킹 호출을 수행
            # 여기서는 단순 업로드이므로 그대로 사용
            self.s3_client.upload_file(
                Filename=local_path,
                Bucket=settings.S3_BUCKET_NAME,
                Key=file_key,
                ExtraArgs=extra_args
            )
            return f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"파일 업로드 실패: {str(e)}"
            )

    async def download_file(self, file_key: str, destination_path: str) -> bool:
        """스토리지에서 파일을 다운로드하여 로컬 경로에 저장

        Args:
            file_key: 스토리지의 파일 키
            destination_path: 저장할 로컬 경로

        Returns:
            성공 여부
        """
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        if not self.use_s3:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="S3가 구성되어 있지 않습니다."
            )

        try:
            self.s3_client.download_file(settings.S3_BUCKET_NAME, file_key, destination_path)
            return True
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"파일 다운로드 실패: {str(e)}"
            )

    async def delete_file(self, file_key: str) -> bool:
        """S3에서 파일 삭제"""
        if not self.use_s3:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="S3가 구성되어 있지 않습니다."
            )

        try:
            self.s3_client.delete_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=file_key
            )
            return True
        except ClientError as e:
            # 파일이 존재하지 않는 경우는 성공으로 처리
            if e.response['Error']['Code'] == 'NoSuchKey':
                return True
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"파일 삭제 실패: {str(e)}"
            )

    async def file_exists(self, file_key: str) -> bool:
        """파일 존재 여부 확인"""
        if not self.use_s3:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="S3가 구성되어 있지 않습니다."
            )

        try:
            self.s3_client.head_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=file_key
            )
            return True
        except ClientError:
            return False

    async def get_file_size(self, file_key: str) -> Optional[int]:
        """파일 크기 조회"""
        if not self.use_s3:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="S3가 구성되어 있지 않습니다."
            )

        try:
            response = self.s3_client.head_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=file_key
            )
            return response['ContentLength']
        except ClientError:
            return None

    async def copy_file(self, source_key: str, destination_key: str) -> bool:
        """파일 복사"""
        if not self.use_s3:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="S3가 구성되어 있지 않습니다."
            )

        try:
            copy_source = {
                'Bucket': settings.S3_BUCKET_NAME,
                'Key': source_key
            }
            
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=settings.S3_BUCKET_NAME,
                Key=destination_key,
                ServerSideEncryption='AES256'
            )
            return True
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"파일 복사 실패: {str(e)}"
            )

    def generate_file_key(
        self,
        user_id: str,
        file_type: str,
        filename: str,
        subfolder: Optional[str] = None
    ) -> str:
        """파일 키 생성"""
        # 파일 확장자 추출
        file_ext = os.path.splitext(filename)[1].lower()
        # UUID로 고유한 파일명 생성
        unique_id = str(uuid4())
        new_filename = f"{unique_id}{file_ext}"
        
        # 파일 경로 구성
        if subfolder:
            return f"{file_type}/{user_id}/{subfolder}/{new_filename}"
        else:
            return f"{file_type}/{user_id}/{new_filename}"

    def generate_thumbnail_key(
        self,
        user_id: str,
        video_id: str,
        timestamp: Optional[float] = None
    ) -> str:
        """썸네일 파일 키 생성"""
        if timestamp is not None:
            return f"thumbnails/{user_id}/{video_id}_t{timestamp:.1f}.jpg"
        else:
            return f"thumbnails/{user_id}/{video_id}.jpg"

    async def validate_file_type(
        self,
        file: UploadFile,
        allowed_types: list
    ) -> bool:
        """파일 타입 검증"""
        if not file.content_type:
            return False
            
        # MIME 타입 검증
        if file.content_type not in allowed_types:
            return False
            
        # 파일 확장자 검증
        if file.filename:
            file_ext = os.path.splitext(file.filename)[1].lower()
            allowed_extensions = [
                mimetypes.guess_extension(mime_type) 
                for mime_type in allowed_types
            ]
            if file_ext not in allowed_extensions:
                return False
                
        return True

# 전역 Storage Service 인스턴스
storage_service = StorageService()