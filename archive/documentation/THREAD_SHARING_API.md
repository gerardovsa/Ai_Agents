# Thread Sharing API Documentation

Complete API reference for multi-user thread collaboration.

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
4. [Error Codes](#error-codes)
5. [Workflows](#workflows)
6. [Testing](#testing)

---

## Overview

The Thread Sharing system enables multi-user collaboration on conversation threads. Users can:
- Share threads directly with other users
- Send email invitations to external users
- Accept share invitations via token
- Manage collaborator roles (viewer, editor, admin)
- Revoke access at any time
- View sharing history and audit trail

### Database Tables

**thread_users** - Active thread collaborators
- `id` - Unique record ID
- `thread_id` - Thread reference
- `user_id` - User with access
- `role` - Access role (viewer/editor/admin)
- `access_level` - Permission level (read/read_write/full)
- `added_by_user_id` - Who granted access
- `added_at` - Grant timestamp
- `removed_at` - Revocation timestamp (NULL if active)
- `last_accessed_at` - Last access timestamp
- `metadata` - JSON metadata

**thread_shares** - Complete sharing audit trail
- `id` - Unique record ID
- `thread_id` - Thread reference
- `shared_by_user_id` - User who shared
- `shared_with_user_id` - Recipient user ID (NULL for email invites)
- `shared_with_email` - Recipient email (NULL for direct shares)
- `share_type` - Type (direct/email)
- `action` - Action (added/updated/invited/revoked)
- `role_granted` - Role assigned
- `share_token` - Invitation token (NULL for direct)
- `share_link` - Invitation URL (NULL for direct)
- `created_at` - Action timestamp
- `expires_at` - Token expiration (NULL if no expiry)
- `accessed_at` - Token use timestamp
- `revoked_at` - Revocation timestamp
- `revoked_by_user_id` - Who revoked
- `revoke_reason` - Revocation reason
- `metadata` - JSON metadata

---

## Authentication

All endpoints require authentication. Include user credentials via:

**Session-based:**
```bash
# Login first, then requests use session cookie
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

**Request body (for testing):**
```json
{
  "_user_id": 1,
  "other_params": "..."
}
```

---

## Endpoints

### 1. Share Thread (Direct)

Share thread with an existing user.

**Endpoint:** `POST /api/threads/<thread_slug>/share`

**Request:**
```json
{
  "shared_with_user_id": 5,
  "role": "viewer"
}
```

**Parameters:**
- `shared_with_user_id` (integer, required) - User ID to share with
- `role` (string, optional) - Access role: `viewer`, `editor`, or `admin` (default: `viewer`)

**Response:**
```json
{
  "success": true,
  "share_id": 1,
  "thread_user_id": 12,
  "thread_slug": "proj-alpha",
  "thread_id": 5,
  "shared_with_user_id": 5,
  "role": "viewer",
  "action": "added",
  "shared_at": "2025-11-10T10:30:00"
}
```

**Status Codes:**
- `200` - Success
- `400` - Missing required parameters
- `401` - Authentication required
- `403` - Permission denied (not owner/admin)
- `404` - Thread not found
- `500` - Server error

**cURL Example:**
```bash
curl -X POST http://localhost:5001/api/threads/proj-alpha/share \
  -H "Content-Type: application/json" \
  -d '{
    "shared_with_user_id": 5,
    "role": "editor",
    "_user_id": 1
  }'
```

---

### 2. Share Thread (Email Invitation)

Send email invitation to share thread.

**Endpoint:** `POST /api/threads/<thread_slug>/share-email`

**Request:**
```json
{
  "email": "user@example.com",
  "role": "viewer"
}
```

**Parameters:**
- `email` (string, required) - Email address to invite
- `role` (string, optional) - Access role (default: `viewer`)

**Response:**
```json
{
  "success": true,
  "share_id": 2,
  "thread_slug": "proj-alpha",
  "thread_id": 5,
  "invited_email": "user@example.com",
  "role": "viewer",
  "share_token": "m8cE1czkSl6fPcbg74kc7q7sQRrjxnM3WVzu_AeEl_U",
  "expires_at": "2025-11-17T10:30:00",
  "share_link": "/accept-thread-share/m8cE1czkSl6fPcbg74kc7q7sQRrjxnM3WVzu_AeEl_U"
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid email
- `401` - Authentication required
- `403` - Permission denied
- `404` - Thread not found
- `500` - Server error

**cURL Example:**
```bash
curl -X POST http://localhost:5001/api/threads/proj-alpha/share-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "colleague@example.com",
    "role": "editor",
    "_user_id": 1
  }'
```

---

### 3. Accept Thread Share

Accept a thread share invitation.

**Endpoint:** `POST /api/thread-shares/accept/<token>`

**Request:**
```json
{
  "_user_id": 5
}
```

**Response:**
```json
{
  "success": true,
  "thread_user_id": 12,
  "thread_id": 5,
  "thread_slug": "proj-alpha",
  "thread_title": "Project Alpha Discussion",
  "role": "viewer",
  "access_level": "read"
}
```

**Status Codes:**
- `200` - Success
- `401` - Authentication required
- `404` - Invalid or expired token
- `500` - Server error

**cURL Example:**
```bash
curl -X POST http://localhost:5001/api/thread-shares/accept/m8cE1czkSl6fPcbg74kc7q7sQRrjxnM3WVzu_AeEl_U \
  -H "Content-Type: application/json" \
  -d '{"_user_id": 5}'
```

---

### 4. Revoke Thread Share

Revoke user's access to thread.

**Endpoint:** `DELETE /api/threads/<thread_slug>/share/<user_id>`

**Request (optional):**
```json
{
  "reason": "Access no longer needed"
}
```

**Response:**
```json
{
  "success": true,
  "thread_slug": "proj-alpha",
  "revoked_user_id": 5,
  "revoked_by": 1,
  "revoked_at": "2025-11-10T14:30:00"
}
```

**Status Codes:**
- `200` - Success
- `401` - Authentication required
- `403` - Permission denied
- `404` - Thread or user not found
- `500` - Server error

**cURL Example:**
```bash
curl -X DELETE http://localhost:5001/api/threads/proj-alpha/share/5 \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Project completed",
    "_user_id": 1
  }'
```

---

### 5. List Thread Collaborators

Get all users with access to thread.

**Endpoint:** `GET /api/threads/<thread_slug>/collaborators`

**Response:**
```json
{
  "success": true,
  "thread_slug": "proj-alpha",
  "collaborators": [
    {
      "id": 12,
      "user_id": 5,
      "username": "john_doe",
      "email": "john@example.com",
      "role": "viewer",
      "access_level": "read",
      "added_at": "2025-11-10T10:30:00",
      "last_accessed_at": "2025-11-10T12:00:00"
    },
    {
      "id": 13,
      "user_id": 8,
      "username": "jane_smith",
      "email": "jane@example.com",
      "role": "editor",
      "access_level": "read_write",
      "added_at": "2025-11-09T15:00:00",
      "last_accessed_at": null
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `401` - Authentication required
- `403` - No access to thread
- `404` - Thread not found
- `500` - Server error

**cURL Example:**
```bash
curl http://localhost:5001/api/threads/proj-alpha/collaborators \
  --cookie "session=..."
```

---

### 6. List My Shared Threads

Get threads shared with current user.

**Endpoint:** `GET /api/my-shared-threads`

**Response:**
```json
{
  "success": true,
  "shared_threads": [
    {
      "thread_id": 5,
      "thread_slug": "proj-alpha",
      "title": "Project Alpha Discussion",
      "owner_id": 1,
      "owner_username": "alice",
      "my_role": "viewer",
      "my_access_level": "read",
      "shared_at": "2025-11-10T10:30:00",
      "updated_at": "2025-11-10T12:00:00"
    },
    {
      "thread_id": 8,
      "thread_slug": "team-meeting",
      "title": "Weekly Team Meeting",
      "owner_id": 3,
      "owner_username": "bob",
      "my_role": "editor",
      "my_access_level": "read_write",
      "shared_at": "2025-11-08T09:00:00",
      "updated_at": "2025-11-09T16:30:00"
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `401` - Authentication required
- `500` - Server error

**cURL Example:**
```bash
curl http://localhost:5001/api/my-shared-threads \
  --cookie "session=..."
```

---

## Error Codes

### 400 Bad Request
```json
{
  "success": false,
  "error": "shared_with_user_id required"
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "success": false,
  "error": "You don't have permission to share this thread"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "Thread proj-alpha not found"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Internal server error: database connection failed"
}
```

---

## Workflows

### Workflow 1: Direct User Sharing

1. **List available users** (optional)
   ```bash
   GET /api/auth/users
   ```

2. **Share thread**
   ```bash
   POST /api/threads/proj-alpha/share
   Body: {"shared_with_user_id": 5, "role": "editor"}
   ```

3. **Verify in collaborators list**
   ```bash
   GET /api/threads/proj-alpha/collaborators
   ```

4. **Shared user sees thread in their list**
   ```bash
   GET /api/my-shared-threads
   ```

### Workflow 2: Email Invitation

1. **Send invitation**
   ```bash
   POST /api/threads/proj-alpha/share-email
   Body: {"email": "user@example.com", "role": "viewer"}
   ```

2. **Copy share link from response**
   ```json
   "share_link": "/accept-thread-share/TOKEN"
   ```

3. **User visits link and accepts**
   ```bash
   POST /api/thread-shares/accept/TOKEN
   ```

4. **User is redirected to thread**

### Workflow 3: Access Revocation

1. **List current collaborators**
   ```bash
   GET /api/threads/proj-alpha/collaborators
   ```

2. **Revoke user's access**
   ```bash
   DELETE /api/threads/proj-alpha/share/5
   ```

3. **Verify removal**
   ```bash
   GET /api/threads/proj-alpha/collaborators
   # User 5 no longer in list
   ```

---

## Testing

### Test Script

Run complete backend tests:
```bash
cd c:\Users\gpoli\GIT\AI_agents
python scripts/testing/test_thread_sharing.py
```

### Manual API Testing

1. **Start server:**
   ```powershell
   BISTART
   ```

2. **Share thread:**
   ```bash
   curl -X POST http://localhost:5001/api/threads/1762663889170/share \
     -H "Content-Type: application/json" \
     -d '{"shared_with_user_id": 13, "role": "viewer", "_user_id": 12}'
   ```

3. **List collaborators:**
   ```bash
   curl http://localhost:5001/api/threads/1762663889170/collaborators?_user_id=12
   ```

4. **Send email invite:**
   ```bash
   curl -X POST http://localhost:5001/api/threads/1762663889170/share-email \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "role": "editor", "_user_id": 12}'
   ```

### Expected Results

All requests should return `"success": true` with appropriate data. Check database tables:

```sql
-- Active collaborators
SELECT * FROM thread_users WHERE removed_at IS NULL;

-- Sharing history
SELECT * FROM thread_shares ORDER BY created_at DESC;
```

---

## Role Permissions

| Role | View Thread | Add Messages | Edit Messages | Delete Messages | Manage Sharing | Delete Thread |
|------|------------|--------------|---------------|-----------------|----------------|---------------|
| **viewer** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **editor** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **owner** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Security Considerations

1. **Token Security:**
   - Share tokens are 32-byte URL-safe random strings
   - Tokens expire after 7 days by default
   - One-time use (marked accessed on first use)

2. **Permission Checks:**
   - Only thread owner or admins can share threads
   - Only owner or admins can revoke access
   - All operations verify user authentication

3. **Audit Trail:**
   - All sharing events recorded in `thread_shares`
   - Includes who shared, when, and reason for revocation
   - Soft deletes (removed_at) preserve history

4. **Data Privacy:**
   - Users only see threads they own or have access to
   - Collaborator lists only visible to thread members
   - Email invitations don't expose user data

---

## Support

For issues or questions:
- Backend code: `AI_infrastructure/threads/thread_sharing_manager.py`
- API routes: `AI_infrastructure/routes/thread_sharing_routes.py`
- Frontend UI: `UI/components/ThreadSharingModal.jsx`
- Tests: `scripts/testing/test_thread_sharing.py`

**Last Updated:** November 10, 2025  
**API Version:** 1.0.0  
**Status:** Production Ready
