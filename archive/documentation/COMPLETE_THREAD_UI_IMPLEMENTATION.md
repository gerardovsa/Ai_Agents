# Complete Thread UI Implementation Plan
**Date:** November 8, 2025  
**Purpose:** Implement all 10 UI integration points + drag-and-drop

---

## ✅ ALIGNMENT WITH YOUR CHECKLIST

Your checklist has **10 points + drag-and-drop**. Here's the complete implementation:

---

## 1️⃣ PRIME AI CHAT HEADER INFO (Lines 7590-7610)

### **Elements Present:**
| Element ID | Purpose | Current Status |
|-----------|---------|----------------|
| `prime-thread-title` | Thread title with edit | ✅ Exists |
| `prime-msg-count` | Message count | ✅ Exists |
| `prime-date` | Last updated date | ✅ Exists |
| `prime-time` | Last updated time | ✅ Exists |
| `prime-thread-tags` | Tags row | ✅ Exists (hidden) |
| `prime-thread-synergy` | Synergy badge | ✅ Exists (hidden) |

### **Update Function:**
```javascript
updatePrimeHeader(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        // Clear header if no thread
        document.getElementById('prime-thread-title').textContent = 'No thread loaded';
        document.getElementById('prime-msg-count').textContent = '0';
        document.getElementById('prime-date').textContent = '--';
        document.getElementById('prime-time').textContent = '--';
        document.getElementById('prime-thread-tags').style.display = 'none';
        document.getElementById('prime-thread-synergy').style.display = 'none';
        return;
    }
    
    // Update title
    document.getElementById('prime-thread-title').textContent = thread.title || 'Untitled';
    
    // Update message count
    document.getElementById('prime-msg-count').textContent = thread.messages.length;
    
    // Update date
    const createdDate = new Date(thread.created);
    document.getElementById('prime-date').textContent = createdDate.toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric'
    });
    
    // Update time
    const updatedDate = new Date(thread.updated || thread.created);
    document.getElementById('prime-time').textContent = updatedDate.toLocaleTimeString('en-US', {
        hour: 'numeric', minute: '2-digit'
    });
    
    // Update tags
    const tagsRow = document.getElementById('prime-thread-tags');
    if (thread.tags && thread.tags.length > 0) {
        tagsRow.innerHTML = thread.tags.map(tag => 
            `<span class="thread-tag-pill">
                <i class="fas fa-tag"></i> ${tag}
                <button onclick="ThreadManager.removeTag('${threadId}', '${tag}')" class="tag-remove-btn">×</button>
            </span>`
        ).join('');
        tagsRow.style.display = 'flex';
    } else {
        tagsRow.style.display = 'none';
    }
    
    // Update Synergy badge
    const synergyRow = document.getElementById('prime-thread-synergy');
    if (thread.synergy_card_id) {
        synergyRow.innerHTML = `
            <div class="synergy-badge" onclick="ThreadManager.copySynergyInfo('${thread.synergy_card_id}', '${thread.synergy_card_name || 'Synergy Session'}')">
                <i class="fas fa-link"></i>
                <span class="synergy-id">${thread.synergy_card_id.slice(0, 8)}...</span>
                <span class="synergy-name">${thread.synergy_card_name || 'Synergy Session'}</span>
                <button onclick="event.stopPropagation(); ThreadManager.unlinkFromSynergy('${threadId}')" class="synergy-unlink-btn">×</button>
            </div>
        `;
        synergyRow.style.display = 'flex';
    } else {
        synergyRow.style.display = 'none';
    }
}
```

### **When to Call:**
✅ After `createThreadWithMetadata()` - Line ~15700  
✅ After `switchThread()` - Line ~14650  
✅ After each message sent - In message handlers  
✅ After `editThreadTitle()` - Line ~15800  
✅ After `addTag()` / `removeTag()` - Tag functions  
✅ After `linkToSynergy()` / `unlinkFromSynergy()` - Synergy functions

---

## 2️⃣ THREAD MODAL (New Chat Modal)

### **Current Location:** Lines 15385-15550

### **Elements:**
- Modal popup with thread creation form
- Title input
- Tags input
- Synergy session dropdown
- Location selector (Prime/Agent)

