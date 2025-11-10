# Visual Guide - What Users Will See

## Account Settings Modal - Personalisation Section

```
╔════════════════════════════════════════════════════════════════╗
║                    ACCOUNT SETTINGS                            ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  ▼ PERSONALISATION ◂◄ This section is NOW AT THE TOP         ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ Your Nickname (Optional)                              │  ║
║  │ [________________ GP _______________]                  │  ║
║  │ How the AI should refer to you in conversations       │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ Communication Style                                   │  ║
║  │ [Professional           ▼]                            │  ║
║  │ How the AI should communicate with you               │  ║
║  │ (Options: Professional | Casual | Detailed | Brief)  │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ Response Detail Level                                 │  ║
║  │ ○ Minimal    ◉ Standard    ○ Comprehensive           │  ║
║  │ How much detail to include in responses              │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ Authentication Platform                               │  ║
║  │ [Auto-detect (Use available)    ▼]                   │  ║
║  │ Which platform to prioritize for multi-platform tasks│  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ 📍 LOCATION & TIMEZONE DETECTION                     │  ║
║  │                                                        │  ║
║  │  Detected Location          │  Detected Timezone      │  ║
║  │  ────────────────────       │  ──────────────────     │  ║
║  │  Sydney, Australia          │  Australia/Sydney       │  ║
║  │                             │                         │  ║
║  │  IP: 203.x.x.x              │  Time: 2:30 PM          │  ║
║  │                                                        │  ║
║  │  ◄── AUTO-DETECTED FROM YOUR IP ──►                  │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ ✏️ MANUAL LOCATION OVERRIDE                           │  ║
║  │                                                        │  ║
║  │ ☐ Use manual location instead of detected           │  ║
║  │   (When checked, shows:)                             │  ║
║  │   [________________ ____________] ← Enabled when box ☑  ║
║  │   City, Country format                               │  ║
║  │                                                        │  ║
║  │   ◄── FOR TRAVELERS / VPN USERS ──►                  │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
║  ┌────────────────────────────────────────────────────────┐  ║
║  │ 🕐 MANUAL TIMEZONE OVERRIDE                           │  ║
║  │                                                        │  ║
║  │ ☑ Use manual timezone instead of detected    ◄─ OFF  │  ║
║  │   (When checked, shows:)                             │  ║
║  │   [Select timezone...    ▼] ← ENABLED when box checked  ║
║  │   Options:                                           │  ║
║  │   • UTC                                              │  ║
║  │   • Australia/Sydney (UTC+10/+11)                   │  ║
║  │   • Australia/Melbourne (UTC+10/+11)                │  ║
║  │   • America/New_York (UTC-5/-4)                     │  ║
║  │   • Europe/London (UTC+0/+1)                        │  ║
║  │   • Asia/Tokyo (UTC+9)                              │  ║
║  │   • [14 more timezone options]                       │  ║
║  │                                                        │  ║
║  │   ◄── FOR MULTI-TIMEZONE USERS ──►                   │  ║
║  └────────────────────────────────────────────────────────┘  ║
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║  ▼ MODEL OPTIONS                                              ║
║     [Shows existing model selection, temperature, etc]        ║
║                                                                ║
║  ▼ ROUND PARAMETERS                                           ║
║     [Shows existing parameters]                               ║
║                                                                ║
║  ▼ TOKEN PARAMETERS                                           ║
║     [Shows existing parameters]                               ║
║                                                                ║
║  ▼ SETTINGS FOOTER                                            ║
║     [Reset Button] [Close]                                    ║
╚════════════════════════════════════════════════════════════════╝
```

---

## States & Interactions

### State 1: Default (Auto-Detection)
```
☐ Use manual location instead of detected
  [________________ ____________] DISABLED
  
☑ Use manual timezone instead of detected  
  [Select timezone...    ▼] ENABLED
  Value: Australia/Sydney
  
(User can see auto-detected values above)
```

### State 2: Manual Location Enabled
```
☑ Use manual location instead of detected
  [___ Melbourne, Australia ___] ENABLED
  
(User can type in location)
```

