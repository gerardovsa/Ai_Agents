# Agent Coordination Tools - Quick Reference

## Overview
Multi-agent coordination system with 3 tools for distributing work across 26 NATO-named AI agents (Alpha through Zulu).

## Discovery Commands

**For AI agents to discover these tools:**

```python
# Method 1: List tools by platform name (direct)
list_platform_tools('advanced_agent_coordination')

# Method 2: List tools using alias
list_platform_tools('agent')
list_platform_tools('agents')
list_platform_tools('multi-agent')
list_platform_tools('coordination')

# Method 3: Search by task
recommend_tools_for_task('distribute work agents')
recommend_tools_for_task('agent coordination')
recommend_tools_for_task('delegate tasks')

# Method 4: Get specific tool schema
get_tool_schema('assign_and_activate_agent_with_slugs')
```

## Tool List

### 1. assign_and_activate_agent_with_slugs
**Purpose:** Primary tool for work distribution  
**Description:** ALL-IN-ONE COMBO TOOL - Assign multiple resource slugs to an agent thread, send instructions, and optionally trigger agent activation with automatic UI updates.

**Use for:**
- Distributing work to agents
- Creating agent threads
- Assigning workflows, docs, synergy sessions
- Automatic UI updates

**Example:**
```python
assign_and_activate_agent_with_slugs(
    target_agent='Alpha',  # NATO name, 'agent-1', or '1'
    thread_title='Build E-Commerce Frontend',
    instructions='Create React frontend with Material-UI...',
    slugs={
        'workflow_slug': 'react-workflow',
        'synergy_session_id': 'sess_abc123'
    },
    auto_trigger=True,
    open_ui=True
)
```

**Parameters:**
- `target_agent` (string): NATO name ('Alpha'-'Zulu'), location ('agent-1'-'agent-26'), or number (1-26)
- `thread_title` (string): Clear, descriptive title for the work
- `instructions` (string): Detailed instructions to send to agent
- `slugs` (object): Resource slugs to attach
  - `workflow_slug`: Visual automation workflow
  - `internal_doc_slug`: Internal documentation
  - `synergy_session_id`: Synergy project card
- `auto_trigger` (boolean): Immediately trigger agent processing
- `open_ui` (boolean): Automatically open agent column in UI

---

###  2. request_update_from_thread
**Purpose:** Cross-thread communication initiator  
**Description:** Request information or status from another agent's thread with priority levels and tracking.

**Use for:**
- Requesting status updates
- Asking for deliverables
- Coordinating between agents
- Requesting resources

**Example:**
```python
request_update_from_thread(
    target_thread_id='Bravo',
    request_message='What is the status of the API endpoints?',
    request_type='status_update',
    priority='high',
    wait_for_response=True,
    timeout=300
)
```

**Parameters:**
- `target_thread_id` (string): Target agent identifier
- `request_message` (string): The request/question
- `request_type` (string): Type - 'status_update', 'deliverable', 'question', 'coordination', 'resource_request'
- `priority` (string): Priority - 'low' (blue), 'medium' (yellow), 'high' (orange), 'urgent' (red)
- `wait_for_response` (boolean): Poll for response
- `timeout` (integer): Polling timeout in seconds

---

### 3. respond_to_cross_thread_request
**Purpose:** Cross-thread response handler  
**Description:** Respond to incoming requests from other agents, updating request status and notifying source thread.

**Use for:**
- Responding to status requests
- Providing deliverables
- Answering questions
- Completing request/response cycle

**Example:**
```python
respond_to_cross_thread_request(
    request_id='req_abc123',
    response_message='API is 90% complete. Endpoints ready for testing by EOD.'
)
```

**Parameters:**
- `request_id` (string): Request ID from database
- `response_message` (string): Response text

---

## Agent Names (NATO Alphabet)

26 agents available:
- **Alpha** (1)
- **Bravo** (2)
- **Charlie** (3)
- **Delta** (4)
- **Echo** (5)
- **Foxtrot** (6)
- **Golf** (7)
- **Hotel** (8)
- **India** (9)
- **Juliet** (10)
- **Kilo** (11)
- **Lima** (12)
- **Mike** (13)
- **November** (14)
- **Oscar** (15)
- **Papa** (16)
- **Quebec** (17)
- **Romeo** (18)
- **Sierra** (19)
- **Tango** (20)
- **Uniform** (21)
- **Victor** (22)
- **Whiskey** (23)
- **X-ray** (24)
- **Yankee** (25)
- **Zulu** (26)

## Workflow Patterns

### A) Distribute Multi-Agent Project
1. Call `assign_and_activate_agent_with_slugs` for each agent (Alpha, Bravo, Charlie)
2. Each call assigns work, attaches resources, and opens UI
3. Set `auto_trigger=True` to immediately start agents
4. Result: 3 agents working in parallel with full coordination

### B) Request/Response Cycle
1. Agent Alpha calls `request_update_from_thread(target='Bravo', ...)`
2. Request inserted into Bravo's thread with priority icon
3. Agent Bravo processes request
4. Agent Bravo calls `respond_to_cross_thread_request(request_id=..., response=...)`
5. Response delivered back to Alpha's thread
6. Result: Cross-agent communication with tracking

### C) Synergy Integration
1. Distribute work across 3 agents with same `synergy_session_id`
2. All agents linked to same Synergy project card
3. Updates from any agent visible in central dashboard
4. Result: Unified project view with multi-agent progress

## Key Features

- **Flexible Identifiers:** 'Alpha', 'agent-1', or '1' all work the same
- **UI Automation:** Automatic tab switching, column opening, thread info display
- **Resource Linking:** Attach workflows, internal docs, synergy sessions
- **Cross-Thread Messaging:** Agents can request updates and receive responses
- **Database Tracking:** All requests/responses tracked in `cross_thread_requests` table
- **Priority Levels:** 4 priority levels with color-coded icons (blue/yellow/orange/red)

## Status & Testing

- **Status:** ✅ PRODUCTION READY - All backend tests passing (4/4)
- **Tools:** 3 total
- **Platform:** `advanced_agent_coordination`
- **Database:** `cross_thread_requests` table with indexed queries
- **UI:** Command processor ready (450+ lines JavaScript)
- **Meta Tools:** Fully integrated with 8+ discovery aliases

## Related Documentation

- Backend Implementation: `tools/implementations/advanced_agent_coordination.py` (600+ lines)
- Tool Schemas: `tools/schemas/advanced_agent_coordination_tools.json` (265 lines)
- Database Migration: `AGENT_COORDINATION_IMPLEMENTATION_COMPLETE.md`
- UI Module: `UI/external/modules/ui-command-processor.js` (450+ lines)
- Test Suite: `test_agent_discovery.py` (234 lines)

---

**Last Updated:** January 2025  
**Version:** 1.0.0  
**Integration Status:** Meta tools integrated, discovery paths validated
