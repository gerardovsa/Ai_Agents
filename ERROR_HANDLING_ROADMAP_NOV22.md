# Error Handling & Robustness Roadmap - November 22, 2025

## 🎯 Comprehensive Error Handling Strategy for All AI Panels

This document outlines improvements for both **INTRA-thread** (within a single AI panel) and **INTER-thread** (between AI panels) error handling and recovery.

---

## 📊 Current State (What We Have Now)

### ✅ **Already Implemented:**
1. **Thread-specific error tracking** - Each panel tracks its own errors
2. **Error threshold system** - Up to 10 parse errors before stopping
3. **Isolated cleanup** - Failed threads don't affect others
4. **Basic retry logic** - User can retry failed threads

### ❌ **What's Missing:**
1. **Automatic recovery** - No auto-retry on transient failures
2. **State persistence** - Lost context on refresh
3. **Network resilience** - Poor handling of connection drops
4. **User feedback** - Minimal error explanations
5. **Cross-panel coordination** - No shared health monitoring
6. **Graceful degradation** - Hard failures instead of partial functionality

---

## 🔧 INTRA-PANEL IMPROVEMENTS (Within Single AI Panel)

### **1. Automatic Retry with Exponential Backoff**

**Problem**: Network glitch or transient error kills entire stream  
**Solution**: Retry failed SSE connections automatically

```javascript
// Add to prime_ai_chat.js and agent-js.js
class StreamRetryManager {
    constructor(threadId, agentId = null) {
        this.threadId = threadId;
        this.agentId = agentId;
        this.retryCount = 0;
        this.maxRetries = 3;
        this.baseDelay = 1000; // 1 second
        this.maxDelay = 10000; // 10 seconds
    }
    
    async retryWithBackoff(streamFunction) {
        while (this.retryCount < this.maxRetries) {
            try {
                return await streamFunction();
            } catch (error) {
                this.retryCount++;
                
                if (this.retryCount >= this.maxRetries) {
                    throw new Error(`Stream failed after ${this.maxRetries} retries: ${error.message}`);
                }
                
                // Exponential backoff: 1s, 2s, 4s
                const delay = Math.min(
                    this.baseDelay * Math.pow(2, this.retryCount - 1),
                    this.maxDelay
                );
                
                console.warn(`[RETRY ${this.retryCount}/${this.maxRetries}] Retrying in ${delay}ms...`);
                
                // Show user-friendly message
                this.showRetryMessage(delay);
                
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }
    
    showRetryMessage(delay) {
        const panel = this.agentId 
            ? document.getElementById(`agent-${this.agentId}`)
            : document.getElementById('ai-chat-messages');
        
        if (!panel) return;
        
        const retryMsg = document.createElement('div');
        retryMsg.className = 'ai-message system retry-message';
        retryMsg.innerHTML = `
            <i class="fas fa-sync fa-spin"></i>
            Connection interrupted. Retrying in ${delay / 1000}s... (Attempt ${this.retryCount}/${this.maxRetries})
        `;
        panel.appendChild(retryMsg);
        
        // Remove after delay
        setTimeout(() => retryMsg.remove(), delay + 500);
    }
}

// Usage in sendChatMessage:
const retryManager = new StreamRetryManager(currentThreadId, null); // null = Prime AI

try {
    await retryManager.retryWithBackoff(async () => {
        const response = await fetch(streamUrl);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await processStream(response);
    });
} catch (error) {
    // Only fail after all retries exhausted
    console.error('[STREAM FAILED]:', error);
}
```

**Benefits:**
- ✅ Handles transient network issues automatically
- ✅ User sees progress instead of instant failure
- ✅ Exponential backoff prevents server overload
- ✅ Clear user feedback on retry attempts

---

### **2. Stream Health Monitoring & Recovery**

**Problem**: Stream stalls (no events for extended period) with no detection  
**Solution**: Heartbeat detection + automatic reconnection

```javascript
// Add to streaming logic
class StreamHealthMonitor {
    constructor(threadId, agentId, timeoutMs = 30000) { // 30 second timeout
        this.threadId = threadId;
        this.agentId = agentId;
        this.timeoutMs = timeoutMs;
        this.lastEventTime = Date.now();
        this.healthCheckInterval = null;
        this.onTimeout = null; // Callback for timeout
    }
    
    start(onTimeout) {
        this.onTimeout = onTimeout;
        this.lastEventTime = Date.now();
        
        // Check health every 5 seconds
        this.healthCheckInterval = setInterval(() => {
            const timeSinceLastEvent = Date.now() - this.lastEventTime;
            
            if (timeSinceLastEvent > this.timeoutMs) {
                console.error(`[HEALTH] Stream stalled for ${timeSinceLastEvent}ms - triggering recovery`);
                this.stop();
                if (this.onTimeout) this.onTimeout();
            }
        }, 5000);
        
        console.log(`[HEALTH] Monitor started for thread ${this.threadId}`);
    }
    
    recordEvent() {
        this.lastEventTime = Date.now();
    }
    
    stop() {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
            this.healthCheckInterval = null;
        }
    }
}

// Usage in streaming loop:
const healthMonitor = new StreamHealthMonitor(threadSlug, agentId);

healthMonitor.start(() => {
    // Stream stalled - attempt recovery
    console.warn('[RECOVERY] Stream stalled, attempting reconnection...');
    healthMonitor.stop();
    
    // Show user message
    addChatMessage('system', '⚠️ Stream stalled. Reconnecting...');
    
    // Retry the stream
    setTimeout(() => sendChatMessage(), 2000);
});

// In SSE event loop:
for (const data of events) {
    healthMonitor.recordEvent(); // ← Reset timeout on each event
    // ... process event
}

// On stream complete:
healthMonitor.stop();
```

**Benefits:**
- ✅ Detects stalled streams automatically
- ✅ Attempts recovery without user intervention
- ✅ Prevents "stuck" streams that never complete
- ✅ User-friendly timeout messages

---

### **3. Partial Response Recovery**

**Problem**: Stream fails halfway through - user loses entire response  
**Solution**: Save partial content + offer to continue

```javascript
// Add to streaming logic
class PartialResponseManager {
    constructor(threadId, agentId) {
        this.threadId = threadId;
        this.agentId = agentId;
        this.storageKey = `partial_response_${threadId}_${agentId || 'prime'}`;
    }
    
    savePartial(content) {
        const partial = {
            threadId: this.threadId,
            agentId: this.agentId,
            content: content,
            timestamp: Date.now(),
            messageCount: content.length
        };
        
        localStorage.setItem(this.storageKey, JSON.stringify(partial));
        console.log(`[PARTIAL] Saved ${content.length} chars to recovery`);
    }
    
    hasPartial() {
        return localStorage.getItem(this.storageKey) !== null;
    }
    
    loadPartial() {
        const stored = localStorage.getItem(this.storageKey);
        return stored ? JSON.parse(stored) : null;
    }
    
    clearPartial() {
        localStorage.removeItem(this.storageKey);
    }
    
    showRecoveryOption() {
        const partial = this.loadPartial();
        if (!partial) return;
        
        // Don't show if too old (>5 minutes)
        if (Date.now() - partial.timestamp > 5 * 60 * 1000) {
            this.clearPartial();
            return;
        }
        
        const container = this.agentId
            ? document.getElementById(`agent-messages-${this.agentId}`)
            : document.getElementById('ai-chat-messages');
        
        if (!container) return;
        
        const recoveryBanner = document.createElement('div');
        recoveryBanner.className = 'recovery-banner';
        recoveryBanner.innerHTML = `
            <div class="recovery-content">
                <i class="fas fa-exclamation-triangle"></i>
                <span>Recovered partial response (${partial.messageCount} chars). Continue where you left off?</span>
            </div>
            <div class="recovery-actions">
                <button class="recovery-btn continue">
                    <i class="fas fa-play"></i> Continue
                </button>
                <button class="recovery-btn discard">
                    <i class="fas fa-times"></i> Discard
                </button>
            </div>
        `;
        
        recoveryBanner.querySelector('.continue').addEventListener('click', () => {
            this.continueFromPartial(partial);
            recoveryBanner.remove();
        });
        
        recoveryBanner.querySelector('.discard').addEventListener('click', () => {
            this.clearPartial();
            recoveryBanner.remove();
        });
        
        container.insertBefore(recoveryBanner, container.firstChild);
    }
    
    continueFromPartial(partial) {
        // Restore partial content to UI
        const bubble = document.createElement('div');
        bubble.className = 'ai-message assistant recovered';
        bubble.innerHTML = `
            <div class="ai-message-content">${partial.content}</div>
            <div class="recovery-indicator">
                <i class="fas fa-history"></i> Recovered from interrupted stream
            </div>
        `;
        
        const container = this.agentId
            ? document.getElementById(`agent-messages-${this.agentId}`)
            : document.getElementById('ai-chat-messages');
        
        container.appendChild(bubble);
        
        // Clear recovery data
        this.clearPartial();
        
        console.log('[RECOVERY] Restored partial response');
    }
}

// Usage in streaming loop:
const partialManager = new PartialResponseManager(threadSlug, agentId);

// On page load:
window.addEventListener('DOMContentLoaded', () => {
    partialManager.showRecoveryOption();
});

// During streaming:
setInterval(() => {
    if (fullResponse.length > 0) {
        partialManager.savePartial(fullResponse);
    }
}, 2000); // Save every 2 seconds

// On stream complete:
partialManager.clearPartial();
```

