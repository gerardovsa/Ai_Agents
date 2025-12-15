# Module Creator & Verifier - Developer Tool

**A standalone development UI for rapidly prototyping, testing, and deploying modules without impacting production code.**

---

## 🎯 Purpose

The Module Creator & Verifier is a **development-only tool** that enables you to:

- ✅ Create new modules with auto-generated file structures
- ✅ Edit and validate module manifests in real-time
- ✅ Test API endpoints without touching production
- ✅ Preview module UI in sandboxed iframe
- ✅ Monitor console logs and network requests
- ✅ Connect to live backend for testing (read-only)
- ✅ Iterate quickly without restarting servers

This tool **lives outside the main UI** and is designed exclusively for rapid iteration during module development.

---

## 📁 File Structure

```
dev-tools/
├── module-creator.html        # Main UI (270 lines)
├── module-creator.js          # JavaScript controller (658 lines)
└── module-creator.css         # Dark theme styling

AI_infrastructure/routes/
└── dev_tools_routes.py        # Flask API endpoints (4 routes)
```

**Backend Integration:**
- Registered in `AI_infrastructure/flask_app.py` (line ~440)
- Blueprint: `dev_tools_bp` → `/api/dev-tools/*`

---

## 🚀 Getting Started

### 1. Start Flask Backend

Ensure your Flask server is running on port 5001:

```bash
python AI_infrastructure/flask_app.py
```

Backend status will show as **Connected** (green indicator) in the UI header.

### 2. Open Module Creator

Open `dev-tools/module-creator.html` in your browser:

```bash
# PowerShell
Start-Process "c:\Users\gpoli\GIT\AI_agents\dev-tools\module-creator.html"

# Or drag-and-drop into browser
```

### 3. Verify Connection

Check the header for status indicators:
- ✅ **Backend Connected** (green) - Flask API reachable
- ✅ **Database Connected** (green) - Database pool healthy

---

## 🛠️ Features

### Left Panel: Module Configuration

**Module Type:**
- **New Module** - Create from scratch
- **Existing Module** - Load and edit existing module

**Basic Information:**
- Module ID (e.g., `my_module`, `xero_integration`)
- Module Name (display name in UI)
- Description (what the module does)
- Version (semantic versioning: `1.0.0`)
- Icon (Font Awesome class: `fas fa-cube`)

**File Structure:**
- ☑️ HTML Template - Generate `{module_id}.html`
- ☑️ JavaScript Controller - Generate `{module_id}.js`
- ☑️ CSS Stylesheet - Generate `{module_id}.css`
- ☑️ Flask Routes - Generate `routes/{module_id}_routes.py`

**Features:**
- ☑️ Requires Authentication - User must be logged in
- ☑️ Show in Sidebar - Display in main navigation
- ☑️ Auto-load on Startup - Load automatically when app starts
- ☑️ Main Tab Integration - Display in main tabbed interface

**Required Platforms:**
- Select platforms (Xero, Shopify, etc.) that this module depends on
- Multi-select checkboxes for credential requirements

---

### Center Panel: Preview & Testing

**Tab 1: Live Preview**
- Sandboxed `<iframe>` for testing module UI
- Isolated environment (no impact on main app)
- Refresh to reload module

**Tab 2: API Tester**
- Send HTTP requests to backend
- Methods: GET, POST, PUT, DELETE
- Custom endpoint input
- JSON request body editor
- Response display (status code, body, time)
- Network logging (all requests tracked)

**Tab 3: Manifest Editor**
- Real-time JSON preview of manifest
- Editable code block (click to edit)
- Actions:
  - **Copy to Clipboard** - Copy manifest JSON
  - **Download JSON** - Save as `manifest.json`
  - **Save to Module** - Write to module folder (requires module ID)

---

### Right Panel: Developer Console

**Console Output:**
- Timestamped log entries
- Log levels: `LOG`, `INFO`, `WARN`, `ERROR`
- Color-coded by severity
- Filter by level (click buttons to toggle)
- Auto-scroll toggle
- Clear console button

**Network Log:**
- All API requests (method, endpoint, status, time)
- Success/error indicators
- Response time tracking
- Filterable by status code

---

## 📝 Workflow Examples

### Example 1: Create New Module

1. **Enter Module Details:**
   ```
   Module ID: my_dashboard
   Name: Analytics Dashboard
   Version: 1.0.0
   Description: Real-time analytics and reporting
   Icon: fas fa-chart-line
   ```

2. **Select Files:**
   - ✅ HTML Template
   - ✅ JavaScript Controller
   - ✅ CSS Stylesheet
   - ❌ Flask Routes (not needed for frontend-only module)

3. **Configure Features:**
   - ✅ Requires Authentication
   - ✅ Show in Sidebar
   - ❌ Auto-load on Startup
   - ✅ Main Tab Integration

