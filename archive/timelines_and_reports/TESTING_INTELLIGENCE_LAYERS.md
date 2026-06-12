# 🧪 Testing Intelligence Layers - Quick Start Guide

**Purpose:** Step-by-step guide to test natural language and tool intelligence features  
**Estimated Time:** 30-45 minutes  
**Prerequisites:** AI Agent server running (BISTART), Database access

---

## 🎯 Test 1: Natural Language Communication (15 minutes)

### Goal
Verify AI uses conversational language instead of technical tool names.

### Steps

**1. Start the AI Agent Server**
```powershell
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

Wait 10-15 seconds for tools to load.

**2. Test Email Commands**
```powershell
# Test 1: Check emails
CHAT Check my unread emails

# Expected AI Response:
# ✅ "I'll check your emails" or "Let me check your inbox"
# ❌ NOT "I'll call gmail_list_messages"

# Test 2: Send email
CHAT Send an email to test@example.com with subject Hello

# Expected AI Response:
# ✅ "I'll send that email"
# ❌ NOT "I'll execute gmail_send_email"
```

**3. Test Document Commands**
```powershell
# Test 3: Create document
CHAT Create a new Google Doc titled Test Document

# Expected AI Response:
# ✅ "I'll create that document"
# ❌ NOT "I'll call google_docs_create_document"

# Test 4: List documents
CHAT Show me my recent Google Docs

# Expected AI Response:
# ✅ "I'll check your documents" or "Let me look at your docs"
# ❌ NOT "I'll call google_docs_list_documents"
```

**4. Test Calendar Commands**
```powershell
# Test 5: Calendar check
CHAT What's on my calendar today?

# Expected AI Response:
# ✅ "I'll check your calendar"
# ❌ NOT "I'll call google_calendar_list_events"
```

**5. Test Export Translations**
```powershell
# Test 6: Export with natural language
CHAT Check my emails and save to my dashboard

# Expected AI Response:
# ✅ "I'll check your emails and save to your dashboard"
# ❌ NOT "I'll call gmail_list_messages with export='synergy'"
```

### ✅ Success Criteria

- [ ] AI uses natural action verbs (check, send, create, get)
- [ ] NO technical tool names mentioned (no "gmail_list_messages")
- [ ] Export translations used ("save to your dashboard" not "export='synergy'")
- [ ] Responses sound conversational and natural

### ❌ Failure Indicators

- AI says "I'll call [tool_name]"
- AI mentions function names
- AI says "I'll execute the tool"
- AI uses technical export parameter names

---

## 🧠 Test 2: Tool Intelligence Logging (20 minutes)

### Goal
Verify tool execution data is logged to database with AI observations.

### Prerequisites

**Database Access:**
You need access to Supabase PostgreSQL with connection to `ai_infrastructure` schema.

**Connection String:**
```
postgresql://user:password@host:5432/postgres
```

### Steps

**1. Execute Multiple Tools**
```powershell
# Execute 3 tools in sequence
CHAT Check my unread emails
CHAT Get the first email
CHAT Create a document with the email content
```

**2. Check Database for Logs**

Open Supabase dashboard or use psql:

```sql
-- Query latest log entries
SELECT 
    id,
    user_id,
    tool_name,
    execution_timestamp,
    execution_duration_ms,
    execution_status,
    log_type,
    LEFT(ai_observation, 100) as observation_preview
FROM ai_infrastructure.ai_tool_intelligence_log
ORDER BY execution_timestamp DESC
LIMIT 10;
```

**3. Verify Log Entry Structure**

Each row should have:

```sql
-- Example expected row
{
    "id": 1,
    "user_id": 14,
    "tool_name": "gmail_list_messages",
    "execution_timestamp": "2025-11-27 10:30:15.123",
    "execution_duration_ms": 1250,
    "execution_status": "success",
    "log_type": "workflow",
    "ai_observation": "User checked unread emails to review inbox - common morning routine detected.",
    "user_request_original": "Check my unread emails",
    "tool_parameters": {"query": "is:unread", "max_results": 20},
    "workflow_sequence": ["gmail_list_messages"],
    "confidence_score": 85,
    "created_at": "2025-11-27 10:30:15.123"
}
```

**4. Test Workflow Detection**

Execute a multi-tool workflow:

```powershell
CHAT Check my emails
# Wait for response
CHAT Send the first one to john@example.com
# Wait for response
CHAT Create a doc summarizing the conversation
```

Check database for workflow sequence:

```sql
SELECT 
    tool_name,
    workflow_sequence,
    log_type,
    ai_observation
