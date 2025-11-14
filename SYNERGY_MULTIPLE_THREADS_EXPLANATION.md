# How Synergy Cards Display Multiple Threads 🧵

**Date:** November 14, 2025  
**Topic:** Multiple thread cards rendering inside a single Synergy card  
**Status:** FULLY DOCUMENTED

---

## Quick Answer

A Synergy card can display **multiple thread cards** stacked vertically inside the "Linked Threads" section. Each thread card is a complete, interactive mini-card that shows thread info and can be clicked to open.

---

## Visual Example

```
┌─────────────────────────────────────────────────────┐
│ 📋 Morning Email Follow-ups [SYNERGY CARD]         │
│                                                     │
│ 🎯 Next Steps (4)                                  │
│ ✅ Checklist (0/7)                                  │
│ 📄 Documents (1)                                    │
│                                                     │
│ 💬 Linked Threads (3)  ← Section header            │
│ ┌─────────────────────────────────────────────┐   │
│ │ 🔵 Thread #1762828793392         [THREAD 1] │   │
│ │ 📩 5 messages | Updated 2 mins ago          │   │
│ │ 🏷️ urgent, email                             │   │
│ └─────────────────────────────────────────────┘   │
│ ┌─────────────────────────────────────────────┐   │
│ │ 🔵 Thread #1762830154821         [THREAD 2] │   │
│ │ 📩 12 messages | Updated 15 mins ago        │   │
│ │ 🏷️ customer-service                         │   │
│ └─────────────────────────────────────────────┘   │
│ ┌─────────────────────────────────────────────┐   │
│ │ 🔵 Thread #1762831456789         [THREAD 3] │   │
│ │ 📩 3 messages | Updated 1 hour ago          │   │
│ │ 🏷️ quote-request                            │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ 📜 Activity Log                                     │
└─────────────────────────────────────────────────────┘
```

---

## How It Works - Complete Flow

### Step 1: Synergy Session Data Structure

When a Synergy session is created, it stores linked thread IDs in a JSON array:

```javascript
// Database: synergy_sessions table
{
    session_id: "sess_20251113_1309_morning_email_follow-ups",
    title: "Morning Email Follow-ups",
    thread_ids: ["1762828793392", "1762830154821", "1762831456789"],  // ← Array of thread slugs
    next_steps: [...],
    checklist: [...],
    documents: [...]
}
```

### Step 2: Card Rendering Trigger

When `renderCard(session)` is called (line 28498):

```javascript
renderCard(session) {
    // ... create card element ...
    
    // Parse thread_ids from JSON
    const threadIds = this.parseJsonField(session.thread_ids, []); 
    // Result: ["1762828793392", "1762830154821", "1762831456789"]
    
    if (threadIds.length > 0) {
        // Asynchronously load thread details and render
        this.renderLinkedThreads(threadIds).then(threadsHTML => {
            const threadsSection = document.getElementById(`threads-section-${session.session_id}`);
            if (threadsSection) {
                const loadingDiv = threadsSection.querySelector('.thread-list-loading');
                if (loadingDiv) {
                    loadingDiv.outerHTML = threadsHTML;  // Replace loading spinner with threads
                }
            }
        });
    }
}
```

### Step 3: Fetch Thread Details

The `renderLinkedThreads()` function (line 30780) fetches full thread data:

```javascript
async renderLinkedThreads(threadIds) {
    // Input: ["1762828793392", "1762830154821", "1762831456789"]
    
    // API call to get thread details
    const response = await fetch(`${this.apiBaseUrl}/api/threads/details`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ thread_ids: threadIds })
    });
    
    const result = await response.json();
    const threads = result.data || result;
    
    // Result: Array of thread objects
    // [
    //   { id: 18, thread_slug: "1762828793392", name: "...", message_count: 5, ... },
    //   { id: 19, thread_slug: "1762830154821", name: "...", message_count: 12, ... },
    //   { id: 20, thread_slug: "1762831456789", name: "...", message_count: 3, ... }
    // ]
}
```

### Step 4: Render Each Thread Card

