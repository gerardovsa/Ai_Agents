# Agent Expandable Input Container Implementation Plan
**Date:** December 1, 2025  
**Objective:** Implement Prime-style expandable input containers with transcription for all Agent columns  
**Requirement:** Maintain complete thread/column-specific isolation

---

## 🎯 Implementation Overview

### **Goal**
Give every Agent column the same expandable input container functionality as AI Prime:
- ✅ 4-state sliding input system (collapsed bar → hover → focus → expanded)
- ✅ Feedback area (give guidance to AI mid-task)
- ✅ Voice transcription with microphone button
- ✅ Prompt library button
- ✅ Auto-scroll toggle
- ✅ File attachments
- ✅ Chevron animation on collapsed bar

### **Critical Constraint**
**Column-Specific Isolation:** Each agent must have completely independent state:
- Agent-1 can be recording while Agent-2 is idle
- Agent-1 feedback area open while Agent-2 is closed
- Agent-1 expanded while Agent-2 collapsed
- No cross-contamination of transcript data, feedback text, or UI states

---

## 📋 Current State Analysis

### **AI Prime Input Container (Reference)**
**Location:** `business-ai-platform-v2.html` lines 16965-17040

**Structure:**
```html
<div class="ai-chat-input-container">
    <!-- Feedback Area (toggleable) -->
    <div id="user-feedback-container" class="user-feedback-container">
        <textarea id="user-feedback-text"></textarea>
        <buttons: pause, stop, explain, send>
    </div>
    
    <!-- Input Wrapper (shown/hidden) -->
    <div class="ai-chat-input-wrapper" style="display: none;">
        <div class="ai-chat-attached-files"></div>
        <div class="ai-chat-input-controls">
            <textarea id="ai-chat-input"></textarea>
            <div class="ai-chat-right-buttons">
                <button: prompt-library>
                <button: autoscroll>
                <button: feedback>
                <button: microphone>
                <button: attach>
                <button: send>
            </div>
        </div>
    </div>
</div>
```

**CSS Classes:**
- `.ai-chat-input-container` - Parent (collapsed bar)
- `.ai-chat-input-container.expanded` - Expanded state
- `.ai-chat-input-wrapper` - Inner wrapper (visibility controlled)
- `.ai-chat-right-buttons` - Button stack (6 buttons)
- `.user-feedback-container` - Feedback area

**JavaScript Functions:**
- `toggleFeedbackContainer()` - Show/hide feedback area
- `insertQuickFeedback(type)` - Insert pause/stop/explain
- `sendFeedback()` - Send feedback to AI
- `toggleTranscriptionRecording()` - Start/stop voice recording
- `toggleAutoScroll()` - Enable/disable auto-scroll
- `expandInputArea()` / `collapseInputArea()` - 4-state system

---

### **Current Agent Input (Simple)**
**Location:** `agent-column.js` line 155, `agent-js.js` line 2464

**Structure:**
```html
<div class="agent-input-area" style="display: none;">
    <div id="agent-attached-files-{agentId}"></div>
    <div class="agent-input-group">
        <textarea id="input-{agentId}"></textarea>
        <div class="agent-input-right-buttons">
            <button: attach>
            <button: send>
        </div>
    </div>
</div>
```

**Issues:**
- ❌ No expandable/collapsible behavior
- ❌ No feedback area
- ❌ No transcription support
- ❌ No prompt library
- ❌ No auto-scroll toggle
- ❌ Only 2 buttons (vs 6 in Prime)
- ❌ No 4-state sliding system

---

## 🏗️ Implementation Architecture

### **Phase 1: HTML Structure Update**

