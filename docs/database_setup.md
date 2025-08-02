# 데이터베이스 설정 가이드

OneVoice Backend에서 PostgreSQL과 Alembic을 설정하는 방법을 안내합니다.

## 📋 사전 요구사항

1. **PostgreSQL 설치** (버전 12 이상 권장)
2. **Python 가상환경** 활성화
3. **의존성 설치**: `pip install -r requirements.txt`

## 🔧 환경 설정

### 1. 환경변수 파일 생성

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 입력하세요:

```bash
# 기본 설정
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-super-secret-jwt-key-change-in-production

# 데이터베이스 설정 (필수)
DATABASE_URL=postgresql://postgres:password@localhost:5432/onevoice_db

# API 키들 (선택사항, 나중에 설정 가능)
OPENAI_API_KEY=your-openai-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
```

### 2. PostgreSQL 데이터베이스 생성

```bash
# PostgreSQL 서비스 시작 (macOS Homebrew)
brew services start postgresql

# 데이터베이스 생성
createdb onevoice_db

# 또는 PostgreSQL CLI에서
psql -c "CREATE DATABASE onevoice_db;"
```

## 🚀 설정 및 초기화

### 방법 1: 자동 설정 스크립트 실행

```bash
# 데이터베이스 설정 및 테스트
python scripts/db_setup.py

# 성공 시 서버 실행
python -m uvicorn app.main:app --reload
```

### 방법 2: 수동 설정

```bash
# 1. 가상환경에서 Alembic 설치 확인
pip install alembic

# 2. Alembic 초기 마이그레이션 생성
alembic -c db/alembic.ini revision --autogenerate -m "Initial tables"

# 3. 마이그레이션 적용
alembic -c db/alembic.ini upgrade head

# 4. 서버 실행
python -m uvicorn app.main:app --reload
```

## 📊 Alembic 마이그레이션 관리

### 새로운 마이그레이션 생성

```bash
# 편리한 스크립트 사용
python scripts/create_migration.py "Add new column to users"

# 또는 직접 Alembic 명령어 사용
alembic -c db/alembic.ini revision --autogenerate -m "Add new column to users"
alembic -c db/alembic.ini upgrade head
```

### 마이그레이션 히스토리 확인

```bash
alembic -c db/alembic.ini history
alembic -c db/alembic.ini current
```

### 마이그레이션 롤백

```bash
# 이전 버전으로 롤백
alembic -c db/alembic.ini downgrade -1

# 특정 버전으로 롤백
alembic -c db/alembic.ini downgrade <revision_id>
```

## 🔍 문제 해결

### 일반적인 오류들

1. **"alembic: command not found"**
   ```bash
   # 가상환경 활성화 확인
   pip install alembic
   ```

2. **데이터베이스 연결 오류**
   ```bash
   # PostgreSQL 서비스 상태 확인
   brew services list | grep postgresql
   
   # 연결 테스트
   psql postgresql://postgres:password@localhost:5432/onevoice_db -c "SELECT 1"
   ```

3. **권한 오류**
   ```bash
   # 스크립트 실행 권한 부여
   chmod +x scripts/*.py
   ```

### 로그 확인

```bash
# FastAPI 서버 로그에서 데이터베이스 연결 상태 확인
python -m uvicorn app.main:app --reload --log-level debug
```

## 📁 파일 구조

```
db/
├── __init__.py
├── alembic.ini           # Alembic 설정 파일
├── migration_env.py      # 마이그레이션 환경 설정
└── migrations/           # Alembic 마이그레이션 폴더
    ├── env.py
    ├── script.py.mako
    └── versions/         # 마이그레이션 파일들

app/
├── core/
│   ├── database.py      # 데이터베이스 연결 설정
│   └── __init__.py
├── models/              # SQLAlchemy 모델들
├── dependecies.py       # FastAPI 의존성 주입
└── config.py           # 애플리케이션 설정

scripts/
├── db_setup.py         # 데이터베이스 자동 설정
└── create_migration.py # 마이그레이션 생성 도구
```

## 🔗 관련 문서

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- [Alembic 문서](https://alembic.sqlalchemy.org/)
- [PostgreSQL 문서](https://www.postgresql.org/docs/)