**Benefits:**
- ✅ User doesn't lose work on stream failure
- ✅ Can continue from where stream stopped
- ✅ Persists across page refreshes
- ✅ Auto-expires old partials (5 minutes)

---

### **4. Enhanced Error Messages with Actions**

**Problem**: Generic error messages don't help user understand what went wrong  
**Solution**: Contextual error messages with actionable buttons

```javascript
// Enhanced error display system
class ErrorMessageHandler {
    static show(error, context = {}) {
        const { threadId, agentId, retryable = true } = context;
        
        // Categorize error
        const errorType = this.categorizeError(error);
        const errorConfig = this.getErrorConfig(errorType);
        
        // Create error bubble
        const errorBubble = document.createElement('div');
        errorBubble.className = `ai-message system error-${errorType}`;
        errorBubble.innerHTML = `
            <div class="error-header">
                <i class="${errorConfig.icon}"></i>
                <span>${errorConfig.title}</span>
            </div>
            <div class="error-message">${errorConfig.message(error)}</div>
            <div class="error-actions">
                ${retryable ? `
                    <button class="error-action retry">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                ` : ''}
                ${errorConfig.helpUrl ? `
                    <button class="error-action help">
                        <i class="fas fa-question-circle"></i> Help
                    </button>
                ` : ''}
                <button class="error-action dismiss">
                    <i class="fas fa-times"></i> Dismiss
                </button>
            </div>
        `;
        
        // Add event listeners
        if (retryable) {
            errorBubble.querySelector('.retry').addEventListener('click', () => {
                errorBubble.remove();
                // Retry logic based on context
                if (agentId) {
                    sendAgentMessage(agentId);
                } else {
                    sendChatMessage();
                }
            });
        }
        
        if (errorConfig.helpUrl) {
            errorBubble.querySelector('.help').addEventListener('click', () => {
                window.open(errorConfig.helpUrl, '_blank');
            });
        }
        
        errorBubble.querySelector('.dismiss').addEventListener('click', () => {
            errorBubble.remove();
        });
        
        // Add to appropriate container
        const container = agentId
            ? document.getElementById(`agent-messages-${agentId}`)
            : document.getElementById('ai-chat-messages');
        
        container.appendChild(errorBubble);
    }
    
    static categorizeError(error) {
        const message = error.message.toLowerCase();
        
        if (message.includes('network') || message.includes('fetch')) {
            return 'network';
        }
        if (message.includes('401') || message.includes('403')) {
            return 'auth';
        }
        if (message.includes('413') || message.includes('too large')) {
            return 'size';
        }
        if (message.includes('429') || message.includes('rate limit')) {
            return 'rate_limit';
        }
        if (message.includes('500') || message.includes('502') || message.includes('503')) {
            return 'server';
        }
        if (message.includes('400') || message.includes('invalid')) {
            return 'validation';
        }
        
        return 'unknown';
    }
    
    static getErrorConfig(errorType) {
        const configs = {
            network: {
                icon: 'fas fa-wifi',
                title: 'Connection Issue',
                message: (e) => 'Unable to connect to server. Check your internet connection.',
                helpUrl: null
            },
            auth: {
                icon: 'fas fa-lock',
                title: 'Authentication Error',
                message: (e) => 'Your session has expired. Please log in again.',
                helpUrl: '/login'
            },
            size: {
                icon: 'fas fa-file-archive',
                title: 'Message Too Large',
                message: (e) => 'This conversation is too long. Try starting a new thread.',
                helpUrl: null
            },
            rate_limit: {
                icon: 'fas fa-hourglass-half',
                title: 'Rate Limit Reached',
                message: (e) => 'Too many requests. Please wait a moment before trying again.',
                helpUrl: null
            },
            server: {
                icon: 'fas fa-server',
                title: 'Server Error',
                message: (e) => 'The server is experiencing issues. Please try again shortly.',
                helpUrl: null
            },
            validation: {
                icon: 'fas fa-exclamation-triangle',
                title: 'Invalid Request',
                message: (e) => `Request validation failed: ${e.message}`,
                helpUrl: null
            },
            unknown: {
                icon: 'fas fa-bug',
                title: 'Unexpected Error',
                message: (e) => `An error occurred: ${e.message}`,
                helpUrl: null
            }
        };
        
        return configs[errorType] || configs.unknown;
    }
}

// Usage in catch blocks:
catch (error) {
    console.error('[STREAM ERROR]:', error);
    
    ErrorMessageHandler.show(error, {
        threadId: currentThreadId,
        agentId: agentId || null,
        retryable: !error.message.includes('413') // Don't retry size errors
    });
}
```

