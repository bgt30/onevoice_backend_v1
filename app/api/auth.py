# Authentication API endpoints
# Endpoints:
# - POST /api/auth/forgot-password
# - POST /api/auth/login
# - POST /api/auth/logout
# - POST /api/auth/reset-password
# - POST /api/auth/signup (임시 저장 + 이메일 발송)
# - POST /api/auth/verify-email (이메일 인증 + 계정 생성)
# - POST /api/auth/resend-verification (인증 이메일 재발송)

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependecies import get_db, get_current_active_user
from app.services.auth_service import AuthService
from app.services.notification_service import NotificationService
from app.core.security import create_reset_token, verify_reset_token
from app.models.user import User
from app.schemas import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    LoginRequest,
    SignupRequest,
    AuthResponse,
    Error
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/forgot-password",
    responses={
        200: {"model": ForgotPasswordResponse, "description": "Password reset email sent"},
        404: {"model": Error, "description": "User not found"},
    },
    summary="Request password reset",
    response_model_by_alias=True,
)
async def forgot_password(
    request: ForgotPasswordRequest = Body(..., description=""),
    db: AsyncSession = Depends(get_db)
) -> ForgotPasswordResponse:
    """Request password reset email"""
    # 사용자 존재 확인
    user = await AuthService.get_user_by_email(db, request.email)
    if not user:
        # 보안상 이메일이 없어도 성공 응답 (정보 노출 방지)
        return ForgotPasswordResponse(
            message="비밀번호 재설정 이메일이 발송되었습니다."
        )
    
    # 비밀번호 재설정 토큰 생성
    reset_token = create_reset_token(user.email)
    
    # 비밀번호 재설정 이메일 발송
    try:
        await NotificationService.send_password_reset_email(user, reset_token)
    except Exception as e:
        # 이메일 발송 실패해도 사용자에게는 성공 메시지 (보안상)
        print(f"비밀번호 재설정 이메일 발송 실패: {str(e)}")
    
    return ForgotPasswordResponse(
        message="비밀번호 재설정 이메일이 발송되었습니다."
    )


@router.post(
    "/login",
    responses={
        200: {"model": AuthResponse, "description": "Successful login"},
        401: {"model": Error, "description": "Invalid credentials"},
    },
    summary="User login",
    response_model_by_alias=True,
)
async def login(
    login_request: LoginRequest = Body(..., description=""),
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """User login with email and password"""
    return await AuthService.login_user(db, login_request)


@router.post(
    "/logout",
    responses={
        200: {"model": ForgotPasswordResponse, "description": "Logout successful"},
    },
    summary="User logout",
    response_model_by_alias=True,
)
async def logout(
    current_user: User = Depends(get_current_active_user)
) -> ForgotPasswordResponse:
    """User logout"""
    # JWT는 stateless이므로 클라이언트에서 토큰을 삭제하면 됨
    # refresh token이나 blacklist가 없으므로 단순히 성공 응답만 반환
    return ForgotPasswordResponse(
        message="성공적으로 로그아웃되었습니다."
    )


@router.post(
    "/reset-password",
    responses={
        200: {"model": ForgotPasswordResponse, "description": "Password reset successful"},
        400: {"model": Error, "description": "Invalid or expired token"},
    },
    summary="Reset password with token",
    response_model_by_alias=True,
)
async def reset_password(
    request: ResetPasswordRequest = Body(..., description=""),
    db: AsyncSession = Depends(get_db)
) -> ForgotPasswordResponse:
    """Reset password using reset token"""
    # 토큰 검증 및 이메일 추출
    email = verify_reset_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않거나 만료된 토큰입니다."
        )
    
    # 사용자 조회
    user = await AuthService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 비밀번호 업데이트
    success = await AuthService.update_password(db, user, request.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="비밀번호 변경에 실패했습니다."
        )
    
    return ForgotPasswordResponse(
        message="비밀번호가 성공적으로 변경되었습니다."
    )


@router.post(
    "/signup",
    responses={
        200: {"model": ForgotPasswordResponse, "description": "Registration request submitted, awaiting email verification"},
        400: {"model": Error, "description": "Invalid input data or user already exists"},
        500: {"model": Error, "description": "Email sending failed"},
    },
    summary="User registration - Email verification required",
    response_model_by_alias=True,
)
async def signup(
    signup_request: SignupRequest = Body(..., description=""),
    db: AsyncSession = Depends(get_db)
) -> ForgotPasswordResponse:
    """User registration - 이메일 인증 대기 상태로 임시 저장"""
    try:
        # 임시 사용자 생성 (실제 계정 생성 안함)
        pending_user, verification_token = await AuthService.create_pending_user(db, signup_request)
        
        # 회원가입 인증 이메일 발송
        try:
            # 임시 사용자 정보로 User 객체 생성 (이메일 발송용)
            temp_user = type('TempUser', (), {
                'email': pending_user.email,
                'username': pending_user.username,
                'full_name': pending_user.full_name
            })()
            
            await NotificationService.send_signup_verification_email(temp_user, verification_token)
            
        except Exception as e:
            # 이메일 발송 실패 시 임시 사용자도 삭제
            await db.delete(pending_user)
            await db.commit()
            print(f"회원가입 인증 이메일 발송 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="인증 이메일 발송에 실패했습니다. 다시 시도해주세요."
            )
        
        return ForgotPasswordResponse(
            message="회원가입 신청이 완료되었습니다. 이메일을 확인하여 계정을 활성화해주세요."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원가입 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.post(
    "/verify-email",
    responses={
        200: {"model": AuthResponse, "description": "Email verified successfully, account created"},
        400: {"model": Error, "description": "Invalid or expired verification token"},
        500: {"model": Error, "description": "Account creation failed"},
    },
    summary="Email verification and account creation",
    response_model_by_alias=True,
)
async def verify_email(
    token: str = Body(..., description="Email verification token"),
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """이메일 인증 완료 및 실제 계정 생성"""
    return await AuthService.verify_email_and_create_user(db, token)


@router.post(
    "/resend-verification",
    responses={
        200: {"model": ForgotPasswordResponse, "description": "Verification email resent"},
        404: {"model": Error, "description": "Registration request not found"},
        400: {"model": Error, "description": "Registration expired"},
    },
    summary="Resend email verification",
    response_model_by_alias=True,
)
async def resend_verification_email(
    email: str = Body(..., description="Email address"),
    db: AsyncSession = Depends(get_db)
) -> ForgotPasswordResponse:
    """이메일 인증 재발송"""
    try:
        pending_user, verification_token = await AuthService.resend_verification_email(db, email)
        
        # 이메일 발송
        temp_user = type('TempUser', (), {
            'email': pending_user.email,
            'username': pending_user.username,
            'full_name': pending_user.full_name
        })()
        
        await NotificationService.send_signup_verification_email(temp_user, verification_token)
        
        return ForgotPasswordResponse(
            message="인증 이메일이 재발송되었습니다. 이메일을 확인해주세요."
        )
        
    except Exception as e:
        print(f"인증 이메일 재발송 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="인증 이메일 재발송에 실패했습니다."
        ) 