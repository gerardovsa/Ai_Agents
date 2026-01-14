# Advanced Multi-Agent Coordination Tools - Enhanced Specification

## Overview

Enhanced system with:
1. **Combo slug assignment** - Assign multiple slugs + instructions + auto-open agent column + auto-trigger
2. **Cross-thread communication** - AI requests updates from other threads and receives responses
3. **Real-time UI updates** - Agent cards and synergy cards automatically update

## Tool 1: `assign_and_activate_agent_with_slugs`

**Purpose**: All-in-one tool to assign resources to an agent, open the column, and optionally trigger a request

### Schema
```json
{
  "name": "assign_and_activate_agent_with_slugs",
  "description": "Complete agent activation: assign workflow/doc/synergy slugs to an agent thread, send instructions, open the agent column in UI, and optionally trigger the agent to start working immediately. This is the primary coordination tool for distributing work.",
  "parameters": {
    "type": "object",
    "properties": {
      "target_agent": {
        "type": "string",
        "description": "Agent to activate: 'agent-1' through 'agent-26', or agent name like 'Alpha', 'Bravo', etc.",
        "examples": ["agent-5", "Alpha", "Bravo", "Charlie"]
      },
      "thread_title": {
        "type": "string",
        "description": "Title for the thread (creates new if agent is empty, or updates existing)"
      },
      "instructions": {
        "type": "string",
        "description": "Initial instructions for the agent - what you want them to do. This becomes the first message in their thread."
      },
      "slugs": {
        "type": "object",
        "description": "Resources to assign to the agent",
        "properties": {
          "workflow_slug": {
            "type": "string",
            "description": "Workflow slug to link (e.g., 'email-automation-v2')"
          },
          "workflow_title": {
            "type": "string",
            "description": "Workflow display title"
          },
          "internal_doc_slug": {
            "type": "string",
            "description": "Internal document slug to link (e.g., 'api-documentation')"
          },
          "internal_doc_title": {
            "type": "string",
            "description": "Internal doc display title"
          },
          "synergy_session_id": {
            "type": "string",
            "description": "Synergy session card ID to link"
          }
        }
      },
      "auto_trigger": {
        "type": "boolean",
        "description": "If true, automatically send the instructions message to trigger agent processing. If false, just setup and wait for user.",
        "default": false
      },
      "open_ui": {
        "type": "boolean",
        "description": "If true, automatically switch to Multi-Agent tab and open this agent's column",
        "default": true
      }
    },
    "required": ["target_agent", "instructions"]
  }
}
```

### Implementation Flow

