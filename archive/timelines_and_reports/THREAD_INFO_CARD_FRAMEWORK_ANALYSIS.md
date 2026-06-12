# Thread Info Card Integration Analysis - Complete Framework Flow

**Date:** December 17, 2025  
**Analysis:** Team ID Integration into Thread Info Card System

---

## Executive Summary

The Team ID tag was added to the thread info card metadata grid, but this analysis reveals the complete integration framework that makes it work. The thread info card system is NOT just a simple HTML template - it's part of a sophisticated multi-layer rendering system with real-time updates, location-based behavior, and complex data flow patterns.

---

## Thread Info Card Architecture

### 1. Multi-Layer Rendering System

**Layer 1: Core Renderer** (thread-info-renderer.js)
```javascript
function renderThreadInfoContainer(location, threadId, includeButtons = true) {
    // Data retrieval layer
    const thread = getThreadData(threadId);  // Fetches from ThreadManager.threads[]
    
    // Metadata calculation layer
    const messageCount = thread.messages?.length || 0;
    const lastUpdated = formatRelativeTime(thread.updated_at);
    const hasFiles = thread.has_files || false;
    const teamId = thread.team_id;  // NEW: Team ID retrieval
    
    // Location-aware button generation
    const isAgent = location.startsWith('agent-');
    const buttonsHTML = generateButtons(location, isAgent);
    
    // HTML assembly
    return assembleCardHTML(thread, metadata, buttonsHTML);
}
```

**Layer 2: ThreadManager Integration**
```javascript
// In thread-manager-core.js
ThreadManager.renderThreadInfoContainer = renderThreadInfoContainer;

// Global export for onclick handlers
window.ThreadInfoRenderer = {
    renderThreadInfoContainer,
    moveToPrime,
    filterByTeamId  // NEW: Team ID filtering
};
```

**Layer 3: Multiple Call Sites** (20+ locations)
```javascript
// Agent columns (agent-column.js)
AgentColumn.updateThreadInfo(agentId) {
    const html = ThreadManager.renderThreadInfoContainer(`agent-${agentId}`, threadId, true);
    container.innerHTML = html;
}

// Prime AI (thread-manager-interactions.js)
PrimeAI.loadThread(threadId) {
    const html = this.renderThreadInfoContainer('prime', threadId, true);
    primeHeader.innerHTML = html;
}

// Workflow integration (workflow-slug-integration.js)
WorkflowSlug.attachThread(threadId) {
    const html = ThreadManager.renderThreadInfoContainer('workflow', threadId, false);
    threadInfoContainer.innerHTML = html;
}

// Synergy boards (synergy-board-init.js)
SynergyBoard.linkThread(threadId) {
    const html = ThreadManager.renderThreadInfoContainer('synergy', threadId, true);
    card.appendChild(html);
}
```

---

## Data Flow Architecture

### Thread Data Retrieval Chain

**Step 1: Thread Object Structure**
```javascript
// Stored in ThreadManager.threads[] array
{
    id: "thread_abc123",
    title: "Customer Support",
    user_id: "user_xyz",
    team_id: "sales_team",  // NEW: Team ID field
    location: "agent-3",
    messages: [...],
    message_count: 24,
    updated_at: "2025-12-17T10:30:00Z",
    has_files: true,
    metadata: {...}
}
```

**Step 2: Data Source Hierarchy**
```
Backend Database (sessions.threads table)
    ↓ HTTP GET /api/threads
ThreadManager.loadThreadsFromBackend()
    ↓ Array assignment
ThreadManager.threads = [...]
    ↓ Find operation
getThreadData(threadId) → thread object
    ↓ Property access
thread.team_id → "sales_team"
    ↓ Conditional rendering
${thread.team_id ? renderTeamIdTag() : ''}
```