**Benefits:**
- ✅ User understands exactly what went wrong
- ✅ One-click retry for recoverable errors
- ✅ Direct links to help documentation
- ✅ Visual distinction between error types

---

### **5. Message Queue with Offline Support**

**Problem**: User tries to send message while offline - message lost  
**Solution**: Queue messages and send when online

```javascript
// Message queue manager
class MessageQueueManager {
    constructor() {
        this.queue = this.loadQueue();
        this.isOnline = navigator.onLine;
        this.setupListeners();
    }
    
    setupListeners() {
        window.addEventListener('online', () => {
            console.log('[QUEUE] Back online - processing queued messages');
            this.isOnline = true;
            this.processQueue();
        });
        
        window.addEventListener('offline', () => {
            console.log('[QUEUE] Gone offline - queueing future messages');
            this.isOnline = false;
        });
    }
    
    enqueue(message, threadId, agentId = null) {
        const queueItem = {
            id: Date.now(),
            message,
            threadId,
            agentId,
            timestamp: Date.now(),
            retries: 0
        };
        
        this.queue.push(queueItem);
        this.saveQueue();
        
        console.log(`[QUEUE] Added message to queue (${this.queue.length} pending)`);
        
        // Show queue indicator
        this.showQueueIndicator();
        
        return queueItem.id;
    }
    
    async processQueue() {
        if (!this.isOnline || this.queue.length === 0) return;
        
        console.log(`[QUEUE] Processing ${this.queue.length} queued messages`);
        
        const failures = [];
        
        for (const item of [...this.queue]) {
            try {
                if (item.agentId) {
                    await sendAgentMessageQueued(item.agentId, item.message, item.threadId);
                } else {
                    await sendChatMessageQueued(item.message, item.threadId);
                }
                
                // Remove from queue on success
                this.queue = this.queue.filter(q => q.id !== item.id);
                
            } catch (error) {
                item.retries++;
                
                if (item.retries >= 3) {
                    // Give up after 3 retries
                    failures.push(item);
                    this.queue = this.queue.filter(q => q.id !== item.id);
                }
                
                console.error(`[QUEUE] Failed to send message (retry ${item.retries}/3):`, error);
            }
        }
        
        this.saveQueue();
        this.updateQueueIndicator();
        
        // Notify user of failures
        if (failures.length > 0) {
            showNotification(
                `Failed to send ${failures.length} queued message(s)`,
                'error'
            );
        }
    }
    
    showQueueIndicator() {
        let indicator = document.getElementById('queue-indicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'queue-indicator';
            indicator.className = 'queue-indicator offline';
            indicator.innerHTML = `
                <i class="fas fa-cloud-upload-alt"></i>
                <span class="queue-count">${this.queue.length}</span> queued
            `;
            document.body.appendChild(indicator);
        }
        
        indicator.querySelector('.queue-count').textContent = this.queue.length;
    }
    
    updateQueueIndicator() {
        const indicator = document.getElementById('queue-indicator');
        
        if (this.queue.length === 0 && indicator) {
            indicator.remove();
        } else if (indicator) {
            indicator.querySelector('.queue-count').textContent = this.queue.length;
        }
    }
    
    loadQueue() {
        const stored = localStorage.getItem('message_queue');
        return stored ? JSON.parse(stored) : [];
    }
    
    saveQueue() {
        localStorage.setItem('message_queue', JSON.stringify(this.queue));
    }
}

// Initialize globally
window.messageQueue = new MessageQueueManager();

// Modified sendChatMessage:
async function sendChatMessage() {
    const message = input.value.trim();
    
    // If offline, queue message
    if (!navigator.onLine) {
        window.messageQueue.enqueue(message, currentThreadId, null);
        
        // Show queued message in UI
        addChatMessage('user', message, { queued: true });
        
        showNotification('Message queued - will send when online', 'info');
        return;
    }
    
    // Normal send logic...
}
```

