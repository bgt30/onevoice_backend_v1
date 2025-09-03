# Deep Architectural Overview of the OneVoice Project

## High-Level Summary

OneVoice is a modular, scalable backend API service designed for AI-powered multilingual voice dubbing. Built with FastAPI and SQLAlchemy, it integrates multiple AI modules (speech recognition, translation, TTS) and external services (Paddle, OpenAI, ElevenLabs) to deliver high-quality audio-visual dubbing workflows. Its architecture emphasizes separation of concerns, extensibility, and robustness, supporting features like user management, billing, job orchestration, and real-time processing via message queues.

---

## 1. System Architecture & Major Containers

### 1.1 API Layer (FastAPI Application)
- **Main Application (`app/main.py`)**: Initializes the FastAPI app, configures middleware (CORS, GZip), exception handlers, and includes routers for core functionalities.
- **Routers (`app/api/*`)**:
  - **Auth (`auth.py`)**: Handles user registration, login, email verification, password resets.
  - **Users (`users.py`)**: Manages user profiles, activity logs, notifications, subscription info.
  - **Videos (`videos.py`)**: Manages video uploads, metadata, download URLs, dubbing initiation.
  - **Billing (`billing.py`)**: Handles billing history, payment methods, plans, subscriptions, webhooks.
  - **Jobs (`jobs.py`)**: Monitors and controls background jobs (status, cancel, resume).

### 1.2 Core Business Logic (Services Layer)
- **Service Modules (`app/services/*`)**:
  - **Auth (`auth_service.py`)**: Authentication, user creation, token management.
  - **User (`user_service.py`)**: Profile, activity, notification, billing, subscription management.
  - **Video (`video_service.py`)**: Video CRUD, media file handling, upload URLs, download URLs, thumbnail generation.
  - **Billing (`billing_service.py`)**: Billing history, plans, subscriptions, payment methods, webhook processing.
  - **Job (`job_service.py`)**: Job lifecycle, status updates, step management.
  - **Dubbing (`dubbing_service.py`)**: Orchestrates AI dubbing pipeline, manages tasks, handles failures, resumes.
  - **Notification (`notification_service.py`)**: Email notifications, templating, dispatching.
  - **Storage (`storage_service.py`)**: S3 interactions, presigned URLs, file uploads/downloads, validation.
  
### 1.3 Data Layer (ORM Models & Database)
- **Models (`app/models/*`)**:
  - **User (`user.py`)**: User info, subscription, activity logs.
  - **Video (`video.py`)**: Video metadata, media files, statuses.
  - **Billing (`billing.py`)**: Billing records, credit usage.
  - **Job (`job.py`)**: Jobs, job steps, status, progress.
  - **PendingUser (`pending_user.py`)**: Temporary users awaiting email verification.
- **Database (`app/core/database.py`)**:
  - Synchronous (`create_engine`) and asynchronous (`create_async_engine`) engines.
  - Session management (`SessionLocal`, `AsyncSessionLocal`).
  - Migration environment (`env.py`) with Alembic for schema evolution.

### 1.4 External Integrations & Services
- **AI Modules (`ai/*`)**:
  - **Speech Recognition**: OpenAI, ElevenLabs, WhisperX, Demucs for audio preprocessing.
  - **Translation & Summarization**: GPT-based prompts for text processing.
  - **TTS**: OpenAI, FishTTS, custom, F5TTS for voice synthesis.
  - **Audio Processing**: Pydub, librosa, soundfile for audio manipulation.
- **Billing & Payments**:
  - **Paddle**: Main payment provider, with webhook handling for subscription events.
  - **Stripe**: Deprecated, replaced by Paddle (migration scripts).
- **Message Queue (`app/queue`)**:
  - **SQS Client (`sqs_client.py`)**: Sends messages for asynchronous task execution.
  - **Consumer (`consumer.py`)**: Processes messages, triggers dubbing pipeline.
  - **Dispatcher (`dispatcher.py`)**: Enqueues jobs into SQS.
  - **Message Models (`message_models.py`)**: Defines message schemas.

### 1.5 Background Workers (`worker/`)
- **Runner (`runner.py`)**: Runs event loop, continuously polls SQS, triggers `DubbingService`.
- **Handlers (`handlers.py`)**: Executes specific tasks like dubbing pipeline.

### 1.6 Monitoring & Logging
- **Health Checks (`health_check.py`)**: System resource and database health endpoints.
- **Logging (`logging_config.py`)**: Structured logging with JSON, request tracing middleware.

---

## 2. Core Components & Responsibilities

### 2.1 User Management
- **`user_service.py`**: Handles profile updates, avatar uploads, activity logs, subscription info, credit management.
- **`auth_service.py`**: Authentication, token issuance, password resets, email verification.
- **`dependecies.py`**: Dependency injection for user/session management, current user validation, subscription/credit checks.

### 2.2 Video & Media Handling
- **`video_service.py`**:
  - CRUD operations for videos.
  - Media file management (`MediaFile` model): paths, formats, durations, URLs.
  - Upload URL generation (`get_upload_url`).
  - Download URL provisioning (`get_download_url`).
  - Thumbnail generation and update.
- **`_find_video.py`**: Finds video files in workspace.
- **`_7_sub_into_vid.py`**: Merges subtitles into videos, burns subtitles, overlays text.

