# Row 45 — Top-Level Archive Directories Audit

**Date:** 2026-06-11
**Scope:** `meta` — read-only audit, no file moves
**Author:** Claude (cleanup session, branch `cleanup/top-archive-audit`)

---

## 1. Scope

Per `ARCHIVE_CLEANUP_TRACKER.md` row 45:
> "Top-level archive directories audit | meta | ARCHIVE_OCT30_2025/, archive/, _ARCHIVED_NOV25/, UI/ARCHIVE_OLD_UI_20251030_223356/, UI/components_ARCHIVED/. For each: confirm contents are truly historical; consolidate where appropriate."

User instruction for this row: **read-only, no moves** (in contrast to rows 46/47 which executed moves).

---

## 2. Inventory

`_ARCHIVED_NOV25/` does not exist in the worktree. It was either renamed or never created in the cleanup round that ran before this one. The remaining 4 directories were audited.

### 2.1 `archive/` (the big one)

| Subdirectory | Files | Size | Type | Verdict |
|---|---:|---:|---|---|
| `analysis_reports/` | 21 | 144K | .md analysis reports | **Keep** — well-categorized historical |
| `calculator_history/` | 4 | 64K | .md calculator fix logs | **Keep** — domain-specific |
| `database_utilities/` | 53 | 360K | .py column-adding / migration scripts | **Keep** — useful git archaeology |
| `deployment_scripts/` | 11 | 64K | .ps1 / .py deployment helpers | **Keep** — historical |
| `deprecated/` | 2 | 48K | `DEPRECATION_NOTICE.md` + 1 .py | **Keep** — textbook deprecation bundle |
| `documentation/` | 290 | 4.3M | flat .md historicals (Oct 30 2025 cleanup) | **Keep** — distinct from `docs/archive/` (see §4) |
| `documentation_20251030_222325/` | 21 | 308K | .md agent_routes refactor docs | **Keep** — single-topic V3→V4 historical |
| `old_scripts_20251030_222325/` | 15 | 83K | .py DB inspection scripts | **Keep** — well-bounded |
| `routes/` | 3 | 532K | `agent_routes_OLD_MONOLITHIC.py` + v2 + v3 | **Keep** — pre-V4 route files |
| `test_scripts/` | 186 | 1.3M | .py + .ps1 historical tests | **Keep** — large but harmless |
| `timelines_and_reports/` | 21 | 29M | HTML dashboards + git log dumps | **Keep but flag bloat** (see §3) |
| `unused_routes_dec7/` | 1 | 24K | `microsoft_auth_routes.py` | **Keep** — single small file |
| `xero/` | 8 | 76K | Xero integration fix logs | **Keep** — domain-specific |
| **Total** | **636** | **~40M** | | |

### 2.2 `ARCHIVE_OCT30_2025/`

| Subdirectory | Files | Size | Type | Verdict |
|---|---:|---:|---|---|
| `agent_routes_docs/` | 9 | 92K | .md V4 / stock module fix logs | **Keep** — Oct 30 2025 snapshot |
| `calculator_docs/` | 2 | 20K | .md calculator integration | **Keep** |
| `test_scripts/` | 3 | 28K | .ps1 + .py deployment helpers | **Keep** |
| **Total** | **14** | **140K** | | |

Named for date (Oct 30 2025), well-bounded. This is a snapshot from one specific cleanup round, distinct from the ongoing `archive/` (which is a different lineage).

### 2.3 `UI/ARCHIVE_OLD_UI_20251030_223356/`

| File | Size | Type | Verdict |
|---|---:|---|---|
| `business-ai-platform-v2 copy.html` | 596K | old SPA (dated 2025-10-30) | **Archive** |
| `stock_management_updated.html` | 604K | old SPA | **Archive** |
| `triple_agent.html` | 220K | old SPA variant | **Archive** |
| `transcript_processor.html` | 221K | old SPA variant | **Archive** |
| `shopify_dashboard.html` | 66K | old module page | **Archive** |
| `business-ai-platform.html` | 59K | very old SPA | **Archive** |
| `test-agent-visualization.html` | 13K | test page | **Archive** |
| `integration-test.html` | 12K | test page | **Archive** |
| `DEBUG_RENDERING_CHECKLIST.html` | 16K | debug doc | **Archive** |
| `grid-test.html` | 6K | test page | **Archive** |
| `test-chat-simple.html` | 8K | test page | **Archive** |
| `serve_ui.py` | 1.5K | dev helper script | **Archive** |
| **Total** | **12** | **1.8M** | |

All 12 files are dated 2025-10-30 and are old SPA versions. The 4 large HTMLs (`business-ai-platform-v2 copy.html`, `stock_management_updated.html`, `triple_agent.html`, `transcript_processor.html`) total 1.6 MB and are clearly superseded by the current `UI/business-ai-platform-v2.html`.