#### **New Agent Input Container Structure**
```html
<div class="agent-input-container" data-agent-id="{agentId}">
    <!-- Feedback Area (Per-Agent) -->
    <div id="agent-feedback-{agentId}" class="agent-feedback-container">
        <div class="feedback-header">
            <div class="feedback-header-left">
                <i class="fas fa-comment-dots"></i>
                <span class="feedback-header-text">Provide guidance to AI</span>
            </div>
            <button class="feedback-close-btn" onclick="Agent.toggleFeedback({agentId})">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="feedback-body">
            <textarea id="agent-feedback-text-{agentId}" 
                      placeholder="Type instructions or guidance..."></textarea>
            <div class="feedback-quick-buttons">
                <button onclick="Agent.insertQuickFeedback({agentId}, 'pause')">
                    <i class="fas fa-pause"></i>
                </button>
                <button onclick="Agent.insertQuickFeedback({agentId}, 'stop')">
                    <i class="fas fa-stop"></i>
                </button>
                <button onclick="Agent.insertQuickFeedback({agentId}, 'explain')">
                    <i class="fas fa-question-circle"></i>
                </button>
                <button onclick="Agent.sendFeedback({agentId})">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        </div>
    </div>
    
    <!-- Input Wrapper (Per-Agent) -->
    <div class="agent-input-wrapper" style="display: none;">
        <div class="agent-attached-files" id="agent-attached-files-{agentId}"></div>
        <div class="agent-input-controls">
            <div class="agent-input-center">
                <textarea id="agent-input-{agentId}" 
                          placeholder="Type your message..."
                          rows="3"></textarea>
            </div>
            <div class="agent-input-right-buttons">
                <button class="agent-prompt-library-btn" 
                        id="agent-prompt-library-{agentId}"
                        onclick="Agent.showPromptLibrary({agentId})"
                        title="Browse Prompt Library">
                    <i class="fas fa-bolt"></i>
                </button>
                <button class="agent-autoscroll-btn active" 
                        id="agent-autoscroll-{agentId}"
                        onclick="Agent.toggleAutoScroll({agentId})"
                        title="Toggle auto-scroll">
                    <i class="fas fa-angle-double-down"></i>
                </button>
                <button class="agent-feedback-btn" 
                        id="agent-feedback-btn-{agentId}"
                        onclick="Agent.toggleFeedback({agentId})"
                        title="Give feedback to AI">
                    <i class="fas fa-comment-dots"></i>
                </button>
                <button class="agent-mic-btn" 
                        id="agent-mic-{agentId}"
                        onclick="Agent.toggleTranscription({agentId})"
                        title="Start voice transcription">
                    <i class="fas fa-microphone"></i>
                </button>
                <button class="agent-attach-btn" 
                        id="agent-attach-{agentId}"
                        onclick="Agent.showFileDialog({agentId})"
                        title="Attach files">
                    <i class="fas fa-paperclip"></i>
                    <input type="file" 
                           id="agent-file-input-{agentId}" 
                           multiple 
                           accept=".pdf,.png,.jpg,.jpeg,.gif,.webp"
                           style="display: none;">
                </button>
                <button class="agent-send-btn" 
                        id="agent-send-{agentId}"
                        onclick="Agent.sendMessage({agentId})"
                        title="Send message">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        </div>
    </div>
</div>
```

**Key Changes:**
- `.agent-input-area` → `.agent-input-container` (matches Prime naming)
- Added `.agent-feedback-container` (per-agent feedback)
- Added `.agent-input-wrapper` (inner wrapper for visibility control)
- All IDs parameterized with `{agentId}` (isolation)
- 6 buttons (matches Prime: prompt, autoscroll, feedback, mic, attach, send)

---

### **Phase 2: CSS Styling**

