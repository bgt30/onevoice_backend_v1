# 비디오 관리 서비스 로직
import json
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from uuid import uuid4

from fastapi import HTTPException, status, UploadFile
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.video import Video, MediaFile
from app.models.user import User
from app.config import get_settings
from app.schemas import (
    Video as VideoSchema,
    VideoCreateRequest,
    VideoUpdateRequest,
    VideosResponse,
    UploadUrlRequest,
    UploadUrlResponse,
    DownloadResponse,
    ThumbnailUploadResponse,
    DubRequest,
    DubResponse,
    Language,
    Voice,
    ForgotPasswordResponse
)
from app.services.storage_service import storage_service
from app.services.job_service import JobService

settings = get_settings()


class VideoService:
    """비디오 관리 관련 서비스"""

    @staticmethod
    async def get_videos(
        db: AsyncSession,
        user: User,
        page: int = 1,
        per_page: int = 20,
        status_filter: Optional[str] = None
    ) -> VideosResponse:
        """사용자 비디오 목록 조회"""
        offset = (page - 1) * per_page
        
        # 쿼리 구성
        query = select(Video).where(Video.user_id == user.id)
        
        if status_filter:
            query = query.where(Video.status == status_filter)
            
        query = query.order_by(desc(Video.created_at)).offset(offset).limit(per_page)
        
        # 비디오 목록 조회
        result = await db.execute(query)
        videos = result.scalars().all()
        
        # 전체 개수 조회
        count_query = select(func.count(Video.id)).where(Video.user_id == user.id)
        if status_filter:
            count_query = count_query.where(Video.status == status_filter)
            
        total_count = await db.execute(count_query)
        total = total_count.scalar() or 0

        # 스키마로 변환
        video_list = []
        for video in videos:
            # target_languages JSON 파싱
            target_languages = []
            if video.target_languages:
                try:
                    target_languages = json.loads(video.target_languages)
                except:
                    pass

            video_list.append(VideoSchema(
                id=video.id,
                title=video.title,
                description=video.description,
                duration=video.duration,
                original_language=video.original_language,
                target_languages=target_languages,
                status=video.status,
                thumbnail_url=video.thumbnail_url,
                video_url=video.processed_file_path or video.original_file_path,
                created_at=video.created_at,
                updated_at=video.updated_at
            ))

        pagination = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }

        return VideosResponse(videos=video_list, pagination=pagination)

    @staticmethod
    async def create_video(
        db: AsyncSession,
        user: User,
        request: VideoCreateRequest
    ) -> VideoSchema:
        """새 비디오 생성"""
        video = Video(
            user_id=user.id,
            title=request.title,
            description=request.description,
            original_language=request.original_language,
            status="uploaded"
        )

        db.add(video)
        await db.commit()
        await db.refresh(video)

        return VideoSchema(
            id=video.id,
            title=video.title,
            description=video.description,
            duration=video.duration,
            original_language=video.original_language,
            target_languages=[],
            status=video.status,
            thumbnail_url=video.thumbnail_url,
            video_url=video.original_file_path,
            created_at=video.created_at,
            updated_at=video.updated_at
        )

    @staticmethod
    async def get_video(
        db: AsyncSession,
        user: User,
        video_id: str
    ) -> VideoSchema:
        """비디오 상세 조회"""
        result = await db.execute(
            select(Video).where(
                and_(Video.id == video_id, Video.user_id == user.id)
            )
        )
        video = result.scalar_one_or_none()

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="비디오를 찾을 수 없습니다."
            )

        # target_languages JSON 파싱
        target_languages = []
        if video.target_languages:
            try:
                target_languages = json.loads(video.target_languages)
            except:
                pass

        return VideoSchema(
            id=video.id,
            title=video.title,
            description=video.description,
            duration=video.duration,
            original_language=video.original_language,
            target_languages=target_languages,
            status=video.status,
            thumbnail_url=video.thumbnail_url,
            video_url=video.processed_file_path or video.original_file_path,
            created_at=video.created_at,
            updated_at=video.updated_at
        )

    @staticmethod
    async def update_video(
        db: AsyncSession,
        user: User,
        video_id: str,
        request: VideoUpdateRequest
    ) -> VideoSchema:
        """비디오 정보 업데이트"""
        result = await db.execute(
            select(Video).where(
                and_(Video.id == video_id, Video.user_id == user.id)
            )
        )
        video = result.scalar_one_or_none()

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="비디오를 찾을 수 없습니다."
            )

        # 업데이트
        if request.title is not None:
            video.title = request.title
        if request.description is not None:
            video.description = request.description

        video.updated_at = datetime.now(timezone.utc)

        try:
            await db.commit()
            await db.refresh(video)
            return await VideoService.get_video(db, user, video_id)
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="비디오 업데이트 중 오류가 발생했습니다."
            )

    @staticmethod
    async def delete_video(
        db: AsyncSession,
        user: User,
        video_id: str
    ) -> ForgotPasswordResponse:
        """비디오 삭제"""
        result = await db.execute(
            select(Video).where(
                and_(Video.id == video_id, Video.user_id == user.id)
            )
        )
        video = result.scalar_one_or_none()

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="비디오를 찾을 수 없습니다."
            )

        try:
            # S3에서 파일들 삭제
            if video.s3_key:
                await storage_service.delete_file(video.s3_key)
            
            # 썸네일 삭제
            if video.thumbnail_url and video.thumbnail_url.startswith("http"):
                parts = video.thumbnail_url.split('/')
                if len(parts) >= 3:
                    thumbnail_key = '/'.join(parts[-3:])
                    await storage_service.delete_file(thumbnail_key)
            
            # 처리된 파일이 있다면 삭제
            if video.processed_file_path and video.processed_file_path != video.original_file_path:
                # 처리된 파일의 키 생성 (URL에서 추출)
                if video.processed_file_path.startswith("http"):
                    parts = video.processed_file_path.split('/')
                    if len(parts) >= 3:
                        processed_key = '/'.join(parts[-3:])
                        await storage_service.delete_file(processed_key)

            await db.delete(video)
            await db.commit()
            return ForgotPasswordResponse(message="비디오가 성공적으로 삭제되었습니다.")
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="비디오 삭제 중 오류가 발생했습니다."
            )

    @staticmethod
    async def upload_video(
        db: AsyncSession,
        user: User,
        file: UploadFile,
        title: str,
        description: Optional[str] = None
    ) -> VideoSchema:
        """비디오 파일 직접 업로드"""
        # 파일 크기 체크
        if hasattr(file, 'size') and file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"파일 크기가 너무 큽니다. 최대 {settings.MAX_FILE_SIZE / (1024*1024):.0f}MB까지 업로드 가능합니다."
            )

        # 비디오 파일 타입 검증
        allowed_types = ["video/mp4", "video/avi", "video/mov", "video/mkv", "video/webm"]
        if not await storage_service.validate_file_type(file, allowed_types):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="지원되지 않는 비디오 형식입니다."
            )

        try:
            # 파일 키 생성
            file_key = storage_service.generate_file_key(
                user_id=user.id,
                file_type="videos",
                filename=file.filename,
                subfolder="original"
            )
            
            # S3에 업로드
            video_url = await storage_service.upload_file(
                file=file,
                file_key=file_key
            )
            
            video = Video(
                user_id=user.id,
                title=title,
                description=description,
                original_file_path=video_url,
                s3_bucket=settings.S3_BUCKET_NAME,
                s3_key=file_key,
                file_size=file.size if hasattr(file, 'size') else None,
                format=file.filename.split('.')[-1].lower() if file.filename else None,
                status="uploaded"
            )

            db.add(video)
            await db.commit()
            await db.refresh(video)

            return VideoSchema(
                id=video.id,
                title=video.title,
                description=video.description,
                duration=video.duration,
                original_language=video.original_language,
                target_languages=[],
                status=video.status,
                thumbnail_url=video.thumbnail_url,
                video_url=video.original_file_path,
                created_at=video.created_at,
                updated_at=video.updated_at
            )
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="비디오 업로드 중 오류가 발생했습니다."
            )

    @staticmethod
    async def get_upload_url(
        db: AsyncSession,
        user: User,
        request: UploadUrlRequest
    ) -> UploadUrlResponse:
        """S3 업로드용 프리사인드 URL 생성"""
        try:
            video_id = str(uuid4())
            
            # 파일 키 생성
            file_key = storage_service.generate_file_key(
                user_id=user.id,
                file_type="videos",
                filename=request.filename,
                subfolder="original"
            )
            
            # 프리사인드 URL 생성
            upload_url = await storage_service.create_presigned_upload_url(
                file_key=file_key,
                content_type=request.content_type,
                expires_in=3600  # 1시간
            )
            
            # 임시 비디오 레코드 생성
            video = Video(
                id=video_id,
                user_id=user.id,
                title=request.filename,
                s3_bucket=settings.S3_BUCKET_NAME,
                s3_key=file_key,
                status="pending"
            )
            
            db.add(video)
            await db.commit()

            return UploadUrlResponse(
                upload_url=upload_url,
                video_id=video_id
            )
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="업로드 URL 생성 중 오류가 발생했습니다."
            )

    @staticmethod
    async def get_download_url(
        db: AsyncSession,
        user: User,
        video_id: str,
        language: Optional[str] = None
    ) -> DownloadResponse:
        """비디오 다운로드 URL 생성"""
        result = await db.execute(
            select(Video).where(
                and_(Video.id == video_id, Video.user_id == user.id)
            )
        )
        video = result.scalar_one_or_none()

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="비디오를 찾을 수 없습니다."
            )

        if video.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="완료된 비디오만 다운로드 가능합니다."
            )

        try:
            # 다운로드할 파일의 S3 키 결정
            file_key = video.s3_key  # 기본적으로 원본 파일
            
            # 언어별 더빙 파일이 있는 경우 해당 파일 사용
            if language:
                # TODO: 언어별 파일 키 로직 구현
                pass
            
            # 프리사인드 다운로드 URL 생성
            download_url = await storage_service.create_presigned_download_url(
                file_key=file_key,
                expires_in=3600,  # 1시간
                filename=f"{video.title}.{video.format or 'mp4'}"
            )
            
            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

            return DownloadResponse(
                download_url=download_url,
                expires_at=expires_at
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="다운로드 URL 생성 중 오류가 발생했습니다."
            )

    @staticmethod
    async def start_dubbing(
        db: AsyncSession,
        user: User,
        video_id: str,
        dub_request: DubRequest
    ) -> DubResponse:
        """비디오 더빙 프로세스 시작"""
        result = await db.execute(
            select(Video).where(
                and_(Video.id == video_id, Video.user_id == user.id)
            )
        )
        video = result.scalar_one_or_none()

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="비디오를 찾을 수 없습니다."
            )

        if video.status not in ["uploaded", "completed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="업로드되거나 완료된 비디오만 더빙 가능합니다."
            )

        # 더빙 작업 설정
        job_config = {
            "target_language": dub_request.target_language,
            "voice_id": dub_request.voice_id,
            "preserve_background_music": dub_request.preserve_background_music,
            "tts_method": "openai_tts"  # 기본값, 추후 사용자 선택 가능
        }
        
        try:
            # 더빙 작업 생성
            job = await JobService.create_job(
                db=db,
                user_id=user.id,
                job_type="dubbing",
                video_id=video_id,
                config=job_config
            )
            
            # 비디오 상태 업데이트
            video.status = "processing"
            video.processing_started_at = datetime.now(timezone.utc)
            video.updated_at = datetime.now(timezone.utc)
            
            # 크레딧 사용량 계산 및 기록
            credits_used = settings.CREDIT_COST_PER_MINUTE * int(video.duration or 1)
            await JobService.record_credit_usage(
                db=db,
                job=job,
                credits_used=credits_used,
                operation_type="dubbing",
                description=f"더빙 작업: {video.title}"
            )
            
            # NOTE: 실제 더빙 파이프라인은 API 레벨에서 BackgroundTasks로 실행됩니다
            
            return DubResponse(
                job_id=job.id,
                message="더빙 작업이 시작되었습니다."
            )
            
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="더빙 작업 시작 중 오류가 발생했습니다."
            )

    @staticmethod
    async def duplicate_video(
        db: AsyncSession,
        user: User,
        video_id: str
    ) -> VideoSchema:
        """비디오 복제"""
        result = await db.execute(
            select(Video).where(
                and_(Video.id == video_id, Video.user_id == user.id)
            )
        )
        original_video = result.scalar_one_or_none()

        if not original_video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="비디오를 찾을 수 없습니다."
            )

        try:
            # 새 파일 키 생성
            new_file_key = None
            new_video_url = None
            new_thumbnail_url = None

            if original_video.s3_key:
                # 원본 파일명 추출
                original_filename = original_video.s3_key.split('/')[-1]
                new_file_key = storage_service.generate_file_key(
                    user_id=user.id,
                    file_type="videos",
                    filename=original_filename,
                    subfolder="original"
                )
                
                # S3에서 파일 복사
                if await storage_service.copy_file(original_video.s3_key, new_file_key):
                    new_video_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{new_file_key}"

            # 썸네일도 복사 (있는 경우)
            if original_video.thumbnail_url and original_video.thumbnail_url.startswith("http"):
                # 원본 썸네일 키 추출
                thumbnail_parts = original_video.thumbnail_url.split('/')
                if len(thumbnail_parts) >= 3:
                    original_thumbnail_key = '/'.join(thumbnail_parts[-3:])
                    new_thumbnail_key = storage_service.generate_thumbnail_key(
                        user_id=user.id,
                        video_id=str(uuid4())
                    )
                    if await storage_service.copy_file(original_thumbnail_key, new_thumbnail_key):
                        new_thumbnail_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{new_thumbnail_key}"

            # 새 비디오 생성
            new_video = Video(
                user_id=user.id,
                title=f"{original_video.title} (복사본)",
                description=original_video.description,
                duration=original_video.duration,
                file_size=original_video.file_size,
                format=original_video.format,
                resolution=original_video.resolution,
                fps=original_video.fps,
                original_language=original_video.original_language,
                status="uploaded",
                original_file_path=new_video_url or original_video.original_file_path,
                thumbnail_url=new_thumbnail_url,
                s3_bucket=original_video.s3_bucket,
                s3_key=new_file_key
            )

            db.add(new_video)
            await db.commit()
            await db.refresh(new_video)

            return VideoSchema(
                id=new_video.id,
                title=new_video.title,
                description=new_video.description,
                duration=new_video.duration,
                original_language=new_video.original_language,
                target_languages=[],
                status=new_video.status,
                thumbnail_url=new_video.thumbnail_url,
                video_url=new_video.original_file_path,
                created_at=new_video.created_at,
                updated_at=new_video.updated_at
            )
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="비디오 복제 중 오류가 발생했습니다."
            )

    @staticmethod
    async def update_thumbnail(
        db: AsyncSession,
        user: User,
        video_id: str,
        thumbnail_file: Optional[UploadFile] = None,
        timestamp: Optional[float] = None
    ) -> ThumbnailUploadResponse:
        """썸네일 생성/업데이트"""
        result = await db.execute(
            select(Video).where(
                and_(Video.id == video_id, Video.user_id == user.id)
            )
        )
        video = result.scalar_one_or_none()

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="비디오를 찾을 수 없습니다."
            )

        try:
            # 기존 썸네일 삭제
            if video.thumbnail_url and video.thumbnail_url.startswith("http"):
                # URL에서 파일 키 추출
                parts = video.thumbnail_url.split('/')
                if len(parts) >= 3:
                    old_file_key = '/'.join(parts[-3:])
                    await storage_service.delete_file(old_file_key)

            if thumbnail_file:
                # 파일 업로드 방식
                # 이미지 타입 검증
                allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
                if not await storage_service.validate_file_type(thumbnail_file, allowed_types):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="지원되지 않는 이미지 형식입니다."
                    )
                
                file_key = storage_service.generate_thumbnail_key(user.id, video_id)
                thumbnail_url = await storage_service.upload_file(
                    file=thumbnail_file,
                    file_key=file_key
                )
            else:
                # 타임스탬프에서 추출 (실제로는 비디오 처리 서비스에서 추출)
                # 현재는 임시 썸네일 URL 생성
                file_key = storage_service.generate_thumbnail_key(user.id, video_id, timestamp)
                # TODO: 실제 비디오에서 썸네일 추출 로직 구현
                thumbnail_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"

            video.thumbnail_url = thumbnail_url
            video.updated_at = datetime.now(timezone.utc)

            await db.commit()
            return ThumbnailUploadResponse(thumbnail_url=thumbnail_url)
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="썸네일 업데이트 중 오류가 발생했습니다."
            )

    @staticmethod
    async def get_supported_languages() -> List[Language]:
        """지원 언어 목록 조회"""
        return [Language(**lang) for lang in settings.SUPPORTED_LANGUAGES]

    @staticmethod
    async def get_available_voices(language: str) -> List[Voice]:
        """특정 언어의 사용 가능한 음성 목록 조회"""
        voices = settings.AVAILABLE_VOICES.get(language, [])
        return [Voice(**voice) for voice in voices]