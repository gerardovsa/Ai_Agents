# AI Settings Flow Analysis - November 11, 2025

## Executive Summary

**STATUS:** ❌ **PARTIALLY IMPLEMENTED** - AI settings are collected in UI but **NOT saved to database or passed to API**

### Critical Issues Found:
1. ❌ AI settings (model, temperature, max_tokens, thinking_enabled) **NOT saved to database**
2. ❌ AI settings **NOT passed** from UI to backend in API requests
3. ❌ Backend hardcodes AI parameters (ignores user preferences)
4. ✅ UI collects and stores settings in localStorage (working)

---

## 1. UI Layer Analysis (business-ai-platform-v2.html)

### Settings Collection ✅ WORKING

**Location:** Lines 22495-22530

```javascript
const settings = {
    // Model Options
    model: modelSelect ? modelSelect.value : 'claude-sonnet-4-5-20250929',
    temperature: temperature ? parseFloat(temperature.value) : 1.0,
    topP: topP ? parseFloat(topP.value) : 1.0,
    enableThinking: enableThinking ? enableThinking.checked : false,
    
    // Token Parameters
    maxTokens: maxTokens ? parseInt(maxTokens.value) : 4096,
    thinkingBudget: thinkingBudget ? parseInt(thinkingBudget.value) : 10000,
    
    // Personalisation Settings
    nickname: userNickname ? userNickname.value : '',
    communicationStyle: communicationStyle ? communicationStyle.value : 'professional',
    detailLevel: detailLevelRadio ? detailLevelRadio.value : 'standard',
    authPlatform: authPlatform ? authPlatform.value : 'auto',
    // ... location, timezone settings
};
```

**Result:** All AI settings collected correctly ✅

---

### Settings Storage - PARTIAL ⚠️

**Location:** Lines 22547-22558

```javascript
// Save to localStorage (WORKS)
localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(settings));
console.log('Saved to localStorage');

// Save to backend if user is authenticated
if (window.currentUserId) {
    console.log('Saving ALL settings to backend for user:', window.currentUserId);
    saveAllSettingsToBackend(window.currentUserId, settings);  // ❌ PROBLEM HERE
} else {
    console.log('No currentUserId - skipping backend save');
}
```

**Problem:** `saveAllSettingsToBackend()` function **excludes AI model settings**!

---

### Backend Save Function - MISSING AI SETTINGS ❌

**Location:** Lines 22565-22620 (saveAllSettingsToBackend)

```javascript
const payload = {
    user_id: userId,
    
    // Personalisation Settings ✅
    nickname: settings.nickname || '',
    communication_style: settings.communicationStyle || 'professional',
    detail_level: settings.detailLevel || 'standard',
    auth_platform: settings.authPlatform || 'auto',
    
    // Location & Timezone ✅
    use_manual_location: settings.useManualLocation || false,
    use_manual_timezone: settings.useManualTimezone || false,
    // ...
    
    // User Preferences ✅
    preferred_tools: JSON.stringify(preferredTools || []),
    custom_preferences: JSON.stringify(customPreferences || [])
    
    // ❌ MISSING: model, temperature, topP, enableThinking, maxTokens, thinkingBudget
};
```

**Problem:** AI model settings NOT included in backend payload!

---

### Chat API Request - MISSING AI SETTINGS ❌

**Location:** Lines 11354-11375 (when sending messages)

```javascript
const requestBody = {
    message: message,
    session_id: sessionId,
    conversation_history: conversationHistory,
    user_context: userContext,  // ✅ Contains nickname, auth_platform, memories
    context: {
        tab: AppState.currentTab,
        platform: 'business_ai_platform',
        tools_enabled: true,
        available_tools: ToolManager.availableTools.length,
        google_auth: AuthManager.isAuthenticated ? AuthManager.getAccessToken() : null
    },
    preferences: {
        use_tools: true,
        verbose_tool_output: true,
        streaming: true
        // ❌ MISSING: model, temperature, max_tokens, enable_thinking
    }
};
```

**Problem:** Request body doesn't include AI model preferences!

---

## 2. Database Layer Analysis

### Current Schema ❌ INCOMPLETE

**Table:** `user_preferences`

**Existing columns:**
- ✅ `nickname` (TEXT)
- ✅ `communication_style` (TEXT)
- ✅ `detail_level` (TEXT)
- ✅ `auth_platform` (TEXT)
- ✅ `preferred_tools` (TEXT, JSON)
- ✅ `custom_preferences` (TEXT, JSON)
- ✅ `ai_memories` (TEXT, JSON)

