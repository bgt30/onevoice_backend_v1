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
            # S3를 사용하지 않는 경우 로컬 개발용 URL 반환
            return f"http://localhost:8000/uploads/{file_key}"

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
            # S3를 사용하지 않는 경우 로컬 개발용 URL 반환
            return f"http://localhost:8000/downloads/{file_key}"

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
            # S3를 사용하지 않는 경우 로컬 저장
            return await self._save_file_locally(file, file_key)

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

    async def delete_file(self, file_key: str) -> bool:
        """S3에서 파일 삭제"""
        if not self.use_s3:
            # 로컬 파일 삭제
            return await self._delete_file_locally(file_key)

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
            return await self._file_exists_locally(file_key)

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
            return await self._get_file_size_locally(file_key)

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
            return await self._copy_file_locally(source_key, destination_key)

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

    # 로컬 개발용 메소드들 (S3를 사용하지 않을 때)
    async def _save_file_locally(self, file: UploadFile, file_key: str) -> str:
        """로컬에 파일 저장"""
        local_path = f"storage/{file_key}"
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        with open(local_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        await file.seek(0)
        return f"http://localhost:8000/storage/{file_key}"

    async def _delete_file_locally(self, file_key: str) -> bool:
        """로컬 파일 삭제"""
        local_path = f"storage/{file_key}"
        try:
            if os.path.exists(local_path):
                os.remove(local_path)
            return True
        except Exception:
            return False

    async def _file_exists_locally(self, file_key: str) -> bool:
        """로컬 파일 존재 확인"""
        local_path = f"storage/{file_key}"
        return os.path.exists(local_path)

    async def _get_file_size_locally(self, file_key: str) -> Optional[int]:
        """로컬 파일 크기 조회"""
        local_path = f"storage/{file_key}"
        try:
            return os.path.getsize(local_path)
        except Exception:
            return None

    async def _copy_file_locally(self, source_key: str, destination_key: str) -> bool:
        """로컬 파일 복사"""
        source_path = f"storage/{source_key}"
        dest_path = f"storage/{destination_key}"
        
        try:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(source_path, 'rb') as src, open(dest_path, 'wb') as dst:
                dst.write(src.read())
            return True
        except Exception:
            return False


# 전역 Storage Service 인스턴스
storage_service = StorageService()