# 🎯 When to Use Which Platform - Quick Reference Guide

**Date:** October 28, 2025  
**Purpose:** Decision tree for syncing Kanban cards to Google/Microsoft platforms

---

## 🚦 Decision Flow Chart

```
┌─────────────────────────────────────────┐
│    User Creates/Updates Kanban Card    │
└──────────────┬──────────────────────────┘
               │
               ▼
        ┌──────────────┐
        │ Has Reminder? │
        └──────┬───────┘
               │
       ┌───────┴───────┐
       │ YES           │ NO
       ▼               ▼
┌─────────────┐  ┌─────────────┐
│ Has         │  │ Has         │
│ Recurrence? │  │ Recurrence? │
└──────┬──────┘  └──────┬──────┘
       │                │
   YES │ NO         YES │ NO
       │                │
       ▼                ▼
┌──────────────────────────────────────┐
│           SYNC STRATEGY              │
└──────────────────────────────────────┘
```

---

## 📋 Sync Strategy Matrix

| Scenario | Google Tasks | Microsoft To Do | Google Calendar | Why |
|----------|-------------|-----------------|-----------------|-----|
| **Simple task** | ✅ Sync | ✅ Sync | ❌ Skip | No special features needed |
| **Task with reminder** | ✅ Sync | ✅ Sync | ✅ **Create event** | Google Tasks has NO reminders |
| **Recurring task** | ⚠️ Single | ✅ Sync | ✅ **Create event** | Google Tasks has NO recurrence |
| **Recurring + reminder** | ⚠️ Single | ✅ Sync | ✅ **Create event** | Calendar handles both |
| **Task with checklist** | ✅ Subtasks | ✅ Native | ❌ Skip | Different implementations |
| **Task with priority** | ✅ Prefix | ✅ Native | ✅ Color | Different implementations |
| **Task with location** | ❌ Skip | ❌ Skip | ✅ Sync | Only Calendar supports |
| **Task with attendees** | ❌ Skip | ❌ Skip | ✅ Sync | Only Calendar supports |
| **All-day task** | ✅ Date | ✅ Sync | ✅ Sync | All support with variations |

---

## 🎯 Detailed Scenarios

### **Scenario 1: Simple Task (No Reminder, No Recurrence)**

```javascript
const kanbanCard = {
    title: "Review budget report",
    description: "Check Q4 expenses",
    due_date: "2025-10-31T17:00:00Z",
    priority: "medium",
    tags: ["finance", "q4"]
};
```

**Action:**
- ✅ Sync to **Google Tasks**
- ✅ Sync to **Microsoft To Do**
- ❌ Skip **Google Calendar**

**Result:**
```
Google Tasks: [MED] Review budget report (with notes)
Microsoft To Do: Review budget report (with categories)
Calendar: (not created)
```

---

### **Scenario 2: Task with Reminder (No Recurrence)**

```javascript
const kanbanCard = {
    title: "Submit expense report",
    due_date: "2025-10-31T17:00:00Z",
    reminder_date: "2025-10-31T09:00:00Z",  // 8 hours before
    reminder_minutes_before: 480
};
```

**Action:**
- ✅ Sync to **Google Tasks** (flagged with 🔔)
- ✅ Sync to **Microsoft To Do** (with native reminder)
- ✅ **Create Google Calendar event** for reminder

**Result:**
```
Google Tasks: [🔔 HAS REMINDER] Submit expense report
Microsoft To Do: Submit expense report (reminderDateTime: 09:00)
Calendar: ⏰ Reminder: Submit expense report (event at 09:00)
```

**Why:** Google Tasks can't send reminders, but Calendar can!

---

### **Scenario 3: Recurring Task (No Reminder)**

```javascript
const kanbanCard = {
    title: "Weekly team standup",
    recurrence_type: "weekly",
    recurrence_pattern: {
        interval: 1,
        daysOfWeek: ["monday", "wednesday", "friday"]
    },
    start_time: "09:00:00",
    duration_minutes: 15
};
```

**Action:**
- ⚠️ Create **single Google Task** (with recurrence note)
- ✅ Sync to **Microsoft To Do** (with native recurrence)
- ✅ **Create recurring Google Calendar event**

**Result:**
```
Google Tasks: [🔁 RECURRING] Weekly team standup (single task with note)
Microsoft To Do: Weekly team standup (recurring: Mon/Wed/Fri)
Calendar: Weekly team standup (RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR)
```

**Why:** Google Tasks can't do recurring tasks, but Calendar can!

---

### **Scenario 4: Recurring Task WITH Reminder**

```javascript
const kanbanCard = {
    title: "Daily scrum meeting",
    recurrence_type: "daily",
    recurrence_pattern: { interval: 1 },
    reminder_minutes_before: 15,
    start_time: "09:00:00",
    duration_minutes: 15
};
```

**Action:**
- ⚠️ Create **single Google Task** (flagged 🔁🔔)
- ✅ Sync to **Microsoft To Do** (recurring + reminder)
- ✅ **Create recurring Google Calendar event with reminder**

**Result:**
```
Google Tasks: [🔁🔔 RECURRING+REMINDER] Daily scrum (see Calendar)
Microsoft To Do: Daily scrum (recurring daily, reminder 15min before)
Calendar: Daily scrum (RRULE:FREQ=DAILY + reminder popup)
```

**Why:** Google Tasks can't do either, Calendar does both!

---

### **Scenario 5: Task with Checklist**

```javascript
const kanbanCard = {
    title: "Prepare presentation",
    checklist: [
        { item: "Create slides", completed: true },
        { item: "Add charts", completed: false },
        { item: "Rehearse", completed: false }
    ]
};
```