```python
# tools/implementations/advanced_agent_coordination.py

def assign_and_activate_agent_with_slugs(
    target_agent,
    instructions,
    thread_title=None,
    slugs=None,
    auto_trigger=False,
    open_ui=True,
    **kwargs
):
    """
    All-in-one agent activation with slug assignment
    
    Flow:
    1. Parse agent identifier (convert 'Alpha' -> 'agent-1')
    2. Check if agent has existing thread
    3. Create thread if needed, or get existing
    4. Assign all slugs to thread
    5. Add instruction message to thread
    6. Return UI command to open agent column
    7. Optionally trigger agent to process instructions
    
    Returns:
        {
            "success": true,
            "action": "assigned_and_activated",
            "agent_id": 1,
            "agent_name": "Alpha",
            "agent_location": "agent-1",
            "thread_id": "1763287561207",
            "thread_title": "Email Campaign Setup",
            "slugs_assigned": {
                "workflow_slug": "email-automation-v2",
                "internal_doc_slug": "email-templates"
            },
            "instruction_message_id": "msg_12345",
            "triggered": true,
            "ui_commands": [
                {
                    "type": "switch_tab",
                    "tab": "multi-agent"
                },
                {
                    "type": "open_agent_column",
                    "agent_id": 1
                },
                {
                    "type": "show_thread_info",
                    "thread_id": "1763287561207",
                    "location": "agent-1"
                }
            ]
        }
    """
    import sqlite3
    from pathlib import Path
    from datetime import datetime
    
    # 1. Parse agent identifier
    agent_id, agent_name, location = parse_agent_identifier(target_agent)
    
    # 2. Get database connection
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'sessions.db'
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    user_id = kwargs.get('_user_id', 1)
    
    # 3. Check for existing thread at this location
    cursor.execute("""
        SELECT thread_slug, name, id
        FROM threads
        WHERE user_id = ? AND location = ?
        ORDER BY updated_at DESC
        LIMIT 1
    """, (user_id, location))
    
    existing_thread = cursor.fetchone()
    
    if existing_thread:
        # Use existing thread
        thread_id = existing_thread['thread_slug']
        thread_db_id = existing_thread['id']
        thread_title = thread_title or existing_thread['name']
        
        # Update title if provided
        if thread_title and thread_title != existing_thread['name']:
            cursor.execute("""
                UPDATE threads SET name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE thread_slug = ?
            """, (thread_title, thread_id))
    else:
        # Create new thread
        thread_id = str(int(datetime.now().timestamp() * 1000))
        thread_title = thread_title or f"{agent_name} Task"
        
        cursor.execute("""
            INSERT INTO threads (
                thread_slug, workspace_id, name, user_id, 
                created_at, updated_at, metadata, location
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            thread_id,
            1,  # default workspace
            thread_title,
            user_id,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            '{}',
            location
        ))
        
        # Get the database ID
        thread_db_id = cursor.lastrowid
    
    # 4. Assign slugs if provided
    slugs_assigned = {}
    
    if slugs:
        update_fields = []
        update_values = []
        
        if slugs.get('workflow_slug'):
            update_fields.extend(['workflow_slug = ?', 'workflow_title = ?'])
            update_values.extend([slugs['workflow_slug'], slugs.get('workflow_title', '')])
            slugs_assigned['workflow_slug'] = slugs['workflow_slug']
            slugs_assigned['workflow_title'] = slugs.get('workflow_title')
        
        if slugs.get('internal_doc_slug'):
            update_fields.extend(['internal_doc_slug = ?', 'internal_doc_title = ?'])
            update_values.extend([slugs['internal_doc_slug'], slugs.get('internal_doc_title', '')])
            slugs_assigned['internal_doc_slug'] = slugs['internal_doc_slug']
            slugs_assigned['internal_doc_title'] = slugs.get('internal_doc_title')
        
        if slugs.get('synergy_session_id'):
            update_fields.append('synergy_card_id = ?')
            update_values.append(slugs['synergy_session_id'])
            slugs_assigned['synergy_session_id'] = slugs['synergy_session_id']
        
        if update_fields:
            update_values.append(thread_id)
            cursor.execute(f"""
                UPDATE threads SET 
                    {', '.join(update_fields)},
                    updated_at = CURRENT_TIMESTAMP
                WHERE thread_slug = ?
            """, update_values)
    
    # 5. Add instruction message to thread
    message_id = f"msg_{int(datetime.now().timestamp() * 1000)}"
    
    cursor.execute("""
        INSERT INTO messages (
            thread_id, role, content, timestamp, message_type
        ) VALUES (?, ?, ?, ?, ?)
    """, (
        thread_db_id,
        'system',
        f"📋 **Coordination Instructions from {kwargs.get('_source_agent', 'Prime')}:**\n\n{instructions}",
        datetime.now().isoformat(),
        'instruction'
    ))
    
    conn.commit()
    conn.close()
    
    # 6. Build UI commands
    ui_commands = []
    
    if open_ui:
        ui_commands.append({
            "type": "switch_tab",
            "tab": "multi-agent"
        })
        ui_commands.append({
            "type": "open_agent_column",
            "agent_id": agent_id,
            "agent_name": agent_name
        })
        ui_commands.append({
            "type": "show_thread_info",
            "thread_id": thread_id,
            "location": location,
            "highlight": True
        })
    
    # 7. Optionally trigger agent processing
    triggered = False
    if auto_trigger:
        ui_commands.append({
            "type": "trigger_agent_request",
            "agent_id": agent_id,
            "thread_id": thread_id,
            "message": instructions
        })
        triggered = True
    
    return {
        "success": True,
        "action": "assigned_and_activated",
        "agent_id": agent_id,
        "agent_name": agent_name,
        "agent_location": location,
        "thread_id": thread_id,
        "thread_title": thread_title,
        "slugs_assigned": slugs_assigned,
        "instruction_message_id": message_id,
        "triggered": triggered,
        "ui_commands": ui_commands,
        "message": f"✅ {agent_name} activated with task: '{thread_title}'. " + 
                   (f"Assigned {len(slugs_assigned)} resource(s). " if slugs_assigned else "") +
                   ("Agent triggered and processing." if triggered else "Ready for user to start.")
    }


def parse_agent_identifier(target_agent):
    """
    Convert agent identifier to (agent_id, agent_name, location)
    
    Handles:
    - 'agent-5' -> (5, 'Echo', 'agent-5')
    - 'Alpha' -> (1, 'Alpha', 'agent-1')
    - '5' -> (5, 'Echo', 'agent-5')
    """
    nato_alphabet = [
        'Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot',
        'Golf', 'Hotel', 'India', 'Juliet', 'Kilo', 'Lima',
        'Mike', 'November', 'Oscar', 'Papa', 'Quebec', 'Romeo',
        'Sierra', 'Tango', 'Uniform', 'Victor', 'Whiskey',
        'X-ray', 'Yankee', 'Zulu'
    ]
    
    # Handle 'agent-N' format
    if target_agent.startswith('agent-'):
        agent_id = int(target_agent.split('-')[1])
        agent_name = nato_alphabet[agent_id - 1]
        return agent_id, agent_name, target_agent
    
    # Handle NATO name
    if target_agent in nato_alphabet:
        agent_id = nato_alphabet.index(target_agent) + 1
        return agent_id, target_agent, f"agent-{agent_id}"
    
    # Handle numeric ID
    try:
        agent_id = int(target_agent)
        if 1 <= agent_id <= 26:
            agent_name = nato_alphabet[agent_id - 1]
            return agent_id, agent_name, f"agent-{agent_id}"
    except ValueError:
        pass
    
    raise ValueError(f"Invalid agent identifier: {target_agent}. Use 'agent-1' through 'agent-26', NATO names, or numeric IDs 1-26")
```

