## 백엔드 API 엔드포인트 목록

### 1. 인증 관련 엔드포인트 (Authentication)

```http
POST /api/auth/login
POST /api/auth/signup  
POST /api/auth/forgot-password
POST /api/auth/reset-password
POST /api/auth/logout
```

### 2. 사용자 관리 엔드포인트 (User Management)

```http
GET  /api/users/profile
PUT  /api/users/profile
PUT  /api/users/password
POST /api/users/avatar
DELETE /api/users/avatar
GET  /api/users/subscription
GET  /api/users/credits/usage
GET  /api/users/dashboard/stats
GET  /api/users/notifications/preferences
PUT  /api/users/notifications/preferences
GET  /api/users/activity
POST /api/users/delete-account
```

### 3. 결제 및 구독 엔드포인트 (Billing & Subscriptions)

```http
GET  /api/billing/plans
GET  /api/billing/subscription
POST /api/billing/subscribe
PUT  /api/billing/subscription
POST /api/billing/subscription/cancel
POST /api/billing/subscription/resume
GET  /api/billing/history?page={page}&perPage={perPage}
GET  /api/billing/upcoming-invoice
PUT  /api/billing/payment-method
GET  /api/billing/payment-methods
DELETE /api/billing/payment-methods/{id}
POST /api/billing/setup-intent
GET  /api/billing/usage
```

### 4. 비디오 관리 엔드포인트 (Video Management)

```http
GET  /api/videos
GET  /api/videos/{id}
POST /api/videos
PUT  /api/videos/{id}
DELETE /api/videos/{id}
POST /api/videos/upload-url
POST /api/videos/upload
POST /api/videos/{id}/dub          #`job_id` 반환 → 폴링으로 상태 추적
GET  /api/videos/{id}/status       #`job_id` 반환 → 폴링으로 상태 추적
POST /api/videos/{id}/cancel
GET  /api/videos/{id}/download
POST /api/videos/{id}/duplicate
POST /api/videos/{id}/thumbnail
GET  /api/videos/languages
GET  /api/videos/voices?language={languageCode}

```