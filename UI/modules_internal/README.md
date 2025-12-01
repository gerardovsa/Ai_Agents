# Internal Modules Directory

## 🎯 Purpose

This directory contains **core platform components** that are always loaded and integral to the AI Agents Platform functionality.

---

## 📁 Directory Structure

```
modules_internal/
├── module_loader.js           ✅ Main module loading system
├── components/                🔧 Shared UI components
│   ├── user_auth.js          🔐 Authentication system
│   └── [other components]
├── sidebar-framework/         🚪 Universal sidebar system
├── synergy/                   🤝 Synergy dashboard components
├── thread-cards/              💬 Thread card system
├── automation-workflows/      ⚙️ Workflow automation UI
├── settings-sidebar/          ⚚ Settings interface
├── agents/                    🤖 AI agent management
└── [other internal modules]
```

---

## 🔧 What Goes Here

**Internal modules are:**

- Core platform functionality
- Always loaded on application startup
- Part of the platform's fundamental features
- Not dynamically loaded/unloaded
- No manifest.json required (usually)

**Examples:**
- Authentication system
- Sidebar framework
- Module loader itself
- Thread management
- Synergy dashboard
- Settings interface

---

## 🚫 What Does NOT Go Here

**External/business modules** should go in **`../modules_external/`** instead:

- Optional business features
- Dynamically loaded modules
- Integration modules (Shopify, Salesforce, etc.)
- Business-specific tools (Kanban, Quote Calculator, etc.)
- Requires manifest.json for discovery

---

## 📝 Naming Convention

- **Directory:** `modules_internal/` (clearly indicates core platform)
- **Old name:** `modules/` (renamed for clarity Nov 29, 2025)
- **Reason:** Avoid confusion with external modules

---

## 🔗 Related Directories

- **`../modules_external/`** - Business/optional modules
- **`../../frontend/modules_ARCHIVED/`** - Old unused code (archived)

---

## 📚 Documentation

See `MODULE_CLEANUP_REORGANIZATION_NOV29.md` for complete reorganization details.

---

**Last Updated:** November 29, 2025  
**Status:** ✅ Active Core Platform Directory
