# 환경 변수 설정 가이드

## .env 파일 생성

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 복사하여 실제 값으로 변경하세요:

```bash
# OneVoice Backend API 환경 변수
# 아래 내용을 .env 파일에 복사하고 실제 값으로 변경하세요

# ========================================
# 필수 설정
# ========================================

# 애플리케이션 기본 설정
ENVIRONMENT=development
DEBUG=true
PROJECT_NAME="OneVoice Backend API"
SECRET_KEY=your-super-secret-jwt-key-change-in-production-MUST-CHANGE-THIS
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 서버 설정
HOST=0.0.0.0
PORT=8000

# 데이터베이스 설정 (필수)
DATABASE_URL=postgresql://postgres:password@localhost:5432/onevoice_db

# ========================================
# 외부 서비스 설정 (선택사항)
# ========================================

# AWS 설정 (S3 파일 저장용)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-west-2
S3_BUCKET_NAME=onevoice-videos

# Stripe 설정 (결제 처리용)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# ========================================
# AI 서비스 API 키 (선택사항)
# ========================================

# OpenAI (GPT 모델용)
OPENAI_API_KEY=your-openai-api-key

# ElevenLabs (TTS용)
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# Anthropic (Claude 모델용)
ANTHROPIC_API_KEY=your-anthropic-api-key

# ========================================
# 이메일 설정 (선택사항)
# ========================================

# SMTP settings removed; using Amazon SES only
EMAILS_FROM_EMAIL=noreply@onevoice.ai
EMAILS_FROM_NAME=OneVoice

# ========================================
# 모니터링 및 로깅 (선택사항)
# ========================================

# Sentry 오류 추적
SENTRY_DSN=your-sentry-dsn

# 로깅 레벨
LOG_LEVEL=INFO

# 메트릭 수집
ENABLE_METRICS=true

# ========================================
# 크레딧 시스템 설정
# ========================================

DEFAULT_FREE_CREDITS=100
CREDIT_COST_PER_MINUTE=10

# ========================================
# 파일 업로드 설정
# ========================================

# 최대 업로드 크기 (바이트, 기본값: 500MB)
MAX_UPLOAD_SIZE=524288000
```

## 빠른 시작 명령어

```bash
# 1. .env 파일 생성
cp docs/environment_setup.md .env
# 위 내용을 복사하여 .env 파일에 붙여넣기

# 2. PostgreSQL 데이터베이스 생성
createdb onevoice_db

# 3. 데이터베이스 설정 및 테스트
python scripts/db_setup.py

# 4. 서버 실행
python -m uvicorn app.main:app --reload
```