# Module Development - Best Practices

**Version:** 2.0.0  
**Last Updated:** November 3, 2025  
**Reference Implementation:** `stock-management` module

---

## Overview

This guide provides best practices for developing modules in the AI Agents Platform, based on production-tested patterns from the `stock-management` module (our reference implementation).

---

## Table of Contents

1. [Golden Rules](#golden-rules)
2. [File Structure](#file-structure)
3. [Naming Conventions](#naming-conventions)
4. [manifest.json Structure](#manifestjson-structure)
5. [JavaScript Patterns](#javascript-patterns)
6. [CSS Standards](#css-standards)
7. [Backend Integration](#backend-integration)
8. [Documentation Requirements](#documentation-requirements)
9. [Testing Standards](#testing-standards)
10. [Validation Checklist](#validation-checklist)

---

## Golden Rules

### 🚨 **CRITICAL: The Four Commandments**

1. **Folder Name = Module ID**
   ```
   ✅ CORRECT:
   quote-calculator/
   └── manifest.json (id: "quote-calculator")
   
   ❌ WRONG:
   calculator-module/
   └── manifest.json (id: "quote-calculator")
   ```

2. **File Names Match Module ID**
   ```
   ✅ CORRECT:
   stock-management/
   ├── stock-management.js
   ├── stock-management.css
   └── manifest.json (id: "stock-management")
   
   ❌ WRONG:
   stock-management/
   ├── stockManagement.js
   ├── stock.css
   ```

3. **Class Name = PascalCase(Module ID) + "Module"**
   ```javascript
   ✅ CORRECT:
   // Module ID: stock-management
   class StockManagementModule extends BaseModule { }
   
   ❌ WRONG:
   class StockModule extends BaseModule { }
   class stockManagement extends BaseModule { }
   ```

4. **Extend BaseModule**
   ```javascript
   ✅ CORRECT:
   class MyModule extends BaseModule {
     constructor(moduleId) {
       super(moduleId);
     }
   }
   
   ❌ WRONG:
   class MyModule {  // Missing extends BaseModule
     constructor() {  // Missing moduleId parameter
     }
   }
   ```

---

## File Structure

### Minimal Module (Required Files)
```
my-module/
├── manifest.json          # REQUIRED - Module configuration
├── my-module.js           # REQUIRED - Module implementation
└── my-module.css          # OPTIONAL - Module styles
```

### Standard Module (Recommended)
```
my-module/
├── manifest.json          # Module config
├── my-module.js           # Main module code
├── my-module.css          # Module styles
└── README.md              # Documentation
```

### Advanced Module (Best Practice - Reference: stock-management)
```
stock-management/
├── manifest.json                          # Module config
├── stock-management.js                    # Main module (1,375 lines)
├── stock-management.css                   # Base styles
├── stock-management-enhanced.js           # Enhanced features
├── stock_routes.py                        # Backend Flask routes
├── database-config.json                   # Database configuration
├── TABLE_ENHANCEMENTS.js                  # Additional utilities
├── README.md                              # Main documentation
├── IMPLEMENTATION_COMPLETE.md             # Implementation guide
├── INTEGRATION_CHECKLIST.md               # Integration verification
├── INTEGRATION_FEATURES_SUMMARY.md        # Feature overview
├── INTEGRATION_GUIDE.md                   # Setup instructions
├── ENHANCEMENTS_COMPLETE.md               # Enhancement docs
├── README_TABLE_ENHANCEMENTS.md           # Table feature docs
├── TEST_ENHANCEMENTS.html                 # Test file
├── USAGE_EXAMPLE.html                     # Usage examples
├── VISUAL_DASHBOARD.html                  # Visual demo
└── __pycache__/                          # Python cache (normal)
```

**Key Takeaway:** The stock-management module shows how comprehensive documentation and testing files create a maintainable, professional module.

---

## Naming Conventions

### Module ID Format

**Rules:**
- lowercase letters only
- hyphens for word separation (no underscores, no spaces)
- descriptive and concise
- 2-4 words maximum

**Examples:**
```
✅ GOOD:
- salesforce
- stock-management
- quote-calculator
- database-visualizer
- asana-projects

❌ BAD:
- Salesforce               (uppercase)
- stock_management         (underscores)
- quote calculator         (spaces)
- calc                     (too vague)
- super-advanced-calculator-v2  (too long)
```

### File Naming Patterns

| File Type | Pattern | Example |
|-----------|---------|---------|
| Manifest | `manifest.json` | `manifest.json` |
| JavaScript | `{module-id}.js` | `stock-management.js` |
| CSS | `{module-id}.css` | `stock-management.css` |
| Python Routes | `{module_id}_routes.py` | `stock_routes.py` |
| Enhanced JS | `{module-id}-enhanced.js` | `stock-management-enhanced.js` |
| Utilities | `FEATURE_NAME.js` | `TABLE_ENHANCEMENTS.js` |

**Special Cases:**
- **Python files:** Use snake_case (Python convention): `stock_routes.py`
- **Documentation:** Use UPPERCASE.md for major docs: `IMPLEMENTATION_COMPLETE.md`
- **Theme-specific CSS:** Allowed if explicitly referenced in manifest.json: `database-visualizer-dark-tags.css`

---

## manifest.json Structure

### Minimal manifest.json
```json
{
  "id": "my-module",
  "name": "My Module",
  "version": "1.0.0",
  "description": "Brief description of what this module does",
  "icon": "fas fa-icon-name",
  "colors": {
    "primary": "#3498db",
    "secondary": "#5dade2",
    "hover": "#2980b9"
  }
}
```

### Complete manifest.json (Reference: stock-management)
```json
{
  "id": "stock-management",
  "name": "Stock Management",
  "version": "1.0.0",
  "description": "Complete stock inventory management, analytics, and AI-powered invoice processing",
  "icon": "fas fa-boxes",
  "author": "InHouse Print",
  
  "scriptPath": "external/modules/stock-management/stock-management.js",
  "stylePath": "external/modules/stock-management/stock-management.css",
  "enhancedScript": "external/modules/stock-management/stock-management-enhanced.js",
  
  "dependencies": [
    "https://cdn.plot.ly/plotly-2.27.0.min.js",
    "external/modules/stock-management/TABLE_ENHANCEMENTS.js"
  ],
  
  "colors": {
    "primary": "#0078d4",
    "secondary": "#00b294",
    "hover": "#006cbe"
  },
  
  "settings": {
    "api_endpoint": "/api/stock",
    "backend_url": "http://localhost:5001"
  },
  
  "tabs": [
    {
      "id": "invoice-processing",
      "name": "Invoice Processing",
      "icon": "fas fa-file-invoice",
      "description": "AI-powered invoice extraction and stock matching",
      "default": true
    },
    {
      "id": "usage-analytics",
      "name": "Usage Analytics",
      "icon": "fas fa-chart-line",
      "description": "Stock consumption trends and patterns"
    }
  ]
}
```

### manifest.json Best Practices

**Required Fields:**
- `id` - Matches folder name (critical!)
- `name` - Display name
- `version` - Semantic versioning (1.0.0)
- `icon` - FontAwesome icon class

**Recommended Fields:**
- `description` - Brief purpose statement
- `author` - Organization or developer name
- `colors` - Primary, secondary, hover colors
- `tabs` - Tab definitions with icons and descriptions

**Optional Fields:**
- `scriptPath` - Explicit script path (auto-detected if omitted)
- `stylePath` - Explicit CSS path (auto-detected if omitted)
- `html_file` - Separate HTML template file (see HTML Patterns section below)
- `dependencies` - External libraries or additional scripts
- `settings` - Module-specific configuration
- `enhancedScript` - Progressive enhancement version
- `has_database` - Boolean indicating database requirement

---

## HTML Patterns: Two Approaches

### 🎯 Critical Choice: HTML File vs. JavaScript-Generated UI

**Every module must choose ONE of these patterns:**

---

### Pattern 1: JavaScript-Generated UI (Recommended for Complex Modules)

**When to Use:**
- ✅ Dynamic, interactive UIs with frequent updates
- ✅ Complex state management requirements
- ✅ Modules with conditional rendering
- ✅ AI chat integration with live data updates
- ✅ Tabs with different content types

**Advantages:**
- Full programmatic control over UI
- Easy to update UI based on state changes
- No separate HTML file to maintain
- Better for data-driven interfaces
- Cleaner separation of concerns

**Example: Communication Hub Module**

```javascript
// communication-hub/manifest.json
{
  "id": "communication-hub",
  "name": "Communication Hub",
  "js_file": "communication-hub.js",
  "css_file": "communication-hub.css"
  // NOTE: NO html_file field - UI is created in JavaScript!
}
```

```javascript
// communication-hub/communication-hub.js
class CommunicationHubModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);
    }

    async initialize() {
        console.log('🔧 Initializing Communication Hub...');
        
        // Create UI programmatically
        await this.createModuleStructure();
        
        // Load data and render
        await this.loadEmails();
        this.renderEmailList();
        
        console.log('✅ Communication Hub ready');
    }

    async createModuleStructure() {
        // Get container (created by module loader)
        const container = document.getElementById(`tab-${this.manifest.main_tab_id || this.moduleId}`);
        
        if (!container) {
            console.error('Container not found!');
            return;
        }

        // Build UI with template literals
        container.innerHTML = `
            <div class="comm-hub-container">
                <!-- Header -->
                <div class="comm-hub-header">
                    <h2><i class="fas fa-inbox"></i> Unified Inbox</h2>
                    <div class="comm-hub-actions">
                        <button id="refresh-emails" class="btn-icon">
                            <i class="fas fa-sync"></i> Refresh
                        </button>
                        <button id="compose-email" class="btn-primary">
                            <i class="fas fa-pen"></i> Compose
                        </button>
                    </div>
                </div>

                <!-- Filter Bar -->
                <div class="comm-hub-filters">
                    <select id="account-filter">
                        <option value="all">All Accounts</option>
                        <option value="gmail">Gmail</option>
                        <option value="outlook">Outlook</option>
                    </select>
                    <input type="search" id="email-search" placeholder="Search emails...">
                </div>

                <!-- Email List -->
                <div id="email-list" class="comm-hub-email-list">
                    <!-- Emails will be rendered here dynamically -->
                </div>

                <!-- Email Detail Pane -->
                <div id="email-detail" class="comm-hub-detail">
                    <div class="empty-state">
                        <i class="fas fa-inbox"></i>
                        <p>Select an email to view</p>
                    </div>
                </div>
            </div>
        `;

        // Attach event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.getElementById('refresh-emails')?.addEventListener('click', () => {
            this.loadEmails();
        });

        document.getElementById('compose-email')?.addEventListener('click', () => {
            this.openComposeDialog();
        });

        document.getElementById('email-search')?.addEventListener('input', (e) => {
            this.filterEmails(e.target.value);
        });
    }

    async loadEmails() {
        try {
            const response = await fetch('/api/emails/list');
            this.emails = await response.json();
            this.renderEmailList();
        } catch (error) {
            console.error('Failed to load emails:', error);
        }
    }

    renderEmailList() {
        const listContainer = document.getElementById('email-list');
        
        listContainer.innerHTML = this.emails.map(email => `
            <div class="email-item" data-id="${email.id}">
                <div class="email-sender">${email.from}</div>
                <div class="email-subject">${email.subject}</div>
                <div class="email-preview">${email.preview}</div>
                <div class="email-time">${this.formatTime(email.timestamp)}</div>
            </div>
        `).join('');

        // Add click handlers to email items
        listContainer.querySelectorAll('.email-item').forEach(item => {
            item.addEventListener('click', () => {
                this.showEmailDetail(item.dataset.id);
            });
        });
    }
}

// Register module
window.ModuleRegistry['communication-hub'] = {
    init: () => new CommunicationHubModule('communication-hub')
};
```

**Key Points for JavaScript-Generated UI:**
1. **NO `html_file` in manifest** - Module loader will skip HTML loading
2. **Create UI in `initialize()` method** - Build DOM programmatically
3. **Use template literals** - Clean, readable HTML strings
4. **Attach event listeners after DOM creation** - In `setupEventListeners()`
5. **Store references to key elements** - For efficient updates

---

### Pattern 2: Separate HTML Template File (Recommended for Static Modules)

**When to Use:**
- ✅ Static or semi-static content layouts
- ✅ Simple modules with minimal interaction
- ✅ Designer-friendly templates (non-developers can edit)
- ✅ Modules with complex, nested HTML structures
- ✅ Legacy modules being migrated

**Advantages:**
- Clean separation of HTML structure from logic
- Easier for designers to modify layout
- Better for complex nested structures
- IDE syntax highlighting for HTML
- Can include inline styles/scripts if needed

**Example: InHouse Kanban Module**

```javascript
// inhouse-kanban/manifest.json
{
  "id": "inhouse-kanban",
  "name": "InHouse Kanban",
  "html_file": "inhouse-kanban-SIDEBAR.html",  // ← HTML file specified!
  "js_file": "inhouse-kanban.js",
  "css_file": "inhouse-kanban.css"
}
```

```html
<!-- inhouse-kanban/inhouse-kanban-SIDEBAR.html -->
<div class="kanban-sidebar-container">
    <!-- Sidebar Header -->
    <div class="kanban-sidebar-header">
        <h3>
            <i class="fas fa-briefcase"></i>
            Production Workflow
        </h3>
        <div class="kanban-header-actions">
            <button id="kanban-refresh" class="btn-icon" title="Refresh">
                <i class="fas fa-sync"></i>
            </button>
            <button id="kanban-settings" class="btn-icon" title="Settings">
                <i class="fas fa-cog"></i>
            </button>
        </div>
    </div>

    <!-- Filter Bar -->
    <div class="kanban-filters">
        <select id="kanban-stage-filter" class="filter-select">
            <option value="all">All Stages</option>
            <option value="new">New Orders</option>
            <option value="in-progress">In Progress</option>
            <option value="completed">Completed</option>
        </select>
        <input type="search" id="kanban-search" placeholder="Search jobs..." class="filter-search">
    </div>

    <!-- Kanban Board -->
    <div id="kanban-board" class="kanban-board">
        <!-- Columns will be rendered here by JavaScript -->
    </div>

    <!-- Footer Stats -->
    <div class="kanban-footer">
        <div class="stat">
            <span class="stat-label">Total Jobs:</span>
            <span id="total-jobs" class="stat-value">0</span>
        </div>
        <div class="stat">
            <span class="stat-label">In Progress:</span>
            <span id="in-progress-jobs" class="stat-value">0</span>
        </div>
    </div>
</div>
```

```javascript
// inhouse-kanban/inhouse-kanban.js
class InHouseKanbanModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);
    }

    async initialize() {
        console.log('🔧 Initializing InHouse Kanban...');
        
        // HTML is already loaded by module loader!
        // Just need to attach event listeners and load data
        
        this.setupEventListeners();
        await this.loadKanbanData();
        this.renderBoard();
        
        console.log('✅ InHouse Kanban ready');
    }

    setupEventListeners() {
        // Elements from HTML file are already in DOM
        document.getElementById('kanban-refresh')?.addEventListener('click', () => {
            this.loadKanbanData();
        });

        document.getElementById('kanban-search')?.addEventListener('input', (e) => {
            this.filterJobs(e.target.value);
        });

        document.getElementById('kanban-stage-filter')?.addEventListener('change', (e) => {
            this.filterByStage(e.target.value);
        });
    }

    async loadKanbanData() {
        try {
            const response = await fetch('/api/kanban/jobs');
            this.jobs = await response.json();
            this.renderBoard();
            this.updateStats();
        } catch (error) {
            console.error('Failed to load kanban data:', error);
        }
    }

    renderBoard() {
        const board = document.getElementById('kanban-board');
        // Render kanban columns and cards dynamically
        // HTML structure is already there, just populate data
    }

    updateStats() {
        document.getElementById('total-jobs').textContent = this.jobs.length;
        document.getElementById('in-progress-jobs').textContent = 
            this.jobs.filter(j => j.stage === 'in-progress').length;
    }
}

// Register module
window.ModuleRegistry['inhouse-kanban'] = {
    init: () => new InHouseKanbanModule('inhouse-kanban')
};
```

**Key Points for HTML Template Files:**
1. **Include `html_file` in manifest** - Module loader will fetch and inject HTML
2. **HTML loads BEFORE JavaScript** - DOM elements ready in `initialize()`
3. **Use IDs for key elements** - Easy to target from JavaScript
4. **Keep HTML semantic** - Use proper structure and accessibility
5. **Minimize inline JavaScript** - Keep logic in .js file

---

### Comparison Table

| Feature | JavaScript-Generated | HTML Template File |
|---------|---------------------|-------------------|
| **Flexibility** | ⭐⭐⭐⭐⭐ Very high | ⭐⭐⭐ Moderate |
| **Maintainability** | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| **Performance** | ⭐⭐⭐⭐ Fast render | ⭐⭐⭐⭐⭐ Pre-loaded |
| **Designer-Friendly** | ⭐⭐ Needs JS skills | ⭐⭐⭐⭐⭐ Pure HTML |
| **Dynamic Updates** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐ Manual updates |
| **File Count** | 2 files (JS + CSS) | 3 files (HTML + JS + CSS) |
| **Example Modules** | communication-hub, automation-workflows | inhouse-kanban, stock-management |

---

### Migration Path: HTML File → JavaScript

If you have an existing module with an HTML file and want to convert to JavaScript-generated UI:

```javascript
// Step 1: Copy your HTML file content
// Step 2: Create a method that generates the HTML

createModuleStructure() {
    const container = this.getContainer();
    
    // Paste your HTML here as template literal
    container.innerHTML = `
        <!-- Your HTML content from the .html file -->
        <div class="your-module-container">
            <!-- ... -->
        </div>
    `;
}

// Step 3: Remove html_file from manifest.json
// Step 4: Call createModuleStructure() in initialize()
// Step 5: Test and delete the old .html file
```

---

## JavaScript Patterns

### Class Structure Template

```javascript
/**
 * MODULE_NAME Module
 * Brief description of module purpose
 * 
 * @class ModuleNameModule
 * @extends BaseModule
 * @created YYYY-MM-DD
 * 
 * Features:
 * - Feature 1
 * - Feature 2
 * - Feature 3
 */
class ModuleNameModule extends BaseModule {
    constructor(moduleId) {
        super(moduleId);

        // Configuration
        this.apiEndpoint = '/api/module-name';
        this.backendUrl = 'http://localhost:5001';

        // State management
        this.currentView = 'default';
        this.data = {};

        // Data cache
        this.cache = new Map();
    }

    async initialize() {
        console.log('🔧 Initializing Module Name module...');

        // Apply module colors
        this.applyModuleColors();

        // Initialize UI from BaseModule
        await super.initialize();

        // Load initial data
        await this.loadInitialData();

        // Set up event listeners
        this.setupEventListeners();

        console.log('Module Name module ready');
    }

    async loadInitialData() {
        // Fetch data from backend
        try {
            const response = await fetch(`${this.backendUrl}${this.apiEndpoint}/data`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            this.data = await response.json();
        } catch (error) {
            console.error('Failed to load data:', error);
            this.showError('Failed to load module data');
        }
    }

    setupEventListeners() {
        // Add event listeners for user interactions
    }

    renderContent() {
        // Render module content
    }

    showError(message) {
        // Display error message to user
    }

    cleanup() {
        // Clean up resources before module unload
        super.cleanup();
    }
}

// Register module
window.ModuleNameModule = ModuleNameModule;
```

### Key Patterns from stock-management

**1. State Management:**
```javascript
constructor(moduleId) {
    super(moduleId);
    
    // Configuration (immutable)
    this.apiEndpoint = '/api/stock';
    
    // State (mutable)
    this.currentPeriod = 90;
    this.editingCell = null;
    
    // Caches (performance)
    this.charts = {};
    this.dataCache = new Map();
}
```

**2. Async/Await Pattern:**
```javascript
async initialize() {
    await super.initialize();  // Always call parent first
    await this.loadInitialData();
    this.setupUI();
}
```

**3. Error Handling:**
```javascript
try {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
} catch (error) {
    console.error('Operation failed:', error);
    this.showNotification('error', `Failed: ${error.message}`);
}
```

**4. Event Delegation:**
```javascript
setupEventListeners() {
    // Use event delegation for dynamic content
    document.querySelector(`#tab-${this.moduleId}`).addEventListener('click', (e) => {
        if (e.target.matches('.btn-action')) {
            this.handleAction(e.target.dataset.action);
        }
    });
}
```

---

## CSS Standards

### CSS File Structure

```css
/**
 * MODULE_NAME Module Styles
 * Version: 1.0.0
 * Last Updated: YYYY-MM-DD
 */

/* === VARIABLES === */
:root {
    --module-primary: #0078d4;
    --module-secondary: #00b294;
    --module-hover: #006cbe;
}

/* === MODULE CONTAINER === */
.module-my-module {
    /* Module-specific container styles */
}

/* === TABS === */
.module-my-module .tab-content {
    /* Tab content styles */
}

/* === COMPONENTS === */
.module-my-module .component-name {
    /* Component styles */
}

/* === UTILITIES === */
.module-my-module .btn-primary {
    background-color: var(--module-primary);
}

.module-my-module .btn-primary:hover {
    background-color: var(--module-hover);
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
    .module-my-module {
        /* Mobile styles */
    }
}
```

### CSS Best Practices

1. **Namespace all styles** with module class
2. **Use CSS variables** for colors (enables theming)
3. **Mobile-first responsive design**
4. **Consistent spacing** (use 8px grid)
5. **Accessibility** (focus states, ARIA support)

---

## Backend Integration

### Flask Routes Pattern

**File:** `{module_id}_routes.py`

```python
"""
{Module Name} Flask Routes
Provides API endpoints for {module_name} module

Routes:
- GET /api/{module-name}/data - Fetch data
- POST /api/{module-name}/action - Perform action
- PUT /api/{module-name}/update - Update data
- DELETE /api/{module-name}/delete - Delete data
"""

from flask import Blueprint, request, jsonify
import sqlite3
from pathlib import Path

# Create blueprint
{module_name}_bp = Blueprint('{module_name}', __name__)

def get_db_connection():
    """Get database connection"""
    db_path = Path(__file__).parent / 'module_data.db'
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


@{module_name}_bp.route('/api/{module-name}/data', methods=['GET'])
def get_data():
    """Fetch module data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM data_table")
        rows = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': [dict(row) for row in rows]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@{module_name}_bp.route('/api/{module-name}/action', methods=['POST'])
def perform_action():
    """Perform module action"""
    try:
        data = request.json
        # Process action
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Export blueprint
def register_routes(app):
    """Register module routes with Flask app"""
    app.register_blueprint({module_name}_bp)
```

### Backend Best Practices

1. **Use Blueprints** for module routes
2. **Consistent API patterns** (GET/POST/PUT/DELETE)
3. **Error handling** with try/except
4. **JSON responses** with success/error fields
5. **Database connections** properly closed
6. **CORS support** for frontend requests

---

## Documentation Requirements

### Required Documentation Files

1. **README.md** - Main module documentation
2. **IMPLEMENTATION_COMPLETE.md** - Implementation guide
3. **INTEGRATION_GUIDE.md** - Setup instructions

### README.md Template

```markdown
# {Module Name}

**Version:** 1.0.0  
**Module ID:** `{module-id}`  
**Author:** {Your Name}  
**Last Updated:** YYYY-MM-DD

## Overview
Brief description of what the module does.

## Features
- Feature 1
- Feature 2
- Feature 3

## Installation
Step-by-step setup instructions

## Usage
How to use the module

## Technical Details
Dependencies, API endpoints, configuration

## Troubleshooting
Common issues and solutions

## Changelog
Version history
```

---

## Testing Standards

### Test File Structure

```
my-module/
├── TEST_FEATURE.html              # Feature tests
├── USAGE_EXAMPLE.html             # Usage examples
└── VISUAL_DASHBOARD.html          # Visual demonstrations
```

### Test HTML Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Module Test - {Feature Name}</title>
    <style>
        /* Test page styles */
    </style>
</head>
<body>
    <h1>Module Test: {Feature Name}</h1>
    
    <div id="test-container">
        <!-- Test interface -->
    </div>
    
    <script>
        // Test code
        console.log('Testing {feature}...');
    </script>
</body>
</html>
```

---

## Validation Checklist

### Pre-Deployment Checklist

Run this checklist before deploying your module:

```bash
# 1. Validate module structure
python scripts/maintenance/validate_modules.py

# 2. Check for errors
# Expected output: ✅ {module-name}: VALID

# 3. Manual checks:
```

- [ ] Folder name matches module ID
- [ ] JavaScript file matches module ID
- [ ] CSS file matches module ID (or listed in manifest)
- [ ] Class extends BaseModule
- [ ] Constructor calls super(moduleId)
- [ ] manifest.json is valid JSON
- [ ] All tabs defined in manifest.json
- [ ] Backend routes registered (if applicable)
- [ ] README.md created
- [ ] Implementation guide created
- [ ] Test files created
- [ ] Module loads without console errors
- [ ] All features work as expected

---

## Reference Implementations

### Minimal Module
**Example:** `salesforce`
- Basic structure
- Single responsibility
- Clear naming

### Standard Module
**Example:** `database-visualizer`
- Full feature set
- External dependencies (Tabulator)
- Theme-specific CSS

### Advanced Module
**Example:** `stock-management` ⭐
- Comprehensive documentation
- Backend integration
- Enhanced features
- Multiple test files
- AI integration
- **Use this as your template!**

---

## Common Mistakes and Solutions

### Mistake 1: Folder Name Mismatch
```
❌ WRONG:
calculator-module/
└── manifest.json (id: "quote-calculator")

✅ CORRECT:
quote-calculator/
└── manifest.json (id: "quote-calculator")
```

### Mistake 2: Missing super() Call
```javascript
❌ WRONG:
constructor(moduleId) {
    this.data = {};
}

✅ CORRECT:
constructor(moduleId) {
    super(moduleId);  // MUST call super first!
    this.data = {};
}
```

### Mistake 3: Synchronous Code in Initialize
```javascript
❌ WRONG:
async initialize() {
    super.initialize();  // Missing await!
    this.loadData();     // Missing await!
}

✅ CORRECT:
async initialize() {
    await super.initialize();
    await this.loadData();
}
```

### Mistake 4: Not Cleaning Up Resources
```javascript
✅ CORRECT:
cleanup() {
    // Clean up event listeners
    this.removeEventListeners();
    
    // Clean up timers
    if (this.updateTimer) clearInterval(this.updateTimer);
    
    // Clean up charts
    Object.values(this.charts).forEach(chart => chart.destroy());
    
    // Call parent cleanup
    super.cleanup();
}
```

---

## Quick Start: New Module in 10 Minutes

1. **Create folder** (matches desired module ID):
   ```bash
   mkdir UI/external/modules/my-new-module
   cd UI/external/modules/my-new-module
   ```

2. **Create manifest.json**:
   ```json
   {
     "id": "my-new-module",
     "name": "My New Module",
     "version": "1.0.0",
     "icon": "fas fa-star",
     "colors": { "primary": "#3498db", "secondary": "#5dade2", "hover": "#2980b9" }
   }
   ```

3. **Create my-new-module.js** (use template from JavaScript Patterns section above)

4. **Create my-new-module.css** (use template from CSS Standards section above)

5. **Update main manifest**:
   Edit `UI/external/modules/manifest.json` and add your module entry

6. **Test**:
   ```bash
   python scripts/maintenance/validate_modules.py
   ```

7. **Deploy**:
   Reload browser - module should appear in sidebar!

---

## Getting Help

1. **Study the reference implementation:**
   - Location: `UI/external/modules/stock-management/`
   - Read all documentation files
   - Review code structure and patterns

2. **Use validation script:**
   ```bash
   python scripts/maintenance/validate_modules.py
   ```

3. **Check documentation:**
   - `Instructions.md` - Complete technical guide
   - `MODULE_BEST_PRACTICES.md` - This file
   - `ARCHITECTURE.md` - System architecture

4. **Review other modules:**
   - `salesforce/` - Minimal example
   - `database-visualizer/` - Standard example
   - `stock-management/` - Advanced example

---

**Remember:** When in doubt, follow the `stock-management` module pattern. It's battle-tested and production-ready! 🚀