**Note:** Location is unusual — these are historical UI files but live at `UI/` level, intermixed with current UI. The repo's convention for "historical stuff" is to put it under `archive/`. Moving them under `archive/ui_archives_20251030/` would consolidate them with the other archive subdirs.

### 2.4 `UI/components_ARCHIVED/`

| File | Size | Type | Verdict |
|---|---:|---|---|
| `AcceptSharePage.jsx` | 15K | JSX component | **Dead code** — see note |
| `ThreadSharingModal.jsx` | 21K | JSX component | **Dead code** — see note |
| `confirmation-bubble.js` | 18K | old component | **Archive** |
| `feedback-area-new.js` | 30K | old component variant | **Archive** |
| `feedback-area.js` | 13K | old component | **Archive** |
| **Total** | **5** | **97K** | |

**Important note on the JSX files:** The current SPA (`UI/business-ai-platform-v2.html`) is **vanilla JavaScript with no build step** (confirmed in `CLAUDE.md` §5 and `package.json` — only `three` + `manifold-3d` are listed, no Babel/JSX). JSX files cannot be loaded by the current SPA. The two `.jsx` files in this directory are **100% dead code** — they were either from an abandoned React/Preact attempt or were placeholders that never compiled.

The 3 `.js` files (`confirmation-bubble.js`, `feedback-area.js`, `feedback-area-new.js`) are vanilla JS. They were superseded by current implementations, but were at one point real code.

---

## 3. Bloat / consolidation candidates (NOT executed)

These are observations from the audit. Per the user's "no moves" instruction, **none of these were executed**. They are listed here so the user can decide on a follow-up row.

### 3.1 `archive/timelines_and_reports/` — 29 MB of mostly-unused static dashboards

| File | Size | Note |
|---|---:|---|
| `ai_agents_accurate_timeline.html` | **18.8 MB** | one-off static dashboard, single largest file in the repo |
| `git_full_stats.txt` | 2.7 MB | raw `git log` dump, can be regenerated |
| `git_detailed_log.txt` | 1.4 MB | same |
| `ai_agents_timeline.html` | 3.9 MB | another one-off dashboard |
| `combined_timeline_v3_ultra_detailed.html` | 1.0 MB | yet another dashboard |
| `master_timeline_all_projects.html` | 85K | dashboard |
| `combined_project_timeline.html` | 91K | dashboard |
| `project_gantt_chart.html` | 390K | dashboard |
| `combined_timeline_v2_detailed.html` | 371K | dashboard |
| `work_quote_dashboard.html` | 89K | dashboard (canonical) |
| `work_quote_dashboard copy.html` | 89K | **exact md5 duplicate** of the above |
| `focused_timeline_detailed copy.html` | 382K | has " copy" suffix, likely a duplicate of a now-missing original |
| `ai_agents_work_hours.html` | 55K | dashboard |
| `work_quote_report.html` | 5.5K | dashboard |
| `combined_project_timeline.py` | 22K | **generator** for one of the above |
| `detailed_size_comparison.py` | 5.4K | generator |
| `all_projects_summary.txt` | 1.9K | summary |
| `commits_by_date.txt` | 117B | empty stub |
| `git_commit_stats.txt` | 2.9K | git output |
| `git_contribution_analysis.txt` | 1.9K | git output |
| `DETAILED_WORK_TIMELINE.md` | 13K | the only `.md` — actual narrative |

**Verdict:** The dir is 29 MB but the durable value is the one 13K narrative .md and possibly the two .py generators. Everything else is regenerable static output.

**Potential savings:** ~28 MB if all `.html`/`.txt` dashboards were deleted. Risk: very low (none of them is referenced by any current code or doc — see §5).

### 3.2 `UI/ARCHIVE_OLD_UI_20251030_223356/` → `archive/ui_archives_20251030/`

The 12 files could be `git mv`'d to consolidate with the existing 13 archive/ subdirs. This is a pure location change, not a deletion. **Cost: low** (one `git mv` per file, plus updating 1 cross-reference in `CLAUDE.md`).

### 3.3 `UI/components_ARCHIVED/` → `archive/ui_components_archived/`

Same as 3.2 — pure location change. The 2 dead JSX files are particularly safe to relocate since they can't be imported by the current SPA anyway.

### 3.4 `work_quote_dashboard copy.html` (exact duplicate)

md5 `77b5481efd80751620825736a389d466` matches the canonical `work_quote_dashboard.html`. Could be renamed to a `_DUPLICATE_*` prefix or moved to `archive/duplicate_removals/`.

### 3.5 `commits_by_date.txt` (117 bytes)

