# AI Status Sidebar Specification - November 22, 2025

## 🎯 Purpose
Provide real-time visibility into AI agent health, streaming status, and error recovery operations across all panels (Prime AI + Agent Columns).

---

## 📊 What Should Be Tracked & Displayed

### **1. Active Streams Section**
```
🔵 ACTIVE STREAMS (3)
├─ Prime AI
│  ├─ Status: Streaming
│  ├─ Thread: wf_abc123_1732125847
│  ├─ Duration: 12.4s
│  ├─ Tokens: ~2,450 received
│  └─ Health: ✅ Normal (last event 0.3s ago)
│
├─ Agent Alpha
│  ├─ Status: Streaming
│  ├─ Thread: wf_xyz789_1732125850
│  ├─ Duration: 8.2s
│  ├─ Tokens: ~1,820 received
│  └─ Health: ⚠️ Slow (last event 4.2s ago)
│
└─ Agent Bravo
   ├─ Status: Queued (position 1)
   ├─ Thread: wf_def456_1732125852
   └─ Waiting for: Slot availability (2/3 used)
```

### **2. Error Recovery Section**
```
🔧 ERROR RECOVERY (2 Active)
├─ Prime AI - Thread wf_abc123_1732125847
│  ├─ Error: "context_length_exceeded"
│  ├─ Detected: 2.1s ago
│  ├─ Recovery Action: History reconstruction (Phase 1/3)
│  ├─ Progress: Analyzing conversation (45% complete)
│  └─ Next Step: Remove oldest messages, retry in 3s
│
└─ Agent Charlie - Thread wf_ghi789_1732125855
   ├─ Error: "rate_limit_exceeded"
   ├─ Detected: 15.3s ago
   ├─ Recovery Action: Exponential backoff (retry 2/3)
   └─ Next Retry: 4s
```

### **3. History Reconstruction Log**
```
📜 HISTORY RECONSTRUCTION (Active)
Panel: Prime AI
Thread: wf_abc123_1732125847

Step 1: ✅ Fetched conversation from backend (42 messages)
Step 2: ✅ Analyzed token count (~28,450 tokens)
Step 3: 🔄 Removing oldest messages (target: 20,000 tokens)
        ├─ Removed: 8 messages (~6,200 tokens)
        ├─ Current: ~22,250 tokens
        └─ Target: 20,000 tokens (88% progress)
Step 4: ⏳ Pending - Rebuild history array
Step 5: ⏳ Pending - Resubmit to Anthropic
```

### **4. System Health Indicators**
```
🏥 SYSTEM HEALTH
├─ Backend API: ✅ Online (latency 45ms)
├─ Anthropic API: ✅ Online (rate limit: 78% available)
├─ Active Panels: 4 (1 Prime + 3 Agents)
├─ Concurrent Streams: 2/3 slots used
├─ Message Queue: 0 pending
└─ Last Error: 2m ago (recovered successfully)
```

### **5. Token Usage Tracking**
```
🎫 TOKEN USAGE (Current Session)
├─ Prime AI: ~125,450 tokens sent
│  ├─ Input: ~98,200 tokens
│  └─ Output: ~27,250 tokens
│
├─ Agent Alpha: ~45,820 tokens
├─ Agent Bravo: ~32,140 tokens
├─ Agent Charlie: ~28,950 tokens
│
└─ Total Session: ~232,360 tokens
   └─ Estimated Cost: $2.78
```

### **6. Recent Events Timeline**
```
📅 RECENT EVENTS (Last 5 minutes)
├─ 2:34:12 PM - Prime AI: Stream started (thread: wf_abc123)
├─ 2:34:08 PM - Agent Alpha: Completed successfully (12.4s)
├─ 2:33:55 PM - Prime AI: Error recovered (context_length_exceeded)
│  └─ Action: Removed 8 messages, resubmitted successfully
├─ 2:33:40 PM - Agent Charlie: Rate limit hit, retry in 30s
└─ 2:33:22 PM - Agent Bravo: Stream queued (slot full)
```