FROM ai_infrastructure.ai_tool_intelligence_log
WHERE user_id = 14
ORDER BY execution_timestamp DESC
LIMIT 3;
```

Expected: Last entry should have `workflow_sequence` with all 3 tools.

**5. Test Error Logging**

Trigger a tool error:

```powershell
CHAT Send email to invalid-email (no subject or body)
```

Check database:

```sql
SELECT 
    tool_name,
    execution_status,
    log_type,
    ai_observation
FROM ai_infrastructure.ai_tool_intelligence_log
WHERE execution_status = 'error'
ORDER BY execution_timestamp DESC
LIMIT 1;
```

Expected: Entry with `execution_status = 'error'` and `log_type = 'error'`.

### ✅ Success Criteria

- [ ] Database entries created after tool execution
- [ ] `execution_duration_ms` populated with numeric value
- [ ] `ai_observation` contains human-readable text
- [ ] `log_type` is one of: error, workflow, refinement, suggestion, pattern
- [ ] `tool_parameters` is valid JSONB with actual parameters
- [ ] `workflow_sequence` tracks multi-tool workflows
- [ ] `execution_status` is 'success' or 'error'
- [ ] Error tool calls also logged (not just successes)

### ❌ Failure Indicators

- No database entries created
- `execution_duration_ms` is NULL
- `ai_observation` is empty or generic
- `tool_parameters` is empty JSONB `{}`
- `workflow_sequence` not tracking multi-tool workflows
- Errors not logged

---

## 📊 Test 3: Performance Verification (10 minutes)

### Goal
Verify intelligence logging doesn't slow down tool execution.

### Steps

**1. Measure Execution Time**

```powershell
# Execute same tool multiple times
CHAT Check my emails
# Note response time

CHAT Check my emails
# Note response time

CHAT Check my emails
# Note response time
```

**2. Check Average Execution Time**

```sql
SELECT 
    tool_name,
    AVG(execution_duration_ms) as avg_duration_ms,
    MIN(execution_duration_ms) as min_duration_ms,
    MAX(execution_duration_ms) as max_duration_ms,
    COUNT(*) as execution_count
