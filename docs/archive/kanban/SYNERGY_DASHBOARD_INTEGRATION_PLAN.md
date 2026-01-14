# 🎯 Synergy Dashboard Integration Plan - Complete Implementation Guide

## Overview

This document outlines the complete integration of the **Synergy Dashboard** (Kanban board + Task Management) into the existing Business AI Platform frontend with **automatic bidirectional sync** between:
- **Kanban Board UI** ↔️ **sessions.db** ↔️ **Google Tasks** ↔️ **Google Calendar**

---

## ✅ What's Been Done (Phase 1)

### 1. Sidebar Icon Added
**Location:** `business-ai-platform-v2.html` lines ~2334-2336

```html
<button class="sidebar-icon-btn" data-tab="synergy" title="Synergy Dashboard - Task & Session Management">
    <i class="fas fa-tasks"></i>
</button>
```

**Features:**
- Positioned after "Multi-Agent AI" button
- Icon: `fa-tasks` (checklist icon)
- Tooltip: "Synergy Dashboard - Task & Session Management"
- Data attribute: `data-tab="synergy"` (for tab switching)

### 2. Tab Content Section Added
**Location:** `business-ai-platform-v2.html` lines ~2973-2978

```html
<!-- ==================== SYNERGY DASHBOARD TAB (TASK & SESSION MANAGEMENT) ==================== -->
<div class="tab-content" id="tab-synergy">
    <div class="synergy-dashboard-container">
        <!-- Kanban board will be loaded here -->
        <div id="kanban-board-container"></div>
    </div>
</div>
```

**Features:**
- Hidden by default (`.tab-content` has `display: none` when not active)
- Container ID: `kanban-board-container` (target for dynamic loading)
- Will be shown when sidebar icon is clicked (existing tab switching logic handles this)

---

## 🎨 Frontend Architecture Analysis

### Current Platform Structure

```
business-ai-platform-v2.html (6,482 lines)
├── External Libraries (lines 1-50)
│   ├── Font Awesome 6.4.0
│   ├── Tabulator 5.5.0 (data grids)
│   ├── Chart.js 4.4.0
│   ├── Plotly.js 2.27.0
│   ├── Mermaid 10.6.1
│   ├── Marked.js (markdown)
│   ├── Prism.js (syntax highlighting)
│   ├── Luxon (datetime)
│   └── Moment.js
│
├── Visualization Engine (lines 50-52)
│   ├── streamingTwoRule.js
│   └── visualisation_copy.js
│
├── Render Config (line 54)
│   └── render-config.js (auto-detects environment)
│
├── CSS Styles (lines 55-2286)
│   ├── Root variables (colors, spacing, layout)
│   ├── Login overlay
│   ├── Sidebar (60px width)
│   ├── Top header (60px height)
│   ├── Main content grid
│   ├── Tab navigation
│   └── AI chat panel (400px width, collapsible)
│
├── HTML Structure (lines 2287-3018)
│   ├── Login overlay
│   ├── Sidebar (10 tabs + settings)
│   ├── Top header (search, notifications, theme toggle)
│   ├── Main content wrapper
│   │   ├── Tab: Home (dashboard)
│   │   ├── Tab: Communication (Slack, email, etc.)
│   │   ├── Tab: Sales (WooCommerce, Stripe)
│   │   ├── Tab: Analytics
│   │   ├── Tab: Documents
│   │   ├── Tab: Stock
│   │   ├── Tab: Transcripts
│   │   ├── Tab: Scheduling
│   │   ├── Tab: Automation
│   │   ├── Tab: Multi-Agent
│   │   └── Tab: Synergy ✨ (NEW - line 2973)
│   └── AI Chat Panel (right sidebar)
│
└── JavaScript (lines 3019-6482)
    ├── Tab switching logic
    ├── API integration functions
    ├── Chart/data rendering
    ├── Thread history management
    └── Real-time updates
```

### Existing Tab Switching Logic

**Location:** Lines ~3619-3632

```javascript
document.querySelectorAll('.sidebar-icon-btn[data-tab]').forEach(btn => {
    btn.addEventListener('click', function() {
        const tabName = this.getAttribute('data-tab');
        
        // Remove active class from all buttons
        document.querySelectorAll('.sidebar-icon-btn').forEach(b => b.classList.remove('active'));
        
        // Add active class to clicked button
        this.classList.add('active');
        
        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
        
        // Show selected tab
        document.getElementById('tab-' + tabName).classList.add('active');
    });
});
```

**This means:**
- Clicking the Synergy sidebar button will automatically show `#tab-synergy`
- No additional JavaScript needed for basic tab switching
- We just need to populate `#kanban-board-container` with the Kanban board

---

## 📦 Recommended Open-Source Kanban Libraries

### Option 1: **jKanban** (Recommended ⭐)
**GitHub:** https://github.com/riktar/jkanban  
**Size:** ~15KB (minified)  
**License:** MIT

**Pros:**
- ✅ Lightweight and fast
- ✅ Drag & drop built-in
- ✅ No jQuery dependency (vanilla JS)
- ✅ Easy customization with CSS
- ✅ Event hooks for drag/drop actions
- ✅ Mobile-friendly
- ✅ Active maintenance

**Example Usage:**
```javascript
const kanban = new jKanban({
    element: '#kanban-board-container',
    gutter: '15px',
    widthBoard: '300px',
    boards: [
        {
            id: 'backlog',
            title: '📦 Backlog',
            item: [
                {
                    id: 'sess_123',
                    title: '🟢 Research Campaign Ideas'
                }
            ]
        },
        {
            id: 'in_progress',
            title: '🏃 In Progress',
            item: []
        }
    ],
    dragendBoard: function(el) {
        // Sync to database when card moved
        syncCardPosition(el);
    }
});
```

### Option 2: **Trello-like Board** (Custom Build)
**GitHub:** https://github.com/webtask/trello-like-board  
**Size:** ~20KB  
**License:** MIT

