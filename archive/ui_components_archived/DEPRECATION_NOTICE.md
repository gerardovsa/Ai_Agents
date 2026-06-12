# Deprecation Notice: `UI/components_ARCHIVED/`

**Date archived at this location:** June 11, 2026
**Status:** ARCHIVED — superseded by components in `UI/business-ai-platform-v2.html`

---

## What this directory contains

5 historical frontend component files (97K total). Of these, **2 are 100% dead code** (see below).

| File | Size | Type | Status |
|---|---:|---|---|
| `AcceptSharePage.jsx` | 15K | JSX | **Dead code** (see note) |
| `ThreadSharingModal.jsx` | 21K | JSX | **Dead code** (see note) |
| `confirmation-bubble.js` | 18K | vanilla JS | Superseded by current implementation |
| `feedback-area.js` | 13K | vanilla JS | Superseded by current implementation |
| `feedback-area-new.js` | 30K | vanilla JS | Superseded by current implementation |

## The 2 JSX files are 100% dead code

The current SPA (`UI/business-ai-platform-v2.html`) is a **vanilla JavaScript single-page application with no build step** (see `CLAUDE.md` §2 and `package.json` — only `three` + `manifold-3d` are listed, with no Babel/JSX transform).

The two `.jsx` files (`AcceptSharePage.jsx`, `ThreadSharingModal.jsx`) cannot be loaded by the current SPA:

- There is no JSX compiler in the project.
- There is no `import` statement that references them anywhere in the live code.
- The `UI/` directory contains only `.html`, `.css`, and `.js` files — no other `.jsx` exists.

These files are evidence of an abandoned React/Preact experiment. They are preserved here for historical reference only.

## Why it was moved

Historical components were living under `UI/components_ARCHIVED/`. `UI/` is for live code. They were moved under the top-level `archive/` namespace during the June 11, 2026 cleanup round (row 45 of `ARCHIVE_CLEANUP_TRACKER.md`).

## What replaced it

The current components are inline in `UI/business-ai-platform-v2.html` (the single-file SPA pattern — all components live in that one file).

## How to recover

Preserved in `git log` history. To view the pre-move state:

```bash
git log --diff-filter=R -- archive/ui_components_archived/
```

## References

- **Cleanup row:** row 45 of `ARCHIVE_CLEANUP_TRACKER.md`
- **Findings doc:** `docs/agents/ROW_45_TOP_LEVEL_ARCHIVE_AUDIT.md`
- **Branch:** `cleanup/top-archive-audit` (commit `e977ace8`)