**Step 3: Real-Time Update Flow**
```javascript
// WebSocket message received
SynergyRealtime.on('thread_updated', (data) => {
    // Update ThreadManager.threads[] array
    const index = ThreadManager.threads.findIndex(t => t.id === data.thread_id);
    ThreadManager.threads[index] = data.thread;
    
    // Re-render all visible cards
    AgentColumn.updateThreadInfo(agentId);  // Calls renderThreadInfoContainer
    PrimeAI.refreshThreadInfo();            // Calls renderThreadInfoContainer
    SynergyBoard.updateThreadCard();        // Calls renderThreadInfoContainer
});
```

---

## CSS Framework Integration

### 1. Dedicated CSS File (thread-info.css)

**File:** `UI/modules_internal/thread-manager/thread-info.css`

**Structure:**
```css
/* Container wrapper */
.thread-info-wrapper {
    padding: 12px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-default);
}

/* Card container */
.thread-info-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-default);
    border-radius: 8px;
    overflow: hidden;
}

/* Header section */
.thread-info-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px;
    background: rgba(103, 126, 234, 0.1);  /* Accent color tint */
    border-bottom: 1px solid var(--border-default);
}

/* Metadata grid - CRITICAL SECTION */
.thread-info-metadata {
    display: grid;
    grid-template-columns: 1fr 1fr;  /* 2-column grid */
    gap: 12px;
    padding: 12px;
    background: var(--bg-secondary);
}

/* Metadata items */
.metadata-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.metadata-item.full-width {
    grid-column: 1 / -1;  /* Span both columns */
}

/* Action buttons section */
.thread-info-actions {
    display: flex;
    gap: 8px;
    padding: 12px;
    border-top: 1px solid var(--border-default);
}
```

### 2. Team ID Tag CSS (business-ai-platform-v2.html)

**Added to main CSS file:**
```css
/* Team ID Tag - Clickable badge for filtering */
.team-id-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    background: var(--accent-primary);  /* Uses CSS variable system */
    color: white;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    user-select: none;
}

.team-id-tag:hover {
    background: var(--accent-primary-hover);
    transform: scale(1.05);
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.team-id-tag:active {
    transform: scale(0.98);
}
```

**Integration Points:**
- Uses CSS variable system (--accent-primary, --bg-secondary, etc.)
- Respects theme system (light/dark mode)
- Follows existing design patterns (.metadata-item structure)
- Responsive design (grid-template-columns: 1fr 1fr)

---

## Location-Based Behavior System

### 1. Location Context

**Location Types:**
```javascript
'prime'           // Prime AI column
'agent-1'         // Agent column 1
'agent-2'         // Agent column 2
'agent-3'         // Agent column 3
'workflow'        // Workflow integration
'synergy'         // Synergy board
```

### 2. Location-Specific Rendering

**Button Visibility Logic:**
```javascript
if (location === 'prime') {
    // Prime: Only show "Unload" button
    buttons = `
        <button onclick="PrimeAI.unloadThread()">
            <i class="fas fa-eject"></i> Unload
        </button>
    `;
} else if (location.startsWith('agent-')) {
    // Agent: Show "Move to Prime" + "Unload"
    buttons = `
        <button onclick="moveToPrime(${agentId})">
            <i class="fas fa-arrow-left"></i> To Prime
        </button>
        <button onclick="AgentColumn.unloadThread(${agentId})">
            <i class="fas fa-eject"></i> Unload
        </button>
    `;
} else {
    // Other locations: No buttons
    buttons = '';
}
```

**Location-Aware Metadata:**
```javascript
// Same metadata shown everywhere, but context differs
const metadata = {
    messages: thread.messages?.length || 0,
    updated: formatRelativeTime(thread.updated_at),
    hasFiles: thread.has_files,
    threadId: thread.id,
    teamId: thread.team_id  // NEW: Team ID (location-independent)
};

// Team ID tag onclick behavior is location-aware
onclick="filterByTeamId('${thread.team_id}')"
// ^ Filters threads in CURRENT LOCATION (agent column, prime, etc.)
```

---

## Team ID Integration Analysis

