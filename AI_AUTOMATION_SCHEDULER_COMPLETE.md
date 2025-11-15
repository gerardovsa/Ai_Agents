# AI Automation Scheduler System
## Complete Documentation

**Status:** ✅ Production Ready  
**Created:** November 15, 2025  
**Version:** 1.0.0  

---

## Overview

The AI Automation Scheduler is a flexible, robust system that allows both users and AI agents to create, manage, and execute scheduled automation tasks. It provides a complete automation pipeline with support for:

- **Scheduled Tasks** - Cron expressions and datetime triggers
- **Thread Linking** - Connect tasks to specific conversation threads
- **Agent Assignment** - Specify which AI agent executes the task
- **Location Tracking** - Know where the task runs (dashboard, synergy, etc.)
- **Approval Workflow** - Optional user approval before execution
- **Webhook Triggers** - External system integration
- **Execution History** - Complete audit trail with logs

---

## Architecture

### Database Tables

**1. `scheduled_tasks` Table:**
```sql
CREATE TABLE scheduled_tasks (
    task_id TEXT PRIMARY KEY,               -- Unique identifier
    task_name TEXT NOT NULL,                -- Display name
    description TEXT,                       -- What this task does
    created_by TEXT NOT NULL,               -- 'user' or 'ai'
    created_by_user_id INTEGER,             -- Who created it
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    
    -- Schedule Configuration
    trigger_type TEXT NOT NULL,             -- 'cron', 'datetime', 'webhook', 'conditional', 'manual'
    cron_expression TEXT,                   -- e.g., '0 9 * * 1-5' (Mon-Fri 9am)
    datetime_trigger TIMESTAMP,             -- One-time execution time
    webhook_url TEXT,                       -- For webhook triggers
    condition_config TEXT,                  -- JSON condition definition
    
    -- Execution Configuration
    action_type TEXT NOT NULL,              -- 'resume_session', 'send_message', 'execute_tool', 'run_workflow'
    
    -- Linking
    synergy_session_id TEXT,                -- Link to Synergy session
    thread_id TEXT,                         -- Specific conversation thread
    agent_name TEXT,                        -- Which agent (Prime, Email, etc.)
    location TEXT,                          -- Where it runs (dashboard, synergy_sidebar, etc.)
    
    -- Action Configuration
    action_payload TEXT,                    -- JSON with action-specific data
    context_instructions TEXT,              -- Additional AI instructions
    
    -- Approval Workflow
    requires_approval BOOLEAN DEFAULT 0,
    approval_status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    approval_note TEXT,
    approved_by_user_id INTEGER,
    approved_at TIMESTAMP,
    
    -- Status & Control
    enabled BOOLEAN DEFAULT 1,
    last_execution_time TIMESTAMP,
    next_execution_time TIMESTAMP,
    execution_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    retry_delay_seconds INTEGER DEFAULT 300,
    
    -- Metadata
    tags TEXT,                              -- JSON array
    priority INTEGER DEFAULT 5,             -- 1-10 (10 = highest)
    timeout_seconds INTEGER DEFAULT 300
);
```

**2. `task_executions` Table:**
```sql
CREATE TABLE task_executions (
    execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT NOT NULL,                   -- 'running', 'completed', 'failed', 'timeout', 'cancelled'
    result_data TEXT,                       -- JSON execution results
    error_message TEXT,
    retry_attempt INTEGER DEFAULT 0,
    execution_duration_ms INTEGER,
    
    FOREIGN KEY (task_id) REFERENCES scheduled_tasks(task_id)
);
```

---

## API Endpoints

### 1. Create Task
**POST** `/api/scheduler/tasks`

**Request Body:**
```json
{
    "task_name": "Send Daily Report",
    "description": "Email daily analytics report to management",
    "created_by": "ai",
    "created_by_user_id": 1,
    
    "trigger_type": "cron",
    "cron_expression": "0 9 * * 1-5",
    
    "action_type": "resume_session",
    "synergy_session_id": "sess_12345678",
    "thread_id": "thread_abc123",
    "agent_name": "Email Agent",
    "location": "synergy_sidebar",
    
    "action_payload": {
        "message": "Generate and send the daily report",
        "tools": ["gmail_send_email", "google_sheets_read"],
        "context": {
            "report_type": "daily_analytics",
            "recipients": ["manager@company.com"]
        }
    },
    "context_instructions": "Include last 7 days of data. Use professional tone.",
    
    "requires_approval": false,
    "enabled": true,
    "tags": ["reports", "email", "daily"],
    "priority": 7
}
```

