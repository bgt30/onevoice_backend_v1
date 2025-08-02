# JWT 및 인증 관련 유틸리티 함수
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()

# 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """JWT 토큰 검증 및 페이로드 반환"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def decode_access_token(token: str) -> Optional[str]:
    """액세스 토큰에서 사용자 ID 추출"""
    payload = verify_token(token)
    if payload is None:
        return None
    
    user_id: str = payload.get("sub")
    return user_id


def create_reset_token(email: str) -> str:
    """비밀번호 재설정 토큰 생성 (짧은 만료 시간)"""
    expire = datetime.now(timezone.utc) + timedelta(hours=1)  # 1시간 후 만료
    to_encode = {
        "sub": email,
        "exp": expire,
        "type": "password_reset"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def verify_reset_token(token: str) -> Optional[str]:
    """비밀번호 재설정 토큰 검증 및 이메일 반환"""
    payload = verify_token(token)
    if payload is None:
        return None
    
    # 토큰 타입 확인
    if payload.get("type") != "password_reset":
        return None
    
    email: str = payload.get("sub")
    return email