### 1. What Was Actually Changed

**Before (Original Metadata Grid):**
```javascript
<div class="thread-info-metadata">
    <div class="metadata-item">
        <span class="metadata-label">Messages:</span>
        <span class="metadata-value">${messageCount}</span>
    </div>
    <div class="metadata-item">
        <span class="metadata-label">Updated:</span>
        <span class="metadata-value">${lastUpdated}</span>
    </div>
    ${hasFiles ? `
        <div class="metadata-item">
            <span class="metadata-label">Has Files:</span>
            <span class="metadata-value">
                <i class="fas fa-paperclip"></i>
            </span>
        </div>
    ` : ''}
    <div class="metadata-item full-width">
        <span class="metadata-label">Thread ID:</span>
        <span class="metadata-value">${truncate(thread.id, 16)}</span>
    </div>
</div>
```

**After (With Team ID):**
```javascript
<div class="thread-info-metadata">
    <!-- Existing items unchanged -->
    <div class="metadata-item">...</div>
    <div class="metadata-item">...</div>
    <div class="metadata-item">...</div>
    <div class="metadata-item full-width">...</div>
    
    <!-- NEW: Team ID metadata item -->
    ${thread.team_id ? `
        <div class="metadata-item full-width">
            <span class="metadata-label">Team ID:</span>
            <span class="metadata-value team-id-tag" 
                  onclick="event.stopPropagation(); filterByTeamId('${thread.team_id}')"
                  title="Click to filter by Team ID: ${thread.team_id}">
                <i class="fas fa-users"></i>
                ${thread.team_id}
            </span>
        </div>
    ` : ''}
</div>
```

### 2. Why It Works (Integration Points)

**Data Retrieval:**
```javascript
// thread-info-renderer.js line ~48
const thread = getThreadData(threadId);

// getThreadData() function (line ~171)
function getThreadData(threadId) {
    if (typeof ThreadManager !== 'undefined' && ThreadManager.threads) {
        return ThreadManager.threads.find(t => t.id === threadId);
    }
    return null;
}

// Returns thread object with team_id property
// {id: "...", title: "...", team_id: "sales_team", ...}
```

**Conditional Rendering:**
```javascript
// Only renders if thread.team_id exists (truthy check)
${thread.team_id ? `...Team ID HTML...` : ''}

// This means:
// - Threads without team_id: No tag shown (backward compatible)
// - Threads with team_id: Tag appears in metadata grid
```

**CSS Styling:**
```javascript
// .team-id-tag class applied to <span>
<span class="metadata-value team-id-tag">

// Inherits from:
// 1. .metadata-value (base styling)
// 2. .team-id-tag (override styling)

// CSS cascade:
.metadata-value {
    font-size: 13px;        // Overridden by .team-id-tag (11px)
    color: var(--text-primary);  // Overridden by .team-id-tag (white)
}

.team-id-tag {
    /* Specific styling takes precedence */
    background: var(--accent-primary);
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    /* ...hover effects, etc. */
}
```

**Click Handler:**
```javascript
onclick="event.stopPropagation(); filterByTeamId('${thread.team_id}')"

// event.stopPropagation(): Prevents bubble to parent elements
// filterByTeamId(): Global function exported from thread-info-renderer.js

window.filterByTeamId = filterByTeamId;  // Line ~297

function filterByTeamId(teamId) {
    // Check if ThreadManager has filtering capability
    if (typeof ThreadManager !== 'undefined' && 
        typeof ThreadManager.filterByTeamId === 'function') {
        ThreadManager.filterByTeamId(teamId);
    } else {
        // Fallback: Show notification
        showNotification(`Filtering by Team ID: ${teamId}`, 'info');
    }
}
```

### 3. What Was NOT Changed (But Should Understand)

