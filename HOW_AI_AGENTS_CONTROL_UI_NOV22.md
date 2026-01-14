# How AI Agents Control the UI - Complete Guide

## Overview

AI agents don't directly interact with the UI. Instead, they use **backend tools** that return **UI command objects** in their response. These commands are then processed by the **frontend UICommandProcessor** to update the interface.

---

## The Complete Flow

```
User: "Assign this work to Agent Alpha"
         ↓
AI Agent (Claude/GPT) thinks and plans
         ↓
AI Agent calls: assign_and_activate_agent_with_slugs(...)
         ↓
Backend Tool (Python) executes:
  - Creates/updates thread in database
  - Links resources (workflows, docs, synergy)
  - Inserts instructions as user message
  ↓
Backend Tool RETURNS UI commands in response:
{
  "success": true,
  "thread_id": "abc-123",
  "ui_commands": [
    {"command": "switch_tab", "tab_name": "multi-agent"},
    {"command": "open_agent_column", "agent_number": 1},
    {"command": "show_thread_info", "thread_id": "abc-123"}
  ]
}
         ↓
Frontend receives tool response
         ↓
UnifiedMessageRenderer displays response with UI command pills
         ↓
User clicks pill OR auto-execute triggers
         ↓
UICommandProcessor.executeCommands(ui_commands)
         ↓
DOM updated: Tab switches, agent column opens, thread info shown
```

---

## Part 1: How AI Agents Learn About UI Control

### System Prompt Location
**File:** `AI_infrastructure/prompts/tool_usage_system_prompt.md`

### Tool Schema Location
**File:** `tools/schemas/advanced_agent_coordination_tools.json`

**Key Tool:** `assign_and_activate_agent_with_slugs`

**Tool Description (What AI reads):**
```json
{
  "name": "assign_and_activate_agent_with_slugs",
  "description": "ALL-IN-ONE COMBO TOOL: Assign multiple resource slugs to an agent thread, send instructions, and optionally trigger agent activation with automatic UI updates. Creates new thread if agent is empty or updates existing thread. Returns UI commands for automatic tab switching, agent column opening, and thread info display. Use this to distribute work across agents with complete coordination.",
  "parameters": {
    "target_agent": "Alpha|Bravo|...|agent-1|...|1-26",
    "thread_title": "Clear descriptive title",
    "instructions": "Detailed instructions for agent",
    "slugs": {
      "workflow_slug": "Optional workflow link",
      "internal_doc_slug": "Optional doc link",
      "synergy_session_id": "Optional synergy link"
    },
    "auto_trigger": false,  // Trigger agent AI processing?
    "open_ui": true         // Return UI commands?
  },
  "returns": {
    "ui_commands": [
      {"command": "switch_tab", "tab_name": "multi-agent"},
      {"command": "open_agent_column", "agent_number": 1},
      {"command": "show_thread_info", "thread_id": "..."}
    ]
  }
}
```

### Example in System Prompt

The system prompt teaches AI to think in this pattern:

```markdown
# USER REQUEST HANDLING

When user says: "Assign this to Alpha"

AI thinks:
1. Need to use assign_and_activate_agent_with_slugs tool
2. Set target_agent="Alpha"
3. Set thread_title from context
4. Set instructions with clear details
5. Set open_ui=true to get UI commands
6. Tool will return ui_commands array
7. Frontend will process commands automatically
```

**AI does NOT need to know:**
- HTML structure
- CSS selectors
- JavaScript code
- DOM manipulation
- Event handling

**AI only needs to know:**
- Which tool to call
- What parameters to pass
- That `ui_commands` will be returned
- That frontend will handle execution

---

## Part 2: Backend Tool Implementation

### File: `tools/implementations/advanced_agent_coordination.py`

### Function: `assign_and_activate_agent_with_slugs()`