**Missing columns:**
- ❌ `ai_model` (TEXT) - e.g., 'claude-sonnet-4-5-20250929'
- ❌ `ai_temperature` (REAL) - e.g., 1.0
- ❌ `ai_top_p` (REAL) - e.g., 1.0
- ❌ `ai_max_tokens` (INTEGER) - e.g., 4096
- ❌ `ai_thinking_enabled` (INTEGER/BOOLEAN) - e.g., 0 or 1
- ❌ `ai_thinking_budget` (INTEGER) - e.g., 10000
- ❌ `ai_streaming_enabled` (INTEGER/BOOLEAN) - e.g., 1

---

## 3. Backend Layer Analysis

### Route Handler - NOT READING AI SETTINGS ❌

**File:** `agent_routes_v4.py`
**Location:** Lines 650-720

```python
# Get user preferences (nickname, auth platform, communication style)
user_prefs = get_user_preferences(user_id) if user_id else None

nickname = user_prefs.get('nickname', '') if user_prefs else ''
auth_platform = user_prefs.get('auth_platform', 'auto') if user_prefs else 'auto'
communication_style = user_prefs.get('communication_style', 'professional') if user_prefs else 'professional'
detail_level = user_prefs.get('detail_level', 'standard') if user_prefs else 'standard'

# ❌ MISSING: No extraction of AI model settings!
# Should have:
# ai_model = user_prefs.get('ai_model', 'claude-sonnet-4-5-20250929')
# ai_temperature = user_prefs.get('ai_temperature', 1.0)
# ai_max_tokens = user_prefs.get('ai_max_tokens', 4096)
# ai_thinking_enabled = user_prefs.get('ai_thinking_enabled', False)
# ai_thinking_budget = user_prefs.get('ai_thinking_budget', 5000)
```

**Problem:** Route doesn't extract AI model preferences from database!

---

### Agent Worker - HARDCODED PARAMETERS ❌

**File:** `combined_agent_worker.py`
**Location:** Lines 685-693

```python
# Call AI with tools
response = ai_client.create_message(
    messages=messages,
    provider='anthropic',
    model='claude-sonnet-4-5-20250929',  # ❌ HARDCODED
    max_tokens=16000,                      # ❌ HARDCODED
    system=system_prompt,
    tools=tools,
    enable_thinking=True,                  # ❌ HARDCODED
    thinking_budget=5000,                  # ❌ HARDCODED
    enable_web_search=True,
    enable_web_fetch=True
)
```

**Problem:** All AI parameters are hardcoded, ignoring user preferences!

---

## 4. Complete Flow Diagram

### CURRENT (BROKEN) FLOW:

```
UI Settings Modal
    ↓
[User sets: model, temperature, thinking, tokens]
    ↓
saveSettings() ✅ Collects all settings
    ↓
localStorage ✅ Stores all settings (working)
    ↓
saveAllSettingsToBackend() ❌ DROPS AI settings
    ↓
POST /api/user/preferences ❌ Only saves nickname, auth_platform, etc.
    ↓
Database ❌ No columns for AI settings
    ↓
[User sends chat message]
    ↓
POST /api/agent/agent/1/start ❌ Request missing AI preferences
    ↓
agent_routes_v4.py ❌ Doesn't read AI settings from DB
    ↓
combined_agent_worker.py ❌ Uses hardcoded parameters
    ↓
Anthropic API ❌ Ignores user's preferences
```

### DESIRED (FIXED) FLOW:

```
UI Settings Modal
    ↓
[User sets: model, temperature, thinking, tokens]
    ↓
saveSettings() ✅ Collects all settings
    ↓
localStorage ✅ Stores all settings
    ↓
saveAllSettingsToBackend() ✅ Includes AI settings in payload
    ↓
POST /api/user/preferences ✅ Saves ALL settings (including AI)
    ↓
Database ✅ New columns store AI preferences
    ↓
[User sends chat message]
    ↓
POST /api/agent/agent/1/start ✅ Request includes AI preferences
    ↓
agent_routes_v4.py ✅ Reads AI settings from DB or request
    ↓
combined_agent_worker.py ✅ Uses user's AI parameters
    ↓
Anthropic API ✅ Respects user's preferences
```

---

## 5. Summary of Required Fixes

### Fix 1: Database Schema Update ⚡ HIGH PRIORITY

**Action:** Add columns to `user_preferences` table

