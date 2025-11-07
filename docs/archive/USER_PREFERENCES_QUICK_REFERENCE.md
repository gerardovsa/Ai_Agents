# User Preferences - Quick Reference Guide

## The 3 Questions - ANSWERED

### 1️⃣ "Implement the endpoints?"
**Status:** ✅ DONE

**Location:** `AI_infrastructure/routes/user_preferences_routes.py`

**Endpoints:**
- `GET /api/user/preferences` - Retrieve user preferences from database
- `POST /api/user/preferences` - Save user preferences to database

**Both endpoints:**
- Require JWT Bearer token authentication
- Handle 17 fields (core settings + geolocation)
- Auto-create preferences if they don't exist
- Return JSON with full preference data

---

### 2️⃣ "Put a save button in account settings?"
**Status:** ✅ DONE

**Location:** `UI/business-ai-platform-v2.html` - Modal Footer (line 6291)

**Button:**
- Label: "Save Changes" with save icon
- Position: Bottom right of Account Settings modal
- Function: `saveAndCloseSettings()` - saves all settings then closes modal
- Plus: Auto-save still active (saves on every field change)

**How it works:**
1. User changes any setting
2. Option A: Click "Save Changes" button → Manual save + close
3. Option B: Just close → Auto-save already happened on field change
4. Either way: Data syncs to backend database

---

### 3️⃣ "Where is user preferences stored?"
**Status:** ✅ LOCATED & DOCUMENTED

**Storage Location:**
- **Table:** `user_preferences`
- **Database:** `data/ai_infrastructure.db`
- **17 Fields:**

| Category | Fields |
|----------|--------|
| **Core Preferences** | nickname, communication_style, detail_level, auth_platform, preferred_tools, custom_preferences |
| **Detected Location** | detected_country, detected_city, detected_timezone, detected_ip_address, last_location_check |
| **Manual Overrides** | manual_location_override, manual_timezone_override, use_manual_location, use_manual_timezone |
| **Metadata** | created_at, updated_at |

---

## QUICK TEST

### Test the Flow
```
1. Start server:
   BISTART

2. Open Account Settings:
   - Click profile icon (top right)
   - Click "Account Settings"

3. Change something:
   - Enter nickname: "Test User"
   - Change communication style to "Casual"

4. Notice two save behaviors:
   - Toast notification: "Settings Saved" appears (auto-save)
   - Click "Save Changes" button → Saves + closes modal

5. Refresh page:
   - Settings still there! (persisted to backend)

6. Verify backend:
   - Check browser DevTools → Network
   - See POST to /api/user/preferences
   - Response shows all 17 fields saved
```

---

## WHAT WAS CHANGED

### Backend File
**`AI_infrastructure/routes/user_preferences_routes.py`** (571 lines)

```python
# 1. Enhanced table schema - added 10 new fields
CREATE TABLE user_preferences (
    user_id INTEGER PRIMARY KEY,
    # ... existing 8 fields ...
    nickname TEXT,                          # NEW
    detected_country TEXT,                  # NEW
    detected_city TEXT,                     # NEW
    detected_timezone TEXT,                 # NEW
    detected_ip_address TEXT,               # NEW
    manual_location_override TEXT,          # NEW
    manual_timezone_override TEXT,          # NEW
    use_manual_location INTEGER,            # NEW
    use_manual_timezone INTEGER,            # NEW
    last_location_check TIMESTAMP           # NEW
)

# 2. GET endpoint returns all 17 fields
@user_preferences_bp.route('/preferences', methods=['GET'])
# Selects: user_id, communication_style, detail_level, ... + all 10 new fields

# 3. POST endpoint accepts all 17 fields
@user_preferences_bp.route('/preferences', methods=['POST'])
# Updates: all existing fields + all 10 new geolocation fields

# 4. Helper functions updated
def get_user_preferences(user_id)    # Returns all 17 fields
def save_user_preferences(user_id, preferences_dict)  # Saves all 17
```

### Frontend File
**`UI/business-ai-platform-v2.html`** (17,712 lines)

```javascript
// 1. Save button added to modal footer
<button class="btn btn-primary" onclick="saveAndCloseSettings()">
    <i class="fas fa-save"></i> Save Changes
</button>

// 2. New function: saveAndCloseSettings()
function saveAndCloseSettings() {
    saveSettings();      // Save all values
    closeAccountSettings();  // Close modal
}

// 3. Enhanced: savePersonalisationPreferencesToBackend()
// Now includes detected geolocation fields:
{
    detected_country,
    detected_city,
    detected_timezone,
    detected_ip_address,
    manual_location_override,
    manual_timezone_override,
    use_manual_location,
    use_manual_timezone
}
```

---