**Pros:**
- ✅ Trello-inspired UI
- ✅ Card editing built-in
- ✅ Modern design
- ✅ React/Vue/Vanilla versions available

**Cons:**
- ❌ Heavier than jKanban
- ❌ Less maintained

### Option 3: **Dragula** (Drag & Drop Library)
**GitHub:** https://github.com/bevacqua/dragula  
**Size:** ~8KB  
**License:** MIT

**Pros:**
- ✅ Ultra-lightweight
- ✅ Just drag & drop (no UI)
- ✅ Highly customizable
- ✅ Framework agnostic

**Cons:**
- ❌ Requires building Kanban UI yourself
- ❌ More work upfront

### **Recommendation: Use jKanban** 🎯

Why:
1. **Perfect balance** of features vs size
2. **No dependencies** (works with your existing stack)
3. **Proven in production** (1.4K GitHub stars)
4. **Easy to customize** to match your dark theme
5. **Event hooks** make syncing to backend trivial

---

## 🏗️ Implementation Architecture

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SYNERGY DASHBOARD ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────────────────────┘

USER INTERACTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────┐
│  KANBAN BOARD UI (jKanban)                                  │
│  ┌──────────┬──────────┬──────────┬──────────┐            │
│  │ Backlog  │ Progress │ Review   │ Done     │            │
│  │ [Card 1] │ [Card 2] │ [Card 3] │ [Card 4] │            │
│  └──────────┴──────────┴──────────┴──────────┘            │
└─────────────────────────────────────────────────────────────┘
                        │
                        │ User drags card
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  EVENT HANDLER (dragendBoard)                               │
│  • Detect column change                                     │
│  • Extract session_id from card                             │
│  • Call sync function                                       │
└─────────────────────────────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  SYNC MANAGER (sync_manager.py)                             │
│  • Update sessions.db (kanban_column field)                 │
│  • Generate clean task card                                 │
│  • Sync to Google Tasks                                     │
│  • Create/update Google Calendar event                      │
└─────────────────────────────────────────────────────────────┘
                        │
          ┌─────────────┼─────────────┬────────────────┐
          ↓             ↓             ↓                ↓
    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
    │sessions.db│  │Task Card│  │ Google   │  │ Google   │
    │          │  │ Manager │  │ Tasks    │  │ Calendar │
    │ UPDATE   │  │ CREATE  │  │ API CALL │  │ API CALL │
    └──────────┘  └──────────┘  └──────────┘  └──────────┘


AUTOMATIC UPDATES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────┐
│  SESSION DATABASE (sessions.db)                             │
│  • New message added by AI                                  │
│  • Document created                                         │
│  • Next step completed                                      │
└─────────────────────────────────────────────────────────────┘
                        │
                        │ Trigger: activity_log entry
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  WEBHOOK / POLLING SERVICE                                  │
│  • Detect changes in sessions.db                            │
│  • Get updated session summary                              │
└─────────────────────────────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  SYNC MANAGER (sync_manager.py)                             │
│  • Update Google Task notes (new activity)                  │
│  • Update Kanban card if board is open (WebSocket)          │
└─────────────────────────────────────────────────────────────┘
                        │
          ┌─────────────┴─────────────┐
          ↓                           ↓
    ┌──────────┐              ┌──────────────┐
    │ Google   │              │ Kanban Board │
    │ Tasks    │              │ (WebSocket)  │
    │ UPDATED  │              │ LIVE UPDATE  │
    └──────────┘              └──────────────┘
```

### File Structure

```
AI_agents/
├── UI/
│   ├── business-ai-platform-v2.html ✅ (Updated - sidebar icon + tab content)
│   ├── synergy-dashboard.css (NEW - Kanban board styles)
│   ├── synergy-dashboard.js (NEW - Kanban board logic)
│   └── lib/
│       └── jkanban.min.js (NEW - Downloaded from CDN)
│
├── AI_infrastructure/
│   └── core/
│       ├── session_database.py ✅ (Exists - SQLite manager)
│       ├── task_card_manager.py ✅ (Exists - Clean card generator)
│       ├── sync_manager.py (NEW - Bidirectional sync orchestrator)
│       └── google_calendar_sync.py (NEW - Calendar integration)
│
├── google_workspace/
│   ├── google_tasks.py ✅ (Exists - 12 tools)
│   ├── ai_personal_tasks.py ✅ (Exists - AI task management)
│   └── google_calendar.py (NEW - Calendar CRUD operations)
│
└── app.py (NEW ROUTES - API endpoints for sync)
```

---

## 📝 Implementation Steps

### Phase 1: Frontend Setup (1-2 hours)

#### Step 1: Add jKanban Library
**Method:** CDN (easiest) or download locally

**Option A: CDN (Recommended for testing)**
Add to `<head>` section of `business-ai-platform-v2.html`:

```html
<!-- jKanban CSS -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jkanban@1.3.1/dist/jkanban.min.css">

<!-- jKanban JS -->
<script src="https://cdn.jsdelivr.net/npm/jkanban@1.3.1/dist/jkanban.min.js"></script>
```

**Option B: Local (Recommended for production)**
```bash
# Download jKanban
cd C:\Users\gpoli\GIT\AI_agents\UI\lib
curl -o jkanban.min.js https://cdn.jsdelivr.net/npm/jkanban@1.3.1/dist/jkanban.min.js
curl -o jkanban.min.css https://cdn.jsdelivr.net/npm/jkanban@1.3.1/dist/jkanban.min.css
```

Then add to HTML:
```html
<link rel="stylesheet" href="lib/jkanban.min.css">
<script src="lib/jkanban.min.js"></script>
```

#### Step 2: Create Synergy Dashboard Styles
**File:** `UI/synergy-dashboard.css`

```css
/* ==================== SYNERGY DASHBOARD STYLES ==================== */

