## OneVoice FastAPI app/ Refactor Plan

### 1) Objectives
- Decouple web request lifecycle from long-running AI dubbing work.
- Introduce a durable task queue (Amazon SQS) and a dedicated Worker runtime.
- Standardize AWS integrations (S3, SES, SNS, CloudWatch) with IAM-first configuration.
- Keep the current API contracts stable while enabling gradual migration.

### 2) Target Deployment Topology
- Web/API (Elastic Beanstalk web env): serves FastAPI (`app/main.py`).
- Worker (Elastic Beanstalk worker env): runs an SQS consumer that executes long-running pipelines.
- SQS: default queue for background jobs; DLQ for poison messages.
- RDS (PostgreSQL): unchanged.
- S3: originals and outputs; presigned URLs for upload/download.
- SES: transactional emails (password reset, signup verification, job notifications).
- SNS: operational alerts (pipeline failures, unexpected worker exits).
- CloudWatch: application logs, metrics, alarms.

### 3) app/ changes (high level)
- Introduce a first-class Task Queue abstraction backed by SQS.
- Move background execution of dubbing from FastAPI `BackgroundTasks` to SQS-based worker.
- Harden AWS service clients for production (IAM role by default, explicit keys only in dev).
- Standardize logging and metrics across API and Worker.

### 4) New modules and directories
- app/queue/
  - `message_models.py`: Pydantic models for queue messages (e.g., `DubbingJobMessage`).
  - `sqs_client.py`: thin wrapper around boto3 SQS with long polling, visibility timeout, batch ops.
  - `dispatcher.py`: enqueue helpers (e.g., `enqueue_dubbing_job(job_id: str)`).
  - `consumer.py`: message dispatch; validates payload → calls service handlers.
- worker/
  - `runner.py`: entrypoint loop for EB Worker; long-polls SQS, processes messages, handles retries/DLQ.
  - `handlers.py`: maps message types → service calls (e.g., `handle_dubbing_job(job_id) → DubbingService.execute_dubbing_pipeline`).

### 5) Configuration updates (`app/config.py`)
- Add feature flags and settings:
  - `USE_SQS_TASK_QUEUE: bool = True`
  - `SQS_QUEUE_URL: Optional[str]`
  - `SQS_DLQ_URL: Optional[str]`
  - `SQS_WAIT_TIME_SECONDS: int = 20` (long polling)
  - `SQS_VISIBILITY_TIMEOUT: int = 900`
  - `AWS_USE_IAM_ROLE: bool = True` (prefer instance/role credentials)
  - `SES_ENABLED: bool = True` (SES is the only mail transport; SMTP removed)
  - `SNS_ALERTS_TOPIC_ARN: Optional[str]`
- Ensure boto3 clients fall back to instance role when keys are unset.
 - Ensure SQS queue is created/configured with the specified visibility timeout; worker will extend per-message visibility as needed.

### 6) Task Queue refactor
- `app/api/videos.py` → `start_dubbing`:
  - Keep validation and job creation in `DubbingService.start_dubbing_job`.
  - Replace `BackgroundTasks.add_task(...)` with `dispatcher.enqueue_dubbing_job(job_id)` when `USE_SQS_TASK_QUEUE` is True.
  - Provide a transitional toggle: when False, use current in-process execution (existing behavior).

- Worker execution flow:
  - `consumer.py` receives `DubbingJobMessage(job_id)` and calls `DubbingService.execute_dubbing_pipeline(job_id)`.
  - Ensure idempotency: before executing, check `Job.status`; skip if already terminal (`completed/failed/cancelled`).
  - Use SQS message attributes for `messageType`, `attempt`, `jobId`.
  - Respect visibility timeout; on handled retriable errors, leave message to be re-delivered; on non-retriable, send to DLQ.

- Reliability:
  - Configure DLQ with redrive policy; set `maxReceiveCount` (e.g., 5).
  - Include application-level deduplication guard (read job state) to tolerate duplicate deliveries.
  - Use exponential backoff for transient failures.

### 7) AWS Integrations hardening
- Storage (S3) — `app/services/storage_service.py`:
  - Prefer IAM role when keys not provided (boto3 default). Keep explicit keys for local/dev.
  - Enforce SSE (AES256) and content-type; add multipart upload for large media (optional in phase 2).

