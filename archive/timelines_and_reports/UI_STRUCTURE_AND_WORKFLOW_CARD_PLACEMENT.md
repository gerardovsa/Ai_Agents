# UI Structure & Workflow Card Placement Guide

## Current UI Architecture

### Header Bar Structure
The platform has a **multi-panel layout** without a traditional top header bar:

```
┌─────────────────────────────────────────────────────────────┐
│ SIDEBAR (Left) │ PRIME PANEL │ AGENT 1 │ AGENT 2 │ AGENT 3 │
│                │   (Center)  │         │         │         │
│  - Dashboard   │             │         │         │         │
│  - Threads     │   AI Chat   │ AI Chat │ AI Chat │ AI Chat │
│  - Synergy     │   Messages  │ Messages│ Messages│ Messages│
│  - Automation  │             │         │         │         │
│  - Tools       │             │         │         │         │
└─────────────────────────────────────────────────────────────┘
```

### Fixed Positioning Elements (Current)

**1. Zoom Controls (Automation Canvas)**
- **Location**: `.zoom-controls` class
- **Position**: Fixed to automation canvas (bottom-right area)
- **Contains**:
  - Zoom Out button
  - Zoom Level display (100%)
  - Zoom In button
  - Reset Zoom button
  - Recenter button
- **CSS**: Custom positioning within canvas wrapper
- **File**: Line ~12809 in `business-ai-platform-v2.html`

**2. Shapes Library (Automation Canvas)**
- **Location**: `.shapes-library` panel
- **Position**: Left side of automation canvas
- **Contains**:
  - Shape selection (rectangle, circle, diamond, hexagon, etc.)
  - Connection tools
  - Color swatches
- **Collapsible**: Can be toggled on/off

**3. Internal Document Popup**
- **Location**: `.internal-doc-popup` class
- **Position**: `position: fixed` with draggable functionality
- **Style**: Line ~11139
- **Features**:
  - Draggable header
  - Resizable
  - Collapsible
  - Maximizable
  - Z-index: 9000

**4. Notification Container**
- **Position**: Fixed top-right
- **Z-index**: High priority for visibility

---

## Proposed Workflow Card Placement

### Option 1: Fixed Top-Right Corner (RECOMMENDED)

**Similar to Zoom Controls Pattern:**

```css
.workflow-status-card {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 320px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 8000; /* Below modals (9000+), above canvas */
    padding: 16px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.workflow-status-card.collapsed {
    height: 56px;
    overflow: hidden;
}

.workflow-status-card:hover {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
}
```

**HTML Structure:**
```html
<div class="workflow-status-card" id="workflow-status-card">
    <!-- Header (Always Visible) -->
    <div class="workflow-card-header">
        <div class="workflow-card-title">
            <i class="fas fa-robot"></i>
            <span>Active Workflow</span>
        </div>
        <div class="workflow-card-actions">
            <button class="workflow-card-btn" title="Collapse">
                <i class="fas fa-chevron-down"></i>
            </button>
            <button class="workflow-card-btn" title="Close">
                <i class="fas fa-times"></i>
            </button>
        </div>
    </div>
    
    <!-- Body (Collapsible) -->
    <div class="workflow-card-body">
        <!-- Workflow slug pill -->
        <div class="workflow-slug-pill">
            <i class="fas fa-hashtag"></i>
            <span>wf_k7m3p9x2_1732125847</span>
            <button class="copy-slug-btn">
                <i class="fas fa-copy"></i>
            </button>
        </div>
        
        <!-- Workflow metadata -->
        <div class="workflow-metadata">
            <div class="workflow-meta-item">
                <i class="fas fa-clock"></i>
                <span>Trigger: Schedule (Daily 9am)</span>
            </div>
            <div class="workflow-meta-item">
                <i class="fas fa-check-circle"></i>
                <span>Status: Active</span>
            </div>
            <div class="workflow-meta-item">
                <i class="fas fa-play-circle"></i>
                <span>Last Run: 2 hours ago</span>
            </div>
        </div>
        
        <!-- Quick Actions -->
        <div class="workflow-quick-actions">
            <button class="workflow-action-btn primary">
                <i class="fas fa-play"></i>
                Execute Now
            </button>
            <button class="workflow-action-btn">
                <i class="fas fa-edit"></i>
                Edit
            </button>
            <button class="workflow-action-btn">
                <i class="fas fa-pause"></i>
                Pause
            </button>
        </div>
        
        <!-- Recent Executions -->
        <div class="workflow-executions">
            <div class="execution-header">Recent Executions</div>
            <div class="execution-item success">
                <i class="fas fa-check-circle"></i>
                <span>Success</span>
                <span class="execution-time">10:23 AM</span>
            </div>
            <div class="execution-item success">
                <i class="fas fa-check-circle"></i>
                <span>Success</span>
                <span class="execution-time">09:05 AM</span>
            </div>
            <div class="execution-item error">
                <i class="fas fa-exclamation-circle"></i>
                <span>Failed</span>
                <span class="execution-time">Yesterday</span>
            </div>
        </div>
    </div>
</div>
```

---

### Option 2: Sidebar Integration

Add workflow card to the existing sidebar navigation:

```
┌───────────────────┐
│ SIDEBAR           │
│                   │
│ 🏠 Dashboard      │
│ 💬 Threads        │
│ 🔄 Synergy        │
│ 🤖 Automation     │
│                   │
│ ┌───────────────┐ │
│ │ WORKFLOW CARD │ │  ← Fixed position within sidebar
│ │               │ │
│ │ wf_k7m3p9x2   │ │
│ │ Active        │ │
│ │ [Actions]     │ │
│ └───────────────┘ │
│                   │
│ ⚙️  Settings      │
└───────────────────┘
```

