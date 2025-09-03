## OneVoice Backend API 명세서

이 문서는 `app/api` 디렉터리의 FastAPI 라우터 정의를 기반으로 자동 정리된 API 명세서입니다. 스키마 상세 필드는 `app/schemas.py` 및 관련 모델을 참고하세요. 본 문서의 모든 경로는 동일한 서버 베이스 URL을 전제로 하며, 별도 표기가 없으면 JSON 요청/응답을 사용합니다.

- 인증 방식: Bearer JWT (Authorization: Bearer <token>)
- 기본 Media Type: application/json (파일 업로드 시 multipart/form-data)
- 표기 규칙: 요청 본문/응답은 Pydantic 모델 이름으로 명시합니다.


### 공통 에러
- 400: 잘못된 요청, 만료/무효 토큰, 처리 불가 상태 등
- 401: 인증 실패 또는 토큰 누락
- 403: 권한 부족
- 404: 대상 리소스 없음
- 500: 서버 내부 오류


## Authentication API
Prefix: `/api/auth`

1) POST `/forgot-password`
- 설명: 비밀번호 재설정 이메일 발송 요청
- 인증: 불필요
- Body: `ForgotPasswordRequest`
- 200: `ForgotPasswordResponse`
- 404: `Error` (사용자 미발견, 보안상 실제 응답은 200과 동일 메시지를 반환)

2) POST `/login`
- 설명: 이메일/비밀번호로 로그인
- 인증: 불필요
- Body: `LoginRequest`
- 200: `AuthResponse`
- 401: `Error`

3) POST `/logout`
- 설명: 로그아웃 (클라이언트 측 토큰 제거 필요)
- 인증: 필요
- 200: `ForgotPasswordResponse`

4) POST `/reset-password`
- 설명: 재설정 토큰으로 비밀번호 변경
- 인증: 불필요
- Body: `ResetPasswordRequest`
- 200: `ForgotPasswordResponse`
- 400: `Error` (토큰 무효/만료 등)

5) POST `/signup`
- 설명: 회원가입 신청(이메일 인증 대기 상태로 임시 저장)
- 인증: 불필요
- Body: `SignupRequest`
- 200: `ForgotPasswordResponse`
- 400: `Error`
- 500: `Error`

6) POST `/verify-email`
- 설명: 이메일 인증 및 실제 계정 생성
- 인증: 불필요
- Body: `str` (token)
- 200: `AuthResponse`
- 400: `Error`
- 500: `Error`

7) POST `/resend-verification`
- 설명: 회원가입 인증 이메일 재발송
- 인증: 불필요
- Body: `str` (email)
- 200: `ForgotPasswordResponse`
- 404: `Error`
- 400: `Error`


## Billing & Subscriptions API
Prefix: `/api/billing`

1) GET `/history`
- 설명: 청구 이력 페이징 조회
- 인증: 필요
- Query:
  - `page` (int, 기본 1)
  - `perPage` (int, 기본 20)
- 200: `BillingHistoryResponse`

2) PUT `/payment-method`
- 설명: 기본 결제수단 업데이트
- 인증: 필요
- Body: `PaymentMethodUpdateRequest`
- 200: `ForgotPasswordResponse`

3) GET `/payment-methods`
- 설명: 등록된 모든 결제수단 조회
- 인증: 필요
- 200: `List[PaymentMethod]`

4) DELETE `/payment-methods/{id}`
- 설명: 결제수단 삭제
- 인증: 필요
- Path: `id` (str)
- 200: `ForgotPasswordResponse`

5) GET `/plans`
- 설명: 제공 중인 요금제 목록 조회
- 인증: 필요
- 200: `List[BillingPlan]`

6) POST `/setup-intent`
- 설명: 결제수단 추가를 위한 클라이언트 토큰/세트업 인텐트 생성 (Paddle)
- 인증: 필요
- 200: `SetupIntentResponse`

7) POST `/subscribe`
- 설명: 구독 생성
- 인증: 필요
- Body: `SubscribeRequest`
- 201: `Subscription`

8) POST `/subscription/cancel`
- 설명: 현재 구독 취소
- 인증: 필요
- 200: `ForgotPasswordResponse`

9) GET `/subscription`
- 설명: 현재 구독 조회
- 인증: 필요
- 200: `Subscription`

10) PUT `/subscription`
- 설명: 구독 플랜 변경/업데이트
- 인증: 필요
- Body: `SubscriptionUpdateRequest`
- 200: `Subscription`

11) POST `/subscription/resume`
- 설명: 취소 예정 구독 재개
- 인증: 필요
- 200: `Subscription`

12) GET `/upcoming-invoice`
- 설명: 다음 청구서(인보이스) 프리뷰 조회
- 인증: 필요
- 200: `UpcomingInvoiceResponse`

13) GET `/usage`
- 설명: 사용량/과금 메터링 조회
- 인증: 필요
- 200: `UsageResponse`


## Video Management API
Prefix: `/api/videos`

1) GET ``
- 설명: 사용자 비디오 목록 조회 (페이징/상태 필터)
- 인증: 필요
- Query:
  - `page` (int, 기본 1)
  - `per_page` (int, 기본 20)
  - `status` (str, 선택)
- 200: `VideosResponse`

2) POST ``
- 설명: 새 비디오 메타데이터 생성
- 인증: 필요
- Body: `VideoCreateRequest`
- 201: `Video`

3) GET `/{id}`
- 설명: 비디오 단건 조회
- 인증: 필요
- Path: `id` (str)
- 200: `Video`

4) PUT `/{id}`
- 설명: 비디오 메타데이터 업데이트
- 인증: 필요
- Path: `id` (str)
- Body: `VideoUpdateRequest`
- 200: `Video`

5) DELETE `/{id}`
- 설명: 비디오 영구 삭제
- 인증: 필요
- Path: `id` (str)
- 200: `ForgotPasswordResponse`

6) POST `/upload-url`
- 설명: S3 직업로드용 프리사인드 URL 발급
- 인증: 필요
- Body: `UploadUrlRequest`
- 200: `UploadUrlResponse`

7) GET `/{id}/download`
- 설명: 처리 결과물 다운로드용 프리사인드 URL 반환
- 인증: 필요
- Path: `id` (str)
- Query:
  - `language` (str, 선택, 예: en, ja)
  - `file_type` (enum FileType, 선택: `dubbed_video` | `subtitle_video` | `dub_subtitles` | `translation_subtitles` | `source_subtitles` | `original`)
- 200: `DownloadResponse`

8) POST `/{id}/dub`
- 설명: 더빙 파이프라인 시작 (크레딧 체크 포함). 비동기 실행 트리거 반환
- 인증: 필요 (크레딧 검증)
- Path: `id` (str)
- Body: `DubRequest`
- 202: `DubResponse`

9) POST `/{id}/duplicate`
- 설명: 기존 비디오 복제
- 인증: 필요 (크레딧 검증)
- Path: `id` (str)
- 201: `Video`

10) POST `/{id}/thumbnail`
- 설명: 썸네일 생성/업데이트
- 인증: 필요
- Path: `id` (str)
- Form:
  - `thumbnail` (file, 선택)
  - `timestamp` (float|int, 선택, 초 단위)
- 200: `ThumbnailUploadResponse`

11) GET `/languages`
- 설명: 지원 언어 목록 조회
- 인증: 불필요 (공개)
- 200: `List[Language]`

12) GET `/voices`
- 설명: 언어별 사용 가능한 보이스 목록 조회
- 인증: 불필요 (공개)
- Query: `language` (str, 필수)
- 200: `List[Voice]`


## Job Management API (per Video)
Prefix: `/api/videos`

1) GET `/{id}/status`
- 설명: 해당 비디오 처리(더빙) Job 상태 조회
- 인증: 필요
- Path: `id` (str)
- 200: `JobStatus`
- 404: `Error`

2) POST `/{id}/cancel`
- 설명: 진행 중인 비디오 처리 Job 취소
- 인증: 필요
- Path: `id` (str)
- 200: `ForgotPasswordResponse`
- 400/404/500: `Error`

3) POST `/{id}/resume`
- 설명: 실패/보류/진행 중 더빙 작업 재개 또는 시작
- 인증: 필요
- Path: `id` (str)
- 200: `ForgotPasswordResponse`
- 400/404: `Error`


## Jobs API (사용자 작업 목록/상세)
Prefix: `/api/jobs`

1) GET ``
- 설명: 현재 사용자 작업 목록 조회 (필터/페이징)
- 인증: 필요
- Query:
  - `job_type` (str, 선택)
  - `status` (str, 선택)
  - `limit` (int, 기본 50, 1~100)
  - `offset` (int, 기본 0)
- 200: `JobsResponse`

2) GET `/{id}`
- 설명: 작업 상세 조회
- 인증: 필요
- Path: `id` (str)
- 200: `Job`
- 404: `Error`


## Webhooks (Paddle)
Prefix: `/api/webhooks`

1) POST `/paddle`
- 설명: Paddle 웹훅 수신 엔드포인트. `paddle-signature` 헤더를 이용해 서명 검증 수행
- 인증: 불필요 (서명 검증)
- Headers: `paddle-signature` (string, 선택 — 개발 환경에선 미검증 가능)
- Body: Paddle 이벤트 JSON (원문 Payload)
- 200: `{ "status": "success" }`
- 400: `Invalid webhook signature` 또는 페이로드 오류
- 500: 처리 중 오류

- 처리 이벤트 예시:
  - `subscription.created` / `subscription.updated` / `subscription.cancelled` / `subscription.resumed`
  - `transaction.completed` / `transaction.payment_failed`


## 보안 및 인증
- 보호 엔드포인트는 `Authorization: Bearer <JWT>` 헤더 필요
- 이메일 관련 토큰(`reset-password`, `verify-email`)은 Body 필드로 전달
- 더빙 시작/복제 엔드포인트는 크레딧 검증을 통과해야 함


## 파일 업로드/다운로드
- 업로드: `/{id}/thumbnail` 에서 `multipart/form-data` 사용
- 프리사인드 URL: `/api/videos/upload-url`, `/{id}/download`로 발급받아 직접 S3 업/다운로드 수행


## 모델 레퍼런스
아래 모델은 이름만 명시합니다. 상세 필드 정의는 `app/schemas.py` 및 각 서비스 로직을 참고하세요.
- Auth/사용자: `AuthResponse`, `User`, `UserProfileUpdateRequest`, `PasswordUpdateRequest`, `ForgotPasswordRequest`, `ForgotPasswordResponse`, `SignupRequest`
- 비디오: `Video`, `VideosResponse`, `VideoCreateRequest`, `VideoUpdateRequest`, `ThumbnailUploadResponse`, `UploadUrlRequest`, `UploadUrlResponse`, `DubRequest`, `DubResponse`, `Language`, `Voice`, `FileType`
- 잡: `Job`, `JobsResponse`, `JobStatus`
- 과금/구독: `BillingHistoryResponse`, `PaymentMethodUpdateRequest`, `PaymentMethod`, `SetupIntentResponse`, `SubscribeRequest`, `SubscriptionUpdateRequest`, `UpcomingInvoiceResponse`, `UsageResponse`, `BillingPlan`, `Subscription`