**Response:**
```json
{
    "success": true,
    "task_id": "task_20251115_093000_Send_Daily_Report",
    "task": { /* full task object */ },
    "message": "Task 'Send Daily Report' created successfully"
}
```

---

### 2. List Tasks
**GET** `/api/scheduler/tasks`

**Query Parameters:**
- `synergy_session_id` - Filter by session
- `thread_id` - Filter by thread
- `agent_name` - Filter by agent
- `enabled` - Filter by status (true/false)
- `created_by` - Filter by creator (user/ai)

**Response:**
```json
{
    "success": true,
    "tasks": [
        {
            "task_id": "task_20251115_093000_Send_Daily_Report",
            "task_name": "Send Daily Report",
            "trigger_type": "cron",
            "cron_expression": "0 9 * * 1-5",
            "next_execution_time": "2025-11-18T09:00:00Z",
            "enabled": true,
            /* ... */
        }
    ],
    "count": 15
}
```

---

### 3. Get Task Details
**GET** `/api/scheduler/tasks/<task_id>`

**Response:**
```json
{
    "success": true,
    "task": {
        "task_id": "task_20251115_093000_Send_Daily_Report",
        "task_name": "Send Daily Report",
        "description": "Email daily analytics report",
        "created_by": "ai",
        "trigger_type": "cron",
        "cron_expression": "0 9 * * 1-5",
        "action_type": "resume_session",
        "synergy_session_id": "sess_12345678",
        "thread_id": "thread_abc123",
        "agent_name": "Email Agent",
        "enabled": true,
        "execution_count": 45,
        "last_execution_time": "2025-11-15T09:00:00Z",
        "next_execution_time": "2025-11-18T09:00:00Z"
    }
}
```

---

### 4. Update Task
**PATCH** `/api/scheduler/tasks/<task_id>`

**Request Body (partial updates):**
```json
{
    "enabled": false,
    "cron_expression": "0 10 * * 1-5",
    "priority": 9
}
```

---

### 5. Delete Task
**DELETE** `/api/scheduler/tasks/<task_id>`

**Response:**
```json
{
    "success": true,
    "message": "Task task_20251115_093000_Send_Daily_Report deleted successfully"
}
```

---

### 6. Manual Execution
**POST** `/api/scheduler/tasks/<task_id>/execute`

Triggers immediate execution regardless of schedule.

---

### 7. Approve Task
**POST** `/api/scheduler/tasks/<task_id>/approve`

**Request Body:**
```json
{
    "approved_by_user_id": 1,
    "approval_note": "Approved for production use"
}
```

---

### 8. Reject Task
**POST** `/api/scheduler/tasks/<task_id>/reject`

**Request Body:**
```json
{
    "approved_by_user_id": 1,
    "approval_note": "Security concerns - needs review"
}
```

---

### 9. Execution History
**GET** `/api/scheduler/tasks/<task_id>/history?limit=50`

**Response:**
```json
{
    "success": true,
    "task_id": "task_20251115_093000_Send_Daily_Report",
    "executions": [
        {
            "execution_id": 123,
            "task_id": "task_20251115_093000_Send_Daily_Report",
            "started_at": "2025-11-15T09:00:00Z",
            "completed_at": "2025-11-15T09:02:15Z",
            "status": "completed",
            "result_data": { "emails_sent": 5 },
            "execution_duration_ms": 135000
        }
    ],
    "count": 50
}
```

---

### 10. Webhook Trigger
**POST** `/api/webhook/scheduler/trigger/<task_id>`

External systems can trigger tasks via this endpoint.

---

## Action Types

### 1. `resume_session`
Resumes a Synergy session with AI agent.

**Configuration:**
```json
{
    "action_type": "resume_session",
    "synergy_session_id": "sess_12345678",
    "thread_id": "thread_abc123",
    "agent_name": "Email Agent",
    "context_instructions": "Complete the pending checklist items",
    "action_payload": {
        "auto_approve": true,
        "skip_items": []
    }
}
```

---

### 2. `send_message`
Sends a message to an AI agent.

**Configuration:**
```json
{
    "action_type": "send_message",
    "thread_id": "thread_abc123",
    "agent_name": "Prime Agent",
    "action_payload": {
        "message": "What's the status of project Alpha?",
        "context": {
            "project_id": "alpha_2025"
        }
    }
}
```

---

### 3. `execute_tool`
Executes a specific tool directly.

