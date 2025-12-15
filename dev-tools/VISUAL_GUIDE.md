# Module Creator & Verifier - Visual Guide

## 🖥️ What You'll See

### Header
```
┌────────────────────────────────────────────────────────────────┐
│ 🧰 Module Creator & Verifier                                   │
│                                                                 │
│ ● Backend Connected    ● Database Connected                    │
└────────────────────────────────────────────────────────────────┘
```
- **Green dot** = Connected
- **Red dot** = Disconnected
- **Gray dot** = Unknown

---

### Main Interface (Three Panels)

```
┌──────────────┬─────────────────────────┬─────────────────────┐
│              │                         │                     │
│  ⚙️ CONFIG   │  📋 PREVIEW & TESTING  │  🔍 CONSOLE & LOGS  │
│              │                         │                     │
│ Module Type  │  [Live Preview Tab]    │  Console Output:    │
│ ○ New Module │  [API Tester Tab]      │                     │
│ ○ Existing   │  [Manifest Editor Tab] │  LOG: Initialized   │
│              │                         │  INFO: Connected    │
│ Module ID    │                         │  WARN: Validation   │
│ [________]   │                         │  ERROR: Failed      │
│              │                         │                     │
│ Name         │                         │  Network Log:       │
│ [________]   │                         │  GET /api/modules   │
│              │                         │  POST /create       │
│ Version      │                         │                     │
│ [1.0.0]      │                         │                     │
│              │                         │                     │
│ Files:       │                         │                     │
│ ☑ HTML       │                         │                     │
│ ☑ JavaScript │                         │                     │
│ ☑ CSS        │                         │                     │
│ ☐ Routes     │                         │                     │
│              │                         │                     │
│ Features:    │                         │                     │
│ ☑ Auth       │                         │                     │
│ ☑ Sidebar    │                         │                     │
│ ☐ Auto-load  │                         │                     │
│              │                         │                     │
│ [Create]     │                         │                     │
│ [Validate]   │                         │                     │
│              │                         │                     │
└──────────────┴─────────────────────────┴─────────────────────┘
```

---

## 📋 Left Panel: Configuration

### What You'll Enter

**Module Type:**
```
● New Module    ○ Existing Module
```

**Basic Info:**
```
Module ID:    my_dashboard
Name:         Analytics Dashboard
Version:      1.0.0
Description:  Real-time analytics and reporting
Icon:         fas fa-chart-line
```

**File Structure:**
```
☑ HTML Template          (my_dashboard.html)
☑ JavaScript Controller  (my_dashboard.js)
☑ CSS Stylesheet        (my_dashboard.css)
☐ Flask Routes          (routes/my_dashboard_routes.py)
```

**Features:**
```
☑ Requires Authentication  (User must be logged in)
☑ Show in Sidebar         (Display in navigation)
☐ Auto-load on Startup    (Load automatically)
☐ Main Tab Integration    (Tabbed interface)
```

**Platforms:**
```
☐ Xero
☐ Shopify
☐ Google Workspace
☐ Microsoft 365
```

**Actions:**
```
[Create Module]  [Validate Manifest]  [Generate Manifest]
```

---

## 🎬 Center Panel: Preview & Testing

### Tab 1: Live Preview

```
┌─────────────────────────────────────────────────────┐
│ 🔄 Refresh                                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│          [Your Module Preview Here]                 │
│                                                     │
│     Sandboxed iframe shows module UI                │
│     Safe testing environment                        │
│     No impact on production                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### Tab 2: API Tester

```
┌─────────────────────────────────────────────────────┐
│ API Request Builder                                 │
├─────────────────────────────────────────────────────┤
│ Method:   [GET ▼]                                   │
│ Endpoint: [/api/modules_________________________]   │
│                                                     │
│ Request Body:                                       │
│ ┌───────────────────────────────────────────────┐   │
│ │ {                                             │   │
│ │   "id": "test_module",                        │   │
│ │   "name": "Test"                              │   │
│ │ }                                             │   │
│ └───────────────────────────────────────────────┘   │
│                                                     │
│ [Send Request]                                      │
│                                                     │
│ Response:                                           │
│ ┌───────────────────────────────────────────────┐   │
│ │ Status: 200 OK                   Time: 45ms   │   │
│ │ {                                             │   │
│ │   "success": true,                            │   │
│ │   "modules": [...]                            │   │
│ │ }                                             │   │
│ └───────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