## DATABASE STORAGE WORKFLOW

```
┌─────────────────────────────────────────┐
│ User changes nickname in UI             │
└────────────────────┬────────────────────┘
                     ↓
┌─────────────────────────────────────────┐
│ Field onchange event fires              │
│ Calls: saveSettings()                   │
└────────────────────┬────────────────────┘
                     ↓
┌─────────────────────────────────────────┐
│ Two simultaneous actions:               │
│ 1. localStorage.setItem(settings)       │
│ 2. savePersonalisationPreferencesTo     │
│    Backend(userId, preferences)         │
└────────────────────┬────────────────────┘
                     ↓
┌─────────────────────────────────────────┐
│ POST /api/user/preferences              │
│ - JWT token verified                    │
│ - user_id extracted from token          │
│ - All 17 fields in request body         │
└────────────────────┬────────────────────┘
                     ↓
┌─────────────────────────────────────────┐
│ Backend endpoint processes:             │
│ - Validates preference values           │
│ - INSERT or UPDATE database             │
│ - Returns success response              │
└────────────────────┬────────────────────┘
                     ↓
┌─────────────────────────────────────────┐
│ Data now stored in:                     │
│ Table: user_preferences                 │
│ Database: data/ai_infrastructure.db     │
│ Fields: All 17 columns updated          │
└─────────────────────────────────────────┘
```

---

## WHAT GETS SAVED

### When User Clicks "Save Changes"
```json
{
  "nickname": "GP",
  "communication_style": "professional",
  "detail_level": "standard",
  "auth_platform": "auto",
  "detected_country": "Australia",
  "detected_city": "Sydney",
  "detected_timezone": "Australia/Sydney",
  "detected_ip_address": "203.0.113.45",
  "manual_location_override": "",
  "manual_timezone_override": "",
  "use_manual_location": false,
  "use_manual_timezone": false
}
```

### What Gets Stored in Database
```
user_id                    | 1
nickname                   | "GP"
communication_style        | "professional"
detail_level              | "standard"
auth_platform             | "auto"
preferred_tools           | ""
custom_preferences        | null
detected_country          | "Australia"
detected_city             | "Sydney"
detected_timezone         | "Australia/Sydney"
detected_ip_address       | "203.0.113.45"
manual_location_override  | ""
manual_timezone_override  | ""
use_manual_location       | 0
use_manual_timezone       | 0
last_location_check       | 2025-01-XX 14:30:00
created_at               | 2025-01-XX 12:00:00
updated_at               | 2025-01-XX 14:30:00
```

---

## COMMON SCENARIOS

### Scenario 1: User Sets Nickname
```
User: Types "Gerardo" in nickname field
Trigger: onchange event
Result: 
  - Saved to localStorage immediately
  - POST sent to /api/user/preferences
  - Database updated
  - Toast: "Settings Saved"
```

### Scenario 2: User Overrides Timezone
```
User: Checks "Use manual timezone" checkbox
Trigger: onchange event
Result:
  - Checkbox enables timezone selector
  - User selects "America/New_York"
  - Both stored in database
  - use_manual_timezone = 1
  - manual_timezone_override = "America/New_York"
```

### Scenario 3: Explicit Save Button
```
User: Changes 3 settings (nickname, style, timezone)
User: Clicks "Save Changes" button
Trigger: saveAndCloseSettings() function
Result:
  - All 3 changes saved (as above)
  - Modal closes
  - User sees updated Account Settings
```

---

## FILES TO KNOW

| File | Purpose | Key Info |
|------|---------|----------|
| `AI_infrastructure/routes/user_preferences_routes.py` | Backend endpoints | GET/POST /api/user/preferences |
| `UI/business-ai-platform-v2.html` | Frontend UI | Save button + geolocation UI |
| `data/ai_infrastructure.db` | Database | Stores 17-field preferences |
| `data/schema_...db.json` | Schema definition | Table structure |

---

## NEXT STEPS

### For Testing:
1. ✅ Backend endpoints ready
2. ✅ Frontend Save button ready
3. ✅ Database schema updated
4. ✅ Auto-save working
5. Next: Test with actual users

### For Production:
1. ✅ Code complete
2. ⏳ Performance testing needed
3. ⏳ Security review
4. ⏳ Database migration
5. ⏳ User documentation

---

## ANSWERS SUMMARY

| Question | Answer | Where |
|----------|--------|-------|
| Endpoints implemented? | YES ✅ | `user_preferences_routes.py` |
| Save button added? | YES ✅ | `business-ai-platform-v2.html` footer |
| Preferences stored? | YES ✅ | `user_preferences` table in `ai_infrastructure.db` |

---

**Everything is ready to use! Just start the server and test it out.**
