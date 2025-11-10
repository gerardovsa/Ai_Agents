# Business AI Platform v2 - Integration Implementation

**Date**: January 2025  
**Status**: In Progress  
**Goal**: Integrate Triple Agent multi-panel + Shopify enhancements into business-ai-platform-v2.html

---

## 🎯 Integration Checklist

### Phase 1: Multi-Agent Panel Integration ✅ IN PROGRESS

#### Step 1: Replace Single Chat Panel with Multi-Agent Container
**Location**: Lines 400-600 in business-ai-platform-v2.html

**Current Structure**:
```html
<div class="ai-chat-panel">
    <!-- Single chat panel -->
</div>
```

**New Structure**:
```html
<div class="ai-chat-container">
    <div class="ai-agents-wrapper" id="aiAgentsWrapper">
        <!-- Dynamic agent columns -->
    </div>
    <div class="add-agent-bar" onclick="addAIAgent()">
        <div class="add-agent-icon">
            <i class="fas fa-plus"></i>
            <span>Add Agent</span>
        </div>
    </div>
</div>
```

#### Step 2: Add CSS for Multi-Agent Columns
**Add after line 600**:

```css
/* ==================== MULTI-AGENT CHAT SYSTEM ==================== */
.ai-chat-container {
    position: relative;
    display: flex;
    overflow-x: auto;
    overflow-y: hidden;
}

.ai-agents-wrapper {
    display: flex;
    gap: 16px;
    padding: 16px;
    flex: 1;
    overflow-x: auto;
}

/* Agent Column */
.ai-agent-column {
    min-width: 400px;
    max-width: 400px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    height: calc(100vh - var(--header-height) - 32px);
}

.agent-header {
    padding: 16px;
    border-bottom: 1px solid var(--border-default);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.agent-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    font-size: 15px;
}

.agent-controls {
    display: flex;
    align-items: center;
    gap: 12px;
}

/* Display Mode Selector */
.display-mode-selector {
    display: flex;
    gap: 4px;
    background: var(--bg-tertiary);
    padding: 4px;
    border-radius: 6px;
}

.mode-btn {
    padding: 6px 10px;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    border-radius: 4px;
    font-size: 12px;
    transition: all 0.2s;
}

.mode-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
}

.mode-btn.active {
    background: var(--accent-primary);
    color: white;
}

/* Hamburger Menu */
.hamburger-menu {
    position: relative;
}

.hamburger-btn {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 8px;
    border-radius: 4px;
    transition: all 0.2s;
}

.hamburger-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
}

.menu-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-default);
    border-radius: 8px;
    min-width: 200px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.3);
    display: none;
    z-index: 1000;
    margin-top: 4px;
}

.menu-dropdown.show {
    display: block;
}

.menu-item {
    padding: 10px 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--text-primary);
    font-size: 14px;
    transition: all 0.2s;
}

.menu-item:hover {
    background: var(--bg-hover);
}

.menu-item i {
    width: 16px;
    color: var(--text-secondary);
}

.menu-separator {
    height: 1px;
    background: var(--border-default);
    margin: 4px 0;
}

/* Messages Container */
.messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

/* Message Bubbles */
.message-bubble {
    padding: 12px;
    border-radius: 8px;
    max-width: 85%;
    word-wrap: break-word;
    animation: slideIn 0.3s ease;
    position: relative;
}

.message.user {
    display: flex;
    justify-content: flex-end;
}

.message.user .message-bubble {
    background: var(--accent-primary);
    color: white;
    margin-left: auto;
}

.message.assistant .message-bubble {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-default);
    color: var(--text-primary);
}

/* Bubble Controls */
.bubble-controls {
    position: absolute;
    top: 4px;
    right: 4px;
    display: flex;
    gap: 4px;
    opacity: 0;
    transition: opacity 0.2s;
}

.message-bubble:hover .bubble-controls {
    opacity: 1;
}

.bubble-collapse-btn,
.bubble-copy-btn {
    background: rgba(0,0,0,0.3);
    border: none;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
}

.bubble-collapse-btn:hover,
.bubble-copy-btn:hover {
    background: rgba(0,0,0,0.5);
}

/* Terminal Mode */
.messages-container[data-display-mode="terminal"] .message-bubble {
    max-width: 100%;
    background: var(--bg-primary);
    border: 1px solid var(--border-default);
    font-family: var(--font-mono);
    font-size: 13px;
}

.messages-container[data-display-mode="terminal"] .log-entry {
    padding: 8px 12px;
    border-left: 3px solid var(--text-muted);
    font-family: var(--font-mono);
    font-size: 13px;
}

.log-entry.thinking_block { border-left-color: #bc8cff; color: #bc8cff; }
.log-entry.tool_use_request { border-left-color: var(--accent-success); color: var(--accent-success); }
.log-entry.text_block { border-left-color: var(--accent-info); }
.log-entry.server_tool_use { border-left-color: var(--accent-warning); }
.log-entry.error { border-left-color: var(--accent-error); color: var(--accent-error); }

/* Separated Mode */
.messages-container[data-display-mode="separated"] .message.thinking .message-bubble {
    background: rgba(188, 140, 255, 0.1);
    border: 1px solid #bc8cff;
    font-style: italic;
}

.messages-container[data-display-mode="separated"] .message.tool .message-bubble {
    background: rgba(63, 185, 80, 0.1);
    border: 1px solid var(--accent-success);
    font-family: var(--font-mono);
    font-size: 13px;
}

/* File Upload */
.file-preview-container {
    padding: 0 16px;
    display: none;
    gap: 8px;
    flex-wrap: wrap;
}

.file-preview-container.has-files {
    display: flex;
    padding: 12px 16px;
}

.file-chip {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-default);
    border-radius: 6px;
    padding: 6px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
}

.file-chip i {
    color: var(--accent-primary);
}

.file-name {
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.file-size {
    color: var(--text-secondary);
    font-size: 11px;
}

.remove-file {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 4px;
}

.remove-file:hover {
    color: var(--accent-error);
}

/* Input Area */
.agent-input-area {
    padding: 16px;
    border-top: 1px solid var(--border-default);
    display: flex;
    gap: 8px;
}

.agent-input-area textarea {
    flex: 1;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-default);
    border-radius: 6px;
    padding: 10px;
    color: var(--text-primary);
    font-size: 14px;
    resize: none;
    min-height: 44px;
    max-height: 120px;
    font-family: var(--font-primary);
}

.agent-input-area textarea:focus {
    outline: none;
    border-color: var(--accent-primary);
}

.attach-btn,
.send-btn {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-default);
    color: var(--text-primary);
    padding: 10px 14px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
}

.attach-btn:hover,
.send-btn:hover {
    background: var(--bg-hover);
    border-color: var(--accent-primary);
}

.send-btn {
    background: var(--accent-primary);
    color: white;
    border-color: var(--accent-primary);
}

.send-btn:hover {
    background: #4493e8;
}

/* Add Agent Bar */
.add-agent-bar {
    position: sticky;
    right: 0;
    top: 0;
    width: 60px;
    height: 100%;
    background: var(--bg-tertiary);
    border-left: 1px solid var(--border-default);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
    flex-shrink: 0;
}

.add-agent-bar:hover {
    background: var(--bg-hover);
    border-left-color: var(--accent-primary);
}

.add-agent-icon {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    color: var(--text-secondary);
}

.add-agent-bar:hover .add-agent-icon {
    color: var(--accent-primary);
}

.add-agent-icon i {
    font-size: 24px;
}

.add-agent-icon span {
    font-size: 11px;
    writing-mode: vertical-rl;
    text-orientation: mixed;
}

/* Thread History Sidebar */
.thread-history-sidebar {
    position: fixed;
    right: -400px;
    top: var(--header-height);
    bottom: 0;
    width: 400px;
    background: var(--bg-secondary);
    border-left: 1px solid var(--border-default);
    z-index: 2000;
    transition: right 0.3s ease;
    display: flex;
    flex-direction: column;
}

.thread-history-sidebar.show {
    right: 0;
}

.sidebar-header {
    padding: 16px;
    border-bottom: 1px solid var(--border-default);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.sidebar-header h3 {
    font-size: 16px;
    font-weight: 600;
}

.close-sidebar {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 8px;
    border-radius: 4px;
}

.close-sidebar:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
}

.thread-list {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
}

.thread-item {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-default);
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s;
}

.thread-item:hover {
    border-color: var(--accent-primary);
    transform: translateX(-4px);
}

.thread-title {
    font-weight: 600;
    margin-bottom: 4px;
}

.thread-date {
    font-size: 12px;
    color: var(--text-secondary);
}

.thread-actions {
    display: flex;
    gap: 8px;
    margin-top: 8px;
}

.open-thread-btn,
.delete-thread-btn {
    flex: 1;
    padding: 6px 12px;
    border: 1px solid var(--border-default);
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.2s;
}

.open-thread-btn {
    background: var(--accent-primary);
    color: white;
    border-color: var(--accent-primary);
}

.open-thread-btn:hover {
    background: #4493e8;
}

.delete-thread-btn {
    background: transparent;
    color: var(--accent-error);
}

.delete-thread-btn:hover {
    background: rgba(248, 81, 73, 0.1);
}
```

