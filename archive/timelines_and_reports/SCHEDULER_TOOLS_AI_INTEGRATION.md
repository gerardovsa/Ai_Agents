# Scheduler Tools - AI Integration Summary

## Overview

The AI Automation Scheduler system integrates with the existing tool registry system (`registry_v3.py`) through:

1. **Tool Schema** - `tools/schemas/scheduler_tools.json` (9 tools defined)
2. **Tool Implementation** - `tools/implementations/scheduler.py` (9 wrapper functions)
3. **Backend Scheduler** - `AI_infrastructure/scheduler.py` (core automation engine)
4. **API Routes** - `AI_infrastructure/routes/scheduler_routes.py` (REST endpoints)

---

## How Tool Loading Works

### Tool Registry Flow (registry_v3.py)

```python
class RegistryV3:
    def __init__(self):
        self._load_schemas()          # Load from tools/schemas/*.json
        self._load_implementations()  # Load from tools/implementations/*.py
        
    def execute_tool(self, **kwargs):
        tool_name = kwargs.pop('tool_name')
        func = self.get_tool_function(tool_name)
        result = func(**kwargs)  # Credentials auto-injected via _user_id
```

**Key Points:**
- Registry auto-discovers all `.json` files in `tools/schemas/`
- Registry auto-discovers all `.py` files in `tools/implementations/`
- Tool functions receive `**kwargs` including:
  - `_user_id` - User ID for credential injection
  - `_injected_credentials` - Pre-fetched credentials
  - `_session_id` - Session ID for context
- No manual registration required - just add files!

---

## Scheduler Tools Available to AI

### 1. `scheduler_create_task` - PRIMARY TOOL
**When to use:** User asks to schedule/automate anything

**Common triggers:**
- "Send me a daily report at 9am"
- "Remind me tomorrow at 2pm"
- "Check stock levels every hour"
- "Automate the weekly newsletter"

**Example call:**
```javascript
registry.execute_tool(
    tool_name='scheduler_create_task',
    task_name='Daily Sales Report',
    description='Send analytics to management',
    trigger_type='cron',
    cron_expression='0 9 * * 1-5',  // Mon-Fri 9am
    action_type='resume_session',
    synergy_session_id=currentSessionId,
    thread_id=currentThreadId,
    agent_name='Email Agent',
    context_instructions='Include last 24 hours data',
    _user_id=userId,
    _session_id=sessionId
)
```

**Returns:**
```json
{
    "success": true,
    "task_id": "task_20251115_093000_Daily_Sales_Report",
    "task": { /* full task object */ },
    "message": "Task 'Daily Sales Report' created successfully",
    "next_execution_time": "2025-11-18T09:00:00Z"
}
```

---

### 2. `scheduler_list_tasks` - VIEW AUTOMATIONS
**When to use:** User asks "what tasks are scheduled?" or "show my automations"

**Example call:**
```javascript
registry.execute_tool(
    tool_name='scheduler_list_tasks',
    synergy_session_id=sessionId,  // Optional filter
    _user_id=userId
)
```

**Returns:**
```json
{
    "success": true,
    "tasks": [
        {
            "task_id": "task_20251115_093000_Daily_Report",
            "task_name": "Daily Sales Report",
            "trigger_type": "cron",
            "cron_expression": "0 9 * * 1-5",
            "next_execution_time": "2025-11-18T09:00:00Z",
            "enabled": true
        }
    ],
    "count": 15
}
```

---

### 3. `scheduler_get_task` - CHECK STATUS
**When to use:** Need details about specific task

**Example call:**
```javascript
registry.execute_tool(
    tool_name='scheduler_get_task',
    task_id='task_20251115_093000_Daily_Report',
    _user_id=userId
)
```

---

### 4. `scheduler_update_task` - MODIFY SCHEDULE
**When to use:** User asks to change schedule or disable task

**Example call:**
```javascript
registry.execute_tool(
    tool_name='scheduler_update_task',
    task_id='task_20251115_093000_Daily_Report',
    cron_expression='0 10 * * 1-5',  // Change to 10am
    enabled=false,  // Or disable
    _user_id=userId
)
```

---