## Tool 2: `request_update_from_thread`

**Purpose**: AI in one thread requests information/update from another thread and receives response

### Schema
```json
{
  "name": "request_update_from_thread",
  "description": "Request an update or information from another agent's thread. The target thread will receive your request, process it, and return a response. Useful for coordination, getting status updates, or requesting deliverables from other agents.",
  "parameters": {
    "type": "object",
    "properties": {
      "target_thread_id": {
        "type": "string",
        "description": "Thread ID to request update from (e.g., '1763287561207'). Can also use 'agent-5' to target agent's current thread."
      },
      "request_message": {
        "type": "string",
        "description": "What you're requesting from the other thread. Be specific about what information or deliverable you need."
      },
      "request_type": {
        "type": "string",
        "description": "Type of request",
        "enum": ["status_update", "deliverable", "question", "coordination", "resource_request"],
        "default": "question"
      },
      "priority": {
        "type": "string",
        "description": "Request priority",
        "enum": ["low", "normal", "high", "urgent"],
        "default": "normal"
      },
      "wait_for_response": {
        "type": "boolean",
        "description": "If true, wait for target thread to respond before returning. If false, send request and return immediately.",
        "default": false
      },
      "timeout_seconds": {
        "type": "integer",
        "description": "If wait_for_response is true, max time to wait (default 30 seconds)",
        "default": 30
      }
    },
    "required": ["target_thread_id", "request_message"]
  }
}
```

### Implementation with WebSocket/SSE

