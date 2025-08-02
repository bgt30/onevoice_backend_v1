# API Schemas - Pydantic 모델 (요청/응답)
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr, field_validator
from typing_extensions import Annotated

# ===== 기본 모델 =====
class Error(BaseModel):
    """에러 응답 모델"""
    model_config = ConfigDict(from_attributes=True)
    
    error: Optional[StrictStr] = None
    message: Optional[StrictStr] = None
    details: Optional[Dict[str, Any]] = None

# ===== 인증 관련 스키마 =====
class LoginRequest(BaseModel):
    """로그인 요청"""
    email: StrictStr
    password: Annotated[str, Field(min_length=8, strict=True)]

class SignupRequest(BaseModel):
    """회원가입 요청"""
    email: StrictStr
    password: Annotated[str, Field(min_length=8, strict=True)]
    username: StrictStr
    full_name: Optional[StrictStr] = None

class ForgotPasswordRequest(BaseModel):
    """비밀번호 재설정 요청"""
    email: StrictStr

class ResetPasswordRequest(BaseModel):
    """비밀번호 재설정"""
    token: StrictStr
    new_password: Annotated[str, Field(min_length=8, strict=True)]

class ForgotPasswordResponse(BaseModel):
    """비밀번호 재설정 이메일 발송 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    message: Optional[StrictStr] = None

# ===== 사용자 관련 스키마 =====
class User(BaseModel):
    """사용자 정보"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[StrictStr] = None
    email: Optional[StrictStr] = None
    username: Optional[StrictStr] = None
    full_name: Optional[StrictStr] = None
    avatar_url: Optional[StrictStr] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class AuthResponse(BaseModel):
    """인증 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    access_token: Optional[StrictStr] = None
    token_type: Optional[StrictStr] = None
    expires_in: Optional[StrictInt] = None
    user: Optional[User] = None

class UserProfileUpdateRequest(BaseModel):
    """사용자 프로필 업데이트 요청"""
    username: Optional[StrictStr] = None
    full_name: Optional[StrictStr] = None
    email: Optional[StrictStr] = None

class PasswordUpdateRequest(BaseModel):
    """비밀번호 변경 요청"""
    current_password: StrictStr
    new_password: Annotated[str, Field(min_length=8, strict=True)]

class DeleteAccountRequest(BaseModel):
    """계정 삭제 요청"""
    password: StrictStr

class AvatarUploadResponse(BaseModel):
    """아바타 업로드 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    avatar_url: Optional[StrictStr] = None

# ===== 사용자 활동/통계 =====
class ActivityItem(BaseModel):
    """활동 항목"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[StrictStr] = None
    action: Optional[StrictStr] = None
    description: Optional[StrictStr] = None
    timestamp: Optional[datetime] = None

class UserActivityResponse(BaseModel):
    """사용자 활동 내역 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    activities: Optional[List[ActivityItem]] = None
    pagination: Optional[Dict[str, Any]] = None

class DashboardStatsResponse(BaseModel):
    """대시보드 통계 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    total_videos: Optional[StrictInt] = None
    completed_videos: Optional[StrictInt] = None
    processing_videos: Optional[StrictInt] = None
    total_duration: Optional[Union[StrictFloat, StrictInt]] = None
    credits_used_this_month: Optional[StrictInt] = None

class CreditsUsageResponse(BaseModel):
    """크레딧 사용량 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    total_credits: Optional[StrictInt] = None
    used_credits: Optional[StrictInt] = None
    remaining_credits: Optional[StrictInt] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None

# ===== 알림 설정 =====
class NotificationPreferencesResponse(BaseModel):
    """알림 설정 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    email_notifications: Optional[StrictBool] = None
    processing_complete: Optional[StrictBool] = None
    billing_updates: Optional[StrictBool] = None
    marketing_emails: Optional[StrictBool] = None

# ===== 결제/구독 관련 스키마 =====
class BillingPlan(BaseModel):
    """결제 플랜"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[StrictStr] = None
    name: Optional[StrictStr] = None
    price: Optional[Union[StrictFloat, StrictInt]] = None
    currency: Optional[StrictStr] = None
    billing_period: Optional[StrictStr] = None
    credits_included: Optional[StrictInt] = None
    features: Optional[List[StrictStr]] = None

    @field_validator('billing_period')
    def billing_period_validate_enum(cls, value):
        if value is None:
            return value
        if value not in ('monthly', 'yearly',):
            raise ValueError("must be one of enum values ('monthly', 'yearly')")
        return value

class Subscription(BaseModel):
    """구독 정보"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[StrictStr] = None
    plan_id: Optional[StrictStr] = None
    status: Optional[StrictStr] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: Optional[StrictBool] = None

    @field_validator('status')
    def status_validate_enum(cls, value):
        if value is None:
            return value
        if value not in ('active', 'cancelled', 'past_due', 'unpaid',):
            raise ValueError("must be one of enum values ('active', 'cancelled', 'past_due', 'unpaid')")
        return value

class SubscribeRequest(BaseModel):
    """구독 요청"""
    plan_id: StrictStr
    payment_method_id: StrictStr

class SubscriptionUpdateRequest(BaseModel):
    """구독 변경 요청"""
    plan_id: StrictStr

class PaymentMethodUpdateRequest(BaseModel):
    """결제 수단 변경 요청"""
    payment_method_id: StrictStr

class PaymentMethod(BaseModel):
    """결제 수단"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[StrictStr] = None
    type: Optional[StrictStr] = None
    last4: Optional[StrictStr] = None
    brand: Optional[StrictStr] = None
    is_default: Optional[StrictBool] = None