### 2.3 Job Orchestration & Management
- **`job_service.py`**:
  - Create, update, cancel, resume jobs.
  - Track progress, handle retries, manage job steps.
- **`dubbing_service.py`**:
  - Orchestrates AI dubbing pipeline.
  - Manages multi-step process: audio extraction, recognition, translation, TTS, merging.
  - Handles failures, retries, and resumption.
- **`handlers.py` & `runner.py`**:
  - Polls message queue.
  - Executes jobs asynchronously.
  - Ensures idempotency and error handling.

### 2.4 AI Modules & External APIs
- **Speech Recognition**:
  - `openai_asr.py`, `elevenlabs_asr.py`, `whisperX_302.py`, `demucs_vl.py`.
  - Handles audio preprocessing, transcription, timestamp alignment.
- **Translation & Summarization**:
  - `translate_lines.py`, `summarize.py`, GPT prompts.
  - Text segmentation, summarization, terminology extraction.
- **TTS**:
  - `openai_tts.py`, `fish_tts.py`, `custom_tts.py`, `f5tts.py`.
  - Voice synthesis, audio post-processing.
- **Audio Processing**:
  - `audio_preprocess.py`, `merge_audio.py`, `ref_audio.py`.
  - Audio normalization, segmentation, merging, reference extraction.

### 2.5 Storage & File Management
- **`storage_service.py`**:
  - S3 interactions: presigned URLs, uploads, downloads, validation.
  - Handles local fallback if S3 unavailable.
- **`path_constants.py`**:
  - Defines standardized paths for logs, media, audio segments, temp files.

### 2.6 Billing & Subscription
- **`billing_service.py`**:
  - Manages billing history, plans, subscriptions.
  - Integrates with Paddle API.
  - Handles webhook events for subscription lifecycle.
- **`models/billing.py`**:
  - Billing records, credit usage, invoice tracking.
- **`webhooks.py`**:
  - Processes Paddle webhook notifications.
  - Updates subscription status, billing records accordingly.

### 2.7 Notifications & User Engagement
- **`notification_service.py`**:
  - Sends email notifications for verification, password reset, job completion.
  - Uses templates and SMTP/SNS integrations.

### 2.8 Infrastructure & Utilities
- **`dependecies.py`**:
  - Dependency injection for database sessions, user validation, subscription checks.
- **`workspace_utils.py`**:
  - Manages workspace directories, config paths, file retrieval.
- **`logging_config.py`**:
  - Structured logging setup.
- **`health_check.py`**:
  - System health endpoints.

---

## 3. Data Flow & Control Flow

### 3.1 User Interaction
- Users interact via REST API endpoints (FastAPI routers).
- User registration triggers email verification (`auth/signup`).
- Authenticated users manage videos, profiles, subscriptions.
- Billing endpoints handle payment methods, plans, billing history.

### 3.2 Job Lifecycle
- User initiates dubbing (`/videos/{id}/dub`).
- API calls `DubbingService.start_dubbing_job()`.
- Job is created in DB, status set to pending.
- Message enqueued into SQS (`enqueue_dubbing_job()`).
- Worker polls SQS (`consumer.py`), retrieves message.
- Worker triggers `DubbingService.execute_dubbing_pipeline()`.
- Pipeline steps:
  - Extract audio from video.
  - Transcribe audio (ASR modules).
  - Split and align text.
  - Translate text.
  - Generate TTS audio.
  - Merge audio and video.
  - Upload final video.
- Status updates propagate back to DB.
- Notifications sent upon completion or failure.

### 3.3 External API & AI Module Interaction
- Transcription modules call respective APIs (OpenAI, ElevenLabs, WhisperX).
- Translation modules invoke GPT prompts.
- TTS modules call respective APIs/services.
- Audio processing modules handle file conversions, normalization, merging.

### 3.4 Error Handling & Resumption
- Failures in any step update job status.
- `DubbingService` supports resuming from failures.
- Message queue retries or manual restart.
- Exception handlers in API layer ensure robustness.

---

## 4. Scalability & Extensibility
- **Modular design**: Each AI component (ASR, TTS, translation) is pluggable.
- **Message Queue**: Asynchronous task execution decouples API from processing.
- **Database models**: Extendable for new features (e.g., new billing plans, media types).
- **External integrations**: Easily switch or add providers (e.g., new TTS API).

---

## 5. Summary of Critical External Dependencies
| Container | External Service | Role |
|------------|---------------------|-------|
| API Layer | FastAPI | HTTP interface, middleware, exception handling |
| AI Modules | OpenAI, ElevenLabs, WhisperX, Demucs | Speech recognition, TTS, audio preprocessing |
| Storage | AWS S3 | Media storage, presigned URLs |
| Billing | Paddle | Subscription, payment management |
| Message Queue | AWS SQS | Asynchronous task orchestration |
| Notification | SES/SNS | Email notifications |

---

## 6. Missing or Uncertain Details
- Exact deployment architecture (containerized, serverless, etc.) is **Unknown**.
- Specific scaling strategies (horizontal scaling, worker pools) are **Unknown**.
- Internal data flow diagrams are **Not available**; only control flow described.

---

This detailed, precise architecture overview captures all concrete evidence from the codebase and directory structure, emphasizing modularity, external integrations, and control flow, suitable for diagram generation and further documentation.