# UI Control Instructions Missing from System Prompt - November 22, 2025

## 🚨 CRITICAL FINDING

The **system prompt does NOT contain instructions** for the advanced agent coordination tools that control the UI!

## What's Missing

### Tool Name:
`assign_and_activate_agent_with_slugs`

### What It Does:
- Assigns work to one of 26 agent threads (Alpha, Bravo, ..., Zulu)
- Links resources (workflows, docs, synergy sessions)
- Returns UI commands to switch tabs, open agent columns, show thread info
- Enables multi-agent project coordination

### Current Status:
❌ **NOT documented** in `AI_infrastructure/prompts/tool_usage_system_prompt.md`

## Evidence

### Search Results:
```
Searched for: "assign_and_activate"
Location: AI_infrastructure/prompts/**/*.md
Result: No matches found

Searched for: "ui_command|UI command|switch.*tab|open.*agent"
Location: AI_infrastructure/prompts/tool_usage_system_prompt.md
Result: No matches found

Searched for: "26 agents|NATO|Alpha.*Bravo|agent thread|multi.*agent"
Location: AI_infrastructure/prompts/tool_usage_system_prompt.md
Result: 1 match (generic mention of "AI AGENT")

Searched for: "advanced.*coordination|assign.*work|distribute.*tasks"
Location: AI_infrastructure/prompts/tool_usage_system_prompt.md
Result: No matches found
```

## What IS in the System Prompt

The system prompt DOES document:
- ✅ Synergy Dashboard (visual project tracking)
- ✅ Gmail/Outlook tools
- ✅ Google Docs/Sheets tools
- ✅ Microsoft Word/Excel tools
- ✅ User interaction tools
- ✅ Feedback area tools
- ✅ 646 tools total across 40 platforms

But it does NOT document:
- ❌ Multi-agent coordination tools
- ❌ UI control commands
- ❌ Agent assignment workflow
- ❌ Cross-thread communication
- ❌ 26 agent threads (NATO alphabet)
- ❌ How UI updates work

## How AI Currently Learns About These Tools

### Method 1: Tool Schema Only
The AI receives the tool schema from `tools/schemas/advanced_agent_coordination_tools.json` which includes:

```json
{
  "name": "assign_and_activate_agent_with_slugs",
  "description": "ALL-IN-ONE COMBO TOOL: Assign multiple resource slugs to an agent thread, send instructions, and optionally trigger agent activation with automatic UI updates. Creates new thread if agent is empty or updates existing thread. Returns UI commands for automatic tab switching, agent column opening, and thread info display. Use this to distribute work across agents with complete coordination.",
  "parameters": {...},
  "examples": [...]
}
```

### Method 2: Function Calling Discovery
When the AI receives the list of 646 tools, it sees:
- `assign_and_activate_agent_with_slugs`
- `request_update_from_thread`
- `respond_to_cross_thread_request`

But has NO context for:
- When to use them
- What multi-agent coordination means
- How the UI updates work
- Best practices for agent assignment

## Impact