```python
# tools/implementations/advanced_agent_coordination.py

def request_update_from_thread(
    target_thread_id,
    request_message,
    request_type="question",
    priority="normal",
    wait_for_response=False,
    timeout_seconds=30,
    **kwargs
):
    """
    Request update from another thread with optional wait for response
    
    Flow:
    1. Validate target thread exists and get its location
    2. Create cross-thread request record in database
    3. Insert request message into target thread
    4. Trigger target agent if requested
    5. Optionally wait for response
    6. Return request ID and response (if waited)
    
    Returns:
        {
            "success": true,
            "request_id": "req_1763288123456",
            "target_thread_id": "1763287561207",
            "target_agent": "Agent Echo (agent-5)",
            "request_sent": true,
            "response_received": true,  # if wait_for_response=true
            "response": {
                "message": "Response from Agent Echo...",
                "timestamp": "2025-11-16T21:45:00",
                "attachments": []
            },
            "ui_commands": [
                {
                    "type": "show_cross_thread_request",
                    "request_id": "req_1763288123456",
                    "source_thread": "1763287802456",
                    "target_thread": "1763287561207"
                }
            ]
        }
    """
    import sqlite3
    from pathlib import Path
    from datetime import datetime
    import time
    
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'sessions.db'
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get source thread info
    source_thread_id = kwargs.get('thread_id')
    source_location = kwargs.get('location', 'prime')
    user_id = kwargs.get('_user_id', 1)
    
    # 1. Validate and get target thread
    # Handle 'agent-N' shorthand
    if target_thread_id.startswith('agent-'):
        cursor.execute("""
            SELECT thread_slug, name, location
            FROM threads
            WHERE user_id = ? AND location = ?
            ORDER BY updated_at DESC
            LIMIT 1
        """, (user_id, target_thread_id))
    else:
        cursor.execute("""
            SELECT thread_slug, name, location, id
            FROM threads
            WHERE thread_slug = ? AND user_id = ?
        """, (target_thread_id, user_id))
    
    target_thread = cursor.fetchone()
    
    if not target_thread:
        conn.close()
        return {
            "success": False,
            "error": f"Target thread {target_thread_id} not found or not accessible"
        }
    
    target_thread_id = target_thread['thread_slug']
    target_thread_db_id = target_thread['id']
    target_location = target_thread['location']
    target_thread_title = target_thread['name']
    
    # 2. Create cross-thread request record
    request_id = f"req_{int(datetime.now().timestamp() * 1000)}"
    
    # Create requests table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cross_thread_requests (
            request_id TEXT PRIMARY KEY,
            source_thread_id INTEGER,
            target_thread_id INTEGER,
            request_message TEXT,
            request_type TEXT,
            priority TEXT,
            status TEXT,
            response_message TEXT,
            created_at TIMESTAMP,
            responded_at TIMESTAMP,
            user_id INTEGER
        )
    """)
    
    cursor.execute("""
        INSERT INTO cross_thread_requests (
            request_id, source_thread_id, target_thread_id,
            request_message, request_type, priority, status,
            created_at, user_id
        ) VALUES (?, 
            (SELECT id FROM threads WHERE thread_slug = ?),
            ?,
            ?, ?, ?, 'pending', ?, ?
        )
    """, (
        request_id,
        source_thread_id,
        target_thread_db_id,
        request_message,
        request_type,
        priority,
        datetime.now().isoformat(),
        user_id
    ))
    
    # 3. Insert request message into target thread
    priority_icon = {"low": "ℹ️", "normal": "📬", "high": "⚠️", "urgent": "🚨"}[priority]
    
    cursor.execute("""
        INSERT INTO messages (
            thread_id, role, content, timestamp, message_type, metadata
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        target_thread_db_id,
        'system',
        f"{priority_icon} **Cross-Thread Request** from {source_location}:\n\n{request_message}\n\n*Request ID: {request_id}*",
        datetime.now().isoformat(),
        'cross_thread_request',
        f'{{"request_id": "{request_id}", "source_thread": "{source_thread_id}", "request_type": "{request_type}"}}'
    ))
    
    conn.commit()
    
    # 4. Build UI commands
    ui_commands = [
        {
            "type": "show_cross_thread_request",
            "request_id": request_id,
            "source_thread": source_thread_id,
            "target_thread": target_thread_id,
            "target_location": target_location
        },
        {
            "type": "trigger_agent_notification",
            "agent_location": target_location,
            "message": f"New request from {source_location}"
        }
    ]
    
    # 5. Wait for response if requested
    response_data = None
    response_received = False
    
    if wait_for_response:
        start_time = time.time()
        
        while (time.time() - start_time) < timeout_seconds:
            cursor.execute("""
                SELECT status, response_message, responded_at
                FROM cross_thread_requests
                WHERE request_id = ?
            """, (request_id,))
            
            request_status = cursor.fetchone()
            
            if request_status and request_status['status'] == 'completed':
                response_received = True
                response_data = {
                    "message": request_status['response_message'],
                    "timestamp": request_status['responded_at']
                }
                break
            
            time.sleep(1)  # Poll every second
    
    conn.close()
    
    return {
        "success": True,
        "request_id": request_id,
        "target_thread_id": target_thread_id,
        "target_thread_title": target_thread_title,
        "target_agent": f"{target_location}",
        "request_sent": True,
        "response_received": response_received,
        "response": response_data,
        "waited": wait_for_response,
        "ui_commands": ui_commands,
        "message": f"✅ Request sent to {target_location} (Thread: {target_thread_title}). " + 
                   (f"Response received: {response_data['message'][:100]}..." if response_received else
                    "Waiting for response..." if wait_for_response else
                    "Request delivered, not waiting for response.")
    }
```