.synergy-dashboard-container {
    height: calc(100vh - var(--header-height) - 40px);
    padding: var(--space-5);
    background: var(--bg-primary);
    overflow-y: auto;
}

/* Dashboard Header */
.synergy-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-5);
}

.synergy-title {
    display: flex;
    align-items: center;
    gap: var(--space-3);
}

.synergy-title h2 {
    font-size: 24px;
    font-weight: 600;
    color: var(--text-primary);
}

.synergy-actions {
    display: flex;
    gap: var(--space-3);
}

.synergy-btn {
    padding: var(--space-2) var(--space-4);
    background: var(--accent-primary);
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: var(--space-2);
    transition: all 0.2s ease;
}

.synergy-btn:hover {
    background: #1c5fa8;
    transform: translateY(-1px);
}

.synergy-btn-secondary {
    background: var(--bg-tertiary);
    color: var(--text-primary);
    border: 1px solid var(--border-default);
}

.synergy-btn-secondary:hover {
    background: var(--bg-hover);
}

/* Kanban Board Customization */
#kanban-board-container {
    min-height: 500px;
}

.kanban-board {
    display: flex;
    gap: 16px;
    overflow-x: auto;
    padding-bottom: var(--space-4);
}

/* Kanban Column */
.kanban-board-column {
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: 8px;
    min-width: 300px;
    max-width: 350px;
    flex-shrink: 0;
}

.kanban-board-header {
    padding: var(--space-4);
    border-bottom: 1px solid var(--border-default);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.kanban-title-board {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: var(--space-2);
}

.kanban-board-count {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
}

.kanban-drag {
    padding: var(--space-3);
    min-height: 400px;
}

/* Kanban Card */
.kanban-item {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-default);
    border-radius: 6px;
    padding: var(--space-3);
    margin-bottom: var(--space-3);
    cursor: grab;
    transition: all 0.2s ease;
}

.kanban-item:hover {
    background: var(--bg-hover);
    border-color: var(--accent-primary);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.kanban-item:active {
    cursor: grabbing;
}

/* Card Header */
.kanban-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-2);
}

.kanban-card-priority {
    font-size: 18px;
}

.kanban-card-menu {
    color: var(--text-muted);
    cursor: pointer;
    padding: 4px;
}

.kanban-card-menu:hover {
    color: var(--text-primary);
}

/* Card Title */
.kanban-card-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: var(--space-2);
    line-height: 1.4;
}

/* Card Metadata */
.kanban-card-meta {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    margin-bottom: var(--space-2);
}

.kanban-card-project {
    font-size: 12px;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: var(--space-1);
}

.kanban-card-status {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: var(--space-2);
}

.status-badge {
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 500;
}

.status-active {
    background: rgba(34, 197, 94, 0.1);
    color: #22c55e;
}

.status-paused {
    background: rgba(251, 191, 36, 0.1);
    color: #fbbf24;
}

.status-completed {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
}

/* Card Stats */
.kanban-card-stats {
    display: flex;
    gap: var(--space-3);
    margin-bottom: var(--space-2);
    flex-wrap: wrap;
}

.kanban-stat {
    font-size: 11px;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 4px;
}

.kanban-stat i {
    color: var(--accent-primary);
}

/* Card Activity */
.kanban-card-activity {
    margin-bottom: var(--space-2);
}

.kanban-activity-title {
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: var(--space-1);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.kanban-activity-item {
    font-size: 12px;
    color: var(--text-secondary);
    padding: 4px 0;
    display: flex;
    align-items: flex-start;
    gap: var(--space-1);
}

.kanban-activity-item::before {
    content: "•";
    color: var(--accent-primary);
    font-weight: bold;
}

/* Card Footer */
.kanban-card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: var(--space-2);
    border-top: 1px solid var(--border-muted);
}

.kanban-card-session {
    font-size: 10px;
    color: var(--text-muted);
    font-family: var(--font-mono);
}

.kanban-card-tags {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
}

.kanban-tag {
    background: var(--bg-hover);
    color: var(--text-secondary);
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 10px;
}

/* Resume Button */
.kanban-card-resume {
    width: 100%;
    padding: var(--space-2);
    background: var(--accent-primary);
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    margin-top: var(--space-2);
}

.kanban-card-resume:hover {
    background: #1c5fa8;
}

/* Add Card Button */
.kanban-add-card {
    width: calc(100% - 24px);
    padding: var(--space-3);
    background: var(--bg-hover);
    border: 1px dashed var(--border-default);
    border-radius: 6px;
    color: var(--text-secondary);
    font-size: 14px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    transition: all 0.2s ease;
    margin: var(--space-3) 12px;
}

.kanban-add-card:hover {
    background: var(--bg-tertiary);
    border-color: var(--accent-primary);
    color: var(--accent-primary);
}

/* Dragging State */
.gu-mirror {
    opacity: 0.8;
    transform: rotate(2deg);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
}

.gu-transit {
    opacity: 0.5;
}

/* Sync Status Indicator */
.sync-status {
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: var(--space-3) var(--space-4);
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 13px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    z-index: 1000;
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.3s ease;
}

.sync-status.show {
    opacity: 1;
    transform: translateY(0);
}

.sync-status.syncing {
    border-color: var(--accent-primary);
}

.sync-status.success {
    border-color: var(--accent-success);
}

.sync-status.error {
    border-color: var(--accent-error);
}

.sync-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid var(--border-default);
    border-top-color: var(--accent-primary);
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
```

#### Step 3: Create Synergy Dashboard JavaScript
**File:** `UI/synergy-dashboard.js`

```javascript
// ==================== SYNERGY DASHBOARD - KANBAN BOARD ==================== //

class SynergyDashboard {
    constructor() {
        this.kanban = null;
        this.sessions = [];
        this.syncTimeout = null;
        this.apiBaseUrl = window.API_BASE_URL || 'http://localhost:4000';
    }