### **Status:** ✅ WORKING after recent fixes

### **Enhancements Needed:**
```javascript
// In showNewChatModal() - Add thread list display
async showNewChatModal(location = 'prime') {
    // ... existing code ...
    
    // NEW: Show recent threads in modal (optional feature)
    const recentThreadsDiv = document.getElementById('modal-recent-threads');
    if (recentThreadsDiv) {
        const recentThreads = this.threads.slice(0, 5); // Show last 5
        recentThreadsDiv.innerHTML = recentThreads.map(thread => `
            <div class="modal-thread-card" onclick="ThreadManager.switchThread('${thread.id}')">
                <div class="modal-thread-title">${thread.title}</div>
                <div class="modal-thread-meta">
                    ${thread.messages.length} msg · ${new Date(thread.updated).toLocaleDateString()}
                </div>
            </div>
        `).join('');
    }
}
```

---

## 3️⃣ THREAD LIST SIDEBAR (ThreadManager)

### **Current Location:** Lines 15137-15199 (renderThreadList)

### **Status:** ✅ IMPLEMENTED (3-row layout)

### **Enhancements Needed:**
```javascript
renderThreadList() {
    const container = document.getElementById('threadListContainer');
    if (!container) return;
    
    // Filter based on search/filter
    let filteredThreads = this.threads.filter(t => !t.archived);
    
    // Sort by updated date (newest first)
    filteredThreads.sort((a, b) => 
        new Date(b.updated || b.created) - new Date(a.updated || a.created)
    );
    
    // Render each thread card
    container.innerHTML = filteredThreads.map(thread => {
        const active = thread.id === this.currentThreadId ? 'active' : '';
        const messages = thread.messages || [];
        const dateStr = new Date(thread.created).toLocaleDateString('en-US', {
            month: 'short', day: 'numeric'
        });
        
        const agentClass = thread.agent === 'main' ? 'main' : 'agent';
        const agentIcon = thread.agent === 'main' ? 'fa-robot' : 'fa-users';
        const agentLabel = thread.agent === 'main' ? 'Prime' : thread.agent.replace('agent-', 'Agent ');
        
        return `
            <div class="thread-item ${active}" 
                 draggable="true"
                 data-thread-id="${thread.id}"
                 data-synergy-id="${thread.synergy_card_id || ''}"
                 ondragstart="ThreadManager.handleDragStart(event)"
                 ondblclick="ThreadManager.openThreadInPrime('${thread.id}')">
                 
                <!-- ROW 1: Title + Actions -->
                <div class="thread-item-row thread-item-row-1">
                    <span class="thread-item-title-text">${thread.title}</span>
                    <div class="thread-item-actions">
                        <button class="thread-action-btn archive" onclick="event.stopPropagation(); ThreadManager.archiveThread('${thread.id}')">
                            <i class="fas fa-archive"></i>
                        </button>
                        <button class="thread-action-btn delete" onclick="event.stopPropagation(); ThreadManager.deleteThread('${thread.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                        <button class="thread-action-btn rename" onclick="event.stopPropagation(); ThreadManager.startRename('${thread.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                    </div>
                </div>
                
                <!-- ROW 2: Stats + Copy + Tag -->
                <div class="thread-item-row thread-item-row-2">
                    <div class="thread-item-stats">
                        <span><i class="fas fa-comments"></i> ${messages.length}</span>
                        <span><i class="fas fa-calendar"></i> ${dateStr}</span>
                    </div>
                    <button class="thread-copy-id-btn" onclick="event.stopPropagation(); ThreadManager.copyThreadId('${thread.id}')">
                        <i class="fas fa-clipboard"></i> Copy ID
                    </button>
                    <div class="thread-item-agent-tag ${agentClass}">
                        <i class="fas ${agentIcon}"></i> ${agentLabel}
                    </div>
                </div>
                
                <!-- ROW 3: Synergy Link (if linked) -->
                ${thread.synergy_card_id ? `
                    <div class="thread-item-row thread-item-row-3"
                         onclick="event.stopPropagation(); ThreadManager.copySynergyInfo('${thread.synergy_card_id}', '${thread.synergy_card_name || 'Synergy Session'}')">
                        <i class="fas fa-link"></i>
                        <span class="synergy-session-name">${thread.synergy_card_name || 'Synergy Session'}</span>
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
    
    // Show/hide "Start New Chat" button
    if (filteredThreads.length === 0) {
        this.showEmptyState();
    }
}
```

---

## 4️⃣ APPSTATE SYNCHRONIZATION

### **Global State Variables:**
```javascript
const AppState = {
    sessionId: null,          // Current thread ID
    chatMessages: [],         // Current thread messages
    threadTitle: null,        // Current thread title
    threadTags: [],           // Current thread tags
    synergyCardId: null,      // Linked Synergy session
    currentLocation: 'prime'  // prime | agent-1 | agent-2 | agent-3
};
```

### **Sync Function:**
```javascript
syncAppState(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        // Clear state
        AppState.sessionId = null;
        AppState.chatMessages = [];
        AppState.threadTitle = null;
        AppState.threadTags = [];
        AppState.synergyCardId = null;
        return;
    }
    
    // Update state
    AppState.sessionId = thread.id;
    AppState.chatMessages = [...thread.messages]; // Clone array
    AppState.threadTitle = thread.title;
    AppState.threadTags = thread.tags || [];
    AppState.synergyCardId = thread.synergy_card_id;
    AppState.currentLocation = thread.agent || 'main';
    
    console.log('🔄 [AppState] Synced:', AppState.sessionId);
}
```

### **When to Call:**
✅ On thread switch  
✅ After each message  
✅ On thread creation  
✅ On page reload

---

## 5️⃣ MESSAGE COUNT UPDATES

### **Triggers:**
- User sends message → +1
- AI responds → +1
- Load thread history → count all
- Delete message → -1

### **Update Function:**
```javascript
updateMessageCount(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;
    
    const count = thread.messages.length;
    
    // Update Prime header
    if (this.currentThreadId === threadId) {
        document.getElementById('prime-msg-count').textContent = count;
    }
    
    // Update agent header (if in agent)
    if (thread.agent && thread.agent.startsWith('agent-')) {
        const agentId = thread.agent.replace('agent-', '');
        const msgCountEl = document.getElementById(`msg-count-${agentId}`);
        if (msgCountEl) msgCountEl.textContent = count;
    }
    
    // Update sidebar card
    const cardEl = document.querySelector(`[data-thread-id="${threadId}"]`);
    if (cardEl) {
        const statsEl = cardEl.querySelector('.thread-item-stats span:first-child');
        if (statsEl) statsEl.innerHTML = `<i class="fas fa-comments"></i> ${count}`;
    }
}
```

### **Integration Points:**
```javascript
// After sending message in Prime
async sendMessage(message) {
    // ... send message ...
    ThreadManager.updateMessageCount(ThreadManager.currentThreadId);
    ThreadManager.updatePrimeHeader(ThreadManager.currentThreadId);
}

// After AI response
function handleAIResponse(response) {
    // ... process response ...
    ThreadManager.updateMessageCount(ThreadManager.currentThreadId);
    ThreadManager.updatePrimeHeader(ThreadManager.currentThreadId);
}
```

---

## 6️⃣ DATE/TIME UPDATES

### **Format:**
- Date: "Nov 8, 2025"
- Time: "2:45 PM"

### **Update Function:**
```javascript
updateDateTime(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;
    
    const createdDate = new Date(thread.created);
    const updatedDate = new Date(thread.updated || thread.created);
    
    // Format date
    const dateStr = createdDate.toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric'
    });
    
    // Format time
    const timeStr = updatedDate.toLocaleTimeString('en-US', {
        hour: 'numeric', minute: '2-digit'
    });
    
    // Update Prime header
    if (this.currentThreadId === threadId) {
        document.getElementById('prime-date').textContent = dateStr;
        document.getElementById('prime-time').textContent = timeStr;
    }
    
    // Update agent header
    if (thread.agent && thread.agent.startsWith('agent-')) {
        const agentId = thread.agent.replace('agent-', '');
        const dateEl = document.getElementById(`thread-date-${agentId}`);
        const timeEl = document.getElementById(`thread-time-${agentId}`);
        if (dateEl) dateEl.textContent = dateStr;
        if (timeEl) timeEl.textContent = timeStr;
    }
}
```

### **Real-time Time Updates:**
```javascript
// Start timer to update "updated_at" display every 30 seconds
setInterval(() => {
    if (ThreadManager.currentThreadId) {
        ThreadManager.updateDateTime(ThreadManager.currentThreadId);
    }
}, 30000); // Every 30 seconds
```

---

## 7️⃣ TAGS DISPLAY

### **Functionality:**
- Show/hide `#prime-thread-tags` row
- Render tag pills with icons
- Allow tag editing (inline)

### **Update Function:**
```javascript
updateTagsDisplay(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;
    
    const tagsRow = document.getElementById('prime-thread-tags');
    if (!tagsRow) return;
    
    if (thread.tags && thread.tags.length > 0) {
        tagsRow.innerHTML = thread.tags.map(tag => `
            <span class="thread-tag-pill">
                <i class="fas fa-tag"></i> ${tag}
                <button onclick="ThreadManager.removeTag('${threadId}', '${tag}')" class="tag-remove-btn">×</button>
            </span>
        `).join('') + `
            <button onclick="ThreadManager.showAddTagModal('${threadId}')" class="tag-add-btn">
                <i class="fas fa-plus"></i> Add Tag
            </button>
        `;
        tagsRow.style.display = 'flex';
    } else {
        tagsRow.innerHTML = `
            <button onclick="ThreadManager.showAddTagModal('${threadId}')" class="tag-add-btn">
                <i class="fas fa-plus"></i> Add Tag
            </button>
        `;
        tagsRow.style.display = 'flex';
    }
}
```

### **Add Tag Function:**
```javascript
async addTag(threadId, tag) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;
    
    if (!thread.tags) thread.tags = [];
    if (!thread.tags.includes(tag)) {
        thread.tags.push(tag);
        
        // Save to backend
        await this.saveThreadToBackend(thread);
        
        // Update UI
        this.updateTagsDisplay(threadId);
        this.renderThreadList(); // Refresh sidebar
    }
}
```

### **Remove Tag Function:**
```javascript
async removeTag(threadId, tag) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;
    
    thread.tags = thread.tags.filter(t => t !== tag);
    
    // Save to backend
    await this.saveThreadToBackend(thread);
    
    // Update UI
    this.updateTagsDisplay(threadId);
    this.renderThreadList(); // Refresh sidebar
}
```

---

## 8️⃣ SYNERGY INTEGRATION

### **Elements:**
- `#prime-thread-synergy` - Badge row
- Badge shows session ID (truncated)
- Click to open Synergy session
- Unlink button (×)

### **Update Function:**
```javascript
updateSynergyDisplay(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;
    
    const synergyRow = document.getElementById('prime-thread-synergy');
    if (!synergyRow) return;
    
    if (thread.synergy_card_id) {
        synergyRow.innerHTML = `
            <div class="synergy-badge" onclick="ThreadManager.openSynergySession('${thread.synergy_card_id}')">
                <i class="fas fa-link"></i>
                <span class="synergy-id">${thread.synergy_card_id.slice(0, 8)}...</span>
                <span class="synergy-name">${thread.synergy_card_name || 'Synergy Session'}</span>
                <button onclick="event.stopPropagation(); ThreadManager.unlinkFromSynergy('${threadId}')" class="synergy-unlink-btn">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        synergyRow.style.display = 'flex';
    } else {
        synergyRow.innerHTML = `
            <button onclick="ThreadManager.showLinkSynergyModal('${threadId}')" class="synergy-link-btn">
                <i class="fas fa-link"></i> Link to Synergy Session
            </button>
        `;
        synergyRow.style.display = 'none'; // Hide if not linked
    }
}
```

### **Link to Synergy:**
```javascript
async linkToSynergy(threadId, synergyCardId, synergyCardName) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;
    
    thread.synergy_card_id = synergyCardId;
    thread.synergy_card_name = synergyCardName;
    
    // Save to backend
    await this.saveThreadToBackend(thread);
    
    // Update UI
    this.updateSynergyDisplay(threadId);
    this.renderThreadList(); // Refresh sidebar (shows Row 3)
}
```

### **Unlink from Synergy:**
```javascript
async unlinkFromSynergy(threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) return;
    
    thread.synergy_card_id = null;
    thread.synergy_card_name = null;
    
    // Save to backend
    await this.saveThreadToBackend(thread);
    
    // Update UI
    this.updateSynergyDisplay(threadId);
    this.renderThreadList(); // Refresh sidebar (hides Row 3)
}
```

---

## 9️⃣ AGENT COLUMNS (Multi-Agent)

### **Similar to Prime, but for each agent (1, 2, 3)**

### **Update Function:**
```javascript
updateAgentHeader(agentId, threadId) {
    const thread = this.threads.find(t => t.id === threadId);
    if (!thread) {
        // Clear agent header
        const headerEl = document.getElementById(`thread-info-${agentId}`);
        if (headerEl) headerEl.innerHTML = '<div class="no-thread-message">No thread assigned</div>';
        return;
    }
    
    const headerEl = document.getElementById(`thread-info-${agentId}`);
    if (!headerEl) return;
    
    const createdDate = new Date(thread.created);
    const updatedDate = new Date(thread.updated || thread.created);
    
    headerEl.innerHTML = `
        <div class="agent-thread-title" id="thread-title-${agentId}">${thread.title || 'Untitled'}</div>
        <div class="agent-thread-meta">
            <span><i class="fas fa-comments"></i> <span id="msg-count-${agentId}">${thread.messages.length}</span> msg</span>
            <span><i class="fas fa-calendar"></i> <span id="thread-date-${agentId}">${createdDate.toLocaleDateString()}</span></span>
            <span><i class="fas fa-clock"></i> <span id="thread-time-${agentId}">${updatedDate.toLocaleTimeString()}</span></span>
        </div>
        ${thread.tags && thread.tags.length > 0 ? `
            <div class="agent-thread-tags">
                ${thread.tags.map(tag => `<span class="thread-tag-pill"><i class="fas fa-tag"></i> ${tag}</span>`).join('')}
            </div>
        ` : ''}
        ${thread.synergy_card_id ? `
            <div class="agent-synergy-badge" onclick="ThreadManager.openSynergySession('${thread.synergy_card_id}')">
                <i class="fas fa-link"></i> ${thread.synergy_card_name || 'Synergy Session'}
            </div>
        ` : ''}
    `;
}
```

### **When to Call:**
✅ After `sendToAgent()` (thread assignment)  
✅ After message sent in agent  
✅ After AI response in agent  
✅ On agent column load

---

## 🔟 DATABASE SYNCHRONIZATION

### **Tables:**
- `threads` - Main thread data
- `messages` - Individual messages
- `thread_assignments` - Location assignments

### **Critical Fields:**
```sql
threads:
- id (UUID)
- thread_slug (for URLs)
- name (title)
- created_at
- updated_at
- tags (JSON array)
- synergy_card_id (foreign key)
- location (prime | agent-1 | agent-2 | agent-3)

