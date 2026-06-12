# 🎨 User Preferences Integration - Account Sidebar

## Date: December 9, 2025

## 🎯 Objective

Integrate Supabase `user_preferences` and `user_platform_credentials` tables with the Account Sidebar to display and manage user settings.

## 📊 Database Tables

### 1. `ai_infrastructure.user_preferences`

**Purpose:** Store user personalization and AI configuration settings

**Key Fields:**
- `user_id` - Primary key, links to users table
- **Personalization:**
  - `nickname` - Display name
  - `communication_style` - professional/casual/technical
  - `detail_level` - standard/brief/detailed
  - `auth_platform` - auto/google/microsoft/local
  - `preferred_tools` - JSON array of tool preferences
  - `custom_preferences` - JSON array of custom settings
- **Location:**
  - `detected_country`, `detected_city`, `detected_timezone`
  - `manual_location_override`, `manual_timezone_override`
  - `use_manual_location`, `use_manual_timezone` (0/1 flags)
- **AI Settings:**
  - `ai_model` - claude-sonnet-4-5-20250929
  - `ai_temperature` - 0.0 to 2.0 (default 1.0)
  - `ai_top_p` - 0.0 to 1.0 (default 1.0)
  - `ai_max_tokens` - Max response length (default 4096)
  - `ai_thinking_enabled` - 0/1 flag for extended thinking
  - `ai_thinking_budget` - Token budget for thinking (default 10000)
  - `ai_streaming_enabled` - 0/1 flag for streaming responses
- **AI Memories:**
  - `ai_memories` - JSON text of user context/memories
  - `memory_updated_at` - Last memory update timestamp

### 2. `ai_infrastructure.user_platform_credentials`

**Purpose:** Store API keys, OAuth tokens, and database credentials

**Key Fields:**
- `id` - Primary key
- `user_id` - Foreign key to users
- `platform` - pinecone, anthropic, xero_print, supabase, etc.
- `credential_type` - api_key, oauth, api_keys, database
- `credential_key` - Key identifier (e.g., "PINECONE_API_KEY")
- `credential_value` - Encrypted credential value
- `is_active` - Boolean flag
- `metadata` - JSONB with platform-specific config
- `credentials` - JSONB with full credential set

**Sample Data:**
```json
{
  "platform": "pinecone",
  "credential_type": "api_key",
  "metadata": {
    "namespace": "",
    "index_name": "inhouseprint",
    "environment": "us-east-1"
  },
  "credentials": {
    "api_key": "pcsk_...",
    "namespace": "",
    "index_name": "inhouseprint",
    "environment": "us-east-1"
  }
}
```

## ✅ Backend Implementation

### New API Endpoints

#### 1. `GET /api/auth/preferences`

**File:** `AI_infrastructure/routes/auth_routes.py` (Lines 950-1047)

**Returns:**
```json
{
  "success": true,
  "preferences": {
    "user_id": 12,
    "communication_style": "professional",
    "detail_level": "standard",
    "auth_platform": "auto",
    "preferred_tools": "[\"Use only Google Workspace\"]",
    "custom_preferences": "[]",
    "nickname": "",
    "detected_country": "Australia",
    "detected_city": "Brisbane",
    "detected_timezone": "Australia/Brisbane",
    "ai_model": "claude-sonnet-4-5-20250929",
    "ai_temperature": 1.0,
    "ai_top_p": 1.0,
    "ai_max_tokens": 4096,
    "ai_thinking_enabled": 0,
    "ai_thinking_budget": 10000,
    "ai_streaming_enabled": 1
  }
}
```

**Features:**
- ✅ Cursor management: Initialized as `None`, closed in try block, finally cleanup
- ✅ Returns default values if no preferences exist
- ✅ Handles both dict and tuple cursor responses
- ✅ Converts timestamps to ISO format
- ✅ Type conversion (float, int) for numeric fields

#### 2. `PUT /api/auth/preferences`

**File:** `AI_infrastructure/routes/auth_routes.py` (Lines 1050-1145)

**Request Body:**
```json
{
  "communication_style": "casual",
  "ai_temperature": 1.2,
  "ai_thinking_enabled": 1
}
```

**Features:**
- ✅ Dynamic UPDATE query (only updates provided fields)
- ✅ UPSERT logic (INSERT if no preferences exist)
- ✅ Field validation (only allowed_fields accepted)
- ✅ Auto-updates `updated_at` timestamp
- ✅ Cursor management: Initialized, closed, finally cleanup