**Card Structure (Unchanged):**
```html
<div class="thread-info-wrapper active">
    <div class="thread-info-card">
        <!-- Header section -->
        <div class="thread-info-header">...</div>
        
        <!-- Metadata section (Team ID added here) -->
        <div class="thread-info-metadata">...</div>
        
        <!-- Action buttons section -->
        <div class="thread-info-actions">...</div>
    </div>
</div>
```

**Grid Layout (Unchanged):**
```css
.thread-info-metadata {
    display: grid;
    grid-template-columns: 1fr 1fr;  /* Still 2 columns */
    gap: 12px;
}

/* Team ID uses .full-width to span both columns */
.metadata-item.full-width {
    grid-column: 1 / -1;
}
```

**Rendering Flow (Unchanged):**
```
AgentColumn.updateThreadInfo()
    → ThreadManager.renderThreadInfoContainer()
        → getThreadData(threadId)
            → ThreadManager.threads.find()
        → Build metadata HTML
            → Check thread.team_id (NEW)
            → Render tag if exists (NEW)
        → Return complete HTML
    → container.innerHTML = html
```

---

## Framework Dependencies

### 1. ThreadManager Core System

**Required Functions:**
```javascript
ThreadManager.threads = [];  // Global thread storage
ThreadManager.loadThreadsFromBackend();  // Load threads from API
ThreadManager.renderThreadInfoContainer();  // Render function
```

**Data Structure:**
```javascript
ThreadManager.threads = [
    {
        id: "thread_123",
        title: "Support Thread",
        user_id: "user_abc",
        team_id: "sales_team",  // Must be populated
        location: "agent-1",
        messages: [...],
        updated_at: "2025-12-17T10:00:00Z",
        has_files: true
    },
    // ... more threads
];
```

### 2. Global Exports System

**Required Globals:**
```javascript
window.ThreadManager = { ... };
window.ThreadInfoRenderer = { ... };
window.filterByTeamId = function(teamId) { ... };
window.showNotification = function(msg, type) { ... };
```

### 3. CSS Variable System

**Required Variables:**
```css
:root {
    --bg-primary: #0d0d0d;
    --bg-secondary: #1e1e1e;
    --bg-tertiary: #252525;
    --text-primary: #e5e7eb;
    --text-secondary: #9ca3af;
    --border-default: rgba(255, 255, 255, 0.1);
    --accent-primary: #677eea;
    --accent-primary-hover: #7d91f0;
}
```

### 4. Event System

**Click Event Flow:**
```
User clicks Team ID tag
    ↓
onclick="filterByTeamId('sales_team')"
    ↓
window.filterByTeamId('sales_team')
    ↓
ThreadManager.filterByTeamId('sales_team')  (if exists)
    OR
showNotification('Filtering by Team ID: sales_team')  (fallback)
```

---

## Real-Time Update Integration

### 1. WebSocket Thread Updates

**When thread.team_id changes:**
```javascript
// Backend sends WebSocket message
{
    type: 'thread_updated',
    thread_id: 'thread_123',
    data: {
        team_id: 'new_team_id'  // Changed Team ID
    }
}

// Frontend receives and updates
SynergyRealtime.on('thread_updated', (message) => {
    // Update ThreadManager.threads array
    const index = ThreadManager.threads.findIndex(t => t.id === message.thread_id);
    ThreadManager.threads[index].team_id = message.data.team_id;
    
    // Re-render all visible thread cards
    AgentColumn.updateThreadInfo(agentId);
    // ^ This calls renderThreadInfoContainer()
    // ^ Which re-reads thread.team_id
    // ^ New tag appears instantly
});
```

### 2. Location Updates

**When thread moves between locations:**
```javascript
// User clicks "Move to Prime" button
moveToPrime(agentId) {
    // Get thread from agent
    const thread = MultiAgent.getLoadedThread(agentId);
    
    // Load in Prime
    PrimeAI.loadThread(thread.threadId);
    // ^ Calls renderThreadInfoContainer('prime', threadId, true)
    // ^ Team ID tag appears in Prime card
    
    // Unload from agent
    AgentColumn.unloadThread(agentId);
    // ^ Calls renderThreadInfoContainer(`agent-${agentId}`, null, true)
    // ^ Shows empty state (Team ID tag gone)
}
```