- Emails (SES) — `app/services/notification_service.py`:
  - Use Amazon SES as the sole mail transport (no SMTP fallback). If SES is not configured, disable email sends in non-prod with clear logs.
  - Keep templates as-is; only switch transport to SES.

- Alerts (SNS):
  - Add `publish_alert(subject, message, context)` helper; on pipeline failure or repeated worker exceptions, publish to `SNS_ALERTS_TOPIC_ARN`.

- Logging (CloudWatch):
  - Use structured logs (JSON) for worker events, job transitions, and error contexts.

### 8) API compatibility & incremental migration
- Maintain current API routes and payloads.
- Phase flag: default `USE_SQS_TASK_QUEUE=True` in prod; `False` in local dev to ease iteration.
- Add `/monitoring/health` signals for worker by publishing heartbeats (optional).

### 9) Code-level edits (by file)
- `app/api/videos.py`
  - Replace BackgroundTasks usage in `start_dubbing` with conditional enqueue to SQS.
  - Keep response semantics unchanged.

- `app/services/dubbing_service.py`
  - No logic change to pipeline; ensure it remains callable by worker without FastAPI context.
  - Confirm all storage and DB interactions are independent of request state.

- `app/services/notification_service.py`
  - Implement SES transport only; remove SMTP code and configuration.
  - Add SNS admin alert publisher.

- `app/services/storage_service.py`
  - Detect IAM role automatically; only require keys in dev.
  - Keep presigned URL behavior intact.

- `app/main.py`
  - Remove any direct background task orchestration references.
  - Ensure logging is initialized with CloudWatch when configured.

- New: `app/queue/*`, `worker/*` as described above.

### 10) Observability & metrics
- Emit metrics:
  - Job lifecycle: created → processing → completed/failed/cancelled.
  - Step timings and success rates in `DubbingService`.
  - Queue metrics: receive count, processing latency, handler error rates.
- Wire to CloudWatch (custom metrics) or Prometheus endpoint (future).

### 11) Security & permissions
- Use IAM roles for EB instances (web and worker) with least-privilege policies:
  - S3 (bucket-scoped CRUD for `onevoice-videos`),
  - SQS (SendMessage for web; Receive/Delete/ChangeVisibility for worker),
  - SES: SendEmail,
  - SNS: Publish to the alerts topic.
- Encrypt data at rest (S3 SSE) and in transit (HTTPS, TLS for SMTP/SES).

### 12) Testing strategy
- Unit tests
  - Dispatcher enqueues valid SQS messages.
  - Consumer dispatches to correct handler; idempotency checks.
  - Notification service SES send path only (no SMTP).
  - Storage service presigned URL generation and key building.
- Integration tests
  - End-to-end flow: POST /api/videos/{id}/dub → SQS → worker → media files persisted → status updates.
  - Error handling: simulate step failure → job failed → email alert → DLQ on repeated failures.

### 13) Migration plan
- Phase 0 (local): `USE_SQS_TASK_QUEUE=False`; verify existing behavior intact.
- Phase 1 (staging): enable SQS path; deploy worker env; canary users/jobs; monitor metrics.
- Phase 2 (prod): enable SQS path; set DLQ/alarms; deprecate FastAPI BackgroundTasks path.

### 14) Work breakdown
- Queue layer (app/queue/*): 1–2 days
- Worker runtime (worker/*): 1–2 days
- API edit (`start_dubbing` enqueue): 0.5 day
- SES/SNS integration: 0.5–1 day
- Logging to CloudWatch: 0.5 day
- Infra (queues, DLQ, roles, alarms): 1–2 days
- Tests (unit + e2e): 1–2 days

### 15) Acceptance criteria
- Dubbing requests are acknowledged immediately and processed by the worker.
- Idempotent job handling; duplicate SQS deliveries do not corrupt state.
- Results (media files) persist to S3 and are downloadable via existing endpoints.
- Email notifications are sent via SES (or fallback SMTP) and operational alerts via SNS.
- Logs and key metrics visible in CloudWatch.

### 16) Message schema (example)
```json
{
  "messageType": "DUBBING_JOB",
  "jobId": "<uuid>",
  "userId": "<uuid>",
  "videoId": "<uuid>",
  "requestedAt": "2025-08-20T12:34:56Z"
}
```


