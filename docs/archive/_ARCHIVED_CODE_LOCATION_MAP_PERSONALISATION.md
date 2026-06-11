# Code Location Map - Personalisation & Geolocation

## Files Modified

### 1. Database Schema
**File:** `data/schema_C__Users_gpoli_GIT_AI_agents_data_ai_infrastructure.db.json`

**What changed:**
- Added complete `user_preferences` table definition (lines before `"users":`)
- 17 new fields for preferences, geolocation, and timezone handling

**Fields added:**
```json
"user_preferences": [
  { "name": "id", "pk": true, "type": "INTEGER" },
  { "name": "user_id", "notnull": true, "type": "INTEGER" },
  { "name": "nickname", "type": "TEXT" },
  { "name": "communication_style", "type": "TEXT" },
  { "name": "detail_level", "type": "TEXT" },
  { "name": "auth_platform", "type": "TEXT" },
  { "name": "detected_country", "type": "TEXT" },
  { "name": "detected_city", "type": "TEXT" },
  { "name": "detected_timezone", "type": "TEXT" },
  { "name": "detected_ip_address", "type": "TEXT" },
  { "name": "manual_location_override", "type": "TEXT" },
  { "name": "manual_timezone_override", "type": "TEXT" },
  { "name": "use_manual_location", "type": "BOOLEAN" },
  { "name": "use_manual_timezone", "type": "BOOLEAN" },
  { "name": "last_location_check", "type": "TIMESTAMP" },
  { "name": "created_at", "type": "TIMESTAMP" },
  { "name": "updated_at", "type": "TIMESTAMP" }
]
```

---

### 2. HTML UI
**File:** `UI/business-ai-platform-v2.html`

#### Section A: Nickname Field
**Location:** Personalisation section, TOP (after section header)  
**Lines:** ~6063-6069

```html
<div class="settings-field">
    <label>Your Nickname <span style="color: var(--text-muted);">(Optional)</span></label>
    <input type="text" id="userNickname" placeholder="e.g., Gerardo, GP, The Boss" 
        onchange="saveSettings()" style="...">
    <small>How the AI should refer to you in conversations</small>
</div>
```

#### Section B: Location & Timezone Detection Display
**Location:** After "Authentication Platform" field in Personalisation section  
**Lines:** ~6095-6120

```html
<div class="settings-field">
    <label><i class="fas fa-map-marker-alt"></i> Location & Timezone Detection</label>
    <div style="...">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <div>
                <small>Detected Location</small>
                <div id="detectedLocation">Detecting...</div>
                <small>IP: <span id="detectedIP">--</span></small>
            </div>
            <div>
                <small>Detected Timezone</small>
                <div id="detectedTimezone">Detecting...</div>
                <small>Current Time: <span id="currentTime">--</span></small>
            </div>
        </div>
    </div>
</div>
```

**HTML Elements (DOM IDs):**
- `#detectedLocation` - Displays "City, Country"
- `#detectedIP` - Displays detected IP address
- `#detectedTimezone` - Displays "Timezone/Name (UTC±X)"
- `#currentTime` - Displays current time in that timezone

#### Section C: Manual Location Override
**Location:** Below Location & Timezone Detection card  
**Lines:** ~6121-6133

```html
<div class="settings-field">
    <label><i class="fas fa-edit"></i> Manual Location Override</label>
    <div style="display: flex; gap: 8px; align-items: center;">
        <input type="checkbox" id="useManualLocation" onchange="toggleManualLocation()">
        <label for="useManualLocation">Use manual location instead of detected</label>
    </div>
    <input type="text" id="manualLocation" placeholder="e.g., Sydney, Australia" 
        onchange="saveSettings()" style="..." disabled>
    <small>City, Country format</small>
</div>
```

**HTML Elements (DOM IDs):**
- `#useManualLocation` - Checkbox to enable/disable
- `#manualLocation` - Text input for location

#### Section D: Manual Timezone Override
**Location:** Below Manual Location Override  
**Lines:** ~6134-6166

```html
<div class="settings-field">
    <label><i class="fas fa-clock"></i> Manual Timezone Override</label>
    <div style="display: flex; gap: 8px; align-items: center;">
        <input type="checkbox" id="useManualTimezone" onchange="toggleManualTimezone()">
        <label for="useManualTimezone">Use manual timezone instead of detected</label>
    </div>
    <select id="manualTimezone" onchange="saveSettings()" style="..." disabled>
        <option value="">Select timezone...</option>
        <option value="UTC">UTC</option>
        <option value="Australia/Sydney">Australia/Sydney (UTC+10/+11)</option>
        <!-- ... 14 more options ... -->
    </select>
</div>
```