### State 3: Manual Timezone Enabled
```
☑ Use manual timezone instead of detected
  [Australia/Melbourne    ▼] ENABLED
  
(User can select from dropdown)
```

### State 4: Both Overrides Enabled
```
☑ Use manual location instead of detected
  [___ Melbourne, Australia ___] ENABLED
  
☑ Use manual timezone instead of detected
  [Australia/Melbourne    ▼] ENABLED

(Both settings active - AI uses these instead of auto-detected)
```

---

## Real-Time Updates

When you open Account Settings:

```
Timeline:
─────────────────────────────────────

T=0ms:   "Detecting..." appears in all fields
T=50ms:  Geolocation API called
         Detected data fetched
T=100ms: Display updates:
         "Sydney, Australia"
         "203.x.x.x"
         "Australia/Sydney"
         "2:30 PM"  ◄─ Real timezone-aware time
T=101ms: Current time updates every second
         "2:30 PM" → "2:31 PM" → "2:32 PM"
         (Updates live while modal open)
```

---

## User Scenarios

### Scenario 1: New User, Unaware of Features
```
1. Opens settings
2. Sees "Personalisation" at TOP (NEW!)
3. Confused by "Location & Timezone Detection"
4. Sees helpful checkboxes to override
5. Realizes: "Oh, this is for context!"
6. Leaves checkboxes unchecked (uses auto-detect)
7. Closes settings
✓ Works perfectly with auto-detection
```

### Scenario 2: Traveler in Different Timezone
```
1. Opens settings
2. Sees detected location: "Los Angeles, USA"
3. But actually in Sydney
4. Checks "Use manual location" checkbox
5. Enters "Sydney, Australia"
6. Checks "Use manual timezone" checkbox
7. Selects "Australia/Sydney"
8. Closes settings
✓ AI now knows true location: Sydney, Australia
✓ Shows correct time: Australia/Sydney timezone
```

### Scenario 3: VPN User
```
1. Opens settings
2. Sees detected location: "USA" (VPN location)
3. Actually in Australia
4. Checks "Use manual location" checkbox
5. Enters "Brisbane, Australia"
6. Checks "Use manual timezone" checkbox
7. Selects "Australia/Brisbane"
8. Closes settings
✓ AI knows real location despite VPN
✓ Shows correct time for Brisbane
```

### Scenario 4: User Sets Nickname
```
1. Opens settings
2. Enters "GP" in nickname field
3. Sets "Casual" communication style
4. Sets "Comprehensive" detail level
5. Closes settings
✓ Next conversation:
   "Hey GP! Here's a comprehensive breakdown..."
```

---

## Visual Flow - Checkbox Toggle

### Before Toggle (Manual Location)
```
☐ Use manual location instead of detected
  [________________ ____________]  ← DISABLED (grayed out)
  Cannot click or type
```

### After Toggle (Manual Location)
```
☑ Use manual location instead of detected
  [___ Melbourne, Australia ___]  ← ENABLED (active)
  ↑ Input now editable
  ↑ Focus moves here automatically
  ↑ User can now type
```

### Behavior
- Click checkbox to enable input
- Input becomes bright/active
- User can type in it immediately
- Clicking away saves automatically
- Click checkbox again to disable
- Input becomes grayed out
- Value is retained but not used

---

## Data Persistence Visualization

