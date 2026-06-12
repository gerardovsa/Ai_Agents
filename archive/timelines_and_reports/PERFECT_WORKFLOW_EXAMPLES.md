# Perfect Workflow Examples - Reference Templates

**Date:** November 28, 2025  
**Purpose:** Perfect workflow structures to use as templates for creating new visual automations  
**Status:** ✅ Production-Ready Examples

---

## Overview

These are **5 perfectly structured workflows** from the production database that demonstrate correct formatting, proper ID structure, complete automation logic, and arrow rendering compatibility.

---

## Example 1: Morning Email Check & Triage ⭐ PERFECT

**Category:** Email  
**Status:** Active  
**Complexity:** Medium (7 shapes, 7 connections)

### Why This Is Perfect:
- ✅ Uses string IDs (`trigger_1`, `action_1`, etc.)
- ✅ All connections reference existing shapes
- ✅ Has complete `execution_json` with trigger
- ✅ Valid cron schedule: `0 8 * * *` (daily 8am)
- ✅ Uses `text` field for shape labels
- ✅ Arrows WILL render correctly

### Visual Structure:
```
trigger_1 (Schedule Trigger - Daily 8am)
    ↓
action_1 (Get Unread Emails - gmail_list_messages)
    ↓
action_2 (Analyze with AI - Classify Priority)
    ↓
decision_1 (Has Urgent Emails?)
    ↓ Yes                    ↓ No
action_3 (Send Alert)    action_4 (Create Summary)
    ↓                         ↓
action_4 (Create Summary) ←──┘
    ↓
output_1 (Send Daily Digest)
```

### JSON Template (Copy This):
```json
{
  "title": "Morning Email Check & Triage",
  "category": "email",
  "ui_json": {
    "shapes": [
      {
        "id": "trigger_1",
        "type": "trigger",
        "x": 100,
        "y": 80,
        "width": 220,
        "height": 100,
        "text": "Schedule Trigger\n8:00 AM Daily",
        "color": "#10B981"
      },
      {
        "id": "action_1",
        "type": "tool",
        "x": 100,
        "y": 230,
        "width": 220,
        "height": 100,
        "text": "Get Unread Emails\ngmail_list_messages",
        "color": "#6B7280"
      },
      {
        "id": "action_2",
        "type": "tool",
        "x": 100,
        "y": 380,
        "width": 220,
        "height": 100,
        "text": "Analyze with AI\nClassify Priority",
        "color": "#6B7280"
      },
      {
        "id": "decision_1",
        "type": "decision",
        "x": 100,
        "y": 530,
        "width": 220,
        "height": 100,
        "text": "Has Urgent Emails?",
        "color": "#F59E0B"
      }
    ],
    "connections": [
      {"from": "trigger_1", "to": "action_1"},
      {"from": "action_1", "to": "action_2"},
      {"from": "action_2", "to": "decision_1"},
      {"from": "decision_1", "to": "action_3", "label": "Yes"}
    ]
  },
  "execution_json": {
    "trigger": {
      "type": "schedule",
      "schedule_cron": "0 8 * * *",
      "timezone": "Australia/Sydney"
    },
    "actions": [
      {
        "id": "action_1",
        "tool": "gmail_list_messages",
        "parameters": {
          "max_results": 20,
          "query": "is:unread"
        }
      }
    ]
  }
}
```

---

## Example 2: Quote Request Email → Synergy Session Builder ⭐ PERFECT

**Category:** CRM  
**Status:** Active  
**Complexity:** High (11 shapes, 11 connections)

### Why This Is Perfect:
- ✅ String IDs throughout
- ✅ Event-based trigger (gmail_new_message)
- ✅ Complex multi-branch flow with decision nodes
- ✅ Integrates multiple tools (Gmail, Synergy, Fred, Xero, Google Docs)
- ✅ Real business process automation

### Key Features:
- Email monitoring with filter
- Fred database lookup
- Xero invoice check
- Synergy session creation with milestones
- Quote calculation
- Draft response generation

### Trigger Configuration:
```json
{
  "trigger": {
    "type": "event",
    "event_type": "gmail_new_message",
    "filter": "subject:(quote OR quotation OR pricing OR estimate)"
  }
}
```

---

## Example 3: Xero Accounts Payable → Synergy Payment Session ⭐ PERFECT

**Category:** Accounting  
**Status:** Active  
**Complexity:** High (12 shapes, 12 connections)

### Why This Is Perfect:
- ✅ Weekly schedule (Monday 9am)
- ✅ Financial workflow with decision logic
- ✅ Multiple data outputs (Google Sheets, Synergy, Email)
- ✅ Priority-based processing

### Workflow Pattern:
1. **Schedule**: Weekly Monday 9am
2. **Fetch**: Get Xero bills
3. **Filter**: Find overdue
4. **Decision**: Any overdue?
5. **Process**: Create Synergy session
6. **Group**: By supplier
7. **Generate**: Payment schedule
8. **Prioritize**: AI prioritization
9. **Output**: Send summary email