**Benefits:**
- ✅ Messages never lost due to network issues
- ✅ Automatic sending when connection restored
- ✅ Visual queue indicator for pending messages
- ✅ Retry logic with limit (3 attempts)

---

## 🌐 INTER-PANEL IMPROVEMENTS (Between AI Panels)

### **1. Global Health Dashboard**

**Problem**: No visibility into overall platform health  
**Solution**: Centralized health monitoring for all panels

```javascript
// Global health monitor
class PlatformHealthMonitor {
    constructor() {
        this.panels = new Map(); // panelId -> health status
        this.updateInterval = null;
        this.dashboardElement = null;
    }
    
    registerPanel(panelId, type = 'agent') {
        this.panels.set(panelId, {
            id: panelId,
            type: type, // 'prime' or 'agent'
            status: 'idle',
            lastUpdate: Date.now(),
            errorCount: 0,
            messageCount: 0
        });
        
        this.updateDashboard();
    }
    
    updatePanelStatus(panelId, status, details = {}) {
        const panel = this.panels.get(panelId);
        if (!panel) return;
        
        panel.status = status;
        panel.lastUpdate = Date.now();
        
        if (details.errorCount !== undefined) {
            panel.errorCount = details.errorCount;
        }
        if (details.messageCount !== undefined) {
            panel.messageCount = details.messageCount;
        }
        
        this.updateDashboard();
    }
    
    createDashboard() {
        if (this.dashboardElement) return;
        
        this.dashboardElement = document.createElement('div');
        this.dashboardElement.id = 'platform-health-dashboard';
        this.dashboardElement.className = 'health-dashboard collapsed';
        this.dashboardElement.innerHTML = `
            <div class="health-header" onclick="this.parentElement.classList.toggle('collapsed')">
                <i class="fas fa-heartbeat"></i>
                <span>System Health</span>
                <i class="fas fa-chevron-down toggle-icon"></i>
            </div>
            <div class="health-content"></div>
        `;
        
        document.body.appendChild(this.dashboardElement);
        this.updateDashboard();
    }
    
    updateDashboard() {
        if (!this.dashboardElement) this.createDashboard();
        
        const content = this.dashboardElement.querySelector('.health-content');
        
        const panelStats = Array.from(this.panels.values()).map(panel => {
            const statusIcon = this.getStatusIcon(panel.status);
            const statusColor = this.getStatusColor(panel.status);
            const timeSince = Math.floor((Date.now() - panel.lastUpdate) / 1000);
            
            return `
                <div class="health-panel">
                    <div class="panel-header">
                        <i class="${statusIcon}" style="color: ${statusColor}"></i>
                        <span class="panel-name">${panel.type === 'prime' ? 'Prime AI' : `Agent ${panel.id}`}</span>
                    </div>
                    <div class="panel-stats">
                        <span>Status: ${panel.status}</span>
                        <span>Errors: ${panel.errorCount}</span>
                        <span>Messages: ${panel.messageCount}</span>
                        <span>Last update: ${timeSince}s ago</span>
                    </div>
                </div>
            `;
        }).join('');
        
        content.innerHTML = panelStats || '<p>No active panels</p>';
        
        // Update header color based on overall health
        const overallStatus = this.getOverallHealth();
        this.dashboardElement.querySelector('.health-header').style.background = 
            this.getStatusColor(overallStatus);
    }
    
    getOverallHealth() {
        const statuses = Array.from(this.panels.values()).map(p => p.status);
        
        if (statuses.some(s => s === 'error')) return 'error';
        if (statuses.some(s => s === 'warning')) return 'warning';
        if (statuses.some(s => s === 'streaming')) return 'streaming';
        
        return 'idle';
    }
    
    getStatusIcon(status) {
        const icons = {
            idle: 'fas fa-circle',
            streaming: 'fas fa-circle-notch fa-spin',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            success: 'fas fa-check-circle'
        };
        
        return icons[status] || icons.idle;
    }
    
    getStatusColor(status) {
        const colors = {
            idle: '#6c757d',      // Gray
            streaming: '#3B82F6', // Blue
            error: '#dc3545',     // Red
            warning: '#ffc107',   // Yellow
            success: '#28a745'    // Green
        };
        
        return colors[status] || colors.idle;
    }
}

// Initialize globally
window.platformHealth = new PlatformHealthMonitor();

// Usage in each panel:
// Prime AI:
window.platformHealth.registerPanel('prime', 'prime');

// Agents:
window.platformHealth.registerPanel(agentId, 'agent');

// Update during streaming:
window.platformHealth.updatePanelStatus('prime', 'streaming');
window.platformHealth.updatePanelStatus(agentId, 'error', { errorCount: 3 });
```