messages:
- thread_id (foreign key)
- role (user | assistant)
- content (text)
- created_at
```

### **Save Function:**
```javascript
async saveThreadToBackend(thread) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/threads/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: (window.UserAuth.user && (window.UserAuth.user.id || window.UserAuth.user.user_id)) || 1,
                thread_id: thread.id,
                title: thread.title,
                messages: JSON.stringify(thread.messages),
                tags: JSON.stringify(thread.tags || []),
                synergy_card_id: thread.synergy_card_id,
                location: thread.agent || 'main',
                archived: thread.archived || false,
                updated: new Date().toISOString()
            })
        });
        
        const data = await response.json();
        if (data.success) {
            console.log('✅ [SAVE] Thread saved to backend');
            // Update local thread object
            thread.updated = new Date().toISOString();
            return true;
        }
    } catch (error) {
        console.error('[ERROR] Failed to save thread:', error);
        return false;
    }
}
```

---

## 1️⃣1️⃣ DRAG AND DROP FUNCTIONALITY

### **Status:** ⚠️ PARTIAL (only dragstart implemented)

### **Complete Implementation:**

#### **1. Make Thread Cards Draggable:**
```javascript
// Already implemented in renderThreadList() - Line 15463
draggable="true"
ondragstart="ThreadManager.handleDragStart(event)"
```

#### **2. Handle Drag Start:**
```javascript
handleDragStart(event) {
    const threadId = event.currentTarget.dataset.threadId;
    event.dataTransfer.setData('text/plain', threadId);
    event.dataTransfer.effectAllowed = 'move';
    
    // Add dragging class
    event.currentTarget.classList.add('dragging');
    
    console.log('[DRAG] Started dragging thread:', threadId);
}
```

#### **3. Add Drop Zones (Agent Columns + Prime):**
```javascript
// In createAgentColumn() - Add to agent chat area
function setupDropZone(agentId) {
    const chatArea = document.querySelector(`#agent-${agentId} .agent-chat-messages`);
    if (!chatArea) return;
    
    chatArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        chatArea.classList.add('drag-over');
    });
    
    chatArea.addEventListener('dragleave', (e) => {
        chatArea.classList.remove('drag-over');
    });
    
    chatArea.addEventListener('drop', (e) => {
        e.preventDefault();
        chatArea.classList.remove('drag-over');
        
        const threadId = e.dataTransfer.getData('text/plain');
        ThreadManager.sendToAgent(threadId, `agent-${agentId}`);
        
        console.log(`[DROP] Thread ${threadId} dropped on Agent ${agentId}`);
    });
}