The file is **117 bytes** — barely 2 lines. Looking at the size, it's likely a stub/empty placeholder. Worth deleting if confirmed empty.

---

## 4. Overlap with `docs/archive/` (row 47 result)

Row 47 created `docs/archive/` as a categorized archive of 253 `_ARCHIVED_*.md` files + 17 subdirs. The question for row 45 is: **does the existing top-level `archive/documentation/` overlap with `docs/archive/`?**

| Comparison | Count |
|---|---:|
| `archive/documentation/` .md basenames | 290 |
| `docs/archive/` `_ARCHIVED_*.md` basenames (after stripping prefix) | 253 |
| **Exact basename matches** (after stripping prefix) | **3** |

The 3 matches:
- `TABULATOR_INTEGRATION_COMPLETE.md`
- `TABULATOR_PREPARATION_GUIDE.md`
- `TABULATOR_QUICK_START.md`

**Interpretation:** The two archive trees are **mostly distinct** — they document different historical events from different eras:

- `archive/documentation/` is the **Oct 30 2025 cleanup's** flat archive. It contains fix logs and integration summaries from that era, with no category prefixes.
- `docs/archive/` is the **June 11 2026 cleanup's** categorized archive (row 47). The `_ARCHIVED_` prefix is uniform and the subdirs are categorized (e.g. `kanban/`, `tools/`, `google_workspace/`, etc.).

**Recommendation:** **Keep both.** Merging them would lose the lineage distinction. The 3 tabulator duplicates are not significant.

---

## 5. Cross-reference graph

**No code file imports from any `archive/` subdirectory.** The only matches in `grep` were:
- `UI/modules_internal/synergy/synergy-board-init.js:1800` — string literal `'Archive this session? You can restore it later from archived sessions.'` (UI text, not an import)
- `.github/AI_DOCUMENTATION_CONSOLIDATION_INSTRUCTIONS.md` — references `archive/` as the historical bucket (legitimate)
- `docs/agents/PER_FEATURE_CLEANUP_PROMPT.md` — references `archive/test_scripts/` as a valid destination (legitimate)
- `CLAUDE.md` line 139 — lists `archive/` and `ARCHIVE_OCT30_2025/` as "historical directories; leave alone" (this is the rule that row 45 audits)

**No current code depends on any file in any of the 4 audit directories.** They are all safely archive-only.

---

## 6. Recommendations (for the user's follow-up decision)

| # | Action | Risk | Savings | Notes |
|---|---|---|---|---|
| 1 | `git mv` `UI/ARCHIVE_OLD_UI_20251030_223356/` → `archive/ui_archives_20251030/` | Very low | none | Pure location change; 1 cross-ref in `CLAUDE.md` |
| 2 | `git mv` `UI/components_ARCHIVED/` → `archive/ui_components_archived/` | Very low | none | Pure location change |
| 3 | `git mv` `work_quote_dashboard copy.html` → `archive/duplicate_removals/` | Very low | 89K | Exact md5 duplicate |
| 4 | Delete `archive/timelines_and_reports/*.html` and `git_*.txt` (10 files) | Low | ~28 MB | All regenerable, none referenced |
| 5 | Update `CLAUDE.md` line 139 to reflect audited state | None | none | Documentation only |
| 6 | Add a `DEPRECATION_NOTICE.md` to `UI/ARCHIVE_OLD_UI_20251030_223356/` and `UI/components_ARCHIVED/` if moved | None | none | Documents the move |

**Recommended bundle:** actions 1, 2, 3, 5 (and 6 if 1+2 are done). Skip action 4 unless the user wants to reclaim disk space; the 28 MB savings is real but the files are already in `archive/` and out of the way.

---

## 7. Impact on row 47

**None of the audit findings contradict or modify what row 47 did.** Row 47 created `docs/archive/` (a categorized archive of historical .md). Row 45 audited the top-level `archive/`, `ARCHIVE_OCT30_2025/`, `UI/ARCHIVE_OLD_UI_20251030_223356/`, and `UI/components_ARCHIVED/`. The only relationship is the 3-name overlap between `archive/documentation/` and `docs/archive/` (§4), and the recommendation is to **keep both** rather than merge.

If the user does execute the recommended actions 1+2 (move UI archives to `archive/`), the net result is:
- `docs/archive/` is unchanged from row 47.
- `archive/` gains 2 new subdirs (`ui_archives_20251030/`, `ui_components_archived/`) and a `duplicate_removals/` dir.
- The `UI/` directory loses 2 obsolete-looking subdirs (`ARCHIVE_OLD_UI_20251030_223356/`, `components_ARCHIVED/`).
- `CLAUDE.md` line 139 is updated to reflect the audited state.

---

**Audit complete. No file moves executed (per user instruction). Recommendations in §6 await user decision.**