#### **New CSS Classes Needed**
```css
/* Agent Input Container - Collapsed Bar (State 1) */
.agent-input-container {
    flex-shrink: 0;
    padding: 0 20px;
    background: transparent;
    transition: all 0.4s cubic-bezier(0.4, 0.0, 0.2, 1);
    height: 30px; /* Collapsed bar height */
    overflow: hidden;
    cursor: pointer;
    position: relative;
}

/* State 4: Expanded */
.agent-input-container.expanded {
    height: auto;
    padding: 20px;
    cursor: default;
    overflow: visible;
}

/* Collapsed bar visual */
.agent-input-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: rgba(255, 255, 255, 0.08);
    transition: all 0.3s ease;
    pointer-events: none;
}

/* Hover state - accent border */
.agent-input-container:not(.expanded):hover::before {
    background: var(--accent-primary);
    box-shadow: 0 0 8px rgba(88, 166, 255, 0.5);
}

/* Chevron indicator (double stacked) */
.agent-input-container::after {
    content: '\f077\A\f077';
    font-family: 'Font Awesome 5 Free';
    font-weight: 900;
    white-space: pre;
    line-height: 0.5;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 10px;
    color: rgba(139, 148, 158, 0.5);
    transition: all 0.3s ease;
    pointer-events: none;
    opacity: 1;
}

/* Hover - animate chevrons upward */
.agent-input-container:not(.expanded):hover::after {
    color: var(--accent-primary);
    text-shadow: 0 0 8px rgba(88, 166, 255, 0.8);
    transform: translate(-50%, -60%) scale(1.2);
    animation: chevron-bounce-up 0.6s ease-in-out infinite;
}

/* Hide chevrons when expanded */
.agent-input-container.expanded::after,
.agent-input-container.expanded::before {
    opacity: 0;
}

/* Agent Input Wrapper */
.agent-input-wrapper {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    position: relative;
    opacity: 0;
    transition: opacity 0.4s cubic-bezier(0.4, 0.0, 0.2, 1);
    pointer-events: none;
}

/* Expanded state - wrapper visible */
.agent-input-container.expanded .agent-input-wrapper {
    opacity: 1;
    pointer-events: auto;
}

/* Agent Feedback Container */
.agent-feedback-container {
    display: none; /* Hidden by default */
    flex-direction: column;
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
}

.agent-feedback-container.active {
    display: flex !important;
}

/* Right Button Stack (6 buttons) */
.agent-input-right-buttons {
    position: absolute;
    bottom: 3px;
    right: 0px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: 32px;
    pointer-events: auto;
    z-index: 10;
}

/* Button styling */
.agent-prompt-library-btn,
.agent-autoscroll-btn,
.agent-feedback-btn,
.agent-mic-btn,
.agent-attach-btn {
    width: 32px;
    height: 32px;
    padding: 0;
    background: transparent;
    color: rgba(139, 148, 158, 0.5);
    border: none;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}

.agent-send-btn {
    width: 32px;
    height: 32px;
    padding: 0;
    background: transparent;
    color: var(--accent-primary);
    border: 1px solid var(--accent-primary);
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    opacity: 0.5;
}

/* Expanded state - buttons interactive */
.agent-input-container.expanded .agent-prompt-library-btn,
.agent-input-container.expanded .agent-autoscroll-btn,
.agent-input-container.expanded .agent-feedback-btn,
.agent-input-container.expanded .agent-mic-btn,
.agent-input-container.expanded .agent-attach-btn {
    background: transparent;
    border: 1px solid var(--border-default);
    color: var(--text-primary);
}

.agent-input-container.expanded .agent-send-btn {
    background: var(--accent-primary);
    color: white;
    border: 1px solid var(--accent-primary);
    opacity: 1;
}

/* Hover states */
.agent-prompt-library-btn:hover,
.agent-autoscroll-btn:hover,
.agent-feedback-btn:hover,
.agent-mic-btn:hover,
.agent-attach-btn:hover {
    background: transparent !important;
    color: var(--accent-primary);
    border-color: var(--accent-primary) !important;
    transform: scale(1.05);
}

.agent-send-btn:hover {
    background: var(--accent-primary) !important;
    transform: scale(1.1);
    box-shadow: 0 2px 8px rgba(88, 166, 255, 0.4);
}

/* Recording state for microphone button */
.agent-mic-btn.recording {
    color: #ef4444 !important;
    border-color: #ef4444 !important;
    animation: pulse-recording 1.5s ease-in-out infinite;
}

@keyframes pulse-recording {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}
```

---

### **Phase 3: JavaScript State Management**

#### **Agent State Object (Per-Column Isolation)**
```javascript
// Global state object for all agents
window.AgentInputStates = {};

// Initialize state for specific agent
function initAgentInputState(agentId) {
    window.AgentInputStates[agentId] = {
        isExpanded: false,
        isFeedbackOpen: false,
        isRecording: false,
        isAutoScrollEnabled: true,
        feedbackText: '',
        transcriptionActive: false,
        attachedFiles: []
    };
}

// Get state for specific agent
function getAgentState(agentId) {
    if (!window.AgentInputStates[agentId]) {
        initAgentInputState(agentId);
    }
    return window.AgentInputStates[agentId];
}
```