```sql
ALTER TABLE user_preferences ADD COLUMN ai_model TEXT DEFAULT 'claude-sonnet-4-5-20250929';
ALTER TABLE user_preferences ADD COLUMN ai_temperature REAL DEFAULT 1.0;
ALTER TABLE user_preferences ADD COLUMN ai_top_p REAL DEFAULT 1.0;
ALTER TABLE user_preferences ADD COLUMN ai_max_tokens INTEGER DEFAULT 4096;
ALTER TABLE user_preferences ADD COLUMN ai_thinking_enabled INTEGER DEFAULT 0;
ALTER TABLE user_preferences ADD COLUMN ai_thinking_budget INTEGER DEFAULT 10000;
ALTER TABLE user_preferences ADD COLUMN ai_streaming_enabled INTEGER DEFAULT 1;
```

---

### Fix 2: UI Backend Save Function ⚡ HIGH PRIORITY

**File:** `UI/business-ai-platform-v2.html`
**Location:** Line ~22595 (in saveAllSettingsToBackend)

**Add to payload:**
```javascript
const payload = {
    // ... existing fields ...
    
    // AI Model Settings (NEW)
    ai_model: settings.model || 'claude-sonnet-4-5-20250929',
    ai_temperature: settings.temperature || 1.0,
    ai_top_p: settings.topP || 1.0,
    ai_max_tokens: settings.maxTokens || 4096,
    ai_thinking_enabled: settings.enableThinking || false,
    ai_thinking_budget: settings.thinkingBudget || 10000,
    ai_streaming_enabled: settings.enableStreaming !== false
};
```

---

### Fix 3: Backend Preferences Route ⚡ HIGH PRIORITY

**File:** `AI_infrastructure/routes/user_preferences_routes.py`
**Location:** Lines ~403-450 (POST handler)

**Add fields to INSERT/UPDATE:**
```python
ai_model = data.get('ai_model', 'claude-sonnet-4-5-20250929')
ai_temperature = data.get('ai_temperature', 1.0)
ai_top_p = data.get('ai_top_p', 1.0)
ai_max_tokens = data.get('ai_max_tokens', 4096)
ai_thinking_enabled = data.get('ai_thinking_enabled', False)
ai_thinking_budget = data.get('ai_thinking_budget', 10000)
ai_streaming_enabled = data.get('ai_streaming_enabled', True)

# Update SQL INSERT/UPDATE to include these fields
```

---

### Fix 4: Agent Route - Load AI Settings ⚡ HIGH PRIORITY

**File:** `AI_infrastructure/routes/agent_routes_v4.py`
**Location:** Line ~670 (after loading user_prefs)

**Extract AI settings:**
```python
# Get AI model preferences
ai_model = user_prefs.get('ai_model', 'claude-sonnet-4-5-20250929') if user_prefs else 'claude-sonnet-4-5-20250929'
ai_temperature = user_prefs.get('ai_temperature', 1.0) if user_prefs else 1.0
ai_max_tokens = user_prefs.get('ai_max_tokens', 4096) if user_prefs else 4096
ai_thinking_enabled = user_prefs.get('ai_thinking_enabled', False) if user_prefs else False
ai_thinking_budget = user_prefs.get('ai_thinking_budget', 10000) if user_prefs else 10000

print(f"[Stream {agent_id}] 🤖 AI Model: {ai_model}")
print(f"[Stream {agent_id}] 🌡️  Temperature: {ai_temperature}")
print(f"[Stream {agent_id}] 🎯 Max Tokens: {ai_max_tokens}")
print(f"[Stream {agent_id}] 🧠 Thinking: {ai_thinking_enabled}")
```

---

### Fix 5: Agent Route - Pass to Worker ⚡ HIGH PRIORITY

**File:** `AI_infrastructure/routes/agent_routes_v4.py`
**Location:** Line ~930 (where worker is called)

**Pass AI settings to worker:**
```python
worker_thread = threading.Thread(
    target=process_agent_request_async,
    args=(agent_id, user_message, conversation_history, session_id),
    kwargs={
        'ai_model': ai_model,
        'ai_temperature': ai_temperature,
        'ai_max_tokens': ai_max_tokens,
        'ai_thinking_enabled': ai_thinking_enabled,
        'ai_thinking_budget': ai_thinking_budget
    }
)
```

---

### Fix 6: Agent Worker - Use Dynamic Parameters ⚡ CRITICAL

**File:** `AI_infrastructure/core/combined_agent_worker.py`
**Location:** Line ~685 (create_message call)

