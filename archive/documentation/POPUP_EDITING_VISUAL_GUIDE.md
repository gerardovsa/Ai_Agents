# Synergy Popup Inline Editing - Visual Guide

**Visual walkthrough of the new popup editing feature**

---

## 🎨 UI States

### **State 1: Normal Popup (View Mode)**

```
┌─────────────────────────────────────────────┐
│ Synergy Pop-Out     [✎ Edit] [🗑] [✕ Close]│
├─────────────────────────────────────────────┤
│                                             │
│  📌 Update Database Schema                  │
│                                             │
│  Description:                               │
│  Add new fields for synergy integration     │
│                                             │
│  📁 Database Project                        │
│  🟡 Medium  ⚡ Active  🕐 2h ago            │
│                                             │
│  👥 John, Sarah                             │
│  📅 Due: Nov 20, 2025                       │
│                                             │
│  📄 Documents (2)                           │
│  🔗 Links (1)                               │
│  ✓ Next Steps (3)                           │
│                                             │
└─────────────────────────────────────────────┘
```

**Features:**
- Clean, readable view
- Edit button (blue) in top-right
- Delete button (red) next to edit
- Close button (gray) at far right
- All content displayed (not editable)

---

### **State 2: Edit Mode Activated**

```
┌─────────────────────────────────────────────┐
│ Synergy Pop-Out       [💾 Save] [✕ Cancel] │ ← Orange border
├─────────────────────────────────────────────┤
│                                             │
│  📌 [EDITING]                               │ ← Orange badge
│                                             │
│  📝 Title                                   │
│  ┌───────────────────────────────────────┐ │
│  │ Update Database Schema                │ │ ← Text input
│  └───────────────────────────────────────┘ │
│                                             │
│  📄 Description                             │
│  ┌───────────────────────────────────────┐ │
│  │ Add new fields for synergy           │ │ ← Textarea
│  │ integration                           │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  📁 Project          🚩 Priority            │
│  ┌─────────────┐    ┌─────────────┐       │
│  │ Database    │    │ Medium ▼   │       │ ← Two columns
│  └─────────────┘    └─────────────┘       │
│                                             │
│  ⚡ Status           📊 Column              │
│  ┌─────────────┐    ┌─────────────┐       │
│  │ Active ▼   │    │ In Progress│       │
│  └─────────────┘    └─────────────┘       │
│                                             │
│  📅 Due Date         🕐 Due Time            │
│  ┌─────────────┐    ┌─────────────┐       │
│  │ 2025-11-20  │    │ 14:30       │       │
│  └─────────────┘    └─────────────┘       │
│                                             │
│  👥 Assignees (comma-separated)             │
│  ┌───────────────────────────────────────┐ │
│  │ John, Sarah                           │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  🏷️ Tags (comma-separated)                 │
│  ┌───────────────────────────────────────┐ │
│  │ database, backend, urgent             │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  💬 Thread IDs (comma-separated)            │
│  ┌───────────────────────────────────────┐ │
│  │ thread_123, thread_456                │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  🤖 Assigned Agents (comma-separated)       │
│  ┌───────────────────────────────────────┐ │
│  │ Database Agent, Schema Agent          │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  📝 Notes                                   │
│  ┌───────────────────────────────────────┐ │
│  │ Remember to backup before changes     │ │
│  │                                       │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ╔═══════════════════════════════════════╗ │
│  ║ ℹ️  Documents, links, next steps,     ║ │ ← Info box
│  ║    and checklists can be edited      ║ │
│  ║    after saving.                      ║ │
│  ╚═══════════════════════════════════════╝ │
│                                             │
└─────────────────────────────────────────────┘
```

**Features:**
- Orange border around entire popup
- "EDITING" badge with pencil icon
- Save button (green) replaces Edit
- Cancel button (gray) replaces Close
- All fields become inputs/selects/textareas
- Two-column layout for related fields
- Info box explains limitations
- Focused field gets blue outline

---

### **State 3: After Save (Back to View Mode)**

```
┌─────────────────────────────────────────────┐
│ Synergy Pop-Out     [✎ Edit] [🗑] [✕ Close]│ ← Normal border
├─────────────────────────────────────────────┤
│                                             │
│  📌 Update Database Schema (UPDATED!)       │ ← Shows changes
│                                             │
│  Description:                               │
│  Add new fields for synergy integration     │
│  (with additional notes...)                 │
│                                             │
│  📁 Database Project                        │
│  🔴 High  ⚡ Active  🕐 Just now            │
│                                             │
│  👥 John, Sarah, Mike                       │
│  📅 Due: Nov 20, 2025 14:30                 │
│                                             │
│  🏷️ database, backend, urgent, critical    │
│                                             │
│  ✅ Changes saved successfully!             │ ← Success message
│                                             │
└─────────────────────────────────────────────┘
```