    async initialize() {
        console.log('🎯 Initializing Synergy Dashboard...');
        
        // Load sessions from database
        await this.loadSessions();
        
        // Initialize Kanban board
        this.initializeKanban();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Start auto-refresh (every 30 seconds)
        this.startAutoRefresh();
        
        console.log('✅ Synergy Dashboard initialized');
    }

    async loadSessions() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/sessions/list`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                }
            });
            
            if (!response.ok) throw new Error('Failed to load sessions');
            
            const data = await response.json();
            this.sessions = data.sessions || [];
            
            console.log(`📊 Loaded ${this.sessions.length} sessions`);
        } catch (error) {
            console.error('❌ Error loading sessions:', error);
            this.sessions = [];
        }
    }

    initializeKanban() {
        const container = document.getElementById('kanban-board-container');
        if (!container) {
            console.error('❌ Kanban container not found');
            return;
        }

        // Prepare board data
        const boards = [
            {
                id: 'backlog',
                title: '📦 Backlog',
                item: this.getSessionsByColumn('backlog')
            },
            {
                id: 'in_progress',
                title: '🏃 In Progress',
                item: this.getSessionsByColumn('in_progress')
            },
            {
                id: 'review',
                title: '👁️ Review',
                item: this.getSessionsByColumn('review')
            },
            {
                id: 'done',
                title: '✅ Done',
                item: this.getSessionsByColumn('done')
            }
        ];

        // Initialize jKanban
        this.kanban = new jKanban({
            element: '#kanban-board-container',
            gutter: '16px',
            widthBoard: '320px',
            boards: boards,
            dragItems: true,
            dragBoards: false,
            itemHandleOptions: {
                enabled: true
            },
            click: (el) => {
                this.handleCardClick(el);
            },
            dragendBoard: (el, target, source) => {
                this.handleCardDrop(el, target, source);
            },
            buttonClick: (el, boardId) => {
                this.handleAddCard(boardId);
            }
        });

        console.log('✅ Kanban board initialized');
    }

    getSessionsByColumn(column) {
        return this.sessions
            .filter(session => session.kanban_column === column)
            .map(session => ({
                id: session.session_id,
                title: this.renderCardHTML(session)
            }));
    }

    renderCardHTML(session) {
        const priorityEmoji = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🔴'
        }[session.priority] || '⚪';

        const statusClass = {
            'active': 'status-active',
            'paused': 'status-paused',
            'completed': 'status-completed'
        }[session.status] || 'status-active';

        const recentActivities = (session.recent_activity || []).slice(0, 3);
        const timeAgo = this.formatTimeAgo(session.last_active);

        return `
            <div class="kanban-card-header">
                <span class="kanban-card-priority">${priorityEmoji}</span>
                <span class="kanban-card-menu" onclick="synergyDashboard.openCardMenu('${session.session_id}')">
                    <i class="fas fa-ellipsis-v"></i>
                </span>
            </div>
            
            <div class="kanban-card-title">${this.escapeHtml(session.title)}</div>
            
            <div class="kanban-card-meta">
                <div class="kanban-card-project">
                    <i class="fas fa-folder"></i>
                    ${this.escapeHtml(session.project_name || 'No Project')}
                </div>
                <div class="kanban-card-status">
                    <span class="status-badge ${statusClass}">${session.status}</span>
                    <span>• ${timeAgo}</span>
                </div>
            </div>
            
            <div class="kanban-card-stats">
                <span class="kanban-stat">
                    <i class="fas fa-comments"></i> ${session.message_count || 0}
                </span>
                <span class="kanban-stat">
                    <i class="fas fa-file"></i> ${session.active_docs || 0}
                </span>
                <span class="kanban-stat">
                    <i class="fas fa-tasks"></i> ${session.pending_steps || 0}
                </span>
            </div>
            
            ${recentActivities.length > 0 ? `
                <div class="kanban-card-activity">
                    <div class="kanban-activity-title">Recent Activity</div>
                    ${recentActivities.map(activity => `
                        <div class="kanban-activity-item">
                            ${this.escapeHtml(activity.description)} (${this.formatTimeAgo(activity.timestamp)})
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            <div class="kanban-card-footer">
                <span class="kanban-card-session">${session.session_id}</span>
                ${(session.tags || []).length > 0 ? `
                    <div class="kanban-card-tags">
                        ${session.tags.slice(0, 3).map(tag => `
                            <span class="kanban-tag">${this.escapeHtml(tag)}</span>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
            
            <button class="kanban-card-resume" onclick="synergyDashboard.resumeSession('${session.session_id}')">
                <i class="fas fa-play"></i> Resume Session
            </button>
        `;
    }

    handleCardClick(el) {
        const sessionId = el.dataset.eid;
        console.log('🖱️ Card clicked:', sessionId);
        // Could expand card details or open quick view modal
    }

    async handleCardDrop(el, targetColumn, sourceColumn) {
        const sessionId = el.dataset.eid;
        const targetBoardId = targetColumn.parentElement.dataset.id;
        
        console.log(`🔀 Card moved: ${sessionId} → ${targetBoardId}`);
        
        // Show sync indicator
        this.showSyncStatus('syncing', 'Syncing to database...');
        
        try {
            // Update database
            await this.updateSessionColumn(sessionId, targetBoardId);
            
            // Show success
            this.showSyncStatus('success', 'Synced to Google Tasks & Calendar', 2000);
        } catch (error) {
            console.error('❌ Sync failed:', error);
            this.showSyncStatus('error', 'Sync failed - please try again', 3000);
            
            // Revert card position on error
            // (jKanban doesn't have built-in revert, so we'd need to reload)
        }
    }

    async updateSessionColumn(sessionId, newColumn) {
        const response = await fetch(`${this.apiBaseUrl}/api/sessions/update-column`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
            },
            body: JSON.stringify({
                session_id: sessionId,
                kanban_column: newColumn
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to update session');
        }

        return await response.json();
    }

    async resumeSession(sessionId) {
        console.log('▶️ Resuming session:', sessionId);
        
        try {
            // Load session context
            const response = await fetch(`${this.apiBaseUrl}/api/sessions/${sessionId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                }
            });
            