**Action:**
- ✅ Sync to **Google Tasks** (1 parent + 3 subtasks)
- ✅ Sync to **Microsoft To Do** (1 task with checklistItems)
- ❌ Skip **Google Calendar** (no checklist support)

**Result:**
```
Google Tasks:
  └─ Prepare presentation (parent)
      ├─ Create slides ✓ (subtask)
      ├─ Add charts (subtask)
      └─ Rehearse (subtask)

Microsoft To Do:
  Prepare presentation
    ☑ Create slides
    ☐ Add charts
    ☐ Rehearse

Calendar: (not created)
```

**Why:** Different implementations but same functionality!

---

### **Scenario 6: Task with Location & Attendees**

```javascript
const kanbanCard = {
    title: "Client meeting",
    due_date: "2025-10-31T14:00:00Z",
    duration_minutes: 60,
    location: "Conference Room A",
    attendees: ["client@company.com", "team@mycompany.com"],
    reminder_minutes_before: 30
};
```

**Action:**
- ⚠️ Sync to **Google Tasks** (no location/attendees support)
- ⚠️ Sync to **Microsoft To Do** (no location/attendees support)
- ✅ **Create Google Calendar event** (full meeting details)

**Result:**
```
Google Tasks: [🔔 HAS REMINDER] Client meeting
Microsoft To Do: Client meeting (with reminder)
Calendar: Client meeting @ Conference Room A (invites sent to attendees)
```

**Why:** Only Calendar supports meetings with location & attendees!

---

### **Scenario 7: All-Day Task**

```javascript
const kanbanCard = {
    title: "Team building event",
    due_date: "2025-11-15",  // No time = all day
    is_all_day: true
};
```

**Action:**
- ✅ Sync to **Google Tasks** (date only)
- ✅ Sync to **Microsoft To Do** (with isAllDay flag)
- ✅ Sync to **Google Calendar** (all-day event)

**Result:**
```
Google Tasks: Team building event (due: Nov 15)
Microsoft To Do: Team building event (all day: Nov 15)
Calendar: Team building event (all-day event on Nov 15)
```

**Why:** All platforms support all-day, just different formats!

---

## 🔑 Key Decision Rules

### **When to Create Google Calendar Event:**

✅ **ALWAYS create if:**
- `reminder_date` is set (Google Tasks can't send reminders)
- `recurrence_type` != 'none' (Google Tasks can't recur)
- `location` is set (only Calendar supports)
- `attendees` array has items (only Calendar supports)
- `duration_minutes` > 0 (for actual meetings)

❌ **Skip if:**
- Simple task with no special features
- Only checklist needed (Calendar doesn't help)
- Only tags/priority (Calendar doesn't add value)

### **When to Sync to Google Tasks:**

✅ **ALWAYS sync** - It's a task!

⚠️ **But flag it if:**
- Has reminder: Add 🔔 emoji in title
- Has recurrence: Add 🔁 emoji in title
- Has both: Add 🔁🔔 emoji in title

### **When to Sync to Microsoft To Do:**

✅ **ALWAYS sync** - It supports everything!

---

## 📊 Feature Support Summary

| Feature | Google Tasks | Microsoft To Do | Google Calendar | Kanban Field |
|---------|-------------|-----------------|-----------------|--------------|
| ✅ Basic task tracking | ✅ | ✅ | ⚠️ Use events | `title`, `description` |
| 🔔 Reminders | ❌ **NO** | ✅ Native | ✅ Multiple | `reminder_date` → **Use Calendar!** |
| 🔁 Recurrence | ❌ **NO** | ✅ Native | ✅ RRULE | `recurrence_type` → **Use Calendar!** |
| ⭐ Priority | ⚠️ Title prefix | ✅ Native | ⚠️ Color | `priority` |
| 🏷️ Tags | ⚠️ In notes | ✅ Categories | ⚠️ In description | `tags` |
| ✅ Checklist | ⚠️ Subtasks | ✅ Native | ❌ NO | `checklist` |
| 📍 Location | ❌ NO | ❌ NO | ✅ Native | `location` → **Use Calendar!** |
| 👥 Attendees | ❌ NO | ❌ NO | ✅ Native | `attendees` → **Use Calendar!** |

---

## 🚀 Implementation Code Pattern

```python
def sync_kanban_card_to_platforms(kanban_card):
    """Intelligently sync Kanban card to appropriate platforms"""
    
    # Always sync to Google Tasks
    google_task = sync_to_google_tasks(kanban_card)
    
    # Always sync to Microsoft To Do
    ms_task = sync_to_microsoft_todo(kanban_card)
    
    # Conditionally create Google Calendar event
    calendar_event = None
    should_create_calendar = (
        kanban_card.get('reminder_date') or
        kanban_card.get('recurrence_type') != 'none' or
        kanban_card.get('location') or
        kanban_card.get('attendees') or
        kanban_card.get('duration_minutes', 0) > 0
    )
    
    if should_create_calendar:
        calendar_event = sync_to_google_calendar(kanban_card)
    
    return {
        'google_task_id': google_task.id,
        'microsoft_todo_id': ms_task.id,
        'google_calendar_event_id': calendar_event.id if calendar_event else None
    }
```

---

## 💡 Pro Tips

1. **Always use Google Calendar for reminders** instead of relying on Google Tasks
2. **Microsoft To Do is the most feature-complete** task platform
3. **Google Calendar is the best for meetings** with location & attendees
4. **Kanban board should have ALL fields** from all three platforms
5. **Use emojis (🔔🔁) in Google Tasks** to flag special features

---

**Summary:** The universal Kanban board tracks EVERYTHING. When syncing:
- Google Tasks = basic task tracking
- Microsoft To Do = full-featured task management
- Google Calendar = reminders, recurrence, meetings, locations

Use all three together for complete coverage! 🎯