4. **Click "Create Module"**
   - Backend creates folder: `UI/modules_external/my_dashboard/`
   - Generates 3 files: `my_dashboard.html`, `my_dashboard.js`, `my_dashboard.css`
   - Creates `manifest.json` with configuration

5. **Result:**
   ```
   ✅ Module "Analytics Dashboard" created successfully
   📁 Path: C:/Users/gpoli/GIT/AI_agents/UI/modules_external/my_dashboard
   📄 Files: manifest.json, my_dashboard.html, my_dashboard.js, my_dashboard.css
   ```

---

### Example 2: Load & Edit Existing Module

1. **Select Module Type:** "Existing Module"
2. **Choose from Dropdown:** "Xero Integration"
3. **Module loads:**
   - All fields populate with existing data
   - Manifest JSON displays in editor
   - Console logs module details

4. **Edit Configuration:**
   - Change version: `1.0.0` → `1.1.0`
   - Add new platform: "Shopify"
   - Enable auto-load feature

5. **Click "Validate Manifest"**
   - Backend checks manifest structure
   - Displays validation errors (if any)
   - Console shows validation results

6. **Click "Save to Module"**
   - Backs up existing manifest (timestamped)
   - Writes updated manifest
   - Console confirms save

---

### Example 3: Test API Endpoints

1. **Navigate to "API Tester" tab**

2. **Test Module List Endpoint:**
   ```
   Method: GET
   Endpoint: /api/modules
   Body: (empty)
   ```
   Click "Send Request" → Response shows all modules

3. **Test Create Module:**
   ```
   Method: POST
   Endpoint: /api/dev-tools/create-module
   Body: {
     "id": "test_module",
     "name": "Test Module",
     "version": "1.0.0",
     "description": "Test description",
     "files": { "html": true, "js": true, "css": false, "routes": false },
     "features": { "requires_auth": true }
   }
   ```
   Click "Send Request" → Module created, files generated

4. **Network Log Shows:**
   ```
   POST /api/dev-tools/create-module - 200 OK - 245ms
   ```

---

## 🔌 API Endpoints

### Backend Endpoints (`/api/dev-tools/*`)

**1. Validate Manifest**
```http
POST /api/dev-tools/validate-manifest
Content-Type: application/json

{
  "id": "my_module",
  "name": "My Module",
  "version": "1.0.0",
  "description": "Module description",
  "files": { "html": true, "js": true, "css": true, "routes": false },
  "features": { "requires_auth": true },
  "required_platforms": ["xero"]
}
```

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "message": "Manifest is valid"
}
```

---

**2. Create Module**
```http
POST /api/dev-tools/create-module
Content-Type: application/json

{
  "id": "my_module",
  "name": "My Module",
  "version": "1.0.0",
  "description": "Module description",
  "files": { "html": true, "js": true, "css": true, "routes": true },
  "features": { "requires_auth": true, "show_in_sidebar": true },
  "required_platforms": []
}
```

**Response:**
```json
{
  "success": true,
  "module_id": "my_module",
  "path": "C:/Users/gpoli/GIT/AI_agents/UI/modules_external/my_module",
  "files_created": [
    "manifest.json",
    "my_module.html",
    "my_module.js",
    "my_module.css",
    "routes/my_module_routes.py"
  ],
  "message": "Module \"My Module\" created successfully"
}
```

---

**3. Save Manifest**
```http
POST /api/dev-tools/save-manifest
Content-Type: application/json

{
  "module_id": "my_module",
  "manifest": {
    "id": "my_module",
    "name": "My Module Updated",
    "version": "1.1.0",
    ...
  }
}
```

**Response:**
```json
{
  "success": true,
  "module_id": "my_module",
  "backup_path": "C:/Users/.../my_module/manifest.json.backup.20231206_143022",
  "message": "Manifest saved successfully"
}
```

---

**4. Get Templates**
```http
GET /api/dev-tools/templates
```

**Response:**
```json
{
  "templates": [
    {
      "id": "basic",
      "name": "Basic Module",
      "description": "Minimal module with HTML and JavaScript",
      "manifest": { ... }
    },
    {
      "id": "full",
      "name": "Full Module",
      "description": "Complete module with all file types",
      "manifest": { ... }
    },
    {
      "id": "api",
      "name": "API Module",
      "description": "Backend-focused module with Flask routes",
      "manifest": { ... }
    }
  ]
}
```

---

## 📋 Manifest Structure

```json
{
  "id": "module_id",
  "name": "Display Name",
  "version": "1.0.0",
  "description": "What this module does",
  "icon": "fas fa-cube",
  "files": {
    "html": true,
    "js": true,
    "css": true,
    "routes": false
  },
  "features": {
    "requires_auth": true,
    "show_in_sidebar": true,
    "auto_load": false,
    "main_tab": false
  },
  "required_platforms": ["xero", "shopify"]
}
```

**Required Fields:**
- `id` - Unique identifier (alphanumeric, underscores, hyphens)
- `name` - Display name
- `version` - Semantic versioning (`major.minor.patch`)
- `description` - Brief description

**Validation Rules:**
- ID must be alphanumeric + underscores/hyphens
- ID cannot start with underscore or hyphen
- Version must be `X.Y.Z` format (numbers only)
- Files must be: `html`, `js`, `css`, `routes`
- Features must be: `requires_auth`, `show_in_sidebar`, `auto_load`, `main_tab`
- Platforms must exist in `/api/modules/platforms`

---

## 🎨 UI Architecture

### Three-Panel Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Header: Backend Status | Database Status                    │
├─────────────┬────────────────────────┬──────────────────────┤
│             │                        │                      │
│  CONFIG     │   PREVIEW / API TEST   │   CONSOLE / NETWORK  │
│  PANEL      │   MANIFEST EDITOR      │   LOGS               │
│             │                        │                      │
│  - Module   │  [Live Preview]        │  [Console Output]    │
│    Info     │  [API Tester]          │  [Network Log]       │
│  - Files    │  [Manifest JSON]       │                      │
│  - Features │                        │                      │
│  - Actions  │                        │                      │
│             │                        │                      │
├─────────────┴────────────────────────┴──────────────────────┤
│ Footer: Console Messages: 12 | API Calls: 5 | Errors: 0     │
└─────────────────────────────────────────────────────────────┘
```