## Tool 3: `respond_to_cross_thread_request`

**Purpose**: AI in target thread responds to incoming request

### Schema
```json
{
  "name": "respond_to_cross_thread_request",
  "description": "Respond to a cross-thread request that was sent to your thread. Use this when you see a cross-thread request message in your conversation.",
  "parameters": {
    "type": "object",
    "properties": {
      "request_id": {
        "type": "string",
        "description": "Request ID from the cross-thread request message (e.g., 'req_1763288123456')"
      },
      "response_message": {
        "type": "string",
        "description": "Your response to the request. Include the information, status update, or deliverable that was requested."
      },
      "attachments": {
        "type": "array",
        "description": "Optional: File paths, URLs, or resource slugs to attach to response",
        "items": {"type": "string"}
      }
    },
    "required": ["request_id", "response_message"]
  }
}
```

### Implementation

```python
def respond_to_cross_thread_request(
    request_id,
    response_message,
    attachments=None,
    **kwargs
):
    """
    Respond to cross-thread request
    
    Returns:
        {
            "success": true,
            "request_id": "req_1763288123456",
            "response_sent": true,
            "source_thread_notified": true,
            "message": "Response sent to requesting thread"
        }
    """
    import sqlite3
    from pathlib import Path
    from datetime import datetime
    
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'sessions.db'
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get request details
    cursor.execute("""
        SELECT 
            ctr.*,
            source.thread_slug as source_thread_slug,
            source.name as source_thread_name,
            source.location as source_location
        FROM cross_thread_requests ctr
        JOIN threads source ON ctr.source_thread_id = source.id
        WHERE ctr.request_id = ?
    """, (request_id,))
    
    request = cursor.fetchone()
    
    if not request:
        conn.close()
        return {
            "success": False,
            "error": f"Request {request_id} not found"
        }
    
    # Update request status
    cursor.execute("""
        UPDATE cross_thread_requests
        SET status = 'completed',
            response_message = ?,
            responded_at = ?
        WHERE request_id = ?
    """, (response_message, datetime.now().isoformat(), request_id))
    
    # Add response message to source thread
    cursor.execute("""
        INSERT INTO messages (
            thread_id, role, content, timestamp, message_type, metadata
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        request['source_thread_id'],
        'system',
        f"✅ **Response to Request {request_id}**\n\nFrom: {kwargs.get('location', 'unknown')}\n\n{response_message}",
        datetime.now().isoformat(),
        'cross_thread_response',
        f'{{"request_id": "{request_id}", "has_attachments": {bool(attachments)}}}'
    ))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "request_id": request_id,
        "response_sent": True,
        "source_thread_id": request['source_thread_slug'],
        "source_thread_notified": True,
        "ui_commands": [
            {
                "type": "notify_thread_response",
                "thread_id": request['source_thread_slug'],
                "location": request['source_location']
            }
        ],
        "message": f"✅ Response sent to {request['source_location']} successfully"
    }
```

