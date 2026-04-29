# 🔒 Vector Database Authentication Integration - Complete Implementation Plan

**Date**: December 7, 2025  
**Status**: ⚠️ **SUPERSEDED — See `.github/VECTOR_DB_ORG_ALIGNMENT_ANALYSIS_APR29_2026.md`**  
**Original Target Complexity**: Medium (4-6 hours)  
**Risk Level**: Low (backward compatible, additive changes)

> **NOTE (April 29, 2026):** This document identified the auth gap correctly but was never implemented.  
> The full updated analysis — covering auth, org credential resolver, namespace isolation, Settings tab  
> retirement, and module gating — is documented in:  
> **`.github/VECTOR_DB_ORG_ALIGNMENT_ANALYSIS_APR29_2026.md`** (GAP-V1 through GAP-V8).  
> Implement from that document, not this one.

---

## 📋 Executive Summary

### Current State (BROKEN)
- ❌ No authentication on vector database API requests
- ❌ Uses query parameter `user_id=1` instead of JWT tokens
- ❌ Security vulnerability: users can access other users' credentials
- ❌ window.currentUserId not reliably set
- ❌ Duplicate code (legacy.js has auth, modern doesn't)

### Target State (SECURE)
- ✅ All API requests authenticated with JWT Bearer tokens
- ✅ Backend validates tokens via `@require_auth` decorator
- ✅ User ID extracted from JWT, not query params
- ✅ Auto-refresh on 401 Unauthorized
- ✅ Single source of truth (remove legacy file)

---

## 🗺️ Implementation Pathway

### CHECKPOINT 1: Frontend Authentication Layer (2 hours)

#### Step 1.1: Update ModuleLoaderV4 API Utility
**File**: `UI/shared/js/module-utilities.js`  
**Goal**: Add automatic JWT token injection to all API requests

```javascript
// BEFORE (line 370-400):
api: {
    get: async (url) => {
        const response = await fetch(url);
        return response.json();
    },
    post: async (url, data) => {
        const response = await fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        return response.json();
    }
}

// AFTER (add authentication):
api: {
    _getAuthHeaders() {
        const token = localStorage.getItem('authToken') || 
                     sessionStorage.getItem('authToken');
        return {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : ''
        };
    },
    
    async get(url) {
        const response = await fetch(url, {
            headers: this._getAuthHeaders()
        });
        
        // Handle 401 Unauthorized
        if (response.status === 401) {
            console.warn('[API] Unauthorized - redirecting to login');
            window.location.href = '/login';
            throw new Error('Unauthorized');
        }
        
        return response.json();
    },
    
    async post(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: this._getAuthHeaders(),
            body: JSON.stringify(data)
        });
        
        if (response.status === 401) {
            console.warn('[API] Unauthorized - redirecting to login');
            window.location.href = '/login';
            throw new Error('Unauthorized');
        }
        
        return response.json();
    },
    
    async delete(url, data) {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: this._getAuthHeaders(),
            body: data ? JSON.stringify(data) : undefined
        });
        
        if (response.status === 401) {
            window.location.href = '/login';
            throw new Error('Unauthorized');
        }
        
        return response.json();
    }
}
```

**Tests**:
- ✅ Verify Authorization header sent on all requests
- ✅ Verify 401 redirects to login page
- ✅ Verify token retrieved from localStorage/sessionStorage

---

#### Step 1.2: Update Vector Database Module
**File**: `UI/modules_internal/vector_database/vector_database.js`  
**Goal**: Remove `user_id` query parameters, rely on JWT

**Changes**:

```javascript
// LINE 218 - loadCredentials()
// BEFORE:
async loadCredentials() {
    const response = await this.api.get(
        `${this.state.API_BASE_URL}/api/vector-db/credentials/get?user_id=${window.currentUserId || 1}`
    );
}

// AFTER:
async loadCredentials() {
    const response = await this.api.get(
        `${this.state.API_BASE_URL}/api/vector-db/credentials/get`
    );
    // Backend extracts user_id from JWT token
}

// LINE 247 - loadEmbeddingConfig()
// BEFORE:
const response = await this.api.get(
    `${this.state.API_BASE_URL}/api/vector-db/embedding-config/get?user_id=${window.currentUserId || 1}`
);

// AFTER:
const response = await this.api.get(
    `${this.state.API_BASE_URL}/api/vector-db/embedding-config/get`
);

// LINE 285 - testConnection()
// BEFORE:
const response = await this.api.post(`${this.state.API_BASE_URL}/api/vector-db/test-connection`, {
    user_id: window.currentUserId || 1
});

// AFTER:
const response = await this.api.post(`${this.state.API_BASE_URL}/api/vector-db/test-connection`, {});

// LINE 357 - saveEmbeddingConfig()
// BEFORE:
const response = await this.api.post(`${this.state.API_BASE_URL}/api/vector-db/embedding-config/save`, {
    user_id: window.currentUserId || 1,
    provider: provider,
    ...
});

// AFTER:
const response = await this.api.post(`${this.state.API_BASE_URL}/api/vector-db/embedding-config/save`, {
    provider: provider,
    // user_id extracted from JWT by backend
    ...
});

// LINE 466 - processFiles()
// BEFORE:
formData.append('user_id', window.currentUserId || 1);

// AFTER:
// Remove user_id from formData - backend gets it from JWT

// LINE 537 - loadStats()
// BEFORE:
const response = await this.api.get(
    `${this.state.API_BASE_URL}/api/vector-db/stats?user_id=${window.currentUserId || 1}`
);

// AFTER:
const response = await this.api.get(
    `${this.state.API_BASE_URL}/api/vector-db/stats`
);

// LINE 578 - loadDocuments()
// BEFORE:
const response = await this.api.get(
    `${this.state.API_BASE_URL}/api/vector-db/documents?user_id=${window.currentUserId || 1}&include_metadata=true&include_cloud_links=true`
);

// AFTER:
const response = await this.api.get(
    `${this.state.API_BASE_URL}/api/vector-db/documents?include_metadata=true&include_cloud_links=true`
);

// LINE 652 - deleteDocument()
// BEFORE:
const response = await this.api.delete(
    `${this.state.API_BASE_URL}/api/vector-db/document/${docId}`,
    { user_id: window.currentUserId || 1 }
);

// AFTER:
const response = await this.api.delete(
    `${this.state.API_BASE_URL}/api/vector-db/document/${docId}`
);
```

**Count**: 9 locations to update

**Tests**:
- ✅ Load credentials without user_id param
- ✅ Save credentials
- ✅ Upload document
- ✅ List documents
- ✅ Delete document
- ✅ Load stats

---

#### Step 1.3: Remove Legacy File
**Action**: Delete `UI/modules_internal/vector_database/vector_database.legacy.js`

**Reason**: 
- Modern version now has proper authentication
- Duplicate code causes confusion
- Legacy file not referenced in module loader

---

### CHECKPOINT 2: Backend Authentication Enforcement (1.5 hours)

#### Step 2.1: Add @require_auth Decorators
**File**: `AI_infrastructure/routes/vector_db_routes.py`  
**Goal**: Enforce JWT validation on all endpoints

```python
# LINE 1 - Add import
from AI_infrastructure.auth.user_auth import require_auth

# Update all endpoint functions:

@vector_db_bp.route('/api/vector-db/upload-document', methods=['POST'])
@require_auth  # ← ADD THIS
def upload_document():
    user_id = request.user['id']  # ← From JWT, not query param
    # ... rest of function ...

@vector_db_bp.route('/api/vector-db/documents', methods=['GET'])
@require_auth  # ← ADD THIS
def list_documents():
    user_id = request.user['id']  # ← From JWT
    # Remove: user_id = request.args.get('user_id', 1, type=int)

@vector_db_bp.route('/api/vector-db/stats', methods=['GET'])
@require_auth  # ← ADD THIS
def get_stats():
    user_id = request.user['id']  # ← From JWT

@vector_db_bp.route('/api/vector-db/credentials/get', methods=['GET'])
@require_auth  # ← ADD THIS
def get_credentials():
    user_id = request.user['id']  # ← From JWT
    # Remove: user_id = request.args.get('user_id', type=int)

@vector_db_bp.route('/api/vector-db/credentials/save', methods=['POST'])
@require_auth  # ← ADD THIS
def save_credentials():
    user_id = request.user['id']  # ← From JWT
    # Remove: user_id = data.get('user_id')

@vector_db_bp.route('/api/vector-db/embedding-config/get', methods=['GET'])
@require_auth  # ← ADD THIS
def get_embedding_config():
    user_id = request.user['id']  # ← From JWT

@vector_db_bp.route('/api/vector-db/embedding-config/save', methods=['POST'])
@require_auth  # ← ADD THIS
def save_embedding_config():
    user_id = request.user['id']  # ← From JWT
    # Remove: user_id = data.get('user_id')
```

**Count**: 8 endpoints to secure

---

#### Step 2.2: Update Form Data Handling
**File**: `AI_infrastructure/routes/vector_db_routes.py`  
**Line**: 207 (upload_document function)

```python
# BEFORE:
user_id = request.form.get('user_id', 1, type=int)

# AFTER:
user_id = request.user['id']  # From @require_auth decorator
```

---

### CHECKPOINT 3: Database Credential Security (1 hour)

#### Step 3.1: Verify Credential Encryption
**File**: `AI_infrastructure/auth/credential_encryptor.py`  
**Goal**: Ensure all vector DB credentials are encrypted at rest

**Verification Steps**:
1. Run SQL query to check encryption status:
```sql
SELECT 
    user_id,
    platform,
    LENGTH(credential_value) as value_length,
    LEFT(credential_value, 20) as preview
FROM ai_infrastructure.user_platform_credentials
WHERE platform IN ('pinecone', 'voyager', 'openai_embeddings')
AND user_id = 1;
```

2. Expected results:
   - Value should NOT be plain API key
   - Should be encrypted string (Fernet format)
   - Length > original key length

3. If not encrypted, run:
```bash
cd C:\Users\gpoli\GIT\AI_agents
python AI_infrastructure/auth/migrate_to_encrypted_credentials.py
```

---

#### Step 3.2: Add Credential Rotation Reminder
**File**: `AI_infrastructure/auth/user_auth.py`  
**Goal**: Track last validation timestamp

```python
# In get_platform_credentials() function, add after successful retrieval:

# Update last_validated_at timestamp
cursor.execute('''
    UPDATE ai_infrastructure.user_platform_credentials
    SET last_validated_at = CURRENT_TIMESTAMP,
        validation_status = 'valid'
    WHERE user_id = %s AND platform = %s
''', (user_id, platform))
conn.commit()
```

---

### CHECKPOINT 4: Error Handling & User Experience (1 hour)

#### Step 4.1: Add Connection Status Banner
**File**: `UI/modules_internal/vector_database/vector_database.js`  
**Goal**: Show clear authentication status

```javascript
// Add to onSidebarLoad() after loadCredentials():
async onSidebarLoad(utilities) {
    // ... existing code ...
    
    try {
        await this.loadCredentials();
        this.showConnectedBanner();
    } catch (error) {
        if (error.message === 'Unauthorized') {
            this.showAuthenticationError();
        } else {
            this.showDisconnectedBanner();
        }
    }
}

showAuthenticationError() {
    const banner = this.container.querySelector('#credential-status-banner');
    if (banner) {
        banner.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <i class="fas fa-exclamation-triangle" style="color: #F59E0B;"></i>
                <div>
                    <div style="font-weight: 600; color: #92400E;">
                        Authentication Required
                    </div>
                    <div style="font-size: 12px; color: #92400E;">
                        Please log in to access vector database features.
                    </div>
                </div>
            </div>
            <button onclick="window.location.href='/login'" 
                style="width: 100%; margin-top: 10px; padding: 8px; 
                       background: #F59E0B; color: white; border: none; 
                       border-radius: 6px; cursor: pointer;">
                <i class="fas fa-sign-in-alt"></i> Log In
            </button>
        `;
        banner.style.background = '#FFF3CD';
        banner.style.borderLeft = '4px solid #FFC107';
        banner.style.display = 'block';
    }
}
```

---

#### Step 4.2: Add Retry Logic for Token Refresh
**File**: `UI/shared/js/module-utilities.js`

```javascript
api: {
    async _refreshTokenIfNeeded() {
        // Check token expiry
        const token = localStorage.getItem('authToken');
        if (!token) return false;
        
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const exp = payload.exp * 1000; // Convert to ms
            const now = Date.now();
            
            // Refresh if less than 5 minutes remaining
            if (exp - now < 5 * 60 * 1000) {
                console.log('[API] Token expiring soon, refreshing...');
                const response = await fetch('/api/auth/refresh', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem('authToken', data.token);
                    console.log('[API] Token refreshed successfully');
                    return true;
                }
            }
            return true;
        } catch (error) {
            console.error('[API] Token refresh failed:', error);
            return false;
        }
    },
    
    async get(url) {
        await this._refreshTokenIfNeeded();
        // ... rest of get() implementation ...
    }
}
```

---

### CHECKPOINT 5: Testing & Validation (1 hour)

#### Step 5.1: Manual Testing Checklist

**Prerequisites**:
1. ✅ User logged in (valid JWT token in localStorage)
2. ✅ Credentials exist in database for user_id=1
3. ✅ Backend server running (BISTART)
4. ✅ Browser console open for debugging

**Test Cases**:

**Test 1: Load Credentials**
```
1. Open Vector Database sidebar
2. Check browser network tab:
   ✅ Request has Authorization header
   ✅ No user_id query parameter
   ✅ Response 200 OK with credentials
