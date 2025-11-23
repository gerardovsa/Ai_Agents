# CSS Extractor Tool - Complete Guide

**Created:** November 22, 2025  
**Location:** Debug Menu → CSS Extract Tab  
**Purpose:** Extract computed CSS from rendered UI elements to consolidate fragmented styles

---

## Overview

The CSS Extractor is an interactive tool built into the Debug Menu that allows you to:
1. **Visually select** HTML elements from your rendered UI
2. **View their computed CSS** styles in real-time
3. **Export clean, consolidated CSS** to replace fragmented styles

This tool solves the problem of piecemeal CSS scattered across multiple files by showing you the **actual rendered styles** that the browser uses.

---

## Features

### 1. Interactive Inspector Mode
- Click **"Enable Inspector"** to activate crosshair cursor
- Hover over any element to see it highlighted with blue overlay
- Click to select/deselect elements
- Auto-stops after each selection (click button again to continue)

### 2. HTML Tree View (Left Panel)
- **Hierarchical tree** of all page elements (max depth: 3 levels)
- **Checkboxes** for easy selection
- **Visual indicators:**
  - Blue highlight = selected element
  - Orange text = element ID (#id)
  - Purple text = CSS classes (.class)
- **Auto-skips** debug sidebar and hidden elements

### 3. CSS Output (Right Panel)
- **Real-time display** of computed styles
- **Organized by element** with clear comments
- **Filtered properties** - only relevant CSS (no browser defaults)
- **Live counter** shows number of selected elements

### 4. Bulk Actions
- **Select All Visible** - Grabs all elements in main content area
- **Deselect All** - Clear all selections
- **Copy CSS** - Copy to clipboard
- **Export CSS** - Download as `.css` file
- **Clear** - Reset everything

---

## How to Use

### Step 1: Open Debug Menu
1. Look for the **bug icon** (🐛) in your UI (usually top-right corner)
2. Click to open the debug sidebar
3. Click the **"CSS Extract"** tab (🎨 palette icon)

### Step 2: Select Elements

**Method A: Inspector Mode (Recommended)**
```
1. Click "Enable Inspector" button
2. Your cursor becomes a crosshair
3. Hover over elements you want to extract
4. Click to select (blue highlight appears)
5. Repeat for other elements
```

**Method B: Tree View**
```
1. Scroll through the HTML tree on the left
2. Check boxes next to elements you want
3. Selected elements turn blue
```

**Method C: Bulk Selection**
```
1. Click "Select All Visible" 
2. Deselect unwanted elements
```

### Step 3: Review CSS
- **Right panel** shows extracted CSS automatically
- Each element gets its own section with comments
- Properties are organized and formatted

### Step 4: Export
```
Option 1: Click "Copy CSS" to copy to clipboard
Option 2: Click "Export CSS" to download file
```

---

## Understanding the Output

### Example Output Format:
```css
/* Extracted CSS from Selected Elements */
/* Generated: 11/22/2025, 10:30:45 AM */
/* Total Elements: 3 */

/* #main-header */
#main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    background-color: rgb(30, 30, 30);
    border-bottom: 1px solid rgb(60, 60, 60);
}

/* .message-bubble.user */
.message-bubble.user {
    background-color: rgb(59, 130, 246);
    color: rgb(255, 255, 255);
    padding: 12px 16px;
    border-radius: 12px;
    max-width: 70%;
}
```

### What's Included:
✅ **Layout properties** (display, position, flex, grid)  
✅ **Spacing** (margin, padding)  
✅ **Typography** (font-family, font-size, line-height)  
✅ **Colors** (color, background, borders)  
✅ **Effects** (box-shadow, opacity, transform)  

### What's Excluded:
❌ Browser defaults (like `margin: 0px`)  
❌ Inherited values that match parent  
❌ Auto-calculated values (like `width: auto`)  
❌ Non-visual properties  

---

## Use Cases

### 1. CSS Consolidation (Your Goal)
**Problem:** CSS scattered across multiple files  
**Solution:**
```
1. Select all elements in a specific area (e.g., chat interface)
2. Export CSS
3. Review and merge duplicate properties
4. Replace fragmented CSS in your codebase
```

### 2. Component Styling
**Problem:** Need to extract styles for a reusable component  
**Solution:**
```
1. Use Inspector to select component elements
2. Export CSS
3. Create new component stylesheet
4. Remove inline styles from HTML
```

### 3. Debug Style Issues
**Problem:** Element not looking right  
**Solution:**
```
1. Select the problematic element
2. Review computed styles in real-time
3. See exactly what the browser is rendering
4. Compare with your CSS files
```

### 4. Create Style Guide
**Problem:** Need to document existing styles  
**Solution:**
```
1. Select representative elements (buttons, headers, cards)
2. Export CSS
3. Use as basis for design system documentation
```

---

## Tips & Tricks

### Tip 1: Focus on Specific Areas
Don't select everything at once. Instead:
- Extract **chat interface** styles separately
- Extract **header/navigation** separately
- Extract **sidebar** separately
- Merge later in organized fashion

### Tip 2: Use the Tree View for Precision
The inspector is fast, but the tree view lets you:
- See the exact hierarchy
- Select hidden elements
- Avoid accidentally clicking wrong elements

### Tip 3: Compare Before/After
1. Extract current styles → Save as `before.css`
2. Consolidate and clean → Save as `after.css`
3. Use a diff tool to see what changed

### Tip 4: Filter by Selector Type
After exporting, you can organize by:
- **IDs** (`#` selectors) - Unique elements
- **Classes** (`.` selectors) - Reusable styles
- **Tags** (`div`, `span`) - Base styles

### Tip 5: Incremental Replacement
Don't replace all CSS at once:
1. Start with one component (e.g., message bubbles)
2. Extract, clean, and test
3. Move to next component
4. Repeat until all CSS is consolidated

---

## Common Workflows

### Workflow 1: Clean Up Message Styles
```
1. Open CSS Extract tab
2. Click "Enable Inspector"
3. Click on a user message bubble
4. Click on an AI message bubble
5. Click on a system message
6. Review extracted CSS
7. Copy to clipboard
8. Paste into message-styles.css
9. Remove inline styles from HTML
10. Test in browser
```

### Workflow 2: Extract Entire Chat Interface
```
1. Open CSS Extract tab
2. Scroll tree view to find #chat-container
3. Check the box
4. Check boxes for child elements:
   - .message-list
   - .message-bubble
   - .input-area
5. Click "Export CSS"
6. Save as chat-interface.css
7. Replace existing chat CSS
```

### Workflow 3: Debug Why Element Looks Wrong
```
1. Open CSS Extract tab
2. Use Inspector to select problem element
3. Review computed styles in right panel
4. Look for unexpected values
5. Compare with your CSS files
6. Fix in source CSS
7. Refresh and verify
```

---

## Technical Details

### What is "Computed CSS"?
- **Definition:** The final CSS values the browser actually uses after resolving inheritance, specificity, and cascading
- **Why it matters:** Shows you what's REALLY rendering, not just what's in your CSS files
- **Example:**
  ```css
  /* Your CSS */
  .button { padding: 1rem; }
  
  /* Computed CSS */
  .button { padding: 16px; } /* Converted to pixels */
  ```

### Selector Generation
The tool generates selectors in this order:
1. **ID** if element has one (`#my-element`)
2. **Tag + Classes** if no ID (`div.message.user`)
3. **:nth-child()** if needed for uniqueness

### Property Filtering
Extracts ~40 most relevant CSS properties:
- **Layout:** display, position, flex, grid
- **Spacing:** margin, padding
- **Typography:** font-*, text-*, line-height
- **Visual:** color, background, border, shadow
- **Misc:** opacity, z-index, overflow, cursor

Skips:
- Default values (0px margins)
- Browser-specific prefixes
- Computed-only properties (scrollHeight)

---

## Limitations & Notes

### Known Limitations:
1. **Max tree depth: 3 levels** - Prevents overwhelming display
2. **No pseudo-elements** - Can't extract ::before, ::after styles
3. **No media queries** - Only extracts current viewport styles
4. **No animations** - Keyframes not included

### Performance Notes:
- Selecting 100+ elements may slow down display
- Use "Select All Visible" carefully on large pages
- Export is instantaneous regardless of selection size

### Browser Compatibility:
- ✅ Chrome/Edge (tested)
- ✅ Firefox (should work)
- ⚠️ Safari (may need testing)

---

## Troubleshooting

### Problem: "Element not found" error
**Solution:** Element was removed from DOM after selection. Click "Clear" and reselect.

### Problem: CSS output is empty
**Solution:** Make sure elements are actually selected (blue highlight). Try "Select All Visible".

### Problem: Inspector not highlighting correctly
**Solution:** 
1. Click "Enable Inspector" again to restart
2. Make sure debug sidebar isn't covering elements
3. Try using tree view instead

### Problem: Exported CSS doesn't match rendered styles
**Solution:** 
1. Make sure no dynamic styles are being applied via JavaScript
2. Check if styles are applied conditionally (hover, focus, etc.)
3. Use browser DevTools to compare

### Problem: Too much CSS extracted
**Solution:** 
1. Deselect elements you don't need
2. Use tree view to select more precisely
3. Extract in smaller chunks (one component at a time)

---

## Next Steps After Extraction

### 1. Organize Extracted CSS
```css
/* Group by component */
/* ==================== */
/* HEADER STYLES */
/* ==================== */
#main-header { ... }

/* ==================== */
/* MESSAGE STYLES */
/* ==================== */
.message-bubble { ... }
```

### 2. Remove Duplicates
Look for repeated property values across selectors and consolidate:
```css
/* Before */
.button { padding: 12px 24px; }
.link { padding: 12px 24px; }

/* After */
.button, .link { padding: 12px 24px; }
```

### 3. Use CSS Variables
Replace repeated values with variables:
```css
:root {
    --primary-color: rgb(59, 130, 246);
    --spacing-md: 16px;
}

.button {
    background-color: var(--primary-color);
    padding: var(--spacing-md);
}
```

### 4. Test Thoroughly
- ✅ Check all breakpoints (mobile, tablet, desktop)
- ✅ Test all states (hover, focus, active)
- ✅ Verify in different browsers
- ✅ Check with different themes (light/dark)

---

## Support & Feedback

**Found a bug?** Check browser console for error messages  
**Need help?** Review this guide or check the tool's tooltips  
**Want a feature?** Note it and discuss with the team

---

**Last Updated:** November 22, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅
