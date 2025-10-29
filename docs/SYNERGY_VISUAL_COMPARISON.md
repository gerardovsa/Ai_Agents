# 🎨 Synergy Dashboard - Visual Comparison: Collapsed vs Expanded Views

## 📊 Overview

This document provides a visual comparison of the Kanban card views to help understand what users see in each state.

---

## 🔍 Collapsed View (Default)

### What Users See

```
┌─────────────────────────────────────────────┐
│ 🔴  Email Marketing Campaign           [⋮]  │  ← Priority + Menu
│                                             │
│ Email Marketing Campaign                    │  ← Title (Bold)
│                                             │
│ 📁 Q4 Marketing                             │  ← Project
│ [Active] • 2h ago                           │  ← Status + Time
│                                             │
│ 💬 12  📄 3  ✅ 4                            │  ← Stats
│                                             │
│ Recent Activity                             │
│ • Assistant message added (2h ago)          │  ← Recent (3 max)
│ • Doc created: Customer List (3h ago)       │
│ • Next step: Upload customer CSV (4h ago)   │
│                                             │
│ sess_20251028_1430_john_...                 │  ← Session ID (truncated)
│ [email] [marketing] [campaign]              │  ← Tags (3 max)
│                                             │
│ [⬇ Expand]          [▶ Resume]              │  ← Action Buttons
└─────────────────────────────────────────────┘
```

### Features Visible in Collapsed View

✅ Priority indicator (emoji)  
✅ Card menu (⋮)  
✅ Edit button  
✅ Title  
✅ Project name  
✅ Status badge  
✅ Time ago  
✅ Stats (messages, docs, steps)  
✅ Recent activity (first 3)  
✅ Tags (first 3)  
✅ Session ID (truncated)  
✅ Expand button  
✅ Resume button  

**Size:** Compact (~180px height)  
**Purpose:** Show summary at a glance  
**Best for:** Viewing many cards simultaneously

---

## 🔎 Expanded View (Detailed)

### What Users See

```
┌─────────────────────────────────────────────────────────────┐
│ 🔴  Email Marketing Campaign            [✏️] [⋮]            │  ← Priority + Edit + Menu
│                                                             │
│ Email Marketing Campaign                                    │  ← Title (Larger)
│                                                             │
│ ═══════════════════════════════════════════════════════════ │
│ 📋 Description                                              │
│ Create and launch Q4 email marketing campaign targeting     │
│ existing customers with holiday promotions and special      │
│ offers. Focus on customer retention and upselling.          │  ← Full Description
│ ═══════════════════════════════════════════════════════════ │
│                                                             │
│ 📁 Q4 Marketing  [Active]  🕐 2h ago                        │  ← Project + Status + Time
│                                                             │
│ 👥 John Doe, AI Assistant                                   │  ← Assignees
│ 📅 Due: 11/02/2025                                          │  ← Due Date
│                                                             │
│ ═══════════════════════════════════════════════════════════ │
│ 📄 Documents (3)                                            │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📄 Email Templates Draft      [google_doc]              │ │
│ │    https://docs.google.com/document/d/abc123            │ │
│ │                                                         │ │
│ │ 📊 Customer Segmentation List [google_sheet]            │ │
│ │    https://sheets.google.com/spreadsheets/d/xyz789      │ │
│ │                                                         │ │
│ │ 📈 Campaign Performance Dashboard [dashboard]            │ │
│ │    https://datastudio.google.com/reporting/def456       │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ═══════════════════════════════════════════════════════════ │
│                                                             │
│ 🔗 Links (3)                                                │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🔗 Campaign Brief            [notion]                   │ │
│ │    https://notion.so/campaign-brief                     │ │
│ │                                                         │ │
│ │ 🎨 Design Mockups            [figma]                    │ │
│ │    https://figma.com/mockups                            │ │
│ │                                                         │ │
│ │ 📊 Analytics Dashboard       [analytics]                │ │
│ │    https://analytics.google.com/dashboard               │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ═══════════════════════════════════════════════════════════ │
│                                                             │
│ ✅ Next Steps (4)                                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ☐ Upload customer CSV              Due: 10/29/2025      │ │  ← Interactive Checkbox
│ │ ☐ Review email templates           Due: 10/30/2025      │ │
│ │ ☐ Set up A/B test                  Due: 10/31/2025      │ │
│ │ ☐ Schedule send time               Due: 11/01/2025      │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ═══════════════════════════════════════════════════════════ │
│                                                             │
│ ☑️ Checklist (2/5)                                          │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ☑ Customer segmentation                    (completed)   │ │  ← Interactive Checkbox
│ │ ☑ Email template design                    (completed)   │ │
│ │ ☐ Copy writing                                          │ │
│ │ ☐ Legal review                                          │ │
│ │ ☐ QA testing                                            │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ═══════════════════════════════════════════════════════════ │
│                                                             │
│ 📝 Notes                                                    │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Customer segmentation complete. Need to finalize email  │ │
│ │ templates and get approval from legal team. Marketing   │ │
│ │ manager requested additional A/B test variants.         │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ═══════════════════════════════════════════════════════════ │
│                                                             │
│ 📜 Activity Log                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ • Assistant message added               2h ago          │ │
│ │ • Doc created: Customer List Template   3h ago          │ │
│ │ • Next step: Upload customer CSV        4h ago          │ │
│ │ • Checklist updated (2/5 complete)      5h ago          │ │
│ │ • Card created by AI                    7d ago          │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [email] [marketing] [campaign]                              │  ← All Tags
│ sess_20251028_1430_john_email_campaign                      │  ← Full Session ID
│                                                             │
│ [⬆ Collapse]                    [▶ Resume Session]          │  ← Action Buttons
└─────────────────────────────────────────────────────────────┘
```

