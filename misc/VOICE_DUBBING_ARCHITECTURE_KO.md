# 영상 더빙(Voice-Dubbing) 백엔드 — 심층 설계 청사진

아래는 영상 더빙 서비스 백엔드의 MMP 버전입니다. 최소한의 기능만 구현할 계획이야. 시간과 비용이 많이 드는 툴들을 최대한 사용하지 않을거야. 그러니 여기에 명시되어있는 툴만 사용해.

⸻

## 1. 시스템 아키텍처 & 워크플로우 설계

### 핵심 아키텍처 결정사항

| 계층 | 기술 선택 |
|---|---|
| **프론트엔드** | React + Next.js + TypeScript |
| **API 게이트웨이** | FastAPI + uvicorn |
| **데이터베이스** | PostgreSQL |
| **파일 저장소** | S3 |

### 보안 & 인증 플로우

1. **인증 흐름**
   ```
   Login → JWT Token
   ```

2. **파일 접근 제어**
   ```python
   S3 Path: /{user_id}/{video_id}/{file_type}/
   Presigned URL: 1시간 만료 + IP 제한
   ```

### 확장성 & 성능 고려사항

| 구성요소 | 확장 전략 | 모니터링 지표 |
|---|---|---|
| **API 서버** | 수평 확장 + 로드밸런서 | RPS, 응답시간, 에러율 |
| **데이터베이스** | 읽기 복제본 + 샤딩 | 연결 수, 쿼리 시간 |

### 데이터 계약 & API 스키마

1. **Pydantic 모델 공유**
   ```python
   # shared-contracts/models.py
   class VideoUploadRequest(BaseModel):
       title: str
       language: LanguageCode
       settings: DubbingSettings
   ```

2. **OpenAPI 스키마 관리**
   - 자동 생성: FastAPI → OpenAPI 3.0
   - 코드 생성: OpenAPI → TypeScript SDK
   - 버전 관리: 스키마 diff + 호환성 체크

⸻

## 2. API 설계 & 문서화

### 핵심 설계 원칙

1. **REST + 비동기 패턴**
   - 모든 라우트에 `/api/` 접두사
   - 긴 작업은 `job_id` 반환 → 폴링으로 상태 추적
   - Idempotency-Key 헤더로 중복 요청 방지

2. **표준화된 응답 형식**
   ```json
   {
     "success": true,
     "data": {...},
     "message": "Operation completed",
     "timestamp": "2024-01-15T10:30:00Z"
   }
   ```

### 도메인별 API 그룹

misc/API.md 파일 참고

### 파일 업로드 전략

```python
# 1단계: 업로드 URL 요청
POST /api/v1/videos/upload-url
→ { "upload_url": "https://...", "video_id": "123" }

# 2단계: 직접 S3 업로드 (클라이언트)
PUT {upload_url} with multipart data

# 3단계: 더빙 작업 시작
POST /api/v1/videos/123/dub
→ { "job_id": "job_456" }
```

### 에러 처리 & 상태 코드

| 상황 | HTTP 코드 | 응답 예시 |
|---|---|---|
| 성공 | 200/201 | `{"success": true, "data": {...}}` |
| 검증 실패 | 422 | `{"success": false, "errors": [...]}` |
| 인증 실패 | 401 | `{"success": false, "message": "Invalid token"}` |
| 권한 부족 | 403 | `{"success": false, "message": "Insufficient credits"}` |
| 리소스 없음 | 404 | `{"success": false, "message": "Video not found"}` |
| 중복 요청 | 409 | `{"success": false, "message": "Already processing"}` |
| 서버 오류 | 500 | `{"success": false, "message": "Internal error", "trace_id": "..."}` |

### 페이지네이션 & 필터링

```python
# 표준 페이지네이션
GET /api/v1/videos?page=1&perPage=20&sortBy=created_at&sortOrder=desc

# 응답 형식
{
  "data": [...],
  "pagination": {
    "page": 1,
    "perPage": 20,
    "total": 150,
    "totalPages": 8
  }
}
```

### OpenAPI & 코드 생성

1. **FastAPI 자동 문서화** → `/docs`, `/redoc`
2. **TypeScript SDK 생성** → `openapi-generator-cli`
3. **API 테스트 자동화** → Pydantic 모델 기반 검증
4. **버전 호환성** → OpenAPI 스키마 diff 체크

### 연결 고리
- `job_id`는 Jobs 테이블 FK → 워커가 상태 업데이트
- FastAPI의 의존성 주입으로 인증/권한 체크 자동화
- Pydantic 모델로 요청/응답 검증 및 직렬화

⸻

## 3. 데이터베이스 & 상태 모델

### 핵심 테이블 구조

