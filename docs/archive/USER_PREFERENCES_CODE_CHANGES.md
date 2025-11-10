# User Preferences Implementation - Code Changes Reference

## CHANGES AT A GLANCE

### Backend (Python)
- **File:** `AI_infrastructure/routes/user_preferences_routes.py`
- **Lines Changed:** ~100 lines modified across multiple functions
- **Key Changes:** Added 10 geolocation fields to table schema and all queries

### Frontend (HTML/JavaScript)
- **File:** `UI/business-ai-platform-v2.html`
- **Lines Changed:** ~5 locations modified
- **Key Changes:** Save button + enhanced geolocation sync

---

## BACKEND CHANGES DETAIL

### Change 1: Enhanced Table Schema (Lines 65-88)

**OLD:**
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_preferences (
        user_id INTEGER PRIMARY KEY,
        communication_style TEXT DEFAULT 'professional',
        detail_level TEXT DEFAULT 'standard',
        auth_platform TEXT DEFAULT 'auto',
        preferred_tools TEXT,
        custom_preferences TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")
```

**NEW:**
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_preferences (
        user_id INTEGER PRIMARY KEY,
        communication_style TEXT DEFAULT 'professional',
        detail_level TEXT DEFAULT 'standard',
        auth_platform TEXT DEFAULT 'auto',
        preferred_tools TEXT,
        custom_preferences TEXT,
        nickname TEXT,
        detected_country TEXT,
        detected_city TEXT,
        detected_timezone TEXT,
        detected_ip_address TEXT,
        manual_location_override TEXT,
        manual_timezone_override TEXT,
        use_manual_location INTEGER DEFAULT 0,
        use_manual_timezone INTEGER DEFAULT 0,
        last_location_check TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")
```

**Additions:**
- 6 new fields: `nickname`, `detected_country`, `detected_city`, `detected_timezone`, `detected_ip_address`, `last_location_check`
- 4 new fields: `manual_location_override`, `manual_timezone_override`, `use_manual_location`, `use_manual_timezone`

---

### Change 2: GET Endpoint SELECT Query (Lines 121-140)

**OLD:**
```python
cursor.execute("""
    SELECT 
        user_id,
        communication_style,
        detail_level,
        auth_platform,
        preferred_tools,
        custom_preferences,
        updated_at
    FROM user_preferences
    WHERE user_id = ?
""", (user_id,))
```

**NEW:**
```python
cursor.execute("""
    SELECT 
        user_id,
        communication_style,
        detail_level,
        auth_platform,
        preferred_tools,
        custom_preferences,
        nickname,
        detected_country,
        detected_city,
        detected_timezone,
        detected_ip_address,
        manual_location_override,
        manual_timezone_override,
        use_manual_location,
        use_manual_timezone,
        last_location_check,
        updated_at
    FROM user_preferences
    WHERE user_id = ?
""", (user_id,))
```

---

### Change 3: GET Endpoint Default Response (Lines 144-167)

**OLD:**
```python
if not row:
    return jsonify({
        'success': True,
        'data': {
            'user_id': user_id,
            'communication_style': 'professional',
            'detail_level': 'standard',
            'auth_platform': 'auto',
            'preferred_tools': '',
            'custom_preferences': None,
            'updated_at': None
        }
    }), 200
```

**NEW:**
```python
if not row:
    return jsonify({
        'success': True,
        'data': {
            'user_id': user_id,
            'communication_style': 'professional',
            'detail_level': 'standard',
            'auth_platform': 'auto',
            'preferred_tools': '',
            'custom_preferences': None,
            'nickname': '',
            'detected_country': '',
            'detected_city': '',
            'detected_timezone': '',
            'detected_ip_address': '',
            'manual_location_override': '',
            'manual_timezone_override': '',
            'use_manual_location': 0,
            'use_manual_timezone': 0,
            'last_location_check': None,
            'updated_at': None
        }
    }), 200
```

---

### Change 4: GET Endpoint Response (Lines 169-189)

**OLD:**
```python
return jsonify({
    'success': True,
    'data': {
        'user_id': row['user_id'],
        'communication_style': row['communication_style'],
        'detail_level': row['detail_level'],
        'auth_platform': row['auth_platform'],
        'preferred_tools': row['preferred_tools'],
        'custom_preferences': row['custom_preferences'],
        'updated_at': row['updated_at']
    }
}), 200
```

**NEW:**
```python
return jsonify({
    'success': True,
    'data': {
        'user_id': row['user_id'],
        'communication_style': row['communication_style'],
        'detail_level': row['detail_level'],
        'auth_platform': row['auth_platform'],
        'preferred_tools': row['preferred_tools'],
        'custom_preferences': row['custom_preferences'],
        'nickname': row['nickname'],
        'detected_country': row['detected_country'],
        'detected_city': row['detected_city'],
        'detected_timezone': row['detected_timezone'],
        'detected_ip_address': row['detected_ip_address'],
        'manual_location_override': row['manual_location_override'],
        'manual_timezone_override': row['manual_timezone_override'],
        'use_manual_location': row['use_manual_location'],
        'use_manual_timezone': row['use_manual_timezone'],
        'last_location_check': row['last_location_check'],
        'updated_at': row['updated_at']
    }
}), 200
```

---

### Change 5: POST Endpoint - Extract Request Values (Lines 232-249)

**OLD:**
```python
preferred_tools = data.get('preferred_tools', '')
custom_preferences = data.get('custom_preferences')

# Convert custom_preferences dict to JSON string if provided
if custom_preferences:
    import json
    custom_preferences = json.dumps(custom_preferences)

# Save to database
conn = get_db_connection()
```

**NEW:**
```python
preferred_tools = data.get('preferred_tools', '')
custom_preferences = data.get('custom_preferences')
nickname = data.get('nickname', '')
detected_country = data.get('detected_country', '')
detected_city = data.get('detected_city', '')
detected_timezone = data.get('detected_timezone', '')
detected_ip_address = data.get('detected_ip_address', '')
manual_location_override = data.get('manual_location_override', '')
manual_timezone_override = data.get('manual_timezone_override', '')
use_manual_location = 1 if data.get('use_manual_location', False) else 0
use_manual_timezone = 1 if data.get('use_manual_timezone', False) else 0

# Convert custom_preferences dict to JSON string if provided
if custom_preferences:
    import json
    custom_preferences = json.dumps(custom_preferences)

# Save to database
conn = get_db_connection()
```

---

### Change 6: POST Endpoint - UPDATE Query (Lines 265-283)

**OLD:**
```python
cursor.execute("""
    UPDATE user_preferences
    SET communication_style = ?,
        detail_level = ?,
        auth_platform = ?,
        preferred_tools = ?,
        custom_preferences = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = ?
""", (communication_style, detail_level, auth_platform, preferred_tools, custom_preferences, user_id))
```

**NEW:**
```python
cursor.execute("""
    UPDATE user_preferences
    SET communication_style = ?,
        detail_level = ?,
        auth_platform = ?,
        preferred_tools = ?,
        custom_preferences = ?,
        nickname = ?,
        detected_country = ?,
        detected_city = ?,
        detected_timezone = ?,
        detected_ip_address = ?,
        manual_location_override = ?,
        manual_timezone_override = ?,
        use_manual_location = ?,
        use_manual_timezone = ?,
        last_location_check = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = ?
""", (communication_style, detail_level, auth_platform, preferred_tools, custom_preferences, 
      nickname, detected_country, detected_city, detected_timezone, detected_ip_address,
      manual_location_override, manual_timezone_override, use_manual_location, use_manual_timezone, user_id))
```

---

### Change 7: POST Endpoint - INSERT Query (Lines 285-295)

**OLD:**
```python
cursor.execute("""
    INSERT INTO user_preferences
    (user_id, communication_style, detail_level, auth_platform, preferred_tools, custom_preferences)
    VALUES (?, ?, ?, ?, ?, ?)
""", (user_id, communication_style, detail_level, auth_platform, preferred_tools, custom_preferences))
```

**NEW:**
```python
cursor.execute("""
    INSERT INTO user_preferences
    (user_id, communication_style, detail_level, auth_platform, preferred_tools, custom_preferences,
     nickname, detected_country, detected_city, detected_timezone, detected_ip_address,
     manual_location_override, manual_timezone_override, use_manual_location, use_manual_timezone, last_location_check)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
""", (user_id, communication_style, detail_level, auth_platform, preferred_tools, custom_preferences,
      nickname, detected_country, detected_city, detected_timezone, detected_ip_address,
      manual_location_override, manual_timezone_override, use_manual_location, use_manual_timezone))
```

---

### Change 8: POST Endpoint - SELECT for Response (Lines 298-314)

**OLD:**
```python
cursor.execute("""
    SELECT 
        user_id,
        communication_style,
        detail_level,
        auth_platform,
        preferred_tools,
        custom_preferences,
        updated_at
    FROM user_preferences
    WHERE user_id = ?
""", (user_id,))
```

**NEW:**
```python
cursor.execute("""
    SELECT 
        user_id,
        communication_style,
        detail_level,
        auth_platform,
        preferred_tools,
        custom_preferences,
        nickname,
        detected_country,
        detected_city,
        detected_timezone,
        detected_ip_address,
        manual_location_override,
        manual_timezone_override,
        use_manual_location,
        use_manual_timezone,
        last_location_check,
        updated_at
    FROM user_preferences
    WHERE user_id = ?
""", (user_id,))
```

---

### Change 9: POST Endpoint - Response JSON (Lines 317-336)

**OLD:**
```python
return jsonify({
    'success': True,
    'message': 'Preferences saved successfully',
    'data': {
        'user_id': row['user_id'],
        'communication_style': row['communication_style'],
        'detail_level': row['detail_level'],
        'auth_platform': row['auth_platform'],
        'preferred_tools': row['preferred_tools'],
        'custom_preferences': row['custom_preferences'],
        'updated_at': row['updated_at']
    }
}), 200
```

**NEW:**
```python
return jsonify({
    'success': True,
    'message': 'Preferences saved successfully',
    'data': {
        'user_id': row['user_id'],
        'communication_style': row['communication_style'],
        'detail_level': row['detail_level'],
        'auth_platform': row['auth_platform'],
        'preferred_tools': row['preferred_tools'],
        'custom_preferences': row['custom_preferences'],
        'nickname': row['nickname'],
        'detected_country': row['detected_country'],
        'detected_city': row['detected_city'],
        'detected_timezone': row['detected_timezone'],
        'detected_ip_address': row['detected_ip_address'],
        'manual_location_override': row['manual_location_override'],
        'manual_timezone_override': row['manual_timezone_override'],
        'use_manual_location': row['use_manual_location'],
        'use_manual_timezone': row['use_manual_timezone'],
        'last_location_check': row['last_location_check'],
        'updated_at': row['updated_at']
    }
}), 200
```

---

### Change 10: get_user_preferences() Helper (Lines 345-402)

**OLD:**
```python
def get_user_preferences(user_id):
    # ...
    cursor.execute("""
        SELECT 
            user_id,
            communication_style,
            detail_level,
            auth_platform,
            preferred_tools,
            custom_preferences,
            updated_at
        FROM user_preferences
        WHERE user_id = ?
    """, (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        'user_id': row['user_id'],
        'communication_style': row['communication_style'],
        'detail_level': row['detail_level'],
        'auth_platform': row['auth_platform'],
        'preferred_tools': row['preferred_tools'],
        'custom_preferences': row['custom_preferences'],
        'updated_at': row['updated_at']
    }
```

**NEW:**
```python
def get_user_preferences(user_id):
    # ...
    cursor.execute("""
        SELECT 
            user_id,
            communication_style,
            detail_level,
            auth_platform,
            preferred_tools,
            custom_preferences,
            nickname,
            detected_country,
            detected_city,
            detected_timezone,
            detected_ip_address,
            manual_location_override,
            manual_timezone_override,
            use_manual_location,
            use_manual_timezone,
            last_location_check,
            updated_at
        FROM user_preferences
        WHERE user_id = ?
    """, (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        'user_id': row['user_id'],
        'communication_style': row['communication_style'],
        'detail_level': row['detail_level'],
        'auth_platform': row['auth_platform'],
        'preferred_tools': row['preferred_tools'],
        'custom_preferences': row['custom_preferences'],
        'nickname': row['nickname'],
        'detected_country': row['detected_country'],
        'detected_city': row['detected_city'],
        'detected_timezone': row['detected_timezone'],
        'detected_ip_address': row['detected_ip_address'],
        'manual_location_override': row['manual_location_override'],
        'manual_timezone_override': row['manual_timezone_override'],
        'use_manual_location': row['use_manual_location'],
        'use_manual_timezone': row['use_manual_timezone'],
        'last_location_check': row['last_location_check'],
        'updated_at': row['updated_at']
    }
```

---

### Change 11: save_user_preferences() Helper (Lines 479-572)

**Additions:**
- Extract 10 new fields from preferences_dict
- Add them to UPDATE query
- Add them to INSERT query

**KEY SNIPPET:**
```python
# NEW: Extract geolocation fields
nickname = preferences_dict.get('nickname', '')
detected_country = preferences_dict.get('detected_country', '')
detected_city = preferences_dict.get('detected_city', '')
detected_timezone = preferences_dict.get('detected_timezone', '')
detected_ip_address = preferences_dict.get('detected_ip_address', '')
manual_location_override = preferences_dict.get('manual_location_override', '')
manual_timezone_override = preferences_dict.get('manual_timezone_override', '')
use_manual_location = 1 if preferences_dict.get('use_manual_location', False) else 0
use_manual_timezone = 1 if preferences_dict.get('use_manual_timezone', False) else 0

# Then in UPDATE query:
manual_location_override = ?,
manual_timezone_override = ?,
use_manual_location = ?,
use_manual_timezone = ?,
last_location_check = CURRENT_TIMESTAMP,
```

---

## FRONTEND CHANGES DETAIL

### Change 1: Add Save Button to Modal Footer (Line 6291)

**OLD:**
```html
<div class="modal-footer"
    style="display: flex; gap: var(--space-2); padding: var(--space-4); border-top: 1px solid var(--border-default);">
    <button class="btn btn-secondary" onclick="resetAccountSettings()">
        <i class="fas fa-redo"></i> Reset to Defaults
    </button>
    <button class="btn btn-primary" onclick="closeAccountSettings()">
        <i class="fas fa-check"></i> Close
    </button>
</div>
```

**NEW:**
```html
<div class="modal-footer"
    style="display: flex; gap: var(--space-2); padding: var(--space-4); border-top: 1px solid var(--border-default); justify-content: space-between;">
    <button class="btn btn-secondary" onclick="resetAccountSettings()">
        <i class="fas fa-redo"></i> Reset to Defaults
    </button>
    <div style="display: flex; gap: var(--space-2);">
        <button class="btn btn-primary" id="savePreferencesBtn" onclick="saveAndCloseSettings()" style="display: none;">
            <i class="fas fa-save"></i> Save Changes
        </button>
        <button class="btn btn-primary" onclick="closeAccountSettings()">
            <i class="fas fa-check"></i> Close
        </button>
    </div>
</div>
```

**Changes:**
- Added `justify-content: space-between` to footer
- Wrapped close buttons in a flex div
- Added Save button (hidden by default)
- Save button calls `saveAndCloseSettings()`

---

### Change 2: Add saveAndCloseSettings() Function (After line 12726)

**NEW FUNCTION:**
```javascript
function saveAndCloseSettings() {
    saveSettings();
    closeAccountSettings();
}
```

**Purpose:** Provides explicit save action with confirmation

---

### Change 3: Enhance savePersonalisationPreferencesToBackend() (Lines 12883-12950)

**OLD:**
```javascript
async function savePersonalisationPreferencesToBackend(userId, preferences) {
    try {
        const backendUrl = window.API_BASE_URL || 'http://localhost:5001';
        const response = await fetch(`${backendUrl}/api/user/preferences`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify({
                user_id: userId,
                nickname: preferences.nickname,
                communication_style: preferences.communicationStyle,
                detail_level: preferences.detailLevel,
                auth_platform: preferences.authPlatform,
                use_manual_location: preferences.useManualLocation,
                use_manual_timezone: preferences.useManualTimezone,
                manual_location_override: preferences.manualLocation,
                manual_timezone_override: preferences.manualTimezone
            })
        });

        if (!response.ok) {
            console.warn('Failed to save preferences to backend:', response.statusText);
        }
    } catch (error) {
        console.warn('Error saving preferences to backend:', error.message);
    }
}
```

**NEW:**
```javascript
async function savePersonalisationPreferencesToBackend(userId, preferences) {
    try {
        const backendUrl = window.API_BASE_URL || 'http://localhost:5001';
        
        // Get detected geolocation data from UI
        const detectedLocation = document.getElementById('detectedLocation').textContent;
        const detectedIP = document.getElementById('detectedIP').textContent;
        const detectedTimezone = document.getElementById('detectedTimezone').textContent;
        
        // Parse detected location into city and country
        let detectedCity = '';
        let detectedCountry = '';
        if (detectedLocation && detectedLocation !== 'Detecting...' && detectedLocation !== 'Unable to detect') {
            const parts = detectedLocation.split(', ');
            if (parts.length >= 2) {
                detectedCity = parts[0];
                detectedCountry = parts[1];
            } else {
                detectedCountry = parts[0];
            }
        }
        
        const response = await fetch(`${backendUrl}/api/user/preferences`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify({
                user_id: userId,
                nickname: preferences.nickname,
                communication_style: preferences.communicationStyle,
                detail_level: preferences.detailLevel,
                auth_platform: preferences.authPlatform,
                use_manual_location: preferences.useManualLocation,
                use_manual_timezone: preferences.useManualTimezone,
                manual_location_override: preferences.manualLocation,
                manual_timezone_override: preferences.manualTimezone,
                detected_country: detectedCountry,
                detected_city: detectedCity,
                detected_timezone: detectedTimezone,
                detected_ip_address: detectedIP
            })
        });

        if (!response.ok) {
            console.warn('Failed to save preferences to backend:', response.statusText);
        } else {
            const data = await response.json();
            console.log('Preferences saved successfully:', data);
        }
    } catch (error) {
        console.warn('Error saving preferences to backend:', error.message);
    }
}
```

**Changes:**
- Extract detected geolocation from UI elements
- Parse `detectedLocation` into city/country parts
- Include 4 new fields in POST body:
  - `detected_country`
  - `detected_city`
  - `detected_timezone`
  - `detected_ip_address`

---

## SUMMARY OF CHANGES

| Component | Old | New | Change |
|-----------|-----|-----|--------|
| Table schema | 8 fields | 18 fields | +10 geolocation |
| GET query SELECT | 7 fields | 17 fields | All new fields |
| POST query UPDATE | 6 params | 16 params | All new fields |
| POST query INSERT | 6 params | 16 params | All new fields |
| Response JSON | 7 fields | 17 fields | All new fields |
| Helper functions | 7 fields | 17 fields | Updated both |
| Frontend buttons | 2 buttons | 3 buttons | Added Save |
| Backend sync | 8 fields | 12 fields | +4 geolocation |

---

## TESTING CHECKLIST

After changes, verify:
- [ ] Backend server starts without errors
- [ ] GET /api/user/preferences returns 17 fields
- [ ] POST /api/user/preferences accepts 17 fields
- [ ] Save button appears in modal
- [ ] Click Save button → saves + closes
- [ ] Refresh page → settings persist
- [ ] Auto-save still works on field change
- [ ] Database shows all 17 columns
- [ ] No JavaScript errors in console

---

**All changes complete and ready for testing!**