3. Verify UI shows:
   ✅ Green "Connected" banner
   ✅ Masked API key (****last8chars)
   ✅ Index name populated
   ✅ Environment populated
```

**Test 2: Save Credentials**
```
1. Enter new Pinecone API key
2. Click "Save Credentials"
3. Check network tab:
   ✅ POST request has Authorization header
   ✅ No user_id in request body
   ✅ Response 200 OK
4. Verify database:
   SELECT * FROM ai_infrastructure.user_platform_credentials
   WHERE user_id = 1 AND platform = 'pinecone';
   ✅ Credential updated
   ✅ updated_at timestamp changed
```

**Test 3: Upload Document**
```
1. Select PDF file
2. Click "Process and Upload"
3. Check network tab:
   ✅ FormData has Authorization header
   ✅ No user_id in FormData
   ✅ Response 200 OK with vectors_uploaded count
4. Verify Pinecone:
   ✅ Vectors created in namespace
   ✅ Metadata includes user_id from JWT
```

**Test 4: Unauthorized Access**
```
1. Delete authToken from localStorage
2. Refresh page
3. Open Vector Database sidebar
4. Verify:
   ✅ Request returns 401 Unauthorized
   ✅ Redirects to /login page
   ✅ Error message displayed
```

**Test 5: Token Expiry**
```
1. Manually expire JWT token (edit exp claim)
2. Try to load credentials
3. Verify:
   ✅ 401 Unauthorized response
   ✅ Auto-redirect to login
   ✅ Session cleared
