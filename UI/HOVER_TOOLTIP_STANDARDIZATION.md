# 🎯 Hover Tooltip Standardization - Implementation Guide

## Date: November 12, 2025
## Status: 🚧 IN PROGRESS

---

## 📋 Current State Analysis

### ✅ Already Implemented (Thread History Modal)

**Location:** Thread history sidebar - Synergy badge hover
**Implementation:** Lines 17065-17195 in business-ai-platform-v2.html

**Features:**
- Rich tooltip with session title, description, users, last updated
- Priority badge (high/medium/low with color coding)
- "Open in Synergy Dashboard" link button
- Smooth fade-in animation (200ms delay)
- Smart positioning (centers under badge, adjusts if off-screen)
- Auto-hides on scroll

**Data Attributes Used:**
```html
<div class="synergy-badge"
     data-tooltip-title="Yesterday's Outlook Email Processing"
     data-tooltip-desc="Multi-platform project involving: Microsoft Outlook..."
     data-tooltip-users="Alpha-1"
     data-tooltip-updated="11/11/2025, 11:25 PM"
     data-priority="high">
```

**CSS Classes:** (Lines 1963-2067)
- `.synergy-tooltip` - Main container
- `.synergy-tooltip-title` - Session title with icon
- `.synergy-tooltip-priority` - Priority badge (high/medium/low)
- `.synergy-tooltip-desc` - Description text
- `.synergy-tooltip-meta` - Metadata rows (users, date)
- `.synergy-tooltip-actions` - Action buttons
- `.synergy-tooltip-link` - Dashboard link button

---

## 🎯 Areas Needing Standardization

### 1. **AI Agent Columns** (PRIORITY 1)
**Current:** Simple browser `title` attribute
**Needs:** Rich tooltip like thread history modal

**Locations:**
- Agent 1/2/3 thread-info cards
- Synergy badge in agent columns (Row 5)

**What to Show:**
- Full Synergy session title (not generic "Synergy Session")
- Session description (first 100 chars)
- Priority badge
- Assigned users/agents
- Last updated time
- "Open in Synergy Dashboard" link
- "Unlink from Synergy" button with icon

**Current Implementation (Line 18563):**
```html
<div class="synergy-badge" 
     onclick="ThreadManager.copySynergyInfo('${thread.synergy_card_id}', '${thread.synergy_card_name || 'Synergy Session'}')">
    <i class="fas fa-link"></i>
    <span class="synergy-id">${thread.synergy_card_id.slice(0, 8)}...</span>
    <span class="synergy-name">${thread.synergy_card_name || 'Synergy Session'}</span>
    <button onclick="event.stopPropagation(); ThreadManager.unlinkFromSynergy('${thread.id}')" 
            class="synergy-unlink-btn" 
            title="Unlink from Synergy">×</button>  <!-- ❌ Using × character -->
</div>
```

**Needed Changes:**
1. Add data attributes for tooltip
2. Change unlink button icon from `×` to `<i class="fas fa-unlink"></i>`
3. Fetch actual session details to populate tooltip
4. Apply hover tooltip JavaScript

---

### 2. **Prime Panel Sidebar** (PRIORITY 2)
**Current:** Simple browser `title` attribute
**Needs:** Same rich tooltip

**Locations:**
- Prime thread-info cards in sidebar
- Synergy badges

**Same implementation as agent columns**

---

### 3. **Synergy Dashboard Cards** (PRIORITY 3)
**Current:** No hover tooltip, only click-to-expand
**Needs:** Quick preview on hover

**Locations:**
- Synergy Kanban board cards (collapsed view)
- Thread links within cards

**What to Show:**
- Full session title
- Description preview
- Status/Priority
- Linked threads count
- Next steps preview
- "Click to expand" hint

---

### 4. **Thread List Items** (PRIORITY 4)
**Current:** Basic title truncation
**Needs:** Full preview on hover

**Locations:**
- Thread history modal list items
- Thread picker modal

**What to Show:**
- Full thread title (if truncated)
- Message count
- Last message preview
- Creation date
- Tags
- Agent assignment

---

## 🔧 Implementation Plan

### Phase 1: Universal Tooltip System (FOUNDATION)

**Step 1: Create Global Tooltip Manager**

Create a reusable tooltip system that works everywhere:

```javascript
// Global Tooltip Manager
const UnifiedTooltip = {
    element: null,
    timeout: null,
    
    create() {
        if (!this.element) {
            this.element = document.createElement('div');
            this.element.className = 'unified-tooltip';
            document.body.appendChild(this.element);
        }
        return this.element;
    },
    
    show(config) {
        // config = { target, title, content, actions, delay }
        const tooltip = this.create();
        
        // Build HTML
        tooltip.innerHTML = `
            <div class="unified-tooltip-title">${config.title}</div>
            ${config.content || ''}
            ${config.actions || ''}
        `;
        
        // Position relative to target
        this.position(tooltip, config.target);
        
        // Show with delay
        clearTimeout(this.timeout);
        this.timeout = setTimeout(() => {
            tooltip.classList.add('show');
        }, config.delay || 200);
    },
    
    hide() {
        clearTimeout(this.timeout);
        if (this.element) {
            this.element.classList.remove('show');
        }
    },
    
    position(tooltip, target) {
        const rect = target.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        let left = rect.left + (rect.width / 2) - 160;
        let top = rect.bottom + 8;
        
        // Adjust for screen boundaries
        if (left < 10) left = 10;
        if (left + 320 > window.innerWidth) left = window.innerWidth - 330;
        if (top + tooltipRect.height > window.innerHeight) {
            top = rect.top - tooltipRect.height - 8;
        }
        
        tooltip.style.left = `${left}px`;
        tooltip.style.top = `${top}px`;
    }
};
```

**Step 2: Global Event Listeners**

```javascript
// Unified tooltip event delegation
document.addEventListener('mouseover', (e) => {
    const tooltipTarget = e.target.closest('[data-unified-tooltip]');
    if (tooltipTarget) {
        const config = JSON.parse(tooltipTarget.getAttribute('data-unified-tooltip'));
        UnifiedTooltip.show({ target: tooltipTarget, ...config });
    }
});

document.addEventListener('mouseout', (e) => {
    const tooltipTarget = e.target.closest('[data-unified-tooltip]');
    if (tooltipTarget) {
        UnifiedTooltip.hide();
    }
});

document.addEventListener('scroll', () => UnifiedTooltip.hide(), true);
```

---

### Phase 2: Synergy Badge Enhancement (AGENT COLUMNS)

**Step 1: Add Synergy Session Metadata Cache**

When rendering Synergy badge, fetch and cache session metadata:

```javascript
// In ThreadManager or global scope
const SynergyMetadataCache = {
    cache: new Map(),
    
    async get(sessionId) {
        if (this.cache.has(sessionId)) {
            return this.cache.get(sessionId);
        }
        
        try {
            const response = await fetch(`http://localhost:5001/api/synergy/${sessionId}`);
            const data = await response.json();
            const metadata = {
                title: data.title,
                description: data.description,
                priority: data.priority,
                assignees: data.assignees,
                updated: data.last_active,
                thread_count: data.thread_ids?.length || 0
            };
            this.cache.set(sessionId, metadata);
            return metadata;
        } catch (error) {
            console.error('[SynergyMetadataCache] Failed to fetch:', error);
            return null;
        }
    }
};
```

**Step 2: Update Synergy Badge Rendering**

In `renderThreadInfoContainer()` (Line 18563):

```javascript
// Row 5: Synergy badge (if any) - ENHANCED WITH RICH TOOLTIP
<div class="thread-synergy-row" id="${location}-thread-synergy" 
     style="display: ${thread.synergy_card_id ? 'flex' : 'none'};">
    ${thread.synergy_card_id ? `
        <div class="synergy-badge" 
             onclick="ThreadManager.copySynergyInfo('${safeEscape(thread.synergy_card_id)}', '${safeEscape(thread.synergy_card_name || 'Synergy Session')}')"
             data-tooltip-title="${safeEscape(thread.synergy_card_name || 'Synergy Session')}"
             data-tooltip-desc="${safeEscape(thread.synergy_card_desc || '')}"
             data-tooltip-users="${safeEscape(thread.synergy_card_users || '')}"
             data-tooltip-updated="${safeEscape(thread.synergy_card_updated || '')}"
             data-priority="${thread.synergy_priority || 'medium'}">
            <i class="fas fa-link"></i>
            <span class="synergy-id">${thread.synergy_card_id.slice(0, 8)}...</span>
            <span class="synergy-name">${thread.synergy_card_name || 'Synergy Session'}</span>
            
            <!-- ENHANCED: Font Awesome icon instead of × -->
            <button onclick="event.stopPropagation(); ThreadManager.confirmUnlinkFromSynergy('${safeEscape(thread.id)}', '${safeEscape(thread.synergy_card_name || 'Synergy Session')}')" 
                    class="synergy-unlink-btn" 
                    title="Unlink from Synergy">
                <i class="fas fa-unlink"></i>  <!-- ✅ Font Awesome icon -->
            </button>
        </div>
    ` : ''}