**Configuration:**
```json
{
    "action_type": "execute_tool",
    "action_payload": {
        "tool_name": "gmail_send_email",
        "tool_params": {
            "to": "user@example.com",
            "subject": "Daily Report",
            "body": "Report content here"
        }
    }
}
```

---

### 4. `run_workflow`
Executes a multi-step workflow.

**Configuration:**
```json
{
    "action_type": "run_workflow",
    "action_payload": {
        "steps": [
            {
                "type": "tool",
                "tool_name": "google_sheets_read",
                "tool_params": { "spreadsheet_id": "abc123" }
            },
            {
                "type": "delay",
                "seconds": 2
            },
            {
                "type": "message",
                "message": "Process the data from the spreadsheet",
                "agent_name": "Data Agent"
            }
        ]
    }
}
```

---

## Trigger Types

### 1. `cron` - Recurring Schedule
Uses standard cron expressions:

**Examples:**
```
"0 9 * * 1-5"    → Monday-Friday at 9:00 AM
"0 */6 * * *"    → Every 6 hours
"0 0 1 * *"      → First day of each month at midnight
"*/15 * * * *"   → Every 15 minutes
"0 0 * * 0"      → Every Sunday at midnight
```

**Cron Format:**
```
* * * * *
│ │ │ │ │
│ │ │ │ └─ Day of week (0-7, 0 and 7 are Sunday)
│ │ │ └─── Month (1-12)
│ │ └───── Day of month (1-31)
│ └─────── Hour (0-23)
└───────── Minute (0-59)
```

---

### 2. `datetime` - One-Time Trigger
Execute once at a specific datetime:

```json
{
    "trigger_type": "datetime",
    "datetime_trigger": "2025-11-16T14:00:00Z"
}
```

---

### 3. `webhook` - External Trigger
Task triggered by external webhook call:

```json
{
    "trigger_type": "webhook",
    "webhook_url": "/api/webhook/scheduler/trigger/<task_id>"
}
```

---

### 4. `conditional` - Event-Based
Trigger when certain conditions are met (checked periodically):

```json
{
    "trigger_type": "conditional",
    "condition_config": {
        "type": "checklist_completed",
        "session_id": "sess_12345678"
    }
}
```

---

### 5. `manual` - On-Demand
Only executes when manually triggered via API.

---

## Use Cases

### 1. Daily Report Email
```json
{
    "task_name": "Daily Analytics Report",
    "trigger_type": "cron",
    "cron_expression": "0 9 * * 1-5",
    "action_type": "resume_session",
    "synergy_session_id": "sess_reports",
    "agent_name": "Email Agent",
    "context_instructions": "Generate daily report with last 24 hours of data"
}
```

---

### 2. Birthday Reminder
```json
{
    "task_name": "John's Birthday Reminder",
    "trigger_type": "datetime",
    "datetime_trigger": "2025-12-01T08:00:00Z",
    "action_type": "send_message",
    "thread_id": "thread_reminders",
    "agent_name": "Prime Agent",
    "action_payload": {
        "message": "Remind team about John's birthday today"
    }
}
```

---

### 3. Hourly News Check
```json
{
    "task_name": "Check Industry News",
    "trigger_type": "cron",
    "cron_expression": "0 * * * *",
    "action_type": "execute_tool",
    "action_payload": {
        "tool_name": "web_search",
        "tool_params": {
            "query": "AI industry news",
            "max_results": 5
        }
    }
}
```

---

### 4. Auto-Execute Approved Tasks
```json
{
    "task_name": "Execute Approved Marketing Campaign",
    "trigger_type": "conditional",
    "condition_config": {
        "type": "approval_granted",
        "session_id": "sess_marketing"
    },
    "action_type": "resume_session",
    "synergy_session_id": "sess_marketing",
    "agent_name": "Marketing Agent"
}
```

---

## AI Agent Integration

### How AI Creates Scheduled Tasks

When a user asks the AI to "schedule a task" or "set up automation", the AI can:

1. **Understand the request:**
   ```
   User: "Send me a daily report every weekday at 9am"
   ```

2. **Create the task:**
   ```javascript
   await fetch('/api/scheduler/tasks', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({
           task_name: 'Daily Report Email',
           created_by: 'ai',
           created_by_user_id: 1,
           trigger_type: 'cron',
           cron_expression: '0 9 * * 1-5',
           action_type: 'resume_session',
           synergy_session_id: currentSessionId,
           thread_id: currentThreadId,
           agent_name: 'Email Agent',
           context_instructions: 'Generate and send daily report',
           requires_approval: false
       })
   });
   ```