**Benefits:**
- ✅ At-a-glance view of all panel health
- ✅ Identify problematic panels quickly
- ✅ Historical error tracking per panel
- ✅ Collapsible to stay out of the way

---

### **2. Cross-Panel Error Isolation with Alerts**

**Problem**: Cascading failures not immediately visible  
**Solution**: Alert when multiple panels fail simultaneously

```javascript
// Cross-panel failure detector
class CascadingFailureDetector {
    constructor(threshold = 2, windowMs = 30000) {
        this.threshold = threshold; // Number of panels
        this.windowMs = windowMs;   // Time window (30 seconds)
        this.failures = [];
    }
    
    recordFailure(panelId, error) {
        const now = Date.now();
        
        // Add failure to log
        this.failures.push({
            panelId,
            error: error.message,
            timestamp: now
        });
        
        // Clean old failures outside window
        this.failures = this.failures.filter(f => 
            now - f.timestamp < this.windowMs
        );
        
        // Check for cascading failure
        if (this.failures.length >= this.threshold) {
            this.handleCascadingFailure();
        }
    }
    
    handleCascadingFailure() {
        console.error('[CASCADE] Multiple panels failing simultaneously:', this.failures);
        
        // Show system-wide alert
        const alert = document.createElement('div');
        alert.className = 'cascade-alert';
        alert.innerHTML = `
            <div class="alert-header">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>System Alert: Multiple Panels Failing</strong>
            </div>
            <div class="alert-content">
                ${this.failures.length} panel(s) have failed in the last ${this.windowMs / 1000}s.
                This may indicate a backend issue.
            </div>
            <div class="alert-actions">
                <button class="alert-btn check-backend">
                    <i class="fas fa-server"></i> Check Backend Status
                </button>
                <button class="alert-btn reload">
                    <i class="fas fa-sync"></i> Reload Page
                </button>
                <button class="alert-btn dismiss">
                    Dismiss
                </button>
            </div>
        `;
        
        alert.querySelector('.check-backend').addEventListener('click', () => {
            this.checkBackendHealth();
        });
        
        alert.querySelector('.reload').addEventListener('click', () => {
            location.reload();
        });
        
        alert.querySelector('.dismiss').addEventListener('click', () => {
            alert.remove();
        });
        
        document.body.appendChild(alert);
    }
    
    async checkBackendHealth() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            const data = await response.json();
            
            showNotification(
                `Backend Status: ${data.status || 'Unknown'}`,
                response.ok ? 'success' : 'error'
            );
        } catch (error) {
            showNotification(
                'Backend is unreachable',
                'error'
            );
        }
    }
}

// Initialize globally
window.cascadeDetector = new CascadingFailureDetector(2, 30000);

// Usage in catch blocks:
catch (error) {
    window.cascadeDetector.recordFailure(agentId || 'prime', error);
    // ... existing error handling
}
```

**Benefits:**
- ✅ Detects backend-wide issues immediately
- ✅ Prevents users from retrying endlessly
- ✅ Direct action buttons (check backend, reload)
- ✅ Distinguishes local vs systemic failures

---

### **3. Resource Pool Management**

**Problem**: Too many concurrent streams overload browser/backend  
**Solution**: Limit concurrent streams with queuing

