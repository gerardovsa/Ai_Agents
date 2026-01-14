# 💬 Messaging Sidebar - Complete Design Specification

**Date:** December 17, 2025  
**Integration:** Realtime Messaging System

---

## 🎯 System Analysis

### Existing Infrastructure Found:

**1. Display Name & Device Detection** ([synergy-realtime.js](UI/shared/js/synergy-realtime.js#L506-L570))
```javascript
// Already implemented by another AI:
- sessionDisplayName: Per-session identity (stored in localStorage)
- _getUserName(): Gets username from UserAuth
- _getDeviceInfo(): Returns device emoji (📱 iPhone, 💻 Windows, etc.)
- Multi-device tracking: Same user on different devices differentiated
```

**2. Toast Notification System** ([enhanced-toast-notifications.js](UI/shared/js/enhanced-toast-notifications.js))
```javascript
// Already implemented:
- Bottom-left toast display
- Quick reply textarea
- Quick reactions (thumbs up, check, heart, etc.)
- Integrates with notification sidebar
- Auto-marks messages as read
```

**3. Existing Notification System** ([business-ai-platform-v2.html](UI/business-ai-platform-v2.html#L23915))
```javascript
// Generic notifications:
- showNotification(message, type, duration)
- Types: success, error, warning, info
- Auto-dismiss after duration
```

---

## 🏗️ Messaging Sidebar Architecture

### **Design Philosophy:**
The messaging sidebar is the **persistent message hub** while toasts are **instant notifications**.

```
┌────────────────────────────────────────┐
│         MESSAGING FLOW                 │
├────────────────────────────────────────┤
│                                        │
│  1. Message Arrives (WebSocket)        │
│          ↓                             │
│  2. Toast Appears (Bottom-Left)        │
│     - Quick glimpse                    │
│     - Quick reply option               │
│     - Auto-dismissible                 │
│          ↓                             │
│  3. Message Saved to Sidebar           │
│     - Persistent history               │
│     - Full conversation view           │
│     - Search & filter                  │
│          ↓                             │
│  4. User Responds                      │
│     - From toast (quick reply)         │
│     - OR from sidebar (full chat)      │
│                                        │
└────────────────────────────────────────┘
```

---

## 📐 Sidebar Layout

### **Location:** Right side of screen (next to account sidebar)

### **Toggle Button:** 
Add to multi-agent-header-right (line 18563):
```html
<button class="multi-agent-action-btn" 
        onclick="MessagingSidebar.toggle()" 
        id="messaging-sidebar-toggle"
        title="Messages">
    <i class="fas fa-comments"></i>
    <span class="message-badge" id="unread-message-count" style="display: none;">0</span>
</button>
```

### **Sidebar Structure:**

```html
<!-- Messaging Sidebar -->
<div id="messaging-sidebar" class="messaging-sidebar" style="display: none;">
    
    <!-- Header -->
    <div class="messaging-sidebar-header">
        <div class="messaging-header-left">
            <i class="fas fa-comments"></i>
            <h3>Messages</h3>
        </div>
        <div class="messaging-header-right">
            <button class="messaging-icon-btn" 
                    onclick="MessagingSidebar.toggleCompose()" 
                    title="New message">
                <i class="fas fa-edit"></i>
            </button>
            <button class="messaging-icon-btn" 
                    onclick="MessagingSidebar.markAllRead()" 
                    title="Mark all read">
                <i class="fas fa-check-double"></i>
            </button>
            <button class="messaging-icon-btn" 
                    onclick="MessagingSidebar.close()" 
                    title="Close">
                <i class="fas fa-times"></i>
            </button>
        </div>
    </div>

    <!-- Tabs -->
    <div class="messaging-tabs">
        <button class="messaging-tab active" 
                data-tab="conversations" 
                onclick="MessagingSidebar.switchTab('conversations')">
            <i class="fas fa-inbox"></i>
            <span>Conversations</span>
            <span class="tab-count" id="conversations-count">0</span>
        </button>
        <button class="messaging-tab" 
                data-tab="online-users" 
                onclick="MessagingSidebar.switchTab('online-users')">
            <i class="fas fa-users"></i>
            <span>Online</span>
            <span class="tab-count" id="online-users-count">0</span>
        </button>
        <button class="messaging-tab" 
                data-tab="broadcasts" 
                onclick="MessagingSidebar.switchTab('broadcasts')">
            <i class="fas fa-bullhorn"></i>
            <span>Broadcasts</span>
            <span class="tab-count" id="broadcasts-count">0</span>
        </button>
    </div>

    <!-- Search & Filter -->
    <div class="messaging-search">
        <div class="messaging-search-input-wrapper">
            <i class="fas fa-search"></i>
            <input type="text" 
                   id="messaging-search-input" 
                   placeholder="Search messages..."
                   oninput="MessagingSidebar.search(this.value)">
        </div>
        <button class="messaging-filter-btn" 
                onclick="MessagingSidebar.toggleFilters()" 
                title="Filters">
            <i class="fas fa-filter"></i>
        </button>
    </div>

    <!-- Filter Panel (hidden by default) -->
    <div id="messaging-filters" class="messaging-filters" style="display: none;">
        <label>
            <input type="checkbox" id="filter-unread" onchange="MessagingSidebar.applyFilters()">
            Unread only
        </label>
        <label>
            <input type="checkbox" id="filter-direct" checked onchange="MessagingSidebar.applyFilters()">
            Direct messages
        </label>
        <label>
            <input type="checkbox" id="filter-broadcast" checked onchange="MessagingSidebar.applyFilters()">
            Broadcasts
        </label>
        <select id="filter-time" onchange="MessagingSidebar.applyFilters()">
            <option value="all">All time</option>
            <option value="today">Today</option>
            <option value="week">This week</option>
            <option value="month">This month</option>
        </select>
    </div>

    <!-- Content Area -->
    <div class="messaging-content">
        
        <!-- TAB 1: Conversations List -->
        <div id="tab-conversations" class="messaging-tab-content active">
            <div class="messaging-conversations-list" id="conversations-list">
                <!-- Populated dynamically with conversation items -->
                <!-- Example structure:
                <div class="conversation-item unread" data-conversation-id="conv_123">
                    <div class="conversation-avatar">
                        <img src="..." alt="User">
                        <span class="device-badge">💻</span>
                    </div>
                    <div class="conversation-info">
                        <div class="conversation-header">
                            <span class="conversation-name">John Doe (Windows)</span>
                            <span class="conversation-time">2 min ago</span>
                        </div>
                        <div class="conversation-preview">
                            <span class="conversation-last-message">Hey, can you review...</span>
                            <span class="unread-badge">3</span>
                        </div>
                    </div>
                </div>
                -->
            </div>
            
            <!-- Empty State -->
            <div class="messaging-empty-state" id="conversations-empty" style="display: none;">
                <i class="fas fa-inbox"></i>
                <p>No messages yet</p>
                <button onclick="MessagingSidebar.switchTab('online-users')">
                    Start a conversation
                </button>
            </div>
        </div>

        <!-- TAB 2: Online Users List -->
        <div id="tab-online-users" class="messaging-tab-content">
            <div class="online-users-list" id="online-users-list">
                <!-- Populated dynamically with online users -->
                <!-- Example structure:
                <div class="online-user-item" data-user-id="2">
                    <div class="online-user-avatar">
                        <img src="..." alt="User">
                        <span class="online-indicator"></span>
                    </div>
                    <div class="online-user-info">
                        <div class="online-user-name">Sarah Smith</div>
                        <div class="online-user-device">
                            💻 Windows • Viewing Alpha-3
                        </div>
                    </div>
                    <button class="online-user-message-btn" 
                            onclick="MessagingSidebar.startConversation(2)">
                        <i class="fas fa-comment"></i>
                    </button>
                </div>
                -->
            </div>
        </div>

        <!-- TAB 3: Broadcasts List -->
        <div id="tab-broadcasts" class="messaging-tab-content">
            <div class="broadcasts-list" id="broadcasts-list">
                <!-- Populated dynamically with broadcast messages -->
                <!-- Example structure:
                <div class="broadcast-item" data-message-id="msg_456">
                    <div class="broadcast-header">
                        <i class="fas fa-bullhorn"></i>
                        <span class="broadcast-sender">Admin</span>
                        <span class="broadcast-time">10 min ago</span>
                    </div>
                    <div class="broadcast-message">
                        System maintenance scheduled for tonight at 10 PM EST
                    </div>
                    <div class="broadcast-actions">
                        <button onclick="MessagingSidebar.acknowledgeBroadcast('msg_456')">
                            <i class="fas fa-check"></i> Acknowledge
                        </button>
                    </div>
                </div>
                -->
            </div>
        </div>
    </div>

    <!-- Compose Panel (slides in from bottom when activated) -->
    <div id="messaging-compose-panel" class="messaging-compose-panel" style="display: none;">
        <div class="messaging-compose-header">
            <span>New Message</span>
            <button onclick="MessagingSidebar.closeCompose()">
                <i class="fas fa-times"></i>
            </button>
        </div>
        
        <div class="messaging-compose-to">
            <label>To:</label>
            <select id="messaging-compose-recipient" onchange="MessagingSidebar.updateRecipient()">
                <option value="">Select recipient...</option>
                <option value="broadcast">📢 Broadcast to All Users</option>
                <optgroup label="Online Users" id="compose-online-users">
                    <!-- Populated dynamically -->
                </optgroup>
            </select>
        </div>
        
        <textarea id="messaging-compose-text" 
                  placeholder="Type your message..." 
                  rows="4"></textarea>
        
        <div class="messaging-compose-actions">
            <button class="btn-secondary" onclick="MessagingSidebar.closeCompose()">
                Cancel
            </button>
            <button class="btn-primary" onclick="MessagingSidebar.sendComposedMessage()">
                <i class="fas fa-paper-plane"></i> Send
            </button>
        </div>
    </div>

    <!-- Conversation View (slides in when conversation opened) -->
    <div id="messaging-conversation-view" class="messaging-conversation-view" style="display: none;">
        <div class="messaging-conversation-header">
            <button class="back-btn" onclick="MessagingSidebar.closeConversation()">
                <i class="fas fa-arrow-left"></i>
            </button>
            <div class="conversation-user-info">
                <div class="conversation-user-avatar">
                    <img src="..." alt="User" id="conv-user-avatar">
                    <span class="device-badge" id="conv-device-badge">💻</span>
                </div>
                <div>
                    <div class="conversation-user-name" id="conv-user-name">John Doe</div>
                    <div class="conversation-user-status" id="conv-user-status">
                        <span class="online-indicator"></span> Online • Windows
                    </div>
                </div>
            </div>
            <button class="messaging-icon-btn" 
                    onclick="MessagingSidebar.toggleConversationOptions()" 
                    title="Options">
                <i class="fas fa-ellipsis-v"></i>
            </button>
        </div>

        <div class="messaging-conversation-messages" id="conversation-messages">
            <!-- Populated dynamically with message bubbles -->
            <!-- Example structure:
            <div class="message-bubble received">
                <div class="message-content">Hello!</div>
                <div class="message-meta">
                    <span class="message-time">2:30 PM</span>
                    <span class="message-status read">
                        <i class="fas fa-check-double"></i>
                    </span>
                </div>
            </div>
            
            <div class="message-bubble sent">
                <div class="message-content">Hi, how can I help?</div>
                <div class="message-meta">
                    <span class="message-time">2:31 PM</span>
                    <span class="message-status delivered">
                        <i class="fas fa-check"></i>
                    </span>
                </div>
            </div>
            -->
        </div>

        <div class="messaging-conversation-input">
            <textarea id="conversation-input" 
                      placeholder="Type a message..." 
                      rows="2"
                      onkeydown="MessagingSidebar.handleConversationKeydown(event)"></textarea>
            <button onclick="MessagingSidebar.sendConversationMessage()">
                <i class="fas fa-paper-plane"></i>
            </button>
        </div>
    </div>

</div>
```

---

## 🎨 CSS Styling

```css
/* Messaging Sidebar */
.messaging-sidebar {
    position: fixed;
    top: 0;
    right: 0;
    width: 380px;
    height: 100vh;
    background: var(--bg-primary);
    border-left: 1px solid var(--border-default);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    box-shadow: -4px 0 20px rgba(0, 0, 0, 0.3);
    animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* Header */
.messaging-sidebar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid var(--border-default);
}

.messaging-header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.messaging-header-left i {
    font-size: 20px;
    color: var(--accent-primary);
}

.messaging-header-left h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
}

.messaging-header-right {
    display: flex;
    gap: 8px;
}

.messaging-icon-btn {
    width: 32px;
    height: 32px;
    border-radius: 6px;
    border: none;
    background: var(--bg-secondary);
    color: var(--text-secondary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.messaging-icon-btn:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
}

/* Tabs */
.messaging-tabs {
    display: flex;
    border-bottom: 1px solid var(--border-default);
    background: var(--bg-secondary);
}

.messaging-tab {
    flex: 1;
    padding: 12px 8px;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    font-size: 13px;
    position: relative;
    transition: all 0.2s;
}

.messaging-tab:hover {
    background: var(--bg-tertiary);
}

.messaging-tab.active {
    color: var(--accent-primary);
    background: var(--bg-primary);
}

.messaging-tab.active::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--accent-primary);
}

.tab-count {
    background: var(--accent-secondary);
    color: white;
    font-size: 11px;
    padding: 2px 6px;
    border-radius: 10px;
    min-width: 18px;
    text-align: center;
}

/* Search */
.messaging-search {
    padding: 12px;
    display: flex;
    gap: 8px;
    border-bottom: 1px solid var(--border-default);
}

.messaging-search-input-wrapper {
    flex: 1;
    position: relative;
}

.messaging-search-input-wrapper i {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-tertiary);
}

#messaging-search-input {
    width: 100%;
    padding: 8px 12px 8px 36px;
    border: 1px solid var(--border-default);
    border-radius: 6px;
    background: var(--bg-secondary);
    color: var(--text-primary);
    font-size: 14px;
}

/* Filters */
.messaging-filters {
    padding: 12px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-default);
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    font-size: 13px;
}

.messaging-filters label {
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Content Area */
.messaging-content {
    flex: 1;
    overflow-y: auto;
    position: relative;
}

.messaging-tab-content {
    display: none;
}

.messaging-tab-content.active {
    display: block;
}

/* Conversation Item */
.conversation-item {
    display: flex;
    gap: 12px;
    padding: 12px;
    border-bottom: 1px solid var(--border-default);
    cursor: pointer;
    transition: background 0.2s;
}

.conversation-item:hover {
    background: var(--bg-secondary);
}

.conversation-item.unread {
    background: rgba(74, 158, 255, 0.05);
}

.conversation-avatar {
    position: relative;
    width: 48px;
    height: 48px;
}

.conversation-avatar img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
}

.device-badge {
    position: absolute;
    bottom: -2px;
    right: -2px;
    font-size: 14px;
    background: var(--bg-primary);
    border-radius: 50%;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.conversation-info {
    flex: 1;
    min-width: 0;
}

.conversation-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 4px;
}

.conversation-name {
    font-weight: 600;
    font-size: 14px;
}

.conversation-time {
    font-size: 12px;
    color: var(--text-tertiary);
}

.conversation-preview {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.conversation-last-message {
    color: var(--text-secondary);
    font-size: 13px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.unread-badge {
    background: var(--accent-primary);
    color: white;
    font-size: 11px;
    padding: 2px 6px;
    border-radius: 10px;
    min-width: 18px;
    text-align: center;
}

/* Online Users */
.online-user-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border-bottom: 1px solid var(--border-default);
}

.online-user-avatar {
    position: relative;
    width: 40px;
    height: 40px;
}

.online-indicator {
    position: absolute;
    bottom: 0;
    right: 0;
    width: 12px;
    height: 12px;
    background: #4CAF50;
    border: 2px solid var(--bg-primary);
    border-radius: 50%;
}

.online-user-info {
    flex: 1;
}

.online-user-name {
    font-weight: 500;
    font-size: 14px;
}

.online-user-device {
    font-size: 12px;
    color: var(--text-secondary);
}

.online-user-message-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: none;
    background: var(--accent-primary);
    color: white;
    cursor: pointer;
}

/* Broadcast Item */
.broadcast-item {
    padding: 16px;
    border-bottom: 1px solid var(--border-default);
}

.broadcast-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}

.broadcast-header i {
    color: var(--accent-secondary);
}

.broadcast-sender {
    font-weight: 600;
    font-size: 13px;
}

.broadcast-time {
    margin-left: auto;
    font-size: 12px;
    color: var(--text-tertiary);
}

.broadcast-message {
    padding: 12px;
    background: var(--bg-secondary);
    border-radius: 8px;
    margin-bottom: 12px;
    font-size: 14px;
}

/* Conversation View */
.messaging-conversation-view {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--bg-primary);
    display: flex;
    flex-direction: column;
    animation: slideInRight 0.3s ease-out;
}

.messaging-conversation-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border-bottom: 1px solid var(--border-default);
}

.conversation-user-info {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
}

.messaging-conversation-messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.message-bubble {
    max-width: 70%;
    padding: 10px 14px;
    border-radius: 12px;
    font-size: 14px;
    animation: messageSlideIn 0.2s ease-out;
}

@keyframes messageSlideIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.message-bubble.received {
    align-self: flex-start;
    background: var(--bg-secondary);
}

.message-bubble.sent {
    align-self: flex-end;
    background: var(--accent-primary);
    color: white;
}

.message-meta {
    display: flex;
    justify-content: space-between;
    margin-top: 4px;
    font-size: 11px;
    opacity: 0.7;
}

.messaging-conversation-input {
    display: flex;
    gap: 8px;
    padding: 12px;
    border-top: 1px solid var(--border-default);
}

.messaging-conversation-input textarea {
    flex: 1;
    padding: 10px;
    border: 1px solid var(--border-default);
    border-radius: 8px;
    background: var(--bg-secondary);
    color: var(--text-primary);
    resize: none;
    font-family: inherit;
}

.messaging-conversation-input button {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: none;
    background: var(--accent-primary);
    color: white;
    cursor: pointer;
}

/* Empty State */
.messaging-empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    text-align: center;
    color: var(--text-secondary);
}

.messaging-empty-state i {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
}

/* Message Badge on Toggle Button */
.message-badge {
    position: absolute;
    top: -4px;
    right: -4px;
    background: #ff4444;
    color: white;
    font-size: 11px;
    padding: 2px 6px;
    border-radius: 10px;
    min-width: 18px;
    text-align: center;
}
```

---

## 🔧 JavaScript Implementation

### **Core Module:**

```javascript
window.MessagingSidebar = {
    isOpen: false,
    currentTab: 'conversations',
    conversations: new Map(),
    activeConversation: null,
    unreadCount: 0,
    
    init() {
        // Initialize after WebSocket connects
        if (typeof SynergyRealtime !== 'undefined') {
            this.setupWebSocketListeners();
        }
        
        // Load conversation history from database
        this.loadConversationHistory();
        
        // Update online users list
        this.updateOnlineUsers();
    },
    
    setupWebSocketListeners() {
        // Listen for new messages
        window.addEventListener('synergy:direct_message', (e) => {
            this.handleIncomingMessage(e.detail, 'direct');
        });
        
        window.addEventListener('synergy:broadcast_message', (e) => {
            this.handleIncomingMessage(e.detail, 'broadcast');
        });
        
        // Listen for user presence changes
        SynergyRealtime.socket.on('user_joined', (data) => {
            this.updateOnlineUsers();
        });
        
        SynergyRealtime.socket.on('user_session_left', (data) => {
            this.updateOnlineUsers();
        });
    },
    
    toggle() {
        const sidebar = document.getElementById('messaging-sidebar');
        this.isOpen = !this.isOpen;
        sidebar.style.display = this.isOpen ? 'flex' : 'none';
        
        if (this.isOpen) {
            this.refreshContent();
        }
    },
    
    close() {
        this.isOpen = false;
        document.getElementById('messaging-sidebar').style.display = 'none';
    },
    
    switchTab(tabName) {
        this.currentTab = tabName;
        
        // Update tab buttons
        document.querySelectorAll('.messaging-tab').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });
        
        // Update content
        document.querySelectorAll('.messaging-tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `tab-${tabName}`);
        });
        
        // Load content
        this.loadTabContent(tabName);
    },
    
    handleIncomingMessage(messageData, type) {
        // 1. Add to conversation history
        this.addMessageToConversation(messageData, type);
        
        // 2. Update unread count
        if (type === 'direct') {
            this.unreadCount++;
            this.updateUnreadBadge();
        }
        
        // 3. Refresh UI if sidebar is open
        if (this.isOpen) {
            this.refreshConversationsList();
        }
        
        // 4. Toast notification handled by EnhancedToast (already integrated)
    },
    
    startConversation(userId) {
        // Open conversation view with this user
        this.activeConversation = userId;
        this.loadConversation(userId);
        document.getElementById('messaging-conversation-view').style.display = 'flex';
    },
    
    sendConversationMessage() {
        const input = document.getElementById('conversation-input');
        const message = input.value.trim();
        
        if (!message || !this.activeConversation) return;
        
        // Send via WebSocket
        SynergyRealtime.sendDirectMessage(this.activeConversation, message);
        
        // Add to UI immediately (optimistic update)
        this.addMessageBubble(message, 'sent');
        
        // Clear input
        input.value = '';
    },
    
    updateUnreadBadge() {
        const badge = document.getElementById('unread-message-count');
        badge.textContent = this.unreadCount;
        badge.style.display = this.unreadCount > 0 ? 'block' : 'none';
    },
    
    markAllRead() {
        this.conversations.forEach((conv) => {
            conv.messages.forEach(msg => {
                if (!msg.read && msg.from_user_id !== SynergyRealtime._getUserId()) {
                    this.markMessageRead(msg.message_id);
                }
            });
        });
        
        this.unreadCount = 0;
        this.updateUnreadBadge();
        this.refreshConversationsList();
    },
    
    markMessageRead(messageId) {
        if (SynergyRealtime.isConnected()) {
            SynergyRealtime.socket.emit('mark_message_read', {
                message_id: messageId,
                user_id: SynergyRealtime._getUserId()
            });
        }
    }
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    MessagingSidebar.init();
});
```

---

## 🔄 Integration with Existing Systems

### **1. Toast Notifications**
- **Keep toasts for instant alerts** (already working)
- **Sidebar stores full history** (persistent)
- **Toast "quick reply" sends via `SynergyRealtime.sendDirectMessage()`**
- **Both systems share same WebSocket events**

### **2. Display Names & Devices**
```javascript
// Use existing infrastructure from synergy-realtime.js
const displayName = SynergyRealtime.sessionDisplayName;  // Per-session identity
const device = SynergyRealtime._getDeviceInfo();         // Device emoji
const userName = SynergyRealtime._getUserName();         // Username from UserAuth
```

### **3. Database Integration**
```javascript
// Load message history on sidebar open
async loadConversationHistory() {
    const response = await fetch('/api/messages/history', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    });
    
    const data = await response.json();
    this.conversations = new Map(data.conversations.map(c => [c.user_id, c]));
    this.refreshConversationsList();
}
```

---

## 📊 Data Flow

```
USER A                          WEBSOCKET                     USER B
  │                                │                            │
  │ Types message                  │                            │
  │ Clicks "Send" in sidebar       │                            │
  ├────────────────────────────────►                            │
  │ sendDirectMessage()            │                            │
  │                                ├────────────────────────────►
  │                                │ direct_message_received    │
  │                                │                            │
  │                                │          1. Toast appears  │
  │                                │             (bottom-left)  │
  │                                │                            │
  │                                │          2. Sidebar gets   │
  │                                │             message (if open)
  │                                │                            │
  │                                │          3. Unread badge   │
  │                                │             increments     │
  │                                │                            │
  │                                │          User clicks       │
  │                                │          "Quick Reply"     │
  │                                │          in toast          │
  │                                ◄────────────────────────────┤
  │                                │ sendDirectMessage()        │
  ◄────────────────────────────────┤                            │
  │ Toast appears                  │                            │
  │ + Sidebar updates              │                            │
```

---

## 🎯 Key Features Summary

### **Messaging Sidebar Contains:**

1. **Conversations Tab**
   - List of all direct message conversations
   - Unread count badges
   - Last message preview
   - Device indicators (💻 Windows, 📱 iPhone)
   - Click to open full conversation view

2. **Online Users Tab**
   - Real-time list of connected users
   - Online indicators (green dot)
   - Device info (from `_getDeviceInfo()`)
   - Current agent they're viewing
   - "Message" button to start conversation

3. **Broadcasts Tab**
   - System-wide announcements
   - Important notifications
   - Acknowledgement tracking

4. **Conversation View** (slides in when conversation opened)
   - Full message history
   - Message bubbles (sent/received)
   - Delivery status (delivered ✓, read ✓✓)
   - Input field with send button
   - Typing indicators integration

5. **Compose Panel** (slides in from bottom)
   - Recipient selector (users + broadcast option)
   - Message textarea
   - Send/Cancel buttons

6. **Search & Filters**
   - Search messages by text
   - Filter by unread, type, time range
   - Quick access to specific conversations

---

## ✅ Advantages of This Design

**Why Sidebar + Toast Together:**

1. **Toast = Instant Notification**
   - Non-intrusive (bottom-left)
   - Quick reply without context switch
   - Auto-dismissible
   - Shows device info immediately

2. **Sidebar = Persistent Hub**
   - Full conversation history
   - Search & filter capabilities
   - See all online users
   - Manage multiple conversations
   - Message composition

3. **Best of Both Worlds:**
   - Quick interactions → Use toast
   - Deep conversations → Use sidebar
   - User chooses workflow
   - Both sync to same database

---

## 🚀 Implementation Priority

**Phase 1: Core Sidebar** (2-3 hours)
- Sidebar HTML structure
- CSS styling
- Toggle button integration
- Conversations list (read from database)

**Phase 2: Online Users** (1 hour)
- Online users tab
- Real-time presence updates
- Device info display

**Phase 3: Conversation View** (2 hours)
- Full conversation interface
- Message bubbles
- Send/receive messages
- Typing indicators

**Phase 4: Polish** (1 hour)
- Search functionality
- Filters
- Broadcasts tab
- Compose panel

---

**Ready to implement? This design integrates perfectly with your existing:**
- Display name system ✓
- Device detection ✓
- Toast notifications ✓
- WebSocket infrastructure ✓
- Database persistence ✓

**Would you like me to start building the sidebar HTML/CSS/JS?**