```

---

#### Step 5.2: Automated Tests

**File**: `tests/test_vector_db_auth.py` (NEW)

```python
import pytest
from flask import Flask
from AI_infrastructure.routes.vector_db_routes import vector_db_bp
from AI_infrastructure.auth.user_auth import UserAuthManager

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(vector_db_bp)
    return app.test_client()

@pytest.fixture
def auth_headers():
    auth_manager = UserAuthManager()
    token = auth_manager.generate_jwt({'id': 1, 'username': 'test', 'email': 'test@test.com', 'role': 'admin'})
    return {'Authorization': f'Bearer {token}'}

def test_get_credentials_requires_auth(client):
    """Test that credentials endpoint requires authentication"""
    response = client.get('/api/vector-db/credentials/get')
    assert response.status_code == 401

def test_get_credentials_with_auth(client, auth_headers):
    """Test successful credential retrieval"""
    response = client.get('/api/vector-db/credentials/get', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'credentials' in data

def test_save_credentials_requires_auth(client):
    """Test that save endpoint requires authentication"""
    response = client.post('/api/vector-db/credentials/save', json={'api_key': 'test'})
    assert response.status_code == 401

def test_user_cannot_access_other_users_credentials(client):
    """Test that user_id from JWT is enforced"""
    # Create token for user 1
    auth_manager = UserAuthManager()
    token = auth_manager.generate_jwt({'id': 1, 'username': 'user1', 'email': 'user1@test.com', 'role': 'user'})
    
    # Try to access user 2's credentials (should fail even if param provided)
    response = client.get('/api/vector-db/credentials/get?user_id=2', 
                         headers={'Authorization': f'Bearer {token}'})
    
    # Should return user 1's credentials, not user 2's
    data = response.get_json()
    # Backend should ignore query param and use JWT user_id
    # This test verifies the security fix
```

**Run tests**:
```bash
cd C:\Users\gpoli\GIT\AI_agents
pytest tests/test_vector_db_auth.py -v
```

---

### CHECKPOINT 6: Documentation & Cleanup (30 minutes)

#### Step 6.1: Update API Documentation
**File**: `VECTOR_DB_API_DOCUMENTATION.md` (UPDATE)

```markdown
# Vector Database API Documentation

## Authentication

**All endpoints require JWT authentication.**

### Authorization Header
```
Authorization: Bearer <jwt_token>
```

### Getting a Token
1. Login: `POST /api/auth/login`
2. Store token in `localStorage.setItem('authToken', token)`
3. Include in all API requests

### Token Expiry
- Tokens expire after 30 days
- 401 Unauthorized response triggers re-authentication
- Auto-refresh available 5 minutes before expiry

---

## Endpoints

### GET /api/vector-db/credentials/get
**Authentication**: Required  
**User Isolation**: Returns credentials for authenticated user only

**Request**:
```javascript
fetch('/api/vector-db/credentials/get', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
})
```

**Response**:
```json
{
    "success": true,
    "credentials": {
        "api_key": "****last8chars",
        "index_name": "inhouseprint",
        "environment": "us-east-1"
    }
}
```

---

### POST /api/vector-db/credentials/save
**Authentication**: Required  
**User Isolation**: Saves credentials for authenticated user only

**Request**:
```javascript
fetch('/api/vector-db/credentials/save', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        api_key: 'pcsk_...',
        index_name: 'myindex',
        environment: 'us-east-1'
    })
})
```

**Response**:
```json
{
    "success": true,
    "message": "Credentials saved successfully"
}
```

---

## Security Features

### ✅ Implemented
- JWT-based authentication on all endpoints
- User ID extracted from token (not query params)
- Encrypted credential storage (Fernet)
- Auto-decryption on retrieval
- Audit logging of credential access
- Session tracking (IP, user agent, device)

### 🔒 Permissions
- Users can only access their own credentials
- Admin users can view all credentials (future)
- Service accounts use encrypted .env.master

### 🚨 Error Handling
- 401 Unauthorized → Redirect to login
- 403 Forbidden → Insufficient permissions
- 404 Not Found → Credentials not configured
```

---

#### Step 6.2: Create Migration Guide
**File**: `VECTOR_DB_AUTH_MIGRATION_GUIDE.md` (NEW)

```markdown
# Vector Database Authentication Migration Guide

## For Developers

### Breaking Changes
1. **User ID Parameter Removed**
   - Old: `?user_id=1` query parameter
   - New: Extracted from JWT token automatically

2. **Authorization Header Required**
   - Old: Optional, relied on query param
   - New: Mandatory on all requests

### Code Migration Examples

**Before**:
```javascript
const response = await fetch(`/api/vector-db/stats?user_id=${userId}`);
```

**After**:
```javascript
const token = localStorage.getItem('authToken');
const response = await fetch('/api/vector-db/stats', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
```

---

## For Users

### No Action Required
- Authentication is automatic if logged in
- Existing credentials remain valid
- Token auto-refreshes before expiry

### Troubleshooting

**Issue**: "Unauthorized" error when accessing Vector DB
**Solution**: Log out and log back in to refresh token

**Issue**: Credentials not loading
**Solution**: 
1. Check browser console for errors
2. Verify authToken in localStorage
3. Try clearing browser cache

---

## Rollback Plan

If issues occur, rollback procedure:

1. Restore legacy file:
   ```bash
   git checkout HEAD~1 -- UI/modules_internal/vector_database/vector_database.legacy.js
   ```

2. Revert backend decorators:
   ```bash
   git checkout HEAD~1 -- AI_infrastructure/routes/vector_db_routes.py
   ```

3. Update module loader to use legacy:
   ```javascript
   // In module loader config
   vectorDatabase: {
       file: 'vector_database.legacy.js'
   }
   ```

4. Report issue with details:
   - Error message
   - Browser console logs
   - Network tab screenshot
```

---

## 📊 Summary

### Files Modified: 4
1. `UI/shared/js/module-utilities.js` - API utility authentication
2. `UI/modules_internal/vector_database/vector_database.js` - Remove user_id params
3. `AI_infrastructure/routes/vector_db_routes.py` - Add @require_auth decorators
4. `AI_infrastructure/auth/user_auth.py` - Track credential validation

### Files Deleted: 1
1. `UI/modules_internal/vector_database/vector_database.legacy.js` - Obsolete

### Files Created: 3
1. `AUTHENTICATION_FIX_IMPLEMENTATION_PLAN.md` (this file)
2. `VECTOR_DB_API_DOCUMENTATION.md` (updated)
3. `VECTOR_DB_AUTH_MIGRATION_GUIDE.md` (new)
4. `tests/test_vector_db_auth.py` (new)

### Estimated Time: 6 hours
- Checkpoint 1: 2 hours
- Checkpoint 2: 1.5 hours
- Checkpoint 3: 1 hour
- Checkpoint 4: 1 hour
- Checkpoint 5: 1 hour
- Checkpoint 6: 0.5 hours

### Risk Assessment: LOW
- Changes are additive (backward compatible)
- Existing credentials unchanged
- Rollback plan available
- No database schema changes

---

## 🚀 Ready to Implement

All analysis complete. Proceed with Checkpoint 1 when ready.