**Features:**
- Returns to normal view mode
- Shows updated data
- Success notification appears briefly
- Edit/Delete/Close buttons restored
- Changes persisted to database

---

## 🖱️ User Interactions

### **Click Flow Diagram**

```
START
  │
  ├─> [Open Popup]
  │     │
  │     ├─> View Mode
  │     │     │
  │     │     ├─> Click [Edit] ──────────────┐
  │     │     │                               │
  │     │     ├─> Click [Delete] ─> Confirm ─> DELETE CARD
  │     │     │                               
  │     │     └─> Click [Close] ───────────> CLOSE POPUP
  │     │
  │     └─> Edit Mode <─────────────────────┘
  │           │
  │           ├─> Modify Fields
  │           │     │
  │           │     ├─> Click [Save] ────> API Call ───> View Mode
  │           │     │                         │
  │           │     │                         ├─> Success → Show Notification
  │           │     │                         │
  │           │     │                         └─> Error → Show Error Message
  │           │     │
  │           │     └─> Click [Cancel] ────> Discard Changes → View Mode
  │           │
  │           └─> Click [Delete] ─> Confirm ─> DELETE CARD
  │
END
```

---

## 🎬 Animation & Transitions

### **Edit Mode Activation**

```
1. User clicks [Edit]
   ↓
2. Border fades from gray to orange (0.2s)
   ↓
3. Header background gradient appears (0.3s)
   ↓
4. Buttons morph: Edit/Delete/Close → Save/Cancel (0.2s)
   ↓
5. Content re-renders with inputs (0.1s)
   ↓
6. "EDITING" badge slides in (0.2s)
   ↓
7. First input auto-focuses (optional)
```

### **Save Operation**

```
1. User clicks [Save]
   ↓
2. Button shows loading spinner (optional)
   ↓
3. API call starts (200-500ms)
   ↓
4. If success:
   │  ├─> Border fades orange → gray (0.2s)
   │  ├─> Content re-renders with saved data (0.1s)
   │  ├─> Buttons morph: Save/Cancel → Edit/Delete/Close (0.2s)
   │  └─> Success notification appears (green, 2s)
   ↓
5. If error:
   │  ├─> Stay in edit mode
   │  └─> Error notification appears (red, 4s)
```

---

## 🎨 Color Scheme

### **Button Colors**

| Button | Normal | Hover | Active |
|--------|--------|-------|--------|
| **Edit** | Blue `#58a6ff` | Blue bg + white text | - |
| **Save** | Green `#3fb950` | Green bg + white text | - |
| **Cancel** | Gray `#8b949e` | Light gray bg | - |
| **Delete** | Red `#f85149` | Red bg + white text | - |
| **Close** | Gray `#8b949e` | Red bg + white text | - |

### **State Colors**

| State | Border | Header | Badge |
|-------|--------|--------|-------|
| **View** | Gray `#30363d` | Dark `#1c2128` | None |
| **Edit** | Orange `#d29922` | Orange gradient | Orange `#d29922` |

### **Form Colors**

| Element | Background | Border | Focus |
|---------|------------|--------|-------|
| **Input** | Dark `#0d1117` | Gray `#30363d` | Blue + shadow |
| **Textarea** | Dark `#0d1117` | Gray `#30363d` | Blue + shadow |
| **Select** | Dark `#0d1117` | Gray `#30363d` | Blue + shadow |

---

## 📱 Responsive Behavior

### **Desktop (>1200px)**
- Popup width: 600px
- Two-column form layout
- Full button labels visible
- All fields displayed

### **Tablet (768px - 1200px)**
- Popup width: 500px
- Two-column form layout maintained
- Button icons + labels
- Scrollable content area

### **Mobile (<768px)**
- Popup width: 90vw (responsive)
- Single-column form layout
- Button icons only (no labels)
- Larger touch targets (44px)

---

