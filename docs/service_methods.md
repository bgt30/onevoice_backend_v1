## 서비스 메서드 레퍼런스

해당 문서는 `app/services/dubbing_service.py`, `app/services/storage_service.py`, `app/services/video_service.py` 내 모든 메서드를 요약합니다. 각 항목은 주요 기능을 한 줄로 간략히 설명합니다.


## app/services/dubbing_service.py

### 클래스: `DubbingService`
- **DUBBING_STEPS**: 더빙 파이프라인 단계 정의(이름, 모듈, 함수, 가중치, 설명) 목록.
- **start_dubbing_job(db, user, video_id, dub_request) -> DubResponse**: 더빙 Job을 생성하고 비디오 상태/과금 처리 후 시작 응답을 반환.
- **execute_dubbing_pipeline(job_id) -> None**: 작업공간 준비, 소스 다운로드, 단계 생성 및 실행, 결과 업로드까지 전체 파이프라인 수행.
- **resume_dubbing_pipeline(job_id) -> None**: 파이프라인 재개. 상태 초기화, 워크스페이스 없으면 생성 및 원본 재다운로드, 실패 단계 없으면 전체 재실행, 각 단계 전 취소 상태 확인, 진행률 재계산, 로그/알림 보강.
- **_setup_workspace(job) -> str**: Job ID 기반 로컬 작업공간 디렉토리 구조 생성.
- **_download_source_video(job, workspace) -> None**: MediaFile에서 원본을 찾아 스토리지에서 로컬 작업공간으로 다운로드.
- **_copy_config_files(workspace) -> None**: `config.yaml` 및 `custom_terms.xlsx`(존재 시) 작업공간으로 복사.
- **_create_job_steps(db, job_id) -> None**: 파이프라인 단계들을 `JobStep` 레코드로 생성하여 진행률 추적 기반 마련.
- **_execute_step(db, job_id, step_config, workspace) -> None**: 단일 단계 실행 및 성공/실패/진행률 업데이트와 에러 알림 처리.
- **_run_ai_module(step_config, workspace) -> None**: 단계 정의의 모듈/함수를 동적으로 호출하고 필요한 인자(`workspace_path`, `config_path`)를 전달.
- **_update_overall_progress(db, job_id) -> None**: 가중치 기반으로 전체 진행률 계산 후 `Job` 진행률 갱신.
- **_finalize_dubbing(db, job, workspace) -> None**: 산출물 업로드, 비디오/잡 상태 업데이트, 완료 알림 발송 및 작업공간 정리.
- **_upload_result_files(db, job, workspace) -> Dict[str, str]**: 결과 파일들을 스토리지로 업로드하고 `MediaFile` 레코드 생성.
- **_update_video_status(db, job, result_files) -> None**: 비디오 상태를 `completed`로 전환하고 완료 시각 기록.
- **_send_completion_notification(job_id) -> None**: 더빙 작업 완료 알림 발송.
- **_send_error_notification(job_id, step_name, error_message) -> None**: 단계 또는 파이프라인 오류 알림 발송.
- **_handle_pipeline_error(db, job_id, error_message) -> None**: Job 상태를 실패로 전환하고 오류 알림 처리.
- **_cleanup_workspace(workspace) -> None**: 로컬 작업공간 디렉토리 정리.
- **cancel_dubbing_job(db, job_id, user_id) -> bool**: 사용자 권한 확인 후 Job을 취소, 작업공간 정리 및 취소 알림 발송.


## app/services/storage_service.py

### 클래스: `StorageService`
- **__init__(self)**: S3 클라이언트를 환경설정으로 초기화하고 사용 가능 여부 플래그 설정.
- **create_presigned_upload_url(self, file_key, content_type, expires_in=3600) -> str**: 지정 키/콘텐츠 타입으로 S3 업로드용 프리사인드 URL 생성.
- **create_presigned_download_url(self, file_key, expires_in=3600, filename=None) -> str**: 파일명 지정 가능 다운로드용 프리사인드 URL 생성.
- **upload_file(self, file, file_key, content_type=None) -> str**: FastAPI `UploadFile` 객체를 S3에 업로드하고 공개 URL 반환.
- **upload_local_file(self, local_path, file_key, content_type=None) -> str**: 로컬 파일을 S3에 업로드하고 공개 URL 반환.
- **download_file(self, file_key, destination_path) -> bool**: S3의 객체를 로컬 경로로 다운로드.
- **delete_file(self, file_key) -> bool**: S3 객체 삭제(존재하지 않으면 성공으로 간주).
- **file_exists(self, file_key) -> bool**: S3 객체 존재 여부 확인.
- **get_file_size(self, file_key) -> Optional[int]**: S3 객체의 바이트 크기 조회.
- **copy_file(self, source_key, destination_key) -> bool**: 동일 버킷 내에서 객체 복사.
- **generate_file_key(self, user_id, file_type, filename, subfolder=None) -> str**: UUID 기반 고유 파일 키 생성.
- **generate_thumbnail_key(self, user_id, video_id, timestamp=None) -> str**: 썸네일 키 생성(타임스탬프 포함 가능).
- **validate_file_type(self, file, allowed_types) -> bool**: MIME/확장자 기반 파일 타입 검증.

> 전역 인스턴스: `storage_service = StorageService()`


## app/services/video_service.py

