# OneVoice Backend V1

AI 기반 음성 더빙 서비스 백엔드 API

## 🚀 빠른 시작

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 설정
```bash
# .env 파일 생성 (docs/environment_setup.md 참고)
cp docs/environment_setup.md .env
# 위 파일의 내용을 복사하여 .env 파일에 붙여넣고 실제 값으로 변경

# PostgreSQL 데이터베이스 생성
createdb onevoice_db
```

### 3. 데이터베이스 설정
```bash
# 자동 설정 스크립트 실행
python scripts/db_setup.py

# 또는 수동 설정
alembic -c db/alembic.ini revision --autogenerate -m "Initial tables"
alembic -c db/alembic.ini upgrade head
```

### 4. 서버 실행
```bash
python -m uvicorn app.main:app --reload
```

서버가 실행되면 다음 URL에서 확인할 수 있습니다:
- API 문서: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 📚 문서

- [데이터베이스 설정 가이드](docs/database_setup.md)
- [환경 변수 설정](docs/environment_setup.md)
- [API 문서](docs/api_docs.md)

## 🛠 개발 도구

### 마이그레이션 관리
```bash
# 새로운 마이그레이션 생성
python scripts/create_migration.py "Add new feature"

# 마이그레이션 적용
alembic -c db/alembic.ini upgrade head

# 마이그레이션 히스토리 확인
alembic -c db/alembic.ini history
```

## 📁 프로젝트 구조

```
onevoice_backend_v1/
├── app/                    # FastAPI 애플리케이션
│   ├── core/              # 핵심 설정 (데이터베이스, 보안)
│   ├── models/            # SQLAlchemy ORM 모델
│   ├── api/               # API 라우터들
│   ├── schemas.py         # Pydantic 스키마
│   ├── config.py          # 설정 관리
│   └── main.py           # FastAPI 앱 진입점
├── db/                    # 데이터베이스 관련
│   ├── alembic.ini       # Alembic 설정
│   └── migrations/       # 마이그레이션 파일들
├── scripts/              # 유틸리티 스크립트
├── monitoring/           # 모니터링 및 로깅
├── ai/                   # AI/ML 모듈
└── docs/                 # 문서
```

## 🔧 기술 스택

- **백엔드**: FastAPI, SQLAlchemy, Alembic
- **데이터베이스**: PostgreSQL
- **인증**: JWT, OAuth2
- **파일 저장**: AWS S3
- **결제**: Stripe
- **AI 서비스**: OpenAI, ElevenLabs
- **모니터링**: Sentry, 커스텀 메트릭

## 🤝 기여

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이센스

This project is licensed under the MIT License.