### **7. Error Statistics**
```
📈 ERROR STATISTICS (Last Hour)
├─ Total Errors: 12
├─ Recovered Automatically: 10 (83%)
├─ Manual Intervention: 2 (17%)
│
├─ Error Types:
│  ├─ context_length_exceeded: 5 (42%)
│  ├─ rate_limit_exceeded: 3 (25%)
│  ├─ network_error: 2 (17%)
│  └─ parse_error: 2 (17%)
│
└─ Recovery Success Rate: 83%
```

### **8. Active Retry Operations**
```
🔄 ACTIVE RETRIES
├─ Agent Delta
│  ├─ Retry: 2/3 attempts
│  ├─ Error: network_timeout
│  ├─ Last Attempt: 8s ago (failed)
│  ├─ Next Attempt: 12s (exponential backoff)
│  └─ Backoff: 1s → 2s → 4s → [current: 8s]
│
└─ Agent Echo
   ├─ Retry: 1/3 attempts
   ├─ Error: server_error_502
   ├─ Next Attempt: 2s
   └─ Auto-retry enabled
```

### **9. Thread Health Monitoring**
```
🧵 THREAD HEALTH
├─ Prime AI (wf_abc123_1732125847)
│  ├─ Age: 2h 15m
│  ├─ Message Count: 42
│  ├─ Token Count: ~22,250 (70% of limit)
│  ├─ Health: ⚠️ Warning (approaching token limit)
│  └─ Recommendation: Consider starting new thread
│
├─ Agent Alpha (wf_xyz789_1732125850)
│  ├─ Age: 45m
│  ├─ Message Count: 18
│  ├─ Token Count: ~8,450 (27% of limit)
│  └─ Health: ✅ Healthy
│
└─ Agent Bravo (wf_def456_1732125852)
   ├─ Age: 12m
   ├─ Message Count: 6
   ├─ Token Count: ~2,100 (7% of limit)
   └─ Health: ✅ Healthy
```

### **10. Quick Actions Panel**
```
⚡ QUICK ACTIONS
├─ [Stop All Streams] ← Emergency stop
├─ [Clear All Errors] ← Reset error states
├─ [Export Health Report] ← Download diagnostics
├─ [Test Backend] ← Check API connectivity
└─ [Reload All Panels] ← Force refresh
```

---

## 🎨 UI Layout Concept

```
┌─────────────────────────────────────┐
│  🤖 AI SYSTEM STATUS                │
│  [Collapse] [Export] [Settings]     │
├─────────────────────────────────────┤
│                                     │
│  🔵 ACTIVE STREAMS (3)              │
│  ├─ Prime AI (12.4s) ✅             │
│  ├─ Agent Alpha (8.2s) ⚠️           │
│  └─ Agent Bravo [Queued]            │
│                                     │
│  🔧 ERROR RECOVERY (2)              │
│  ├─ Prime AI: Reconstructing...     │
│  └─ Agent Charlie: Retry in 4s      │
│                                     │
│  🏥 SYSTEM HEALTH                   │
│  ├─ Backend: ✅ 45ms                │
│  ├─ Anthropic: ✅ 78% available     │
│  └─ Streams: 2/3 slots              │
│                                     │
│  📜 RECENT EVENTS                   │
│  ├─ 2:34:12 PM - Stream started     │
│  ├─ 2:34:08 PM - Completed (12.4s)  │
│  └─ 2:33:55 PM - Error recovered    │
│                                     │
│  ⚡ QUICK ACTIONS                   │
│  [Stop All] [Clear] [Export]        │
│                                     │
└─────────────────────────────────────┘
```

**Position:** Right sidebar (collapsible), similar to Synergy Dashboard

---

## 🔄 Anthropic Error → Auto Recovery Flow

### **Specific Errors Handled:**

