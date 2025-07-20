# Role-Based Access Control (RBAC) Implementation Guide

## Overview

This document provides a comprehensive guide to the Role-Based Access Control (RBAC) system implemented in the OneVoice Backend API. The RBAC system ensures that users can only access resources and perform actions that are appropriate for their assigned roles.

## Architecture

### Core Components

1. **User Roles**: Defined in `app/models/user.py`
2. **Dependencies**: Authorization functions in `app/api/deps.py`
3. **Permissions**: Permission mapping in `app/core/security.py`
4. **Middleware**: Security middleware in `app/middleware/rbac.py`

### User Roles

The system defines three primary user roles:

```python
class UserRole(enum.Enum):
    admin = "admin"      # Full system access
    user = "user"        # Standard user access
    guest = "guest"      # Limited read-only access
```

### Permission Matrix

| Role  | Permissions |
|-------|-------------|
| **Admin** | `users:read`, `users:write`, `users:delete`, `videos:read`, `videos:write`, `videos:delete`, `jobs:read`, `jobs:write`, `jobs:delete`, `analytics:read`, `system:manage` |
| **User** | `profile:read`, `profile:write`, `videos:read`, `videos:write`, `videos:delete_own`, `jobs:read_own`, `jobs:write_own` |
| **Guest** | `profile:read` |

## Implementation

### 1. Role-Based Dependencies

Use these dependencies to protect endpoints based on user roles:

```python
from app.api.deps import require_admin, require_user, require_any_authenticated

# Admin-only endpoint
@router.get("/admin-panel")
def admin_panel(current_user: User = Depends(require_admin)):
    return {"message": "Admin access granted"}

# User or admin access
@router.get("/user-dashboard") 
def user_dashboard(current_user: User = Depends(require_user)):
    return {"message": "User access granted"}

# Any authenticated user
@router.get("/profile")
def get_profile(current_user: User = Depends(require_any_authenticated)):
    return {"user": current_user}
```

### 2. Permission-Based Dependencies

Use these dependencies for fine-grained permission control:

```python
from app.api.deps import require_user_read, require_video_write

# Requires users:read permission
@router.get("/user-stats")
def get_user_stats(current_user: User = Depends(require_user_read)):
    return {"stats": "..."}

# Requires videos:write permission  
@router.post("/videos")
def create_video(current_user: User = Depends(require_video_write)):
    return {"message": "Video created"}
```

### 3. Custom Role Checkers

Create custom role requirements:

```python
from app.api.deps import RoleChecker

# Custom role requirement
require_admin_or_moderator = RoleChecker([UserRole.admin, UserRole.moderator])

@router.get("/moderation")
def moderation_panel(current_user: User = Depends(require_admin_or_moderator)):
    return {"message": "Moderation access granted"}
```

### 4. Resource Ownership Protection

Protect resources so users can only access their own data:

```python
from app.api.deps import require_owner_or_admin

@router.get("/videos/{video_id}")
def get_video(
    video_id: str,
    current_user: User = Depends(require_owner_or_admin(video_owner_id))
):
    # User can only access their own videos, or admin can access any
    return {"video": "..."}
```

### 5. Using Dependencies Parameter

Keep endpoint logic clean by using the `dependencies` parameter:

```python
# Clean endpoint - authorization handled by dependency
@router.get("/admin-only", dependencies=[Depends(require_admin)])
def admin_endpoint():
    return {"detail": "Admin access granted"}

# Multiple dependencies
@router.post("/secure-action", dependencies=[
    Depends(require_admin),
    Depends(validate_csrf_token),
    Depends(check_rate_limit)
])
def secure_action():
    return {"detail": "Action completed"}
```

## Security Features

### 1. JWT Token Validation

All protected endpoints automatically validate JWT tokens:

- Token signature verification
- Expiration checking  
- Blacklist verification
- Role and permission extraction

### 2. Rate Limiting

Authentication endpoints are protected with rate limiting:

- Login: 5 attempts per 5 minutes
- Signup: 3 attempts per hour  
- Password reset: 3 attempts per hour

### 3. Security Headers

Automatic security headers on all responses:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`

### 4. Audit Logging

All authentication and authorization events are logged:

- Successful logins
- Failed authentication attempts
- Authorization failures
- Rate limit violations

## Error Handling

### HTTP Status Codes

| Status | Meaning | When Used |
|--------|---------|-----------|
| `401 Unauthorized` | Invalid or missing authentication | No token, invalid token, expired token |
| `403 Forbidden` | Insufficient permissions | User lacks required role or permission |
| `429 Too Many Requests` | Rate limit exceeded | Too many auth attempts |

### Error Response Format

```json
{
    "detail": "Not enough permissions"
}
```

## Testing

### Running RBAC Tests

```bash
# Run all RBAC tests
pytest tests/test_rbac.py -v