### 클래스: `VideoService`
- **_get_latest_media_file(db, video_id, file_type, language=None, only_active=True) -> Optional[MediaFile]**: 조건에 맞는 최신 `MediaFile` 조회.
- **_get_original_media_file(db, video_id) -> Optional[MediaFile]**: 해당 비디오의 최신 원본 `MediaFile` 조회.
- **_get_thumbnail_media_file(db, video_id) -> Optional[MediaFile]**: 해당 비디오의 최신 썸네일 `MediaFile` 조회.
- **get_videos(db, user, page=1, per_page=20, status_filter=None) -> VideosResponse**: 사용자 비디오 목록과 페이지네이션 정보 반환.
- **create_video(db, user, request) -> VideoSchema**: 새 비디오 레코드 생성 후 스키마로 반환.
- **get_video(db, user, video_id) -> VideoSchema**: 단일 비디오 상세 조회(원본/썸네일 URL 포함).
- **update_video(db, user, video_id, request) -> VideoSchema**: 제목/설명 업데이트 후 갱신 결과 반환.
- **delete_video(db, user, video_id) -> ForgotPasswordResponse**: 비디오와 관련 `MediaFile` S3 객체 삭제 후 비디오 제거.
- **get_upload_url(db, user, request) -> UploadUrlResponse**: 원본 업로드용 프리사인드 URL 생성 및 임시 비디오/MediaFile 레코드 생성.
- **get_download_url(db, user, video_id, language=None, file_type=None) -> DownloadResponse**: 원본 또는 더빙 산출물에 대한 다운로드 URL 생성.
- **duplicate_video(db, user, video_id) -> VideoSchema**: 원본/썸네일 복사하여 새 비디오와 연계 `MediaFile` 생성.
- **update_thumbnail(db, user, video_id, thumbnail_file=None, timestamp=None) -> ThumbnailUploadResponse**: 썸네일 업로드 또는 타임스탬프 기반 생성 후 레코드 갱신.
- **get_supported_languages() -> List[Language]**: 설정에 정의된 지원 언어 목록 반환.
- **get_available_voices(language) -> List[Voice]**: 특정 언어에 대한 사용 가능 음성 목록 반환.


## app/services/job_service.py

### 클래스: `JobService`
- **create_job(db, user_id, job_type, video_id=None, config=None, priority=5) -> Job**: 새 작업을 생성하고 데이터베이스에 저장.
- **get_job(db, job_id, user_id=None) -> Optional[Job]**: Job ID로 작업 조회(관련 단계 및 비디오 정보 포함).
- **get_jobs_by_user(db, user_id, job_type=None, status=None, limit=50, offset=0) -> List[Job]**: 사용자별 작업 목록 조회(필터링 및 페이지네이션 지원).
- **get_jobs_by_video(db, video_id, user_id) -> List[Job]**: 특정 비디오에 대한 모든 작업 목록 조회.
- **update_job_status(db, job_id, status, error_message=None, error_code=None) -> bool**: 작업 상태 업데이트 및 타이밍 정보 기록.
- **update_job_progress(db, job_id, progress, estimated_completion=None) -> bool**: 작업 진행률 업데이트(0-100% 범위 제한).
- **start_job(db, job_id) -> bool**: 대기 중인 작업을 처리 중 상태로 전환.
- **complete_job(db, job_id, result_data=None) -> bool**: 작업을 완료 상태로 전환하고 결과 데이터 저장.
- **fail_job(db, job_id, error_message, error_code=None, can_retry=True) -> bool**: 작업 실패 처리 및 재시도 카운트 관리.
- **cancel_job(db, job_id, user_id) -> bool**: 사용자 권한 확인 후 작업 취소.
- **create_job_steps(db, job_id, steps) -> bool**: 작업 단계 목록을 생성하여 데이터베이스에 저장.
- **update_step_status(db, job_id, step_name, status, progress=0.0, output_data=None, error_message=None) -> bool**: 개별 작업 단계 상태 및 진행률 업데이트.
- **_update_job_progress_from_steps(db, job_id) -> None**: 모든 단계의 평균 진행률을 계산하여 전체 작업 진행률 갱신.
- **get_job_status_for_video(db, video_id, user_id) -> Optional[JobStatus]**: 비디오의 최신 작업 상태 조회.
- **cleanup_old_jobs(db, days_old=30) -> int**: 지정된 일수보다 오래된 완료/실패 작업 정리.
- **get_pending_jobs(db, job_type=None, limit=10) -> List[Job]**: 대기 중인 작업을 우선순위 및 생성일 순으로 조회.
- **record_credit_usage(db, job, credits_used, operation_type, description=None) -> bool**: 작업에 사용된 크레딧을 기록하고 과금 처리.


## app/services/notification_service.py

### 클래스: `NotificationService`
- **TEMPLATES**: 이메일 템플릿 정의(회원가입 인증, 비밀번호 재설정, 영상 처리 완료/실패).
- **send_signup_verification_email(user, verification_token) -> bool**: 회원가입 이메일 인증 링크가 포함된 이메일 발송.
- **send_password_reset_email(user, reset_token) -> bool**: 비밀번호 재설정 링크가 포함된 이메일 발송.
- **send_video_processing_complete_notification(user, video_title, target_language, processing_duration, download_url) -> bool**: 영상 더빙 완료 알림 이메일 발송.
- **send_video_processing_failed_notification(user, video_title, error_message, retry_url=None) -> bool**: 영상 처리 실패 알림 이메일 발송.
- **_send_email(to_email, subject, html_content) -> bool**: SMTP를 통한 HTML 이메일 발송 처리.
- **_send_smtp_email(msg) -> None**: 동기 SMTP 이메일 발송 실행.
- **_render_template(template, data) -> str**: Jinja2를 사용한 이메일 템플릿 렌더링.