#### **Core Functions (Column-Specific)**
```javascript
/**
 * Toggle feedback container for specific agent
 */
function toggleAgentFeedback(agentId) {
    const state = getAgentState(agentId);
    const container = document.getElementById(`agent-feedback-${agentId}`);
    
    if (!container) return;
    
    state.isFeedbackOpen = !state.isFeedbackOpen;
    container.classList.toggle('active', state.isFeedbackOpen);
    
    console.log(`[Agent-${agentId}] Feedback ${state.isFeedbackOpen ? 'opened' : 'closed'}`);
}

/**
 * Insert quick feedback for specific agent
 */
function insertAgentQuickFeedback(agentId, type) {
    const textarea = document.getElementById(`agent-feedback-text-${agentId}`);
    if (!textarea) return;
    
    const messages = {
        'pause': 'Please pause and wait for my instructions.',
        'stop': 'Please stop the current task.',
        'explain': 'Can you explain what you are doing?'
    };
    
    textarea.value = messages[type] || '';
    textarea.focus();
    
    console.log(`[Agent-${agentId}] Quick feedback: ${type}`);
}

/**
 * Send feedback for specific agent
 */
function sendAgentFeedback(agentId) {
    const textarea = document.getElementById(`agent-feedback-text-${agentId}`);
    if (!textarea || !textarea.value.trim()) return;
    
    const feedbackText = textarea.value.trim();
    
    // Send feedback as message to this specific agent
    sendAgentMessage(agentId, feedbackText, { isFeedback: true });
    
    // Clear feedback
    textarea.value = '';
    toggleAgentFeedback(agentId);
    
    console.log(`[Agent-${agentId}] Feedback sent: ${feedbackText}`);
}

/**
 * Toggle transcription for specific agent
 */
function toggleAgentTranscription(agentId) {
    const state = getAgentState(agentId);
    const micBtn = document.getElementById(`agent-mic-${agentId}`);
    
    if (!micBtn) return;
    
    if (state.isRecording) {
        // Stop recording
        if (window.SharedTranscriptionState) {
            window.SharedTranscriptionState.stopRecording();
        }
        micBtn.classList.remove('recording');
        micBtn.querySelector('i').className = 'fas fa-microphone';
        micBtn.title = 'Start voice transcription';
        state.isRecording = false;
    } else {
        // Start recording (target this agent's input)
        if (window.SharedTranscriptionState) {
            window.SharedTranscriptionState.startRecording(`agent-${agentId}`)
                .then(() => {
                    micBtn.classList.add('recording');
                    micBtn.querySelector('i').className = 'fas fa-stop';
                    micBtn.title = 'Stop recording';
                    state.isRecording = true;
                    console.log(`[Agent-${agentId}] Transcription started`);
                })
                .catch(error => {
                    console.error(`[Agent-${agentId}] Transcription failed:`, error);
                    alert('Could not start recording: ' + error.message);
                });
        } else {
            console.error(`[Agent-${agentId}] SharedTranscriptionState not available`);
        }
    }
}

/**
 * Toggle auto-scroll for specific agent
 */
function toggleAgentAutoScroll(agentId) {
    const state = getAgentState(agentId);
    const btn = document.getElementById(`agent-autoscroll-${agentId}`);
    
    if (!btn) return;
    
    state.isAutoScrollEnabled = !state.isAutoScrollEnabled;
    btn.classList.toggle('active', state.isAutoScrollEnabled);
    
    console.log(`[Agent-${agentId}] Auto-scroll ${state.isAutoScrollEnabled ? 'enabled' : 'disabled'}`);
}

/**
 * Expand input area for specific agent
 */
function expandAgentInput(agentId) {
    const state = getAgentState(agentId);
    const container = document.querySelector(`#agent-${agentId} .agent-input-container`);
    
    if (!container || state.isExpanded) return;
    
    state.isExpanded = true;
    container.classList.add('expanded');
    
    // Focus textarea
    const textarea = document.getElementById(`agent-input-${agentId}`);
    if (textarea) {
        textarea.focus();
    }
    
    // Auto-scroll messages
    setTimeout(() => {
        const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
        if (messagesContainer && state.isAutoScrollEnabled) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }, 100);
    
    console.log(`[Agent-${agentId}] Input expanded`);
}

/**
 * Collapse input area for specific agent
 */
function collapseAgentInput(agentId) {
    const state = getAgentState(agentId);
    const container = document.querySelector(`#agent-${agentId} .agent-input-container`);
    
    if (!container || !state.isExpanded) return;
    
    state.isExpanded = false;
    container.classList.remove('expanded');
    
    console.log(`[Agent-${agentId}] Input collapsed`);
}

/**
 * Show prompt library for specific agent
 */
function showAgentPromptLibrary(agentId) {
    // TODO: Implement prompt library for agents
    // Should filter prompts relevant to agent's thread/context
    console.log(`[Agent-${agentId}] Prompt library requested`);
    alert(`Prompt library for Agent ${agentId} (to be implemented)`);
}
```

---

### **Phase 4: Transcription Integration**

#### **Modified TranscriptionSidebarController**
```javascript
// Update SharedTranscriptionState to support agent targets
window.SharedTranscriptionState.startRecording = function(target = 'chat') {
    this.currentTarget = target; // 'chat', 'agent-1', 'agent-2', 'agent-3'
    
    // Start browser speech recognition
    // ...
    
    console.log(`[TRANSCRIPTION] Started for target: ${target}`);
};