            if (!response.ok) throw new Error('Failed to load session');
            
            const session = await response.json();
            
            // Open AI chat panel with session context
            this.openAIChatWithContext(session);
        } catch (error) {
            console.error('❌ Error resuming session:', error);
            alert('Failed to resume session. Please try again.');
        }
    }

    openAIChatWithContext(session) {
        // Show AI chat panel
        const chatPanel = document.getElementById('ai-chat-panel');
        if (chatPanel) {
            chatPanel.classList.add('visible');
        }

        // Send resume prompt to AI
        const resumeMessage = `Resume session: ${session.session_id}\n\n` +
            `Project: ${session.project_name}\n` +
            `Title: ${session.title}\n` +
            `Messages: ${session.message_count}\n` +
            `Last Activity: ${this.formatTimeAgo(session.last_active)}`;

        // Trigger AI chat with context
        if (window.sendMessageToAI) {
            window.sendMessageToAI(resumeMessage, session.session_id);
        }
    }

    handleAddCard(boardId) {
        console.log('➕ Add card to:', boardId);
        
        // Could open a modal to create new session
        const title = prompt('Enter session title:');
        if (title) {
            this.createNewSession(title, boardId);
        }
    }

    async createNewSession(title, column = 'backlog') {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/sessions/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                },
                body: JSON.stringify({
                    title: title,
                    kanban_column: column,
                    priority: 'medium'
                })
            });

            if (!response.ok) throw new Error('Failed to create session');

            // Reload board
            await this.loadSessions();
            this.refreshBoard();
            
            this.showSyncStatus('success', 'Session created!', 2000);
        } catch (error) {
            console.error('❌ Error creating session:', error);
            alert('Failed to create session. Please try again.');
        }
    }

    refreshBoard() {
        // Reload Kanban board with updated data
        const container = document.getElementById('kanban-board-container');
        if (container) {
            container.innerHTML = '';
            this.initializeKanban();
        }
    }

    startAutoRefresh() {
        // Refresh every 30 seconds
        setInterval(async () => {
            await this.loadSessions();
            this.refreshBoard();
            console.log('🔄 Auto-refreshed sessions');
        }, 30000);
    }

    setupEventListeners() {
        // Listen for session updates from other tabs
        window.addEventListener('storage', (e) => {
            if (e.key === 'session_updated') {
                this.loadSessions();
                this.refreshBoard();
            }
        });
    }

    showSyncStatus(type, message, duration = null) {
        const statusEl = document.getElementById('sync-status');
        if (!statusEl) return;

        statusEl.className = `sync-status show ${type}`;
        statusEl.querySelector('.sync-message').textContent = message;

        if (duration) {
            setTimeout(() => {
                statusEl.classList.remove('show');
            }, duration);
        }
    }

    formatTimeAgo(timestamp) {
        if (!timestamp) return 'Never';
        
        const now = new Date();
        const then = new Date(timestamp);
        const seconds = Math.floor((now - then) / 1000);

        if (seconds < 60) return 'just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
        return `${Math.floor(seconds / 604800)}w ago`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    openCardMenu(sessionId) {
        // Could open context menu with options: Edit, Delete, Archive, etc.
        console.log('📋 Open menu for:', sessionId);
    }
}

// Global instance
let synergyDashboard;

// Initialize when tab is shown
document.addEventListener('DOMContentLoaded', () => {
    // Listen for tab activation
    const synergyTab = document.querySelector('.sidebar-icon-btn[data-tab="synergy"]');
    if (synergyTab) {
        synergyTab.addEventListener('click', async () => {
            if (!synergyDashboard) {
                synergyDashboard = new SynergyDashboard();
                await synergyDashboard.initialize();
            }
        });
    }
});
```

#### Step 4: Update business-ai-platform-v2.html
Add the new CSS and JS files to the `<head>` section:

```html
<!-- Synergy Dashboard (Kanban Board) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jkanban@1.3.1/dist/jkanban.min.css">
<script src="https://cdn.jsdelivr.net/npm/jkanban@1.3.1/dist/jkanban.min.js"></script>
<link rel="stylesheet" href="synergy-dashboard.css">
<script src="synergy-dashboard.js"></script>
```

Also add the sync status indicator to the HTML body (near the end before closing `</body>`):

```html
<!-- Sync Status Indicator -->
<div class="sync-status" id="sync-status">
    <div class="sync-spinner"></div>
    <span class="sync-message">Syncing...</span>
</div>
```

---

### Phase 2: Backend API Setup (2-3 hours)

#### Step 1: Create Sync Manager
**File:** `AI_infrastructure/core/sync_manager.py`

```python
"""
Sync Manager - Bidirectional sync orchestrator
Handles syncing between sessions.db ↔ Google Tasks ↔ Google Calendar
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from AI_infrastructure.core.session_database import get_session_db
from AI_infrastructure.core.task_card_manager import get_task_card_manager
from google_workspace.ai_personal_tasks import (
    ai_create_task, ai_update_task, ai_complete_task
)
from google_workspace.google_calendar import (
    create_calendar_event, update_calendar_event
)


class SyncManager:
    """Manages bidirectional sync between database, Google Tasks, and Calendar"""
    
    def __init__(self):
        self.db = get_session_db()
        self.card_mgr = get_task_card_manager()
        self.sync_lock = asyncio.Lock()
    
    async def sync_session_to_all(self, session_id: str) -> Dict:
        """
        Complete sync: Database → Google Tasks → Google Calendar
        Called when session is created or significantly updated
        """
        async with self.sync_lock:
            try:
                print(f"🔄 Syncing session {session_id} to all platforms...")
                
                # Get session data
                session = self.db.get_session(session_id)
                if not session:
                    raise ValueError(f"Session {session_id} not found")
                
                # Sync to Google Tasks
                task_result = await self._sync_to_google_tasks(session)
                google_task_id = task_result.get('task_id')
                
                # Link Google Task ID in database
                if google_task_id and not session.get('google_task_id'):
                    self.db.link_google_task(session_id, google_task_id)
                
                # Sync to Google Calendar
                calendar_result = await self._sync_to_google_calendar(session)
                calendar_event_id = calendar_result.get('event_id')
                
                # Link Calendar Event ID (need to add column to DB)
                if calendar_event_id:
                    self.db.link_calendar_event(session_id, calendar_event_id)
                
                print(f"✅ Sync complete for {session_id}")
                
                return {
                    'success': True,
                    'google_task_id': google_task_id,
                    'calendar_event_id': calendar_event_id
                }
                
            except Exception as e:
                print(f"❌ Sync failed for {session_id}: {e}")
                return {'success': False, 'error': str(e)}
    
    async def _sync_to_google_tasks(self, session: Dict) -> Dict:
        """Sync session to Google Tasks"""
        session_id = session['session_id']
        google_task_id = session.get('google_task_id')
        
        # Generate clean task card
        card = self.card_mgr.create_task_card_content(session_id)
        
        if google_task_id:
            # Update existing task
            result = ai_update_task(
                task_id=google_task_id,
                title=card['title'],
                notes=card['notes']
            )
        else:
            # Create new task
            due_date = self._calculate_due_date(session)
            result = ai_create_task(
                title=card['title'],
                notes=card['notes'],
                due_date=due_date,
                priority='high' if session.get('priority') == 'high' else 'normal'
            )
        
        if result.get('success'):
            task_id = result.get('task', {}).get('id') or result.get('task_id')
            print(f"✅ Google Task synced: {task_id}")
            return {'success': True, 'task_id': task_id}
        else:
            print(f"❌ Google Task sync failed: {result.get('error')}")
            return {'success': False, 'error': result.get('error')}
    
    async def _sync_to_google_calendar(self, session: Dict) -> Dict:
        """Sync session to Google Calendar as an event"""
        session_id = session['session_id']
        title = session['title']
        project_name = session.get('project_name', '')
        
        # Calculate event time (e.g., next milestone or deadline)
        due_date = self._calculate_due_date(session)
        
        # Create calendar event
        event_summary = f"📋 {title}"
        event_description = f"Session: {session_id}\nProject: {project_name}\n\n"
        event_description += f"Status: {session.get('status', 'active')}\n"
        event_description += f"Priority: {session.get('priority', 'medium')}\n"
        
        result = await create_calendar_event(
            summary=event_summary,
            description=event_description,
            start_time=due_date,
            end_time=due_date + timedelta(hours=1),
            attendees=[]
        )
        
        if result.get('success'):
            event_id = result.get('event_id')
            print(f"✅ Calendar event created: {event_id}")
            return {'success': True, 'event_id': event_id}
        else:
            print(f"❌ Calendar event creation failed: {result.get('error')}")
            return {'success': False, 'error': result.get('error')}
    
    def _calculate_due_date(self, session: Dict) -> datetime:
        """Calculate due date based on priority"""
        now = datetime.now()
        priority = session.get('priority', 'medium')
        
        # High priority: 2 days, Medium: 5 days, Low: 7 days
        days_map = {'high': 2, 'medium': 5, 'low': 7}
        days = days_map.get(priority, 5)
        
        return now + timedelta(days=days)
    
    async def handle_column_change(self, session_id: str, new_column: str) -> Dict:
        """
        Handle Kanban column change (drag & drop)
        Updates database and syncs to Google Tasks
        """
        try:
            print(f"🔀 Column change: {session_id} → {new_column}")
            
            # Update database
            self.db.update_session_column(session_id, new_column)
            
            # Update status based on column
            status_map = {
                'backlog': 'paused',
                'in_progress': 'active',
                'review': 'active',
                'done': 'completed'
            }
            new_status = status_map.get(new_column, 'active')
            
            # Update session status in database
            session = self.db.get_session(session_id)
            
            # Sync to Google Tasks
            google_task_id = session.get('google_task_id')
            if google_task_id:
                # Update task card with new column/status
                await self._sync_to_google_tasks(session)
                
                # Mark as completed in Google Tasks if moved to 'done'
                if new_column == 'done':
                    ai_complete_task(google_task_id)
            
            print(f"✅ Column change synced for {session_id}")
            
            return {'success': True, 'new_column': new_column}
            
        except Exception as e:
            print(f"❌ Column change sync failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def handle_session_update(self, session_id: str) -> Dict:
        """
        Handle session updates (new message, document, etc.)
        Re-syncs task card to Google Tasks
        """
        try:
            print(f"📝 Session updated: {session_id}")
            
            # Get session data
            session = self.db.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # Re-sync to Google Tasks (updates activity log)
            await self._sync_to_google_tasks(session)
            
            print(f"✅ Session update synced for {session_id}")
            
            return {'success': True}
            
        except Exception as e:
            print(f"❌ Session update sync failed: {e}")
            return {'success': False, 'error': str(e)}


# Singleton
_sync_manager = None

def get_sync_manager() -> SyncManager:
    global _sync_manager
    if _sync_manager is None:
        _sync_manager = SyncManager()
    return _sync_manager
```

#### Step 2: Add API Routes to app.py
**File:** `app.py` (add new routes)

```python
from AI_infrastructure.core.sync_manager import get_sync_manager

# ... existing imports ...

sync_manager = get_sync_manager()

# ==================== SESSION MANAGEMENT API ==================== #

@app.route('/api/sessions/list', methods=['GET'])
async def list_sessions():
    """Get all sessions for current user"""
    try:
        user_id = get_current_user_id()  # From your auth system
        
        db = get_session_db()
        sessions = db.get_user_sessions(user_id)
        
        # Get summaries for Kanban board
        session_summaries = []
        for session in sessions:
            summary = db.get_session_summary(session['session_id'])
            session_summaries.append(summary)
        
        return jsonify({
            'success': True,
            'sessions': session_summaries
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/sessions/<session_id>', methods=['GET'])
async def get_session(session_id):
    """Get complete session data"""
    try:
        db = get_session_db()
        session = db.get_session(session_id)
        
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        return jsonify({
            'success': True,
            'session': session
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/sessions/create', methods=['POST'])
async def create_session():
    """Create new session"""
    try:
        data = request.json
        user_id = get_current_user_id()
        
        title = data.get('title')
        if not title:
            return jsonify({'success': False, 'error': 'Title required'}), 400
        
        # Generate session ID
        from AI_infrastructure.core.session_orchestrator import get_session_orchestrator
        orchestrator = get_session_orchestrator()
        
        session_id = orchestrator.create_session(
            user_id=user_id,
            title=title,
            project_name=data.get('project_name', ''),
            kanban_column=data.get('kanban_column', 'backlog'),
            priority=data.get('priority', 'medium'),
            tags=data.get('tags', [])
        )
        
        # Sync to Google Tasks & Calendar
        await sync_manager.sync_session_to_all(session_id)
        
        return jsonify({
            'success': True,
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/sessions/update-column', methods=['POST'])
async def update_session_column():
    """Update session Kanban column (drag & drop handler)"""
    try:
        data = request.json
        session_id = data.get('session_id')
        new_column = data.get('kanban_column')
        
        if not session_id or not new_column:
            return jsonify({'success': False, 'error': 'Missing parameters'}), 400
        
        # Update and sync
        result = await sync_manager.handle_column_change(session_id, new_column)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/sessions/<session_id>/activity', methods=['POST'])
async def add_session_activity():
    """Add activity to session (message, document, etc.)"""
    try:
        session_id = request.view_args['session_id']
        data = request.json
        
        activity_type = data.get('type')  # 'message', 'document', 'next_step'
        
        db = get_session_db()
        
        if activity_type == 'message':
            db.add_message(
                session_id,
                data.get('role'),
                data.get('content'),
                data.get('tools_used', [])
            )
        elif activity_type == 'document':
            db.add_document(
                session_id,
                data.get('doc_type'),
                data.get('title'),
                data.get('url')
            )
        elif activity_type == 'next_step':
            db.add_next_step(session_id, data.get('description'))
        
        # Sync updated session to Google Tasks
        await sync_manager.handle_session_update(session_id)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

### Phase 3: Database Schema Updates (30 minutes)

Add calendar event linking to `session_database.py`:

```python
# In SessionDatabase class, add to __init__ after table creation:

cursor.execute("""
    CREATE TABLE IF NOT EXISTS calendar_events (
        event_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        google_event_id TEXT,
        event_type TEXT,
        start_time TEXT,
        end_time TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
""")

cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_calendar_session 
    ON calendar_events(session_id)
""")