class SetupIntentResponse(BaseModel):
    """결제 설정 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    client_secret: Optional[StrictStr] = None

class Invoice(BaseModel):
    """청구서"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[StrictStr] = None
    amount: Optional[Union[StrictFloat, StrictInt]] = None
    currency: Optional[StrictStr] = None
    status: Optional[StrictStr] = None
    created_at: Optional[datetime] = None

class BillingHistoryResponse(BaseModel):
    """결제 내역 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    invoices: Optional[List[Invoice]] = None
    pagination: Optional[Dict[str, Any]] = None

class UpcomingInvoiceResponse(BaseModel):
    """다음 청구서 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    amount: Optional[Union[StrictFloat, StrictInt]] = None
    currency: Optional[StrictStr] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None

class UsageResponse(BaseModel):
    """사용량 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    current_period_usage: Optional[StrictInt] = None
    included_credits: Optional[StrictInt] = None
    overage_credits: Optional[StrictInt] = None
    overage_cost: Optional[Union[StrictFloat, StrictInt]] = None

# ===== 비디오 관련 스키마 =====
class Video(BaseModel):
    """비디오 정보"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[StrictStr] = None
    title: Optional[StrictStr] = None
    description: Optional[StrictStr] = None
    duration: Optional[Union[StrictFloat, StrictInt]] = None
    original_language: Optional[StrictStr] = None
    target_languages: Optional[List[StrictStr]] = None
    status: Optional[StrictStr] = None
    thumbnail_url: Optional[StrictStr] = None
    video_url: Optional[StrictStr] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('status')
    def status_validate_enum(cls, value):
        if value is None:
            return value
        if value not in ('uploaded', 'processing', 'completed', 'failed',):
            raise ValueError("must be one of enum values ('uploaded', 'processing', 'completed', 'failed')")
        return value

class VideoCreateRequest(BaseModel):
    """비디오 생성 요청"""
    title: StrictStr
    description: Optional[StrictStr] = None
    original_language: Optional[StrictStr] = None

class VideoUpdateRequest(BaseModel):
    """비디오 업데이트 요청"""
    title: Optional[StrictStr] = None
    description: Optional[StrictStr] = None

class VideosResponse(BaseModel):
    """비디오 목록 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    videos: Optional[List[Video]] = None
    pagination: Optional[Dict[str, Any]] = None

class UploadUrlRequest(BaseModel):
    """업로드 URL 요청"""
    filename: StrictStr
    content_type: StrictStr

class UploadUrlResponse(BaseModel):
    """업로드 URL 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    upload_url: Optional[StrictStr] = None
    video_id: Optional[StrictStr] = None

class DownloadResponse(BaseModel):
    """다운로드 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    download_url: Optional[StrictStr] = None
    expires_at: Optional[datetime] = None

class ThumbnailUploadResponse(BaseModel):
    """썸네일 업로드 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    thumbnail_url: Optional[StrictStr] = None

# ===== 더빙 관련 스키마 =====
class DubRequest(BaseModel):
    """더빙 요청"""
    target_language: StrictStr
    voice_id: StrictStr
    preserve_background_music: Optional[StrictBool] = True

class DubResponse(BaseModel):
    """더빙 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    job_id: Optional[StrictStr] = None
    message: Optional[StrictStr] = None



# ===== 작업 관련 스키마 =====
class JobStatus(BaseModel):
    """작업 상태"""
    model_config = ConfigDict(from_attributes=True)
    
    job_id: Optional[StrictStr] = None
    status: Optional[StrictStr] = None
    progress: Optional[Union[Annotated[float, Field(le=100, strict=True, ge=0)], Annotated[int, Field(le=100, strict=True, ge=0)]]] = None
    estimated_completion: Optional[datetime] = None
    error_message: Optional[StrictStr] = None

    @field_validator('status')
    def status_validate_enum(cls, value):
        if value is None:
            return value
        if value not in ('pending', 'processing', 'completed', 'failed', 'cancelled',):
            raise ValueError("must be one of enum values ('pending', 'processing', 'completed', 'failed', 'cancelled')")
        return value

# ===== 언어/음성 관련 스키마 =====
class Language(BaseModel):
    """언어 정보"""
    model_config = ConfigDict(from_attributes=True)
    
    code: Optional[StrictStr] = None
    name: Optional[StrictStr] = None
    native_name: Optional[StrictStr] = None

class Voice(BaseModel):
    """음성 정보"""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[StrictStr] = None
    name: Optional[StrictStr] = None
    language: Optional[StrictStr] = None
    gender: Optional[StrictStr] = None
    style: Optional[StrictStr] = None
    preview_url: Optional[StrictStr] = None

    @field_validator('gender')
    def gender_validate_enum(cls, value):
        if value is None:
            return value
        if value not in ('male', 'female', 'neutral',):
            raise ValueError("must be one of enum values ('male', 'female', 'neutral')")
        return value
