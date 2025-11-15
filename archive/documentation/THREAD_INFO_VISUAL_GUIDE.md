# Thread Info Container - Visual Structure Guide

## 📦 Unified Container Structure

```
┌─────────────────────────────────────────────────────────┐
│ 🔷 THREAD INFO CONTAINER                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ROW 1: ┌──────────────────────────┬─────────────────┐ │
│        │ 📄 Thread Title          │ 🤖 Agent Badge  │ │
│        │ (Click to edit)          │ (Prime/Alpha-1) │ │
│        └──────────────────────────┴─────────────────┘ │
│                                                         │
│ ROW 2: ┌─────────┬─────────┬─────────┐               │
│        │ 💬 5 msg│ 📅 Nov 9│ 🕐 2:45PM│               │
│        └─────────┴─────────┴─────────┘               │
│                                                         │
│ ROW 3: ┌──────────────────┬────────────────┐         │
│        │ #️⃣ 1762664086386  │ ➕ Add Tag Btn │         │
│        │ (Click to copy)  │                │         │
│        └──────────────────┴────────────────┘         │
│                                                         │
│ ROW 4: ┌──────┬──────┬──────┐  (Only if tags exist)  │
│        │ urgent│ demo │ bug  │                        │
│        └──────┴──────┴──────┘                        │
│                                                         │
│ ROW 5: ┌─────────────────────────────┐  (Only if     │
│        │ 🔗 Q1 Planning (sess_abc...) │   linked)     │
│        └─────────────────────────────┘               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🎨 Display Modes

### FULL MODE (Prime Panel)
```
Font Sizes:
  Title: 16px (bold)
  Metadata: 12px
  Thread ID: 11px (monospace)
  Tags: 11px
  
Padding:
  Container: 15px
  Rows: 6px gap
  
Colors:
  Background: var(--bg-secondary)
  Border: 1px solid var(--border-default)
  Agent Badge (Prime): Gold gradient
```

### COMPACT MODE (Agents & Synergy)
```
Font Sizes:
  Title: 14px (bold)  ← Smaller
  Metadata: 11px      ← Smaller
  Thread ID: 10px     ← Smaller
  Tags: 10px          ← Smaller
  
Padding:
  Container: 10px     ← Tighter
  Rows: 4px gap       ← Tighter
  
Colors:
  Background: var(--bg-secondary)
  Border: 1px solid var(--border-default)
  Agent Badge (Agent): Blue gradient
```

---

## 🗺️ Where It Appears

### 1. PRIME AI CHAT (Left Sidebar)
```
┌─────────────────────────────────────┐
│ AI PRIME CHAT              [≡]  [○] │
├─────────────────────────────────────┤
│ ┌─────────────────────────────────┐ │
│ │ 🔷 THREAD INFO (FULL MODE)      │ │
│ │                                 │ │
│ │ ROW 1: Title + Prime Badge      │ │
│ │ ROW 2: 5 msg | Nov 9 | 2:45 PM  │ │
│ │ ROW 3: #1762664... | +Tag       │ │
│ │ ROW 4: [urgent] [demo]          │ │
│ │ ROW 5: 🔗 Q1 Planning           │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [User message bubble]               │
│                                     │
│ [AI response bubble]                │
│                                     │
│ [Input area with attachments]      │
│                                     │
└─────────────────────────────────────┘
```

### 2. AGENT COLUMNS (3 Columns)
```
┌──────────────┬──────────────┬──────────────┐
│ AGENT 1      │ AGENT 2      │ AGENT 3      │
│ Alpha-1      │ Bravo-2      │ Charlie-3    │
├──────────────┼──────────────┼──────────────┤
│ ┌──────────┐ │ ┌──────────┐ │ [No Thread]  │
│ │🔷COMPACT │ │ │🔷COMPACT │ │              │
│ │Title+🤖   │ │ │Title+🤖   │ │              │
│ │5msg|Nov9 │ │ │3msg|Nov8 │ │              │
│ │#176266...│ │ │#176261...│ │              │
│ │[demo]    │ │ │[urgent]  │ │              │
│ └──────────┘ │ └──────────┘ │              │
│              │              │              │
│ [Messages]   │ [Messages]   │ [Empty]      │
│              │              │              │
└──────────────┴──────────────┴──────────────┘
```

### 3. SYNERGY KANBAN CARDS
```
┌────────────────────────────────────────────┐
│ BACKLOG             │ IN PROGRESS    │ ... │
├────────────────────────────────────────────┤
│ ┌────────────────┐                         │
│ │ Synergy Card   │                         │
│ │ Q1 Planning    │                         │
│ ├────────────────┤                         │
│ │ Linked Threads │                         │
│ │ ┌────────────┐ │                         │
│ │ │🔷 COMPACT  │ │ ← Clickable wrapper    │
│ │ │Title + 🤖   │ │   opens thread in      │
│ │ │5msg|Nov9   │ │   assigned agent       │
│ │ │#176266...  │ │                         │
│ │ │[demo]      │ │                         │
│ │ └────────────┘ │                         │
│ │ ┌────────────┐ │                         │
│ │ │🔷 COMPACT  │ │                         │
│ │ │Another...  │ │                         │
│ │ └────────────┘ │                         │
│ └────────────────┘                         │
└────────────────────────────────────────────┘
```

---

## 🎯 Row-by-Row Breakdown

### ROW 1: Title + Agent Badge
```html
<div class="thread-info-row-1">
    <div class="thread-title-display" 
         ondblclick="ThreadManager.startInlineTitleEdit('prime')">
        Thread Title Here
    </div>
    <span class="thread-agent-badge thread-agent-badge-prime">
        <i class="fas fa-star"></i>
        <span>Prime</span>
    </span>