**HTML Elements (DOM IDs):**
- `#useManualTimezone` - Checkbox to enable/disable
- `#manualTimezone` - Dropdown select for timezone

---

### 3. JavaScript Functions
**File:** `UI/business-ai-platform-v2.html` (bottom of page, in `<script>` tag)

#### Function 1: Load Settings
**Name:** `loadAccountSettings()`  
**Location:** Lines ~12560-12605  
**What it does:**
- Loads settings from localStorage
- Updates ALL UI elements including new ones
- Calls `detectAndDisplayGeolocation()` if elements exist

**New code in function:**
```javascript
// Update UI - Personalisation Settings (NEW)
if (document.getElementById('userNickname')) {
    document.getElementById('userNickname').value = settings.nickname || '';
}
// ... location/timezone settings ...
if (document.getElementById('detectedLocation')) {
    detectAndDisplayGeolocation();
}
```

#### Function 2: Save Settings
**Name:** `saveSettings()`  
**Location:** Lines ~12609-12657  
**What it does:**
- Collects ALL current values from UI
- Saves to localStorage
- Calls backend sync function
- Shows "Settings saved!" toast

**New settings collected:**
```javascript
nickname: document.getElementById('userNickname').value,
useManualLocation: document.getElementById('useManualLocation').checked,
useManualTimezone: document.getElementById('useManualTimezone').checked,
manualLocation: document.getElementById('manualLocation').value,
manualTimezone: document.getElementById('manualTimezone').value,
```

#### Function 3: Save to Backend
**Name:** `savePersonalisationPreferencesToBackend(userId, preferences)`  
**Location:** Lines ~12659-12683  
**What it does:**
- POSTs settings to `/api/user/preferences`
- Includes all new fields
- Graceful error handling (doesn't block UI)

**New fields sent:**
```javascript
body: JSON.stringify({
    user_id: userId,
    nickname: preferences.nickname,
    use_manual_location: preferences.useManualLocation,
    use_manual_timezone: preferences.useManualTimezone,
    manual_location_override: preferences.manualLocation,
    manual_timezone_override: preferences.manualTimezone
})
```

#### Function 4: Detect Geolocation
**Name:** `detectAndDisplayGeolocation()`  
**Location:** Lines ~12685-12715  
**What it does:**
- Tries to fetch from backend endpoint `/api/geolocation/detect`
- Falls back to public `ipapi.co` service
- Calls `displayGeolocationData()` on success
- Gracefully handles errors

**Endpoints tried:**
1. Backend: `GET /api/geolocation/detect`
2. Fallback: `GET https://ipapi.co/json/`

#### Function 5: Display Geolocation Data
**Name:** `displayGeolocationData(data)`  
**Location:** Lines ~12717-12728  
**What it does:**
- Formats location data
- Updates display fields with detected values
- Calls `updateCurrentTime()`

**Updates these DOM elements:**
- `#detectedLocation` ← "City, Country"
- `#detectedIP` ← IP address
- `#detectedTimezone` ← "Timezone/Name"

#### Function 6: Update Current Time
**Name:** `updateCurrentTime(timezone)`  
**Location:** Lines ~12730-12739  
**What it does:**
- Shows current time in detected timezone
- Uses browser's `toLocaleString()` with timezone param
- Handles invalid timezones gracefully

**Updates DOM element:**
- `#currentTime` ← Formatted time string

#### Function 7: Toggle Manual Location
**Name:** `toggleManualLocation()`  
**Location:** Lines ~12741-12752  
**What it does:**
- Enables/disables `#manualLocation` input based on checkbox
- Auto-focuses input when enabled
- Triggers `saveSettings()`

**Toggles:**
- `#manualLocation.disabled`

#### Function 8: Toggle Manual Timezone
**Name:** `toggleManualTimezone()`  
**Location:** Lines ~12754-12765  
**What it does:**
- Enables/disables `#manualTimezone` select based on checkbox
- Auto-focuses select when enabled
- Triggers `saveSettings()`

**Toggles:**
- `#manualTimezone.disabled`

---

## localStorage Structure

**Key:** `accountSettings`

```javascript
{
  // Existing fields
  model: "claude-sonnet-4-5-20250929",
  temperature: 1.0,
  topP: 1.0,
  enableThinking: true,
  maxRounds: 20,
  roundTimeout: 30,
  enableStreaming: true,
  maxTokens: 16000,
  thinkingBudget: 10000,
  
  // NEW FIELDS
  nickname: "GP",                           // User's nickname
  communicationStyle: "professional",       // professional|casual|detailed|brief
  detailLevel: "standard",                  // minimal|standard|comprehensive
  authPlatform: "auto",                     // auto|microsoft|google
  
  useManualLocation: false,                 // Whether manual location is enabled
  manualLocation: "",                       // Manually entered location
  useManualTimezone: true,                  // Whether manual timezone is enabled
  manualTimezone: "Australia/Melbourne",    // Manually selected timezone
  
  lastUpdated: "2025-11-04T14:30:00.000Z"
}
```

---

## API Endpoints (Frontend Calls)

### 1. Save Preferences to Backend
**Endpoint:** `POST /api/user/preferences`  
**Called from:** `savePersonalisationPreferencesToBackend()`  
**Headers:**
```javascript
{
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${authToken}`
}
```

**Request body:**
```json
{
  "user_id": 1,
  "nickname": "GP",
  "communication_style": "professional",
  "detail_level": "standard",
  "auth_platform": "auto",
  "use_manual_location": false,
  "use_manual_timezone": true,
  "manual_location_override": "",
  "manual_timezone_override": "Australia/Melbourne"
}
```

### 2. Get Geolocation (Optional - Suggested Backend)
**Endpoint:** `GET /api/geolocation/detect`  
**Called from:** `detectAndDisplayGeolocation()` (first attempt)  
**Headers:**
```javascript
{
  'Authorization': `Bearer ${authToken}`
}
```

**Response (expected):**
```json
{
  "country": "Australia",
  "city": "Sydney",
  "timezone": "Australia/Sydney",
  "ip_address": "203.x.x.x",
  "latitude": -33.87,
  "longitude": 151.21,
  "detected_at": "2025-11-04T14:30:00Z"
}
```

### 3. Fallback: Public IP Geolocation
**URL:** `GET https://ipapi.co/json/`  
**Used when:** Backend endpoint unavailable  
**Response fields used:**
- `country_name` → `country`
- `city` → `city`
- `timezone` → `timezone`
- `ip` → `ip_address`

