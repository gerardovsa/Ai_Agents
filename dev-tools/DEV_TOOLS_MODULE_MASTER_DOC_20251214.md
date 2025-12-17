# Dev-Tools Module Master Document
**Date:** December 14, 2025  
**Version:** 2.0  
**Status:** Production Ready

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [File Structure](#file-structure)
4. [Features](#features)
5. [API Integration](#api-integration)
6. [UI Components](#ui-components)
7. [Code Generation Workflow](#code-generation-workflow)
8. [Module Loading System](#module-loading-system)
9. [Styling & Design System](#styling--design-system)
10. [Usage Guide](#usage-guide)
11. [Development Notes](#development-notes)
12. [Troubleshooting](#troubleshooting)

---

## Overview

### Purpose
The Dev-Tools Module is a standalone HTML application that provides a complete development environment for creating custom modules for the AI Agents platform. It combines Monaco Editor for code editing with AI-powered code generation and a module management system.

### Key Capabilities
- **Visual Module Creator**: Build HTML, CSS, JavaScript, and Python modules
- **Monaco Editor Integration**: Full-featured code editor with syntax highlighting
- **AI Code Generation**: Stream AI-generated code directly into the editor
- **Module Loading**: Load and edit existing modules from the platform
- **Real-time Preview**: Test modules before deployment
- **Desktop Shortcut Access**: Quick launch via "Module Creator" shortcut

### Technology Stack
- **Editor**: Monaco Editor (VS Code engine)
- **AI Backend**: Flask (port 5001) with Claude Sonnet 4
- **Frontend**: Vanilla JavaScript (no frameworks)
- **Styling**: Custom CSS with platform design system
- **API**: REST endpoints for module management

---

## Architecture

### System Design
```
┌─────────────────────────────────────────────────────────┐
│                  Desktop Shortcut                        │
│              "Module Creator.lnk"                        │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│         module-creator-enhanced.html (Entry Point)       │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Monaco Editor Workspace                │    │
│  │  - HTML Tab                                    │    │
│  │  - CSS Tab                                     │    │
│  │  - JavaScript Tab                              │    │
│  │  - Routes Tab (Python)                         │    │
│  │  - Manifest Tab (JSON)                         │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Action Buttons                         │    │
│  │  [Load] [Save] [AI Generate] [Preview]        │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Console Output                         │    │
│  │  - Validation messages                         │    │
│  │  - Save confirmations                          │    │
│  │  - Error logs                                  │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         AI Chat Input Area                     │    │
│  │  - Prompt textarea                             │    │
│  │  - Generate button                             │    │
│  │  - Options (append/replace, include thinking)  │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Flask Backend (Port 5001)                   │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  /api/agent/stream                             │    │
│  │  - Streams AI-generated code                   │    │
│  │  - Uses Claude Sonnet 4                        │    │
│  │  - Returns thinking blocks + code              │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  /api/modules/list                             │    │
│  │  - Returns all available modules               │    │
│  │  - Includes metadata and file info             │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  /api/modules/{id}/files                       │    │
│  │  - Returns module source files                 │    │
│  │  - HTML, CSS, JS, Routes, Manifest             │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Component Interaction Flow
```
User Action → UI Event → JavaScript Handler → API Call → Flask Backend
                                   ↓
                          Monaco Editor Update
                                   ↓
                            Console Logging
                                   ↓
                          User Feedback (Visual)
```

---

## File Structure

### Core Files

#### `module-creator-enhanced.html` (Entry Point)
- **Location**: `C:\Users\gpoli\GIT\AI_agents\dev-tools\module-creator-enhanced.html`
- **Purpose**: Main HTML file that loads all dependencies
- **Dependencies**:
  - Monaco Editor (CDN)
  - Font Awesome 6.7.2
  - dev-tools-module.js
  - dev-tools-styles.css
- **Key Features**:
  - Monaco Editor container setup
  - Tab navigation UI
  - Action button toolbar
  - Console output area
  - AI chat input area

#### `dev-tools-module.js` (Core Logic)
- **Location**: `C:\Users\gpoli\GIT\AI_agents\dev-tools\dev-tools-module.js`
- **Lines**: 1,185+
- **Purpose**: All application logic and Monaco integration
- **Key Functions**:
  - `initializeEditor()` - Sets up Monaco Editor with 5 tabs
  - `showLoadDialog()` - Displays module list modal
  - `_loadModuleById(id)` - Fetches and loads module files
  - `saveModule()` - Validates and saves module to platform
  - `showAIPrompt()` - Shows AI chat input area
  - `generateWithAI()` - Streams code from AI backend
  - `_appendToEditor()` - Inserts AI code into active tab
  - `validateModule()` - Checks module structure and syntax
  - `_logToConsole(message, type)` - Console output handler

#### `dev-tools-styles.css` (Styling)
- **Location**: `C:\Users\gpoli\GIT\AI_agents\dev-tools\dev-tools-styles.css`
- **Lines**: 831+
- **Purpose**: All visual styling and layout
- **Key Sections**:
  - Root variables (colors, spacing)
  - Container layout (grid system)
  - Tab navigation styling
  - Monaco Editor wrapper
  - Button styles (action toolbar)
  - Console output styles
  - AI chat input area
  - Modal dialogs
  - Loading states

### Backend Integration Files

#### `module_routes.py` (Flask API)
- **Location**: `C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\module_routes.py`
- **Purpose**: REST API endpoints for module management
- **Endpoints**:
  ```python
  GET  /api/modules/list              # List all modules
  POST /api/modules/save              # Save new/updated module
  GET  /api/modules/{id}/files        # Get module source files
  GET  /api/modules/{id}/manifest     # Get module metadata
  ```

#### `flask_app.py` (Main Server)
- **Location**: `C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\flask_app.py`
- **Relevant Endpoints**:
  ```python
  POST /api/agent/stream              # AI code generation
  ```

---

## Features

### 1. Monaco Editor Integration

**Multi-Tab System:**
- **HTML Tab**: Module UI structure
- **CSS Tab**: Module styling
- **JavaScript Tab**: Module logic
- **Routes Tab**: Python Flask routes (optional)
- **Manifest Tab**: Module metadata (JSON)

**Editor Features:**
- Syntax highlighting for all languages
- IntelliSense and autocomplete
- Multi-cursor editing
- Find and replace
- Code folding
- Minimap navigation
- Line numbers and gutters

**Tab Switching:**
```javascript
function switchTab(tabName) {
    // Updates active tab visual state
    // Switches Monaco editor language mode
    // Preserves unsaved changes in each tab
}
```

### 2. Module Loading System

**Load Button Workflow:**
1. User clicks "Load Module" button
2. Modal opens with list of available modules
3. Each module card shows:
   - Module name
   - Description
   - File count
   - Last modified date
4. User clicks module card
5. System fetches module files via `/api/modules/{id}/files`
6. Files load into respective tabs:
   - HTML → HTML tab
   - CSS → CSS tab
   - JavaScript → JavaScript tab
   - Routes → Routes tab
   - Manifest → Manifest tab
7. Console logs confirmation
8. Modal closes automatically

**Smart File Detection:**
```javascript
// Handles multiple naming patterns:
// - {module-name}.html or index.html
// - {module-name}.css or styles.css
// - {module-name}.js or script.js or main.js
// - {module-name}_routes.py or routes.py
// - manifest.json
```

### 3. AI Code Generation

**Generate Button Workflow:**
1. User clicks "AI Generate" button
2. AI chat input area appears below console
3. User enters prompt (e.g., "Create a dashboard widget")
4. Optional settings:
   - **Append Mode**: Add to existing code
   - **Replace Mode**: Overwrite current tab
   - **Include Thinking**: Show AI reasoning in console
5. User clicks send button (paper plane icon)
6. System streams response from `/api/agent/stream`
7. Thinking blocks appear in console (if enabled)
8. Code blocks insert into active Monaco tab
9. Console shows completion message

**AI Streaming Format:**
```
[THINKING] Analyzing requirements...
[THINKING] Planning component structure...
[CODE] <div class="dashboard">...</div>
[THINKING] Adding responsive styles...
[CODE] .dashboard { display: grid; ... }
```

**Code Insertion Logic:**
```javascript
if (appendMode) {
    // Add to end of current content with newlines
    editor.setValue(currentContent + '\n\n' + aiCode);
} else {
    // Replace entire content
    editor.setValue(aiCode);
}
```

### 4. Save & Validation

**Save Button Workflow:**
1. User clicks "Save Module" button
2. System validates all tabs:
   - HTML: Check for valid structure
   - CSS: Check for syntax errors
   - JavaScript: Check for syntax errors
   - Routes: Validate Python syntax
   - Manifest: Validate JSON format
3. If validation passes:
   - POST to `/api/modules/save`
   - Console shows success message
   - Module appears in platform
4. If validation fails:
   - Console shows errors with line numbers
   - Highlights problematic tab
   - User can fix and retry

**Validation Rules:**
```javascript
// HTML: Must have <html>, <body> tags
// CSS: Must parse without syntax errors
// JavaScript: Must parse without syntax errors
// Routes: Must be valid Python (checked by backend)
// Manifest: Must be valid JSON with required fields:
//   - name (string)
//   - description (string)
//   - version (string)
//   - platform (string)
```

### 5. Console Output

**Log Types:**
- **Info** (blue): General messages, confirmations
- **Success** (green): Operations completed successfully
- **Warning** (yellow): Non-critical issues
- **Error** (red): Critical errors requiring attention
- **Thinking** (purple): AI reasoning process

**Console Features:**
- Auto-scroll to latest message
- Timestamp on each entry
- Color-coded message types
- Icon indicators (Font Awesome)
- Clear button to reset

**Usage:**
```javascript
_logToConsole('Module loaded successfully', 'success');
_logToConsole('Invalid JSON in manifest', 'error');
_logToConsole('Analyzing code structure...', 'thinking');
```

---

## API Integration

### Backend Requirements

**Flask Server:**
- **Host**: `http://localhost:5001`
- **CORS**: Enabled for dev-tools origin
- **Endpoints**: Module routes + AI streaming

**Environment:**
```bash
# Required in .env file
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://...
SUPABASE_KEY=...
```

### API Endpoints

#### 1. List Modules
```javascript
GET /api/modules/list

Response:
{
    "modules": [
        {
            "id": "quote-calculator",
            "name": "Quote Calculator",
            "description": "Calculate quotes for various products",
            "platform": "quote_system",
            "files": ["html", "css", "js", "routes", "manifest"],
            "last_modified": "2025-12-14T10:30:00Z"
        }
    ]
}
```

#### 2. Get Module Files
```javascript
GET /api/modules/{module_id}/files

Response:
{
    "success": true,
    "files": {
        "html": "<div class='module'>...</div>",
        "css": ".module { display: grid; }",
        "js": "function init() { ... }",
        "routes": "from flask import Blueprint...",
        "manifest": "{\"name\": \"Module Name\"}"
    }
}
```

#### 3. Save Module
```javascript
POST /api/modules/save
Content-Type: application/json

Request Body:
{
    "name": "my-module",
    "html": "<div>...</div>",
    "css": ".class { }",
    "js": "function() {}",
    "routes": "# Python code",
    "manifest": {
        "name": "My Module",
        "description": "...",
        "version": "1.0.0",
        "platform": "custom"
    }
}

Response:
{
    "success": true,
    "message": "Module saved successfully",
    "module_id": "my-module"
}
```

#### 4. AI Code Generation
```javascript
POST /api/agent/stream
Content-Type: application/json

Request Body:
{
    "message": "Create a dashboard widget with charts",
    "context": {
        "current_code": "...",
        "language": "html",
        "append_mode": true
    }
}

Response: (Server-Sent Events stream)
data: {"type": "thinking", "content": "Planning structure..."}
data: {"type": "code", "content": "<div class='widget'>..."}
data: {"type": "complete"}
```

### Error Handling

**Network Errors:**
```javascript
try {
    const response = await fetch(url, options);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
} catch (error) {
    _logToConsole(`API Error: ${error.message}`, 'error');
    // Show user-friendly error in UI
}
```

**Backend Down:**
```javascript
// If Flask server not running on port 5001
// Show connection error in console
// Disable AI Generate and Load buttons
// Suggest starting server in terminal
```

---

## UI Components

### Header Section
```html
<div class="header">
    <h1>
        <i class="fas fa-code"></i>
        Module Development Tools
    </h1>
    <div class="header-subtitle">
        Create and manage custom modules for the AI platform
    </div>
</div>
```

### Tab Navigation
```html
<div class="tabs">
    <div class="tab active" data-tab="html">
        <i class="fab fa-html5"></i> HTML
    </div>
    <div class="tab" data-tab="css">
        <i class="fab fa-css3-alt"></i> CSS
    </div>
    <div class="tab" data-tab="javascript">
        <i class="fab fa-js"></i> JavaScript
    </div>
    <div class="tab" data-tab="routes">
        <i class="fab fa-python"></i> Routes
    </div>
    <div class="tab" data-tab="manifest">
        <i class="fas fa-file-code"></i> Manifest
    </div>
</div>
```

### Action Buttons
```html
<div class="action-buttons">
    <button class="btn btn-secondary" onclick="showLoadDialog()">
        <i class="fas fa-folder-open"></i> Load Module
    </button>
    <button class="btn btn-primary" onclick="saveModule()">
        <i class="fas fa-save"></i> Save Module
    </button>
    <button class="btn btn-ai" onclick="showAIPrompt()">
        <i class="fas fa-robot"></i> AI Generate
    </button>
    <button class="btn btn-secondary" onclick="previewModule()">
        <i class="fas fa-eye"></i> Preview
    </button>
</div>
```

### Monaco Editor Container
```html
<div id="editor-container">
    <!-- Monaco Editor mounts here -->
</div>
```

### Console Output
```html
<div class="console-panel">
    <div class="console-header">
        <span>
            <i class="fas fa-terminal"></i> Console Output
        </span>
        <button class="btn-clear" onclick="clearConsole()">
            <i class="fas fa-trash"></i> Clear
        </button>
    </div>
    <div class="console-content" id="console-output">
        <!-- Log messages appear here -->
    </div>
</div>
```

### AI Chat Input Area
```html
<div class="ai-chat-area" style="display: none;">
    <div class="ai-input-group">
        <textarea 
            id="ai-prompt-input" 
            placeholder="Describe what you want to create..."
            rows="3"
        ></textarea>
        <button onclick="generateWithAI()">
            <i class="fas fa-paper-plane"></i>
        </button>
    </div>
    <div class="ai-options">
        <label>
            <input type="checkbox" id="append-mode" checked>
            Append to current code
        </label>
        <label>
            <input type="checkbox" id="include-thinking">
            Show AI thinking
        </label>
    </div>
</div>
```

### Load Module Modal
```html
<div class="modal" id="load-modal">
    <div class="modal-content">
        <div class="modal-header">
            <h3>Load Module</h3>
            <button class="modal-close" onclick="closeLoadDialog()">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="modal-body" id="module-list">
            <!-- Module cards appear here -->
        </div>
    </div>
</div>
```

---

## Code Generation Workflow

### Complete AI Generation Flow

**Step 1: User Input**
```
User clicks "AI Generate" button
  ↓
AI chat area slides in below console
  ↓
User types prompt: "Create a responsive navbar with dropdowns"
  ↓
User selects options:
  - [✓] Append to current code
  - [✓] Show AI thinking
  ↓
User clicks send button (paper plane icon)
```

**Step 2: API Request**
```javascript
const response = await fetch('http://localhost:5001/api/agent/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: userPrompt,
        context: {
            current_code: editor.getValue(),
            language: activeTab,
            append_mode: appendCheckbox.checked
        }
    })
});
```

**Step 3: Stream Processing**
```javascript
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');
    
    for (const line of lines) {
        if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            
            if (data.type === 'thinking') {
                // Show in console with purple color
                _logToConsole(data.content, 'thinking');
            }
            else if (data.type === 'code') {
                // Insert into Monaco editor
                _appendToEditor(data.content);
            }
        }
    }
}
```

**Step 4: Code Insertion**
```javascript
function _appendToEditor(code) {
    const currentContent = editor.getValue();
    const appendMode = document.getElementById('append-mode').checked;
    
    if (appendMode) {
        // Add to end with spacing
        editor.setValue(currentContent + '\n\n' + code);
        // Scroll to bottom
        editor.revealLine(editor.getModel().getLineCount());
    } else {
        // Replace all content
        editor.setValue(code);
    }
    
    // Format code
    editor.getAction('editor.action.formatDocument').run();
}
```

**Step 5: User Review**
```
Generated code appears in editor
  ↓
User reviews the code
  ↓
User can:
  - Edit the generated code manually
  - Generate more code (append mode)
  - Save the module
  - Ask AI to refine specific sections
```

### Example AI Prompts

**Create New Component:**
```
"Create a card component with image, title, description, and action button"
```

**Add Functionality:**
```
"Add a search filter to the table that filters rows in real-time"
```

**Improve Styling:**
```
"Make the navigation responsive with a hamburger menu on mobile"
```

**Fix Issues:**
```
"Fix the CSS so the sidebar doesn't overlap on small screens"
```

**Generate Python Routes:**
```
"Create Flask routes for CRUD operations on a tasks database table"
```

---

## Module Loading System

### Load Dialog UI

**Modal Structure:**
```
┌─────────────────────────────────────────────┐
│  Load Module                            [×] │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Quote Calculator                    │   │
│  │ Calculate quotes for various...     │   │
│  │ Files: HTML, CSS, JS, Routes        │   │
│  │ Modified: Dec 14, 2025              │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Dashboard Widget                    │   │
│  │ Interactive dashboard with...       │   │
│  │ Files: HTML, CSS, JS                │   │
│  │ Modified: Dec 13, 2025              │   │
│  └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

### Module Card Template
```javascript
function createModuleCard(module) {
    return `
        <div class="module-card" onclick="_loadModuleById('${module.id}')">
            <div class="module-card-header">
                <h4>${module.name}</h4>
                <span class="module-platform">${module.platform}</span>
            </div>
            <p class="module-description">${module.description}</p>
            <div class="module-meta">
                <span>
                    <i class="fas fa-file-code"></i>
                    ${module.files.length} files
                </span>
                <span>
                    <i class="fas fa-clock"></i>
                    ${formatDate(module.last_modified)}
                </span>
            </div>
        </div>
    `;
}
```

### File Loading Logic
```javascript
async function _loadModuleById(moduleId) {
    try {
        // Fetch module files from API
        const response = await fetch(
            `http://localhost:5001/api/modules/${moduleId}/files`
        );
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to load module');
        }
        
        // Load each file into respective tab
        const tabs = {
            'html': data.files.html || '',
            'css': data.files.css || '',
            'javascript': data.files.js || '',
            'routes': data.files.routes || '',
            'manifest': data.files.manifest || ''
        };
        
        // Update Monaco editors for each tab
        Object.keys(tabs).forEach(tab => {
            if (tabs[tab]) {
                // Store in memory (will load when tab switched)
                editorContents[tab] = tabs[tab];
            }
        });
        
        // Switch to HTML tab and load content
        switchTab('html');
        editor.setValue(tabs.html);
        
        // Log success
        _logToConsole(
            `Module "${moduleId}" loaded successfully`,
            'success'
        );
        
        // Close modal
        closeLoadDialog();
        
    } catch (error) {
        _logToConsole(
            `Error loading module: ${error.message}`,
            'error'
        );
    }
}
```

---

## Styling & Design System

### Color Palette

**Dark Theme:**
```css
:root {
    /* Background Colors */
    --dev-tools-bg: #0a0a0a;           /* Main background */
    --dev-tools-panel-bg: #141414;     /* Panel background */
    --dev-tools-header-bg: #1a1a1a;    /* Header background */
    
    /* Text Colors */
    --dev-tools-text-primary: #e5e7eb;  /* Primary text */
    --dev-tools-text-secondary: #9ca3af; /* Secondary text */
    --dev-tools-text-muted: #6b7280;    /* Muted text */
    
    /* Accent Colors */
    --dev-tools-accent: #667eea;        /* Primary accent (blue) */
    --dev-tools-accent-hover: #7c3aed;  /* Hover state (purple) */
    --dev-tools-success: #10b981;       /* Success (green) */
    --dev-tools-warning: #f59e0b;       /* Warning (yellow) */
    --dev-tools-error: #ef4444;         /* Error (red) */
    
    /* Border Colors */
    --dev-tools-border: #2d3748;        /* Standard border */
    --dev-tools-border-light: #374151;  /* Light border */
    
    /* Spacing */
    --dev-tools-spacing-xs: 4px;
    --dev-tools-spacing-sm: 8px;
    --dev-tools-spacing-md: 16px;
    --dev-tools-spacing-lg: 24px;
    --dev-tools-spacing-xl: 32px;
}
```

### Component Styles

**Buttons:**
```css
.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s;
}

.btn-primary {
    background: var(--dev-tools-accent);
    color: white;
}

.btn-primary:hover {
    background: var(--dev-tools-accent-hover);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-ai {
    background: #667eea;
    color: white;
}

.btn-ai:hover {
    background: #667eea;
    transform: scale(1.1);
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}
```

**Tabs:**
```css
.tab {
    padding: 12px 24px;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    gap: 8px;
}

.tab:hover {
    background: rgba(102, 126, 234, 0.1);
}

.tab.active {
    border-bottom-color: var(--dev-tools-accent);
    color: var(--dev-tools-accent);
}
```

**Console:**
```css
.console-panel {
    background: var(--dev-tools-panel-bg);
    border-top: 1px solid var(--dev-tools-border);
    height: 200px;
    display: flex;
    flex-direction: column;
}

.console-content {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
}

.log-entry {
    padding: 6px 10px;
    margin: 2px 0;
    border-radius: 4px;
    display: flex;
    gap: 8px;
}

.log-entry.info { color: #60a5fa; }
.log-entry.success { color: #34d399; }
.log-entry.warning { color: #fbbf24; }
.log-entry.error { color: #f87171; }
.log-entry.thinking { color: #a78bfa; }
```

**AI Chat Input:**
```css
.ai-chat-area {
    background: transparent;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.ai-input-group {
    position: relative;
    width: 100%;
}

.ai-input-group textarea {
    width: 100%;
    padding: 12px 50px 12px 16px;
    border: 1px solid rgba(75, 85, 99, 0.5);
    border-radius: 8px;
    background: rgba(17, 24, 39, 0.95);
    color: #e5e7eb;
    resize: vertical;
    min-height: 80px;
}

.ai-input-group button {
    position: absolute;
    bottom: 8px;
    right: 8px;
    width: 36px;
    height: 36px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 6px;
}
```

### Responsive Design

**Desktop (1920px+):**
- Full Monaco editor width
- Side-by-side panels
- Large console (200px height)

**Laptop (1366px):**
- Slightly narrower editor
- Maintained panel layout
- Console at 180px height

**Tablet (768px):**
- Stacked panels
- Compact tab navigation
- Console at 150px height

**Mobile (< 768px):**
- Not optimized (desktop app)
- Use desktop with minimum 1024px width

---

## Usage Guide

### Getting Started

**1. Start Flask Backend:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
python flask_app.py
```

**2. Launch Dev-Tools:**
- Double-click "Module Creator" desktop shortcut
- OR open `module-creator-enhanced.html` in browser

**3. Choose Workflow:**

**Option A: Create New Module**
1. Start typing in HTML tab
2. Switch to CSS tab for styling
3. Add JavaScript logic
4. Optionally add Python routes
5. Fill in manifest.json
6. Click "Save Module"

**Option B: Load Existing Module**
1. Click "Load Module" button
2. Select module from list
3. Edit files in Monaco editor
4. Click "Save Module" to update

**Option C: AI-Powered Creation**
1. Click "AI Generate" button
2. Describe what you want in the prompt
3. Choose append/replace mode
4. Click send (paper plane icon)
5. Review generated code
6. Refine with additional AI prompts
7. Click "Save Module"

### Best Practices

**Module Structure:**
```
my-module/
├── my-module.html          # Main UI (required)
├── my-module.css           # Styling (recommended)
├── my-module.js            # Logic (recommended)
├── my-module_routes.py     # Backend routes (optional)
└── manifest.json           # Metadata (required)
```

**Manifest.json Template:**
```json
{
    "name": "My Module",
    "description": "Brief description of what this module does",
    "version": "1.0.0",
    "platform": "custom",
    "author": "Your Name",
    "dependencies": [],
    "entry_point": "my-module.html"
}
```

**Naming Conventions:**
- Use kebab-case: `my-module-name`
- Avoid spaces and special characters
- Keep names under 30 characters
- Be descriptive but concise

**Code Organization:**
```javascript
// JavaScript best practices
(function() {
    'use strict';
    
    // Constants at top
    const CONFIG = {
        apiUrl: 'http://localhost:5001',
        refreshInterval: 5000
    };
    
    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', init);
    
    function init() {
        setupEventListeners();
        loadInitialData();
    }
    
    // Group related functions
    function setupEventListeners() { }
    function loadInitialData() { }
    
})();
```

### Testing Modules

**Preview Function:**
```javascript
function previewModule() {
    const html = editors.html.getValue();
    const css = editors.css.getValue();
    const js = editors.javascript.getValue();
    
    const previewWindow = window.open('', '_blank');
    previewWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <style>${css}</style>
        </head>
        <body>
            ${html}
            <script>${js}</script>
        </body>
        </html>
    `);
}
```

**Manual Testing:**
1. Save module
2. Refresh main AI platform
3. Navigate to module
4. Test all functionality
5. Check console for errors
6. Verify responsive design

---

## Development Notes

### Recent Updates (Dec 14, 2025)

**Completed Features:**
- ✅ Monaco Editor integration with 5 tabs
- ✅ Load Module dialog with API integration
- ✅ AI code generation with streaming
- ✅ Console output with colored logs
- ✅ Save module with validation
- ✅ Inline AI chat input area (not modal)
- ✅ Append/replace code modes
- ✅ Thinking process display option

**Fixed Issues:**
- ✅ CSS/HTML selector mismatch (h1 vs h2)
- ✅ Tab navigation class names (tab vs file-tab)
- ✅ Load button placeholder ("coming soon")
- ✅ AI chat styling (removed purple gradient)
- ✅ API base URL (localhost:5001)
- ✅ Modal replaced with inline chat area

**Known Limitations:**
- Preview function opens new window (not iframe)
- No syntax validation for Python routes (done backend)
- No auto-save functionality
- No version control integration
- No collaborative editing

### Architecture Decisions

**Why Monaco Editor?**
- Industry-standard (VS Code engine)
- Excellent IntelliSense
- Multi-language support
- Active maintenance
- Easy CDN integration

**Why Vanilla JavaScript?**
- No build process needed
- Faster load times
- Easier debugging
- No framework dependencies
- Simpler deployment

**Why Flask Backend?**
- Already in platform stack
- Easy Python integration
- WebSocket support for streaming
- Familiar to team
- Good performance

**Why Inline Chat (Not Modal)?**
- Better workflow continuity
- Easier to reference code while prompting
- Matches main platform UX
- Less context switching
- More screen space for editor

### Future Enhancements

**High Priority:**
- [ ] Auto-save drafts to localStorage
- [ ] Undo/redo for entire module state
- [ ] Export module as ZIP file
- [ ] Import module from ZIP file
- [ ] Keyboard shortcuts (Ctrl+S to save)
- [ ] Dark/light theme toggle

**Medium Priority:**
- [ ] Multi-module workspace
- [ ] Git integration for version control
- [ ] Diff viewer for module updates
- [ ] Template library (starter templates)
- [ ] Search and replace across all files
- [ ] Code snippets library

**Low Priority:**
- [ ] Collaborative editing (multiple users)
- [ ] Real-time preview (iframe)
- [ ] Integrated debugger
- [ ] Performance profiling
- [ ] Accessibility checker
- [ ] Mobile responsive editing

---

## Troubleshooting

### Common Issues

**Issue: Monaco Editor Not Loading**
```
Symptom: Blank editor area, no syntax highlighting
Cause: CDN blocked or slow connection
Fix:
1. Check browser console for CDN errors
2. Verify internet connection
3. Try different CDN URL
4. Clear browser cache
```

**Issue: Load Button Shows No Modules**
```
Symptom: Modal opens but no module cards appear
Cause: Flask backend not running or API error
Fix:
1. Check Flask is running on port 5001
2. Check console for API errors
3. Verify /api/modules/list endpoint works:
   curl http://localhost:5001/api/modules/list
4. Check Flask logs for errors
```

**Issue: AI Generate Not Working**
```
Symptom: Clicking send does nothing or shows error
Cause: Backend issue or missing API key
Fix:
1. Verify Flask server running
2. Check ANTHROPIC_API_KEY in .env
3. Check browser console for errors
4. Test endpoint manually:
   curl -X POST http://localhost:5001/api/agent/stream
5. Check Flask logs for Claude API errors
```

**Issue: Save Module Fails**
```
Symptom: Console shows "Failed to save module"
Cause: Validation error or backend issue
Fix:
1. Check console for specific error message
2. Verify manifest.json is valid JSON
3. Ensure all required fields present
4. Check Flask logs for backend errors
5. Try saving individual files first
```

**Issue: Code Not Inserting from AI**
```
Symptom: AI generates but code doesn't appear
Cause: Streaming parse error or editor issue
Fix:
1. Check browser console for JS errors
2. Verify active tab is selected
3. Check append/replace mode setting
4. Try refreshing page and retry
5. Check network tab for stream errors
```

### Debug Mode

**Enable Verbose Logging:**
```javascript
// Add to top of dev-tools-module.js
window.DEBUG_MODE = true;

// In functions, add:
if (window.DEBUG_MODE) {
    console.log('[DEBUG]', 'Function called with:', args);
}
```

**Check Flask Backend:**
```powershell
# View recent logs
Get-Content C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\flask_app.log -Tail 50

# Test endpoint
Invoke-WebRequest -Uri "http://localhost:5001/api/modules/list" | ConvertFrom-Json
```

**Browser DevTools:**
```
1. Press F12 to open DevTools
2. Check Console tab for JavaScript errors
3. Check Network tab for API failures
4. Check Application tab for localStorage issues
```

### Performance Optimization

**Large Modules:**
```javascript
// If module files > 1MB, consider:
// 1. Lazy load Monaco editor
// 2. Debounce validation
// 3. Paginate console output
// 4. Stream file loading
```

**Memory Management:**
```javascript
// Clear console periodically
if (consoleEntries.length > 1000) {
    clearConsole();
}

// Dispose Monaco models when switching
editor.getModel()?.dispose();
```

---

## Appendix

### Keyboard Shortcuts

**Monaco Editor (Standard VS Code):**
- `Ctrl+S` - Save (custom handler)
- `Ctrl+F` - Find
- `Ctrl+H` - Replace
- `Ctrl+/` - Toggle comment
- `Alt+Shift+F` - Format document
- `Ctrl+Space` - Trigger IntelliSense
- `F12` - Go to definition
- `Ctrl+D` - Select next occurrence
- `Alt+Up/Down` - Move line

**Custom Shortcuts (Future):**
- `Ctrl+Shift+L` - Load module
- `Ctrl+Shift+A` - AI generate
- `Ctrl+Shift+P` - Preview module

### File Size Limits

**Recommended:**
- HTML: < 500 KB
- CSS: < 200 KB
- JavaScript: < 500 KB
- Routes: < 100 KB
- Manifest: < 10 KB

**Maximum:**
- Total module size: < 2 MB
- Individual file: < 1 MB

### Browser Compatibility

**Supported:**
- ✅ Chrome 90+
- ✅ Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+

**Not Supported:**
- ❌ Internet Explorer
- ❌ Opera Mini
- ❌ Mobile browsers (not optimized)

### Dependencies

**CDN Resources:**
```html
<!-- Monaco Editor -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs/loader.min.js"></script>

<!-- Font Awesome -->
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css" rel="stylesheet">
```

**Backend Dependencies:**
```
Flask==3.0.0
anthropic==0.40.0
flask-cors==4.0.0
```

### Contact & Support

**For Issues:**
1. Check this document first
2. Search Flask logs
3. Check browser console
4. Test API endpoints manually
5. Contact platform team

**For Feature Requests:**
1. Document use case
2. Explain expected behavior
3. Provide examples
4. Submit to platform roadmap

---

**Document Version:** 2.0  
**Last Updated:** December 14, 2025  
**Maintained By:** AI Agents Platform Team  
**Status:** Production Ready ✅
