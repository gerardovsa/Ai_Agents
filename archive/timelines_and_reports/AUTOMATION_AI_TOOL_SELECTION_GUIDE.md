# AI Agent Automation Tool Selection Guide 🤖

**Quick Reference:** How AI agents now choose the correct automation tool

---

## 🎯 The Decision Tree (What AI Sees)

This is now embedded in `tools/schemas/automation_tools.json` under `AI_AGENT_DECISION_TREE`:

```
┌─────────────────────────────────────────┐
│  User provides workflow slug (wf_xxx)?  │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
   YES                 NO
    │                   │
    ▼                   ▼
┌───────────────────────────────────────┐
│ What does user want to do?           │
├───────────────────────────────────────┤
│ "show me" / "open" / "display"        │
│   → automation_get_workflow_by_slug   │
│   → automation_open_workflow_in_canvas│
│                                       │
│ "update" / "add step" / "modify"      │
│   → automation_update_workflow ⭐ NEW │
│                                       │
│ "run" / "execute" / "test"            │
│   → automation_execute_workflow       │
│                                       │
│ "schedule" / "run daily" / "activate" │
│   → automation_schedule_workflow      │
│                                       │
│ "delete" / "remove" / "cancel"        │
│   → automation_delete_workflow        │
│                                       │
│ "status" / "history" / "last run"     │
│   → automation_get_workflow_status    │
└───────────────────────────────────────┘

┌───────────────────────────────────────┐
│ User wants to create or list?        │
├───────────────────────────────────────┤
│ Describes NEW workflow                │
│   → automation_create_workflow        │
│   → automation_open_workflow_in_canvas│
│                                       │
│ "show my workflows" / "list"          │
│   → automation_list_workflows         │
└───────────────────────────────────────┘
```

---

## 📝 User Intent → AI Action Mapping

### ✅ User Provides Slug (wf_xxx)

| User Says | AI Uses This Tool | Then Does This |
|-----------|------------------|----------------|
| "show me wf_xxx" | `automation_get_workflow_by_slug(slug)` | `automation_open_workflow_in_canvas(slug)` |
| "add email step to wf_xxx" | `automation_update_workflow(slug, add_actions=[...])` | Auto-refresh UI |
| "remove first action from wf_xxx" | `automation_update_workflow(slug, remove_actions=[0])` | Auto-refresh UI |
| "change schedule to daily" | `automation_update_workflow(slug, update_trigger=...)` | Auto-refresh UI |
| "run wf_xxx" | `automation_execute_workflow(slug)` | Report results |
| "schedule wf_xxx for 9am daily" | `automation_schedule_workflow(slug, cron='0 9 * * *')` | Confirm schedule |
| "delete wf_xxx" | `automation_delete_workflow(slug)` | Confirm deletion |
| "show status of wf_xxx" | `automation_get_workflow_status(slug)` | Display stats |

### ❌ User Does NOT Provide Slug

| User Says | AI Uses This Tool | Then Does This |
|-----------|------------------|----------------|
| "create workflow that emails me daily" | `automation_create_workflow(title, trigger, actions)` | `automation_open_workflow_in_canvas(new_slug)` |
| "show my workflows" | `automation_list_workflows()` | Display list with slugs |
| "list email automations" | `automation_list_workflows(category='email')` | Display filtered list |

---

## 🔥 The NEW Update Tool - automation_update_workflow

### When AI Uses This
- User says: "add", "remove", "update", "modify", "change", "edit" + workflow slug
- User provides slug (wf_xxx) AND wants to change something

### What It Can Do

#### 1️⃣ Add Actions
```python
automation_update_workflow(
    slug='wf_abc123_1732029847',
    add_actions=[{
        'tool': 'gmail_send_email',
        'parameters': {'to': 'user@example.com', 'subject': 'Done'},
        'position': 3  # Optional: insert at position 3
    }]
)
```

