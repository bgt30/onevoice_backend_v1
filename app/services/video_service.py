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
from app.models.job import Job
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
from app.services.dubbing_service import DubbingService

settings = get_settings()


class VideoService:
    """비디오 관리 관련 서비스"""

    # 내부 공용 헬퍼: 최신 MediaFile 조회 (file_type, language 기준)
    @staticmethod
    async def _get_latest_media_file(
        db: AsyncSession,
        video_id: str,
        file_type: str,
        language: Optional[str] = None,
        only_active: bool = True,
    ) -> Optional[MediaFile]:
        try:
            query = select(MediaFile).where(MediaFile.video_id == video_id)
            if file_type:
                query = query.where(MediaFile.file_type == file_type)
            if only_active:
                query = query.where(MediaFile.is_active == True)
            if language is not None:
                # 언어 컬럼이 존재하는 경우에만 사용 (모델에 정의되어 있음)
                query = query.where(MediaFile.language_code == language)
            query = query.order_by(desc(MediaFile.created_at)).limit(1)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception:
            return None

    @staticmethod
    async def _get_original_media_file(db: AsyncSession, video_id: str) -> Optional[MediaFile]:
        return await VideoService._get_latest_media_file(db, video_id, file_type="original")

    @staticmethod
    async def _get_thumbnail_media_file(db: AsyncSession, video_id: str) -> Optional[MediaFile]:
        return await VideoService._get_latest_media_file(db, video_id, file_type="thumbnail")

    # --------------------------------

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

            # MediaFile에서 원본/썸네일 조회 (헬퍼 사용)
            original_mf = await VideoService._get_original_media_file(db, video.id)
            thumbnail_mf = await VideoService._get_thumbnail_media_file(db, video.id)

            video_list.append(VideoSchema(
                id=video.id,
                title=video.title,
                description=video.description,
                duration=(original_mf.duration if original_mf else None),
                original_language=video.original_language,
                target_languages=target_languages,
                status=video.status,
                thumbnail_url=((thumbnail_mf.public_url or thumbnail_mf.signed_url) if thumbnail_mf else None),
                video_url=((original_mf.public_url or original_mf.signed_url) if original_mf else None),
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
            duration=None,
            original_language=video.original_language,
            target_languages=[],
            status=video.status,
            thumbnail_url=None,
            video_url=None,
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

        # MediaFile에서 원본/썸네일 조회 (헬퍼 사용)
        original_mf = await VideoService._get_original_media_file(db, video.id)
        thumbnail_mf = await VideoService._get_thumbnail_media_file(db, video.id)

        return VideoSchema(
            id=video.id,
            title=video.title,
            description=video.description,
            duration=(original_mf.duration if original_mf else None),
            original_language=video.original_language,
            target_languages=target_languages,
            status=video.status,
            thumbnail_url=((thumbnail_mf.public_url or thumbnail_mf.signed_url) if thumbnail_mf else None),
            video_url=((original_mf.public_url or original_mf.signed_url) if original_mf else None),
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
            # 관련 MediaFile들 S3 객체 삭제
            mf_result = await db.execute(select(MediaFile).where(MediaFile.video_id == video.id))
            media_files = mf_result.scalars().all()
            for mf in media_files:
                if mf.s3_key:
                    try:
                        await storage_service.delete_file(mf.s3_key)
                    except Exception:
                        pass

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
            
            # 임시 비디오 레코드 및 원본 MediaFile 생성
            video = Video(
                id=video_id,
                user_id=user.id,
                title=request.filename,
                status="pending"
            )
            db.add(video)
            await db.flush()

            original_mf = MediaFile(
                video_id=video_id,
                filename=request.filename,
                file_type="original",
                file_format=(request.content_type.split('/')[-1] if '/' in request.content_type else 'bin'),
                file_size=None,
                file_path=file_key,
                s3_bucket=settings.S3_BUCKET_NAME,
                s3_key=file_key,
                public_url=None,
                is_active=True,
            )
            db.add(original_mf)
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
        language: Optional[str] = None,
        file_type: Optional[str] = None,
    ) -> DownloadResponse:
        """비디오(원본 또는 더빙 산출물) 다운로드 URL 생성

        file_type로 더빙 파이프라인 산출물을 선택할 수 있습니다.
        지원 값:
        - 'dubbed_video' -> output_dub.mp4
        - 'subtitle_video' -> output_sub.mp4
        - 'dub_subtitles' -> dub.srt
        - 'translation_subtitles' -> trans.srt
        - 'source_subtitles' -> src.srt
        """
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

        # 원본 파일은 처리 전/후 모두 다운로드 허용, 더빙 산출물은 완료된 더빙 Job 기준으로 제공

        try:
            # 파일 타입 매핑 (더빙 파이프라인 산출물)
            type_to_filename = {
                "dubbed_video": "output_dub.mp4",
                "subtitle_video": "output_sub.mp4",
                "dub_subtitles": "dub.srt",
                "translation_subtitles": "trans.srt",
                "source_subtitles": "src.srt",
            }

            # 파일 타입이 지정되지 않으면 기본은 더빙본(mp4)
            effective_type = file_type or "dubbed_video"

            # 원본 파일 요청 처리
            if effective_type == "original":
                original_mf = await VideoService._get_original_media_file(db, video_id)
                if not original_mf or not original_mf.s3_key:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="원본 파일이 존재하지 않습니다."
                    )
                ext = original_mf.file_format or 'mp4'
                download_url = await storage_service.create_presigned_download_url(
                    file_key=original_mf.s3_key,
                    expires_in=3600,
                    filename=f"{video.title}.{ext}"
                )
                expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
                return DownloadResponse(download_url=download_url, expires_at=expires_at)

            # 더빙 산출물 요청 유효성 검증
            if effective_type not in type_to_filename:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="지원되지 않는 파일 유형입니다. (dubbed_video | subtitle_video | dub_subtitles | translation_subtitles | source_subtitles | original)"
                )

            # 1차: MediaFile 테이블에서 조회 (표준)
            from sqlalchemy import select as _select
            from app.models.video import MediaFile as _MediaFile
            mf_query = _select(_MediaFile).where(
                and_(
                    _MediaFile.video_id == video_id,
                    _MediaFile.file_type == effective_type,
                    _MediaFile.is_active == True,
                )
            )
            if language:
                mf_query = mf_query.where(_MediaFile.language_code == language)
            mf_query = mf_query.order_by(desc(_MediaFile.created_at)).limit(1)

            mf_result = await db.execute(mf_query)
            media_file = mf_result.scalar_one_or_none()

            if media_file:
                file_key = media_file.s3_key or media_file.file_path
                if not file_key:
                    raise HTTPException(status_code=404, detail="요청한 파일 키를 찾을 수 없습니다.")
                # 다운로드 파일명 구성
                def build_download_filename(base_title: str, lang: Optional[str], typ: str) -> str:
                    suffix_map = {
                        "dubbed_video": ("dub", "mp4"),
                        "subtitle_video": ("subtitled", "mp4"),
                        "dub_subtitles": ("dub", "srt"),
                        "translation_subtitles": ("trans", "srt"),
                        "source_subtitles": ("src", "srt"),
                    }
                    suffix, ext = suffix_map[typ]
                    if lang:
                        return f"{base_title}.{lang}.{suffix}.{ext}"
                    return f"{base_title}.{suffix}.{ext}"

                download_filename = build_download_filename(video.title or "video", language, effective_type)
                download_url = await storage_service.create_presigned_download_url(
                    file_key=file_key,
                    expires_in=3600,
                    filename=download_filename,
                )
                expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
                return DownloadResponse(download_url=download_url, expires_at=expires_at)

            # MediaFile에서 찾지 못하면 존재하지 않는 것으로 간주
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="요청한 파일을 찾을 수 없습니다. (media_files에 결과가 없습니다)"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="다운로드 URL 생성 중 오류가 발생했습니다."
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

            # 원본 MediaFile 기준으로 복사
            orig_mf = await VideoService._get_original_media_file(db, original_video.id)
            if orig_mf and orig_mf.s3_key:
                original_filename = orig_mf.s3_key.split('/')[-1]
                new_file_key = storage_service.generate_file_key(
                    user_id=user.id,
                    file_type="videos",
                    filename=original_filename,
                    subfolder="original"
                )
                if await storage_service.copy_file(orig_mf.s3_key, new_file_key):
                    new_video_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{new_file_key}"

            # 썸네일도 복사 (있는 경우)
            orig_thumb = await VideoService._get_thumbnail_media_file(db, original_video.id)
            if orig_thumb and orig_thumb.s3_key:
                new_thumbnail_key = storage_service.generate_thumbnail_key(
                    user_id=user.id,
                    video_id=str(uuid4())
                )
                if await storage_service.copy_file(orig_thumb.s3_key, new_thumbnail_key):
                    new_thumbnail_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{new_thumbnail_key}"

            # 새 비디오 생성
            new_video = Video(
                user_id=user.id,
                title=f"{original_video.title} (복사본)",
                description=original_video.description,
                original_language=original_video.original_language,
                status="uploaded",
            )

            db.add(new_video)
            await db.flush()

            # 새 원본 MediaFile 생성
            if new_file_key and orig_mf:
                new_orig_mf = MediaFile(
                    video_id=new_video.id,
                    filename=orig_mf.filename,
                    file_type="original",
                    file_format=orig_mf.file_format,
                    file_size=orig_mf.file_size,
                    duration=orig_mf.duration,
                    resolution=orig_mf.resolution,
                    fps=orig_mf.fps,
                    file_path=new_file_key,
                    s3_bucket=settings.S3_BUCKET_NAME,
                    s3_key=new_file_key,
                    public_url=new_video_url,
                    is_active=True,
                )
                db.add(new_orig_mf)

            # 새 썸네일 MediaFile 생성
            if new_thumbnail_url:
                new_thumb_mf = MediaFile(
                    video_id=new_video.id,
                    filename="thumbnail.jpg",
                    file_type="thumbnail",
                    file_format="jpg",
                    file_size=None,
                    file_path=new_thumbnail_url.split(f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/")[-1],
                    s3_bucket=settings.S3_BUCKET_NAME,
                    s3_key=new_thumbnail_url.split(f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/")[-1],
                    public_url=new_thumbnail_url,
                    is_active=True,
                )
                db.add(new_thumb_mf)

            await db.commit()
            await db.refresh(new_video)

            return VideoSchema(
                id=new_video.id,
                title=new_video.title,
                description=new_video.description,
                duration=(orig_mf.duration if orig_mf else None),
                original_language=new_video.original_language,
                target_languages=[],
                status=new_video.status,
                thumbnail_url=new_thumbnail_url,
                video_url=new_video_url,
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
            # 기존 썸네일 MediaFile 삭제 (헬퍼 사용)
            existing_thumb = await VideoService._get_thumbnail_media_file(db, video.id)
            if existing_thumb and existing_thumb.s3_key:
                try:
                    await storage_service.delete_file(existing_thumb.s3_key)
                except Exception:
                    pass

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
                ## TODO: 실제 비디오에서 썸네일 추출 로직 구현
                thumbnail_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"

            # 썸네일 MediaFile 생성
            new_thumb_mf = MediaFile(
                video_id=video.id,
                filename="thumbnail.jpg",
                file_type="thumbnail",
                file_format="jpg",
                file_size=None,
                file_path=file_key,
                s3_bucket=settings.S3_BUCKET_NAME,
                s3_key=file_key,
                public_url=thumbnail_url,
                is_active=True,
            )
            db.add(new_thumb_mf)
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