#### Step 3: Add Shopify Dashboard Enhancements

**Enhanced Metric Cards (Add to CSS)**:
```css
/* ==================== ENHANCED METRIC CARDS (FROM SHOPIFY) ==================== */
.metric-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: 12px;
    padding: 20px;
    transition: all 0.2s;
}

.metric-card:hover {
    border-color: var(--accent-primary);
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(88, 166, 255, 0.1);
}

.metric-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.metric-label {
    color: var(--text-secondary);
    font-size: 13px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
}

.metric-icon.purple { background: rgba(124, 58, 237, 0.1); color: #7c3aed; }
.metric-icon.green { background: rgba(63, 185, 80, 0.1); color: var(--accent-success); }
.metric-icon.blue { background: rgba(88, 166, 255, 0.1); color: var(--accent-info); }
.metric-icon.orange { background: rgba(210, 153, 34, 0.1); color: var(--accent-warning); }

.metric-value {
    font-size: 32px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
}

.metric-change {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
}

.metric-change.positive {
    color: var(--accent-success);
}

.metric-change.negative {
    color: var(--accent-error);
}

.metric-change i {
    font-size: 12px;
}

/* Status Badges (From Shopify) */
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.status-badge.paid { background: rgba(63, 185, 80, 0.2); color: var(--accent-success); }
.status-badge.pending { background: rgba(210, 153, 34, 0.2); color: var(--accent-warning); }
.status-badge.fulfilled { background: rgba(88, 166, 255, 0.2); color: var(--accent-info); }
.status-badge.refunded { background: rgba(248, 81, 73, 0.2); color: var(--accent-error); }
.status-badge.high { background: rgba(63, 185, 80, 0.2); color: var(--accent-success); }
.status-badge.medium { background: rgba(210, 153, 34, 0.2); color: var(--accent-warning); }
.status-badge.low { background: rgba(88, 166, 255, 0.2); color: var(--accent-info); }

/* Filter Panels (From Shopify) */
.filters-panel {
    display: none;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-default);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    gap: 16px;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.filters-panel.active {
    display: grid;
}

.filter-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.filter-label {
    color: var(--text-secondary);
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.filter-select {
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: 6px;
    padding: 8px 12px;
    color: var(--text-primary);
    font-size: 14px;
    cursor: pointer;
}

.filter-select:focus {
    outline: none;
    border-color: var(--accent-primary);
}

/* Loading Spinner (From Shopify) */
.loading-spinner {
    display: none;
    text-align: center;
    padding: 40px;
}

.loading-spinner.active {
    display: block;
}

.loading-spinner .spinner {
    border: 3px solid var(--border-default);
    border-top: 3px solid var(--accent-primary);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 16px;
}

.loading-message {
    color: var(--text-secondary);
    font-size: 14px;
}

/* Empty State (From Shopify) */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: var(--text-secondary);
}

.empty-state i {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
}

.empty-state h3 {
    font-size: 18px;
    margin-bottom: 8px;
    color: var(--text-primary);
}

.empty-state p {
    font-size: 14px;
}
```

