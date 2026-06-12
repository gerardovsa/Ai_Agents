# AI Scheduler Quick Reference
## For AI Agents Creating Scheduled Tasks

---

## How to Create a Scheduled Task

### 1. User Asks to Schedule Something

**Example User Requests:**
- "Send me a daily report every weekday at 9am"
- "Remind me tomorrow at 2pm to call John"
- "Check the stock levels every hour"
- "Automate the weekly newsletter on Fridays"

### 2. AI Creates the Task via API

**API Call:**
```javascript
POST /api/scheduler/tasks

{
    "task_name": "Daily Report Email",
    "description": "Send daily analytics report to user",
    "created_by": "ai",
    "created_by_user_id": USER_ID,
    
    // SCHEDULE (choose one):
    "trigger_type": "cron",                 // For recurring
    "cron_expression": "0 9 * * 1-5",       // Mon-Fri 9am
    // OR
    "trigger_type": "datetime",             // For one-time
    "datetime_trigger": "2025-11-16T14:00:00Z",
    
    // ACTION:
    "action_type": "resume_session",        // What to do
    "synergy_session_id": SESSION_ID,       // Which session
    "thread_id": THREAD_ID,                 // Which thread
    "agent_name": "Email Agent",            // Which agent
    "location": "synergy_sidebar",          // Where it runs
    
    // INSTRUCTIONS:
    "context_instructions": "Generate report with last 7 days data",
    "action_payload": {
        "message": "Generate and send the daily report",
        "tools": ["gmail_send_email"],
        "context": {"report_type": "daily"}
    },
    
    // APPROVAL (optional):
    "requires_approval": false,             // Set true for sensitive ops
    
    // METADATA:
    "enabled": true,
    "tags": ["reports", "email", "daily"],
    "priority": 7
}
```

### 3. AI Confirms to User

```
"I've scheduled a daily report to be sent every weekday at 9:00 AM. The Email Agent will automatically generate and send the report. Task ID: task_20251115_093000_Daily_Report_Email"
```

---

## Common Cron Patterns

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

// CUSTOM
"0 10,14,16 * * *"    // Daily at 10am, 2pm, 4pm
"*/15 9-17 * * 1-5"   // Every 15 min, 9am-5pm, Mon-Fri
```

**Cron Format:**
```
┌─ Minute (0-59)
│ ┌─ Hour (0-23)
│ │ ┌─ Day of Month (1-31)
│ │ │ ┌─ Month (1-12)
│ │ │ │ ┌─ Day of Week (0-7, 0=Sunday)
│ │ │ │ │
* * * * *
```

---

## Action Types

### 1. `resume_session` - Resume Synergy Session
```json
{
    "action_type": "resume_session",
    "synergy_session_id": "sess_12345678",
    "thread_id": "thread_abc123",
    "agent_name": "Email Agent",
    "context_instructions": "Complete pending checklist items"
}
```

### 2. `send_message` - Send Message to Agent
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

### 3. `execute_tool` - Run Specific Tool
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

### 4. `run_workflow` - Multi-Step Automation
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

## Quick Decision Tree

```
User wants to schedule something?
├─ ONE TIME (specific date/time)
│  └─ Use: "trigger_type": "datetime"
│     "datetime_trigger": "2025-11-16T14:00:00Z"
│
├─ RECURRING (daily/weekly/etc)
│  └─ Use: "trigger_type": "cron"
│     "cron_expression": "0 9 * * 1-5"
│
├─ ON EVENT (webhook/condition)
│  └─ Use: "trigger_type": "webhook" or "conditional"
│
└─ MANUAL ONLY (run on demand)
   └─ Use: "trigger_type": "manual"
```

---

## Linking to Current Context

**Get Current Context:**
```javascript
const sessionId = SynergyBoard.currentSessionId;
const threadId = aiChat.currentThreadId;
const agentName = aiChat.currentAgent.name;
```

**Create Task with Context:**
```javascript
{
    "synergy_session_id": sessionId,      // Link to this session
    "thread_id": threadId,                // Link to this thread
    "agent_name": agentName,              // Use current agent
    "location": "synergy_sidebar"         // Where user is now
}
```

---

## Use Case Examples

### 1. Daily Report
```json
User: "Send me a daily report every morning at 9am"

{
    "task_name": "Daily Morning Report",
    "trigger_type": "cron",
    "cron_expression": "0 9 * * *",
    "action_type": "resume_session",
    "synergy_session_id": SESSION_ID,
    "agent_name": "Email Agent",
    "context_instructions": "Generate and send daily report"
}
```

### 2. Birthday Reminder
```json
User: "Remind me on December 1st at 8am about John's birthday"

{
    "task_name": "John's Birthday Reminder",
    "trigger_type": "datetime",
    "datetime_trigger": "2025-12-01T08:00:00Z",
    "action_type": "send_message",
    "thread_id": THREAD_ID,
    "agent_name": "Prime Agent",
    "action_payload": {
        "message": "Reminder: John's birthday is today!"
    }
}
```

### 3. Hourly Stock Check
```json
User: "Check stock levels every hour and alert if low"

{
    "task_name": "Hourly Stock Check",
    "trigger_type": "cron",
    "cron_expression": "0 * * * *",
    "action_type": "execute_tool",
    "action_payload": {
        "tool_name": "stock_management_check_low_stock"
    }
}
```

### 4. Weekly Newsletter
```json
User: "Send newsletter every Friday at 5pm"