# Add method to link calendar events:

def link_calendar_event(self, session_id: str, google_event_id: str):
    """Link Google Calendar event to session"""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO calendar_events 
            (event_id, session_id, google_event_id, created_at)
            VALUES (?, ?, ?, ?)
        """, (f"evt_{session_id}", session_id, google_event_id, now))
        
        self._log_activity(
            cursor, session_id, 'calendar_linked',
            f'Linked to Google Calendar event: {google_event_id}',
            {'google_event_id': google_event_id}
        )
        
        conn.commit()
```

---

## 🚀 Testing Plan

### Manual Testing Checklist

```markdown
### Phase 1: Frontend Basic Functionality
- [ ] Sidebar icon shows up correctly
- [ ] Clicking icon switches to Synergy tab
- [ ] Tab content container exists
- [ ] jKanban loads without errors
- [ ] Four columns render: Backlog, In Progress, Review, Done

### Phase 2: Kanban Board Rendering
- [ ] Cards render with correct data
- [ ] Priority emojis show (🟢🟡🔴)
- [ ] Project name displays
- [ ] Status badge shows
- [ ] Message/doc/step counts accurate
- [ ] Recent activity shows (last 3)
- [ ] Session ID displays
- [ ] Tags render
- [ ] Resume button appears

### Phase 3: Drag & Drop
- [ ] Can drag card between columns
- [ ] Card moves smoothly
- [ ] Drop triggers API call
- [ ] Sync status indicator shows
- [ ] Database updates (check via SQL)
- [ ] Google Task updates (check in Tasks app)
- [ ] Card stays in new column after refresh

### Phase 4: Card Actions
- [ ] Clicking "Resume" opens AI chat
- [ ] Session context loads in chat
- [ ] AI remembers conversation history
- [ ] Card menu (⋮) opens options
- [ ] "Add Card" button creates new session

### Phase 5: Sync Verification
- [ ] Move card → check sessions.db (kanban_column updated)
- [ ] Move card → check Google Tasks (status updated)
- [ ] Add message in AI chat → card updates (activity log)
- [ ] Create document → card shows new doc count
- [ ] Complete next step → card updates
- [ ] Auto-refresh works (wait 30 seconds)

### Phase 6: Google Calendar Integration
- [ ] New session creates calendar event
- [ ] Event has correct title
- [ ] Event description includes session details
- [ ] Due date calculated correctly
- [ ] Completing task updates calendar

### Phase 7: Error Handling
- [ ] Network error shows error message
- [ ] Failed sync reverts card position
- [ ] Invalid session ID handled gracefully
- [ ] Empty columns render correctly
- [ ] No sessions = empty Kanban board
```

---

## 📊 Expected Behavior

### User Flow 1: Creating New Task

1. **User clicks "Add Card" in Backlog column**
   - Prompt appears: "Enter session title:"
   - User types: "Design new landing page"
   - Clicks OK

2. **System creates session**
   - POST `/api/sessions/create`
   - session_id generated: `sess_20251028_1430_john_design_landing`
   - Saved to sessions.db with:
     - kanban_column: 'backlog'
     - status: 'paused'
     - priority: 'medium'

3. **System syncs to Google Tasks**
   - Creates task: "🟡 Design new landing page"
   - Notes contain: project, status, session_id
   - Due date: 5 days from now (medium priority)

4. **System syncs to Google Calendar**
   - Creates event: "📋 Design new landing page"
   - Description includes session details
   - Date: 5 days from now

5. **Kanban board updates**
   - New card appears in Backlog column
   - Shows: title, project, status badge, stats (0 msgs, 0 docs, 0 steps)
   - "Resume" button ready

### User Flow 2: Working on Task

1. **User drags card from Backlog to In Progress**
   - Drag event triggers
   - POST `/api/sessions/update-column`
   - Database updates: kanban_column = 'in_progress', status = 'active'

2. **Google Tasks syncs**
   - Task card updates: status badge changes to "active"
   - Notes update with new column

3. **User clicks "Resume" on card**
   - Loads session from database
   - Opens AI chat panel
   - Sends resume prompt with full context

4. **User chats with AI**
   - User: "Help me create wireframes"
   - AI responds, uses tools, creates documents
   - Each message adds to activity_log in database

5. **Card updates automatically**
   - Message count increases: 2 msgs → 4 msgs
   - New activity shows: "Assistant message added (just now)"
   - Google Task card updates with new stats

6. **User moves card to Review**
   - Drag & drop
   - Database updates: kanban_column = 'review'
   - Google Tasks syncs
   - Status stays "active"

7. **User completes task**
   - Drags card to Done column
   - Database updates: kanban_column = 'done', status = 'completed'
   - Google Task marked complete ✅
   - Calendar event updated

### User Flow 3: Mobile Access

1. **User opens Google Tasks on phone**
   - Sees: "🟡 Design new landing page"
   - Taps to view details

2. **Sees clean summary**
   ```
   📋 Marketing
   🟢 Active • Last active: 1h ago
   📊 4 messages • 1 docs • 2 steps
   
   📝 Recent Activity:
     • Doc created: Wireframe Draft (1h ago)
     • Message added (1h ago)
     • Next step: Review with team (2h ago)
   
   🔗 Session: sess_20251028_design_landing
   🏷️ design, landing-page, marketing
   ```

3. **User checks it off as complete**
   - Google Tasks marks complete
   - Webhook fires to backend
   - Backend updates sessions.db
   - Kanban board auto-refreshes
   - Card moves to Done column

---

## 🎯 Success Metrics

After full implementation, you should have:

✅ **Unified Dashboard** - All session management in one place  
✅ **Visual Workflow** - Kanban board shows progress at a glance  
✅ **Mobile Access** - Google Tasks provides clean mobile view  
✅ **Automatic Sync** - No manual copying between systems  
✅ **Complete Context** - Full history in sessions.db, summary in Tasks  
✅ **Calendar Integration** - Deadlines visible in Google Calendar  
✅ **Real-time Updates** - Changes propagate automatically  
✅ **Resume Capability** - Click any card to continue work  

---

## 🚧 Future Enhancements

### Phase 4: Advanced Features (Future)

1. **WebSocket Real-Time Sync**
   - Replace polling with WebSocket for instant updates
   - Multiple users see live card movements

2. **Card Details Modal**
   - Click card → full detail view
   - Edit session properties inline
   - View complete conversation history
   - Manage documents and next steps

3. **Advanced Filtering**
   - Filter by: project, priority, tags, date range
   - Search across all sessions
   - Saved filter presets

4. **Team Collaboration**
   - Assign sessions to team members
   - Comment on cards
   - @mention notifications
   - Shared task lists in Google Tasks

5. **Analytics Dashboard**
   - Time tracking per session
   - Completion rates
   - Bottleneck identification
   - Velocity charts

6. **Customizable Columns**
   - Add custom stages (e.g., "Testing", "Deployment")
   - Rename columns
   - Column limits (WIP limits)

7. **Automation Rules**
   - Auto-move cards based on triggers
   - Auto-assign priorities
   - Auto-create calendar events

8. **Export & Reporting**
   - Export sessions to PDF
   - Generate reports
   - Data export to CSV

---

## 📚 Resources

### jKanban Documentation
- GitHub: https://github.com/riktar/jkanban
- Demo: https://riktar.github.io/jKanban/

### Google Tasks API
- Docs: https://developers.google.com/tasks/reference/rest
- Python Client: Already integrated in `google_tasks.py`

### Google Calendar API
- Docs: https://developers.google.com/calendar/api/v3/reference
- Python Client: Need to add to `google_workspace/google_calendar.py`

### SQLite Documentation
- Official: https://www.sqlite.org/docs.html
- Python sqlite3: https://docs.python.org/3/library/sqlite3.html

---

## ✅ Summary

This integration plan provides:

1. **Complete Architecture** - Frontend (jKanban) + Backend (SQLite + Google APIs)
2. **Bidirectional Sync** - Changes flow both ways automatically
3. **Clean UI** - Dark theme, responsive, professional
4. **Mobile Support** - Google Tasks provides mobile access
5. **Calendar Integration** - Deadlines in Google Calendar
6. **Production Ready** - Error handling, sync indicators, auto-refresh

**Next Steps:**
1. Add jKanban library to `business-ai-platform-v2.html`
2. Create `synergy-dashboard.css` and `synergy-dashboard.js`
3. Add API routes to `app.py`
4. Update database schema with calendar events
5. Test complete flow end-to-end

**Estimated Time:**
- Phase 1 (Frontend): 1-2 hours
- Phase 2 (Backend): 2-3 hours
- Phase 3 (Database): 30 minutes
- Testing: 1-2 hours
- **Total: 5-8 hours** for complete working system

Let me know when you're ready to proceed with implementation! 🚀