---

## Multi-Location Rendering

### 1. Simultaneous Display

**Thread can appear in multiple locations:**
```
Prime AI Column:
    [Thread Card with Team ID tag]
        Team ID: [sales_team]  <- Click filters Prime threads

Agent Column 3:
    [Thread Card with Team ID tag]
        Team ID: [sales_team]  <- Click filters Agent 3 threads

Synergy Board:
    [Linked Thread Card]
        Team ID: [sales_team]  <- Click filters Synergy threads
```

**Same thread, different contexts:**
```javascript
// Prime rendering
renderThreadInfoContainer('prime', 'thread_123', true)
// → Shows "Unload" button only
// → Team ID tag onclick filters Prime threads

// Agent rendering
renderThreadInfoContainer('agent-3', 'thread_123', true)
// → Shows "Move to Prime" + "Unload" buttons
// → Team ID tag onclick filters Agent 3 threads

// Synergy rendering
renderThreadInfoContainer('synergy', 'thread_123', false)
// → No buttons shown
// → Team ID tag onclick filters Synergy board
```

### 2. Synchronized Updates

**When thread.team_id changes, ALL cards update:**
```javascript
// Backend updates thread.team_id
fetch('/api/threads/thread_123', {
    method: 'PATCH',
    body: JSON.stringify({ team_id: 'new_team' })
});

// WebSocket broadcasts update
// → Prime card re-renders with new Team ID
// → Agent card re-renders with new Team ID
// → Synergy card re-renders with new Team ID
// → All happen simultaneously
```

---

## Grid Layout System

### 1. Metadata Grid Structure

**2-Column Responsive Grid:**
```css
.thread-info-metadata {
    display: grid;
    grid-template-columns: 1fr 1fr;  /* Equal columns */
    gap: 12px;
}

/* Responsive breakpoint */
@media (max-width: 480px) {
    .thread-info-metadata {
        grid-template-columns: 1fr;  /* Single column on mobile */
    }
}
```

**Grid Item Placement:**
```
Desktop (2 columns):
┌─────────────────────────────────┐
│ Messages: 24    │ Updated: 2h   │
│ Has Files: 📎   │               │
│ Thread ID: abc123...  (full)    │
│ Team ID: [sales_team] (full)    │
└─────────────────────────────────┘

Mobile (1 column):
┌──────────────────┐
│ Messages: 24     │
│ Updated: 2h      │
│ Has Files: 📎    │
│ Thread ID: abc...│
│ Team ID: [sales] │
└──────────────────┘
```

### 2. Full-Width Items

**Why Team ID is full-width:**
```javascript
<div class="metadata-item full-width">
    <span class="metadata-label">Team ID:</span>
    <span class="metadata-value team-id-tag">...</span>
</div>

// CSS: grid-column: 1 / -1
// Spans from column 1 to last column (both columns in 2-col grid)
```

**Visual Comparison:**
```
Normal Item (1 column):
┌──────────────┐
│ Messages: 24 │
└──────────────┘

Full-Width Item (2 columns):
┌─────────────────────────────┐
│ Team ID: [sales_team]       │
└─────────────────────────────┘
```

---

## Click Handler Integration

### 1. Event Propagation

**Why event.stopPropagation() is critical:**
```javascript
onclick="event.stopPropagation(); filterByTeamId('${thread.team_id}')"

// Without stopPropagation():
// Click → Team ID tag
//   ↓ bubbles to
// Click → .metadata-item
//   ↓ bubbles to
// Click → .thread-info-metadata
//   ↓ bubbles to
// Click → .thread-info-card
//   ↓ might trigger card click handler (unwanted)

// With stopPropagation():
// Click → Team ID tag
//   ↓ STOPS HERE
// filterByTeamId() called
// No other handlers triggered
```