</div>
```

**Interactions:**
- Double-click title → Edit inline
- Agent badge shows assignment (Prime, Alpha-1, etc.)

---

### ROW 2: Metadata (Messages, Date, Time)
```html
<div class="thread-info-row-2">
    <span class="thread-metadata-item">
        <i class="fas fa-comment-dots"></i>
        <span id="prime-msg-count">5</span> msg
    </span>
    <span class="thread-metadata-item">
        <i class="fas fa-calendar"></i>
        <span id="prime-date">Nov 9, 2025</span>
    </span>
    <span class="thread-metadata-item">
        <i class="fas fa-clock"></i>
        <span id="prime-time">2:45 PM</span>
    </span>
</div>
```

**Data Sources:**
- Message count: `thread.message_count` or `thread.messages.length`
- Date: `thread.created` (formatted)
- Time: `thread.updated` or `thread.created` (formatted)

---

### ROW 3: Thread ID + Action Button
```html
<div class="thread-info-row-3">
    <span class="thread-id-badge" 
          onclick="ThreadManager.copyThreadId('1762664086386')"
          title="Thread ID: 1762664086386 (click to copy)">
        <i class="fas fa-hashtag"></i>
        <span>1762664086...</span>
    </span>
    <button class="add-tag-btn" 
            onclick="ThreadManager.showAddTagModal('prime')">
        <i class="fas fa-plus"></i> Add Tag
    </button>
</div>
```

**Interactions:**
- Click thread ID → Copies to clipboard + shows toast
- Click "+ Add Tag" → Opens tag selection modal

**Variants:**
- In Prime/Agents: Full "+ Add Tag" button
- In Synergy: Just "+ Tag" (shorter text)

---

### ROW 4: Tag Pills (Conditional)
```html
<div class="thread-tags-row" style="display: flex;">
    <span class="thread-tag-pill">
        <i class="fas fa-tag"></i> urgent
        <button onclick="ThreadManager.removeTag('threadId', 'urgent')" 
                class="tag-remove-btn">×</button>
    </span>
    <span class="thread-tag-pill">
        <i class="fas fa-tag"></i> demo
        <button onclick="ThreadManager.removeTag('threadId', 'demo')" 
                class="tag-remove-btn">×</button>
    </span>
</div>
```

**Visibility:**
- `style="display: flex"` if `thread.tags.length > 0`
- `style="display: none"` if no tags

**Interactions:**
- Click "×" → Removes tag from thread
- Tags wrap if too many (flexbox wrap)

---

### ROW 5: Synergy Badge (Conditional)
```html
<div class="thread-synergy-row" style="display: flex;">
    <div class="synergy-badge" 
         onclick="ThreadManager.copySynergyInfo('sess_abc123', 'Q1 Planning')">
        <i class="fas fa-link"></i>
        <span class="synergy-id">sess_abc...</span>
        <span class="synergy-name">Q1 Planning</span>
        <button onclick="event.stopPropagation(); 
                         ThreadManager.unlinkFromSynergy('threadId')" 
                class="synergy-unlink-btn">×</button>
    </div>
</div>
```

**Visibility:**
- `style="display: flex"` if `thread.synergy_card_id` exists
- `style="display: none"` if not linked

**Interactions:**
- Click badge → Copies Synergy ID + name to clipboard
- Click "×" → Unlinks thread from Synergy session

---

## 🔄 Dynamic Updates

### When Thread Loads
```javascript
// PRIME
ThreadManager.updatePrimeHeader(threadId)
  → Reads thread data
  → Updates all 5 rows in existing HTML

// AGENT
MultiAgent.loadThreadIntoAgent(agentId, thread)
  → Calls ThreadManager.renderThreadInfoContainer()
  → Replaces #thread-info-{agentId} innerHTML
  → Shows all 5 rows

