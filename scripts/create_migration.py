#!/usr/bin/env python3
"""
Alembic 마이그레이션 생성 스크립트
"""
import subprocess
import sys
from pathlib import Path

def create_migration(message: str):
    """새로운 마이그레이션 파일 생성"""
    project_root = Path(__file__).parent.parent
    
    try:
        cmd = f"cd {project_root} && alembic -c db/alembic.ini revision --autogenerate -m \"{message}\""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ 마이그레이션 '{message}' 생성 완료")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ 마이그레이션 생성 실패")
            if result.stderr:
                print(result.stderr)
            return False
        return True
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def upgrade_database():
    """데이터베이스 업그레이드"""
    project_root = Path(__file__).parent.parent
    
    try:
        cmd = f"cd {project_root} && alembic -c db/alembic.ini upgrade head"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 데이터베이스 업그레이드 완료")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ 데이터베이스 업그레이드 실패")
            if result.stderr:
                print(result.stderr)
            return False
        return True
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python scripts/create_migration.py <마이그레이션_메시지>")
        print("예시: python scripts/create_migration.py 'initial tables'")
        sys.exit(1)
    
    message = sys.argv[1]
    
    print(f"🔄 마이그레이션 생성: {message}")
    if create_migration(message):
        print("\n🔄 데이터베이스 업그레이드 중...")
        upgrade_database()