For **each thread** in the array, create a thread card wrapper:

```javascript
const threadsHTML = threads.map(thread => {
    // Normalize thread data
    const normalizedThread = {
        id: thread.thread_slug || thread.id,  // Use slug (1762828793392) not DB ID (18)
        title: thread.name || thread.thread_slug,
        created: thread.created_at,
        updated: thread.updated_at,
        message_count: thread.message_count || 0,
        tags: thread.tags || [],
        agent: thread.agent_id || 'prime'
    };
    
    // Use ThreadManager to render thread info container
    const threadInfoHTML = window.ThreadManager.renderThreadInfoContainer(
        'synergy',      // context
        normalizedThread.id,  // thread ID
        true            // compact mode
    );
    
    // Wrap in draggable container with click handler
    return `
        <div class="synergy-linked-thread-wrapper" 
             data-thread-id="${normalizedThread.id}"
             draggable="true"
             ondragstart="ThreadManager.handleDragStart(event)"
             onclick="synergyBoard.openThread('${normalizedThread.id}', '${thread.agent_id || 'prime'}')">
            ${threadInfoHTML}
        </div>
    `;
}).join('');  // Join all thread cards into single HTML string
```

### Step 5: Wrap in Container

All thread cards are wrapped in a scrollable container:

```javascript
return `
    <div class="linked-threads-container">
        <div class="linked-threads-list">
            ${threadsHTML}  ← All 3 thread cards concatenated here
        </div>
    </div>
`;
```

### Step 6: Insert into Synergy Card

The HTML is inserted into the `#threads-section-` element:

```javascript
const threadsSection = document.getElementById(`threads-section-${session.session_id}`);
if (threadsSection) {
    const loadingDiv = threadsSection.querySelector('.thread-list-loading');
    if (loadingDiv) {
        loadingDiv.outerHTML = threadsHTML;  // Replace spinner with 3 thread cards
    }
}
```

---

## CSS Layout Structure

### Container Hierarchy

```css
.kanban-card                              /* Synergy card */
  └─ .card-section#threads-section-       /* Linked Threads section */
      └─ .linked-threads-container        /* Outer wrapper */
          └─ .linked-threads-list         /* Vertical stack container */
              ├─ .synergy-linked-thread-wrapper  /* Thread 1 */
              │   └─ .ai-chat-header-info        /* Thread info */
              ├─ .synergy-linked-thread-wrapper  /* Thread 2 */
              │   └─ .ai-chat-header-info        /* Thread info */
              └─ .synergy-linked-thread-wrapper  /* Thread 3 */
                  └─ .ai-chat-header-info        /* Thread info */
```

### Key CSS Classes

**`.linked-threads-list`** (lines 1697-1705) - Vertical stack:
```css
.linked-threads-list {
    display: flex;
    flex-direction: column;   /* Stack vertically */
    gap: 8px;                 /* 8px space between cards */
    max-height: 400px;        /* Max height before scrolling */
    overflow-y: auto;         /* Scroll if > 400px */
    padding: 8px;
}
```

**`.synergy-linked-thread-wrapper`** (lines 1674-1682) - Individual thread card:
```css
.synergy-linked-thread-wrapper {
    margin-bottom: 8px;       /* Spacing */
    border: 1px solid #30363d;
    border-radius: 8px;
    background: #0d1117;
    transition: all 0.2s;
    cursor: pointer;
    overflow: hidden;
}

.synergy-linked-thread-wrapper:hover {
    border-color: #58a6ff;    /* Blue highlight on hover */
    background: #161b22;
    transform: translateY(-2px);  /* Lift up slightly */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
```

---

## Thread Card Features

### 1. Clickable

Each thread card is clickable and opens the thread:

```javascript
onclick="synergyBoard.openThread('${normalizedThread.id}', '${thread.agent_id || 'prime}')"
```

When clicked:
1. Switches to "AI Agents" tab
2. Loads the thread in the appropriate agent column
3. Shows full conversation history

### 2. Draggable

Each thread card is draggable:

```html
<div class="synergy-linked-thread-wrapper" 
     draggable="true"
     ondragstart="ThreadManager.handleDragStart(event)">
```

You can:
- Drag thread OUT of Synergy card
- Drag thread TO another Synergy card
- Drag thread TO agent columns

### 3. Hover Effects

CSS provides visual feedback:
- **Default:** Gray border, dark background
- **Hover:** Blue border, lighter background, lift effect, shadow
- **Transition:** Smooth 0.2s animation

### 4. Compact Display

Each thread card shows:
- 🔵 Thread icon with color
- 📌 Thread title/ID
- 📩 Message count
- 🕒 Last updated time
- 🏷️ Tags (if any)
- 👤 Assigned agent (if any)

---

## How Multiple Threads are Added

### Method 1: Drag-and-Drop (Primary)

1. User drags a thread from thread list
2. User drops thread onto Synergy card
3. `handleThreadDrop()` is called (line 30914)
4. API call: `POST /api/synergy/link-thread`
5. Database: Insert into `synergy_thread_links` table
6. Update session's `thread_ids` array
7. Card re-renders with new thread added

```javascript
async handleThreadDrop(event, synergyId) {
    event.preventDefault();
    
    const threadId = event.dataTransfer.getData('text/plain');
    console.log(`[SYNERGY] Thread ${threadId} dropped on session ${synergyId}`);
    
    try {
        const response = await fetch(`${this.apiBaseUrl}/api/synergy/link-thread`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                synergy_id: synergyId,
                thread_id: threadId
            })
        });
        
        if (response.ok) {
            // Re-render card to show new thread
            const session = this.sessions.find(s => s.session_id === synergyId);
            if (session) {
                this.renderCard(session);
            }
        }
    } catch (error) {
        console.error('[SYNERGY] Failed to link thread:', error);
    }
}
```

### Method 2: API Direct Link

Backend can link threads programmatically:

```python
# AI_infrastructure/routes/synergy_routes.py
@synergy_bp.route('/link-thread', methods=['POST'])
def link_thread():
    data = request.json
    synergy_id = data.get('synergy_id')
    thread_id = data.get('thread_id')
    
    # Update database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current thread_ids
    cursor.execute("SELECT thread_ids FROM synergy_sessions WHERE session_id = ?", (synergy_id,))
    row = cursor.fetchone()
    thread_ids = json.loads(row[0] or '[]')
    
    # Add new thread ID if not already present
    if thread_id not in thread_ids:
        thread_ids.append(thread_id)
        
        # Update session
        cursor.execute("""
            UPDATE synergy_sessions 
            SET thread_ids = ?, updated_at = ? 
            WHERE session_id = ?
        """, (json.dumps(thread_ids), datetime.now().isoformat(), synergy_id))
        
        conn.commit()
    
    conn.close()
    return jsonify({'success': True})
```

---

## Performance Optimization

### 1. Asynchronous Loading

Threads load asynchronously to avoid blocking card render:

```javascript
// Card renders immediately with "Loading..." spinner
card.innerHTML = `... <div class="thread-list-loading">Loading...</div> ...`;

// Threads load in background
this.renderLinkedThreads(threadIds).then(threadsHTML => {
    // Replace spinner when ready
    loadingDiv.outerHTML = threadsHTML;
});
```

### 2. Caching Synergy Metadata

Global cache prevents redundant API calls:

```javascript
if (!window._synergySessionCache) window._synergySessionCache = {};
const cache = window._synergySessionCache;

// Only fetch missing sessions
const missing = synergyIdsToLoad.filter(id => !cache[id]);
if (missing.length > 0) {
    // Fetch batch
    const resp = await fetch(`${this.apiBaseUrl}/api/synergy?ids=${missing.join(',')}`);
    // Store in cache
}
```

### 3. Compact Mode

Thread cards use compact rendering to save space:

```javascript
const threadInfoHTML = window.ThreadManager.renderThreadInfoContainer(
    'synergy',
    normalizedThread.id,
    true  // ← compact mode (less padding, smaller fonts)
);
```

### 4. Max Height + Scroll

