# CSS Extractor - Quick Start Guide

**🎯 Goal:** Extract computed CSS from your UI to replace fragmented styles

---

## ⚡ Quick Steps

### 1. Open the Tool
```
Bug icon (🐛) → Debug Sidebar → CSS Extract Tab (🎨)
```

### 2. Select Elements
**Option A:** Click "Enable Inspector" → Click elements on page  
**Option B:** Use checkboxes in left panel tree view  
**Option C:** Click "Select All Visible"

### 3. Review CSS
Right panel shows extracted styles in real-time

### 4. Export
- **Copy CSS** → Clipboard
- **Export CSS** → Download file

---

## 🎮 Controls

| Button | Function |
|--------|----------|
| **Enable Inspector** | Interactive element picker (crosshair cursor) |
| **Select All Visible** | Grab all elements in main content |
| **Deselect All** | Clear all selections |
| **Copy CSS** | Copy to clipboard |
| **Export CSS** | Download `.css` file |
| **Clear** | Reset everything |

---

## 📊 Display Layout

```
┌─────────────────────────────────────────────────┐
│  [Controls: Inspector, Select All, Export...]   │
├─────────────────────┬───────────────────────────┤
│ HTML TREE           │ EXTRACTED CSS             │
│ (with checkboxes)   │ (live preview)            │
│                     │                           │
│ ☐ <div#app>         │ /* #app */                │
│   ☐ <header>        │ #app {                    │
│     ☑ <h1.title>    │   display: flex;          │
│   ☐ <main>          │   padding: 16px;          │
│     ☑ <div.chat>    │ }                         │
│                     │                           │
│ 2 elements selected │ /* .title */              │
│                     │ .title {                  │
│                     │   font-size: 24px;        │
│                     │   color: white;           │
│                     │ }                         │
└─────────────────────┴───────────────────────────┘
```

---

## 💡 Pro Tips

### 1. **Start Small**
Don't select 100 elements at once. Extract by component:
- Message bubbles → `message-styles.css`
- Header → `header-styles.css`
- Sidebar → `sidebar-styles.css`

### 2. **Use Inspector for Speed**
Fastest way to grab specific elements visually

### 3. **Use Tree for Precision**
When you need exact elements or hidden components

### 4. **Compare & Consolidate**
```
Extract → Review → Remove duplicates → Organize → Replace
```

---

## 🚀 Common Workflows

### Extract Chat Interface Styles
```
1. Enable Inspector
2. Click on user message bubble
3. Click on AI message bubble
4. Click on input box
5. Export CSS
6. Replace chat.css
```

### Clean Up Entire Section
```
1. Find section in tree view (e.g., #chat-container)
2. Check the box
3. Export CSS
4. Create new consolidated file
5. Remove old fragmented CSS
```

### Debug Why Element Looks Wrong
```
1. Use Inspector to select problem element
2. Review computed styles
3. Compare with your CSS files
4. Fix discrepancies
```

---

## ✅ What Gets Extracted

**Included:**
- Display & Layout (flex, grid, position)
- Spacing (margin, padding)
- Typography (font-size, line-height)
- Colors (color, background, border)
- Effects (shadow, opacity, transform)

**Excluded:**
- Browser defaults (`margin: 0px`)
- Auto values
- Inherited duplicates
- Non-visual properties

---

## 🔧 Output Format

```css
/* Extracted CSS from Selected Elements */
/* Generated: [timestamp] */
/* Total Elements: [count] */

/* [selector] */
[selector] {
    [property]: [value];
    [property]: [value];
}

/* [next selector] */
...
```

---

## ⚠️ Remember

- **Max tree depth: 3 levels** (keeps display manageable)
- **Inspector auto-stops** after each click (reactivate to continue)
- **Debug sidebar excluded** from extraction automatically
- **Computed values shown** (e.g., `1rem` becomes `16px`)

---

## 🎯 Your Goal: CSS Consolidation

### Before (Fragmented):
```
styles/header.css → 50 lines
styles/chat.css → 120 lines
inline styles in HTML → 200+ lines
random.css → 80 lines
```

### After (Consolidated):
```
Extract → Review → Clean → Organize

components/chat-interface.css → 150 clean lines
components/header.css → 40 clean lines
components/sidebar.css → 60 clean lines
```

**Result:** Maintainable, organized, DRY CSS! 🎉

---

**Quick Access:** Bug Icon (🐛) → CSS Extract Tab (🎨)

**Full Guide:** See `CSS_EXTRACTOR_GUIDE.md` for detailed documentation