### Current Behavior:
The AI CAN call these tools (they're in the tool list), but:
- ❌ No guidance on WHEN to use them
- ❌ No explanation of the 26-agent system
- ❌ No workflow examples
- ❌ No best practices
- ❌ No UI command explanation

### Expected Behavior:
The AI SHOULD have instructions like:

```markdown
## MULTI-AGENT COORDINATION (26 AI Agents)

You have access to 26 parallel AI agent threads:
- Alpha (agent-1) through Zulu (agent-26)
- Each can work independently on tasks
- Use for complex projects requiring parallel work

### When to Assign Work to Agents:

✅ Use when:
- User has a large project with multiple components
- Work can be parallelized (frontend + backend + database)
- Need to track multiple workstreams
- Want to link resources (workflows, docs) to specific agents

❌ Don't use when:
- Simple single-task requests
- User wants direct conversation
- No clear work distribution needed

### Tool: assign_and_activate_agent_with_slugs

Assigns work to an agent thread with automatic UI updates.

Example:
```python
assign_and_activate_agent_with_slugs(
    target_agent="Alpha",  # or "agent-1" or "1"
    thread_title="Frontend Development",
    instructions="Build React frontend for e-commerce site",
    slugs={
        "workflow_slug": "react-build-process",
        "internal_doc_slug": "react-architecture"
    },
    auto_trigger=False,  # Wait for user to trigger
    open_ui=True         # Return UI commands
)
```

Returns UI commands that automatically:
1. Switch to Multi-Agent tab
2. Open agent column (Alpha)
3. Show thread info with resource badges
4. (Optional) Trigger AI processing

### UI Commands Explained:

When open_ui=True, tool returns:
```json
{
  "ui_commands": [
    {"command": "switch_tab", "tab_name": "multi-agent"},
    {"command": "open_agent_column", "agent_number": 1},
    {"command": "show_thread_info", "thread_id": "..."}
  ]
}
```

Frontend automatically processes these to update the UI.
User sees immediate visual feedback without manual navigation.
```

## Comparison with Synergy Documentation

### What's in Prompt for Synergy:
The system prompt dedicates **~150 lines** to Synergy Dashboard including:
- What it is and why to use it
- When to use vs not use
- Complete workflow examples
- Visual layout diagrams
- Step-by-step instructions
- Tool discovery process
- Best practices

### What's in Prompt for Multi-Agent:
**0 lines** - Not mentioned at all

## Recommendation

### Option 1: Add to System Prompt (Recommended)
Add a new section to `tool_usage_system_prompt.md`:

```markdown
## MULTI-AGENT COORDINATION (26 AI AGENTS)

You have 26 parallel AI agent threads for complex project work:
- NATO Names: Alpha, Bravo, Charlie, ..., Zulu
- Locations: agent-1, agent-2, ..., agent-26
- Numbers: 1, 2, 3, ..., 26

[Include examples, workflows, best practices]
```

**Benefits:**
- AI has clear guidance on when/how to use
- Consistent with Synergy documentation style
- Reduces need for user to explain the system
- Enables proactive suggestions

**Drawback:**
- Adds ~150-200 lines to system prompt
- Increases tokens per request

### Option 2: Create Separate Instructions Document (Alternative)
Create `multi_agent_coordination_instructions.md` and use:

```python
synergy_agent_instructions(topic="multi_agent_overview")
```

**Benefits:**
- Keeps system prompt compact
- Only loads when needed
- Similar to Synergy's discovery pattern

**Drawback:**
- Requires AI to discover tool first
- Less proactive than built-in instructions

### Option 3: Hybrid Approach (Best?)
Add brief overview to system prompt + detailed instructions in separate file:

**In system prompt (~30 lines):**
```markdown
## MULTI-AGENT COORDINATION

You have 26 AI agent threads for parallel work.
Use assign_and_activate_agent_with_slugs to distribute tasks.

For detailed instructions:
synergy_agent_instructions(topic="multi_agent_overview")
```

**In separate file (full details):**
- Complete workflow examples
- UI command explanations
- Best practices
- Advanced patterns

## Files to Update

### If Adding to System Prompt:
1. `AI_infrastructure/prompts/tool_usage_system_prompt.md`
   - Add new section after Synergy Dashboard (~line 650)
   - Include examples and workflows
   - Explain UI command system

### If Creating Separate File:
1. Create: `AI_infrastructure/prompts/multi_agent_coordination.md`
2. Update: `tools/implementations/synergy_instructions.py`
   - Add "multi_agent_overview" topic
   - Add "multi_agent_workflows" topic
   - Add "ui_commands_guide" topic

## Current Workaround

Since these instructions are missing, AI agents currently:
1. See the tool in the tool list
2. Read the tool schema description
3. Infer usage from parameters and examples
4. Call the tool based on schema alone

This works, but:
- No guidance on WHEN to use (vs doing work directly)
- No explanation of the 26-agent system architecture
- No UI command system explanation
- No best practice patterns

## Next Steps

1. **Decide approach:** Option 1, 2, or 3 above
2. **Draft content:** Write multi-agent instructions
3. **Review:** Ensure consistency with existing style
4. **Test:** Verify AI uses tools appropriately
5. **Document:** Update relevant files

---

**Status:** Issue Identified  
**Priority:** Medium (tools work, but lack guidance)  
**Impact:** AI can call tools but may not use them optimally  
**Recommendation:** Add hybrid approach (brief prompt + detailed file)  

**Date Identified:** November 22, 2025  
**Reported By:** System Analysis
