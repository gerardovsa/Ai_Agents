# Deprecation Notice: `UI/_ARCHIVED_NOV25/`

**Date archived at this location:** June 11, 2026
**Originally archived:** November 25, 2025
**Status:** ARCHIVED — superseded by the self-registering module system

---

## What this directory contains

28 historical frontend files (1 README + 5 .js + 11 .md + 6 .css, with 2 subdirs: `js/` and `module_builder/`). These were the old module loading/management code that was frozen on Nov 25, 2025 when the project migrated to a new self-registering module system.

| Path | Type | Note |
|---|---|---|
| `README.md` | .md | Original archive README (preserved verbatim) |
| `js/module-loader.js` | .js | Old manual module loader |
| `js/module-manager.js` | .js | Old manual module manager |
| `js/module-base.js` | .js | Old base class (frozen Nov 25, 2025) |
| `js/module-base copy.js` | .js | Manual backup of the old base class |
| `js/ui-builder.js` | .js | Old UI builder |
| `module_builder/` (11 .md) | .md | Module builder documentation archive |
| `module_builder/templates/` (4 dirs) | .css + .js | Module template scaffolding (dashboard, form, full-featured, minimal) |
| `module_builder/toolkit/` | .css + .js | Design tokens, modal system, UI components |

## What replaced it (per the original Nov 25, 2025 archive README)

> "The new system uses a unified ModuleRegistry pattern (like the tool registry) with automatic credential discovery and dynamic loading."
>
> **New system location:**
> - Backend: `AI_infrastructure/core/module_registry.py`
> - Routes: `AI_infrastructure/routes/module_routes.py`
> - Frontend: `frontend/modules/module_loader.js`

> **Migration path:** Modules are now located in `frontend/modules/<module_name>/` with `manifest.json` defining everything.

> See `MODULE_SYSTEM_ARCHITECTURE_COMPLETE.md` for full documentation.

The original archive README is preserved verbatim in this directory as `README.md`.

## Why it was moved

`UI/_ARCHIVED_NOV25/` was an archive directory living at `UI/` level (the live-code root). The convention established by row 45 of `ARCHIVE_CLEANUP_TRACKER.md` is to keep all archive subdirs under the top-level `archive/` namespace. The directory was renamed to `archive/ui_archives_20251125/` to match the sibling moves from row 45 followup:

- `UI/ARCHIVE_OLD_UI_20251030_223356/` → `archive/ui_archives_20251030/`
- `UI/components_ARCHIVED/` → `archive/ui_components_archived/`

## Important: the live `UI/js/module-base.js` is NOT this one

A current, live `UI/js/module-base.js` (12K, modified 2025-11-25) **also exists** at the parent `UI/js/` level. It is the post-Nov-25 implementation and is **not affected by this move**. The SPA `business-ai-platform-v2.html` references `js/module-base.js` (line 838, currently in a commented-out `<script>` tag) — this points to the **current** file, not the archived one.

## How to recover

Preserved in `git log` history. To view the pre-move state:

```bash
git log --diff-filter=R -- archive/ui_archives_20251125/
```

Or to see the original Nov 25, 2025 archive (the prior `UI/_ARCHIVED_NOV25/` path):

```bash
git log --all -- 'UI/_ARCHIVED_NOV25/'
```

## References

- **Cleanup row:** row 45 of `ARCHIVE_CLEANUP_TRACKER.md` (followup batch D)
- **Findings doc:** `docs/agents/ROW_45_TOP_LEVEL_ARCHIVE_AUDIT.md`
- **Branch:** `cleanup/top-archive-audit` (followup commit after `2038b8f8`)
- **Originally archived:** Nov 25, 2025 per original `README.md`
