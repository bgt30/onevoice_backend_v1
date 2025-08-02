# FastAPI 의존성 주입
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.config import settings
from app.core.database import get_db_session, get_async_db_session
from app.models.user import User

# 보안 스키마
security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """비동기 데이터베이스 세션 의존성"""
    async for session in get_async_db_session():
        yield session


def get_sync_db() -> Session:
    """동기 데이터베이스 세션 의존성"""
    return next(get_db_session())


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """현재 인증된 사용자 반환"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # JWT 토큰 디코딩
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 데이터베이스에서 사용자 조회
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """현재 활성화된 사용자 반환"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user


async def require_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """구독이 필요한 기능에 대한 의존성"""
    from sqlalchemy import select
    from app.models.user import Subscription
    
    # 최신 구독 정보 조회
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .where(Subscription.status == 'active')
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Active subscription required"
        )
    return current_user


async def check_credits(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    required_credits: int = 10
) -> User:
    """크레딧이 충분한지 확인하는 의존성"""
    from sqlalchemy import select
    from app.models.user import Subscription
    
    # 최신 구독 정보 조회
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .where(Subscription.status == 'active')
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="크레딧 사용을 위해서는 구독이 필요합니다."
        )
    
    # 남은 크레딧 확인
    remaining_credits = subscription.credits_remaining
    if remaining_credits < required_credits:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Required: {required_credits}, Available: {current_user.credits}"
        )
    
    return current_user