# Run specific test classes
pytest tests/test_rbac.py::TestRoleChecker -v

# Run with coverage
pytest tests/test_rbac.py --cov=app.api.deps --cov=app.middleware
```

### Test Categories

1. **Unit Tests**: Test individual dependencies and functions
2. **Integration Tests**: Test full endpoint access patterns
3. **Security Tests**: Test authorization edge cases and attacks

## Configuration

### Environment Variables

Add to your `.env` file:

```env
# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Security Settings  
ENABLE_RATE_LIMITING=true
ENABLE_SECURITY_HEADERS=true
ENABLE_AUDIT_LOGGING=true
```

### Middleware Configuration

Enable RBAC middleware in your main app:

```python
from app.middleware import configure_rbac_middleware

# Configure middleware
configure_rbac_middleware(
    app,
    enable_rate_limiting=True,
    enable_logging=True,
    enable_security_headers=True
)
```

## Best Practices

### 1. Use Dependencies, Not Manual Checks

❌ **Don't do this:**
```python
@router.get("/admin")
def admin_endpoint(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.admin:
        raise HTTPException(403, "Not admin")
    return {"data": "..."}
```

✅ **Do this:**
```python
@router.get("/admin")
def admin_endpoint(current_user: User = Depends(require_admin)):
    return {"data": "..."}
```

### 2. Use Permission-Based Access When Possible

❌ **Role-based (less flexible):**
```python
@router.get("/users", dependencies=[Depends(require_admin)])
def get_users():
    return {"users": "..."}
```

✅ **Permission-based (more flexible):**
```python
@router.get("/users", dependencies=[Depends(require_user_read)])
def get_users():
    return {"users": "..."}
```

### 3. Don't Expose Sensitive Information in Errors

❌ **Don't do this:**
```python
raise HTTPException(403, f"User {user.email} lacks admin role")
```

✅ **Do this:**
```python
raise HTTPException(403, "Not enough permissions")
```

### 4. Validate Resource Ownership

Always check that users can only access their own resources:

```python
@router.get("/videos/{video_id}")
def get_video(
    video_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    video = db.query(Video).filter(Video.id == video_id).first()
    
    # Check ownership or admin privileges
    if video.owner_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(403, "Not enough permissions")
    
    return video
```

## Troubleshooting

### Common Issues

1. **ImportError with dependencies**
   - Ensure all imports are correct in `app/api/deps.py`
   - Check that `UserRole` is imported where needed

2. **Tests failing with token errors**
   - Verify `SECRET_KEY` is set in test environment
   - Check that test tokens are created correctly

3. **Rate limiting not working**
   - Ensure middleware is configured
   - Check that Redis is running (if using Redis for rate limiting)

### Debug Mode

Enable debug logging for RBAC events:

```python
import logging
logging.getLogger("app.middleware.rbac").setLevel(logging.DEBUG)
```

## Migration from Previous Systems

If migrating from a system without RBAC:

1. **Add role column** to user table
2. **Set default role** for existing users
3. **Update endpoints** to use new dependencies
4. **Test thoroughly** with different user roles
5. **Deploy gradually** with feature flags

## Security Considerations

1. **Token Storage**: Store JWT tokens securely on client side
2. **HTTPS Only**: Always use HTTPS in production
3. **Token Expiration**: Use short-lived access tokens
4. **Refresh Tokens**: Implement secure refresh token rotation
5. **Audit Logs**: Monitor and review authentication logs regularly
6. **Principle of Least Privilege**: Give users minimum required permissions

## API Documentation

The RBAC system integrates with OpenAPI/Swagger documentation. Security requirements are automatically documented for each endpoint based on the dependencies used.

Visit `/docs` to see the interactive API documentation with security requirements clearly marked.

## Support

For questions or issues with the RBAC system:

1. Check this documentation first
2. Review the test cases in `tests/test_rbac.py` for examples
3. Check the implementation in `app/api/deps.py`
4. Create an issue with detailed error information

## Changelog

- **v1.0.0**: Initial RBAC implementation with roles and permissions
- **v1.1.0**: Added middleware for rate limiting and security headers
- **v1.2.0**: Added comprehensive test suite and documentation 