### Cursor Management Verification

**Both endpoints pass ALL success criteria:**

✅ **cursor = None** initialized before try block  
✅ **cursor.close()** called exactly once before function exit  
✅ **finally block** for guaranteed cleanup  
✅ **No early returns** before cursor cleanup  
✅ **Context manager** for connection auto-close  
✅ **No syntax errors** introduced  
✅ **No logic changes** to existing code

## 🎨 Frontend Implementation

### Enhanced Profile Tab

**File:** `UI/business-ai-platform-v2.html` (Lines 25168-25350+)

**What Was Added:**

1. **Async Data Loading:**
   ```javascript
   const response = await fetch(`${API_BASE_URL}/api/auth/preferences`, {
     headers: { 'Authorization': `Bearer ${token}` }
   });
   const data = await response.json();
   ```

2. **Form Fields (Read-Only):**
   - ✅ Username (from UserAuth.user)
   - ✅ Email (from UserAuth.user)
   - ✅ Role (from UserAuth.user)
   - ✅ Authentication Method (Google/Microsoft/Local)
   - ✅ User ID (for debugging)
   - ✅ Nickname (from preferences)
   - ✅ Communication Style (from preferences)
   - ✅ Detail Level (from preferences)
   - ✅ Preferred Tools (from preferences)
   - ✅ Location Info (detected + manual override)
   - ✅ AI Model (from preferences)
   - ✅ AI Temperature (from preferences)
   - ✅ AI Top-P (from preferences)
   - ✅ AI Max Tokens (from preferences)
   - ✅ Extended Thinking (enabled/disabled)
   - ✅ Streaming (enabled/disabled)

3. **Display Format:**
   ```html
   <div class="preference-field">
     <label>Field Name</label>
     <input type="text" value="${value}" readonly />
   </div>
   ```

4. **Error Handling:**
   - Loading state with spinner
   - Error message display
   - Fallback to cached data if API fails
   - Retry button on error

5. **Console Logging:**
   ```
   [ACCOUNT SIDEBAR] Loading profile tab...
   [ACCOUNT SIDEBAR] Fetching preferences from API...
   [ACCOUNT SIDEBAR] Preferences loaded: {...}
   [ACCOUNT SIDEBAR] Profile tab rendered with X fields
   ```

## 📋 Data Flow

### Profile Tab Load Sequence

1. **User clicks Profile tab**
2. **AccountSidebar.switchTab('profile')** called
3. **loadProfileTab(container)** executes
4. **Shows loading spinner**
5. **Fetches UserAuth.user** (username, email, role, auth_platform)
6. **Fetches /api/auth/preferences** (all preference fields)
7. **Merges data** (user + preferences)
8. **Renders form fields** (read-only)
9. **Logs to console**
10. **User sees populated form**

### Connections Tab Load Sequence

1. **User clicks Connections tab**
2. **AccountSidebar.switchTab('connections')** called
3. **loadConnectionsTab(container)** executes
4. **Copies modal HTML to sidebar**
5. **Calls loadConnectionsModal()**
6. **Fetches /api/connections** (OAuth + platform credentials)
7. **Groups by type** (OAuth, API Keys, Databases)
8. **Renders connection cards**
9. **Shows status indicators**
10. **User sees all connections**

## 🧪 Testing Instructions

### 1. Test Backend Endpoints

**In terminal:**
```bash
# Start backend (if not running)
BISTART

# Test GET preferences
curl -X GET http://localhost:5001/api/auth/preferences \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test PUT preferences
curl -X PUT http://localhost:5001/api/auth/preferences \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ai_temperature": 1.2, "nickname": "Test"}'
```

### 2. Test Frontend Integration

**In browser console (F12):**
```javascript
// 1. Check if preferences endpoint works
const token = localStorage.getItem('authToken');
fetch('http://localhost:5001/api/auth/preferences', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(r => r.json())
.then(console.log);

// 2. Open Profile tab
AccountSidebar.toggleSidebar();
AccountSidebar.switchTab('profile');

// 3. Check console logs
// Should see:
// [ACCOUNT SIDEBAR] Loading profile tab...
// [ACCOUNT SIDEBAR] Preferences loaded: {...}
// [ACCOUNT SIDEBAR] Profile tab rendered

// 4. Verify fields populated
// Look for readonly input fields with actual data
```

