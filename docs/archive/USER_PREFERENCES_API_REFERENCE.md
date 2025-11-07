# User Preferences API - Endpoint Reference

## Base URL
```
http://localhost:5001/api/user
```

## Authentication
All endpoints require Bearer token in Authorization header:
```
Authorization: Bearer <JWT_TOKEN>
```

---

## GET /preferences
**Retrieve user preferences from database**

### Request
```http
GET /api/user/preferences HTTP/1.1
Host: localhost:5001
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Success Response (200 OK)
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "nickname": "GP",
    "communication_style": "professional",
    "detail_level": "standard",
    "auth_platform": "auto",
    "preferred_tools": "gmail,google_docs",
    "custom_preferences": null,
    "detected_country": "Australia",
    "detected_city": "Sydney",
    "detected_timezone": "Australia/Sydney",
    "detected_ip_address": "203.0.113.45",
    "manual_location_override": "",
    "manual_timezone_override": "",
    "use_manual_location": 0,
    "use_manual_timezone": 0,
    "last_location_check": "2025-01-20 14:30:45",
    "updated_at": "2025-01-20 14:30:45"
  }
}
```

### Error Responses

**401 Unauthorized - Missing or invalid token**
```json
{
  "success": false,
  "error": "Missing or invalid Authorization header"
}
```

**401 Unauthorized - Invalid token**
```json
{
  "success": false,
  "error": "Invalid or expired token"
}
```

**500 Server Error**
```json
{
  "success": false,
  "error": "Internal server error"
}
```

### cURL Example
```bash
curl -X GET http://localhost:5001/api/user/preferences \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## POST /preferences
**Save or update user preferences in database**

### Request
```http
POST /api/user/preferences HTTP/1.1
Host: localhost:5001
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "nickname": "GP",
  "communication_style": "professional",
  "detail_level": "standard",
  "auth_platform": "auto",
  "preferred_tools": "gmail,google_docs",
  "custom_preferences": null,
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

### Request Body Fields

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| nickname | string | No | "" | User's display name |
| communication_style | string | No | "professional" | professional \| casual \| detailed \| brief |
| detail_level | string | No | "standard" | minimal \| standard \| comprehensive |
| auth_platform | string | No | "auto" | auto \| microsoft \| google |
| preferred_tools | string | No | "" | Comma-separated tool names |
| custom_preferences | object | No | null | Custom JSON data |
| detected_country | string | No | "" | Country from IP detection |
| detected_city | string | No | "" | City from IP detection |
| detected_timezone | string | No | "" | IANA timezone |
| detected_ip_address | string | No | "" | IP address |
| manual_location_override | string | No | "" | User's custom location |
| manual_timezone_override | string | No | "" | User's custom timezone |
| use_manual_location | boolean | No | false | Use manual instead of detected |
| use_manual_timezone | boolean | No | false | Use manual instead of detected |

### Success Response (200 OK)
```json
{
  "success": true,
  "message": "Preferences saved successfully",
  "data": {
    "user_id": 1,
    "nickname": "GP",
    "communication_style": "professional",
    "detail_level": "standard",
    "auth_platform": "auto",
    "preferred_tools": "gmail,google_docs",
    "custom_preferences": null,
    "detected_country": "Australia",
    "detected_city": "Sydney",
    "detected_timezone": "Australia/Sydney",
    "detected_ip_address": "203.0.113.45",
    "manual_location_override": "",
    "manual_timezone_override": "",
    "use_manual_location": 0,
    "use_manual_timezone": 0,
    "last_location_check": "2025-01-20 14:30:45",
    "updated_at": "2025-01-20 14:30:45"
  }
}
```

### Error Responses

**400 Bad Request - Invalid JSON**
```json
{
  "success": false,
  "error": "Request body must be JSON"
}
```

**401 Unauthorized - Missing token**
```json
{
  "success": false,
  "error": "Missing or invalid Authorization header"
}
```

**401 Unauthorized - Invalid token**
```json
{
  "success": false,
  "error": "Invalid or expired token"
}
```

**500 Server Error**
```json
{
  "success": false,
  "error": "Internal server error"
}
```

### cURL Examples

**Save basic preferences:**
```bash
curl -X POST http://localhost:5001/api/user/preferences \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "nickname": "GP",
    "communication_style": "professional",
    "detail_level": "standard"
  }'
```

**Save with geolocation:**
```bash
curl -X POST http://localhost:5001/api/user/preferences \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "nickname": "GP",
    "communication_style": "professional",
    "detail_level": "standard",
    "detected_country": "Australia",
    "detected_city": "Sydney",
    "detected_timezone": "Australia/Sydney",
    "detected_ip_address": "203.0.113.45"
  }'
```

**Save with manual overrides:**
```bash
curl -X POST http://localhost:5001/api/user/preferences \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "nickname": "GP",
    "communication_style": "professional",
    "use_manual_location": true,
    "manual_location_override": "Melbourne, Australia",
    "use_manual_timezone": true,
    "manual_timezone_override": "Australia/Melbourne"
  }'
```

---

## Python Client Example

