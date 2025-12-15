# Module Creator Enhanced - Quick Start Guide

**Version:** 2.0.0 - Live Code Editor with Monaco, WebSocket, Real CSS  
**Date:** December 15, 2025

---

## 🚀 What's New in Enhanced Version

### Major Upgrades from v1:
- ✅ **Monaco Editor** - VS Code's editor in your browser
  - Syntax highlighting for HTML/JavaScript/CSS/Python/JSON
  - IntelliSense autocomplete
  - Code formatting (Alt+Shift+F)
  - Error detection
  - Minimap navigation
  
- ✅ **Real-Time WebSocket Sync**
  - Changes sync instantly across browser tabs
  - Collaborate on module development
  - Keep-alive ping/pong (30s interval)
  
- ✅ **Real UI CSS Injection**
  - Preview uses actual global CSS from production
  - See exactly how module will look in live UI
  - No more styling surprises
  
- ✅ **Multi-File Tab Editor**
  - Edit HTML, JS, CSS, Routes, Manifest in one view
  - Switch between files without closing editor
  - Auto-save all files (Ctrl+S)
  
- ✅ **Enhanced Live Preview**
  - Auto-refresh toggle
  - Sandboxed iframe for safety
  - Real CSS loaded from `UI/modules_internal/agents/agent-ui.css`

---

## 📋 Prerequisites

1. **Flask Backend Running:**
   ```powershell
   cd c:\Users\gpoli\GIT\AI_agents
   python AI_infrastructure\flask_app.py
   ```
   - Server runs on `http://localhost:5001`
   - WebSocket endpoint: `ws://localhost:5001/ws/dev-tools`

2. **Modern Browser:**
   - Chrome/Edge (recommended)
   - Firefox (supported)
   - Safari (supported)

3. **Internet Connection:**
   - Monaco Editor CDN: `monaco-editor@0.45.0`
   - Socket.IO CDN: `socket.io/4.5.4`

---

## 🎯 Getting Started (5 Minutes)

### Step 1: Start Flask
```powershell
cd c:\Users\gpoli\GIT\AI_agents
python AI_infrastructure\flask_app.py
```

Wait for:
```
[MODULE REGISTRY] Scanning UI/modules_external/
[MODULE REGISTRY] Registered 10 modules
 * Running on http://localhost:5001
```

### Step 2: Open Enhanced Editor
```powershell
Start-Process "dev-tools\module-creator-enhanced.html"
```

Or double-click: `dev-tools/module-creator-enhanced.html`

### Step 3: Verify WebSocket Connection
Look for in browser console (F12):
```
[Module Creator Enhanced] WebSocket connected
[Module Creator Enhanced] Connected to dev tools server: <client_id>
```

Sync indicator (top-right) should show: **🟢 Ready**

---

## 🎨 User Interface Layout

```
┌────────────────────────────────────────────────────────────────────────┐
│  Module Creator Enhanced         [Auto-refresh ☑]  🟢 Ready   Ctrl+S  │
├──────────────┬─────────────────────────────────────┬──────────────────┤
│              │  [HTML] [JS] [CSS] [Routes] [JSON] │                  │
│  Config      │  ┌──────────────────────────────┐  │  Live Preview    │
│  Panel       │  │                              │  │  ┌──────────────┐│
│  ┌────────┐  │  │   Monaco Editor             │  │  │              ││
│  │Module  │  │  │   (Code editing area)       │  │  │   Module     ││
│  │Settings│  │  │                              │  │  │   Renders    ││
│  │        │  │  │   Line numbers, minimap,    │  │  │   Here       ││
│  │  [▼]   │  │  │   syntax highlighting       │  │  │              ││
│  └────────┘  │  └──────────────────────────────┘  │  └──────────────┘│
│              │                                     │                  │
│ [Create]     │  Last Saved: 2025-12-15 10:30 AM   │  [Refresh]      │
│ [Save All]   │  Sync Status: ✅ Synced            │                  │
└──────────────┴─────────────────────────────────────┴──────────────────┘
│  Console Output (Logs, Errors, Warnings)                              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl+S** | Save all files (HTML, JS, CSS, Routes, Manifest) |
| **Alt+Shift+F** | Format code in active editor |
| **Ctrl+Space** | Trigger IntelliSense suggestions |
| **F12** | Go to definition |
| **Alt+Click** | Multi-cursor editing |
| **Ctrl+/** | Toggle line comment |
| **Ctrl+F** | Find in current file |
| **Ctrl+H** | Find and replace |

---

## 📝 Creating Your First Module

### 1. Configure Module (Left Panel)

**Basic Settings:**
- **Module Type:** New Module
- **Module ID:** `sales_dashboard` (snake_case)
- **Module Name:** Sales Dashboard
- **Version:** 1.0.0
- **Description:** Sales metrics and analytics

**Features:**
- ☑ Show in Sidebar
- ☑ Requires Authentication
- ☐ Auto-load on Startup
- ☑ Main Tab Display

**Files:**
- ☑ HTML (UI template)
- ☑ JavaScript (controller)
- ☑ CSS (styles)
- ☑ Routes (Flask API)

### 2. Edit HTML Tab

Switch to **HTML** tab, paste:
```html
<div class="module-container sales-dashboard">
    <div class="module-header">
        <h2><i class="fas fa-chart-line"></i> Sales Dashboard</h2>
        <p>Real-time sales metrics</p>
    </div>
    
    <div class="metrics-grid" id="metrics-grid">
        <!-- Metrics will be inserted by JavaScript -->
    </div>
