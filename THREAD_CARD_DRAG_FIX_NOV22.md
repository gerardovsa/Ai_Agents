# Thread Card Drag-and-Drop Fix - November 22, 2025

## Problem
Thread info cards lost their drag-and-drop functionality. Users could not drag threads between Prime, Agent columns, and Thread History.

## Root Cause
The `ThreadCardTemplates.compactCard()` and `ThreadCardTemplates.fullCard()` functions in `thread-card-templates.js` were missing the `draggable="true"` attribute and drag event handlers (`ondragstart`, `ondragend`).

**Location:** `UI/external/modules/thread-cards/thread-card-templates.js`

## Console Logs Indicated
```
✅ [Drop Zone] Agent 1 configured (entire column is drop area)
✅ [Drop Zone] Agent 2 configured (entire column is drop area)
✅ [Drop Zone] Agent 3 configured (entire column is drop area)
✅ [Drop Zone] Prime configured (entire panel is drop area)
```

Drop zones were working, but the cards themselves were not draggable.

## Fix Applied

### File Modified
`UI/external/modules/thread-cards/thread-card-templates.js`

### Changes Made

**1. compactCard() function (line 169-176):**

**Before:**
```javascript
return `
    <div class="ai-chat-header-info agent-thread-card" id="${location}-thread-info" data-thread-id="${thread.id}" data-location="${location}">
```

**After:**
```javascript
return `
    <div class="ai-chat-header-info agent-thread-card" 
         id="${location}-thread-info" 
         data-thread-id="${thread.id}" 
         data-location="${location}"
         draggable="true"
         ondragstart="ThreadManager.handleDragStart(event)"
         ondragend="ThreadManager.handleDragEnd(event)">
```

**2. fullCard() function (line 237-244):**

**Before:**
```javascript
return `
    <div class="ai-chat-header-info" id="${location}-thread-info" data-thread-id="${thread.id}" data-location="${location}">
```

**After:**
```javascript
return `
    <div class="ai-chat-header-info" 
         id="${location}-thread-info" 
         data-thread-id="${thread.id}" 
         data-location="${location}"
         draggable="true"
         ondragstart="ThreadManager.handleDragStart(event)"
         ondragend="ThreadManager.handleDragEnd(event)">
```

## What This Enables

✅ **Drag threads from Prime to Agent columns**
✅ **Drag threads from Agent columns to other agents**
✅ **Drag threads from Thread History to Prime/Agents**
✅ **Drag threads back to Prime from agents**
✅ **Visual feedback during drag operations**

## Testing
1. Refresh the browser (Ctrl+F5 to clear cache)
2. Try dragging a thread card from Thread History to Prime
3. Try dragging a thread from Prime to an Agent column
4. Try dragging between Agent columns
5. All drag operations should now work smoothly

## Related Files
- `UI/modules/thread-manager/thread-manager-interactions.js` - Contains `handleDragStart()` and `handleDragEnd()` handlers
- `UI/modules/thread-manager/thread-manager-ui.js` - Has fallback inline template with draggable (not used when ThreadCardTemplates exists)
- `UI/external/modules/thread-cards/thread-card-templates.js` - **FIXED FILE** (this is the active template system)

## Technical Details

### Drag Event Flow
```
User clicks and drags card
    ↓
ondragstart fires
    ↓
ThreadManager.handleDragStart(event)
    ↓
Sets event.dataTransfer.effectAllowed = 'move'
    ↓
Stores thread ID in event.dataTransfer
    ↓
User drops on target zone
    ↓
Target's ondrop handler processes the move
    ↓
ondragend fires
    ↓
ThreadManager.handleDragEnd(event)
```

### Why This Broke
The `ThreadCardTemplates` module was introduced to centralize card rendering, but when it was created, the drag attributes were inadvertently omitted from the template functions. The old inline fallback code in `thread-manager-ui.js` had them, but it's never reached because `ThreadCardTemplates` is now always available.

## Status
✅ **FIXED** - Drag-and-drop functionality restored for all thread info cards

## Last Modified
2025-11-22 - Added draggable attributes to compactCard() and fullCard() templates
