# 🎯 Platform Feature Comparison & Universal Mapping Strategy

**Date:** October 28, 2025  
**Purpose:** Complete comparison of Google Tasks, Microsoft To Do, and Google Calendar features  
**Status:** ✅ Comprehensive Analysis

---

## 📊 Feature Availability Matrix

| Feature | Google Tasks | Microsoft To Do | Google Calendar | Universal Kanban Field |
|---------|-------------|-----------------|-----------------|----------------------|
| **✅ CORE FEATURES (All Support)** |
| Task Title | ✅ `title` | ✅ `title` | ✅ `summary` | `title` |
| Description/Notes | ✅ `notes` | ✅ `body.content` | ✅ `description` | `description` |
| Due Date | ✅ `due` | ✅ `dueDateTime` | ✅ `start`/`end` | `due_date` |
| Status/Completion | ✅ `status` | ✅ `status` | ✅ Implied | `status` |
| Created Date | ✅ `created` | ✅ `createdDateTime` | ✅ `created` | `created_at` |
| Updated Date | ✅ `updated` | ✅ `lastModifiedDateTime` | ✅ `updated` | `updated_at` |
| **🔔 REMINDERS & NOTIFICATIONS** |
| Reminders | ❌ **NO** | ✅ `reminderDateTime` | ✅ `reminders` array | `reminder_date` → **Use Calendar!** |
| Reminder Minutes Before | ❌ NO | ✅ Via `reminderDateTime` | ✅ `reminders.overrides` | `reminder_minutes` |
| Multiple Reminders | ❌ NO | ❌ Single only | ✅ Multiple | `reminders` (array) |
| **🔁 RECURRENCE & REPEATING** |
| Recurring Tasks | ❌ **NO** | ✅ `recurrence` | ✅ `recurrence` (RRULE) | `recurrence_pattern` |
| Daily/Weekly/Monthly | ❌ NO | ✅ Pattern object | ✅ RRULE format | `recurrence_type` |
| Custom Recurrence | ❌ NO | ✅ Advanced patterns | ✅ Full RRULE | `recurrence_rule` |
| **⭐ PRIORITY & IMPORTANCE** |
| Priority/Importance | ❌ NO (custom) | ✅ `importance` (low/normal/high) | ❌ NO (use colors) | `priority` |
| Color Coding | ❌ NO | ❌ NO | ✅ `colorId` | `color` |
| **📋 ORGANIZATION** |
| Task Lists | ✅ `taskList` | ✅ `list` | ✅ Multiple calendars | `list_id` / `project_name` |
| Categories/Tags | ❌ NO | ✅ `categories` array | ❌ NO | `tags` |
| Parent/Subtasks | ✅ `parent` field | ❌ NO (only checklist) | ❌ NO | `parent_id` / `checklist` |
| Checklist Items | ❌ NO (use subtasks) | ✅ `checklistItems` | ❌ NO | `checklist` |
| **👥 COLLABORATION** |
| Assignees | ❌ NO (personal) | ❌ NO (personal) | ✅ `attendees` | `assignees` |
| Sharing | ❌ Share list only | ❌ Share list only | ✅ Per-event | `shared_with` |
| **📎 ATTACHMENTS & LINKS** |
| Attachments | ❌ NO | ✅ `attachments` | ✅ `attachments` | `attachments` |
| Links | ✅ In notes | ✅ `linkedResources` | ✅ In description | `links` |
| **🕐 TIME MANAGEMENT** |
| All-Day Events | ❌ Only date | ✅ Via `isAllDay` | ✅ Date without time | `is_all_day` |
| Time Zones | ❌ UTC only | ✅ `timeZone` | ✅ Per-event timezone | `timezone` |
| Duration | ❌ NO | ❌ NO | ✅ `start` + `end` | `duration` |
| **📍 LOCATION** |
| Location Field | ❌ NO | ❌ NO | ✅ `location` | `location` |
| **🔄 SMART FEATURES** |
| My Day / Today View | ❌ NO | ✅ `isAddedToMyDay` | ✅ Today filter | `show_in_today` |
| Suggested Tasks | ❌ NO | ✅ AI suggestions | ❌ NO | N/A |

---

## 🔑 Key Insights

### **1. Google Tasks Limitations**
❌ **NO Reminders** - Must use Google Calendar for reminders  
❌ **NO Recurrence** - Must use Google Calendar for recurring  
❌ **NO Priority Field** - Must encode in title prefix  
❌ **NO Categories/Tags** - Must encode in notes  
❌ **NO Native Checklist** - Must create subtasks  

**Workaround:** For tasks that need reminders/recurrence, **also create a Google Calendar event!**

### **2. Microsoft To Do Advantages**
✅ **Native Reminders** - `reminderDateTime` field  
✅ **Native Recurrence** - Full recurrence patterns  
✅ **Native Priority** - `importance` field (low/normal/high)  
✅ **Native Categories** - `categories` array  
✅ **Native Checklist** - `checklistItems` array  
✅ **My Day** - Special "focus" feature  

**Result:** Microsoft To Do is more feature-complete for task management!

### **3. Google Calendar as Reminder System**
✅ **Multiple Reminders** - Can have email + popup  
✅ **Flexible Timing** - Minutes/hours/days before  
✅ **Recurring Events** - Full RRULE support  
✅ **Attendees** - Can notify others  
✅ **Location** - Can add meeting location  

**Strategy:** Use Google Calendar for tasks with reminders + Google Tasks for the task list!

---

## 🎯 Universal Kanban Field Strategy

### **Complete Universal Schema**

```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    
    -- ✅ CORE FIELDS (All 3 platforms)
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',
    due_date TEXT,  -- ISO 8601
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    
    -- ✅ PRIORITY (Google: title prefix, Microsoft: importance, Calendar: colorId)
    priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high')),
    
    -- ✅ ORGANIZATION
    kanban_column TEXT DEFAULT 'backlog',
    project_name TEXT,
    tags TEXT DEFAULT '[]',           -- Microsoft To Do categories
    
    -- ✅ REMINDERS (Microsoft + Calendar only)
    reminder_date TEXT,               -- Single reminder datetime
    reminder_minutes_before INTEGER,  -- E.g., 15, 30, 60
    reminders TEXT DEFAULT '[]',      -- Multiple reminders: [{"method": "email", "minutes": 15}]
    
    -- ✅ RECURRENCE (Microsoft + Calendar only)
    recurrence_type TEXT CHECK(recurrence_type IN ('none', 'daily', 'weekly', 'monthly', 'yearly', 'custom')),
    recurrence_pattern TEXT,          -- JSON: {"interval": 1, "daysOfWeek": ["monday", "friday"]}
    recurrence_rule TEXT,             -- RRULE format for Google Calendar
    
    -- ✅ CHECKLISTS & SUBTASKS
    checklist TEXT DEFAULT '[]',      -- Microsoft native, Google as subtasks
    parent_task_id TEXT,              -- Google Tasks subtask hierarchy
    
    -- ✅ COLLABORATION (Calendar only)
    assignees TEXT DEFAULT '[]',      -- Store even if not supported by Tasks/To Do
    attendees TEXT DEFAULT '[]',      -- For Calendar events
    location TEXT,                    -- For Calendar events
    
    -- ✅ TIME MANAGEMENT
    is_all_day BOOLEAN DEFAULT 0,
    timezone TEXT DEFAULT 'UTC',
    duration_minutes INTEGER,         -- For Calendar events
    
    -- ✅ VISUAL
    color TEXT,                       -- Map to Calendar colorId
    
    -- ✅ MICROSOFT-SPECIFIC
    is_added_to_my_day BOOLEAN DEFAULT 0,
    
    -- ✅ ATTACHMENTS
    attachments TEXT DEFAULT '[]',    -- Microsoft + Calendar
    links TEXT DEFAULT '[]',
    documents TEXT DEFAULT '[]',
    
    -- ✅ OTHER
    notes TEXT,
    assignees_list TEXT DEFAULT '[]',
    next_steps TEXT DEFAULT '[]',
    session_data TEXT DEFAULT '{}',
    
    -- ✅ SYNC IDENTIFIERS
    google_task_id TEXT,
    google_task_list_id TEXT DEFAULT '@default',
    google_calendar_event_id TEXT,
    google_calendar_id TEXT DEFAULT 'primary',
    microsoft_todo_id TEXT,
    microsoft_todo_list_id TEXT
);
```

---

## 🔄 Sync Strategy for Missing Features

### **Strategy 1: Reminders → Use Google Calendar**

**Problem:** Google Tasks has NO reminder field  
**Solution:** When user adds reminder, create BOTH:
1. Google Task (for task tracking)
2. Google Calendar Event (for reminder notification)