**User says:** "add an email notification to wf_abc123"  
**AI responds:** "Added gmail_send_email action to your workflow. UI has auto-refreshed to show the new step."

---

#### 2️⃣ Remove Actions
```python
automation_update_workflow(
    slug='wf_abc123_1732029847',
    remove_actions=[0, 2]  # Remove actions at positions 0 and 2
)
```

**User says:** "remove the first step from wf_abc123"  
**AI responds:** "Removed action at position 0. Your workflow now has 4 actions. UI has refreshed."

---

#### 3️⃣ Update Trigger
```python
automation_update_workflow(
    slug='wf_abc123_1732029847',
    update_trigger={'type': 'schedule', 'schedule_cron': '0 */2 * * *'}
)
```

**User says:** "change wf_abc123 to run every 2 hours"  
**AI responds:** "Updated trigger to schedule (0 */2 * * *). Next run: in 1h 23m."

---

#### 4️⃣ Update Action Parameters
```python
automation_update_workflow(
    slug='wf_abc123_1732029847',
    update_action_parameters={
        'position': 1,
        'parameters': {'max_results': 50}
    }
)
```

**User says:** "change the max results to 50 in step 2"  
**AI responds:** "Updated action 1 parameters: max_results changed from 20 to 50."

---

#### 5️⃣ Update Metadata
```python
automation_update_workflow(
    slug='wf_abc123_1732029847',
    update_metadata={'title': 'Updated Title', 'description': 'New description'}
)
```

**User says:** "rename wf_abc123 to 'Daily Report Generator'"  
**AI responds:** "Updated workflow title to 'Daily Report Generator'."

---

## 🎭 Real Conversation Examples

### Example 1: User Frustration (Your Original Issue) ✅ SOLVED

**Before (Broken):**
```
User: "use this slug wf_ypsqcqyz_1763565706 and add an email step"
AI: "I can open it in the canvas for you to edit manually..."
User: "NO! The AI doesn't know which tool to use!" 😡
```

**After (Working):**
```
User: "use this slug wf_ypsqcqyz_1763565706 and add an email step"
AI: [Calls automation_update_workflow(slug='wf_ypsqcqyz_1763565706', add_actions=[...])]
AI: "Added gmail_send_email action to your workflow at position 5. The UI canvas has 
     automatically refreshed to show the new action. Next time this workflow runs, 
     it will send you an email when complete." ✅
```

---

### Example 2: Creating vs. Updating

**User provides slug → UPDATE:**
```
User: "add slack notification to wf_abc123_1732029847"
AI: Uses automation_update_workflow(slug='wf_abc123_1732029847', add_actions=[...])
```

**User does NOT provide slug → CREATE:**
```
User: "create a workflow that sends me slack notifications daily"
AI: Uses automation_create_workflow(title='Daily Slack Notifications', ...)
AI: Then uses automation_open_workflow_in_canvas(slug=<new_slug>)
```

---

### Example 3: Complex Multi-Step Update

**User:** "update wf_abc123: remove the first two steps, add email notification, and change schedule to every 2 hours"

**AI Action:**
```python
automation_update_workflow(
    slug='wf_abc123_1732029847',
    remove_actions=[0, 1],
    add_actions=[{
        'tool': 'gmail_send_email',
        'parameters': {'to': 'user@example.com', 'subject': 'Updated Workflow'}
    }],
    update_trigger={'type': 'schedule', 'schedule_cron': '0 */2 * * *'}
)
```

**AI Response:**
> "Updated your workflow with 3 changes:
> 1. Removed actions at positions 0 and 1
> 2. Added gmail_send_email action to end
> 3. Changed trigger to schedule (every 2 hours)
> 
> Your workflow now has 5 actions instead of 6. UI has automatically refreshed."

---

## 🚨 Error Handling

### Invalid Slug
```
User: "update workflow abc123"
AI: ❌ "Invalid slug format: abc123 (must start with 'wf_')"
```