#### **1. `context_length_exceeded` (Most Common)**
```javascript
{
  error: {
    type: "invalid_request_error",
    message: "prompt is too long: ... tokens > ... maximum"
  }
}

RECOVERY FLOW:
1. Detect error type → "context_length_exceeded"
2. Fetch full conversation history from backend
3. Calculate token counts for all messages
4. Remove oldest messages until under limit (target: 70% of max)
5. Rebuild conversation history array
6. Show user: "History trimmed (removed 8 oldest messages)"
7. Automatically resubmit request
8. Update sidebar: "Recovery successful in 3.2s"
```

#### **2. `rate_limit_exceeded`**
```javascript
{
  error: {
    type: "rate_limit_error",
    message: "Rate limit exceeded"
  }
}

RECOVERY FLOW:
1. Detect error type → "rate_limit_exceeded"
2. Apply exponential backoff: 1s → 2s → 4s → 8s → 16s
3. Show user: "Rate limit hit. Retrying in 8s... (2/5)"
4. Wait for backoff period
5. Automatically resubmit request
6. Update sidebar: "Retry 2/5 - waiting 8s"
```

#### **3. `overloaded_error` (Server busy)**
```javascript
{
  error: {
    type: "overloaded_error",
    message: "Overloaded"
  }
}

RECOVERY FLOW:
1. Detect error type → "overloaded_error"
2. Wait 30 seconds (server recovery time)
3. Show user: "API overloaded. Retrying in 30s..."
4. Automatically resubmit request
5. If fails again, increase backoff to 60s
6. Max retries: 3 attempts
```

#### **4. `authentication_error`**
```javascript
{
  error: {
    type: "authentication_error",
    message: "Invalid API key"
  }
}

RECOVERY FLOW:
1. Detect error type → "authentication_error"
2. Check if using API key rotation
3. Try next API key in rotation
4. Show user: "Switched to backup API key"
5. Automatically resubmit request
6. If all keys fail → notify user, manual intervention needed
```

#### **5. `network_error` (Connection lost)**
```javascript
{
  error: {
    type: "network_error",
    message: "Failed to fetch"
  }
}

RECOVERY FLOW:
1. Detect error type → "network_error"
2. Check if browser is online (navigator.onLine)
3. If offline → queue message, wait for reconnection
4. If online → retry with exponential backoff (1s, 2s, 4s)
5. Show user: "Connection lost. Retrying..."
6. Max retries: 5 attempts
```

---

## 🛠️ Technical Implementation

### **New Backend Route: `/api/agent/recover-history`**

```python
@agent_routes.route('/recover-history', methods=['POST'])
def recover_history():
    """
    Reconstruct conversation history for error recovery
    
    Request:
    {
        "thread_id": "wf_abc123_1732125847",
        "max_tokens": 20000,
        "preserve_recent": 10  # Keep last N messages
    }
    
    Response:
    {
        "original_count": 42,
        "original_tokens": 28450,
        "trimmed_count": 34,
        "trimmed_tokens": 19800,
        "removed_messages": 8,
        "history": [...]  # Rebuilt conversation array
    }
    """
    data = request.json
    thread_id = data.get('thread_id')
    max_tokens = data.get('max_tokens', 20000)
    preserve_recent = data.get('preserve_recent', 10)
    
    # Fetch full conversation from database
    messages = get_thread_messages(thread_id)
    
    # Calculate tokens (rough estimate: 4 chars = 1 token)
    def estimate_tokens(text):
        return len(text) / 4
    
    total_tokens = sum(estimate_tokens(m['content']) for m in messages)
    
    if total_tokens <= max_tokens:
        return jsonify({
            "original_count": len(messages),
            "original_tokens": int(total_tokens),
            "trimmed_count": len(messages),
            "trimmed_tokens": int(total_tokens),
            "removed_messages": 0,
            "history": messages
        })
    
    # Keep system message + recent messages
    system_msg = messages[0] if messages[0]['role'] == 'system' else None
    recent_messages = messages[-preserve_recent:]
    
    # Calculate tokens for recent messages
    recent_tokens = sum(estimate_tokens(m['content']) for m in recent_messages)
    remaining_budget = max_tokens - recent_tokens
    if system_msg:
        remaining_budget -= estimate_tokens(system_msg['content'])
    
    # Add older messages until budget exhausted
    trimmed_history = []
    if system_msg:
        trimmed_history.append(system_msg)
    
    for msg in messages[1:-preserve_recent]:
        msg_tokens = estimate_tokens(msg['content'])
        if remaining_budget - msg_tokens > 0:
            trimmed_history.append(msg)
            remaining_budget -= msg_tokens
        else:
            break
    
    trimmed_history.extend(recent_messages)
    
    trimmed_tokens = sum(estimate_tokens(m['content']) for m in trimmed_history)
    
    return jsonify({
        "original_count": len(messages),
        "original_tokens": int(total_tokens),
        "trimmed_count": len(trimmed_history),
        "trimmed_tokens": int(trimmed_tokens),
        "removed_messages": len(messages) - len(trimmed_history),
        "history": trimmed_history
    })
```