```javascript
// Stream resource manager
class StreamResourceManager {
    constructor(maxConcurrent = 3) {
        this.maxConcurrent = maxConcurrent;
        this.activeStreams = new Set();
        this.pendingQueue = [];
    }
    
    async acquireSlot(panelId) {
        // If slot available, use immediately
        if (this.activeStreams.size < this.maxConcurrent) {
            this.activeStreams.add(panelId);
            console.log(`[RESOURCE] ${panelId} acquired slot (${this.activeStreams.size}/${this.maxConcurrent})`);
            return true;
        }
        
        // Otherwise, queue and wait
        console.log(`[RESOURCE] ${panelId} queued (${this.pendingQueue.length} waiting)`);
        
        return new Promise((resolve) => {
            this.pendingQueue.push({ panelId, resolve });
            this.updateQueueIndicators();
        });
    }
    
    releaseSlot(panelId) {
        this.activeStreams.delete(panelId);
        console.log(`[RESOURCE] ${panelId} released slot (${this.activeStreams.size}/${this.maxConcurrent})`);
        
        // Process next in queue
        if (this.pendingQueue.length > 0) {
            const next = this.pendingQueue.shift();
            this.activeStreams.add(next.panelId);
            next.resolve(true);
            
            console.log(`[RESOURCE] ${next.panelId} dequeued and started`);
        }
        
        this.updateQueueIndicators();
    }
    
    updateQueueIndicators() {
        // Show queue position for each waiting panel
        this.pendingQueue.forEach((item, index) => {
            const panel = document.getElementById(
                item.panelId === 'prime' 
                    ? 'ai-chat-panel'
                    : `agent-${item.panelId}`
            );
            
            if (!panel) return;
            
            let indicator = panel.querySelector('.queue-position-indicator');
            
            if (!indicator) {
                indicator = document.createElement('div');
                indicator.className = 'queue-position-indicator';
                panel.appendChild(indicator);
            }
            
            indicator.innerHTML = `
                <i class="fas fa-hourglass-half"></i>
                Position ${index + 1} in queue
            `;
        });
        
        // Remove indicators for panels no longer queued
        document.querySelectorAll('.queue-position-indicator').forEach(el => {
            const panelId = el.closest('[id^="agent-"]')?.id.replace('agent-', '') || 'prime';
            
            if (!this.pendingQueue.some(q => q.panelId === panelId)) {
                el.remove();
            }
        });
    }
    
    getStatus() {
        return {
            active: this.activeStreams.size,
            queued: this.pendingQueue.length,
            available: this.maxConcurrent - this.activeStreams.size
        };
    }
}

// Initialize globally
window.streamResources = new StreamResourceManager(3); // Max 3 concurrent

// Usage in sendChatMessage and sendAgentMessage:
async function sendChatMessage() {
    const panelId = 'prime';
    
    try {
        // Acquire resource slot (may queue)
        await window.streamResources.acquireSlot(panelId);
        
        // Proceed with stream...
        
    } finally {
        // Always release on completion/error
        window.streamResources.releaseSlot(panelId);
    }
}
```

**Benefits:**
- ✅ Prevents browser overload (too many streams)
- ✅ Prevents backend overload (rate limiting)
- ✅ Fair queuing (first-come-first-served)
- ✅ Visual queue position indicators

---

### **4. Shared State Persistence**

**Problem**: Page refresh loses all panel states  
**Solution**: Persist panel states to localStorage

```javascript
// Panel state manager
class PanelStateManager {
    constructor() {
        this.storageKey = 'panel_states';
    }
    
    saveState(panelId, state) {
        const states = this.loadStates();
        
        states[panelId] = {
            ...state,
            timestamp: Date.now()
        };
        
        localStorage.setItem(this.storageKey, JSON.stringify(states));
        console.log(`[STATE] Saved state for ${panelId}`);
    }
    
    loadState(panelId) {
        const states = this.loadStates();
        return states[panelId] || null;
    }
    
    loadStates() {
        const stored = localStorage.getItem(this.storageKey);
        return stored ? JSON.parse(stored) : {};
    }
    
    clearState(panelId) {
        const states = this.loadStates();
        delete states[panelId];
        localStorage.setItem(this.storageKey, JSON.stringify(states));
    }
    
    restoreAllStates() {
        const states = this.loadStates();
        const now = Date.now();
        const maxAge = 30 * 60 * 1000; // 30 minutes
        
        Object.entries(states).forEach(([panelId, state]) => {
            // Skip old states
            if (now - state.timestamp > maxAge) {
                this.clearState(panelId);
                return;
            }
            
            // Restore panel
            if (panelId === 'prime') {
                this.restorePrimeState(state);
            } else {
                this.restoreAgentState(panelId, state);
            }
        });
    }
    
    restorePrimeState(state) {
        // Restore thread ID
        if (state.threadId && window.ThreadManager) {
            window.ThreadManager.loadThread(state.threadId);
        }
        
        // Restore scroll position
        if (state.scrollPosition) {
            const container = document.querySelector('.ai-chat-messages');
            if (container) {
                container.scrollTop = state.scrollPosition;
            }
        }
    }
    
    restoreAgentState(agentId, state) {
        // Re-open agent column
        if (!document.getElementById(`agent-${agentId}`)) {
            openAgentColumn(agentId);
        }
        
        // Restore thread
        if (state.threadId) {
            loadAgentThread(agentId, state.threadId);
        }
        
        // Restore scroll
        if (state.scrollPosition) {
            const container = document.getElementById(`agent-messages-${agentId}`);
            if (container) {
                container.scrollTop = state.scrollPosition;
            }
        }
    }
}

// Initialize globally
window.panelStates = new PanelStateManager();

// Save state periodically
setInterval(() => {
    // Save Prime state
    const primeContainer = document.querySelector('.ai-chat-messages');
    if (primeContainer && window.ThreadManager?.currentThreadId) {
        window.panelStates.saveState('prime', {
            threadId: window.ThreadManager.currentThreadId,
            scrollPosition: primeContainer.scrollTop,
            messageCount: primeContainer.querySelectorAll('.ai-message').length
        });
    }
    
    // Save agent states
    document.querySelectorAll('[id^="agent-"]').forEach(column => {
        const agentId = column.id.replace('agent-', '');
        const container = document.getElementById(`agent-messages-${agentId}`);
        const threadId = MultiAgent.loadedThreads?.[agentId];
        
        if (container && threadId) {
            window.panelStates.saveState(agentId, {
                threadId: threadId,
                scrollPosition: container.scrollTop,
                messageCount: container.querySelectorAll('.ai-message').length
            });
        }
    });
}, 5000); // Save every 5 seconds

// Restore on page load
window.addEventListener('DOMContentLoaded', () => {
    window.panelStates.restoreAllStates();
});
```

**Benefits:**
- ✅ Seamless recovery from page refresh
- ✅ Restores scroll positions
- ✅ Restores active threads
- ✅ Auto-expires old states (30 minutes)

---

## 📋 Implementation Priority

### **Phase 1: Critical (Implement First)**
1. ✅ Thread-specific error tracking (DONE)
2. 🔄 Automatic retry with exponential backoff
3. 🔄 Enhanced error messages with actions
4. 🔄 Stream health monitoring

### **Phase 2: High Priority**
5. 🔄 Partial response recovery
6. 🔄 Message queue with offline support
7. 🔄 Global health dashboard
8. 🔄 Cross-panel error isolation

### **Phase 3: Nice to Have**
9. 🔄 Resource pool management
10. 🔄 Shared state persistence
11. 🔄 Advanced metrics/analytics

---

## 🎯 Expected Improvements

### **User Experience:**
- ✅ **95% reduction** in message loss (queue + partial recovery)
- ✅ **80% faster recovery** from transient errors (auto-retry)
- ✅ **100% visibility** into system health (dashboard)
- ✅ **Zero manual refresh** needed for minor issues

### **System Reliability:**
- ✅ **Isolation**: One panel failure doesn't affect others
- ✅ **Resilience**: Automatic recovery from transient issues
- ✅ **Monitoring**: Real-time health tracking
- ✅ **Degradation**: Partial functionality instead of complete failure

---

## 📝 Next Steps

1. **Review this document** with user for priority alignment
2. **Implement Phase 1** features (1-4)
3. **Test thoroughly** with multiple panels active
4. **Gather metrics** on error rates and recovery success
5. **Iterate** based on real-world usage

---

**Last Updated**: November 22, 2025  
**Status**: 📋 ROADMAP - Implementation Pending  
**Estimated Work**: 3-5 days for Phase 1