### Tab 3: Manifest Editor

```
┌─────────────────────────────────────────────────────┐
│ [Copy] [Download] [Save to Module]                 │
├─────────────────────────────────────────────────────┤
│ {                                                   │
│   "id": "my_dashboard",                             │
│   "name": "Analytics Dashboard",                    │
│   "version": "1.0.0",                               │
│   "description": "Real-time analytics",             │
│   "icon": "fas fa-chart-line",                      │
│   "files": {                                        │
│     "html": true,                                   │
│     "js": true,                                     │
│     "css": true,                                    │
│     "routes": false                                 │
│   },                                                │
│   "features": {                                     │
│     "requires_auth": true,                          │
│     "show_in_sidebar": true,                        │
│     "auto_load": false,                             │
│     "main_tab": false                               │
│   },                                                │
│   "required_platforms": []                          │
│ }                                                   │
└─────────────────────────────────────────────────────┘
```

---

## 🔍 Right Panel: Console & Logs

### Console Output

```
┌─────────────────────────────────────────────────────┐
│ [LOG] [INFO] [WARN] [ERROR] [Clear] [☐ Auto-scroll]│
├─────────────────────────────────────────────────────┤
│ 21:05:31  LOG    Initializing Module Creator       │
│ 21:05:31  INFO   Backend status: Connected          │
│ 21:05:32  INFO   Loaded 12 platforms                │
│ 21:05:35  LOG    Form data updated                  │
│ 21:05:40  INFO   Manifest validated successfully    │
│ 21:05:42  WARN   No platforms selected              │
│ 21:05:50  ERROR  Failed to create module            │
└─────────────────────────────────────────────────────┘
```

**Color Coding:**
- `LOG` - Gray (general info)
- `INFO` - Blue (informational)
- `WARN` - Yellow (warnings)
- `ERROR` - Red (errors)

---

### Network Log

```
┌─────────────────────────────────────────────────────┐
│ 📡 Network Activity                                 │
├─────────────────────────────────────────────────────┤
│ GET    /api/pool/health           200 OK    12ms   │
│ GET    /api/modules/platforms     200 OK    34ms   │
│ GET    /api/modules               200 OK    56ms   │
│ POST   /api/dev-tools/validate    200 OK    23ms   │
│ POST   /api/dev-tools/create      201 OK    145ms  │
│ POST   /api/dev-tools/save        200 OK    67ms   │
└─────────────────────────────────────────────────────┘
```

**Status Colors:**
- `200-299` - Green (success)
- `400-499` - Yellow (client error)
- `500-599` - Red (server error)

---

## 📊 Footer: Statistics

```
┌────────────────────────────────────────────────────────────────┐
│ Console Messages: 12  |  API Calls: 5  |  Errors: 0            │
└────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Color Palette

### Dark Theme
```
Background:  #1e1e1e  ████  Primary
             #252526  ████  Secondary
             #2d2d30  ████  Tertiary

Text:        #cccccc  ████  Primary
             #969696  ████  Secondary
             #6a6a6a  ████  Muted

Accents:     #0e639c  ████  Blue
             #16825d  ████  Green
             #f14c4c  ████  Red
             #cca700  ████  Yellow

Status:      #4ec9b0  ████  Success
             #f48771  ████  Error
             #dcdcaa  ████  Warning
             #569cd6  ████  Info