| 테이블 | 핵심 컬럼 | 비고 |
|---|---|---|
| **users** | id, email, password_hash, avatar_url, stripe_customer_id, subscription_id, notification_preferences, last_activity_at | 사용자 기본 정보 & Stripe 연결 |
| **subscription_plans** | id, name, price, credits_per_month, max_video_duration, features | 구독 요금제 정의 |
| **subscriptions** | id, user_id, plan_id, status, current_period_start, current_period_end, stripe_subscription_id | 활성 구독 관리 |
| **videos** | id, user_id, title, src_url, duration, language_detected, file_size_bytes, checksum_sha256, status | 영상 메타데이터 (불변) |
| **jobs** | id, video_id, user_id, job_type, current_step, total_steps, status, progress%, settings, error_details, estimated_completion_at | 작업 상태 추적 |
| **job_steps** | id, job_id, step_name, status, input_data, output_data, processing_time_ms, worker_id | 단계별 세부 추적 |
| **media_files** | id, video_id, file_type, file_url, file_size_bytes, checksum_sha256, storage_provider, expires_at | 파일 관리 (원본/중간/결과) |
| **credit_usage** | id, user_id, video_id, credits_used, operation_type, created_at | 크레딧 사용량 추적 |

| **voice_options** | id, language_code, voice_name, voice_provider, sample_url | 음성 옵션 관리 |
| **user_notifications** | id, user_id, type, title, message, read_at, created_at | 알림 관리 |
| **billing_history** | id, user_id, amount, status, stripe_invoice_id, created_at | 결제 이력 |
| **worker_events** | job_id, timestamp, payload JSONB | Sentry 추적 & 메트릭용 |

### 주요 Enum 타입

```sql
-- 작업 상태
job_status: 'pending', 'processing', 'completed', 'failed', 'cancelled'
job_type: 'dubbing', 'translation', 'voice_preview'

-- 파일 타입
file_type: 'source', 'audio_extracted', 'dubbed_audio', 'final_video', 'subtitles'

-- 구독 상태
subscription_status: 'active', 'past_due', 'canceled', 'unpaid'
```

### 인덱스 전략
- `videos(user_id, created_at DESC)` - 사용자별 영상 목록
- `jobs(video_id, status)` - 영상별 작업 상태 조회
- `jobs(user_id, created_at DESC)` - 사용자 작업 이력
- `credit_usage(user_id, created_at)` - 크레딧 사용량 집계
- `media_files(video_id, file_type)` - 영상별 파일 조회

### DB 선택
- **PostgreSQL**
- **Alembic**

⸻

## 4. 인증·인가 & 쿼터

### JWT 토큰 관리 전략

| 토큰 타입 | 만료 시간 | 저장 위치 | 용도 |
|---|---|---|---|
| **Access Token** | 15분 | 메모리 (httpOnly 쿠키) | API 호출 인증 |

### 보안 & 인증 구현

```python
# JWT 토큰 검증
@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

# 권한 기반 접근 제어
@router.delete("/videos/{video_id}")
async def delete_video(
    video_id: int,
    current_user: User = Depends(require_scope("write:video"))
):
    # 본인 영상만 삭제 가능 로직
```

### 레이트 리미팅 & 보안

| 보호 대상 | 제한 방식 | 구현 |
|---|---|---|
| **로그인 시도** | IP당 5회/분 | `slowapi` |
| **API 호출** | 사용자당 100회/분 | slowapi |

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: UserCredentials):
    pass

@router.post("/videos")
@limiter.limit("10/minute")
async def create_video(
    request: Request,
    user: User = Depends(get_current_user)
):
    pass
```

### 세션 관리 & 보안 강화

1. **보안 헤더**
   ```python
   from fastapi.middleware.trustedhost import TrustedHostMiddleware
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*.onevoice.ai"])
   app.add_middleware(
       CORSMiddleware,
       allow_credentials=True,
       allow_methods=["GET", "POST", "PUT", "DELETE"],
       allow_headers=["*"],
   )
   ```

### 파일 접근 제어

```python
class S3AccessControl:
    def generate_presigned_url(
        self, 
        user_id: int, 
        video_id: int, 
        file_type: str,
        expires_in: int = 3600
    ) -> str:
        """사용자별 격리된 S3 경로"""
        
        # 경로 검증
        if not self.user_owns_video(user_id, video_id):
            raise HTTPException(403, "Access denied")
        
        object_key = f"{user_id}/{video_id}/{file_type}/file.mp4"
        
        return s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': object_key},
            ExpiresIn=expires_in
        )