## Frontend Integration - UI Command Handler

### New JavaScript Module: `ui-command-processor.js`

```javascript
/**
 * UI Command Processor
 * Handles UI commands returned from backend tools
 */

window.UICommandProcessor = {
    
    /**
     * Process array of UI commands from tool responses
     */
    processCommands(commands) {
        if (!Array.isArray(commands)) return;
        
        commands.forEach(cmd => {
            switch(cmd.type) {
                case 'switch_tab':
                    this.switchTab(cmd.tab);
                    break;
                case 'open_agent_column':
                    this.openAgentColumn(cmd.agent_id, cmd.agent_name);
                    break;
                case 'show_thread_info':
                    this.showThreadInfo(cmd.thread_id, cmd.location, cmd.highlight);
                    break;
                case 'trigger_agent_request':
                    this.triggerAgentRequest(cmd.agent_id, cmd.thread_id, cmd.message);
                    break;
                case 'show_cross_thread_request':
                    this.showCrossThreadRequest(cmd.request_id, cmd.source_thread, cmd.target_thread);
                    break;
                case 'trigger_agent_notification':
                    this.triggerAgentNotification(cmd.agent_location, cmd.message);
                    break;
                case 'notify_thread_response':
                    this.notifyThreadResponse(cmd.thread_id, cmd.location);
                    break;
            }
        });
    },
    
    /**
     * Switch to specified tab
     */
    switchTab(tabName) {
        const tabMap = {
            'multi-agent': 'tab-multi-agent',
            'synergy': 'tab-synergy',
            'automation': 'tab-automation'
        };
        
        const tabId = tabMap[tabName];
        if (tabId) {
            document.getElementById(tabId)?.click();
            console.log(`[UI Command] Switched to ${tabName} tab`);
        }
    },
    
    /**
     * Open agent column in Multi-Agent tab
     */
    openAgentColumn(agentId, agentName) {
        // Expand agent column if collapsed
        const agentColumn = document.querySelector(`#agent-${agentId}.agent-column`);
        if (agentColumn) {
            agentColumn.classList.remove('collapsed');
            
            // Scroll into view
            agentColumn.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            
            // Flash highlight
            agentColumn.style.boxShadow = '0 0 20px rgba(0, 150, 255, 0.6)';
            setTimeout(() => {
                agentColumn.style.boxShadow = '';
            }, 2000);
            
            console.log(`[UI Command] Opened ${agentName || `Agent-${agentId}`} column`);
        }
    },
    
    /**
     * Show thread info card in specified location
     */
    showThreadInfo(threadId, location, highlight = false) {
        // Update thread info container
        const threadInfoContainer = document.getElementById(`thread-info-${location.replace('agent-', '')}`);
        
        if (threadInfoContainer && typeof ThreadManager !== 'undefined') {
            threadInfoContainer.innerHTML = ThreadManager.renderThreadInfoContainer(
                location,
                threadId,
                true  // compact mode
            );
            
            if (highlight) {
                threadInfoContainer.style.border = '2px solid #0096ff';
                setTimeout(() => {
                    threadInfoContainer.style.border = '';
                }, 3000);
            }
            
            console.log(`[UI Command] Updated thread info for ${threadId} in ${location}`);
        }
        
        // Update synergy card if synergy session is linked
        this.updateSynergyCardThreads(threadId);
    },
    
    /**
     * Trigger agent to process request
     */
    async triggerAgentRequest(agentId, threadId, message) {
        console.log(`[UI Command] Triggering agent-${agentId} with request...`);
        
        // Load thread into agent if not already loaded
        if (typeof MultiAgent !== 'undefined') {
            const thread = ThreadManager.threads.find(t => t.id === threadId);
            if (thread) {
                await MultiAgent.loadThreadIntoAgent(agentId, thread);
            }
        }
        
        // Send message to agent
        // This would trigger the agent's AI to process the instruction
        // Implementation depends on your sendToAgent() function
        if (typeof sendToAgent === 'function') {
            setTimeout(() => {
                sendToAgent(agentId, message);
            }, 500);
        }
    },
    
    /**
     * Show cross-thread request indicator
     */
    showCrossThreadRequest(requestId, sourceThread, targetThread) {
        console.log(`[UI Command] Cross-thread request ${requestId}: ${sourceThread} → ${targetThread}`);
        
        // Add visual indicator to target thread
        const targetThreadCard = document.querySelector(`[data-thread-id="${targetThread}"]`);
        if (targetThreadCard) {
            const requestBadge = document.createElement('span');
            requestBadge.className = 'cross-thread-request-badge';
            requestBadge.textContent = '📬';
            requestBadge.title = `Request from ${sourceThread}`;
            targetThreadCard.appendChild(requestBadge);
        }
        
        // Show notification
        if (typeof showNotification === 'function') {
            showNotification(`Cross-thread request sent to ${targetThread}`, 'info');
        }
    },
    
    /**
     * Trigger notification for agent
     */
    triggerAgentNotification(agentLocation, message) {
        const agentId = parseInt(agentLocation.replace('agent-', ''));
        const agentColumn = document.querySelector(`#agent-${agentId}.agent-column`);
        
        if (agentColumn) {
            // Add notification badge
            const header = agentColumn.querySelector('.agent-header');
            if (header) {
                let badge = header.querySelector('.notification-badge');
                if (!badge) {
                    badge = document.createElement('span');
                    badge.className = 'notification-badge';
                    header.appendChild(badge);
                }
                badge.textContent = '🔔';
                badge.title = message;
                
                // Remove after 5 seconds
                setTimeout(() => badge.remove(), 5000);
            }
        }
        
        console.log(`[UI Command] Notified ${agentLocation}: ${message}`);
    },
    
    /**
     * Notify thread of response received
     */
    notifyThreadResponse(threadId, location) {
        console.log(`[UI Command] Thread ${threadId} received response`);
        
        // Refresh thread messages if it's the active thread
        if (typeof ThreadManager !== 'undefined' && ThreadManager.currentThreadId === threadId) {
            ThreadManager.loadMessagesForThread(threadId);
        }
        
        // Show notification
        if (typeof showNotification === 'function') {
            showNotification(`Response received in ${location}`, 'success');
        }
    },
    
    /**
     * Update synergy card linked threads section
     */
    updateSynergyCardThreads(threadId) {
        // Get thread's synergy session
        const thread = ThreadManager.threads.find(t => t.id === threadId);
        if (!thread || !thread.synergy_card_id) return;
        
        // Update synergy card
        const synergyCard = document.querySelector(`[data-synergy-id="${thread.synergy_card_id}"]`);
        if (synergyCard && typeof synergyBoard !== 'undefined') {
            const linkedThreadsContainer = synergyCard.querySelector('.synergy-linked-threads');
            if (linkedThreadsContainer) {
                // Re-render linked threads section
                synergyBoard.renderLinkedThreads(thread.synergy_card_id);
            }
        }
    }
};