**Key Code (Lines 250-295):**
```python
def assign_and_activate_agent_with_slugs(
    target_agent: str,
    thread_title: str,
    instructions: str,
    slugs: Optional[Dict] = None,
    auto_trigger: bool = False,
    open_ui: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    ALL-IN-ONE: Assign resources + send instructions + return UI commands
    """
    
    # 1. Parse agent identifier (NATO/number/location)
    location = parse_agent_identifier(target_agent)
    
    # 2. Create or update thread in database
    thread_id = create_or_update_thread(location, thread_title, slugs)
    
    # 3. Insert instructions as user message
    message_id = insert_user_message(thread_id, instructions)
    
    # 4. Build result
    result = {
        'success': True,
        'thread_id': thread_id,
        'thread_location': location,
        'assigned_slugs': slugs or {},
        'message_id': message_id
    }
    
    # 5. ADD UI COMMANDS (if requested)
    if open_ui:
        ui_commands = []
        
        # Command 1: Switch to Multi-Agent tab
        ui_commands.append({
            'command': 'switch_tab',
            'tab_name': 'multi-agent'
        })
        
        # Command 2: Open agent column
        agent_num = int(location.split('-')[1])
        ui_commands.append({
            'command': 'open_agent_column',
            'agent_location': location,
            'agent_number': agent_num,
            'agent_name': get_nato_name(agent_num),
            'highlight': True
        })
        
        # Command 3: Show thread info with badges
        ui_commands.append({
            'command': 'show_thread_info',
            'thread_id': thread_id,
            'thread_location': location,
            'badges': {
                'workflow': slugs.get('workflow_title'),
                'internal_doc': slugs.get('internal_doc_title'),
                'synergy': slugs.get('synergy_session_id') is not None
            }
        })
        
        # Command 4: Trigger agent (if auto_trigger=True)
        if auto_trigger:
            ui_commands.append({
                'command': 'trigger_agent_request',
                'thread_id': thread_id,
                'agent_location': location,
                'message_id': message_id
            })
        
        # ADD TO RESULT
        result['ui_commands'] = ui_commands
    
    return result
```

**Result Example:**
```python
{
    "success": True,
    "thread_id": "abc-123-def-456",
    "thread_location": "agent-1",
    "assigned_slugs": {
        "workflow_slug": "react-frontend",
        "workflow_title": "React Build Process"
    },
    "message_id": "msg-789",
    "ui_commands": [
        {
            "command": "switch_tab",
            "tab_name": "multi-agent"
        },
        {
            "command": "open_agent_column",
            "agent_location": "agent-1",
            "agent_number": 1,
            "agent_name": "Alpha",
            "highlight": True
        },
        {
            "command": "show_thread_info",
            "thread_id": "abc-123-def-456",
            "thread_location": "agent-1",
            "badges": {
                "workflow": "React Build Process",
                "internal_doc": None,
                "synergy": False
            }
        }
    ]
}
```

---

## Part 3: Frontend UI Command Processing

### File: `UI/external/modules/ui-command-processor.js`

### Object: `UICommandProcessor`

**Key Methods:**

#### 1. `executeCommands(commands)`
Main entry point - processes array of UI command objects

```javascript
executeCommands: function (commands) {
    if (!Array.isArray(commands)) {
        console.warn('[UICommandProcessor] Commands must be an array');
        return;
    }

    console.log(`[UICommandProcessor] Processing ${commands.length} commands`);

    commands.forEach((cmd, index) => {
        try {
            this.executeCommand(cmd, index);
        } catch (error) {
            console.error(`[UICommandProcessor] Error executing command ${index}:`, error, cmd);
        }
    });
}
```

#### 2. `executeCommand(cmd, index)`
Routes individual commands to handlers

```javascript
executeCommand: function (cmd, index) {
    const commandType = cmd.command || cmd.type;

    console.log(`[UICommandProcessor] Executing command ${index}: ${commandType}`);

    switch (commandType) {
        case 'switch_tab':
            this.switchTab(cmd);
            break;

        case 'open_agent_column':
            this.openAgentColumn(cmd);
            break;

        case 'show_thread_info':
            this.showThreadInfo(cmd);
            break;

        case 'trigger_agent_request':
            this.triggerAgentRequest(cmd);
            break;

        case 'send_cross_thread_request':
            this.sendCrossThreadRequest(cmd);
            break;

        case 'receive_cross_thread_response':
            this.receiveCrossThreadResponse(cmd);
            break;

        case 'update_synergy_card':
            this.updateSynergyCard(cmd);
            break;

        default:
            console.warn(`[UICommandProcessor] Unknown command: ${commandType}`);
    }
}
```

#### 3. `switchTab(cmd)`
Switches to specified tab (multi-agent, synergy, etc.)

```javascript
switchTab: function (cmd) {
    const tabName = cmd.tab_name;

    if (tabName === 'multi-agent') {
        // Find and click Multi-Agent tab button
        const multiAgentTab = document.querySelector(
            '[data-tab="multi-agent"], .tab-button[onclick*="multiAgent"]'
        );
        if (multiAgentTab) {
            multiAgentTab.click();  // ← Triggers switchTab() or ModuleManager.switchToModule()
            console.log('[UICommandProcessor] Switched to Multi-Agent tab');
        } else {
            console.warn('[UICommandProcessor] Multi-Agent tab not found');
        }
    } else if (tabName === 'synergy') {
        const synergyTab = document.querySelector('[data-tab="synergy"]');
        if (synergyTab) {
            synergyTab.click();
            console.log('[UICommandProcessor] Switched to Synergy tab');
        }
    }
    // ... other tab cases
}
```