### **Frontend: Auto-Recovery Manager**

```javascript
class AnthropicErrorRecoveryManager {
    constructor(panelId, threadId) {
        this.panelId = panelId;
        this.threadId = threadId;
        this.maxRetries = 3;
        this.retryCount = 0;
    }
    
    async handleError(error, originalPayload) {
        const errorType = this.detectErrorType(error);
        
        console.log(`[RECOVERY] Detected error type: ${errorType}`);
        
        // Update AI Status Sidebar
        window.aiStatusSidebar?.addRecoveryOperation(this.panelId, errorType);
        
        switch (errorType) {
            case 'context_length_exceeded':
                return await this.recoverFromContextLength(originalPayload);
            
            case 'rate_limit_exceeded':
                return await this.recoverFromRateLimit(originalPayload);
            
            case 'overloaded_error':
                return await this.recoverFromOverload(originalPayload);
            
            case 'authentication_error':
                return await this.recoverFromAuth(originalPayload);
            
            case 'network_error':
                return await this.recoverFromNetwork(originalPayload);
            
            default:
                console.error('[RECOVERY] Unknown error type, cannot auto-recover');
                return null;
        }
    }
    
    async recoverFromContextLength(originalPayload) {
        console.log('[RECOVERY] Starting history reconstruction...');
        
        // Update sidebar: Step 1
        window.aiStatusSidebar?.updateRecoveryStep(
            this.panelId, 
            1, 
            'Fetching conversation history'
        );
        
        try {
            // Fetch and rebuild history from backend
            const response = await fetch(`${API_BASE_URL}/api/agent/recover-history`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    thread_id: this.threadId,
                    max_tokens: 20000,
                    preserve_recent: 10
                })
            });
            
            const recoveryData = await response.json();
            
            // Update sidebar: Step 2
            window.aiStatusSidebar?.updateRecoveryStep(
                this.panelId,
                2,
                `Removed ${recoveryData.removed_messages} messages (saved ${recoveryData.original_tokens - recoveryData.trimmed_tokens} tokens)`
            );
            
            // Show user notification
            this.showRecoveryMessage(
                `History trimmed: Removed ${recoveryData.removed_messages} oldest messages to fit token limit. Retrying...`
            );
            
            // Rebuild payload with trimmed history
            const newPayload = {
                ...originalPayload,
                conversation_history: recoveryData.history
            };
            
            // Update sidebar: Step 3
            window.aiStatusSidebar?.updateRecoveryStep(
                this.panelId,
                3,
                'Resubmitting request'
            );
            
            // Resubmit request
            const retryResponse = await this.resubmitRequest(newPayload);
            
            // Success!
            window.aiStatusSidebar?.completeRecovery(this.panelId, 'success');
            
            return retryResponse;
            
        } catch (error) {
            console.error('[RECOVERY] Failed:', error);
            window.aiStatusSidebar?.completeRecovery(this.panelId, 'failed');
            throw error;
        }
    }
    
    async recoverFromRateLimit(originalPayload) {
        this.retryCount++;
        
        if (this.retryCount > this.maxRetries) {
            throw new Error('Max retries exceeded for rate limit');
        }
        
        // Exponential backoff: 1s, 2s, 4s
        const backoffMs = 1000 * Math.pow(2, this.retryCount - 1);
        
        console.log(`[RECOVERY] Rate limit hit. Retry ${this.retryCount}/${this.maxRetries} in ${backoffMs}ms`);
        
        this.showRecoveryMessage(
            `Rate limit exceeded. Retrying in ${backoffMs / 1000}s... (${this.retryCount}/${this.maxRetries})`
        );
        
        // Update sidebar
        window.aiStatusSidebar?.updateRetryCountdown(this.panelId, backoffMs);
        
        // Wait
        await new Promise(resolve => setTimeout(resolve, backoffMs));
        
        // Retry
        return await this.resubmitRequest(originalPayload);
    }
    
    detectErrorType(error) {
        const message = error.message?.toLowerCase() || '';
        
        if (message.includes('prompt is too long') || message.includes('context_length')) {
            return 'context_length_exceeded';
        }
        if (message.includes('rate limit') || error.type === 'rate_limit_error') {
            return 'rate_limit_exceeded';
        }
        if (message.includes('overloaded') || error.type === 'overloaded_error') {
            return 'overloaded_error';
        }
        if (message.includes('authentication') || error.type === 'authentication_error') {
            return 'authentication_error';
        }
        if (message.includes('network') || message.includes('fetch')) {
            return 'network_error';
        }
        
        return 'unknown';
    }
    
    async resubmitRequest(payload) {
        // Make request to backend (same as original send logic)
        const response = await fetch(`${API_BASE_URL}/api/agent/chat-stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        return response;
    }
    
    showRecoveryMessage(message) {
        const bubble = document.createElement('div');
        bubble.className = 'ai-message system recovery';
        bubble.innerHTML = `
            <i class="fas fa-sync fa-spin"></i>
            ${message}
        `;
        
        const container = this.panelId === 'prime'
            ? document.getElementById('ai-chat-messages')
            : document.getElementById(`agent-messages-${this.panelId}`);
        
        container?.appendChild(bubble);
    }
}
```

---

## 📝 Summary: What Gets Tracked in Chat

### **Visible in AI Status Sidebar:**
1. ✅ Active streams (Prime + all agents) with duration/tokens
2. ✅ Stream health (last event time, warnings for stalls)
3. ✅ Error recovery operations (live progress)
4. ✅ History reconstruction steps (what's being removed/kept)
5. ✅ Retry countdowns (exponential backoff timers)
6. ✅ System health (backend/Anthropic API status)
7. ✅ Token usage per panel + session total
8. ✅ Recent events timeline (last 5-10 events)
9. ✅ Error statistics (types, recovery rate)
10. ✅ Thread health (age, message count, token usage)
11. ✅ Quick actions (stop all, clear errors, export diagnostics)

### **NOT Using LocalStorage:**
- All state managed in-memory or via backend database
- History reconstruction fetched from backend (`/api/agent/recover-history`)
- Error logs stored in backend database for persistence
- Sidebar state can collapse/expand but doesn't persist across refresh

---

## 🚀 Next Steps

1. **Implement AI Status Sidebar UI** (clone Thread History sidebar structure)
2. **Create backend `/api/agent/recover-history` endpoint**
3. **Build AnthropicErrorRecoveryManager class**
4. **Integrate with existing streaming logic**
5. **Add error type detection and routing**
6. **Test with deliberate context_length errors**

---

**Last Updated**: November 22, 2025  
**Status**: 📋 SPECIFICATION - Ready for Implementation  
**Estimated Work**: 2-3 days for full AI Status Sidebar + Auto-Recovery