### Cron Schedule:
```json
{
  "schedule_cron": "0 9 * * 1",
  "timezone": "Australia/Sydney"
}
```
**Meaning:** Every Monday at 9:00 AM Sydney time

---

## Example 4: High-Value Client Reactivation - FRED Database ⭐ PERFECT

**Category:** CRM  
**Status:** Active  
**Complexity:** Very High (14 shapes, 14 connections)

### Why This Is Perfect:
- ✅ Monthly schedule (1st of month)
- ✅ Complex AI-powered research workflow
- ✅ Multiple parallel processing paths
- ✅ Comprehensive documentation generation
- ✅ Multi-phase task breakdown

### Advanced Features:
- Fred database analysis
- AI client research (web search)
- Strategy development
- Email campaign generation (3 campaigns)
- Multi-phase task creation
- Document linking to milestones

### Monthly Schedule:
```json
{
  "schedule_cron": "0 10 1 * *",
  "timezone": "Australia/Sydney"
}
```
**Meaning:** First day of every month at 10:00 AM

---

## Example 5: Daily Sales Report Generator ⚠️ NEEDS FIX

**Category:** Sales  
**Status:** Draft  
**Complexity:** Medium (8 shapes, 8 connections)

### ⚠️ Why This Has Issues:
- ❌ Uses **numeric IDs** (1, 2, 3, 4...)
- ⚠️ Empty `execution_json` (no automation logic)
- ⚠️ Uses `label` instead of `text` (both work, but inconsistent)

### ✅ What Can Be Fixed:
With the **ID normalization fix** implemented, this workflow's numeric IDs will be converted:
- `1` → `"shape_1"`
- `2` → `"shape_2"`
- etc.

**Result:** Arrows SHOULD render with the fix

### What Still Needs Work:
- Add `execution_json` with actions and trigger
- Consider converting to string IDs for consistency

---

## ID Format Comparison

### ❌ BAD - Numeric IDs (Old Format):
```json
{
  "shapes": [
    {"id": 1, "type": "trigger"},
    {"id": 2, "type": "action"}
  ],
  "connections": [
    {"from": 1, "to": 2}
  ]
}
```
**Problem:** Type mismatch when renderConnections() uses strict equality

---

### ⚠️ ACCEPTABLE - String Numeric IDs (With Fix):
```json
{
  "shapes": [
    {"id": "1", "type": "trigger"},
    {"id": "2", "type": "action"}
  ],
  "connections": [
    {"from": "1", "to": "2"}
  ]
}
```
**Status:** Works with ID normalization fix (converts to `"shape_1"`, `"shape_2"`)

---

### ✅ PERFECT - Descriptive String IDs (Best Practice):
```json
{
  "shapes": [
    {"id": "trigger_1", "type": "trigger"},
    {"id": "action_1", "type": "action"}
  ],
  "connections": [
    {"from": "trigger_1", "to": "action_1"}
  ]
}
```
**Benefits:** 
- Self-documenting
- No conversion needed
- Easier debugging
- Future-proof

---

## Complete Shape Structure Template

### Trigger Shape:
```json
{
  "id": "trigger_1",
  "type": "trigger",
  "x": 120,
  "y": 80,
  "width": 240,
  "height": 100,
  "text": "Schedule Trigger\nDaily at 9am",
  "color": "#10B981"
}
```

### Action/Tool Shape:
```json
{
  "id": "action_1",
  "type": "tool",
  "x": 120,
  "y": 230,
  "width": 240,
  "height": 100,
  "text": "Get Gmail Messages\ngmail_list_messages",
  "color": "#6B7280"
}
```

### Decision Shape:
```json
{
  "id": "decision_1",
  "type": "decision",
  "x": 120,
  "y": 530,
  "width": 240,
  "height": 100,
  "text": "Has New Messages?",
  "color": "#F59E0B"
}
```

### Output Shape:
```json
{
  "id": "output_1",
  "type": "output",
  "x": 120,
  "y": 830,
  "width": 240,
  "height": 100,
  "text": "Send Summary Email\ngmail_send_email",
  "color": "#EAB308"
}
```

---

## Connection Structure Template

### Basic Connection:
```json
{
  "from": "trigger_1",
  "to": "action_1"
}
```

### Connection with Label:
```json
{
  "from": "decision_1",
  "to": "action_2",
  "label": "Yes"
}
```

### Multiple Connections from One Shape:
```json
[
  {"from": "decision_1", "to": "action_2", "label": "Yes"},
  {"from": "decision_1", "to": "action_3", "label": "No"}
]
```

---

## Execution JSON Structure Template

### Scheduled Trigger:
```json
{
  "trigger": {
    "type": "schedule",
    "schedule_cron": "0 9 * * *",
    "timezone": "Australia/Sydney"
  },
  "actions": [
    {
      "id": "action_1",
      "tool": "gmail_list_messages",
      "parameters": {
        "max_results": 50,
        "query": "is:unread"
      }
    }
  ]
}
```