{
    "task_name": "Weekly Newsletter",
    "trigger_type": "cron",
    "cron_expression": "0 17 * * 5",
    "action_type": "resume_session",
    "synergy_session_id": "sess_newsletter",
    "agent_name": "Marketing Agent",
    "context_instructions": "Generate and send weekly newsletter"
}
```

---

## Checking Task Status

### List All Tasks
```javascript
GET /api/scheduler/tasks

// With filters:
GET /api/scheduler/tasks?synergy_session_id=sess_12345678
GET /api/scheduler/tasks?thread_id=thread_abc123
GET /api/scheduler/tasks?agent_name=Email Agent
```

### Get Task Details
```javascript
GET /api/scheduler/tasks/task_20251115_093000_Daily_Report

Response:
{
    "task_id": "task_20251115_093000_Daily_Report",
    "next_execution_time": "2025-11-18T09:00:00Z",
    "execution_count": 45,
    "enabled": true
}
```

### View Execution History
```javascript
GET /api/scheduler/tasks/TASK_ID/history?limit=10

Response:
{
    "executions": [
        {
            "started_at": "2025-11-15T09:00:00Z",
            "status": "completed",
            "execution_duration_ms": 1350
        }
    ]
}
```

---

## Managing Tasks

### Update Task
```javascript
PATCH /api/scheduler/tasks/TASK_ID

{
    "enabled": false,              // Disable task
    "cron_expression": "0 10 * * *",  // Change schedule
    "priority": 9                  // Increase priority
}
```

### Delete Task
```javascript
DELETE /api/scheduler/tasks/TASK_ID
```

### Manually Trigger
```javascript
POST /api/scheduler/tasks/TASK_ID/execute

// Runs immediately, ignoring schedule
```

---

## Approval Workflow

### Require Approval
```json
{
    "requires_approval": true,     // User must approve
    "approval_status": "pending"   // Initial status
}
```

### Check Approval Status
```javascript
GET /api/scheduler/tasks/TASK_ID

Response:
{
    "requires_approval": true,
    "approval_status": "pending",   // pending/approved/rejected
    "approval_note": ""
}
```

### User Approves
```javascript
POST /api/scheduler/tasks/TASK_ID/approve

{
    "approved_by_user_id": USER_ID,
    "approval_note": "Approved"
}
```

---

## Error Handling

Tasks automatically retry on failure:

- **Max Retries:** 3 (configurable via `max_retries`)
- **Retry Delay:** 5 minutes (configurable via `retry_delay_seconds`)
- **Timeout:** 5 minutes (configurable via `timeout_seconds`)

```json
{
    "max_retries": 3,
    "retry_delay_seconds": 300,
    "timeout_seconds": 300
}
```

---

## Best Practices

1. **Use Descriptive Names**
   ```json
   "task_name": "Daily Sales Report - 9am"  // Good
   "task_name": "Task 1"                    // Bad
   ```

2. **Add Context Instructions**
   ```json
   "context_instructions": "Include last 7 days of data. Format as table."
   ```

3. **Set Appropriate Priority**
   ```json
   "priority": 9  // High (1-10, 10 = highest)
   ```

4. **Use Tags for Organization**
   ```json
   "tags": ["reports", "email", "daily", "analytics"]
   ```

5. **Link to Current Context**
   ```json
   "synergy_session_id": currentSessionId,
   "thread_id": currentThreadId
   ```

6. **Require Approval for Sensitive Ops**
   ```json
   "requires_approval": true  // For emails, payments, deletions
   ```

---

## Response Template

When user requests scheduling, respond like this:

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

---

## Complete Example

**User Request:**
```
"Send me a daily summary email every weekday at 9am with yesterday's analytics"
```

**AI Action:**
```javascript
POST /api/scheduler/tasks

{
    "task_name": "Daily Analytics Summary Email",
    "description": "Send email with previous day analytics",
    "created_by": "ai",
    "created_by_user_id": 1,
    
    "trigger_type": "cron",
    "cron_expression": "0 9 * * 1-5",
    
    "action_type": "resume_session",
    "synergy_session_id": "sess_analytics_report",
    "thread_id": "thread_abc123",
    "agent_name": "Email Agent",
    "location": "synergy_sidebar",
    
    "action_payload": {
        "message": "Generate daily analytics summary",
        "tools": ["gmail_send_email", "google_sheets_read"],
        "context": {
            "report_type": "daily_analytics",
            "timeframe": "yesterday"
        }
    },
    "context_instructions": "Include metrics: revenue, orders, customers. Format as table.",
    
    "requires_approval": false,
    "enabled": true,
    "tags": ["analytics", "email", "daily", "reports"],
    "priority": 7,
    "timeout_seconds": 300,
    "max_retries": 3
}
```

**AI Response:**
```
I've scheduled a daily analytics summary email to be sent every weekday at 9:00 AM.

Details:
- Task ID: task_20251115_093000_Daily_Analytics_Summary_Email
- Schedule: Monday-Friday at 9:00 AM (cron: 0 9 * * 1-5)
- Next run: Monday, November 18, 2025 at 9:00 AM
- Agent: Email Agent
- Action: Resume session and generate analytics report

The Email Agent will automatically:
1. Fetch analytics data from yesterday
2. Generate a summary table with revenue, orders, and customers
3. Send the email to your inbox

The task will run automatically in the background. You can view execution history in the Synergy Dashboard under "Scheduled Automation".
```

---

**Last Updated:** November 15, 2025  
**Status:** ✅ Ready to Use
