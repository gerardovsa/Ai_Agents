# CSS Extractor - Working with Dynamic Elements

**Created:** November 22, 2025  
**Issue:** Stub HTML elements showing instead of actual rendered content  
**Solution:** Use "Rescan DOM" after dynamic content loads

---

## The Problem

When you first open the CSS Extractor, it shows stub/placeholder HTML because:
- JavaScript hasn't finished creating the dynamic UI yet
- The initial tree scan happens before elements like message bubbles are rendered
- The tool only sees the empty container elements, not the content inside

## The Solution: "Rescan DOM" Button

### ✨ New Feature Added

**Button:** `Rescan DOM` (🔄 sync icon)  
**Location:** CSS Extract tab, first row of controls  
**Purpose:** Rebuild the element tree AFTER JavaScript creates dynamic content

---

## How to Extract CSS from Dynamic Elements

### Workflow 1: Rescan After Loading (Recommended)

```
1. Open your application normally
2. Wait for dynamic content to load (messages, panels, etc.)
3. Open Debug Menu (🐛) → CSS Extract tab
4. Click "Rescan DOM" button
5. Now the tree shows REAL elements, not stubs
6. Select elements using checkboxes or Inspector
7. Extract CSS
```

### Workflow 2: Inspector Mode (Easiest)

```
1. Open Debug Menu → CSS Extract
2. Click "Enable Inspector"
3. Click on any visible element on the page
4. Element is automatically selected
5. CSS appears in right panel
6. No need to use tree view at all!
```

### Workflow 3: Trigger Action First

```
1. Perform action that creates elements:
   - Send a chat message
   - Open a modal
   - Click a button that shows content
2. Open CSS Extractor
3. Click "Rescan DOM"
4. Select the newly created elements
5. Extract CSS
```

---

## Understanding Tree Depth

### Default Behavior
- **Initial scan:** Max depth = 5 levels
- **After rescan:** Max depth = 6 levels (shows deeper nested elements)

### Why Depth Matters
```
Body
└─ Main Container (depth 1)
   └─ Chat Panel (depth 2)
      └─ Messages Container (depth 3)
         └─ Message Bubble (depth 4)
            └─ Message Text (depth 5)
               └─ Formatting Span (depth 6) ← Only visible after rescan
```

### When to Increase Depth
If you still don't see deeply nested elements after rescanning:
1. Open browser console
2. Type: `CSSExtractor.buildElementTree(10)` (or any number)
3. Press Enter
4. Tree rebuilds with custom depth

---

## Common Dynamic Elements in Your App

### Prime AI Chat Panel
**Container:** `#ai-chat-panel`  
**Dynamic Elements:**
- `.ai-message` - Message containers
- `.ai-message-bubble` - Message bubbles
- `.ai-message-content` - Message text
- `.thinking-bubble` - AI thinking indicator
- `.tool-bubble` - Tool execution displays

**How to Extract:**
```
1. Send a message in Prime chat
2. Open CSS Extractor
3. Click "Rescan DOM"
4. Look for #ai-chat-panel in tree
5. Check boxes for message elements
6. Extract CSS
```

### Agent Columns
**Dynamic Elements:**
- `.agent-column` - Agent containers
- `.agent-message` - Agent messages
- `.agent-message-bubble` - Agent bubbles
- `.no-thread-message` - Placeholder text

**How to Extract:**
```
1. Load agents (they auto-load)
2. Open CSS Extractor
3. Rescan DOM
4. Select agent-* elements
5. Extract CSS
```

### Thread Cards
**Dynamic Elements:**
- `.thread-card` - Thread list items
- `.thread-title` - Thread titles
- `.thread-indicator` - Message counts
- `.thread-actions` - Action buttons

**How to Extract:**
```
1. Open thread sidebar
2. CSS Extractor → Rescan DOM
3. Select .thread-card elements
4. Extract CSS
```

---

## Pro Tips for Dynamic Content

### Tip 1: Use Inspector for Visible Elements
Don't bother with the tree if you can see it on screen:
- Click "Enable Inspector"
- Click the element visually
- Done!

### Tip 2: Rescan Multiple Times
If content loads in stages:
```
1. Rescan after initial load
2. Trigger more content (scroll, click, etc.)
3. Rescan again
4. Tree shows all elements from both scans
```

### Tip 3: Select Parent Containers
Instead of selecting 50 message bubbles individually:
```
1. Find the parent container (e.g., #ai-chat-panel)
2. Select just the parent
3. CSS shows all inherited styles
4. Clean up in post-processing
```

