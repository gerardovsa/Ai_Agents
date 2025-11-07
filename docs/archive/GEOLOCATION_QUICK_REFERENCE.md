# Geolocation & Personalisation - Quick Reference

## What Users Will See

### Personalisation Section (Top of Account Settings)

```
┌─ PERSONALISATION ─────────────────────────────────┐
│                                                   │
│  Your Nickname                                    │
│  [_________________] (Optional)                  │
│  How the AI should refer to you                   │
│                                                   │
│  Communication Style                              │
│  [Professional ▼]                                 │
│  How the AI should communicate with you          │
│                                                   │
│  Response Detail Level                            │
│  ⊙ Minimal  ○ Standard  ○ Comprehensive          │
│  How much detail to include                       │
│                                                   │
│  Authentication Platform                          │
│  [Auto-detect ▼]                                 │
│  Which platform to prioritize                    │
│                                                   │
│  📍 LOCATION & TIMEZONE DETECTION                 │
│  ┌──────────────────┬──────────────────┐         │
│  │ Detected Loc.    │ Detected TZ      │         │
│  │ Sydney,          │ Australia/       │         │
│  │ Australia        │ Sydney           │         │
│  │                  │                  │         │
│  │ IP: 203.x.x.x    │ Time: 2:30 PM    │         │
│  └──────────────────┴──────────────────┘         │
│                                                   │
│  ✏️ MANUAL LOCATION OVERRIDE                     │
│  ☐ Use manual location instead of detected      │
│    [________________] (disabled)                  │
│    City, Country format                           │
│                                                   │
│  🕐 MANUAL TIMEZONE OVERRIDE                     │
│  ☐ Use manual timezone instead of detected      │
│    [Select timezone... ▼] (disabled)             │
│                                                   │
└───────────────────────────────────────────────────┘
```

## Database Fields

**Table:** `user_preferences`

| Field | Type | Auto-populated? | User can change? |
|-------|------|-----------------|-----------------|
| `nickname` | TEXT | No | Yes |
| `communication_style` | TEXT | No | Yes |
| `detail_level` | TEXT | No | Yes |
| `detected_country` | TEXT | Yes (from IP) | No |
| `detected_city` | TEXT | Yes (from IP) | No |
| `detected_timezone` | TEXT | Yes (from IP) | No |
| `detected_ip_address` | TEXT | Yes (from IP) | No |
| `manual_location_override` | TEXT | No | Yes |
| `manual_timezone_override` | TEXT | No | Yes |
| `use_manual_location` | BOOLEAN | No | Yes |
| `use_manual_timezone` | BOOLEAN | No | Yes |
| `last_location_check` | TIMESTAMP | Yes (on detect) | No |

## JavaScript Functions

| Function | Purpose | Triggered by |
|----------|---------|--------------|
| `detectAndDisplayGeolocation()` | Fetch IP location and display | Page load, manual refresh |
| `displayGeolocationData(data)` | Display location on UI | detectAndDisplayGeolocation() |
| `updateCurrentTime(timezone)` | Show current time in timezone | displayGeolocationData() |
| `toggleManualLocation()` | Enable/disable location input | User clicks checkbox |
| `toggleManualTimezone()` | Enable/disable timezone dropdown | User clicks checkbox |
| `saveSettings()` | Save all settings to localStorage + backend | User changes any setting |
| `savePersonalisationPreferencesToBackend()` | POST to backend API | saveSettings() |

## Timezone Options Available

**Australia:**
- Australia/Sydney (UTC+10/+11)
- Australia/Melbourne (UTC+10/+11)
- Australia/Brisbane (UTC+10)
- Australia/Perth (UTC+8)
- Australia/Adelaide (UTC+9:30/+10:30)

**North America:**
- America/New_York (UTC-5/-4)
- America/Chicago (UTC-6/-5)
- America/Denver (UTC-7/-6)
- America/Los_Angeles (UTC-8/-7)

**Europe:**
- Europe/London (UTC+0/+1)
- Europe/Paris (UTC+1/+2)

**Asia:**
- Asia/Tokyo (UTC+9)
- Asia/Singapore (UTC+8)
- Asia/Bangkok (UTC+7)
- Asia/Dubai (UTC+4)
- Asia/Kolkata (UTC+5:30)
- Asia/Hong_Kong (UTC+8)

**Universal:**
- UTC (Coordinated Universal Time)

## Data Flow

### Settings Save
```
User changes setting (e.g., nickname, manual location)
         ↓
saveSettings() runs
         ↓
Settings object created with all current values
         ↓
Saved to localStorage (key: "accountSettings")
         ↓
If user authenticated:
  savePersonalisationPreferencesToBackend() runs
         ↓
  POST to /api/user/preferences with:
    - nickname
    - communication_style
    - detail_level
    - auth_platform
    - use_manual_location / manual_location_override
    - use_manual_timezone / manual_timezone_override
```

### Geolocation Detection
```
User opens Account Settings
         ↓
loadAccountSettings() runs
         ↓
detectAndDisplayGeolocation() runs
         ↓
Tries /api/geolocation/detect (backend)
         ↓
Falls back to ipapi.co (free public service)
         ↓
Receives: country, city, timezone, ip_address
         ↓
displayGeolocationData() called
         ↓
UI fields updated with:
  - Detected Location: "{city}, {country}"
  - Detected IP: "{ip}"
  - Detected Timezone: "{timezone}"
  - Current Time: "2:30 PM" (in that timezone)
```

## User Stories

### Story 1: First-Time User
**As a:** New user  
**I want:** AI to know where I am and what time it is for me  
**So that:** AI can give location-aware and time-aware responses  

**Flow:**
1. Open Account Settings
2. See "Location & Timezone Detection" card with auto-detected values
3. If in different timezone/country, enable manual override
4. Close settings - all saved automatically

### Story 2: Remote Worker
**As a:** Person traveling or using VPN  
**I want:** Override detected location/timezone  
**So that:** AI uses correct location for my actual location  

**Flow:**
1. Open Account Settings
2. Check "Use manual location instead of detected"
3. Enter "Melbourne, Australia"
4. Check "Use manual timezone instead of detected"
5. Select "Australia/Melbourne" from dropdown
6. Close settings - all saved

### Story 3: Personalized Communication
**As a:** User  
**I want:** Set my nickname and communication preference  
**So that:** AI responds in a style I prefer and addresses me by name  

**Flow:**
1. Open Account Settings
2. Enter "GP" in nickname field
3. Select "Casual (Friendly, conversational)" for communication style
4. Select "Comprehensive" for detail level
5. Close settings
6. Next conversation, AI addresses user as "GP" in casual, detailed tone

---

## Implementation Summary

✅ **Database:** `user_preferences` table created with all fields  
✅ **UI:** Nickname, location detection, manual override controls added  
✅ **Geolocation:** Client-side detection via ipapi.co (fallback to backend)  
✅ **Time Display:** Real-time clock showing time in user's timezone  
✅ **Persistence:** localStorage + backend sync  
✅ **Toggle Controls:** Manual overrides enable/disable smartly  

⏳ **Pending:**
- Backend endpoint `/api/geolocation/detect` (optional - falls back to ipapi.co)
- System prompt injection with nickname, location, timezone
- Response personalization based on communication_style + detail_level
- Geographic context in tool recommendations

---

**Status:** READY FOR TESTING ✅  
**Test:** Open Account Settings modal and verify all fields display and work correctly