Prevent cards from becoming too tall:

```css
.linked-threads-list {
    max-height: 400px;     /* Max 400px */
    overflow-y: auto;      /* Scroll if needed */
}
```

If 10+ threads, the container scrolls instead of expanding infinitely.

---

## Example Scenario

### User Action: Email Follow-up Session

1. **Create Synergy Session**
   - Title: "Morning Email Follow-ups"
   - Next Steps: Respond to 7 emails
   - Checklist: 7 tasks (one per email)

2. **Create Thread for Each Email**
   - Thread 1: "Aaron Woods - Quote Approval"
   - Thread 2: "GoldCoast Marketing - Urgent Order"
   - Thread 3: "MBE Eight Mile - Premium Quote"
   - Thread 4: "MGR Roofing - Standard Order"
   - Thread 5: "ABC Company - Follow-up"
   - Thread 6: "XYZ Corp - Status Update"
   - Thread 7: "DEF Ltd - New Inquiry"

3. **Link All Threads to Session**
   - Drag Thread 1 → Drop on Synergy card
   - Drag Thread 2 → Drop on Synergy card
   - ... repeat for all 7 threads

4. **Result: Synergy Card Shows All 7 Threads**
   ```
   💬 Linked Threads (7)
   ┌─────────────────────────────────┐
   │ Thread 1 | 5 msgs | 2 mins ago  │
   │ Thread 2 | 12 msgs | 5 mins ago │
   │ Thread 3 | 3 msgs | 10 mins ago │
   │ Thread 4 | 8 msgs | 15 mins ago │
   │ Thread 5 | 2 msgs | 20 mins ago │
   │ Thread 6 | 7 msgs | 25 mins ago │
   │ Thread 7 | 1 msg | 30 mins ago  │
   └─────────────────────────────────┘
   ```

5. **User Experience**
   - Hover over any thread → Blue highlight
   - Click any thread → Opens in agent column
   - See all related threads in one place
   - Track progress (message counts, timestamps)

---

## Technical Deep Dive

### Thread ID Resolution

**CRITICAL:** Must use `thread_slug` (e.g., "1762828793392") NOT numeric DB ID (e.g., 18)

```javascript
// ❌ WRONG - Uses numeric DB ID
const normalizedThread = {
    id: thread.id  // 18 (won't match ThreadManager lookup)
};

// ✅ CORRECT - Uses thread slug
const normalizedThread = {
    id: thread.thread_slug || thread.id  // "1762828793392" (matches ThreadManager)
};
```

**Why?** ThreadManager uses slugs as unique identifiers, not DB IDs.

### ThreadManager Integration

Synergy uses ThreadManager's rendering functions for consistency:

```javascript
// Delegate thread card rendering to ThreadManager
const threadInfoHTML = window.ThreadManager.renderThreadInfoContainer(
    'synergy',              // Context (for styling)
    normalizedThread.id,    // Thread slug
    true                    // Compact mode
);
```

**Benefits:**
- Consistent UI across all thread displays
- Same hover effects, icons, formatting
- Automatic updates when ThreadManager changes
- No duplicate rendering code

### Empty State Handling

If no threads linked:

```javascript
if (!threadIds || threadIds.length === 0) {
    return '<div class="no-threads"><i class="fas fa-link-slash"></i> No threads linked</div>';
}
```

Displays friendly message instead of empty space.

---

## Database Schema

### synergy_sessions Table

```sql
CREATE TABLE synergy_sessions (
    session_id TEXT PRIMARY KEY,
    title TEXT,
    thread_ids TEXT,  -- JSON array: ["1762828793392", "1762830154821", ...]
    next_steps TEXT,
    checklist TEXT,
    documents TEXT,
    kanban_column TEXT,
    status TEXT,
    created_at TEXT,
    updated_at TEXT
);
```

### synergy_thread_links Table (Alternative)

Some implementations use a separate junction table:

```sql
CREATE TABLE synergy_thread_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    synergy_id TEXT,
    thread_id TEXT,
    linked_at TEXT,
    FOREIGN KEY (synergy_id) REFERENCES synergy_sessions(session_id),
    FOREIGN KEY (thread_id) REFERENCES threads(thread_slug)
);
```

**Benefits:**
- Better for many-to-many relationships
- Easier to query ("which sessions link to this thread?")
- Can store link metadata (who linked, when, why)

---

## Common Issues & Solutions

### Issue 1: Thread Cards Not Showing

**Symptom:** Linked Threads section shows "Loading..." forever

**Causes:**
- API endpoint `/api/threads/details` not responding
- ThreadManager not loaded
- Invalid thread IDs in `thread_ids` array

**Debug:**
```javascript
console.log('[SYNERGY] thread_ids:', threadIds);
console.log('[SYNERGY] ThreadManager available:', !!window.ThreadManager);
```

**Solution:**
- Verify API endpoint exists and returns data
- Ensure ThreadManager loads before Synergy board
- Validate thread IDs match existing threads

### Issue 2: Wrong Thread Opens

**Symptom:** Clicking thread card opens different thread

**Cause:** Using numeric DB ID instead of thread slug

**Fix:**
```javascript
// Change from:
id: thread.id

// To:
id: thread.thread_slug || thread.id
```

### Issue 3: Threads Not Draggable

**Symptom:** Can't drag threads out of Synergy card

**Cause:** Missing `draggable="true"` or `ondragstart` handler

**Fix:**
```html
<div class="synergy-linked-thread-wrapper" 
     draggable="true"
     ondragstart="ThreadManager.handleDragStart(event)">
```

### Issue 4: Too Many Threads (Performance)

**Symptom:** Synergy card slow with 50+ linked threads

**Solutions:**
1. **Pagination:**
   ```javascript
   // Show first 20, load more on scroll
   const displayThreads = threads.slice(0, 20);
   ```

2. **Lazy Loading:**
   ```javascript
   // Load thread details only when card expanded
   if (card.dataset.expanded === 'true') {
       renderLinkedThreads(threadIds);
   }
   ```

3. **Virtual Scrolling:**
   ```javascript
   // Render only visible threads (complex but fast)
   ```

---

## Best Practices

### 1. Limit Threads Per Session

Recommend max 20-30 threads per Synergy session:
- Better performance
- Easier to manage
- Clearer organization

If more threads needed, create sub-sessions.

### 2. Use Descriptive Thread Titles

Good thread titles help users identify threads:
- ✅ "Aaron Woods - Quote Approval - 2000 business cards"
- ❌ "Thread 1762828793392"

### 3. Update Thread Counts

Show thread count in section header:
```html
<div class="section-title">
    <i class="fas fa-comments"></i> 
    Linked Threads (${threadIds.length})
</div>
```

### 4. Provide Visual Feedback

- Loading spinner while fetching
- Error message if fetch fails
- Empty state if no threads
- Hover effects for interactivity

### 5. Maintain Consistency

Use ThreadManager for all thread rendering:
- Same icons, colors, formatting
- Consistent behavior across app
- Easier maintenance

---

## Summary

**How multiple thread cards render in one Synergy card:**

1. **Storage:** Session stores array of thread IDs in `thread_ids` field
2. **Fetching:** `renderLinkedThreads()` fetches full thread details via API
3. **Mapping:** Each thread object mapped to HTML thread card
4. **Stacking:** All thread cards joined into single HTML string
5. **Layout:** CSS flex column displays cards vertically with 8px gaps
6. **Scrolling:** Container max-height 400px with overflow scroll
7. **Interaction:** Each card clickable and draggable independently

**Key Files:**
- **Rendering:** `business-ai-platform-v2.html` line 30780 (`renderLinkedThreads`)
- **CSS:** `business-ai-platform-v2.html` lines 1674-1750
- **API:** `/api/threads/details` endpoint
- **Database:** `synergy_sessions.thread_ids` (JSON array)

**Result:** Clean, organized display of multiple threads within a single Synergy card!

---

**Last Updated:** November 14, 2025  
**Status:** ✅ PRODUCTION - Working as designed