```javascript
// User creates Kanban card with reminder
const kanbanCard = {
    title: "Review Budget",
    due_date: "2025-10-31T17:00:00Z",
    reminder_date: "2025-10-31T09:00:00Z",  // 8 hours before due
    reminder_minutes_before: 480  // 8 hours
};

// Sync to Google
// 1. Create Google Task (no reminder field)
const googleTask = await google_tasks_create_task({
    title: "[🔔 HAS REMINDER] Review Budget",  // Flag it!
    notes: "...",
    due: "2025-10-31T17:00:00.000Z"
});

// 2. Create Google Calendar Event (for reminder)
const calendarEvent = await google_calendar_create_event({
    summary: "⏰ Reminder: Review Budget",
    description: "Task reminder - Complete: Review Budget",
    start_datetime: "2025-10-31T09:00:00Z",
    end_datetime: "2025-10-31T09:15:00Z",  // 15-min event
    reminders: {
        useDefault: false,
        overrides: [
            { method: 'email', minutes: 0 },  // At event time
            { method: 'popup', minutes: 0 }
        ]
    }
});

// 3. Link them in sync_metadata
await save_sync_metadata({
    session_id: kanbanCard.session_id,
    google_task_id: googleTask.id,
    google_calendar_event_id: calendarEvent.id
});

// Sync to Microsoft (easy - native support!)
const msTask = await microsoft_todo_create_task({
    title: "Review Budget",
    dueDateTime: {
        dateTime: "2025-10-31T17:00:00",
        timeZone: "UTC"
    },
    reminderDateTime: {  // Native field!
        dateTime: "2025-10-31T09:00:00",
        timeZone: "UTC"
    }
});
```

**Result:** 
- ✅ Google: Task in Tasks + Reminder in Calendar
- ✅ Microsoft: Single To Do task with reminder
- ✅ Kanban: Shows reminder for both platforms

---

### **Strategy 2: Recurrence → Use Google Calendar**

**Problem:** Google Tasks has NO recurrence  
**Solution:** For recurring tasks, use Calendar as primary store

```javascript
// User creates recurring Kanban card
const kanbanCard = {
    title: "Weekly Team Standup",
    recurrence_type: "weekly",
    recurrence_pattern: {
        interval: 1,
        daysOfWeek: ["monday", "wednesday", "friday"]
    },
    start_time: "09:00:00",
    duration_minutes: 15
};

// Sync to Google Calendar (primary for recurring)
const calendarEvent = await google_calendar_create_event({
    summary: "Weekly Team Standup",
    start_datetime: "2025-10-28T09:00:00Z",
    end_datetime: "2025-10-28T09:15:00Z",
    recurrence: [
        "RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR"  // iCalendar format
    ]
});

// Sync to Microsoft To Do (native support!)
const msTask = await microsoft_todo_create_task({
    title: "Weekly Team Standup",
    recurrence: {
        pattern: {
            type: "weekly",
            interval: 1,
            daysOfWeek: ["monday", "wednesday", "friday"]
        },
        range: {
            type: "noEnd",
            startDate: "2025-10-28"
        }
    }
});

// Google Tasks: Create SINGLE instance with note about recurrence
const googleTask = await google_tasks_create_task({
    title: "[🔁 RECURRING] Weekly Team Standup",
    notes: "⚠️ This is a recurring task. See Google Calendar for all instances.\n\nRecurrence: Every Mon, Wed, Fri"
});
```

**Result:**
- ✅ Google: Single task (manual tracking) + Calendar event (actual recurrence)
- ✅ Microsoft: Native recurring task
- ✅ Kanban: Shows as recurring task

---

### **Strategy 3: Priority → Different Implementations**

```javascript
const kanbanCard = {
    title: "Review Budget",
    priority: "high"
};

// Google Tasks: Title prefix
const googleTask = await google_tasks_create_task({
    title: "[HIGH] Review Budget"  // ⭐ Add prefix
});

// Microsoft To Do: Native field
const msTask = await microsoft_todo_create_task({
    title: "Review Budget",  // ✅ Clean title
    importance: "high"       // ✅ Native field!
});

// Google Calendar: Color coding
const calendarEvent = await google_calendar_create_event({
    summary: "Review Budget",
    colorId: "11"  // Red = high priority
});
```

---

### **Strategy 4: Categories/Tags → Platform-Specific**

```javascript
const kanbanCard = {
    title: "Review Budget",
    tags: ["finance", "q4", "urgent"],
    project_name: "Finance Review"
};

// Google Tasks: Encode in notes
const googleTask = await google_tasks_create_task({
    title: "Review Budget",
    notes: `
...

🏷️ Tags: #finance #q4 #urgent
📋 Project: Finance Review
    `.trim()
});

// Microsoft To Do: Native categories
const msTask = await microsoft_todo_create_task({
    title: "Review Budget",
    categories: ["Finance Review", "finance", "q4", "urgent"]  // ✅ Native!
});

// Google Calendar: Store in description
const calendarEvent = await google_calendar_create_event({
    summary: "Review Budget",
    description: `