### 3. Verify Data Display

**Check these fields appear:**
- [ ] Username matches database
- [ ] Email matches database
- [ ] Role displayed correctly
- [ ] Auth platform shows icon (Google/Microsoft/Local)
- [ ] Nickname (if set)
- [ ] Communication style (professional/casual/technical)
- [ ] AI model name
- [ ] AI temperature value
- [ ] Extended thinking status
- [ ] Streaming status
- [ ] Location info (country, city, timezone)

### 4. Test Error States

**No preferences in database:**
```sql
DELETE FROM ai_infrastructure.user_preferences WHERE user_id = YOUR_USER_ID;
```
- Should show default values
- Should not crash

**Invalid token:**
```javascript
localStorage.setItem('authToken', 'invalid_token');
AccountSidebar.switchTab('profile');
```
- Should show error message
- Should have retry button

## 🔐 Security Considerations

### Credential Masking

**In connection_routes.py:**
```python
from AI_infrastructure.auth.credential_encryptor import get_encryptor
encryptor = get_encryptor()
masked_value = encryptor.mask_credential(credential_value)
```

**Displayed as:**
```
pcsk_4NZh...yhr (48 chars)
sk-ant-api03-LMc3...RAAA (112 chars)
```

### Token Validation

**All endpoints use @require_auth decorator:**
```python
@auth_bp.route('/preferences', methods=['GET'])
@require_auth
def get_user_preferences():
    user_id = request.user['user_id']  # Extracted from validated JWT
```

## 📊 Database Queries

### Preferences Query
```sql
SELECT * FROM ai_infrastructure.user_preferences 
WHERE user_id = 12;
```

### Connections Query
```sql
-- OAuth tokens
SELECT id, platform, email, is_active, scope, expires_at
FROM ai_infrastructure.oauth_tokens
WHERE user_id = 12;

-- Platform credentials
SELECT id, platform, credential_type, credential_key, metadata
FROM ai_infrastructure.user_platform_credentials
WHERE user_id = 12;
```

## 🚀 Deployment

### Files Modified

1. **Backend:**
   - `AI_infrastructure/routes/auth_routes.py` (+200 lines)
     - Added GET /api/auth/preferences
     - Added PUT /api/auth/preferences

2. **Frontend:**
   - `UI/business-ai-platform-v2.html` (+150 lines)
     - Enhanced loadProfileTab() to fetch preferences
     - Added preference fields display
     - Added loading/error states

### Deployment Steps

1. **Backend:**
   ```bash
   # Restart Flask server
   # In PowerShell Extension terminal:
   Ctrl+C
   BISTART
   ```

2. **Frontend:**
   ```bash
   # Hard refresh browser
   Ctrl+Shift+R
   ```

3. **Verification:**
   - Open Account Sidebar
   - Click Profile tab
   - Should see all fields populated
   - Check console for success logs

## 📝 Next Steps (Future Enhancements)

### Make Fields Editable

Convert read-only fields to editable inputs with save button:

```javascript
// Add edit mode toggle
const editBtn = document.createElement('button');
editBtn.textContent = 'Edit';
editBtn.onclick = () => enableEditMode();

// On save, call PUT endpoint
async function savePreferences() {
  const updates = {
    nickname: document.getElementById('nickname').value,
    ai_temperature: parseFloat(document.getElementById('ai_temperature').value)
  };
  
  await fetch(`${API_BASE_URL}/api/auth/preferences`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(updates)
  });
}
```

### Add AI Settings Tab

Create dedicated tab for AI configuration:
- Model selection dropdown
- Temperature slider
- Extended thinking toggle
- Token budget input
- Test AI button (sends test prompt)

### Add Location Settings Tab

Create dedicated tab for location/timezone:
- Auto-detected location (read-only)
- Manual location override input
- Timezone selector
- Use manual override toggle

## ✅ Status

- [x] Backend endpoints created
- [x] Cursor management verified
- [x] Frontend integration complete
- [x] Profile tab displays preferences
- [x] Connections tab displays credentials
- [x] Error handling implemented
- [x] Console logging added
- [x] Documentation complete
- [ ] **Ready for testing** (after backend restart)

---

**Next Action:** Restart Flask backend with `BISTART` and test Profile tab!