### Workflow Not Found
```
User: "add step to wf_nonexistent_123"
AI: ❌ "Workflow not found: wf_nonexistent_123"
```

### Invalid Position
```
User: "remove step 10 from wf_abc123"
AI: ❌ "Cannot remove position 10 (workflow only has 5 actions)"
```

### Invalid Tool Name
```
User: "add tool xyz_invalid to wf_abc123"
AI: ❌ "Tool xyz_invalid not found in 594-tool library"
```

---

## 📊 Before vs. After Comparison

### Before (The Problem)
```
Available Tools:
  ✅ automation_create_workflow
  ✅ automation_get_workflow
  ✅ automation_execute_workflow
  ✅ automation_schedule_workflow
  ✅ automation_delete_workflow
  ❌ NO UPDATE TOOL

AI Behavior:
  - User provides slug + wants to modify
  - AI doesn't know what to do
  - AI suggests opening in UI for manual editing
  - User frustrated: "AI doesn't know which tool!"
```

### After (The Solution)
```
Available Tools:
  ✅ automation_create_workflow
  ✅ automation_update_workflow ⭐ NEW
  ✅ automation_get_workflow
  ✅ automation_execute_workflow
  ✅ automation_schedule_workflow
  ✅ automation_delete_workflow

AI Behavior:
  - User provides slug + wants to modify
  - AI checks decision tree in automation_tools.json
  - AI sees "modify" keywords → uses automation_update_workflow
  - Workflow updated programmatically
  - UI auto-refreshes with new visual flow
  - User happy: "Perfect! That's what I wanted!" ✅
```

---

## 🧠 How AI Agents Learn This

### Schema Location
**File:** `tools/schemas/automation_tools.json`

### What AI Sees (Top of File)
```json
{
  "platform": "automation",
  "platform_guide": {
    "AI_AGENT_DECISION_TREE": {
      "CRITICAL_INSTRUCTIONS": "READ THIS FIRST - Use this decision tree...",
      "decision_flow": {
        "STEP_1_CHECK_FOR_SLUG": {...},
        "STEP_2_DETERMINE_ACTION_WITH_SLUG": {
          "MODIFY_IT": {
            "user_says": ["update", "change", "modify", "add action", "remove step", "edit", "fix"],
            "use_tool": "automation_update_workflow",
            "note": "After update completes, UI will auto-refresh canvas"
          }
        }
      }
    }
  }
}
```

### Tool Description (What AI Reads)
The `automation_update_workflow` tool has a **150+ line description** including:
- ✅ WHEN TO USE THIS TOOL (trigger keywords)
- ✅ 5 UPDATE OPERATIONS with examples
- ✅ EXAMPLE REQUESTS (user says X → AI calls Y)
- ✅ RESPONSE TO USER (what to tell user after update)
- ✅ AUTO-REFRESH UI (explain UI updates automatically)
- ✅ ERROR HANDLING (what to do when things fail)

---

## 🎉 Success Metrics

### User Satisfaction
- **Before:** Frustrated, confused, manual editing required
- **After:** AI handles updates programmatically, UI auto-refreshes

### Tool Usage
- **Before:** ~600 tools available, UPDATE missing
- **After:** ~600 tools + automation_update_workflow = Full CRUD

### AI Agent Performance
- **Before:** "I don't know which tool to use..." → suggests manual editing
- **After:** Clear decision tree → confidently calls correct tool → updates workflow

---

## 📚 Related Files

- `tools/schemas/automation_tools.json` - AI decision tree + tool schemas
- `tools/implementations/automation.py` - Python wrapper implementation
- `AI_infrastructure/routes/automation_routes.py` - Flask API endpoint
- `AUTOMATION_UPDATE_TOOL_COMPLETE.md` - Full implementation guide
- `.github/copilot-instructions.md` - Should be updated with this feature

---

**🚀 READY TO USE:** Restart Flask server (`BISTART`) and test with your workflow slug `wf_ypsqcqyz_1763565706`!