### Tip 4: Target Specific Classes
After rescanning, use browser Find (Ctrl+F) in the tree:
```
1. Press Ctrl+F
2. Search for class name (e.g., "message-bubble")
3. Browser highlights matches in tree
4. Check those specific elements
```

### Tip 5: Compare Before/After Rescan
```
1. Take screenshot of tree before rescan (stub elements)
2. Click Rescan DOM
3. Take screenshot after rescan (real elements)
4. See the difference!
```

---

## Troubleshooting

### Problem: Still seeing stub elements after rescan
**Cause:** Content hasn't loaded yet  
**Solution:**
- Wait a few more seconds
- Trigger the action that creates content
- Check browser console for JavaScript errors
- Try Inspector mode instead

### Problem: Tree is overwhelming (too many elements)
**Solution:**
- Use Inspector mode (click elements visually)
- Use "Select All Visible" then deselect unwanted
- Search within tree using browser Find (Ctrl+F)

### Problem: Can't find specific element in tree
**Solution:**
- Use Inspector to click it directly
- Increase tree depth: `CSSExtractor.buildElementTree(15)`
- Check if element is hidden (display: none)

### Problem: Rescan button doesn't do anything
**Check:**
- Browser console for errors
- Element tree should flash/reload
- Console should show: `[CSS EXTRACTOR] Rescanning DOM...`

---

## Technical Details

### What Rescan Does
```javascript
rescanDOM() {
    console.log('[CSS EXTRACTOR] Rescanning DOM...');
    this.buildElementTree(6); // Increased depth
    console.log('[CSS EXTRACTOR] DOM rescan complete');
}
```

### Elements Skipped During Scan
- `#debug-sidebar` - The debug menu itself
- `#css-highlight-overlay` - The inspector highlight
- Any element with class `debug-sidebar`

### Tree Building Logic
```javascript
buildTreeRecursive(element, depth, maxDepth) {
    if (depth > maxDepth) return ''; // Stop at max depth
    if (element.id === 'debug-sidebar') return ''; // Skip debug UI
    // ... build tree recursively
}
```

---

## Example: Extract Chat Message Styles

### Step-by-Step Example

**Goal:** Extract CSS for user and AI message bubbles

```
Step 1: Prepare
- Open your app
- Send a test message as user
- Wait for AI response
- Now you have both message types visible

Step 2: Open Extractor
- Click bug icon (🐛)
- Click "CSS Extract" tab
- You see stub elements in tree

Step 3: Rescan
- Click "Rescan DOM" button
- Tree rebuilds with real elements
- Console shows: "Rescanning DOM..."

Step 4: Find Messages
- Scroll tree to find #ai-chat-panel
- Expand it to see children
- Look for .ai-message elements

Step 5: Select Elements
Option A - Use tree:
  - Check box for user message
  - Check box for AI message
Option B - Use Inspector:
  - Click "Enable Inspector"
  - Click user message bubble
  - Click again to activate Inspector
  - Click AI message bubble

Step 6: Review CSS
- Right panel shows extracted styles
- See both user and AI message CSS
- Properties are organized by selector

Step 7: Export
- Click "Copy CSS" → Clipboard
- Or "Export CSS" → Download file
- Use in your consolidated stylesheet
```

### Expected Output
```css
/* Extracted CSS from Selected Elements */
/* Generated: 11/22/2025, 3:45:12 PM */
/* Total Elements: 2 */

/* .ai-message.user */
.ai-message.user {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 16px;
}

/* .ai-message.assistant */
.ai-message.assistant {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 16px;
}
```

---

## Quick Reference

| Button | Purpose | When to Use |
|--------|---------|-------------|
| **Enable Inspector** | Click elements on page | Fastest for visible elements |
| **Rescan DOM** | Rebuild tree with live elements | After dynamic content loads |
| **Select All Visible** | Grab all visible elements | Bulk extraction |
| **Deselect All** | Clear selections | Start over |
| **Copy CSS** | Copy to clipboard | Quick sharing |
| **Export CSS** | Download .css file | Save to project |
| **Clear** | Reset everything | Start fresh |

---

## Summary

**The key to extracting CSS from dynamic elements:**

1. ✅ Let the page load completely
2. ✅ Trigger any actions that create content
3. ✅ Click "Rescan DOM" to see real elements
4. ✅ Select elements using tree or Inspector
5. ✅ Extract and export CSS

**Don't forget:** Inspector mode bypasses the need for tree scanning entirely!

---

**Last Updated:** November 22, 2025  
**Version:** 1.1.0  
**Status:** Enhanced with Rescan DOM feature
