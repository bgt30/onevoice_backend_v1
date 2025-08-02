# Notifications API endpoints
# This file is reserved for notification-related endpoints
# Currently, notification preferences are handled in users.py
# Future endpoints for general notifications will be added here

from fastapi import APIRouter, HTTPException, Security, status

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


# Placeholder for future notification endpoints
# Example endpoints that might be added:
# - GET /api/notifications (get user notifications)
# - POST /api/notifications/mark-read (mark notifications as read)
# - DELETE /api/notifications/{id} (delete notification)

# Note: User notification preferences are handled in app.api.users 