### 5. `scheduler_delete_task` - CANCEL AUTOMATION
**When to use:** User asks to "cancel" or "remove" automation

---

### 6. `scheduler_execute_now` - RUN IMMEDIATELY
**When to use:** User asks to "test" or "run now"

---

### 7. `scheduler_get_history` - VIEW EXECUTION LOG
**When to use:** Debug failures or show execution history

---

### 8. `scheduler_approve_task` - APPROVE TASK
**When to use:** Task has `requires_approval=true` and user approves

---

### 9. `scheduler_reject_task` - REJECT TASK
**When to use:** Task has `requires_approval=true` and user denies

---

## Cron Expression Examples (for AI)

```javascript
// DAILY
"0 9 * * *"           // Every day at 9:00 AM
"0 0 * * *"           // Every day at midnight
"0 18 * * *"          // Every day at 6:00 PM

// WEEKLY
"0 9 * * 1"           // Every Monday at 9:00 AM
"0 9 * * 5"           // Every Friday at 9:00 AM
"0 0 * * 0"           // Every Sunday at midnight

// WEEKDAYS
"0 9 * * 1-5"         // Mon-Fri at 9:00 AM
"0 18 * * 1-5"        // Mon-Fri at 6:00 PM

// HOURLY
"0 * * * *"           // Every hour
"*/30 * * * *"        // Every 30 minutes
"0 */6 * * *"         // Every 6 hours

// MONTHLY
"0 0 1 * *"           // First day of month at midnight
"0 9 15 * *"          // 15th of month at 9:00 AM
```

**Format:**
```
┌─ Minute (0-59)
│ ┌─ Hour (0-23)
│ │ ┌─ Day of Month (1-31)
│ │ │ ┌─ Month (1-12)
│ │ │ │ ┌─ Day of Week (0-7, 0=Sunday)
* * * * *
```

---

## Action Types

### 1. `resume_session` - Resume Synergy Session
Best for: Continuing multi-platform projects

```json
{
    "action_type": "resume_session",
    "synergy_session_id": "sess_12345678",
    "thread_id": "thread_abc123",
    "agent_name": "Email Agent"
}
```

---

### 2. `send_message` - Send Message to Agent
Best for: Simple queries or status checks

```json
{
    "action_type": "send_message",
    "thread_id": "thread_abc123",
    "agent_name": "Prime Agent",
    "action_payload": {
        "message": "What's the status of project Alpha?"
    }
}
```

---

### 3. `execute_tool` - Run Specific Tool
Best for: Single tool execution (email, data fetch, etc.)

```json
{
    "action_type": "execute_tool",
    "action_payload": {
        "tool_name": "gmail_send_email",
        "tool_params": {
            "to": "user@example.com",
            "subject": "Scheduled Report",
            "body": "Report content"
        }
    }
}
```

---

### 4. `run_workflow` - Multi-Step Automation
Best for: Complex sequences

```json
{
    "action_type": "run_workflow",
    "action_payload": {
        "steps": [
            {"type": "tool", "tool_name": "google_sheets_read"},
            {"type": "delay", "seconds": 2},
            {"type": "message", "message": "Process data"}
        ]
    }
}
```

---

## AI Response Template

When creating a scheduled task, respond like this:

```
I've scheduled a [TASK_NAME] to run [SCHEDULE_DESCRIPTION].

Details:
- Task ID: [TASK_ID]
- Schedule: [CRON_OR_DATETIME]
- Next run: [NEXT_EXECUTION_TIME]
- Agent: [AGENT_NAME]
- Action: [ACTION_DESCRIPTION]

The task will run automatically in the background. You can view its status in the Synergy Dashboard under "Scheduled Automation".
```

**Example:**
```
I've scheduled a daily analytics summary email to be sent every weekday at 9:00 AM.

Details:
- Task ID: task_20251115_093000_Daily_Analytics_Summary
- Schedule: Monday-Friday at 9:00 AM (cron: 0 9 * * 1-5)
- Next run: Monday, November 18, 2025 at 9:00 AM
- Agent: Email Agent
- Action: Resume session and generate analytics report

The Email Agent will automatically:
1. Fetch analytics data from yesterday
2. Generate a summary table
3. Send the email to your inbox

The task will run automatically in the background. You can check execution history anytime by asking "show scheduler history for [task_id]".
```