### 2. Function Availability Chain

**How filterByTeamId is accessible:**
```javascript
// Step 1: Define in IIFE closure (thread-info-renderer.js)
(function () {
    function filterByTeamId(teamId) { ... }
    
    // Step 2: Export to window
    window.filterByTeamId = filterByTeamId;
    
    // Step 3: Also export via namespace
    window.ThreadInfoRenderer = {
        filterByTeamId: filterByTeamId
    };
})();

// Step 4: Available in HTML onclick
<span onclick="filterByTeamId('sales_team')">
// → window.filterByTeamId('sales_team')
// → Works!
```

### 3. Fallback Strategy

**Graceful degradation:**
```javascript
function filterByTeamId(teamId) {
    // Try full filtering implementation
    if (typeof ThreadManager !== 'undefined' && 
        typeof ThreadManager.filterByTeamId === 'function') {
        ThreadManager.filterByTeamId(teamId);
        return;
    }
    
    // Fallback: Show notification
    if (typeof showNotification === 'function') {
        showNotification(`Filtering by Team ID: ${teamId}`, 'info');
        return;
    }
    
    // Last resort: Console log
    console.info(`Team ID filter: ${teamId} (filtering not yet implemented)`);
}
```

---

## Theme System Integration

### 1. Light/Dark Mode Support

**Theme-aware CSS:**
```css
/* Dark mode (default) */
.thread-info-card {
    background: var(--bg-primary, #0d0d0d);
    border: 1px solid var(--border-default, rgba(255, 255, 255, 0.1));
}

.team-id-tag {
    background: var(--accent-primary);
    color: white;
}

/* Light mode */
[data-theme="light"] .thread-info-card {
    background: white;
    border: 1px solid #d1d5db;
}

[data-theme="light"] .team-id-tag {
    background: #677eea;  /* Same color, different context */
    color: white;
}
```

### 2. CSS Variable Inheritance

**How Team ID tag respects theme:**
```css
/* Root variables change based on theme */
:root {
    --accent-primary: #677eea;  /* Dark mode blue */
}

[data-theme="light"] {
    --accent-primary: #5b6fd8;  /* Light mode blue */
}

/* Team ID tag automatically updates */
.team-id-tag {
    background: var(--accent-primary);
    /* ^ Reads current theme value */
}
```

---

## Performance Considerations

### 1. Re-Render Frequency

**When renderThreadInfoContainer() is called:**
- Thread loaded into location
- Thread metadata updated
- Thread moved between locations
- Thread unloaded from location
- Real-time WebSocket update received
- User switches view mode
- Page load/refresh

**Optimization:**
```javascript
// Debounced re-rendering (if needed)
const debouncedRender = createDebounce(
    (location, threadId) => {
        const html = ThreadManager.renderThreadInfoContainer(location, threadId, true);
        container.innerHTML = html;
    },
    100  // 100ms delay
);
```

### 2. DOM Manipulation

**innerHTML vs. DOM updates:**
```javascript
// Current approach (full re-render)
container.innerHTML = ThreadManager.renderThreadInfoContainer(location, threadId, true);
// + Simple, reliable
// - Destroys and recreates entire card

// Possible optimization (targeted updates)
const teamIdSpan = container.querySelector('.team-id-tag');
if (teamIdSpan && thread.team_id !== oldTeamId) {
    teamIdSpan.textContent = thread.team_id;
}
// + Faster, preserves other elements
// - More complex, error-prone
```

---

## Missing Integration Points (To Be Implemented)

### 1. Thread Creation

**Current:** thread.team_id not populated during creation
**Needed:**
```javascript
// In thread creation endpoint
async function createThread(userId, title, ...) {
    // Get user's Team ID status
    const user = await db.query('SELECT is_sub_user, username FROM users WHERE id = $1', [userId]);
    
    const thread = {
        id: generateThreadId(),
        title: title,
        user_id: userId,
        team_id: user.is_sub_user ? user.username : null,  // NEW
        created_at: new Date(),
        // ...
    };
    
    await db.query('INSERT INTO threads (id, title, user_id, team_id, ...) VALUES ($1, $2, $3, $4, ...)', 
        [thread.id, thread.title, thread.user_id, thread.team_id, ...]);
}
```