```

### 연결 고리

- **JWT sub** ↔ **users.id** — DB 리소스 접근 제어
- **크레딧 사용량** ↔ **jobs 테이블** — 작업 완료 시점에 크레딧 차감

⸻

## 5. 미디어·AI 처리 파이프라인

### 단계별 처리 모듈 & FastAPI 통합

| 단계 | 모듈 | 주요 기능 | FastAPI 통합 방식 | 예상 처리 시간 |
|---|---|---|---|---|
| **1. 영상 입력** | `_1_find_video.py` | • 직접 업로드 처리<br/>• 영상 메타데이터 추출<br/>• 파일 형식 검증 | `@celery_app.task`로 래핑<br/>S3 업로드와 병렬 처리 | 10~30초 |
| **2. 음성 인식** | `_2_asr.py` | • Whisper/Assembly AI ASR<br/>• 다국어 음성 인식<br/>• 타임스탬프 동기화 | GPU 워커 전용 태스크<br/>배치 처리 최적화 | 1~5분 |
| **3-1. NLP 분할** | `_3_1_split_nlp.py` | • spaCy 기반 문장 분할<br/>• 언어학적 경계 인식 | CPU 집약적 태스크<br/>병렬 처리 가능 | 10~30초 |
| **3-2. 의미 분할** | `_3_2_split_meaning.py` | • 의미 단위 그룹핑<br/>• 문맥 보존 분할 | LLM API 호출<br/>레이트 리미팅 적용 | 30초~2분 |
| **4-1. 요약** | `_4_1_summarize.py` | • 내용 핵심 추출<br/>• 문맥 보존 요약 | LLM API 체인<br/>토큰 최적화 | 20~60초 |
| **4-2. 번역** | `_4_2_translate.py` | • 다국어 번역<br/>• 문맥 기반 번역 | 배치 번역 API<br/>캐시 활용 | 30초~2분 |
| **5. 자막 분할** | `_5_split_sub.py` | • 번역본 자막 분할<br/>• 타이밍 조정 | 빠른 CPU 태스크 | 5~15초 |
| **6. 자막 생성** | `_6_gen_sub.py` | • SRT/VTT 포맷 생성<br/>• 자막 스타일링 | 즉시 처리 가능 | 1~5초 |
| **7. 자막 합성** | `_7_sub_into_vid.py` | • 영상에 자막 오버레이<br/>• FFmpeg 처리 | FFmpeg 워커<br/>GPU 가속 활용 | 1~3분 |
| **8-1. 오디오 준비** | `_8_1_audio_task.py` | • 오디오 전처리<br/>• 품질 분석 | 오디오 처리 워커 | 30초~1분 |
| **8-2. 더빙 청크** | `_8_2_dub_chunks.py` | • 문장별 오디오 분할<br/>• 더빙 단위 생성 | 병렬 청크 처리 | 20~40초 |
| **9. 참조 오디오** | `_9_refer_audio.py` | • 원본 음성 특성 분석<br/>• 톤/스타일 추출 | AI 음성 분석<br/>GPU 리소스 필요 | 1~2분 |
| **10. TTS 생성** | `_10_gen_audio.py` | • 다양한 TTS 엔진 지원<br/>• 음성 클로닝 | TTS API 체인<br/>병렬 생성 | 2~10분 |
| **11. 오디오 병합** | `_11_merge_audio.py` | • 배경음과 더빙 믹싱<br/>• 볼륨 밸런싱 | FFmpeg 오디오 처리 | 30초~2분 |
| **12. 최종 합성** | `_12_dub_to_vid.py` | • 더빙 오디오 + 영상 결합<br/>• 립싱크 동기화 | GPU 가속 인코딩 | 2~5분 |

### 연결 고리

- **API 엔드포인트** → `POST /api/videos/{id}/dub` → `process_video_dubbing.delay()`

⸻

## 6. 비동기 큐 & 워커

### 연결 고리

- **FastAPI 엔드포인트** → **BackgroundTasks**

⸻

## 7. 실시간 상태 & 알림

### 연결 고리

- **작업 상태 변경** → **즉시 브로드캐스트** → **토스트 알림**
- **사용자별 룸 관리** → **JWT 토큰 검증**
- **간단한 클라이언트 자동 재연결 로직 정도만 초기 구현- 하트비트는 서비스 안정화 후 점진적으로 도입**

⸻

## 8. 결과 패키징 & 전달

- **병합** ― 더빙 오디오 + 자막 + 원본 영상 → `output.mp4`
- **자막** ― `output.vtt`, `output.srt` 생성
- **프리사인 URL** ― 7일 만료
- **다운로드 강제** ― `Content-Disposition: attachment`

⸻

## 9. 가시성(Observability)

| 항목 | 도구 | 핵심 지표 |
|---|---|---|
| 로그 | structlog JSON | job_id, latency_ms, gpu_mem_mb |
| 오류 | Sentry | job_id와 연동 |

⸻

## 10. 배포 & 운영

| 레이어 | 권장 설정 |
|---|---|
| 컨테이너 | 멀티 스테이지 빌드 → 슬림 실행 이미지(uvicorn-gunicorn-fastapi) |
| 인그레스 | Caddy 2(자동 TLS) |

⸻

## 배포 전 최종 체크리스트

1. **중복 업로드 대응** — 동일 체크섬 → 409 또는 기존 리턴
2. **모델 폴백 로직** — GPU 불가 시 CPU 모델로 큐 이동
3. **과금 훅** — 병합 성공 시점에만 사용량 증가
4. **데이터 보존 정책** — N일 후 원본 자동 삭제
5. **개인정보·저작권** — 음성 클로닝 동의 확보, TTS 정책 준수

⸻