# 인증 서비스 로직
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import verify_password, get_password_hash, create_access_token
from app.schemas import LoginRequest, SignupRequest, AuthResponse, User as UserSchema
from app.config import get_settings

settings = get_settings()


class AuthService:
    """인증 관련 서비스"""

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """사용자 인증 (이메일과 비밀번호 확인)"""
        # 이메일로 사용자 조회
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # 비밀번호 검증
        if not verify_password(password, user.password_hash):
            return None
        
        return user

    @staticmethod
    async def login_user(db: AsyncSession, login_request: LoginRequest) -> AuthResponse:
        """사용자 로그인"""
        # 사용자 인증
        user = await AuthService.authenticate_user(
            db, login_request.email, login_request.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 비활성화된 사용자 체크
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="비활성화된 계정입니다.",
            )
        
        # 마지막 로그인 시간 업데이트
        user.last_login_at = datetime.now(timezone.utc)
        await db.commit()
        
        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": user.id})
        
        # 사용자 정보 스키마로 변환
        user_data = UserSchema(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 초 단위
            user=user_data
        )

    @staticmethod
    async def create_user(db: AsyncSession, signup_request: SignupRequest) -> AuthResponse:
        """새 사용자 생성"""
        # 이메일 중복 체크
        result = await db.execute(select(User).where(User.email == signup_request.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 이메일입니다."
            )
        
        # 사용자명 중복 체크
        result = await db.execute(select(User).where(User.username == signup_request.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용중인 사용자명입니다."
            )
        
        # 비밀번호 해싱
        hashed_password = get_password_hash(signup_request.password)
        
        # 새 사용자 생성
        new_user = User(
            email=signup_request.email,
            username=signup_request.username,
            full_name=signup_request.full_name,
            password_hash=hashed_password,
            is_active=True,
            is_verified=False,  # 이메일 인증 후 True로 변경
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": new_user.id})
        
        # 사용자 정보 스키마로 변환
        user_data = UserSchema(
            id=new_user.id,
            email=new_user.email,
            username=new_user.username,
            full_name=new_user.full_name,
            avatar_url=new_user.avatar_url,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at
        )
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_data
        )

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """ID로 사용자 조회"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_password(db: AsyncSession, user: User, new_password: str) -> bool:
        """사용자 비밀번호 업데이트"""
        try:
            user.password_hash = get_password_hash(new_password)
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False