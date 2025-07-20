# FastAPI Backend Integration Guide

This guide provides comprehensive instructions for integrating your OneVoice frontend with a FastAPI backend.

## 📋 Required FastAPI Endpoints

Your FastAPI backend should implement these endpoints:

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/signup` - User registration
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/forgot-password` - Password reset request
- `POST /api/auth/reset-password` - Password reset confirmation

### User Management
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `GET /api/users/subscription` - Get subscription details
- `GET /api/users/dashboard/stats` - Get dashboard statistics

### Video Management
- `GET /api/videos` - List videos (with pagination, filtering, sorting)
- `GET /api/videos/{id}` - Get specific video
- `POST /api/videos` - Create video project
- `PUT /api/videos/{id}` - Update video
- `DELETE /api/videos/{id}` - Delete video
- `POST /api/videos/upload` - Upload video file
- `POST /api/videos/{id}/dub` - Start dubbing process
- `GET /api/videos/{id}/status` - Get processing status

### Billing
- `GET /api/billing/plans` - Get pricing plans
- `POST /api/billing/subscribe` - Subscribe to plan
- `GET /api/billing/subscription` - Get current subscription

## 🔧 Implementation Steps

### Step 1: Update Type Definitions

The existing types in `src/types/` have been extended with API-specific interfaces. Key additions:

- `src/types/api.ts` - Comprehensive API request/response types
- Extended existing types with API-compatible fields

### Step 2: HTTP Client Setup
The HTTP client (`src/lib/http-client.ts`) provides:

- Automatic JWT token management
- Token refresh handling
- Request/response interceptors
- Error handling with custom error types
- File upload support with progress tracking

### Step 3: Service Layer

Service classes provide typed API methods:

- `src/services/auth.service.ts` - Authentication operations
- `src/services/video.service.ts` - Video management
- `src/services/user.service.ts` - User profile and settings
- `src/services/billing.service.ts` - Subscription and billing

### Step 4: React Query Integration

Custom hooks for data fetching and mutations:

- `src/hooks/use-videos.ts` - Video-related queries and mutations
- `src/hooks/use-user.ts` - User-related queries and mutations
- Automatic caching, background updates, and optimistic updates

### Step 5: Authentication Context

The auth context (`src/contexts/auth-context.tsx`) provides:

- User authentication state
- Login/logout functionality
- Protected route handling
- Automatic token refresh

### Step 6: Error Handling & UX

Enhanced error handling and loading states:

- `src/components/ui/error-boundary.tsx` - React error boundaries
- `src/components/ui/error-display.tsx` - User-friendly error messages
- `src/components/ui/loading-states.tsx` - Loading indicators and skeletons

## 🎯 Page Integration Examples

### Dashboard Page

Key changes for dashboard integration:

```tsx
// Replace mock data imports
import { useVideos } from '@/hooks/use-videos'
import { useDashboardStats } from '@/hooks/use-user'

// Add authentication check
const { isAuthenticated, isLoading } = useRequireAuth()

// Use API queries instead of mock data
const { data: videosResponse, isLoading: videosLoading, error: videosError } = useVideos(params)
const { data: dashboardStats, isLoading: statsLoading } = useDashboardStats()

// Add loading and error states
if (videosLoading) return <VideoCardSkeleton />
if (videosError) return <ErrorDisplay error={videosError} onRetry={refetch} />
```

### Login Page

Key changes for login integration:

```tsx
// Use auth context
const { login, isLoading, isAuthenticated } = useAuth()

// Handle form submission with API
const handleSubmit = async (formData) => {
  try {
    await login(formData)
    // Navigation handled by auth context
  } catch (error) {
    setLoginError(queryErrorUtils.getErrorMessage(error))
  }
}
```

## 🔐 Authentication Flow

1. **Login**: User submits credentials → API returns JWT tokens → Stored in localStorage
2. **Protected Routes**: Auth context checks token validity → Redirects to login if invalid
3. **API Requests**: HTTP client automatically adds Bearer token to requests
4. **Token Refresh**: Automatic refresh when token expires (with 5-minute buffer)
5. **Logout**: Clear tokens and redirect to login

## 📊 State Management

React Query provides:

- **Caching**: Automatic caching with configurable stale times
- **Background Updates**: Refetch data when window regains focus
- **Optimistic Updates**: Immediate UI updates with rollback on error
- **Pagination**: Built-in pagination support
- **Real-time Updates**: Polling for processing status

## 🚨 Error Handling Strategy

1. **Network Errors**: Show retry button with connection status
2. **Authentication Errors**: Automatic logout and redirect to login
3. **Validation Errors**: Display field-specific error messages
4. **Server Errors**: User-friendly error messages with retry options
5. **Unexpected Errors**: Error boundary catches and displays fallback UI

## 🔄 Real-time Updates

For video processing status:

```tsx
const { data: status } = useVideoStatus(videoId, {
  refetchInterval: (data) => {
    // Poll every 5 seconds if processing
    return data?.status === 'processing' ? 5000 : false
  }
})
```

## 📱 File Upload

Enhanced file upload with progress:

```tsx
const uploadMutation = useUploadVideo()

const handleUpload = (file: File) => {
  uploadMutation.mutate({
    file,
    onProgress: (progress) => setUploadProgress(progress)
  })
}
```

## 🧪 Testing Considerations

1. **Error Scenarios**: Test network failures, authentication errors
2. **Loading States**: Verify loading indicators appear correctly
3. **Optimistic Updates**: Test rollback behavior on failures
4. **Component Testing**: Test components with mock data and providers

## 🚀 Deployment

1. **Environment Variables**: Set production API URL in deployment environment
2. **CORS**: Configure FastAPI to allow your frontend domain
3. **Security**: Use HTTPS in production for secure token transmission
4. **Monitoring**: Implement error tracking (Sentry, LogRocket, etc.)

## 📚 Next Steps

1. Replace mock data in remaining pages
2. Implement real-time notifications (WebSocket/SSE)
3. Add offline support with service workers
4. Implement advanced caching strategies
5. Add comprehensive error monitoring
6. Set up automated testing for API integration

## 🔗 Key Files Reference

- **Configuration**: `src/lib/config.ts`
- **HTTP Client**: `src/lib/http-client.ts`
- **Query Setup**: `src/lib/query-client.ts`
- **Auth Context**: `src/contexts/auth-context.tsx`
- **Providers**: `src/providers/app-providers.tsx`
- **API Types**: `src/types/api.ts`
- **Services**: `src/services/*.ts`
- **Hooks**: `src/hooks/*.ts`
- **UI Components**: `src/components/ui/error-*.tsx`, `src/components/ui/loading-*.tsx`