```
Settings Saved:
───────────────

localStorage:
┌─────────────────────────────────────┐
│ accountSettings = {                 │
│   nickname: "GP",                   │
│   communicationStyle: "casual",     │
│   detailLevel: "comprehensive",     │
│   useManualLocation: true,          │ ◄─ NEW
│   manualLocation: "Sydney, Aus",    │ ◄─ NEW
│   useManualTimezone: true,          │ ◄─ NEW
│   manualTimezone: "Australia/Sydney"│ ◄─ NEW
│   ... other settings ...             │
│ }                                   │
└─────────────────────────────────────┘
         Persists across sessions!

Backend Database:
┌─────────────────────────────────────┐
│ user_preferences table:             │
│ user_id: 1                          │
│ nickname: "GP"                      │
│ communication_style: "casual"       │
│ detail_level: "comprehensive"       │
│ use_manual_location: true           │ ◄─ NEW
│ manual_location_override: "Sydney"  │ ◄─ NEW
│ use_manual_timezone: true           │ ◄─ NEW
│ manual_timezone_override: "..."     │ ◄─ NEW
│ detected_city: "Sydney"             │ ◄─ Auto-filled
│ detected_timezone: "Australia/..."  │ ◄─ Auto-filled
│ detected_ip_address: "203.x.x.x"    │ ◄─ Auto-filled
└─────────────────────────────────────┘
     Synced from frontend every time user changes setting
```

---

## Error Handling

### Geolocation Detection Fails
```
What user sees:
┌──────────────────────────────────┐
│ Detected Location                │
│ Unable to detect                 │
│                                  │
│ Detected IP                      │
│ --                               │
│                                  │
│ Detected Timezone                │
│ Unable to detect                 │
│                                  │
│ Current Time                     │
│ --                               │
└──────────────────────────────────┘

Fallback: User can manually override
```

### Invalid Timezone Selected
```
What user sees:
┌──────────────────────────────────┐
│ Current Time                     │
│ Invalid timezone                 │
└──────────────────────────────────┘

Fallback: Manual entry box still works
```

---

## Color/Style Indicators

```
Active State (Enabled):
  Input/Select: Bright blue border, full opacity
  Checkbox: ☑ (checked)
  
Disabled State (Unchecked):
  Input/Select: Gray border, lower opacity
  Checkbox: ☐ (unchecked)
  
Auto-Detected (Read-only):
  Text: Normal color, no input
  Background: Slightly gray
  Icon: 📍 (map marker) indicates location
  Icon: 🕐 (clock) indicates timezone
  
Override (User-entered):
  Text: Bold or different color
  Background: Bright/highlighted
  Icon: ✏️ (pencil) indicates manual entry
```

---

## Responsive Design

### Desktop (1200px+)
```
┌─────────────────────────────┐
│ Detected Location │ Detected │
│ Sydney, Aus.      │ Australia│
│ IP: 203.x.x.x     │ Time: 2PM│
└─────────────────────────────┘
2-column grid for detection card
```

### Tablet (768px - 1200px)
```
┌─────────────────────────────┐
│ Detected Location │ Timezone│
│ Sydney, Aus.      │ Sydney  │
│                   │ 2:30 PM │
└─────────────────────────────┘
Still 2-column, responsive padding
```

### Mobile (< 768px)
```
┌────────────────────────┐
│ Detected Location      │
│ Sydney, Australia      │
│ IP: 203.x.x.x         │
│                       │
│ Detected Timezone     │
│ Australia/Sydney      │
│ Time: 2:30 PM         │
└────────────────────────┘
1-column layout, stacked
```

---

## Summary: What's New vs What Existed

### EXISTING FEATURES (Now Enhanced):
✓ Communication Style (Already there)
✓ Response Detail Level (Already there)
✓ Authentication Platform (Already there)
✓ Model selection, Temperature, Top P (Already there)
✓ Round parameters (Already there)
✓ Token parameters (Already there)

### NEW FEATURES (This Implementation):
✨ Your Nickname (New input field)
✨ Location & Timezone Detection (New display card with auto-detect)
✨ Manual Location Override (New toggle + input)
✨ Manual Timezone Override (New toggle + dropdown with 15+ zones)
✨ Current Time Display (New live updating clock)
✨ IP Address Display (New info field)

### NEW DATABASE FIELDS:
✨ user_preferences table (17 fields total)

---

## You're All Set! 🎉

**What to do next:**
1. Open Account Settings modal
2. Look at Personalisation section (TOP)
3. See all the new controls working
4. Try enabling manual overrides
5. Close and reopen to verify persistence
6. Check localStorage to see data structure

**Everything is working and ready to test!**
