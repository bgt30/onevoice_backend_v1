## OneVoice Backend V1 — 개발 환경 및 사용 기술 정리

### 개요
- **목표**: AI 기반 다국어 음성 더빙 백엔드 API
- **핵심**: FastAPI 기반 API, 비동기 작업 처리(SQS), AI 모듈(ASR/번역/TTS), 결제(Paddle), AWS 인프라(S3/RDS/EB)

---

## 개발 환경(Runtime & Tooling)
- **언어/런타임**: Python 3.11 (프로젝트 가상환경 `venv/`)
- **패키지 관리**: `pip` + `requirements.txt`
- **웹 프레임워크**: FastAPI 0.116.1, Starlette 0.47.3
- **ASGI 서버**: Uvicorn 0.35.0(개발), Gunicorn 23.0.0(운영)
- **비동기 런타임**: anyio, uvloop
- **설정/환경변수**: Pydantic 2.x, pydantic-settings 2.10.1, python-dotenv, environs
- **형상관리**: Git

---

## 데이터베이스 & ORM
- **RDBMS**: PostgreSQL (Amazon RDS)
- **ORM/드라이버**:
  - SQLAlchemy 2.0.43
  - asyncpg 0.30.0, psycopg2-binary 2.9.10
  - Alembic 1.16.5 (마이그레이션)
  - databases 0.9.0 (비동기 DB 접근)
- **연결 구성**: `app/core/database.py`에서 동기/비동기 엔진, 세션팩토리 관리

---

## 인증/보안
- **JWT/암호화**: python-jose 3.5.0, cryptography, fastapi-jwt-auth 0.5.0
- **비밀번호 해시**: passlib 1.7.4, bcrypt 4.3.0
- **CORS/GZip**: FastAPI 미들웨어 설정 (`app/main.py`)

---

## 스토리지/인프라 & 메시지 큐
- **AWS SDK**: boto3 1.40.19, botocore 1.40.19
- **객체 스토리지**: Amazon S3 (원본/결과 파일, Presigned URL)
- **메시지 큐**: Amazon SQS (비동기 작업 위임)
  - 송신: `app/queue/sqs_client.py`
  - 디스패처: `app/queue/dispatcher.py`
  - 컨슈머/실행기: `worker/runner.py`, `app/queue/consumer.py`
- **이메일/알림**: Amazon SES/SNS (문서/설정 기준)
- **로그/모니터링**: CloudWatch(문서 기준), 프로젝트 로깅 설정은 `monitoring/logging_config.py`

---

## 결제/빌링
- **결제 게이트웨이**: Paddle (`paddle-python-sdk==1.10.0`)
- **웹훅 처리**: `app/api/webhooks.py` (구독/결제 이벤트 반영)
- **비즈니스 로직**: `app/services/billing_service.py`

---

## AI/미디어 처리 모듈
- **ASR(음성 인식)**: OpenAI(Whisper-1), ElevenLabs, WhisperX, Demucs(보컬 분리)
- **번역/요약**: GPT 기반 프롬프트(`ai/prompts.py`, `ai/translate_lines.py`, 요약 모듈)
- **TTS(음성 합성)**: OpenAI, FishTTS, Custom, F5TTS (`ai/tts_backend/*`)
- **오디오/비디오 처리**: ffmpeg-python, pydub, librosa, soundfile, soxr, OpenCV
- **파이프라인 오케스트레이션**: `app/services/dubbing_service.py` 및 `worker/handlers.py`

---

## API 레이어 & 비즈니스 로직
- **FastAPI 앱**: `app/main.py` (CORS/GZip, 예외 처리, 라우터 등록, 라이프사이클)
- **라우터**: `app/api/auth.py`, `users.py`, `videos.py`, `billing.py`, `jobs.py`, `webhooks.py`
- **서비스 계층**: `app/services/*` (Auth/User/Video/Billing/Job/Dubbing/Notification/Storage)
- **모델/스키마**: `app/models/*` (SQLAlchemy), `app/schemas.py` (Pydantic)

---

## 로깅/모니터링
- **로깅**: 표준 logging + structlog(JSON 포맷 가능) — `monitoring/logging_config.py`
- **헬스체크**: `monitoring/health_check.py`, `healthcheck` 라이브러리

---

## 테스트/개발 도구
- **테스트**: pytest 8.4.1, pytest-asyncio 1.1.0, pytest-cov 6.2.1
- **HTTP 클라이언트**: httpx 0.28.1, aiohttp 3.12.x, requests 2.32.x
- **커버리지/품질**: coverage 7.10.5, rich(출력)
- **배포 CLI**: awsebcli 3.25 (Elastic Beanstalk)

---

## 로컬 개발 필수 요소
- **Python 3.11**, **FFmpeg**(시스템 설치 필요), **Git**, **AWS 자격증명**(개발용)
- 가상환경 활성화 후 작업:

```bash
source venv/bin/activate
```

자주 사용하는 명령어:

```bash
# 개발 서버
uvicorn app.main:app --reload

# 워커 실행(SQS 폴링)
python -m worker.runner

# DB 마이그레이션
alembic upgrade head

# 테스트
pytest -q
```

---

## 주요 라이브러리(일부 버전)
| 구분 | 패키지 | 버전 |
|---|---|---|
| 웹 | fastapi | 0.116.1 |
| 서버 | uvicorn | 0.35.0 |
| 서버(운영) | gunicorn | 23.0.0 |
| 설정 | pydantic | 2.11.7 |
| 설정 | pydantic-settings | 2.10.1 |
| ORM | SQLAlchemy | 2.0.43 |
| 마이그레이션 | alembic | 1.16.5 |
| DB 드라이버 | asyncpg | 0.30.0 |
| DB 드라이버 | psycopg2-binary | 2.9.10 |
| AWS | boto3 | 1.40.19 |
| 큐 | SQS(aws) | — |
| 결제 | paddle-python-sdk | 1.10.0 |
| 테스트 | pytest | 8.4.1 |
| HTTP | httpx | 0.28.1 |
| 오디오 | ffmpeg-python | 0.2.0 |
| 오디오 | pydub | 0.25.1 |
| 오디오 | librosa | 0.11.0 |
| 로깅 | structlog | 25.4.0 |

---

## 참고: 미사용/보류(요구사항에는 있으나 코드 경로상 비활성)
- Celery/Flower, Redis: requirements에는 포함되어 있으나 현재 SQS 기반 실행 경로에서 사용하지 않음(전환/보류 가능성)

---

## 배포/운영(요약)
- **플랫폼**: AWS Elastic Beanstalk(Web/Worker 분리 배포)
- **데이터베이스**: Amazon RDS(PostgreSQL)
- **스토리지**: Amazon S3
- **메시지 큐**: Amazon SQS
- **도메인/DNS**: Route 53
- **이메일/알림**: SES/SNS
- **로그/지표**: CloudWatch(로그/알람), 애플리케이션 로깅 구성 포함