---

## Workflow Card Content (Recommended)

### 1. **Header Section**
- **Workflow Icon** (robot emoji 🤖)
- **Title** (user-defined or "Active Workflow")
- **Collapse/Expand button**
- **Close button**

### 2. **Slug Display**
- **Unique identifier pill**: `wf_k7m3p9x2_1732125847`
- **Copy button**: Click to copy slug
- **Drag handle**: Drag slug into chat to load workflow
- **Visual**: Orange/blue pill with monospace font

### 3. **Status Indicators**
- **Current Status**: Active/Paused/Draft/Archived
  - Green (🟢) = Active
  - Yellow (🟡) = Paused
  - Gray (⚫) = Draft
  - Red (🔴) = Error
- **Trigger Type**: Manual/Schedule/Webhook/Event
- **Next Scheduled Run**: For scheduled workflows

### 4. **Metadata Display**
- **Created**: Date created
- **Last Modified**: Last edit timestamp
- **Category**: Email/Data/Notifications/etc.
- **Total Actions**: Number of steps (e.g., "5 actions")

### 5. **Quick Actions**
- **Execute Now** (▶️ button) - Run manually
- **Edit** (✏️ button) - Open in canvas
- **Pause/Resume** (⏸️/▶️ button) - Toggle active status
- **Schedule** (🕐 button) - Modify schedule
- **Delete** (🗑️ button) - Remove workflow

### 6. **Execution History**
- **Recent runs** (last 3-5):
  - Success ✅ with timestamp
  - Failure ❌ with error message
  - Running 🔄 with progress
- **Execution count**: "Executed 47 times"
- **Success rate**: "98% success rate"

### 7. **Visual Flow Preview** (Optional)
- **Mini canvas** showing workflow diagram
- **Thumbnail** of shapes and connections
- Click to expand full view

---

## Integration Points

### JavaScript Hook Points
```javascript
// Show workflow card when workflow is active
window.showWorkflowCard = function(workflowData) {
    const card = document.getElementById('workflow-status-card');
    card.classList.add('active');
    // Populate with workflow data
    updateWorkflowCard(workflowData);
};

// Hide workflow card
window.hideWorkflowCard = function() {
    const card = document.getElementById('workflow-status-card');
    card.classList.remove('active');
};

// Update card with execution status
window.updateWorkflowExecution = function(executionData) {
    const executionsList = document.querySelector('.workflow-executions');
    // Add new execution item
    addExecutionItem(executionData);
};
```

### API Endpoints to Connect
- `GET /api/automation/get?automation_id={slug}` - Fetch workflow details
- `POST /api/automation/execute` - Execute workflow manually
- `GET /api/automation/execution_history?automation_id={slug}` - Get execution log
- `POST /api/automation/schedule` - Update schedule
- `POST /api/automation/deactivate` - Pause workflow

---

## Z-Index Hierarchy

```
10000+ - Critical modals (markdown editor, workflow modal)
 9000  - Floating popups (internal docs)
 8000  - Workflow status card (PROPOSED)
 5000  - Context menus
 1000  - Sidebar/navigation
  500  - Canvas elements
  100  - Background elements
```

---

## CSS Class Naming Convention

Follow existing patterns:
- `.workflow-status-card` - Main container
- `.workflow-card-header` - Header section
- `.workflow-card-body` - Collapsible content
- `.workflow-slug-pill` - Slug display
- `.workflow-meta-item` - Metadata rows
- `.workflow-action-btn` - Action buttons
- `.execution-item` - Execution history rows

---

## Responsive Behavior

**Desktop (1920x1080):**
- Fixed top-right, 320px wide
- Full functionality visible

**Tablet (1024x768):**
- Fixed top-right, 280px wide
- Collapsed by default

**Mobile (<768px):**
- Slide-in drawer from right
- Full-width when open
- Hidden by default

---

## Animation & Transitions

```css
/* Slide in from right */
@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(100%);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.workflow-status-card.active {
    animation: slideInRight 0.3s ease-out;
}

/* Collapse animation */
.workflow-status-card.collapsing {
    transition: height 0.3s ease;
}
```

---

## Implementation Priority

1. ✅ **Create CSS classes** (workflow-status-card, etc.)
2. ✅ **Build HTML structure** (header, body, sections)
3. ✅ **Add JavaScript handlers** (show, hide, update)
4. ✅ **Connect to API** (fetch workflow data)
5. ✅ **Test with real workflows** (use existing slugs)
6. ✅ **Add drag-and-drop** (slug pill to chat)

---

## Example Visual Layout

```
┌─────────────────────────────────────────────────────────────┐
│                                           ┌───────────────┐  │
│ PRIME PANEL                               │ 🤖 WORKFLOW   │  │
│                                           │ wf_k7m3p9x2   │  │
│   User: "Create email workflow"          │               │  │
│                                           │ ⏰ 9:00 AM    │  │
│   AI: "Created Daily Email Summary       │ 🟢 Active     │  │
│        with slug wf_k7m3p9x2"            │               │  │
│                                           │ ▶️ Execute    │  │
│   [Workflow slug pill appears in chat]   │ ✏️ Edit       │  │
│                                           │ ⏸️ Pause      │  │
│                                           │               │  │
│                                           │ EXECUTIONS:   │  │
│                                           │ ✅ 10:23 AM   │  │
│                                           │ ✅ 09:05 AM   │  │
│                                           └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

**RECOMMENDATION**: Use **Option 1 (Fixed Top-Right)** for maximum visibility and accessibility while maintaining the existing UI paradigm. The card should appear when:
1. User creates a workflow
2. User links a workflow to a thread
3. Workflow is actively executing
4. User drags a workflow slug into chat