### Features Visible in Expanded View

✅ **Everything from collapsed view** PLUS:  
✅ Full description text  
✅ Complete notes (long-form)  
✅ All documents with clickable links  
✅ All external links with clickable URLs  
✅ Complete next steps list with interactive checkboxes  
✅ Full checklist with interactive checkboxes  
✅ All assignees  
✅ Created date & due date  
✅ Complete activity log (all entries)  
✅ All tags (not limited to 3)  
✅ Full session ID (not truncated)  
✅ Collapse button  

**Size:** Variable (~400-800px height depending on content)  
**Purpose:** Show complete card details for working  
**Best for:** Detailed task management

---

## 🎭 Comparison Table

| Feature | Collapsed View | Expanded View |
|---------|----------------|---------------|
| **Title** | ✅ Standard size | ✅ Larger size |
| **Description** | ❌ Hidden | ✅ Full text |
| **Notes** | ❌ Hidden | ✅ Full text |
| **Documents** | ❌ Hidden (count only) | ✅ All with links |
| **Links** | ❌ Hidden | ✅ All with URLs |
| **Next Steps** | ❌ Hidden (count only) | ✅ All with checkboxes |
| **Checklist** | ❌ Hidden | ✅ All with checkboxes |
| **Assignees** | ❌ Hidden | ✅ All displayed |
| **Due Date** | ❌ Hidden | ✅ Displayed |
| **Created Date** | ❌ Hidden | ✅ Displayed |
| **Activity Log** | ✅ First 3 entries | ✅ All entries |
| **Tags** | ✅ First 3 | ✅ All tags |
| **Session ID** | ✅ Truncated | ✅ Full ID |
| **Interactive Checkboxes** | ❌ No | ✅ Yes (steps & checklist) |
| **Clickable Links** | ❌ No | ✅ Yes (docs & links) |
| **Height** | ~180px | ~400-800px |

---

## 🎬 Animation & Transitions

### Expand Animation
```
Collapsed → Expanding → Expanded
(180px)      (fade in)    (800px)
   ↓            ↓            ↓
Summary    Smooth grow   Full detail
  view      animation       view
```

**Duration:** 300ms  
**Easing:** ease  
**Effect:** Smooth height transition with fade-in of content

### Collapse Animation
```
Expanded → Collapsing → Collapsed
 (800px)     (fade out)   (180px)
    ↓            ↓            ↓
Full detail  Smooth      Summary
   view      shrink        view
```

**Duration:** 300ms  
**Easing:** ease  
**Effect:** Smooth height transition with fade-out of content

---

## 🖱️ User Interactions

### In Collapsed View

**Click "Expand" button:**
→ Card smoothly expands to show all details

**Click "Resume" button:**
→ Opens AI chat panel with session context

**Click "Edit" button (✏️):**
→ Opens edit modal (coming soon)