// Hook into tool response processing
window.addEventListener('tool-response-received', (event) => {
    const response = event.detail;
    
    if (response.ui_commands) {
        UICommandProcessor.processCommands(response.ui_commands);
    }
});
```

## Usage Examples

### Example 1: Distribute E-Commerce Project with Full Activation

```
User (in Prime): "Build an e-commerce platform. Set up 3 agents to work on different parts."

AI calls:
assign_and_activate_agent_with_slugs(
    target_agent="Alpha",
    thread_title="E-Commerce Frontend",
    instructions="Build React frontend: product catalog, shopping cart, checkout flow. Use modern hooks, TypeScript, and responsive design.",
    slugs={
        "workflow_slug": "react-frontend-workflow",
        "workflow_title": "React Frontend Development Workflow",
        "internal_doc_slug": "react-architecture-guide",
        "internal_doc_title": "React Architecture Best Practices"
    },
    auto_trigger=True,
    open_ui=True
)

Result:
✅ Alpha column opens automatically
✅ Thread "E-Commerce Frontend" created
✅ Workflow and doc badges appear in thread info card
✅ Agent Alpha starts processing immediately
```

### Example 2: Cross-Thread Status Request

```
User (in Prime): "Check on Agent Bravo's progress with the API"

AI in Prime calls:
request_update_from_thread(
    target_thread_id="agent-2",
    request_message="Please provide status update on the API development. What's completed? Any blockers?",
    request_type="status_update",
    priority="normal",
    wait_for_response=False
)