</div>
```

### 3. Edit JS Tab

Switch to **JS** tab, paste:
```javascript
class SalesDashboard {
    constructor() {
        this.API_BASE = 'http://localhost:5001';
        this.init();
    }
    
    async init() {
        console.log('[Sales Dashboard] Initializing...');
        await this.loadMetrics();
    }
    
    async loadMetrics() {
        try {
            const response = await fetch(`${this.API_BASE}/api/sales-dashboard/metrics`);
            const data = await response.json();
            this.renderMetrics(data.metrics);
        } catch (error) {
            console.error('[Sales Dashboard] Error:', error);
        }
    }
    
    renderMetrics(metrics) {
        const grid = document.getElementById('metrics-grid');
        grid.innerHTML = metrics.map(m => `
            <div class="metric-card">
                <h3>${m.label}</h3>
                <div class="value">${m.value}</div>
            </div>
        `).join('');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.salesDashboard = new SalesDashboard();
});
```

### 4. Edit CSS Tab

Switch to **CSS** tab, paste:
```css
.sales-dashboard .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    padding: 20px;
}

.sales-dashboard .metric-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.sales-dashboard .metric-card h3 {
    font-size: 14px;
    color: #666;
    margin-bottom: 8px;
}

.sales-dashboard .metric-card .value {
    font-size: 32px;
    font-weight: bold;
    color: #333;
}
```

### 5. Edit Routes Tab

Switch to **Routes** tab, paste:
```python
from flask import Blueprint, jsonify

sales_dashboard_bp = Blueprint('sales_dashboard', __name__, url_prefix='/api/sales-dashboard')