## ⌨️ Keyboard Shortcuts (Future Enhancement)

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` / `Cmd+S` | Save changes (in edit mode) |
| `Esc` | Cancel edit / Close popup |
| `Ctrl+E` / `Cmd+E` | Toggle edit mode |
| `Tab` | Navigate between fields |
| `Shift+Tab` | Navigate backwards |
| `Ctrl+Z` / `Cmd+Z` | Undo last change (future) |

---

## 🔍 Visual Indicators

### **Edit Mode Active:**
- 🟠 Orange border around popup
- 🟠 Orange "EDITING" badge
- 🟠 Orange gradient in header
- 🔵 Blue outline on focused field
- 💚 Green Save button
- ⚫ Gray Cancel button

### **Changes Saved:**
- ✅ Green success notification
- 🔄 Updated "Last Active" time
- 🔵 Blue border returns
- 🔵 Blue Edit button visible

### **Delete Confirmation:**
- ⚠️ Modal dialog overlay
- ❓ "Are you sure?" message
- 🔴 Red "Delete" button
- ⚫ Gray "Cancel" button

---

## 🧩 Component Breakdown

```
PopupWindow
├── PopupHeader
│   ├── Title ("Synergy Pop-Out")
│   └── ControlButtons
│       ├── EditButton (view mode)
│       ├── SaveButton (edit mode)
│       ├── CancelButton (edit mode)
│       ├── DeleteButton (view mode)
│       └── CloseButton (view mode)
├── PopupContent
│   ├── ViewMode (renderCardExpanded)
│   │   ├── CardHeader
│   │   ├── Title
│   │   ├── Description
│   │   ├── MetaInfo
│   │   ├── Documents
│   │   ├── Links
│   │   ├── NextSteps
│   │   ├── Checklist
│   │   └── ActivityLog
│   └── EditMode (renderCardExpandedEditable)
│       ├── EditBadge
│       ├── TitleInput
│       ├── DescriptionTextarea
│       ├── ProjectInput
│       ├── PrioritySelect
│       ├── StatusSelect
│       ├── ColumnSelect
│       ├── DueDateInput
│       ├── DueTimeInput
│       ├── AssigneesInput
│       ├── TagsInput
│       ├── ThreadIDsInput
│       ├── AssignedAgentsInput
│       ├── NotesTextarea
│       └── InfoBox
└── PopupFooter
    ├── Timestamp
    ├── MoveWarning (expanded only)
    └── SessionID
```

---

## 🎯 Accessibility Features

### **Keyboard Navigation:**
- All buttons focusable via Tab
- Enter/Space activates buttons
- Form fields navigable via Tab
- Escape closes popup (future)

### **Screen Reader Support:**
- Button titles for context
- Label associations for inputs
- Role attributes for modals
- ARIA labels for icons

### **Visual Accessibility:**
- High contrast colors
- Focus indicators (blue outline)
- Sufficient button sizes (28px min)
- Clear state changes (border color)

---

## 🔄 State Management

```javascript
// Popup State Object (conceptual)
const popupState = {
  windowId: 'popout-session_123-1234567890',
  sessionId: 'session_123',
  mode: 'view',  // 'view' or 'edit'
  isActive: true,
  position: { x: 200, y: 100 },
  size: { width: 600, height: 700 },
  isDirty: false,  // Has unsaved changes
  originalData: { /* session object */ },
  editedData: { /* modified fields */ }
}
```

### **State Transitions:**

```
view → edit: User clicks Edit button
edit → view: User clicks Save (success) or Cancel
view → closed: User clicks Close or Delete (after confirm)
edit → closed: User clicks Delete (after confirm)
```

---

## 📐 Layout Specifications

### **Popup Dimensions:**
- Min Width: 500px
- Min Height: 400px
- Default Width: 600px
- Default Height: 700px
- Max Width: 90vw
- Max Height: 90vh
- Resizable: Yes (both directions)

### **Header:**
- Height: 48px
- Padding: 12px
- Background: `#1c2128`

### **Content:**
- Padding: 16px
- Overflow: Scroll (Y-axis)
- Background: `#0d1117`

### **Footer:**
- Height: 36px
- Padding: 8px 12px
- Background: `#1c2128`

### **Form Fields:**
- Input Height: 36px
- Textarea Min Height: 80px
- Label Font Size: 13px
- Input Font Size: 14px
- Border Radius: 6px
- Padding: 8px 12px

---

**This visual guide provides a comprehensive overview of the UI states, interactions, and design specifications for the Synergy popup inline editing feature.**

**Created:** November 14, 2025  
**Version:** 1.0