Result in Agent Bravo's thread:
📬 Cross-Thread Request from prime:
Please provide status update on the API development. What's completed? Any blockers?
Request ID: req_1763288123456

Agent Bravo's AI sees this and calls:
respond_to_cross_thread_request(
    request_id="req_1763288123456",
    response_message="API development is 75% complete. Completed: User auth, product endpoints, order processing. Still working on: Payment integration (blocked on Stripe API keys), inventory sync. ETA: 2 days."
)

Result in Prime thread:
✅ Response to Request req_1763288123456
From: agent-2
API development is 75% complete...
```

### Example 3: Synergy Session Distribution

```
User creates synergy session "Mobile App Redesign"

AI in Prime calls:
assign_and_activate_agent_with_slugs(
    target_agent="Charlie",
    thread_title="Mobile App - Database Migration",
    instructions="Handle database migration for mobile app redesign. Update schema for new features, migrate existing data, test thoroughly.",
    slugs={
        "synergy_session_id": "mobile-redesign-001"
    },
    auto_trigger=False,
    open_ui=True
)

Result:
✅ Charlie column opens
✅ Thread created with synergy link
✅ Thread info card appears in Charlie's column
✅ Thread info card ALSO appears in "mobile-redesign-001" synergy card's linked threads section
```

## Database Schema Updates

```sql
-- Cross-thread requests table
CREATE TABLE IF NOT EXISTS cross_thread_requests (
    request_id TEXT PRIMARY KEY,
    source_thread_id INTEGER,
    target_thread_id INTEGER,
    request_message TEXT,
    request_type TEXT,
    priority TEXT,
    status TEXT,  -- 'pending', 'completed', 'cancelled'
    response_message TEXT,
    created_at TIMESTAMP,
    responded_at TIMESTAMP,
    user_id INTEGER,
    FOREIGN KEY (source_thread_id) REFERENCES threads(id),
    FOREIGN KEY (target_thread_id) REFERENCES threads(id)
);

CREATE INDEX idx_cross_thread_requests_target ON cross_thread_requests(target_thread_id, status);
CREATE INDEX idx_cross_thread_requests_source ON cross_thread_requests(source_thread_id);

-- New message types
-- Add to messages.message_type enum:
-- 'instruction', 'cross_thread_request', 'cross_thread_response'
```

## Implementation Checklist

- [ ] Create `tools/schemas/advanced_agent_coordination_tools.json`
- [ ] Create `tools/implementations/advanced_agent_coordination.py`
- [ ] Create `UI/external/modules/ui-command-processor.js`
- [ ] Add cross_thread_requests table migration
- [ ] Update message types to include new types
- [ ] Hook UI command processor into tool response handler
- [ ] Update ThreadManager to handle synergy card thread updates
- [ ] Add notification badges to agent columns
- [ ] Test full flow: assign → open → trigger → request → respond

## Benefits

1. **One-Step Agent Activation** - No manual UI interaction needed
2. **Real-Time UI Updates** - Cards, badges, and notifications appear automatically
3. **Cross-Thread Communication** - Agents can coordinate without user intervention
4. **Synergy Integration** - Threads automatically appear in synergy cards
5. **Auto-Triggering** - Optional immediate agent processing
6. **Visual Coordination** - See request/response flow in UI

This system enables true autonomous multi-agent coordination! 🚀
