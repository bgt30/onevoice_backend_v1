# 🎬 서비스-급 음성 더빙(Voice-Dubbing) 백엔드 — 심층 설계 청사진

아래는 각 단계를 ① 핵심 작업, ② 구체 구현 팁, ③ 단계 간 연결 고리로 나눠 깊이 있게 정리한 로드맵입니다.

⸻

## 1. 시스템 아키텍처 & 워크플로우 설계

| 의사결정 포인트 | 선택지 & 힌트 | 다음 단계에 끼치는 영향 |
|---|---|---|
| 서비스 토폴로지 | 모놀리식 → 모듈형 모놀리식 → 마이크로서비스/이벤트 기반 | 큐, API, 워커, GPU 노드 배치 방식 결정 |
| 미디어 파이프라인 | DAG(유향 비순환 그래프): 업로드 → 전처리 → STT → 번역 → TTS → 병합 → 전달 | 각 노드가 큐 태스크 및 DB 상태와 1:1 매핑 |
| 데이터 계약 | JSON 스키마 + Pydantic 모델을 shared-contracts/ 저장소에 버전 관리 | API ↔ 워커 ↔ 프론트엔드 스키마 불일치 방지 |
| 다이어그램 | C4 또는 Mermaid → README에 자동 렌더링 | 온보딩 & 운영 문서화 |

**팁**: `/infra/workflows/voice_dubbing.mmd`를 만들고 CI에서 이미지로 렌더해 변경 사항을 즉시 확인하세요.

⸻

## 2. API 설계 & 문서화

1. **버전 관리** — 모든 라우트에 `/v1/videos` 식 접두사
2. **Idempotency-Key 헤더**로 중복 업로드 방지
3. **Async-first** — 변경 요청은 `job_id` 반환, 클라이언트는 상태 구독
4. **OpenAPI 기반 코드 생성** — FastAPI 스텁 + TypeScript SDK 자동 생성

### 연결 고리
- `job_id`는 Jobs 테이블 FK → 워커가 상태 업데이트
- OpenAPI 스펙은 테스트 하네스와 k6 부하 테스트(11단계)에서도 재사용

⸻

## 3. 데이터베이스 & 상태 모델

| 테이블 | 핵심 컬럼 | 비고 |
|---|---|---|
| users | id, 요금제, 한도 | Stripe customer_id 연결 |
| videos | id, user_id, src_url, duration, language_detected | 불변 메타데이터 |
| jobs | id, video_id, step, status(열거형), progress%, error_json | 파이프라인 노드 당 1행 |
| results | id, video_id, dubbed_url, audio_url, subtitles_url | CDN/프리사인 URL |
| worker_events | job_id, timestamp, payload JSONB | Sentry 추적 & 메트릭용 |

### DB 선택
- **PostgreSQL** (+ Timescale 필요 시)
- **Alembic** 자동 생성 후 수동 리뷰로 마이그레이션 관리

⸻

## 4. 인증·인가 & 쿼터

- **JWT + OAuth2** (FastAPI OAuth2PasswordBearer)
- **RBAC 스코프** ― `read:video`, `write:video`, `admin:*`
- **레이트 리미트** ― slowapi 토큰 버킷, 사용자·IP 단위

### 연결
- JWT sub ↔ users.id — S3 경로(`{user_id}/raw/...`) 접근 제어

⸻

## 5. 파일 입출력 & 스토리지

| 과제 | 구현 |
|---|---|
| 대용량 업로드 | tus.io(청크·재개) 또는 uppy + S3 멀티파트 |
| 콜드 스토리지 | S3 / Cloudflare R2 → 30일 후 Glacier |
| 워커 스트리밍 | 프리사인 URL(1h TTL)로 GPU 노드가 직접 다운로드 |
| 체크섬 | SHA-256 저장하여 중복·무결성 확인 |

⸻

## 6. 미디어·AI 처리 파이프라인

| 단계 | 도구 | 상세 |
|---|---|---|
| 오디오 추출 | ffmpeg | `-i input.mp4 -vn -ac 1 -ar 16k raw.wav` |
| 화자 분리 | pyannote.audio 또는 Deepgram Nova | |
| STT | OpenAI Speech-to-Text(2025) / WhisperX | |
| 번역 | OpenAI GPT-4o, Papago, DeepL 등 | |
| TTS·보이스 클로닝 | OpenVoice, ElevenLabs, OpenAI TTS 등 | |
| 립싱크·병합 | ffmpeg, pydub, gensync(리얼타임 립매칭) | |