**Replace hardcoded values:**
```python
def process_agent_request_async(
    agent_id, 
    prompt, 
    conversation_history, 
    session_id,
    ai_model='claude-sonnet-4-5-20250929',
    ai_temperature=1.0,
    ai_max_tokens=16000,
    ai_thinking_enabled=True,
    ai_thinking_budget=5000
):
    # ... existing code ...
    
    # Call AI with USER'S PREFERENCES
    response = ai_client.create_message(
        messages=messages,
        provider='anthropic',
        model=ai_model,                      # ✅ USER'S CHOICE
        max_tokens=ai_max_tokens,            # ✅ USER'S CHOICE
        system=system_prompt,
        tools=tools,
        enable_thinking=ai_thinking_enabled, # ✅ USER'S CHOICE
        thinking_budget=ai_thinking_budget,  # ✅ USER'S CHOICE
        enable_web_search=True,
        enable_web_fetch=True
    )
```

---

### Fix 7: UI Chat Request - Include AI Preferences (OPTIONAL)

**File:** `UI/business-ai-platform-v2.html`
**Location:** Line ~11370 (request body)

**Optional - Include in request for override:**
```javascript
const requestBody = {
    message: message,
    session_id: sessionId,
    conversation_history: conversationHistory,
    user_context: userContext,
    
    // AI Preferences (OPTIONAL - backend can read from DB instead)
    ai_preferences: {
        model: settings.model,
        temperature: settings.temperature,
        max_tokens: settings.maxTokens,
        enable_thinking: settings.enableThinking,
        thinking_budget: settings.thinkingBudget
    },
    
    context: { /* ... */ },
    preferences: { /* ... */ }
};
```

---

## 6. Testing Checklist

After implementing fixes:

### Test 1: Settings Save to Database
```javascript
// Browser console
saveSettings();
```

```powershell
# Verify in database
python -c "import sqlite3; conn = sqlite3.connect('data/ai_infrastructure.db'); cursor = conn.cursor(); cursor.execute('SELECT ai_model, ai_temperature, ai_max_tokens, ai_thinking_enabled FROM user_preferences WHERE user_id = 14'); print(cursor.fetchone()); conn.close()"
```

**Expected:** Should show user's AI settings, not defaults

---

### Test 2: Settings Used in API Call
```javascript
// Browser console - send test message
// Check Flask logs
```

**Expected Flask logs:**
```
[Stream 1] 🤖 AI Model: claude-sonnet-4-5-20250929
[Stream 1] 🌡️  Temperature: 1.0
[Stream 1] 🎯 Max Tokens: 4096
[Stream 1] 🧠 Thinking: True
```

---

### Test 3: Change Settings and Verify
```javascript
// 1. Change temperature to 0.5
// 2. Disable thinking
// 3. Set max tokens to 8000
// 4. Save settings
saveSettings();

// 5. Send test message
// 6. Check Flask logs
```

**Expected:** Logs should show NEW values (0.5, False, 8000)

---

## 7. Priority Order

1. **Fix 1** (Database) - Foundation for everything
2. **Fix 2** (UI Save) - Ensures data reaches backend
3. **Fix 3** (Backend Route) - Stores data correctly
4. **Fix 4** (Load Settings) - Retrieves data
5. **Fix 6** (Worker) - Uses data in API calls
6. **Fix 5** (Pass to Worker) - Connects route to worker
7. **Fix 7** (Optional) - Request-level overrides

---

## 8. Current Status Summary

| Component | Status | Issue |
|-----------|--------|-------|
| UI Collection | ✅ Working | Settings collected correctly |
| UI localStorage | ✅ Working | All settings stored locally |
| UI Backend Save | ❌ Broken | AI settings excluded from payload |
| Database Schema | ❌ Missing | No columns for AI settings |
| Backend Route | ❌ Incomplete | Doesn't handle AI settings |
| Agent Route Load | ❌ Missing | Doesn't read AI settings |
| Agent Worker | ❌ Hardcoded | Ignores user preferences |
| API Request | ❌ Broken | User preferences not respected |

---

## Conclusion

**AI settings flow is 30% complete:**
- ✅ UI captures settings
- ✅ localStorage stores settings
- ❌ Backend doesn't save settings
- ❌ Backend doesn't load settings
- ❌ API calls ignore user preferences

**Impact:** Users can configure AI settings, but they're NEVER used. All conversations use hardcoded defaults.

**Effort to fix:** ~2-3 hours for all 7 fixes
**Priority:** HIGH - User preferences should be respected
**Risk:** LOW - Changes are additive (no breaking changes)

---

**Generated:** November 11, 2025
**Status:** Needs Implementation
**Next Step:** Start with Fix 1 (Database Schema)