```python
import requests

# Configuration
API_BASE_URL = 'http://localhost:5001'
JWT_TOKEN = 'your_jwt_token_here'

# Headers
headers = {
    'Authorization': f'Bearer {JWT_TOKEN}',
    'Content-Type': 'application/json'
}

# GET preferences
def get_preferences():
    response = requests.get(
        f'{API_BASE_URL}/api/user/preferences',
        headers=headers
    )
    return response.json()

# Save preferences
def save_preferences(prefs):
    response = requests.post(
        f'{API_BASE_URL}/api/user/preferences',
        headers=headers,
        json=prefs
    )
    return response.json()

# Usage
if __name__ == '__main__':
    # Get current preferences
    prefs = get_preferences()
    print('Current preferences:', prefs)
    
    # Update preferences
    new_prefs = {
        'nickname': 'GP',
        'communication_style': 'professional',
        'detail_level': 'standard',
        'detected_country': 'Australia',
        'detected_city': 'Sydney'
    }
    
    result = save_preferences(new_prefs)
    print('Save result:', result)
```

---

## JavaScript Client Example

```javascript
// Configuration
const API_BASE_URL = 'http://localhost:5001';
const JWT_TOKEN = localStorage.getItem('authToken');

// Helper function
async function apiCall(method, endpoint, body = null) {
    const options = {
        method: method,
        headers: {
            'Authorization': `Bearer ${JWT_TOKEN}`,
            'Content-Type': 'application/json'
        }
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        options
    );
    
    return response.json();
}

// Get preferences
async function getPreferences() {
    return await apiCall('GET', '/api/user/preferences');
}

// Save preferences
async function savePreferences(prefs) {
    return await apiCall('POST', '/api/user/preferences', prefs);
}

// Usage
(async () => {
    // Get current
    const current = await getPreferences();
    console.log('Current:', current);
    
    // Save new
    const saved = await savePreferences({
        nickname: 'GP',
        communication_style: 'professional',
        detail_level: 'standard',
        detected_country: 'Australia',
        detected_city: 'Sydney',
        detected_timezone: 'Australia/Sydney',
        detected_ip_address: '203.0.113.45'
    });
    console.log('Saved:', saved);
})();
```

---

## Response Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid JSON or missing required fields |
| 401 | Unauthorized | Missing or invalid JWT token |
| 500 | Server Error | Database or server error |

---

## Validation Rules

### Preferences Validation
- `communication_style` must be: professional, casual, detailed, or brief
  - If invalid, defaults to "professional"
- `detail_level` must be: minimal, standard, or comprehensive
  - If invalid, defaults to "standard"
- `auth_platform` must be: auto, microsoft, or google
  - If invalid, defaults to "auto"
- Boolean values (use_manual_*) converted to 0 or 1 in database
- Strings are trimmed and stored as-is
- Null custom_preferences is allowed

### Database Constraints
- `user_id` must exist in `users` table (foreign key)
- Cannot save preferences for other users (validated via JWT)
- Maximum 1 record per user_id

---

## Field Descriptions

### Core Preferences
- **nickname**: How AI should address user (e.g., "GP", "Gerardo")
- **communication_style**: Tone and formality of responses
- **detail_level**: Amount of detail in responses
- **auth_platform**: Which platform to prioritize for multi-platform tasks
- **preferred_tools**: User's most-used tools (for recommendations)
- **custom_preferences**: Any additional custom data as JSON

### Detected Geolocation
- **detected_country**: Country name (auto-detected from IP)
- **detected_city**: City name (auto-detected from IP)
- **detected_timezone**: IANA timezone ID (auto-detected)
- **detected_ip_address**: Client IP that was used for detection
- **last_location_check**: When geolocation was last detected

### Manual Overrides
- **manual_location_override**: User's custom location (e.g., "Sydney, Australia")
- **manual_timezone_override**: User's custom timezone (e.g., "Australia/Sydney")
- **use_manual_location**: Boolean - whether to use manual instead of detected
- **use_manual_timezone**: Boolean - whether to use manual instead of detected

### Metadata
- **updated_at**: ISO 8601 timestamp of last update
- **created_at**: ISO 8601 timestamp of record creation

---

## Database Storage

All preferences are stored in SQLite table:
```
data/ai_infrastructure.db → user_preferences table
```

Each user has exactly 1 row with their 17 fields.

---

## Rate Limiting

No rate limiting currently implemented.
**Recommended:** Add rate limiting in production
- 10 requests per minute per user
- 1000 requests per hour per endpoint

---

## Troubleshooting

### 401 Unauthorized
- ✓ Verify JWT token is valid
- ✓ Check token hasn't expired
- ✓ Ensure Authorization header format: `Bearer <token>`

### 400 Bad Request
- ✓ Verify request is valid JSON
- ✓ Check all required fields present
- ✓ Verify field types (string, boolean, etc.)

### 500 Internal Server Error
- ✓ Check backend logs
- ✓ Verify database connection
- ✓ Ensure user_id exists in users table

### Preferences not saving
- ✓ Check network tab for request/response
- ✓ Verify POST body is correct JSON
- ✓ Check database for INSERT/UPDATE success
- ✓ Verify JWT token user_id matches

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-20 | Initial implementation with 17 fields |

---

**Ready to integrate! Use these endpoints in your applications.**