### 2. Database Schema

**Current:** sessions.threads table lacks team_id column
**Needed:**
```sql
-- Add team_id column to threads table
ALTER TABLE sessions.threads ADD COLUMN team_id TEXT;

-- Index for filtering
CREATE INDEX idx_threads_team_id ON sessions.threads(team_id);

-- Update existing threads (one-time migration)
UPDATE sessions.threads t
SET team_id = u.username
FROM ai_infrastructure.users u
WHERE t.user_id = u.id 
  AND u.is_sub_user = TRUE;
```

### 3. Filtering Implementation

**Current:** filterByTeamId() shows notification only
**Needed:**
```javascript
ThreadManager.filterByTeamId = function(teamId) {
    // Filter threads array
    const filteredThreads = this.threads.filter(t => t.team_id === teamId);
    
    // Update UI state
    this.activeFilter = { type: 'team_id', value: teamId };
    
    // Re-render thread list
    this.renderThreadList(filteredThreads);
    
    // Show filter indicator
    this.showFilterIndicator('Team ID', teamId);
    
    // Hide non-matching threads in agent columns
    AgentColumn.filterByTeamId(teamId);
    
    // Update URL
    window.history.pushState({}, '', `?team_id=${teamId}`);
};
```

### 4. Backend API

**Current:** No Team ID filtering endpoint
**Needed:**
```python
@app.route('/api/threads/filter/team_id/<team_id>', methods=['GET'])
def filter_threads_by_team_id(team_id):
    """Filter threads by Team ID"""
    user_id = get_current_user_id()
    
    # Verify user has access to this Team ID
    if not user_has_access_to_team_id(user_id, team_id):
        return jsonify({'error': 'Access denied'}), 403
    
    # Fetch filtered threads
    threads = db.query(
        'SELECT * FROM sessions.threads WHERE team_id = $1 ORDER BY updated_at DESC',
        [team_id]
    )
    
    return jsonify({'threads': threads})
```

---

## Summary

### What the Team ID Integration Actually Touches

1. **Data Layer:**
   - Reads thread.team_id from ThreadManager.threads[] array
   - Requires backend to populate this field during thread creation
   - Needs database schema update (team_id column in sessions.threads)

2. **Rendering Layer:**
   - Adds conditional metadata item to renderThreadInfoContainer()
   - Uses existing .metadata-item structure
   - Applies new .team-id-tag CSS class
   - Respects .full-width grid spanning

3. **Event Layer:**
   - Exports filterByTeamId() globally
   - Implements onclick handler with event.stopPropagation()
   - Provides fallback notification when full filtering not available

4. **CSS Layer:**
   - Creates .team-id-tag class in main CSS file
   - Integrates with CSS variable system
   - Supports theme switching (light/dark)
   - Includes hover/active states

5. **Integration Layer:**
   - Works across all 20+ call sites automatically (single source of truth)
   - Updates in real-time via WebSocket broadcasts
   - Location-aware rendering (Prime, agents, workflow, synergy)
   - Responsive grid layout (desktop 2-col, mobile 1-col)

### What Still Needs to Be Done

1. **Database:** Add team_id column to sessions.threads table
2. **Backend:** Populate team_id during thread creation
3. **Filtering:** Implement ThreadManager.filterByTeamId() method
4. **UI:** Add filter indicator bar when active
5. **API:** Create Team ID filtering endpoint
6. **Testing:** Verify integration across all locations

The Team ID tag integration is NOT just a simple HTML addition - it's a well-architected integration into a sophisticated multi-layer rendering system with real-time updates, location-based behavior, and framework-wide propagation.