### 예외 처리
- TTS 실패 시 기본 보이스로 폴백, `job.status=needs_review` 표시
- 중간 산출물(`*.json`, `*.wav`)을 `debug/…` 경로에 24h 보관

⸻

## 7. 비동기 큐 & 워커

| 계층 | 기술 | 패턴 |
|---|---|---|
| 브로커 | Redis(Celery/RQ) / RabbitMQ(Dramatiq) | |
| 워커 풀 | GPU 라벨이 있는 Kubernetes Deployment 자동 확장 | |
| 체이닝 | Celery Canvas (chain, group, chord) | |
| 재시도 | 지수 백오프 최대 5회 → 영구 오류는 Sentry 전송 | |

⸻

## 8. 실시간 상태 & 알림

1. 워커 → Redis Streams `job_progress` 퍼블리시
2. FastAPI WS 엔드포인트가 구독 후 프론트에 스트림
3. WS 불가 시 3초마다 `/status` 폴링
4. `status=failed` 토스트 + 재시도 버튼

⸻

## 9. 결과 패키징 & 전달

- **병합** ― 더빙 오디오 + 원본 영상 → `output.mp4`(H.264+AAC)
- **자막** ― `output.vtt`, `output.srt` 생성
- **프리사인 URL** ― 7일 만료
- **다운로드 강제** ― `Content-Disposition: attachment`

⸻

## 10. 가시성(Observability)

| 항목 | 도구 | 핵심 지표 |
|---|---|---|
| 로그 | structlog JSON → Loki/ELK | job_id, latency_ms, gpu_mem_mb |
| 추적 | OpenTelemetry → Jaeger | 전체 파이프라인 Span |
| 메트릭 | Prometheus + Grafana | queue_depth, error_rate, avg_cost_per_min_audio |
| 오류 | Sentry | job_id와 연동 |

⸻

## 11. 테스트 & CI/CD

- **unit** — pytest, ffmpeg & STT 목(Mock)
- **golden-file** — 레퍼런스 음원 MSE 비교
- **부하** — k6로 `/upload`·`/status` 시나리오
- **정적 분석** — Ruff, mypy, Bandit
- **보안 스캔** — trivy
- **CI** — GitHub Actions: pytest → docker build → helm lint → 통합 배포

⸻

## 12. 배포 & 운영

| 레이어 | 권장 설정 |
|---|---|
| 컨테이너 | 멀티 스테이지 빌드 → 슬림 실행 이미지(uvicorn-gunicorn-fastapi) |
| 런타임 | Kubernetes(EKS/GKE): 노드풀 cpu-small, gpu-a10g |
| 인그레스 | Nginx 혹은 Caddy 2(자동 TLS) |
| 시크릿 | AWS Secrets Manager + IAM-RSA |
| 배포 전략 | Argo Rollouts(블루-그린·카나리) |
| 비용 절감 | Spot GPU + 야간 다운스케일 CronJob |

⸻

## 단계 간 데이터·이벤트 흐름

```
Client ──▶ /upload ──▶ DB(videos)
              │
              └─▶ 큐 enqueue ──▶ GPU 워커 ──▶ 상태 업데이트(DB)
     ▲                                            │
     │ WS /status                                  │
     └─────────────────────────────────────────────┘
       /result ──▶ S3 Presigned URL
```

- **단일 진실 원본**: jobs 행 하나로 모든 상태 공유
- **제로-카피 미디어**: API는 영상을 다시 읽지 않고, 워커가 S3에서 바로 스트림
- **추적 ID 전파**: X-Request-ID가 API→큐→워커까지 이어져 Sentry·Grafana에서 로그·트레이스 결합

⸻

## 배포 전 최종 체크리스트

1. **중복 업로드 대응** — 동일 체크섬 → 409 또는 기존 리턴
2. **모델 폴백 로직** — GPU 불가 시 CPU 모델로 큐 이동
3. **과금 훅** — 병합 성공 시점에만 사용량 증가
4. **데이터 보존 정책** — N일 후 원본 자동 삭제
5. **개인정보·저작권** — 음성 클로닝 동의 확보, TTS 정책 준수

⸻

## 한 줄 정리

**탄탄한 음성 더빙 백엔드는 DAG로 쪼개진 작업을 공통 계약(API·DB)으로 엮고, GPU-인식 워커 큐 위에서 자동 확장·관측 가능하게 운영하는 시스템이다.** 