</div>
```

**Step 3: Fetch Metadata When Thread Loads**

When loading thread into agent column, fetch Synergy metadata:

```javascript
// In ThreadManager.loadThread() or assignThread()
async loadThread(threadId, location) {
    const thread = this.threads.find(t => t.id === threadId);
    
    // If thread has Synergy link, fetch metadata
    if (thread.synergy_card_id) {
        const metadata = await SynergyMetadataCache.get(thread.synergy_card_id);
        if (metadata) {
            thread.synergy_card_name = metadata.title;
            thread.synergy_card_desc = metadata.description;
            thread.synergy_card_users = metadata.assignees?.join(', ');
            thread.synergy_card_updated = this.formatTimeAgo(metadata.updated);
            thread.synergy_priority = metadata.priority;
        }
    }
    
    // Render thread-info
    const html = this.renderThreadInfoContainer(location, threadId, true);
    // ... rest of rendering
}
```

---

### Phase 3: CSS Enhancement

**Add unified tooltip styles** (consistent with existing synergy-tooltip):

```css
/* Unified Tooltip System - Works everywhere */
.unified-tooltip {
    position: fixed;
    z-index: 10000;
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: 8px;
    padding: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    max-width: 320px;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.2s ease;
}

.unified-tooltip.show {
    opacity: 1;
}

/* Enhanced Synergy unlink button */
.synergy-unlink-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    padding: 0;
    background: rgba(248, 81, 73, 0.1);
    border: 1px solid rgba(248, 81, 73, 0.3);
    border-radius: 4px;
    color: #f85149;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.synergy-unlink-btn:hover {
    background: rgba(248, 81, 73, 0.2);
    border-color: #f85149;
    transform: scale(1.1);
}

.synergy-unlink-btn i {
    font-size: 10px;
}
```

---

## 🎯 Implementation Priority

### ✅ Phase 1 (Immediate - TODAY)
1. Fix unlink button icon (`×` → `<i class="fas fa-unlink"></i>`)
2. Add Synergy metadata cache
3. Fetch actual session title for agent columns
4. Add data attributes to Synergy badges

### 🚧 Phase 2 (This Week)
1. Implement UnifiedTooltip manager
2. Apply to all Synergy badges (agent columns + sidebar)
3. Test with thread history modal (ensure consistency)

### 📅 Phase 3 (Next Week)
1. Add tooltips to thread list items
2. Add tooltips to Synergy dashboard cards
3. Add tooltips to action buttons (archive, delete, etc.)

---

## 📊 Success Metrics

- ✅ **Consistency:** Same tooltip style everywhere
- ✅ **Performance:** < 200ms to show, no lag
- ✅ **Usability:** Auto-positions, smart boundary detection
- ✅ **Accessibility:** Keyboard navigable, screen reader friendly
- ✅ **Mobile:** Tap-to-show on touch devices

---

## 🐛 Known Issues to Address

1. **Current:** Generic "Synergy Session" text in agent columns
   - **Fix:** Fetch actual session title from API

2. **Current:** `×` character for unlink button
   - **Fix:** Use `<i class="fas fa-unlink"></i>`

3. **Current:** No hover preview in Synergy dashboard
   - **Fix:** Add card preview tooltip

4. **Current:** Truncated thread titles with no preview
   - **Fix:** Add full title tooltip on hover

---

## 📚 API Endpoints Needed

### Get Synergy Session Metadata
```
GET /api/synergy/{session_id}

Response:
{
  "success": true,
  "session_id": "sess_20251111_...",
  "title": "Yesterday's Outlook Email Processing",
  "description": "Multi-platform project involving...",
  "priority": "high",
  "assignees": ["Alpha-1"],
  "last_active": "2025-11-11T23:25:00Z",
  "thread_ids": ["1762851232975", ...],
  "status": "in_progress",
  "kanban_column": "in_progress"
}
```

### Batch Get Synergy Metadata (Optimization)
```
POST /api/synergy/batch

Request:
{
  "session_ids": ["sess_1", "sess_2", "sess_3"]
}

Response:
{
  "success": true,
  "sessions": [...]
}
```

---

## 🎨 Visual Consistency Checklist

- [ ] Same border-radius (8px)
- [ ] Same shadow (0 8px 24px rgba(0,0,0,0.4))
- [ ] Same colors (--bg-secondary, --border-default)
- [ ] Same font sizes (title 13px, desc 12px, meta 11px)
- [ ] Same animations (200ms fade-in)
- [ ] Same positioning logic
- [ ] Same priority badge colors (high/medium/low)
- [ ] Same action button style

---

**Status:** Ready for implementation
**Next Steps:** 
1. Fix unlink button icon
2. Implement SynergyMetadataCache
3. Update renderThreadInfoContainer with data attributes
4. Test across all locations