---

## 🔧 JavaScript Functions to Add

### Multi-Agent Management
```javascript
// NATO phonetic alphabet for agent names
const agentNames = [
    'Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot',
    'Golf', 'Hotel', 'India', 'Juliet', 'Kilo', 'Lima',
    'Mike', 'November', 'Oscar', 'Papa', 'Quebec', 'Romeo',
    'Sierra', 'Tango', 'Uniform', 'Victor', 'Whiskey', 'Xray',
    'Yankee', 'Zulu'
];

let nextAgentId = 1;
const agentSessions = {};
const streams = {};
const attachedFiles = {};

function addAIAgent() {
    const agentId = `agent-${nextAgentId}`;
    const agentName = agentNames[nextAgentId - 1] || `Agent ${nextAgentId}`;
    
    const agentColumn = createAgentColumn(agentId, agentName);
    document.getElementById('aiAgentsWrapper').insertAdjacentHTML('beforeend', agentColumn);
    
    // Initialize agent
    initializeAgent(agentId);
    attachedFiles[agentId] = [];
    agentSessions[agentId] = generateSessionId();
    
    nextAgentId++;
    
    showNotification(`Agent ${agentName} created`, 'success');
}

function createAgentColumn(agentId, agentName) {
    return `
        <div class="ai-agent-column" id="${agentId}" data-display-mode="bubbles">
            <div class="agent-header">
                <div class="agent-title">
                    <i class="fas fa-robot"></i>
                    <span>${agentName}</span>
                </div>
                <div class="agent-controls">
                    <div class="display-mode-selector">
                        <button class="mode-btn active" data-mode="bubbles" onclick="switchDisplayMode('${agentId}', 'bubbles')">
                            <i class="fas fa-comments"></i>
                        </button>
                        <button class="mode-btn" data-mode="terminal" onclick="switchDisplayMode('${agentId}', 'terminal')">
                            <i class="fas fa-terminal"></i>
                        </button>
                        <button class="mode-btn" data-mode="separated" onclick="switchDisplayMode('${agentId}', 'separated')">
                            <i class="fas fa-layer-group"></i>
                        </button>
                    </div>
                    <div class="hamburger-menu">
                        <button class="hamburger-btn" onclick="toggleAgentMenu('${agentId}')">
                            <i class="fas fa-ellipsis-v"></i>
                        </button>
                        <div class="menu-dropdown" id="menu-${agentId}">
                            <div class="menu-item" onclick="newAgentChat('${agentId}')">
                                <i class="fas fa-plus"></i> New Chat
                            </div>
                            <div class="menu-item" onclick="showSaveThread('${agentId}')">
                                <i class="fas fa-save"></i> Save Thread
                            </div>
                            <div class="menu-item" onclick="showThreadHistory('${agentId}')">
                                <i class="fas fa-history"></i> Thread History
                            </div>
                            <div class="menu-item" onclick="copyAgentThread('${agentId}')">
                                <i class="fas fa-copy"></i> Copy Thread
                            </div>
                            <div class="menu-item" onclick="exportAgentThread('${agentId}')">
                                <i class="fas fa-download"></i> Export TXT
                            </div>
                            <div class="menu-separator"></div>
                            <div class="menu-item" onclick="closeAgent('${agentId}')">
                                <i class="fas fa-times"></i> Close Agent
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="messages-container" id="messages-${agentId}" data-display-mode="bubbles">
                <div class="message assistant">
                    <div class="message-bubble">
                        👋 <strong>Hello! I'm Agent ${agentName}</strong><br><br>
                        I have access to <strong>19 platforms</strong> and <strong>114+ tools</strong>.<br><br>
                        How can I help you today?
                    </div>
                </div>
            </div>
            
            <div class="file-preview-container" id="filePreview-${agentId}">
                <!-- File chips will appear here -->
            </div>
            
            <div class="agent-input-area">
                <button class="attach-btn" onclick="triggerFileUpload('${agentId}')">
                    <i class="fas fa-paperclip"></i>
                </button>
                <textarea 
                    id="input-${agentId}" 
                    placeholder="Ask me anything..."
                    oninput="autoExpandTextarea(this)"
                    onkeydown="handleAgentKeyPress(event, '${agentId}')"></textarea>
                <button class="send-btn" onclick="sendAgentMessage('${agentId}')">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
            
            <input type="file" id="fileInput-${agentId}" multiple style="display:none" 
                   onchange="handleFileSelection('${agentId}', this.files)">
        </div>
    `;
}

function initializeAgent(agentId) {
    const messagesContainer = document.getElementById(`messages-${agentId}`);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function switchDisplayMode(agentId, mode) {
    const column = document.getElementById(agentId);
    column.dataset.displayMode = mode;
    
    const messagesContainer = document.getElementById(`messages-${agentId}`);
    messagesContainer.dataset.displayMode = mode;
    
    // Update button states
    column.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.mode === mode) {
            btn.classList.add('active');
        }
    });
}

function toggleAgentMenu(agentId) {
    const menu = document.getElementById(`menu-${agentId}`);
    menu.classList.toggle('show');
    
    // Close other menus
    document.querySelectorAll('.menu-dropdown').forEach(m => {
        if (m.id !== `menu-${agentId}`) {
            m.classList.remove('show');
        }
    });
}

function sendAgentMessage(agentId) {
    const input = document.getElementById(`input-${agentId}`);
    const message = input.value.trim();
    
    if (!message && attachedFiles[agentId].length === 0) return;
    
    // Add user message
    addAgentMessage(agentId, 'user', message);
    input.value = '';
    
    // Send to backend
    sendToBackend(agentId, message, attachedFiles[agentId]);
    
    // Clear files
    attachedFiles[agentId] = [];
    updateFilePreview(agentId);
}

function addAgentMessage(agentId, role, content) {
    const messagesContainer = document.getElementById(`messages-${agentId}`);
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    bubbleDiv.innerHTML = content;
    
    // Add bubble controls
    const controls = document.createElement('div');
    controls.className = 'bubble-controls';
    controls.innerHTML = `
        <button class="bubble-collapse-btn" onclick="toggleBubbleCollapse(this)">
            <i class="fas fa-compress"></i>
        </button>
        <button class="bubble-copy-btn" onclick="copyBubbleContent(this)">
            <i class="fas fa-copy"></i>
        </button>
    `;
    bubbleDiv.appendChild(controls);
    
    messageDiv.appendChild(bubbleDiv);
    messagesContainer.appendChild(messageDiv);
    
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function autoExpandTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function handleAgentKeyPress(event, agentId) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendAgentMessage(agentId);
    }
}

// File Upload Functions
function triggerFileUpload(agentId) {
    document.getElementById(`fileInput-${agentId}`).click();
}

function handleFileSelection(agentId, files) {
    Array.from(files).forEach(file => {
        if (file.size > 10 * 1024 * 1024) {
            showNotification('File too large. Max 10MB', 'error');
            return;
        }
        attachedFiles[agentId].push(file);
    });
    updateFilePreview(agentId);
}

function updateFilePreview(agentId) {
    const container = document.getElementById(`filePreview-${agentId}`);
    
    if (attachedFiles[agentId].length === 0) {
        container.classList.remove('has-files');
        container.innerHTML = '';
        return;
    }
    
    container.classList.add('has-files');
    container.innerHTML = attachedFiles[agentId].map((file, index) => `
        <div class="file-chip">
            <i class="fas fa-paperclip"></i>
            <span class="file-name">${file.name}</span>
            <span class="file-size">${formatFileSize(file.size)}</span>
            <button class="remove-file" onclick="removeFile('${agentId}', ${index})">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `).join('');
}

function removeFile(agentId, index) {
    attachedFiles[agentId].splice(index, 1);
    updateFilePreview(agentId);
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Thread Management
function newAgentChat(agentId) {
    if (confirm('Start a new chat? Current conversation will be cleared.')) {
        document.getElementById(`messages-${agentId}`).innerHTML = '';
        agentSessions[agentId] = generateSessionId();
        toggleAgentMenu(agentId);
    }
}

function closeAgent(agentId) {
    if (confirm('Close this agent? Unsaved conversations will be lost.')) {
        document.getElementById(agentId).remove();
        delete agentSessions[agentId];
        delete attachedFiles[agentId];
        if (streams[agentId]) {
            streams[agentId].close();
            delete streams[agentId];
        }
    }
}

// Backend Communication
async function sendToBackend(agentId, message, files) {
    const sessionId = agentSessions[agentId];
    
    // Create FormData for file upload
    const formData = new FormData();
    formData.append('message', message);
    formData.append('session_id', sessionId);
    files.forEach(file => formData.append('files', file));
    
    try {
        // If files present, upload first
        if (files.length > 0) {
            const uploadResponse = await fetch('http://localhost:4000/api/chat/upload', {
                method: 'POST',
                body: formData
            });
            const uploadData = await uploadResponse.json();
            console.log('Files uploaded:', uploadData);
        }
        
        // Connect to streaming endpoint
        connectStreamToAgent(agentId, message);
        
    } catch (error) {
        console.error('Error sending message:', error);
        addAgentMessage(agentId, 'assistant', '❌ Error connecting to AI service. Please try again.');
    }
}

function connectStreamToAgent(agentId, message) {
    const sessionId = agentSessions[agentId];
    const url = `http://localhost:4000/api/chat/stream?session_id=${sessionId}&message=${encodeURIComponent(message)}`;
    
    const eventSource = new EventSource(url);
    streams[agentId] = eventSource;
    
    let currentMessage = '';
    
    eventSource.addEventListener('content_block_delta', (e) => {
        const data = JSON.parse(e.data);
        currentMessage += data.delta || '';
        updateStreamingMessage(agentId, currentMessage);
    });
    
    eventSource.addEventListener('message_stop', (e) => {
        eventSource.close();
        delete streams[agentId];
    });
    
    eventSource.onerror = (error) => {
        console.error('SSE Error:', error);
        eventSource.close();
        addAgentMessage(agentId, 'assistant', '❌ Connection lost. Please try again.');
    };
}

function updateStreamingMessage(agentId, content) {
    const messagesContainer = document.getElementById(`messages-${agentId}`);
    let streamingMessage = messagesContainer.querySelector('.message.assistant.streaming');
    
    if (!streamingMessage) {
        streamingMessage = document.createElement('div');
        streamingMessage.className = 'message assistant streaming';
        streamingMessage.innerHTML = '<div class="message-bubble"></div>';
        messagesContainer.appendChild(streamingMessage);
    }
    
    const bubble = streamingMessage.querySelector('.message-bubble');
    bubble.innerHTML = marked.parse(content);
    
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
```

---

## 📝 Next Steps

1. **Copy CSS sections** above into business-ai-platform-v2.html after line 600
2. **Replace AI chat panel** HTML with multi-agent container (lines 1200-1400)
3. **Add JavaScript functions** to end of `<script>` tag (before closing `</script>`)
4. **Test in browser** - verify agent columns can be added
5. **Create backend routes** (next phase)

---

**Status**: Ready for implementation  
**Est. Time**: 2 hours for frontend integration  
**Next**: Backend route creation