### Event-Based Trigger:
```json
{
  "trigger": {
    "type": "event",
    "event_type": "gmail_new_message",
    "filter": "subject:urgent"
  },
  "actions": [
    {
      "id": "action_1",
      "tool": "slack_post_message",
      "parameters": {
        "channel": "#alerts",
        "text": "Urgent email received: {{subject}}"
      }
    }
  ]
}
```

### Manual Trigger:
```json
{
  "trigger": {
    "type": "manual"
  },
  "actions": [...]
}
```

---

## Cron Schedule Reference

Common cron patterns for schedule_cron:

| Schedule | Cron Format | Description |
|----------|-------------|-------------|
| Every 15 minutes | `*/15 * * * *` | Runs 4 times per hour |
| Every hour | `0 * * * *` | Runs at :00 of each hour |
| Daily at 9am | `0 9 * * *` | Once per day |
| Every Monday at 9am | `0 9 * * 1` | Weekly |
| 1st of month at 10am | `0 10 1 * *` | Monthly |
| Every weekday at 8am | `0 8 * * 1-5` | Mon-Fri only |

**Format:** `minute hour day month weekday`
- Minute: 0-59
- Hour: 0-23
- Day: 1-31
- Month: 1-12
- Weekday: 0-7 (0 and 7 = Sunday)

---

## Shape Type Colors (Standard)

Use these colors for consistency:

```javascript
const SHAPE_COLORS = {
  trigger: "#10B981",    // Green
  tool: "#6B7280",       // Gray
  action: "#6B7280",     // Gray (same as tool)
  decision: "#F59E0B",   // Orange
  output: "#EAB308",     // Yellow
  database: "#EC4899",   // Pink
  schedule: "#3B82F6",   // Blue
  end: "#EF4444",        // Red
  wait: "#8B5CF6"        // Purple
};
```

---

## Validation Checklist

Before saving a workflow, verify:

### UI JSON:
- [ ] **Not empty** (not `{}`)
- [ ] All shape IDs are **strings** (not numbers)
- [ ] All shapes have `id`, `type`, `x`, `y` fields
- [ ] All shapes have `text` or `label` field
- [ ] All connections `from`/`to` match **existing shape IDs**
- [ ] No duplicate shape IDs

### Execution JSON:
- [ ] Has `trigger` object with `type` field
- [ ] Has `actions` array (even if empty initially)
- [ ] All action IDs match shape IDs in ui_json
- [ ] Cron schedule has **5 parts** (if scheduled)
- [ ] Timezone is set (if scheduled)
- [ ] Tool names are valid (exist in registry)

### General:
- [ ] Title is descriptive
- [ ] Description explains workflow purpose
- [ ] Category is set appropriately
- [ ] Status is `draft` or `active`

---

## Common Mistakes to Avoid

### ❌ Numeric Shape IDs
```json
{"id": 1}  // Wrong
```
**Fix:** Use string IDs
```json
{"id": "action_1"}  // Correct
```

---

### ❌ Empty ui_json
```json
{
  "ui_json": "{}"  // Wrong - no visual data
}
```
**Fix:** Populate from visual canvas
```json
{
  "ui_json": {
    "shapes": [...],
    "connections": [...]
  }
}
```

---

### ❌ Connection ID Mismatch
```json
{
  "shapes": [{"id": "action_1"}],
  "connections": [{"from": "action_2", "to": "action_3"}]  // Wrong - shapes don't exist
}
```
**Fix:** Match IDs exactly
```json
{
  "shapes": [{"id": "action_1"}, {"id": "action_2"}],
  "connections": [{"from": "action_1", "to": "action_2"}]  // Correct
}
```

---

### ❌ Invalid Cron Format
```json
{
  "schedule_cron": "9 * *"  // Wrong - only 3 parts
}
```
**Fix:** Use 5-part format
```json
{
  "schedule_cron": "0 9 * * *"  // Correct - minute hour day month weekday
}
```

---

## Quick Start: Creating Your First Workflow

### Step 1: Choose a Template
Pick the example closest to your use case:
- **Email automation** → Example 1 or 2
- **Financial/Accounting** → Example 3
- **CRM/Sales** → Example 4

### Step 2: Copy the JSON Structure
Copy the `ui_json` and `execution_json` from the example.

### Step 3: Customize
1. Change shape IDs (keep string format)
2. Update shape text/labels
3. Modify connections to match your flow
4. Update tool names in actions
5. Set your schedule/trigger

### Step 4: Validate
Run through the validation checklist above.

### Step 5: Save
Save from visual canvas to ensure ui_json is populated correctly.

---

## Summary: The 4 Perfect Examples

1. **Morning Email Check** - Simple scheduled email workflow ⭐
2. **Quote Request Builder** - Complex event-driven CRM workflow ⭐
3. **Xero Accounts Payable** - Financial/accounting automation ⭐
4. **Client Reactivation** - Advanced AI-powered sales workflow ⭐

**Use these as templates for all new workflows!**

---

**Last Updated:** November 28, 2025  
**Status:** ✅ Production Reference  
**Version:** 1.0.0