```

---

## 📝 Typical Workflow

### Step 1: Fill Out Form
```
1. Enter module details
2. Select file types (HTML/JS/CSS)
3. Choose features (auth, sidebar)
4. Click "Create Module"
```

### Step 2: See Console Output
```
21:05:50  LOG    Creating module: my_dashboard
21:05:50  INFO   Validating manifest...
21:05:51  INFO   Manifest is valid
21:05:51  LOG    Generating files...
21:05:51  INFO   Created manifest.json
21:05:51  INFO   Created my_dashboard.html
21:05:51  INFO   Created my_dashboard.js
21:05:51  INFO   Created my_dashboard.css
21:05:52  INFO   Module created successfully!
```

### Step 3: Check Network Log
```
POST /api/dev-tools/create-module  201 Created  156ms
```

### Step 4: Verify Files
```
✅ UI/modules_external/my_dashboard/
   ├── manifest.json
   ├── my_dashboard.html
   ├── my_dashboard.js
   └── my_dashboard.css
```

---

## 🚀 Success Messages

### Module Created
```
┌────────────────────────────────────────────────────┐
│ ✅ Success!                                        │
│                                                    │
│ Module "Analytics Dashboard" created successfully  │
│                                                    │
│ Files created:                                     │
│ • manifest.json                                    │
│ • my_dashboard.html                                │
│ • my_dashboard.js                                  │
│ • my_dashboard.css                                 │
│                                                    │
│ Path: C:/Users/.../UI/modules_external/my_dash... │
└────────────────────────────────────────────────────┘
```

### Manifest Validated
```
┌────────────────────────────────────────────────────┐
│ ✅ Manifest is valid                               │
│                                                    │
│ No errors found                                    │
│ Ready to create module                             │
└────────────────────────────────────────────────────┘
```

### Manifest Saved
```
┌────────────────────────────────────────────────────┐
│ ✅ Manifest saved successfully                     │
│                                                    │
│ Backup created: manifest.json.backup.20231206...  │
│ Updated: manifest.json                             │
└────────────────────────────────────────────────────┘
```

---

## ❌ Error Messages

### Validation Errors
```
┌────────────────────────────────────────────────────┐
│ ❌ Manifest validation failed                      │
│                                                    │
│ Errors found:                                      │
│ • Missing required field: id                       │
│ • Invalid version format: 1.0                      │
│ • Invalid file type: python                        │
└────────────────────────────────────────────────────┘
```

### Module Already Exists
```
┌────────────────────────────────────────────────────┐
│ ❌ Error: Module already exists                    │
│                                                    │
│ Module ID "my_dashboard" is already in use         │
│                                                    │
│ Solutions:                                         │
│ • Use a different module ID                        │
│ • Load existing module to edit                     │
│ • Delete existing module folder                    │
└────────────────────────────────────────────────────┘
```

### Backend Disconnected
```
┌────────────────────────────────────────────────────┐
│ ❌ Error: Backend not connected                    │
│                                                    │
│ Cannot reach Flask server at localhost:5001        │
│                                                    │
│ Please start the Flask server:                     │
│ python AI_infrastructure/flask_app.py              │
└────────────────────────────────────────────────────┘
```

---

## 🎯 Quick Reference

### Keyboard Shortcuts
- `Ctrl+Enter` - Send API request
- `Ctrl+S` - Save manifest (in manifest editor)
- `Esc` - Clear console
- `F5` - Refresh preview

### Button Colors
- **Blue** - Primary action (Create, Send)
- **Gray** - Secondary action (Validate, Clear)
- **Green** - Success action (Save)
- **Red** - Destructive action (Delete, Clear)

### Status Indicators
- **● Green** - Connected/Success
- **● Red** - Disconnected/Error
- **● Yellow** - Warning/Pending
- **● Gray** - Unknown/Neutral

---

## 📚 Tips & Tricks

1. **Always validate before creating** - Click "Validate Manifest" to catch errors early
2. **Use templates** - Start with Basic/Full/API template for faster setup
3. **Monitor console** - Watch for errors during module creation
4. **Test APIs first** - Use API tester to verify endpoints before building UI
5. **Backup manifests** - Automatic backups created when saving (timestamped)

---

**Ready to start building modules! 🚀**

Open: `c:\Users\gpoli\GIT\AI_agents\dev-tools\module-creator.html`