@sales_dashboard_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get sales metrics"""
    metrics = [
        {'label': 'Revenue', 'value': '$125,430'},
        {'label': 'Orders', 'value': '1,234'},
        {'label': 'Customers', 'value': '567'},
        {'label': 'Growth', 'value': '+23%'}
    ]
    return jsonify({'metrics': metrics})
```

### 6. Review Live Preview

Check the **Live Preview** panel (right side):
- Module should render with global CSS
- Metric cards should have proper styling
- Layout should match production UI

### 7. Save and Create

Press **Ctrl+S** or click **Save All Files**

Watch console output:
```
[Module Creator Enhanced] Saving all files...
[Module Creator Enhanced] Files saved successfully (5 files)
[Module Creator Enhanced] Sync status: Synced
```

Then click **Create Module**:
```
[Module Creator Enhanced] Module created successfully!
[Module Creator Enhanced] Path: UI/modules_external/sales_dashboard
```

---

## 🔄 Real-Time Sync Demo

### Test WebSocket Sync (2 Browser Tabs)

1. **Open tab 1:**
   ```powershell
   Start-Process "dev-tools\module-creator-enhanced.html"
   ```

2. **Open tab 2:**
   ```powershell
   Start-Process "dev-tools\module-creator-enhanced.html"
   ```

3. **In tab 1:**
   - Select existing module: `sales_dashboard`
   - Edit HTML: Change `<h2>` text to "Sales Dashboard v2"
   - Press **Ctrl+S**

4. **In tab 2:**
   - Should automatically update to show "Sales Dashboard v2"
   - Console shows: `[Module Creator Enhanced] File updated: html`

**How it works:**
- Tab 1 saves → POST `/api/dev-tools/save-files`
- Server emits `file_updated` event via WebSocket
- Tab 2 receives event → Updates Monaco Editor model

---

## 🎨 Real CSS Injection

### How Preview Matches Production

**CSS files loaded in preview:**
```javascript
this.uiCssFiles = [
    '../UI/modules_internal/agents/agent-ui.css',
    // Add more global CSS files
];
```

**Preview HTML structure:**
```html
<!DOCTYPE html>
<html>
<head>
    <!-- Real UI CSS -->
    <link rel="stylesheet" href="../UI/modules_internal/agents/agent-ui.css">
    
    <!-- Module CSS -->
    <style>{{ module CSS from CSS tab }}</style>
</head>
<body>
    {{ module HTML from HTML tab }}
    <script>{{ module JS from JS tab }}</script>
</body>
</html>
```

**Result:**
- Module inherits global typography (fonts, sizes)
- Global color scheme applied
- CSS variables from UI (`--primary-color`, etc.)
- Consistent spacing and layout

---

## 🐛 Troubleshooting

### Issue: "WebSocket disconnected"

**Symptoms:**
- Sync indicator shows 🔴 Offline
- Console: `[Module Creator Enhanced] WebSocket disconnected`

**Fix:**
1. Check Flask is running:
   ```powershell
   Get-NetTCPConnection -LocalPort 5001
   ```
2. Restart Flask:
   ```powershell
   python AI_infrastructure\flask_app.py
   ```
3. Refresh browser (Ctrl+R)

---

### Issue: "Monaco Editor not loading"

**Symptoms:**
- Blank editor area
- Console error: `Failed to load monaco-editor`

**Fix:**
1. Check internet connection (CDN required)
2. Clear browser cache (Ctrl+Shift+Delete)
3. Try different browser (Chrome recommended)
4. Check console for specific errors

---

### Issue: "Preview shows broken styling"

**Symptoms:**
- Preview looks different from production
- Missing fonts/colors

**Fix:**
1. Verify CSS path in `updateLivePreview()`:
   ```javascript
   this.uiCssFiles = [
       '../UI/modules_internal/agents/agent-ui.css'
   ];
   ```
2. Check CSS file exists:
   ```powershell
   Test-Path "UI\modules_internal\agents\agent-ui.css"
   ```
3. Inspect iframe (right-click preview → Inspect)
4. Look for 404 errors in Network tab

---

### Issue: "Ctrl+S not saving"

**Symptoms:**
- Keyboard shortcut doesn't work
- No console output

**Fix:**
1. Check Monaco Editor initialized:
   ```javascript
   console.log(this.mainEditor); // Should not be null
   ```
2. Verify event listener registered:
   ```javascript
   this.mainEditor.addCommand(
       monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_S,
       () => this.saveAllFiles()
   );
   ```
3. Try clicking **Save All Files** button instead

---

## 📚 Advanced Features

### Custom Templates

Create reusable module templates:

1. Edit `getDefaultContent()` in `module-creator-enhanced.js`:
```javascript
getDefaultContent(fileType) {
    if (fileType === 'html') {
        return `
<!-- Dashboard Template -->
<div class="module-container">
    <div class="dashboard-grid">
        <!-- Your dashboard layout -->
    </div>
</div>
        `;
    }
}
```

2. Add template selector in UI (left panel)

---

### API-Only Modules

Create backend-only modules (no UI):

1. **Manifest settings:**
   - Uncheck "HTML"
   - Uncheck "JavaScript"
   - Uncheck "CSS"
   - Check "Routes"

2. **Routes tab:**
```python
from flask import Blueprint, jsonify

api_only_bp = Blueprint('api_only', __name__, url_prefix='/api/my-service')

@api_only_bp.route('/data', methods=['GET'])
def get_data():
    return jsonify({'data': [1, 2, 3]})
```

3. **Manifest JSON:**
```json
{
  "features": {
    "show_in_sidebar": false,
    "auto_load": true
  }
}
```

---

### Multi-User Collaboration

**Scenario:** Team members working on same module

**Setup:**
1. All users open `module-creator-enhanced.html`
2. Load same module (e.g., `customer_portal`)
3. Edit different files (Alice: HTML, Bob: JS)

**What happens:**
- Alice edits HTML → Bob's HTML tab updates instantly
- Bob edits JS → Alice's JS tab updates instantly
- Both see changes in live preview
- Conflicts resolved by "last save wins"

**Best practices:**
- Communicate in chat before editing
- Assign files to specific team members
- Use version control (Git) for final code

---

## 🚀 Next Steps

1. **Create 5+ modules** to get comfortable with workflow
2. **Experiment with Monaco shortcuts** (Ctrl+Space, F12, Alt+Click)
3. **Test WebSocket sync** with multiple browser tabs
4. **Customize CSS injection** for your specific UI framework
5. **Add custom templates** for common module patterns

---

## 📖 Related Documentation

- **AI_PROMPT.md** - Comprehensive AI agent instructions
- **IMPLEMENTATION_SUMMARY.md** - Technical architecture details
- **VISUAL_GUIDE.md** - Screenshots and UI walkthrough
- **MODULE_CREATOR_API.md** - API endpoint reference

---

## ✅ Success Checklist

- [ ] Flask backend running on port 5001
- [ ] WebSocket connected (🟢 Ready indicator)
- [ ] Monaco Editor loads (syntax highlighting visible)
- [ ] Can switch between file tabs (HTML/JS/CSS/Routes/Manifest)
- [ ] Live preview updates when editing HTML
- [ ] Real UI CSS loaded in preview
- [ ] Ctrl+S saves all files
- [ ] WebSocket sync works across tabs
- [ ] Created at least one test module
- [ ] Module appears in Flask module registry

---

**Need help?** Check the console output (F12) for detailed error messages.

**Last Updated:** December 15, 2025  
**Version:** 2.0.0  
**Maintainer:** Valor AI Development Team