### Color-Coded Console

- **LOG** - Gray (general information)
- **INFO** - Blue (informational messages)
- **WARN** - Yellow (warnings)
- **ERROR** - Red (errors)

---

## ⚠️ Important Notes

### Development-Only Tool

- **DO NOT** expose this tool in production
- **DO NOT** include in production builds
- **DO NOT** link from main UI navigation

This tool is for **local development only** and should remain in the `dev-tools/` directory.

### Backend Connection

- Tool requires Flask server running on `localhost:5001`
- Backend status indicator shows connection health
- All API calls go through Flask (no direct database access)

### Module Creation

- Modules are created in `UI/modules_external/{module_id}/`
- Existing modules will **not** be overwritten (409 Conflict error)
- Backups are created when saving manifests (timestamped)

### File Generation

Generated files include:
- **HTML** - Basic module layout with header/content
- **JavaScript** - Class-based controller with API integration
- **CSS** - Module-specific styles
- **Routes** - Flask blueprint with GET/POST endpoints

All templates use **best practices**:
- ES6 class syntax
- `async/await` for API calls
- Error handling
- Console logging
- Comments and documentation

---

## 🐛 Troubleshooting

### Backend Status: Disconnected

**Cause:** Flask server not running
**Solution:**
```bash
python AI_infrastructure/flask_app.py
```

### Database Status: Unknown

**Cause:** Connection pool not initialized
**Solution:** Restart Flask server, check database credentials

### Manifest Validation Errors

**Common Errors:**
- `Invalid module ID` → Use only alphanumeric, underscores, hyphens
- `Invalid version format` → Use `X.Y.Z` format (e.g., `1.0.0`)
- `Missing required field` → Ensure `id`, `name`, `version`, `description` are filled

### Module Already Exists (409 Error)

**Cause:** Module folder already exists
**Solution:** 
- Delete existing module folder
- Choose "Existing Module" instead and load it
- Use different module ID

### API Tester Not Working

**Cause:** CORS or network error
**Solution:**
- Check Flask server logs
- Verify endpoint exists
- Check request body JSON syntax

---

## 📚 Additional Resources

### Related Files

- **Module Registry:** `AI_infrastructure/core/module_registry.py` (556 lines)
- **Module Loader:** `AI_infrastructure/core/module_blueprint_loader.py`
- **Flask App:** `AI_infrastructure/flask_app.py` (line 347-365 for module system)
- **Example Modules:** `UI/modules_external/` (Xero, Shopify, Quote Calculator, etc.)

### Module System Documentation

- Modules are **self-registering** (auto-discovered on startup)
- Manifest-driven architecture (all config in `manifest.json`)
- Hot-reload support (Flask development mode)
- API endpoints: `/api/modules/*` (8 routes)

---

## 🎯 Next Steps

After creating a module with this tool:

1. **Test Module Files:** Open generated HTML/JS/CSS in browser
2. **Register Module:** Restart Flask to auto-discover new module
3. **Add Routes:** Implement Flask endpoints in `routes/{module_id}_routes.py`
4. **Integrate UI:** Link module from main navigation (if `show_in_sidebar: true`)
5. **Deploy:** Copy module to production after testing

---

## 📝 Summary

The Module Creator & Verifier is a **powerful development tool** that accelerates module creation by:

- ✅ Generating boilerplate code automatically
- ✅ Validating manifests before deployment
- ✅ Testing APIs without touching production
- ✅ Providing real-time feedback via console

Use this tool to **rapidly prototype and iterate** on new modules, then deploy them to the main application when ready.

**Happy Module Building! 🚀**
