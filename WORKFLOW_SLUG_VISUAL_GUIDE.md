# Workflow Slug - Visual UI Guide

## Where to Find the Slug in the UI

### 1. Workflow List View

```
┌─────────────────────────────────────────────────────────┐
│  📋 Automation Workflows                                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ 🔷 Email to Sheets Automation                  │    │
│  │ Automatically process incoming emails...       │    │
│  │                                                 │    │
│  │ ┌─────────────────────────────────────────┐   │    │
│  │ │ #email-to-sheets-automation  👈 SLUG    │   │  ← Click to copy
│  │ └─────────────────────────────────────────┘   │    │  Drag to AI chat
│  │                                                 │    │
│  │ 🟢 draft    Updated: 2 hours ago               │    │
│  │ [Load] [Duplicate] [Delete]                    │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ 🔷 Daily Sales Report Generator                │    │
│  │ Automatically compile sales data...            │    │
│  │                                                 │    │
│  │ ┌─────────────────────────────────────────┐   │    │
│  │ │ #daily-sales-report  👈 SLUG            │   │    │
│  │ └─────────────────────────────────────────┘   │    │
│  │                                                 │    │
│  │ 🟢 draft    Updated: 3 hours ago               │    │
│  │ [Load] [Duplicate] [Delete]                    │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**The slug pill:**
- **Purple/gray background** with `#` icon
- **Draggable** (cursor changes to grab icon)
- **Clickable** (copies to clipboard with toast notification)
- Located below workflow description
- Shows full slug text

### 2. Workflow Canvas Toolbar

```
┌────────────────────────────────────────────────────────────────┐
│  Visual Automation Canvas - Email to Sheets Automation        │
│                              └─────────────────────────┘       │
│                                      ↑ Workflow title          │
│  ┌──────────────────────────────────────────────────────┐     │
│  │ [New] [Load] [Save] [Export] [Print] [🤖 Send to AI]│     │
│  │                                                       │     │
│  │ 📊 email-to-sheets-automation  👈 SLUG (in toolbar)  │  ← Click to copy
│  │                                      └───────────────┘│    │  Drag to AI chat
│  └──────────────────────────────────────────────────────┘     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                                                           │ │
│  │   [Workflow shapes and connections displayed here]       │ │
│  │                                                           │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

**Toolbar slug button:**
- Small pill button with monospace font
- Located after workflow title in toolbar
- Draggable to AI chat input
- Clickable to copy

### 3. AI Chat Integration

#### Option A: Drag & Drop
```
Step 1: Drag slug from workflow list
┌─────────────────────────────┐
│ #email-to-sheets-automation │  ← Click and drag this
└─────────────────────────────┘
            ↓
            ↓ (drag)
            ↓
Step 2: Drop into AI chat
┌──────────────────────────────────────────────┐
│ 💬 Chat with AI                              │
├──────────────────────────────────────────────┤
│                                              │
│ [email-to-sheets-automation] 👈 Dropped slug│
│ Can you analyze this workflow?               │
│                                              │
│ [Send]                                       │
└──────────────────────────────────────────────┘
```

#### Option B: Click to Copy, Then Paste
```
Step 1: Click slug pill
┌─────────────────────────────┐
│ #email-to-sheets-automation │  ← Click
└─────────────────────────────┘
         ↓
  ✅ "Workflow slug copied to clipboard"
         ↓
Step 2: Paste in AI chat
┌──────────────────────────────────────────────┐
│ 💬 Chat with AI                              │
├──────────────────────────────────────────────┤
│                                              │
│ email-to-sheets-automation 👈 Pasted slug   │
│ Please review this automation                │
│                                              │
│ [Send]                                       │
└──────────────────────────────────────────────┘
```

#### Option C: Send to AI Button
```
Step 1: Click "Send to AI" button on canvas
┌────────────────────────────────────────┐
│ [🤖 Send to AI]  ← Click this button  │
└────────────────────────────────────────┘
         ↓
Step 2: Workflow auto-inserted in chat
┌──────────────────────────────────────────────────────────┐
│ 💬 Chat with AI                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ [AUTOMATION: Email to Sheets Automation                 │
│  (email-to-sheets-automation)] 👈 Auto-inserted         │
│                                                          │
│ [Send]                                                   │
└──────────────────────────────────────────────────────────┘
```

## Slug Format Examples

### Good Slugs (Auto-generated)
```
Original Title                  →  Generated Slug
──────────────────────────────────────────────────────────
"Email to Sheets Automation"    →  email-to-sheets-automation
"Daily Sales Report"            →  daily-sales-report
"Customer Onboarding Flow"      →  customer-onboarding-flow
"Invoice Approval & Payment"    →  invoice-approval-workflow
"TEST 123 Workflow!"            →  test_123_workflow
```

### Slug Rules
- ✅ Lowercase only
- ✅ Letters a-z
- ✅ Numbers 0-9
- ✅ Hyphens `-` (from spaces)
- ✅ Underscores `_` (from spaces)
- ✅ Max 50 characters
- ❌ No special characters (!@#$%^&*()[]{}|;:'",.<>?/)
- ❌ No spaces (converted to underscores/hyphens)
- ❌ No uppercase (converted to lowercase)

## How to Use Slugs with AI

### Scenario 1: "Review my workflow"
```
User: email-to-sheets-automation
      Can you review this workflow and suggest improvements?

AI: 
✅ Fetches workflow using slug
✅ Analyzes 6 shapes and 6 connections
✅ Responds with suggestions:
   - Add error handling for failed email parsing
   - Consider adding retry logic for Sheets API
   - Add notification for urgent emails
```

### Scenario 2: "Make changes"
```
User: [email-to-sheets-automation]
      Add a shape to send Slack notifications for urgent emails

AI:
✅ Fetches workflow data
✅ Adds new "Send Slack" shape at position (500, 360)
✅ Adds connection from "Categorize" to "Send Slack"
✅ Saves updated workflow
✅ Responds: "Added Slack notification shape for urgent emails"
```

### Scenario 3: "Explain workflow"
```
User: Drag slug → [daily-sales-report]
      What does this automation do?

AI:
✅ Fetches workflow by slug
✅ Analyzes shape sequence
✅ Responds:
   "This workflow:
   1. Triggers daily at 9 AM
   2. Queries sales database
   3. Calculates metrics
   4. Generates charts
   5. Formats HTML report
   6. Emails to management
   7. Archives to Google Drive"
```

## Visual Indicators

### Slug Pill States

#### Normal State
```
┌─────────────────────────────┐
│ # email-to-sheets-automation│
└─────────────────────────────┘
Background: Gray/Purple
Text: White
Cursor: Pointer (hand)
```

#### Hover State
```
┌─────────────────────────────┐
│ # email-to-sheets-automation│  ← Lighter background
└─────────────────────────────┘
Background: Lighter gray/purple
Border: Blue highlight
Cursor: Grab (open hand)
```

#### Dragging State
```
┌─────────────────────────────┐
│ # email-to-sheets-automation│  ← Semi-transparent
└─────────────────────────────┘
Opacity: 0.5
Cursor: Grabbing (closed fist)
```

#### After Click (Copy)
```
┌─────────────────────────────┐
│ # email-to-sheets-automation│
└─────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│ ✅ Workflow slug copied to clipboard   │  ← Toast notification
└────────────────────────────────────────┘
```

## Mobile/Touch Support

**Touch Interactions:**
- **Tap** = Copy to clipboard
- **Long press** = Show context menu (copy/share)
- **No drag-and-drop** on mobile (copy/paste only)

## Accessibility

**Screen Readers:**
- Slug pill: "Workflow identifier: email-to-sheets-automation. Click to copy. Draggable."
- Copy button: "Copy workflow slug to clipboard"
- After copy: "Slug copied successfully"

## Summary

### Where Slugs Appear:
1. ✅ Workflow list cards (below description)
2. ✅ Canvas toolbar (next to title)
3. ✅ AI chat input (when dragged/pasted)

### How to Use:
1. ✅ **Click** slug pill → Copies to clipboard
2. ✅ **Drag** slug pill → Drops into AI chat
3. ✅ **Send to AI** button → Auto-inserts in chat

### What AI Does:
1. ✅ Recognizes slug format (lowercase, hyphens/underscores)
2. ✅ Calls API: `GET /api/automation/{slug}`
3. ✅ Retrieves workflow data (shapes, connections)
4. ✅ Analyzes and responds with suggestions

**The slug system is fully functional and ready to use!**

---

**Last Updated:** November 19, 2025  
**Status:** Production Ready ✅