---

## Event Flow Diagram

```
┌─────────────────────────┐
│ Account Settings Opens  │
└────────────┬────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ loadAccountSettings()                │
│ • Reads localStorage                 │
│ • Updates all UI fields              │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ detectAndDisplayGeolocation()         │
│ • Tries /api/geolocation/detect      │
│ • Falls back to ipapi.co             │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ displayGeolocationData(data)         │
│ • Updates #detectedLocation          │
│ • Updates #detectedIP                │
│ • Updates #detectedTimezone          │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ updateCurrentTime(timezone)          │
│ • Updates #currentTime               │
│ • Shows time in that timezone        │
└────────────┬─────────────────────────┘
             │
   User changes setting
             │
             ▼
┌──────────────────────────────────────┐
│ saveSettings()                       │
│ • Collects all values from UI        │
│ • Saves to localStorage              │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ savePersonalisationPreferencesToBack │
│ • POST to /api/user/preferences      │
│ • Syncs all settings to DB           │
└──────────────────────────────────────┘
```

---

## Testing Checklist

- [ ] Open Account Settings
- [ ] Verify "Personalisation" section at TOP
- [ ] See nickname field - try entering one
- [ ] See "Location & Timezone Detection" card
  - [ ] Detected location shows (e.g., "Sydney, Australia")
  - [ ] Detected IP shows (e.g., "203.x.x.x")
  - [ ] Detected timezone shows (e.g., "Australia/Sydney")
  - [ ] Current time updates (e.g., "2:30 PM")
- [ ] See "Manual Location Override"
  - [ ] Checkbox disabled location input by default
  - [ ] Click checkbox to enable input
  - [ ] Enter "Melbourne, Australia"
  - [ ] Verify input is now enabled
- [ ] See "Manual Timezone Override"
  - [ ] Checkbox disabled timezone select by default
  - [ ] Click checkbox to enable select
  - [ ] Choose "Australia/Melbourne"
  - [ ] Verify select is now enabled
- [ ] Close and reopen settings
- [ ] Verify all values persisted
- [ ] Open DevTools > Application > localStorage
- [ ] Check "accountSettings" key has new fields
- [ ] Check Network tab for successful POST to `/api/user/preferences`

---

## Summary

**Total Changes:**
- 1 database table added (17 fields)
- 4 UI sections added/enhanced
- 8 JavaScript functions added/enhanced
- 2 API endpoints to implement (1 optional)
- 5 new localStorage fields
- 4 new DOM elements created

**Status:** ✅ Frontend complete and ready to test
