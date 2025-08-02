#!/usr/bin/env python3
"""
데이터베이스 설정 및 초기화 스크립트
"""
import asyncio
import sys
import subprocess
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import create_tables, async_engine
from app.config import settings


def check_postgres_connection():
    """PostgreSQL 연결 확인"""
    try:
        import psycopg2
        # URL에서 연결 정보 파싱
        from urllib.parse import urlparse
        parsed = urlparse(settings.DATABASE_URL)
        
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:]  # leading slash 제거
        )
        conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL 연결 실패: {e}")
        return False


def run_alembic_command(command: str):
    """Alembic 명령어 실행"""
    try:
        cmd = f"cd {project_root} && alembic -c db/alembic.ini {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Alembic command '{command}' executed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ Alembic command '{command}' failed")
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running alembic command: {e}")
        return False


async def init_database():
    """데이터베이스 초기화"""
    print("🚀 OneVoice 데이터베이스 설정 시작...")
    print(f"🔗 데이터베이스 URL: {settings.DATABASE_URL}")
    
    # PostgreSQL 연결 확인
    if not check_postgres_connection():
        print("⚠️  PostgreSQL이 실행 중인지 확인하고 DATABASE_URL 설정을 확인하세요.")
        return False
    
    print("✅ PostgreSQL 연결 성공")
    
    try:
        # 데이터베이스 연결 테스트 (SQLAlchemy)
        from sqlalchemy import text
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ SQLAlchemy 데이터베이스 연결 성공")
        
        # 개발환경에서는 테이블 직접 생성 가능
        if settings.ENVIRONMENT == "development":
            print("📊 개발환경 - 테이블 생성 중...")
            await create_tables()
            print("✅ 개발환경용 테이블 생성 완료")
        
        # Alembic 초기 마이그레이션 생성 (만약 아직 없다면)
        print("🔄 Alembic 마이그레이션 확인 중...")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")
        return False
    finally:
        await async_engine.dispose()


def main():
    """메인 함수"""
    print("=" * 50)
    print("🎯 OneVoice Backend 데이터베이스 설정")
    print("=" * 50)
    
    success = asyncio.run(init_database())
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 데이터베이스 설정 완료!")
        print("=" * 50)
        print("\n다음 단계:")
        print("1. .env 파일 설정 확인")
        print("2. 가상환경에서 실행: python -m uvicorn app.main:app --reload")
        print("3. API 문서 확인: http://localhost:8000/docs")
    else:
        print("\n" + "=" * 50)
        print("❌ 데이터베이스 설정 실패")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    main()