**Click card menu (⋮):**
→ Shows card actions menu (coming soon)

**Drag card:**
→ Move to different column (Dragula)

### In Expanded View

**Click "Collapse" button:**
→ Card smoothly collapses to summary view

**Click "Resume Session" button:**
→ Opens AI chat panel with session context

**Click document link:**
→ Opens document in new tab

**Click external link:**
→ Opens link in new tab

**Check/uncheck next step:**
→ Toggles completion status
→ Updates pending steps count
→ Card re-renders

**Check/uncheck checklist item:**
→ Toggles completion status
→ Updates checklist progress (e.g., "3/5")
→ Card re-renders

**Click "Edit" button (✏️):**
→ Opens edit modal (coming soon)

**Click card menu (⋮):**
→ Shows card actions menu (coming soon)

**Drag card:**
→ Move to different column (maintains expanded state)

---

## 💼 Use Cases

### When to Use Collapsed View

✅ **Scanning multiple tasks** - See many cards at once  
✅ **Quick prioritization** - Identify high-priority items  
✅ **Status overview** - Check what's in progress  
✅ **Time management** - See what's been idle  
✅ **Tag filtering** - Quick category identification  

### When to Use Expanded View

✅ **Working on a task** - See all context  
✅ **Updating progress** - Check off steps and checklist items  
✅ **Reading notes** - Review detailed context  
✅ **Accessing documents** - Click links to files  
✅ **Reviewing history** - Check complete activity log  
✅ **Understanding scope** - Read full description  

---

## 🎨 Visual Design Principles

### Color Coding

**Priority Indicators:**
- 🔴 High - Red
- 🟡 Medium - Yellow
- 🟢 Low - Green

**Status Badges:**
- 🟦 Active - Blue background
- 🟧 Paused - Orange background
- 🟩 Completed - Green background

**Due Date Indicators:**
- ⚪ Normal - Default color
- 🔴 Overdue - Red text + red background

**Completion States:**
- ☐ Incomplete - Empty checkbox
- ☑ Complete - Checked checkbox (with strikethrough)

### Typography Hierarchy

**Collapsed View:**
```
Title:       14px, bold
Project:     12px, regular
Stats:       11px, regular
Activity:    11px, italic
Tags:        9px, uppercase
Session ID:  9px, monospace
```

**Expanded View:**
```
Title:       16px, bold
Section:     12px, bold, uppercase
Content:     12px, regular
Links:       12px, underline on hover
Notes:       12px, line-height: 1.6
Activity:    11px, regular
Session ID:  10px, monospace
```

### Spacing & Layout

**Collapsed View:**
- Padding: 12px
- Gap between elements: 8px
- Border radius: 8px

**Expanded View:**
- Padding: 16px
- Gap between sections: 16px
- Section padding: 12px
- Border radius: 8px

---

## 📱 Responsive Behavior

### Desktop (>1200px)
- Cards: Full width in column
- Expanded view: Comfortable reading width
- All features visible

### Tablet (768px - 1200px)
- Cards: Full width in column
- Expanded view: Adjusted for smaller screen
- Horizontal scroll for wide content

### Mobile (<768px)
- Kanban board: Vertical stack or horizontal scroll
- Cards: Full width
- Expanded view: Full screen overlay recommended
- Touch-friendly checkbox sizes

---

## 🚀 Performance Notes

**Rendering Performance:**
- Collapsed view: Fast (minimal DOM elements)
- Expanded view: Optimized (lazy rendering of sections)
- Transition: GPU-accelerated (transform/opacity)

**Memory Usage:**
- Collapsed: ~5KB per card
- Expanded: ~15KB per card
- Recommendation: Keep max 50-100 expanded cards visible

**Best Practices:**
- Collapse cards after editing to save memory
- Use virtual scrolling for 100+ cards
- Debounce checkbox toggle events

---

## 🎯 Key Takeaways

1. **Collapsed view** is for **scanning and organizing**
2. **Expanded view** is for **working and managing**
3. **Smooth transitions** make switching comfortable
4. **Interactive elements** only in expanded view
5. **All data preserved** during collapse/expand
6. **Drag & drop works** in both states
7. **State persists** during drag operations

---

**Last Updated:** October 28, 2025  
**Version:** 3.0.0  
**Status:** ✅ Visual Guide Complete

