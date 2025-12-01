# Archived Modules Directory

## ⚠️ ARCHIVED - NOT IN USE

This directory contains **legacy code that is no longer used** by the AI Agents Platform.

---

## 📋 What's Here

```
modules_ARCHIVED/
└── module_loader.js           ❌ OLD - Not used anymore
```

---

## 🚫 Why Archived?

The old `frontend/modules/module_loader.js` was **replaced** by the new active loader:

- **Active Loader:** `UI/modules_internal/module_loader.js`
- **Archived Loader:** `frontend/modules_ARCHIVED/module_loader.js`

**Reason for replacement:**
- Old loader only scanned backend API
- New loader scans both backend API AND direct file paths
- New loader has better error handling
- New loader supports multiple module directories

---

## 📅 Timeline

- **Original:** Created November 25, 2025
- **Replacement:** New loader created November 26-29, 2025
- **Archived:** November 29, 2025

---

## 🔄 Reorganization (November 29, 2025)

The module system was reorganized for clarity:

### Old Structure (Confusing):
```
frontend/modules/              ❌ Unused
UI/modules/                    ⚠️ Internal components (unclear name)
UI/external/modules/           ⚠️ Business modules (unclear name)
```

### New Structure (Clear):
```
frontend/modules_ARCHIVED/     📦 Archived (clearly marked)
UI/modules_internal/           🔧 Core platform (clear purpose)
UI/modules_external/           📦 Business modules (clear purpose)
```

---

## ⚠️ Do NOT Use This Code

This code is **archived for reference only**.

**DO NOT:**
- Import files from this directory
- Copy code from here without checking current version
- Assume this code works with current system

**DO:**
- Use `UI/modules_internal/module_loader.js` instead
- Check current documentation
- Ask before using archived code

---

## 📚 Current Documentation

See these files for active module system:

- `MODULE_CLEANUP_REORGANIZATION_NOV29.md` - Reorganization guide
- `UI/modules_internal/README.md` - Internal modules guide
- `UI/modules_external/README.md` - External modules guide
- `MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md` - Full architecture

---

## 🗑️ Future Plans

This directory may be **deleted** in future cleanup if:
- No longer needed for reference
- All code fully migrated
- Team confirms safe to remove

---

**Archived:** November 29, 2025  
**Status:** ❌ NOT IN USE - Reference Only  
**Active Code:** `UI/modules_internal/module_loader.js`