---

## Linking to Current Context

**Best Practice:** Always link tasks to current context

```javascript
// Get current context
const sessionId = SynergyBoard.currentSessionId;
const threadId = aiChat.currentThreadId;
const agentName = aiChat.currentAgent.name;

// Create task with context
registry.execute_tool(
    tool_name='scheduler_create_task',
    synergy_session_id=sessionId,      // Links to current session
    thread_id=threadId,                // Links to current conversation
    agent_name=agentName,              // Uses current agent
    location='synergy_sidebar'         // Where user is now
)
```

---

## Integration with Synergy

Tasks can link to Synergy sessions via `synergy_session_id`:

```javascript
// 1. Create Synergy session
const session = await registry.execute_tool(
    tool_name='synergy_smart_project_tracker',
    title='Marketing Campaign',
    platforms_involved=['gmail', 'sheets', 'docs']
);

// 2. Create scheduled task for that session
await registry.execute_tool(
    tool_name='scheduler_create_task',
    task_name='Weekly Campaign Report',
    trigger_type='cron',
    cron_expression='0 9 * * 5',  // Friday 9am
    action_type='resume_session',
    synergy_session_id=session.session_id,  // Link to session!
    agent_name='Marketing Agent'
);
```

Now the task will automatically resume that specific Synergy session every Friday.

---

## Error Handling

All tools return consistent format:

**Success:**
```json
{
    "success": true,
    "task_id": "...",
    "message": "..."
}
```

**Error:**
```json
{
    "success": false,
    "error": "Task not found: task_abc123"
}
```

---

## Common Use Cases

### 1. Daily Email Report
```javascript
User: "Send me a daily report at 9am with yesterday's sales"

AI calls:
scheduler_create_task(
    task_name='Daily Sales Report',
    trigger_type='cron',
    cron_expression='0 9 * * *',
    action_type='send_message',
    action_payload={
        message: 'Generate sales report for yesterday'
    }
)
```

---

### 2. Birthday Reminder
```javascript
User: "Remind me on December 1st about John's birthday"

AI calls:
scheduler_create_task(
    task_name="John's Birthday Reminder",
    trigger_type='datetime',
    datetime_trigger='2025-12-01T08:00:00Z',
    action_type='send_message',
    action_payload={
        message: "Reminder: John's birthday is today!"
    }
)
```

---

### 3. Hourly Stock Check
```javascript
User: "Check stock levels every hour and alert if low"

AI calls:
scheduler_create_task(
    task_name='Hourly Stock Check',
    trigger_type='cron',
    cron_expression='0 * * * *',
    action_type='execute_tool',
    action_payload={
        tool_name: 'stock_management_check_low_stock'
    }
)
```

---

### 4. Weekly Newsletter
```javascript
User: "Send newsletter every Friday at 5pm"

AI calls:
scheduler_create_task(
    task_name='Weekly Newsletter',
    trigger_type='cron',
    cron_expression='0 17 * * 5',
    action_type='resume_session',
    synergy_session_id='sess_newsletter',
    agent_name='Marketing Agent'
)
```

---

## Summary

**Tools AI Needs:**
1. ✅ `scheduler_create_task` - Create automations (PRIMARY)
2. ✅ `scheduler_list_tasks` - View automations
3. ✅ `scheduler_get_task` - Check status
4. ✅ `scheduler_update_task` - Modify schedule
5. ✅ `scheduler_delete_task` - Cancel automation
6. ✅ `scheduler_execute_now` - Run immediately
7. ✅ `scheduler_get_history` - View execution log
8. ✅ `scheduler_approve_task` - Approve task
9. ✅ `scheduler_reject_task` - Reject task

**All tools automatically loaded via:**
- `tools/schemas/scheduler_tools.json` - Tool definitions
- `tools/implementations/scheduler.py` - Tool implementations
- `registry_v3.py` - Auto-discovery system

**No manual registration required!**

---

**Status:** ✅ Complete and Ready  
**Last Updated:** November 15, 2025