FROM ai_infrastructure.ai_tool_intelligence_log
WHERE tool_name = 'gmail_list_messages'
GROUP BY tool_name;
```

**3. Verify Logging Overhead**

Intelligence logging should add minimal overhead (<50ms per tool call).

Expected times:
- Gmail API call: ~1000-2000ms
- Intelligence logging: ~20-50ms
- Total: ~1020-2050ms

If total time exceeds 3000ms, investigate logging performance.

### ✅ Success Criteria

- [ ] Tool execution time reasonable (<3 seconds for Gmail)
- [ ] No noticeable delay from logging
- [ ] Logging happens asynchronously (doesn't block tool response)

### ❌ Failure Indicators

- Tool takes >5 seconds to execute
- Console shows logging errors
- Tool execution blocked waiting for database

---

## 🔍 Debugging Common Issues

### Issue: Natural Language Not Working

**Symptom:** AI still says "I'll call gmail_list_messages"

**Diagnosis:**
```powershell
# Check if system prompt loaded correctly
cd C:\Users\gpoli\GIT\AI_agents
python -c "from AI_infrastructure.core.unified_ai_client import UnifiedAIClient; client = UnifiedAIClient('AI_infrastructure/config/database-config.json'); print(client._get_tool_usage_instructions()[:500])"
```

**Expected Output:** Should show "CRITICAL - NATURAL LANGUAGE COMMUNICATION" section

**Fix:** Restart BISTART to reload system prompt

---

### Issue: Tool Intelligence Not Logging

**Symptom:** No database entries after tool execution

**Diagnosis:**
```powershell
# Check if logger initialized
cd C:\Users\gpoli\GIT\AI_agents
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print(f'Intelligence logger: {r.intelligence_logger}')"
```

**Expected Output:** Should show `<ToolIntelligenceLogger object at 0x...>`

**Possible Causes:**
1. Database connection string incorrect
2. Table doesn't exist
3. Logger initialization failed silently

**Fix 1: Check Database Table**
```sql
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'ai_infrastructure' 
    AND table_name = 'ai_tool_intelligence_log'
);
```

If FALSE, run migration:
```powershell
psql -U postgres -d ai_infrastructure -f AI_infrastructure/database_migrations/create_tool_intelligence_log_table.sql
```

**Fix 2: Check Logger Initialization**
Check Flask console output when starting BISTART:
```
[INTELLIGENCE] Tool Intelligence Logger initialized
```

If missing, check for errors:
```
[INTELLIGENCE] Could not initialize Tool Intelligence Logger: [error message]
```

---

### Issue: Execution Time Not Logged

**Symptom:** `execution_duration_ms` is NULL in database

**Diagnosis:**
```sql
SELECT execution_duration_ms 
FROM ai_infrastructure.ai_tool_intelligence_log 
WHERE execution_duration_ms IS NULL 
LIMIT 5;
```

**Possible Cause:** `time` module not imported in registry_v3.py

**Fix:** Verify line 15 in `tools/registry_v3.py`:
```python
import time
```

---

### Issue: Workflow Sequence Empty

**Symptom:** `workflow_sequence` is NULL or `[]`

**Possible Cause:** `_workflow_context` not passed in execute_tool() call

**Expected Call Pattern:**
```python
registry.execute_tool(
    tool_name='gmail_list_messages',
    _user_id=14,
    _user_request='Check emails',
    _workflow_context={'tool_sequence': ['previous_tool', 'current_tool']}
)
```

**Note:** Workflow context is optional - NULL is acceptable for first tool call

---

## 📝 Test Results Template

Copy and fill out after testing:

```
INTELLIGENCE LAYERS - TEST RESULTS
Date: [Fill in]
Tester: [Your name]

=== NATURAL LANGUAGE (Layer 2) ===
✅ / ❌ AI uses natural verbs (check, send, create)
✅ / ❌ No technical tool names mentioned
✅ / ❌ Export translations working
Notes: [Add observations]

=== TOOL INTELLIGENCE (Layer 3) ===
✅ / ❌ Database entries created
✅ / ❌ Execution time logged
✅ / ❌ AI observations generated
✅ / ❌ Workflow sequences tracked
✅ / ❌ Error logging works
Notes: [Add observations]

=== PERFORMANCE ===
Average execution time: [X ms]
Logging overhead: [X ms]
✅ / ❌ Performance acceptable (<3 sec)
Notes: [Add observations]

=== OVERALL STATUS ===
[PASS / FAIL / PARTIAL]

Issues Found:
1. [List any issues]
2. [...]

Recommendations:
1. [Suggested improvements]
2. [...]
```

---

## 🎯 Next Steps After Testing

**If All Tests Pass:**
1. Move to Priority 3: Implement Multi-Modal in Gmail
2. Create end-to-end test script
3. Begin Outlook tools implementation

**If Tests Fail:**
1. Document failure details using template above
2. Use debugging guide to diagnose issues
3. Fix blockers before continuing to multi-modal

**Data Collection:**
- Run for 24 hours with intelligence logging
- Analyze patterns in `ai_tool_intelligence_log`
- Identify most common workflows for automation

---

**Last Updated:** November 27, 2025  
**Status:** Ready for testing  
**Estimated Time:** 30-45 minutes total
