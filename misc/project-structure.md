onevoice_backend_v1/
├──  app/                              # FastAPI 애플리케이션 코어, CORS, 보안 헤더, 로깅
│   ├──  main.py                       # FastAPI 앱 진입점
│   ├──  config.py                     # 환경설정 관리
│   ├──  dependencies.py               # 의존성 주입 (인증, DB 등)   
│   ├──  schemas.py                    # Pydantic 모델 (요청/응답)
│   │
│   ├──  api/                      # API 라우터별 분리
│   │   ├──  __init__.py
│   │   ├──  auth.py                   # 인증 관련 엔드포인트 (5개)
│   │   ├──  users.py                  # 사용자 관리 (12개)
│   │   ├──  billing.py                # 결제/구독 (13개)
│   │   ├──  videos.py                 # 비디오 관리 (17개)
│   │   └──  jobs.py                   # 작업 상태/관리
│   │
│   ├──  models/                       # SQLAlchemy ORM 모델
│   │   ├──  __init__.py
│   │   ├──  base.py                   # 기본 모델 클래스
│   │   ├──  user.py                   # users, subscriptions
│   │   ├──  billing.py                # billing_history, credit_usage
│   │   ├──  video.py                  # videos, media_files
│   │   ├──  job.py                    # jobs, job_steps
│   │   └──  pending_user.py           # pending_user
│   │
│   ├──  services/                     # 비즈니스 로직 서비스
│   │   ├──  __init__.py
│   │   ├──  auth_service.py           # JWT, 인증 로직
│   │   ├──  user_service.py           # 사용자 관리 로직
│   │   ├──  billing_service.py        # Stripe 연동
│   │   ├──  video_service.py          # 비디오 CRUD
│   │   ├──  job_service.py            # 작업 상태 관리
│   │   ├──  notification_service.py   # 알림 발송
│   │   ├──  storage_service.py        # S3 파일 관리
│   │   └──  dubbing_service.py        # ai 더빙 이프라인 관리
│   │
│   └──  core/                         # 공통 유틸리티
│       ├──  __init__.py
│       ├──  security.py               # JWT, 암호화
│       ├──  database.py               # DB 연결/세션
│       └──  validators.py             # 입력 검증
│
├── ai/                               # 기존 AI 모듈 (변경 없음)
│   ├── __init__.py
│   ├── _1_find_video.py              # ... (기존 12단계 모듈들)
│   └── ... (기존 구조 유지)
│
├──  db/                               # 데이터베이스 관련
│   ├──  __init__.py
│   ├──  migrations/                   # Alembic 마이그레이션
│   │   ├──  versions/
│   │   └──  env.py
│   └──  alembic.ini
│
├──  monitoring/                       # 관찰 가능성
│   ├──  __init__.py
│   ├──  logging_config.py            # structlog 설정
│   ├──  metrics.py                   # 성능 지표 수집
│   └──  health_check.py              # 헬스체크 엔드포인트
│
├──  tests/                            # 테스트 코드
│   ├──  __init__.py
│   ├──  conftest.py                  # pytest 설정
│   ├──  unit/                        # 단위 테스트
│   ├──  integration/                 # 통합 테스트
│   └──  e2e/                         # E2E 테스트
│
├──  scripts/                          # 운영 스크립트
│   ├──  deploy.sh
│   ├──  migrate.py
│   └──  seed_data.py
│
├──  docs/                             # 문서화
│   ├──  api_docs.md
│   ├──  deployment.md
│   └──  troubleshooting.md
│
├──  misc/                             # 통합 문서 및 가이드
│   ├──  API.md                        # 전체 API 엔드포인트 목록
│   ├──  API_INTEGRATION_SUMMARY.md    # 프론트-백엔드 통합 요약
│   ├──  FASTAPI_BACKEND_REQUIREMENTS.md # FastAPI 백엔드 요구사항
│   ├──  VOICE_DUBBING_ARCHITECTURE_KO.md # 더빙 백엔드 아키텍처 한글 설계
│   └──  project-structure.md          # 프로젝트 구조
│
├──  requirements.txt                  # Python 의존성
├──  config.yaml                      # 환경 설정
├──  docker-compose.yml               # 로컬 개발 환경
├──  Dockerfile                       # 컨테이너 이미지
└──  README.md                        # 프로젝트 개요