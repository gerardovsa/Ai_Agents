# Deprecation Notice: `UI/ARCHIVE_OLD_UI_20251030_223356/`

**Date archived at this location:** June 11, 2026
**Originally created:** October 30, 2025
**Status:** ARCHIVED — superseded by `UI/business-ai-platform-v2.html`

---

## What this directory contains

12 historical files (1.8 MB total) representing older versions of the single-page application and ad-hoc test pages. None of them are referenced by any current code, build step, or runtime path.

| File | Size | Status |
|---|---:|---|
| `business-ai-platform-v2 copy.html` | 596K | Old SPA (pre-`_fixed` cleanup) |
| `stock_management_updated.html` | 604K | Old module SPA |
| `triple_agent.html` | 220K | Experimental 3-agent SPA variant |
| `transcript_processor.html` | 221K | Experimental transcript UI |
| `shopify_dashboard.html` | 66K | Old Shopify module page |
| `business-ai-platform.html` | 59K | Very old SPA (pre-V2) |
| `test-agent-visualization.html` | 13K | Test page |
| `integration-test.html` | 12K | Test page |
| `DEBUG_RENDERING_CHECKLIST.html` | 16K | Debug checklist doc |
| `grid-test.html` | 6K | Test page |
| `test-chat-simple.html` | 8K | Test page |
| `serve_ui.py` | 1.5K | Dev helper script |

## Why it was moved

These were historicals that had been living under `UI/` — `UI/` is for live code. They were moved under the top-level `archive/` namespace during the June 11, 2026 cleanup round (row 45 of `ARCHIVE_CLEANUP_TRACKER.md`).

## What replaced it

The current SPA is `UI/business-ai-platform-v2.html` (~1.5 MB).

## How to recover

These files are preserved in `git log` history. To view the pre-move state:

```bash
git log --diff-filter=R -- archive/ui_archives_20251030/
```

Or to see them at the original path:

```bash
git log --all -- 'UI/ARCHIVE_OLD_UI_20251030_223356/'
```

## References

- **Cleanup row:** row 45 of `ARCHIVE_CLEANUP_TRACKER.md`
- **Findings doc:** `docs/agents/ROW_45_TOP_LEVEL_ARCHIVE_AUDIT.md`
- **Branch:** `cleanup/top-archive-audit` (commit `e977ace8`)