#### 4. `openAgentColumn(cmd)`
Opens agent column and highlights it

```javascript
openAgentColumn: function (cmd) {
    const agentNum = cmd.agent_number;
    const agentName = cmd.agent_name;
    const shouldHighlight = cmd.highlight !== false;

    // Find agent column by number
    const agentColumn = document.querySelector(`#agent-${agentNum}-column`);

    if (agentColumn) {
        // Make column visible
        agentColumn.classList.remove('collapsed');
        agentColumn.classList.add('active');

        // Highlight if requested
        if (shouldHighlight) {
            agentColumn.classList.add('highlight-pulse');
            setTimeout(() => {
                agentColumn.classList.remove('highlight-pulse');
            }, 2000);
        }

        // Scroll into view
        agentColumn.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        console.log(`[UICommandProcessor] Opened agent column: ${agentName} (${agentNum})`);
    } else {
        console.warn(`[UICommandProcessor] Agent column ${agentNum} not found`);
    }
}
```

#### 5. `showThreadInfo(cmd)`
Displays thread info card with badges

```javascript
showThreadInfo: function (cmd) {
    const threadId = cmd.thread_id;
    const location = cmd.thread_location;
    const badges = cmd.badges || {};

    // Find thread card in agent column
    const agentNum = parseInt(location.split('-')[1]);
    const threadCard = document.querySelector(
        `#agent-${agentNum}-column [data-thread-id="${threadId}"]`
    );

    if (threadCard) {
        // Update badges display
        if (badges.workflow) {
            // Add workflow badge
        }
        if (badges.internal_doc) {
            // Add doc badge
        }
        if (badges.synergy) {
            // Add synergy badge
        }

        // Expand thread info
        threadCard.classList.add('expanded');

        console.log(`[UICommandProcessor] Showed thread info for ${threadId} in ${location}`);
    } else {
        console.warn(`[UICommandProcessor] Thread card not found for ${location}`);
    }
}
```

---

## Part 4: Available UI Commands

### Command Reference

| Command | Purpose | Parameters | Frontend Handler |
|---------|---------|------------|------------------|
| `switch_tab` | Switch to tab | `tab_name` | `UICommandProcessor.switchTab()` |
| `open_agent_column` | Open agent column | `agent_number`, `agent_name`, `highlight` | `UICommandProcessor.openAgentColumn()` |
| `show_thread_info` | Show thread details | `thread_id`, `thread_location`, `badges` | `UICommandProcessor.showThreadInfo()` |
| `trigger_agent_request` | Trigger AI processing | `thread_id`, `agent_location`, `message_id` | `UICommandProcessor.triggerAgentRequest()` |
| `send_cross_thread_request` | Cross-thread message | `target_thread_id`, `request_message`, `priority` | `UICommandProcessor.sendCrossThreadRequest()` |
| `receive_cross_thread_response` | Handle response | `request_id`, `response_message` | `UICommandProcessor.receiveCrossThreadResponse()` |
| `update_synergy_card` | Update synergy card | `thread_id`, `updates` | `UICommandProcessor.updateSynergyCard()` |

### Command Structure Examples

**1. Switch Tab:**
```json
{
  "command": "switch_tab",
  "tab_name": "multi-agent"
}
```

**2. Open Agent Column:**
```json
{
  "command": "open_agent_column",
  "agent_location": "agent-1",
  "agent_number": 1,
  "agent_name": "Alpha",
  "highlight": true
}
```

**3. Show Thread Info:**
```json
{
  "command": "show_thread_info",
  "thread_id": "abc-123",
  "thread_location": "agent-1",
  "badges": {
    "workflow": "React Build Process",
    "internal_doc": "Architecture Guide",
    "synergy": true
  }
}
```

---

## Part 5: Complete Example - User Request to UI Update

### User Says:
> "Assign the frontend work to Agent Alpha with the React workflow"

### AI Agent Thinks:
```
1. Need to assign work to an agent
2. Tool: assign_and_activate_agent_with_slugs
3. target_agent="Alpha"
4. thread_title="Frontend Development"
5. instructions="Build React frontend..."
6. slugs={ workflow_slug: "react-frontend" }
7. open_ui=true (get UI commands)
8. auto_trigger=false (don't start yet)
```

### AI Agent Calls Tool:
```python
assign_and_activate_agent_with_slugs(
    target_agent="Alpha",
    thread_title="Frontend Development",
    instructions="Build the React frontend for the e-commerce platform",
    slugs={
        "workflow_slug": "react-frontend",
        "workflow_title": "React Build Process"
    },
    open_ui=True,
    auto_trigger=False
)
```

### Backend Executes:
1. Parse "Alpha" → "agent-1"
2. Create thread in database (or update existing)
3. Link workflow_slug="react-frontend"
4. Insert user message with instructions
5. Generate UI commands array
6. Return result with ui_commands

### Backend Returns:
```json
{
  "success": true,
  "thread_id": "550e8400-e29b-41d4-a716-446655440000",
  "thread_location": "agent-1",
  "assigned_slugs": {
    "workflow_slug": "react-frontend",
    "workflow_title": "React Build Process"
  },
  "message_id": "msg-12345",
  "ui_commands": [
    {
      "command": "switch_tab",
      "tab_name": "multi-agent"
    },
    {
      "command": "open_agent_column",
      "agent_location": "agent-1",
      "agent_number": 1,
      "agent_name": "Alpha",
      "highlight": true
    },
    {
      "command": "show_thread_info",
      "thread_id": "550e8400-e29b-41d4-a716-446655440000",
      "thread_location": "agent-1",
      "badges": {
        "workflow": "React Build Process",
        "internal_doc": null,
        "synergy": false
      }
    }
  ]
}
```

### Frontend Receives Response:
```javascript
// Tool result received
const toolResult = {
  success: true,
  thread_id: "550e8400...",
  ui_commands: [ /* array of 3 commands */ ]
};

// UnifiedMessageRenderer displays tool result
// Shows clickable pill: "🎯 UI Commands (3)"
```

### User Clicks Pill OR Auto-Execute:
```javascript
// Extracts ui_commands from tool result
UICommandProcessor.executeCommands(toolResult.ui_commands);
```

### Frontend Executes Commands:
```javascript
// Command 1: switch_tab
UICommandProcessor.switchTab({command: "switch_tab", tab_name: "multi-agent"})
  → document.querySelector('[data-tab="multi-agent"]').click()
  → switchTab("multi-agent")
  → Tab switches to Multi-Agent view

// Command 2: open_agent_column
UICommandProcessor.openAgentColumn({
  command: "open_agent_column",
  agent_number: 1,
  agent_name: "Alpha",
  highlight: true
})
  → document.querySelector('#agent-1-column').classList.remove('collapsed')
  → Column opens and highlights
  → Scrolls into view

// Command 3: show_thread_info
UICommandProcessor.showThreadInfo({
  command: "show_thread_info",
  thread_id: "550e8400...",
  badges: {workflow: "React Build Process"}
})
  → Finds thread card in agent-1-column
  → Adds workflow badge
  → Expands thread details
```

### User Sees:
1. ✅ Tab switched to Multi-Agent dashboard
2. ✅ Agent Alpha's column is open and highlighted
3. ✅ Thread "Frontend Development" is visible
4. ✅ Workflow badge "React Build Process" is shown
5. ✅ Thread details are expanded

---

## Key Takeaways

1. **AI Agents Don't Touch the DOM**
   - They call backend tools
   - Tools return structured data with `ui_commands`
   - Frontend processes commands

2. **Separation of Concerns**
   - Backend: Business logic + data persistence
   - AI: Decision making + tool selection
   - Frontend: UI updates + user interaction

3. **Extensible Architecture**
   - Add new UI commands by:
     1. Adding backend command generation
     2. Adding frontend handler method
     3. Updating UICommandProcessor switch statement

4. **Debugging**
   - Backend: Check tool return value has `ui_commands`
   - Frontend: Check `[UICommandProcessor]` console logs
   - UI: Verify DOM elements exist with correct selectors

5. **Why This Works**
   - AI doesn't need to learn JavaScript/DOM
   - Backend controls what UI updates are allowed
   - Frontend ensures security and validation
   - User sees immediate visual feedback

---

## Related Files

- **System Prompt:** `AI_infrastructure/prompts/tool_usage_system_prompt.md`
- **Tool Schema:** `tools/schemas/advanced_agent_coordination_tools.json`
- **Backend Implementation:** `tools/implementations/advanced_agent_coordination.py`
- **Frontend Processor:** `UI/external/modules/ui-command-processor.js`
- **Message Renderer:** `UI/modules/shared/message_renderer.js` (displays UI command pills)

---

**Last Updated:** November 22, 2025  
**Status:** Production  
**Architecture:** Stable and extensible
