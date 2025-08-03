# 사용자 관리 서비스 로직
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import calendar

from fastapi import HTTPException, status, UploadFile
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, Subscription
from app.models.billing import CreditUsage, BillingHistory
from app.models.video import Video
from app.models.job import Job
from app.core.security import verify_password, get_password_hash
from app.schemas import (
    User as UserSchema,
    UserProfileUpdateRequest,
    PasswordUpdateRequest,
    DeleteAccountRequest,
    AvatarUploadResponse,
    UserActivityResponse,
    ActivityItem,
    DashboardStatsResponse,
    CreditsUsageResponse,
    NotificationPreferencesResponse,
    Subscription as SubscriptionSchema,
    ForgotPasswordResponse
)
from app.services.storage_service import storage_service


class UserService:
    """사용자 관리 관련 서비스"""

    @staticmethod
    async def get_user_profile(user: User) -> UserSchema:
        """사용자 프로필 정보 조회"""
        return UserSchema(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    @staticmethod
    async def update_user_profile(
        db: AsyncSession, 
        user: User, 
        request: UserProfileUpdateRequest
    ) -> UserSchema:
        """사용자 프로필 정보 업데이트"""
        # 이메일 중복 체크 (본인 제외)
        if request.email and request.email != user.email:
            result = await db.execute(
                select(User).where(
                    and_(User.email == request.email, User.id != user.id)
                )
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 사용중인 이메일입니다."
                )

        # 사용자명 중복 체크 (본인 제외)
        if request.username and request.username != user.username:
            result = await db.execute(
                select(User).where(
                    and_(User.username == request.username, User.id != user.id)
                )
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 사용중인 사용자명입니다."
                )

        # 프로필 정보 업데이트
        if request.username is not None:
            user.username = request.username
        if request.full_name is not None:
            user.full_name = request.full_name
        if request.email is not None:
            user.email = request.email

        user.updated_at = datetime.now(timezone.utc)
        
        try:
            await db.commit()
            await db.refresh(user)
            return await UserService.get_user_profile(user)
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="프로필 업데이트 중 오류가 발생했습니다."
            )

    @staticmethod
    async def change_password(
        db: AsyncSession, 
        user: User, 
        request: PasswordUpdateRequest
    ) -> ForgotPasswordResponse:
        """사용자 비밀번호 변경"""
        # 현재 비밀번호 확인
        if not verify_password(request.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="현재 비밀번호가 올바르지 않습니다."
            )

        # 새 비밀번호 해싱 및 업데이트
        user.password_hash = get_password_hash(request.new_password)
        user.updated_at = datetime.now(timezone.utc)

        try:
            await db.commit()
            return ForgotPasswordResponse(message="비밀번호가 성공적으로 변경되었습니다.")
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="비밀번호 변경 중 오류가 발생했습니다."
            )

    @staticmethod
    async def upload_avatar(
        db: AsyncSession, 
        user: User, 
        avatar_file: UploadFile
    ) -> AvatarUploadResponse:
        """사용자 아바타 업로드"""
        # 파일 타입 검증
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if not await storage_service.validate_file_type(avatar_file, allowed_types):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="지원되지 않는 이미지 형식입니다. JPEG, PNG, GIF, WEBP만 지원됩니다."
            )

        try:
            # 기존 아바타 삭제
            if user.avatar_url:
                # URL에서 파일 키 추출
                old_key = user.avatar_url.split('/')[-1] if '/' in user.avatar_url else None
                if old_key:
                    old_file_key = f"avatars/{user.id}/{old_key}"
                    await storage_service.delete_file(old_file_key)

            # 새 아바타 업로드
            file_key = storage_service.generate_file_key(
                user_id=user.id,
                file_type="avatars", 
                filename=avatar_file.filename
            )
            
            avatar_url = await storage_service.upload_file(
                file=avatar_file,
                file_key=file_key
            )
            
            user.avatar_url = avatar_url
            user.updated_at = datetime.now(timezone.utc)

            await db.commit()
            return AvatarUploadResponse(avatar_url=avatar_url)
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="아바타 업로드 중 오류가 발생했습니다."
            )

    @staticmethod
    async def delete_avatar(
        db: AsyncSession, 
        user: User
    ) -> ForgotPasswordResponse:
        """사용자 아바타 삭제"""
        try:
            # S3에서 아바타 파일 삭제
            if user.avatar_url:
                # URL에서 파일 키 추출 (더 정확한 방법)
                if user.avatar_url.startswith("http"):
                    # URL에서 파일 키 추출
                    parts = user.avatar_url.split('/')
                    if len(parts) >= 3:
                        file_key = '/'.join(parts[-3:])  # avatars/user_id/filename
                        await storage_service.delete_file(file_key)
                else:
                    # 상대 경로인 경우
                    await storage_service.delete_file(user.avatar_url)

            user.avatar_url = None
            user.updated_at = datetime.now(timezone.utc)

            await db.commit()
            return ForgotPasswordResponse(message="아바타가 성공적으로 삭제되었습니다.")
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="아바타 삭제 중 오류가 발생했습니다."
            )

    @staticmethod
    async def get_user_activity(
        db: AsyncSession, 
        user: User, 
        page: int = 1, 
        per_page: int = 20
    ) -> UserActivityResponse:
        """사용자 활동 내역 조회"""
        offset = (page - 1) * per_page
        
        # 비디오 관련 활동 조회
        video_activities = await db.execute(
            select(Video.id, Video.title, Video.created_at, Video.status)
            .where(Video.user_id == user.id)
            .order_by(Video.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        
        activities = []
        for video in video_activities.fetchall():
            activities.append(ActivityItem(
                id=video.id,
                action="video_created" if video.status == "pending" else f"video_{video.status}",
                description=f"비디오 '{video.title}' {video.status}",
                timestamp=video.created_at
            ))

        # 전체 활동 수 조회
        total_count = await db.execute(
            select(func.count(Video.id)).where(Video.user_id == user.id)
        )
        total = total_count.scalar() or 0

        pagination = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }

        return UserActivityResponse(
            activities=activities,
            pagination=pagination
        )

    @staticmethod
    async def get_dashboard_stats(
        db: AsyncSession, 
        user: User
    ) -> DashboardStatsResponse:
        """대시보드 통계 정보 조회"""
        # 비디오 통계
        video_stats = await db.execute(
            select(
                func.count(Video.id).label('total'),
                func.count(Video.id).filter(Video.status == 'completed').label('completed'),
                func.count(Video.id).filter(Video.status.in_(['processing', 'pending'])).label('processing'),
                func.sum(Video.duration).label('total_duration')
            ).where(Video.user_id == user.id)
        )
        stats = video_stats.fetchone()

        # 이번 달 크레딧 사용량
        current_month = datetime.now(timezone.utc).strftime('%Y-%m')
        credit_usage = await db.execute(
            select(func.sum(CreditUsage.credits_used))
            .where(
                and_(
                    CreditUsage.user_id == user.id,
                    CreditUsage.usage_month == current_month
                )
            )
        )
        credits_used_this_month = credit_usage.scalar() or 0

        return DashboardStatsResponse(
            total_videos=stats.total or 0,
            completed_videos=stats.completed or 0,
            processing_videos=stats.processing or 0,
            total_duration=stats.total_duration or 0,
            credits_used_this_month=credits_used_this_month
        )

    @staticmethod
    async def get_credits_usage(
        db: AsyncSession, 
        user: User
    ) -> CreditsUsageResponse:
        """크레딧 사용량 조회"""
        # 활성 구독 조회
        result = await db.execute(
            select(Subscription)
            .where(
                and_(
                    Subscription.user_id == user.id,
                    Subscription.status == 'active'
                )
            )
            .order_by(Subscription.created_at.desc())
            .limit(1)
        )
        subscription = result.scalar_one_or_none()

        if not subscription:
            return CreditsUsageResponse(
                total_credits=0,
                used_credits=0,
                remaining_credits=0,
                current_period_start=None,
                current_period_end=None
            )

        return CreditsUsageResponse(
            total_credits=subscription.credits_included,
            used_credits=subscription.credits_used,
            remaining_credits=subscription.credits_remaining,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end
        )

    @staticmethod
    async def get_notification_preferences(user: User) -> NotificationPreferencesResponse:
        """알림 설정 조회"""
        return NotificationPreferencesResponse(
            email_notifications=user.email_notifications,
            processing_complete=user.processing_complete,
            billing_updates=user.billing_updates,
            marketing_emails=user.marketing_emails
        )

    @staticmethod
    async def update_notification_preferences(
        db: AsyncSession,
        user: User,
        preferences: NotificationPreferencesResponse
    ) -> ForgotPasswordResponse:
        """알림 설정 업데이트"""
        if preferences.email_notifications is not None:
            user.email_notifications = preferences.email_notifications
        if preferences.processing_complete is not None:
            user.processing_complete = preferences.processing_complete
        if preferences.billing_updates is not None:
            user.billing_updates = preferences.billing_updates
        if preferences.marketing_emails is not None:
            user.marketing_emails = preferences.marketing_emails

        user.updated_at = datetime.now(timezone.utc)

        try:
            await db.commit()
            return ForgotPasswordResponse(message="알림 설정이 성공적으로 업데이트되었습니다.")
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="알림 설정 업데이트 중 오류가 발생했습니다."
            )

    @staticmethod
    async def get_user_subscription(
        db: AsyncSession, 
        user: User
    ) -> SubscriptionSchema:
        """사용자 구독 정보 조회"""
        result = await db.execute(
            select(Subscription)
            .where(Subscription.user_id == user.id)
            .order_by(Subscription.created_at.desc())
            .limit(1)
        )
        subscription = result.scalar_one_or_none()

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="구독 정보를 찾을 수 없습니다."
            )

        return SubscriptionSchema(
            id=subscription.id,
            plan_id=subscription.plan_id,
            status=subscription.status,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end,
            cancel_at_period_end=subscription.cancel_at_period_end
        )

    @staticmethod
    async def delete_user_account(
        db: AsyncSession,
        user: User,
        request: DeleteAccountRequest
    ) -> ForgotPasswordResponse:
        """사용자 계정 삭제"""
        # 비밀번호 확인
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호가 올바르지 않습니다."
            )

        try:
            # 사용자 계정 비활성화 (완전 삭제 대신)
            user.is_active = False
            user.email = f"deleted_{user.id}@deleted.com"  # 이메일 무효화
            user.username = f"deleted_{user.id}"  # 사용자명 무효화
            user.updated_at = datetime.now(timezone.utc)

            await db.commit()
            return ForgotPasswordResponse(message="계정이 성공적으로 삭제되었습니다.")
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="계정 삭제 중 오류가 발생했습니다."
            )