// When transcript is received, route to correct input
window.SharedTranscriptionState.on('transcript', (final, interim) => {
    const target = this.currentTarget;
    
    if (target === 'chat') {
        // Route to Prime chat input
        const chatInput = document.getElementById('ai-chat-input');
        if (chatInput) {
            chatInput.value += final;
        }
    } else if (target.startsWith('agent-')) {
        // Route to specific agent input
        const agentId = target.replace('agent-', '');
        const agentInput = document.getElementById(`agent-input-${agentId}`);
        if (agentInput) {
            agentInput.value += final;
        }
    }
});
```

---

### **Phase 5: Event Handlers**

#### **Input Container Click/Focus Handlers**
```javascript
// Setup for each agent when column is created
function setupAgentInputHandlers(agentId) {
    const container = document.querySelector(`#agent-${agentId} .agent-input-container`);
    const textarea = document.getElementById(`agent-input-${agentId}`);
    
    if (!container || !textarea) return;
    
    // Click collapsed bar to expand
    container.addEventListener('click', (e) => {
        if (!getAgentState(agentId).isExpanded && e.target === container) {
            expandAgentInput(agentId);
        }
    });
    
    // Focus textarea to expand
    textarea.addEventListener('focus', () => {
        expandAgentInput(agentId);
    });
    
    // Blur to collapse (if empty)
    textarea.addEventListener('blur', () => {
        setTimeout(() => {
            if (document.activeElement !== textarea && textarea.value.trim() === '') {
                collapseAgentInput(agentId);
            }
        }, 200); // Delay to allow button clicks
    });
    
    // Enter to send (Shift+Enter for new line)
    textarea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendAgentMessage(agentId);
        }
    });
    
    console.log(`[Agent-${agentId}] Input handlers initialized`);
}
```

---

## 🔄 Implementation Steps

### **Step 1: Update agent-column.js** (Create template)
- Replace simple input area with expandable container
- Add all 6 buttons
- Add feedback area HTML
- Parameterize all IDs with `{agentId}`

### **Step 2: Add CSS** (business-ai-platform-v2.html)
- Copy Prime CSS classes
- Rename `.ai-chat-*` → `.agent-*`
- Add to existing `<style>` section

### **Step 3: Create agent-input-manager.js** (New file)
- Implement state management
- Implement all toggle functions
- Export to window scope

### **Step 4: Update agent-js.js**
- Call `setupAgentInputHandlers(agentId)` in `createAgentColumn()`
- Update `loadThreadIntoAgent()` to show expanded input
- Update `updateAgentHeader()` to handle expanded state

### **Step 5: Update transcription integration**
- Modify `SharedTranscriptionState` to support agent targets
- Route transcripts to correct agent textarea
- Update microphone button states per-agent

### **Step 6: Testing**
- Test each agent independently
- Test multiple agents with different states
- Test transcription routing
- Test feedback system
- Test all buttons

---

## ⚠️ Critical Considerations

### **Isolation Requirements**
1. ✅ **Separate state per agent** - Use `window.AgentInputStates[agentId]`
2. ✅ **Unique IDs** - All elements suffixed with `-{agentId}`
3. ✅ **Independent feedback** - Each agent has own feedback textarea
4. ✅ **Independent transcription** - Route to correct agent via target parameter
5. ✅ **Independent expansion** - Agent-1 can be expanded while Agent-2 collapsed

### **Performance Considerations**
- Don't initialize all agents eagerly - wait for column creation
- Clean up event listeners when agent column is closed
- Debounce textarea auto-resize
- Throttle scroll events

### **Accessibility**
- Add `aria-label` to all buttons
- Add `role="region"` to feedback area
- Add `aria-expanded` to input container
- Support keyboard navigation

---

## 📊 Success Criteria

- [ ] Each agent has expandable input container with chevron animation
- [ ] Each agent has independent feedback area
- [ ] Each agent has 6 buttons (prompt, autoscroll, feedback, mic, attach, send)
- [ ] Each agent can record transcription independently
- [ ] Transcription routes to correct agent's input
- [ ] Feedback system works per-agent
- [ ] Auto-scroll toggle works per-agent
- [ ] All state is column-specific (no cross-contamination)
- [ ] Performance remains smooth with 3 agents active

---

**Next Action:** Implement Step 1 (Update agent-column.js template)

**Estimated Implementation Time:** 4-6 hours for complete implementation and testing

**Last Updated:** December 1, 2025
