# Authentication API endpoints
# Endpoints:
# - POST /api/auth/forgot-password
# - POST /api/auth/login
# - POST /api/auth/logout
# - POST /api/auth/reset-password
# - POST /api/auth/signup

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependecies import get_db, get_current_active_user
from app.services.auth import AuthService
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
    
    # TODO: 실제 이메일 발송 로직 구현
    # send_password_reset_email(user.email, reset_token)
    
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
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"model": AuthResponse, "description": "User created successfully"},
        400: {"model": Error, "description": "Invalid input data or user already exists"},
    },
    summary="User registration",
    response_model_by_alias=True,
)
async def signup(
    signup_request: SignupRequest = Body(..., description=""),
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """User registration"""
    return await AuthService.create_user(db, signup_request) 