3. **Confirm to user:**
   ```
   AI: "I've scheduled a daily report to be sent every weekday at 9:00 AM. 
        The task will run automatically using the Email Agent. 
        Task ID: task_20251115_093000_Daily_Report_Email"
   ```

---

### Accessing Task Status

AI can query task status:

```javascript
const response = await fetch('/api/scheduler/tasks?synergy_session_id=' + sessionId);
const data = await response.json();

// Check next execution
const nextRun = data.tasks[0].next_execution_time;
// Check execution history
const history = await fetch('/api/scheduler/tasks/' + taskId + '/history');
```

---

## Frontend Integration

### Display Scheduled Tasks in Synergy

Add a "Scheduled Automation" section to Synergy cards:

```html
<div class="automation-badge">
    <i class="fas fa-clock"></i>
    <span>Next: Tomorrow 9:00 AM</span>
</div>
```

### Schedule Task Button

Add button to card actions:

```html
<button onclick="showScheduleModal(sessionId)">
    <i class="fas fa-calendar-plus"></i> Schedule AI Trigger
</button>
```

### Schedule Modal

Show modal for creating scheduled tasks:

```javascript
function showScheduleModal(sessionId) {
    // Show modal with:
    // - Trigger type selector (cron/datetime)
    // - Cron expression builder
    // - Datetime picker
    // - Agent selector
    // - Action configuration
}
```

---

## Error Handling & Retries

### Automatic Retry Logic

Tasks automatically retry on failure:

1. **Failure occurs** - Task execution fails
2. **Check retry count** - Compare `failure_count` to `max_retries`
3. **Schedule retry** - Wait `retry_delay_seconds` (default: 5 minutes)
4. **Re-execute** - Try again with incremented retry attempt
5. **Stop after max retries** - Log final failure

### Timeout Protection

Tasks automatically timeout after `timeout_seconds` (default: 5 minutes).

---

## Security Considerations

### Approval Workflow

For sensitive operations, require approval:

```json
{
    "requires_approval": true,
    "approval_status": "pending"
}
```

User must explicitly approve before execution.

### User Isolation

Tasks are isolated by `created_by_user_id` - users only see their own tasks.

### Webhook Authentication

Webhook endpoints should validate origin and include authentication tokens.

---

## Performance

### Background Execution

- Scheduler runs in background thread
- Does not block Flask request handling
- Supports concurrent task execution

### Database Indexes

Optimized indexes for:
- `enabled` status lookups
- `next_execution_time` queries
- `synergy_session_id` filtering
- `thread_id` filtering

---

## Monitoring & Logs

### Execution History

Complete audit trail in `task_executions` table:
- Start/end timestamps
- Execution duration
- Success/failure status
- Error messages
- Result data

### Task Statistics

Track per-task metrics:
- `execution_count` - Total runs
- `failure_count` - Total failures
- `last_execution_time` - Most recent run
- `next_execution_time` - Upcoming run

---

## Future Enhancements

1. **WebSocket Notifications** - Real-time task execution updates
2. **Task Dependencies** - Chain tasks (run B after A completes)
3. **Conditional Triggers** - More advanced event-based triggers
4. **Task Templates** - Pre-built automation templates
5. **Execution Quotas** - Limit execution count or frequency
6. **Cost Tracking** - Track API costs per task
7. **A/B Testing** - Run multiple versions of tasks
8. **Rollback Support** - Undo task execution if needed

---

## Summary

The AI Automation Scheduler provides a complete automation pipeline with:

✅ **Flexible Scheduling** - Cron, datetime, webhooks, conditional  
✅ **Thread Linking** - Connect to specific conversations  
✅ **Agent Assignment** - Specify which AI agent executes  
✅ **Approval Workflow** - Optional user approval gates  
✅ **Complete Audit Trail** - Execution history and logs  
✅ **Automatic Retries** - Fault tolerance built-in  
✅ **User & AI Created** - Both can create automations  
✅ **Production Ready** - Database, API, and scheduler all complete  

**Total Implementation:** ~1,000 lines of backend code  
**API Endpoints:** 10 complete endpoints  
**Database Tables:** 2 tables with indexes  
**Status:** ✅ Ready for immediate use  

---

**Last Updated:** November 15, 2025  
**Version:** 1.0.0  
**Author:** GitHub Copilot (Claude Sonnet 4.5)
