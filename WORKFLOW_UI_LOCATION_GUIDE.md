# Workflow UI - Where Everything Is Located

## Visual Location Guide

Based on your screenshot and the code, here's exactly where the workflow title, metadata, and slug pill are displayed:

---

## Location 1: Load Workflow Modal (Primary Location)

This is where you see the **full workflow card** with all metadata when you click the **"Load"** button in the toolbar.

```
┌─────────────────────────────────────────────────────────────────────┐
│  📂 Load Workflow                                          [X]       │
├─────────────────────────────────────────────────────────────────────┤
│  [Search workflows...]  [All Categories ▼]  [All Status ▼]         │
├─────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ ┌──────────────────────────────────────────────────────────┐  │ │
│  │ │ 🔷 Test Email Automation                  ← TITLE       │  │ │
│  │ │ Test workflow for slug integration         ← DESCRIPTION│  │ │
│  │ ├──────────────────────────────────────────────────────────┤  │ │
│  │ │ #wf_nddmbtgg_1763559840  👈 SLUG PILL (click/drag)     │  │ │
│  │ ├──────────────────────────────────────────────────────────┤  │ │
│  │ │ 🟢 draft   Updated: 11/19/2025    ← METADATA           │  │ │
│  │ ├──────────────────────────────────────────────────────────┤  │ │
│  │ │ [📂 Load] [📋 Duplicate] [🗑️ Delete]    ← ACTIONS      │  │ │
│  │ └──────────────────────────────────────────────────────────┘  │ │
│  │                                                               │ │
│  │ ┌──────────────────────────────────────────────────────────┐  │ │
│  │ │ 🔷 Email to Sheets Automation                           │  │ │
│  │ │ Automatically process incoming emails...                │  │ │
│  │ ├──────────────────────────────────────────────────────────┤  │ │
│  │ │ #wf_m3qel1gr_1763559780                                 │  │ │
│  │ ├──────────────────────────────────────────────────────────┤  │ │
│  │ │ 🟢 draft   Updated: 11/19/2025                          │  │ │
│  │ ├──────────────────────────────────────────────────────────┤  │ │
│  │ │ [📂 Load] [📋 Duplicate] [🗑️ Delete]                    │  │ │
│  │ └──────────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│                                        [Cancel]                     │
└─────────────────────────────────────────────────────────────────────┘
```

### How to Access:
1. Click **"Load"** button in toolbar (🔵 icon with folder)
2. Modal opens showing all workflows
3. Each workflow displays as a card with all metadata

---

## Location 2: Canvas Header (When Workflow is Loaded)

When you have a workflow open on the canvas, the slug appears in the header:

```
┌─────────────────────────────────────────────────────────────────────┐
│  🎨 Visual Automation Canvas  [wf_nddmbtgg_1763559840]  ← SLUG     │
│                                └─────────────────────────┘           │
│                                     Current workflow slug            │
├─────────────────────────────────────────────────────────────────────┤
│  [New] [Load] [Save] [Export] [Print] [🤖 Send to AI]  ← Toolbar   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  [Canvas with shapes and connections]                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Workflow Card Structure (Detailed Breakdown)

Each workflow card in the "Load Workflow" modal has this exact structure:

### 1. Header Section
```html
<div class="workflow-header">
    <div class="workflow-icon">
        🔷  ← Project diagram icon
    </div>
    <div class="workflow-details">
        <div class="workflow-title">Test Email Automation</div>
        <div class="workflow-description">Test workflow for slug integration</div>
    </div>
</div>
```

**What you see:**
- **Icon:** 🔷 (blue diamond with project diagram)
- **Title:** Large, bold text (e.g., "Test Email Automation")
- **Description:** Smaller gray text below title

---

### 2. Slug Pill (Most Important!)
```html
<div class="workflow-slug-pill" 
     draggable="true" 
     data-slug="wf_nddmbtgg_1763559840"
     data-workflow-id="wf_nddmbtgg_1763559840"
     title="Drag to AI chat to activate Workflow Designer mode">
    <i class="fas fa-hashtag"></i>
    wf_nddmbtgg_1763559840
</div>
```

**What you see:**
- **Background:** Purple/gray pill-shaped button
- **Icon:** # (hashtag symbol)
- **Text:** Full slug (e.g., `wf_nddmbtgg_1763559840`)
- **Cursor:** Changes to "grab" hand on hover

**Interactions:**
- **Click** → Copies slug to clipboard (toast notification appears)
- **Drag** → Can drag to AI chat panel on right side
- **Hover** → Background lightens, border highlights blue

---

### 3. Metadata Section
```html
<div class="workflow-meta">
    <span class="workflow-status-badge draft">
        <i class="fas fa-circle-dot"></i>
        draft
    </span>
    <span class="workflow-updated">11/19/2025</span>
</div>
```

**What you see:**
- **Status Badge:** 
  - 🟢 "draft" (green dot + text)
  - OR 🔵 "active" (blue dot + text)
  - OR ⚪ "inactive" (gray dot + text)
- **Updated Date:** Last modified date (e.g., "11/19/2025")

---

### 4. Actions Section
```html
<div class="workflow-actions">
    <button data-action="load">📂 Load</button>
    <button data-action="duplicate">📋 Duplicate</button>
    <button data-action="delete" class="danger">🗑️ Delete</button>