// Call for each agent
setupDropZone(1);
setupDropZone(2);
setupDropZone(3);

// Also add to Prime chat area
const primeChatArea = document.getElementById('ai-chat-messages');
if (primeChatArea) {
    primeChatArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        primeChatArea.classList.add('drag-over');
    });
    
    primeChatArea.addEventListener('dragleave', (e) => {
        primeChatArea.classList.remove('drag-over');
    });
    
    primeChatArea.addEventListener('drop', (e) => {
        e.preventDefault();
        primeChatArea.classList.remove('drag-over');
        
        const threadId = e.dataTransfer.getData('text/plain');
        ThreadManager.sendToAgent(threadId, 'main');
        
        console.log(`[DROP] Thread ${threadId} dropped on Prime`);
    });
}
```

#### **4. Visual Feedback CSS:**
```css
.thread-item.dragging {
    opacity: 0.5;
    transform: scale(0.95);
}

.drag-over {
    background: rgba(88, 166, 255, 0.1);
    border: 2px dashed var(--accent-primary);
    box-shadow: 0 0 20px rgba(88, 166, 255, 0.3);
}

.thread-item:hover {
    cursor: grab;
}

.thread-item.dragging:hover {
    cursor: grabbing;
}
```

---

## 🚀 IMPLEMENTATION ORDER

### **Phase 1: Core Updates (30 min)**
1. Add `updatePrimeHeader()` function
2. Add `updateAgentHeader()` function
3. Add `syncAppState()` function
4. Add `updateMessageCount()` function

### **Phase 2: Enhanced Features (20 min)**
5. Add `updateTagsDisplay()` function
6. Add `updateSynergyDisplay()` function
7. Add `updateDateTime()` function
8. Add real-time time updates

### **Phase 3: Integration (30 min)**
9. Add update calls after thread creation
10. Add update calls after message sent
11. Add update calls after thread operations
12. Test all integration points

### **Phase 4: Drag-and-Drop (20 min)**
13. Add drop zone event listeners
14. Add visual feedback CSS
15. Test drag-and-drop functionality

### **Total Time: ~2 hours**

---

## ✅ TESTING CHECKLIST

- [ ] Create thread → Prime header updates
- [ ] Send message → Message count updates
- [ ] Send 5 messages → Count shows "5"
- [ ] Switch threads → Header updates correctly
- [ ] Assign to Agent 2 → Agent header updates
- [ ] Send message in Agent → Agent header updates
- [ ] Add tag → Tags row appears
- [ ] Remove tag → Tag disappears
- [ ] Link Synergy → Synergy badge appears
- [ ] Unlink Synergy → Synergy badge disappears
- [ ] Drag thread to Agent → Drops correctly
- [ ] Drag thread to Prime → Drops correctly
- [ ] Refresh page → Thread persists with all data
- [ ] Collapse agent → Vertical bar shows info
- [ ] Expand agent → Full header shows

---

**END OF IMPLEMENTATION PLAN**
