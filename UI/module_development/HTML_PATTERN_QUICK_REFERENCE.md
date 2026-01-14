# Module HTML Pattern - Quick Reference

**Last Updated:** November 28, 2025  
**For:** Module Developers

---

## 🎯 Two Patterns, One Choice

Every module must choose **ONE** of these UI rendering patterns:

---

## Pattern 1: JavaScript-Generated UI ⚡

**Use when:** Dynamic, interactive, data-driven UIs

### manifest.json
```json
{
  "id": "my-module",
  "name": "My Module",
  "js_file": "my-module.js",
  "css_file": "my-module.css"
  // NO html_file field!
}
```

### my-module.js
```javascript
class MyModule extends BaseModule {
    async initialize() {
        await this.createModuleStructure();  // Create UI here
        await this.loadData();
        this.render();
    }

    async createModuleStructure() {
        const container = this.getContainer();
        
        // Build UI with template literals
        container.innerHTML = `
            <div class="my-module-container">
                <h2>My Module</h2>
                <div id="content"></div>
            </div>
        `;
        
        this.setupEventListeners();
    }
}
```

**Examples:** communication-hub, automation-workflows

---

## Pattern 2: HTML Template File 📄

**Use when:** Static layouts, designer-friendly

### manifest.json
```json
{
  "id": "my-module",
  "name": "My Module",
  "html_file": "my-module.html",  // ← Specify HTML file
  "js_file": "my-module.js",
  "css_file": "my-module.css"
}
```

### my-module.html
```html
<div class="my-module-container">
    <h2>My Module</h2>
    <div id="content"></div>
</div>
```

### my-module.js
```javascript
class MyModule extends BaseModule {
    async initialize() {
        // HTML already loaded!
        this.setupEventListeners();
        await this.loadData();
        this.render();
    }

    render() {
        // Populate existing HTML
        document.getElementById('content').innerHTML = this.data;
    }
}
```

**Examples:** inhouse-kanban, stock-management

---

## Decision Tree

```
Does your module have...
├─ Frequently changing UI based on state?
│  └─ YES → Pattern 1 (JavaScript)
├─ Multiple dynamic tabs/views?
│  └─ YES → Pattern 1 (JavaScript)
├─ Real-time updates (chat, notifications)?
│  └─ YES → Pattern 1 (JavaScript)
├─ Static form/settings layout?
│  └─ YES → Pattern 2 (HTML file)
└─ Designer needs to edit layout?
   └─ YES → Pattern 2 (HTML file)
```

---

## Checklist

### Pattern 1 (JavaScript):
- [ ] Remove `html_file` from manifest
- [ ] Create `createModuleStructure()` method
- [ ] Use template literals for HTML
- [ ] Call in `initialize()`

### Pattern 2 (HTML File):
- [ ] Add `html_file: "name.html"` to manifest
- [ ] Create separate `.html` file
- [ ] Use semantic HTML with IDs
- [ ] Reference elements by ID in JS

---

## Common Mistakes

❌ **Adding html_file for JavaScript-generated module**
```json
{
  "html_file": "my-module.html"  // ← Module loader will try to fetch this!
}
```

❌ **Forgetting to create HTML in JavaScript**
```javascript
async initialize() {
    // No createModuleStructure() call - UI never appears!
    await this.loadData();
}
```

❌ **Recreating HTML when template exists**
```javascript
// Don't do this if you have an HTML file:
render() {
    container.innerHTML = `<div>...</div>`;  // Wipes out HTML template!
}
```

---

## Full Documentation

See: `UI/module_development/MODULE_BEST_PRACTICES.md` → "HTML Patterns: Two Approaches"

---

**Quick Tip:** When in doubt, check existing modules:
- JavaScript pattern → `communication-hub/`
- HTML pattern → `inhouse-kanban/`