</div>
```

**What you see:**
- **Load button:** Opens workflow on canvas
- **Duplicate button:** Creates a copy
- **Delete button:** Removes workflow (red color)

---

## Drag & Drop to AI Chat

### Step-by-Step Process:

```
Step 1: Open Load Workflow Modal
┌────────────────────────────────────┐
│  [Load] ← Click this button       │
└────────────────────────────────────┘

Step 2: Find Your Workflow
┌──────────────────────────────────────────────┐
│  🔷 Test Email Automation                    │
│  Test workflow description                   │
│  ┌──────────────────────────────────────┐   │
│  │ #wf_nddmbtgg_1763559840              │   │  ← This is the slug pill
│  └──────────────────────────────────────┘   │
│  🟢 draft   Updated: 11/19/2025              │
└──────────────────────────────────────────────┘

Step 3: Drag Slug Pill to AI Chat
         ┌──────────────────────┐
         │ #wf_nddmbtgg_1763559840 │ ← Click & hold
         └──────────────────────┘
                  ↓
                  ↓  (drag across screen)
                  ↓
         ┌───────────────────────────────┐
         │  💬 AI Chat Panel (Right)     │
         │  ┌─────────────────────────┐  │
         │  │ [wf_nddmbtgg_1763559840]│  │ ← Drop here
         │  │                         │  │
         │  └─────────────────────────┘  │
         │  [Send]                       │
         └───────────────────────────────┘

Step 4: AI Recognizes Workflow
         AI fetches workflow data and can:
         - Analyze the workflow
         - Suggest improvements
         - Modify shapes/connections
         - Answer questions about it
```

---

## Code Location Reference

### File: `automation-workflows.js`

**Function that creates the workflow cards:**
- **Line 1119:** `createWorkflowListItem(workflow)`
- **Lines 1133-1142:** Workflow header HTML (title + description)
- **Line 1141:** Slug pill HTML with drag/click handlers
- **Lines 1143-1149:** Metadata HTML (status + date)
- **Lines 1150-1158:** Action buttons HTML

**Function that handles slug interactions:**
- **Line 1189:** `handleSlugDragStart(e)` - Drag handling
- **Lines 1167-1174:** Click handler for copying slug

### File: `business-ai-platform-v2.html`

**Modal container:**
- **Line 12903:** `<div id="load-workflow-modal-overlay">` - Modal wrapper
- **Line 12914:** `<div id="workflow-modal-body">` - Modal content area
- **Line 12940:** `<div id="workflow-load-list">` - Where workflow cards are inserted

---

## Visual Styling Details

### Slug Pill Appearance:

**Normal State:**
```css
background: var(--bg-tertiary);     /* Dark gray/purple */
border: 2px solid var(--border-default);
border-radius: 12px;
padding: 6px 12px;
color: var(--text-secondary);       /* Light gray text */
font-family: monospace;
font-size: 11px;
cursor: grab;                       /* Hand cursor */
```

**Hover State:**
```css
background: var(--bg-hover);        /* Lighter background */
border-color: var(--accent-primary); /* Blue border highlight */
transform: scale(1.02);             /* Slight zoom */
```

**Dragging State:**
```css
opacity: 0.7;                       /* Semi-transparent */
cursor: grabbing;                   /* Closed fist cursor */
```

**After Click (Copied):**
```
Toast notification appears:
┌────────────────────────────────────────┐
│ ✅ Workflow slug copied to clipboard   │
└────────────────────────────────────────┘
```

---

## AI Chat Integration

When you drag the slug pill to the AI chat, this happens:

### 1. Drag Event
```javascript
handleSlugDragStart(e) {
    const slug = e.target.dataset.slug;  // wf_nddmbtgg_1763559840
    e.dataTransfer.setData('text/plain', `[${slug}]`);
    e.dataTransfer.setData('workflow-slug', slug);
}
```

### 2. Drop in AI Chat
```
Input field receives: [wf_nddmbtgg_1763559840]
```

### 3. AI Recognition
```javascript
// AI detects workflow slug pattern
if (message.match(/\[wf_[a-z0-9]{8}_\d{10}\]/)) {
    const slug = extractSlugFromMessage(message);
    const workflow = await fetchWorkflow(slug);
    // AI can now access full workflow data
}
```

---

## Summary

### Where is the Title?
**Location:** Top of workflow card in "Load Workflow" modal
**Element:** `.workflow-title`
**Example:** "Test Email Automation"

### Where is the Metadata?
**Location:** Middle section of workflow card (below slug pill)
**Elements:** 
- `.workflow-status-badge` - Status (draft/active/inactive)
- `.workflow-updated` - Last modified date
**Example:** "🟢 draft   Updated: 11/19/2025"

### Where is the Slug Pill?
**Location:** Between header and metadata sections
**Element:** `.workflow-slug-pill`
**Features:**
- **Click:** Copies slug to clipboard
- **Drag:** Can drag to AI chat panel
- **Appearance:** Purple pill with # icon
**Example:** `#wf_nddmbtgg_1763559840`

### How to Access Everything:
1. Click **"Load"** button in toolbar
2. Modal opens with all workflows
3. Each workflow shows: Title → Slug Pill → Metadata → Actions
4. Click slug pill to copy OR drag to AI chat

---

**Last Updated:** November 20, 2025  
**Status:** Fully Documented ✅