// SYNERGY
synergyBoard.renderLinkedThreads([threadIds])
  → Fetches thread details from backend
  → Calls ThreadManager.renderThreadInfoContainer() for each
  → Wraps in .synergy-linked-thread-wrapper
  → Returns HTML string
```

### When Thread Updated
```javascript
// Message sent
thread.message_count++
thread.updated = new Date().toISOString()
ThreadManager.updatePrimeHeader(threadId)  // Re-renders rows

// Tag added
thread.tags.push('newTag')
ThreadManager.updatePrimeHeader(threadId)  // Shows new tag in row 4

// Synergy linked
thread.synergy_card_id = 'sess_xyz'
thread.synergy_card_name = 'Project Alpha'
ThreadManager.updatePrimeHeader(threadId)  // Shows badge in row 5
```

---

## 🎨 Color Coding

### Agent Badges
```css
Prime:    Gold gradient   (#ffd700 → #ff8c00)
Alpha-1:  Blue gradient   (#4facfe → #00f2fe)
Bravo-2:  Blue gradient   (#4facfe → #00f2fe)
Charlie-3: Blue gradient  (#4facfe → #00f2fe)
```

### Tag Pills
```css
Background: var(--bg-tertiary, #1c2128)
Color:      var(--accent-primary, #58a6ff)
Border:     1px solid var(--border-default, #30363d)
```

### Synergy Badge
```css
Background: var(--bg-tertiary, #1c2128)
Color:      var(--accent-primary, #58a6ff)
Border:     1px solid var(--accent-primary, #58a6ff)
Icon:       var(--accent-primary, #58a6ff)
```

---

## 📊 Data Mapping

| Display | Data Source | Format |
|---------|-------------|--------|
| Title | `thread.title` | String (truncate if > 50 chars) |
| Agent Badge | `thread.agent` or location mapping | String → Icon + Name |
| Message Count | `thread.message_count` or `thread.messages.length` | Integer |
| Date | `thread.created` | "Nov 9, 2025" |
| Time | `thread.updated` or `thread.created` | "2:45 PM" |
| Thread ID | `thread.id` (thread_slug) | Truncate to 12 chars + "..." |
| Tags | `thread.tags` (array) | Array of strings |
| Synergy ID | `thread.synergy_card_id` | Truncate to 8 chars + "..." |
| Synergy Name | `thread.synergy_card_name` | String |

---

## ✅ Validation Rules

### Title
- ✅ Required (fallback: "Untitled")
- ✅ Max length: No limit (truncates in UI if > 50 chars)
- ✅ Editable: Yes (double-click)

### Message Count
- ✅ Default: 0
- ✅ Source: Backend `message_count` (preferred) or `messages.length`
- ✅ Updates: On every message sent

### Date/Time
- ✅ Format: Local timezone
- ✅ Date: "Nov 9, 2025" or "Nov 9" (compact)
- ✅ Time: "2:45 PM" or "14:45" (24hr if user preference)

### Thread ID
- ✅ Format: 13-digit timestamp (1762664086386)
- ✅ Display: Truncate to 12 + "..."
- ✅ Copyable: Click to copy full ID

### Tags
- ✅ Max per thread: No limit (wraps in flexbox)
- ✅ Max tag length: No limit (wraps in pill)
- ✅ Removable: Yes (× button)

### Synergy Link
- ✅ Optional: Can be null
- ✅ Format: sess_[alphanumeric]
- ✅ Display: Truncate to 8 chars + "..."
- ✅ Unlinkable: Yes (× button)

---

## 🚀 Performance Optimization

### Rendering Strategy
```javascript
// DON'T: Re-render entire container on every update
document.getElementById('thread-info').innerHTML = renderThreadInfoContainer(...);

// DO: Update specific elements when possible
document.getElementById('prime-msg-count').textContent = newCount;
document.getElementById('prime-date').textContent = newDate;
```

### Caching Strategy
```javascript
// Cache Synergy session metadata client-side
if (!window._synergySessionCache) window._synergySessionCache = {};

// Reuse cached data instead of fetching again
if (cache[synergyId]) {
    return cache[synergyId];
} else {
    // Fetch from backend + cache
}
```

---

## 🎉 Summary

**One Component, Five Locations:**
1. Prime AI Chat (full mode)
2. Agent Column 1 (compact)
3. Agent Column 2 (compact)
4. Agent Column 3 (compact)
5. Synergy Kanban Cards (compact, read-only)

**All display the same information:**
- Thread title + agent assignment
- Message count + dates
- Thread ID + tags
- Synergy link (if applicable)

**Consistent interactions:**
- Edit title (double-click)
- Copy thread ID (click)
- Add/remove tags (buttons)
- Link/unlink Synergy (buttons)

---

**Result:** Clean, maintainable, consistent UI across the entire platform! 🎊