Tags: finance, q4, urgent
Project: Finance Review
    `.trim()
});
```

---

### **Strategy 5: Checklist → Different Structures**

```javascript
const kanbanCard = {
    title: "Review Budget",
    checklist: [
        { item: "Review marketing spend", completed: false },
        { item: "Analyze ROI", completed: false },
        { item: "Prepare presentation", completed: true }
    ]
};

// Google Tasks: Create subtasks (parent-child hierarchy)
const mainTask = await google_tasks_create_task({
    title: "[HIGH] Review Budget"
});

for (const item of kanbanCard.checklist) {
    await google_tasks_create_task({
        title: item.item,
        parent: mainTask.id,  // ✅ Subtask!
        status: item.completed ? "completed" : "needsAction"
    });
}

// Microsoft To Do: Native checklist
const msTask = await microsoft_todo_create_task({
    title: "Review Budget",
    checklistItems: [  // ✅ Native array!
        { displayName: "Review marketing spend", isChecked: false },
        { displayName: "Analyze ROI", isChecked: false },
        { displayName: "Prepare presentation", isChecked: true }
    ]
});

// Google Calendar: Store in description
const calendarEvent = await google_calendar_create_event({
    summary: "Review Budget",
    description: `
Checklist:
☐ Review marketing spend
☐ Analyze ROI
☑ Prepare presentation
    `.trim()
});
```

---

## 📋 Recommended Universal Field Additions

### **New Fields for Kanban Database:**

```sql
-- Add these to sessions table
ALTER TABLE sessions ADD COLUMN reminder_date TEXT;
ALTER TABLE sessions ADD COLUMN reminder_minutes_before INTEGER DEFAULT 15;
ALTER TABLE sessions ADD COLUMN reminders TEXT DEFAULT '[]';  -- Multiple reminders

ALTER TABLE sessions ADD COLUMN recurrence_type TEXT DEFAULT 'none';
ALTER TABLE sessions ADD COLUMN recurrence_pattern TEXT;  -- JSON
ALTER TABLE sessions ADD COLUMN recurrence_rule TEXT;  -- RRULE format

ALTER TABLE sessions ADD COLUMN is_all_day BOOLEAN DEFAULT 0;
ALTER TABLE sessions ADD COLUMN timezone TEXT DEFAULT 'UTC';
ALTER TABLE sessions ADD COLUMN duration_minutes INTEGER;

ALTER TABLE sessions ADD COLUMN location TEXT;
ALTER TABLE sessions ADD COLUMN attendees TEXT DEFAULT '[]';
ALTER TABLE sessions ADD COLUMN color TEXT;

ALTER TABLE sessions ADD COLUMN is_added_to_my_day BOOLEAN DEFAULT 0;
ALTER TABLE sessions ADD COLUMN attachments TEXT DEFAULT '[]';

ALTER TABLE sessions ADD COLUMN parent_task_id TEXT;
ALTER TABLE sessions ADD COLUMN google_calendar_id TEXT DEFAULT 'primary';
```

---

## 🎯 Final Recommendations

### **For Tasks WITH Reminders:**
1. ✅ **Create in Kanban** with `reminder_date`
2. ✅ **Sync to Microsoft To Do** (native reminder)
3. ✅ **Create Google Task** (for tracking)
4. ✅ **Create Google Calendar Event** (for reminder notification)

### **For Recurring Tasks:**
1. ✅ **Create in Kanban** with `recurrence_pattern`
2. ✅ **Sync to Microsoft To Do** (native recurrence)
3. ✅ **Create Google Calendar Event** (full recurrence)
4. ⚠️ **Create single Google Task** with note about recurrence

### **For Simple Tasks (No Reminder/Recurrence):**
1. ✅ **Create in Kanban**
2. ✅ **Sync to Google Tasks**
3. ✅ **Sync to Microsoft To Do**
4. ❌ **Skip Google Calendar** (not needed)

---

## 🚀 Implementation Priority

**Phase 1: Core Fields** ✅ Already Done
- title, description, status, due_date, priority

**Phase 2: Reminders** 🔜 Add Next
- reminder_date field
- Google Calendar integration for reminders
- Microsoft To Do native reminders

**Phase 3: Recurrence** 🔜 Add After
- recurrence_pattern field
- Google Calendar recurring events
- Microsoft To Do recurring tasks

**Phase 4: Advanced Features** 🔜 Future
- Multiple reminders
- Attachments
- Location
- My Day integration

---

**Summary:** Microsoft To Do has MORE features than Google Tasks. The universal Kanban board should have ALL fields from Microsoft To Do + use Google Calendar to supplement Google Tasks' missing features (reminders & recurrence). 🎯
