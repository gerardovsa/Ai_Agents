# F6 deprecation notice — 11 historical-snapshot HTMLs in `archive/timelines_and_reports/`

**Date:** 2026-06-13
**Followup:** F6 of `ARCHIVE_CLEANUP_TRACKER.md`
**Author:** Claude (cleanup session, branch `cleanup/root-md-cleanup`)
**Scope:** 11 generated timeline/report HTMLs in `archive/timelines_and_reports/` (all `_ARCHIVED_` prefix from row 45)

---

## What this followup was

The F6 row (from row 49's findings doc §4.3) was:

> **1,094 stale cross-references** to docs that have been moved/archived.
> The HTML itself is in `archive/` (read-only per the cleanup contract);
> the broken refs are low-impact. Captured in row 49 findings doc §4.3
> for followup. Not blocking; defer until next round.

It referred to one file: `archive/timelines_and_reports/ai_agents_timeline.html`
(now `archive/timelines_and_reports/_ARCHIVED_ai_agents_timeline.html` after
row 45's prefix pass).

## What the audit found

The F6 row's description was **inaccurate in two important ways**:

1. **There are 11 files, not 1.** The same generator (`combined_project_timeline.py`
   and friends) produced 11 distinct reports, all in `archive/timelines_and_reports/`,
   all prefixed `_ARCHIVED_` in row 45. Total ~25 MB.

2. **There are no "cross-references" — the file paths are textual, not hyperlinked.**
   The HTMLs use `<div class="file-item">path/to/file.py</div>` for file listings,
   not `<a href="path/to/file.py">`. The "stale refs" are text strings, not
   clickable links. There is no "broken hyperlink" experience when viewing
   the HTMLs — only stale text in a file-listing table.

The full set of 11 files:

| File | Size | Title | Generator |
|---|---:|---|---|
| `_ARCHIVED_ai_agents_timeline.html` | 3.8 MB | AI_agents File Activity Timeline | `archive/timelines_and_reports/combined_project_timeline.py` (variant) |
| `_ARCHIVED_ai_agents_accurate_timeline.html` | 18 MB | (accurate timeline variant) | `archive/test_scripts/analyze_file_metadata_accurate.py` |
| `_ARCHIVED_ai_agents_work_hours.html` | 55 KB | AI_agents Work Hours | `work_timeline_tool/calculate_actual_work_hours.py` |
| `_ARCHIVED_combined_project_timeline.html` | 88 KB | Combined Project Timeline | `archive/timelines_and_reports/combined_project_timeline.py` |
| `_ARCHIVED_combined_timeline_v2_detailed.html` | 361 KB | Detailed Project Timeline Analysis | (same generator, v2) |
| `_ARCHIVED_combined_timeline_v3_ultra_detailed.html` | 1 MB | Ultra-Detailed File Timeline | (same generator, v3) |
| `_ARCHIVED_master_timeline_all_projects.html` | 83 KB | Master Project Timeline | `archive/database_utilities/create_master_timeline.py` |
| `_ARCHIVED_project_gantt_chart.html` | 381 KB | Project Development Gantt Chart | `archive/database_utilities/create_project_gantt_chart.py` |
| `_ARCHIVED_work_quote_report.html` | 5.5 KB | Work Quote Analysis Report | `scripts/utilities/generate_work_quote_analysis.ps1` |
| `_DUPLICATE_focused_timeline_detailed copy.html` | 382 KB | (focused timeline — DUPLICATE) | (was in `archive/test_scripts/`, marked DUPLICATE in row 45) |
| `_DUPLICATE_work_quote_dashboard copy.html` | 87 KB | (work quote dashboard — DUPLICATE) | (was in `archive/test_scripts/`, marked DUPLICATE in row 45) |

The 11 files are all **historical snapshots of the repo as of late 2025**.
The F6 target file's own header is the smoking gun:
- "Total Files Tracked: **12,780**"
- "Date Range: **2025-10-26 to 2025-11-08**"
- "Busiest Create Day: **12,154**" (2025-11-08 — 12,154 files created on one day)
- "Busiest Modify Day: **12,398**" (2025-11-08)

The 12,780 figure is the repo size at the time the snapshot was taken. The
filenames in the file-listing tables reflect the pre-cleanup state. After
the cleanup moves (rows 50/51/52, F1/F2/F3, F7, and earlier rows 45/47/48),
many of those filenames no longer exist at the paths shown — but the HTML
is a snapshot of what was there on 2025-11-08, not a live view.

## Why this is RESOLVED, not "needs fixing"

The F6 row framed the 1,094 figure as "stale cross-references" and
implied they were a bug. The audit found:

1. **The "refs" are text strings, not hyperlinks.** There is no
   "click → 404" experience. The HTMLs render correctly; the file
   paths just show pre-cleanup locations.

2. **The HTMLs are historical artifacts by design.** The header
   explicitly says "File Activity Timeline Analysis" with a 2-week
   date range. Updating the paths would destroy the historical
   record (the whole point of the snapshot is to show what the repo
   looked like on 2025-11-08, not what it looks like today).

3. **The HTMLs are in `archive/` (read-only per the cleanup contract).**
   The per-feature prompt and CLAUDE.md §2 establish `archive/` as
   historical, not maintained.

4. **No production path references these HTMLs.** A `git grep` for any
   of the 11 filenames against the live repo (excluding `archive/`,
   `tmp_row5*`, `docs/archive/`, `*.pyc`) returns 0 hits. The HTMLs
   are not loaded by Flask, not imported by any Python, not linked
   from CLAUDE.md, README, or any other live doc. They are
   genuinely orphaned artifacts of a one-shot analysis.

5. **The whole pipeline is dormant.** The generators
   (`archive/timelines_and_reports/combined_project_timeline.py`,
   `archive/database_utilities/create_master_timeline.py`,
   `archive/database_utilities/create_project_gantt_chart.py`,
   `archive/test_scripts/analyze_file_metadata_accurate.py`)
   are in `archive/` (frozen). The live dev tool that produced some
   of the HTMLs is `work_timeline_tool/` at the repo root — but
   `work_timeline_tool/` has 0 references from any CI/CD workflow,
   shell script, or `package.json` task. The tool exists, but is
   not wired into any automated run.

The "1,094 stale refs" finding was a **count of text strings, not
broken hyperlinks**. The 1,094 was correct (the file has ~12,780 file
listings, of which 1,094 reference paths that have since been moved).
But "stale text in a historical snapshot" is not the same as "broken
hyperlink", and is not a bug to fix.

## What "finishing" F6 means

This F6 closeout **does NOT modify any of the 11 HTMLs**. It:

1. Documents the precise nature of the finding (text strings, not
   hyperlinks; historical snapshots, not live reports)
2. Documents the full scope (11 files, not 1; ~25 MB total)
3. Documents the pipeline (generators, data sources, no live wiring)
4. Marks F6 RESOLVED with this decision recorded
5. Flags (but does not execute) the related scope expansion:
   `work_timeline_tool/` at the repo root is in a half-state — its
   outputs are in `archive/` but the tool itself is live. A future
   cleanup round could either:
   - Move `work_timeline_tool/` to `archive/` (it's not referenced
     from any production workflow, so this is safe)
   - Or wire `work_timeline_tool/` into a real workflow and
     regenerate the HTMLs (more surgery, different ask)

The 11 archived HTMLs stay as-is. They are now properly documented
as historical snapshots; future agents who see them in `archive/`
will know exactly what they are.

## Inbound-reference audit (live repo only)

`git grep` for any of the 11 HTML filenames against the live repo
(excluding `archive/`, `tmp_row5*`, `docs/archive/`, `*.pyc`)
returned 0 hits. The HTMLs are not loaded by Flask, not imported by
any Python, not linked from CLAUDE.md, README, or any other live doc.
They are genuinely orphaned artifacts.

The only "live" references to the timeline subsystem are:
- `work_timeline_tool/` (9 Python scripts + 2 PS1 + 1 BAT + 3 generated
  HTMLs + 5 docs) — at the repo root, not wired into any workflow
- 9 markdown files in `archive/documentation/` (TIMELINE_*, WORK_*
  prefix) — historical analysis, all in archive
- The 4 generators in `archive/` (combined_project_timeline.py,
  create_master_timeline.py, create_project_gantt_chart.py,
  analyze_file_metadata_accurate.py) — frozen
- `scripts/utilities/generate_work_quote_analysis.ps1` — a live
  utility, but not in any CI workflow

## Chain of custody

- **Branch:** `cleanup/root-md-cleanup` (continuation of F1/F2/F3/F7)
- **Commits:** 1 (this row's commit)
- **Recovery:** N/A — no files moved, no files modified; this commit
  only adds the deprecation notice and updates the tracker
- **Predecessor:** row 49 (June 12, 2026) findings doc §4.3 first
  captured the "1,094 stale refs" finding
- **Predecessor:** row 45 (June 11, 2026) prefixed the HTMLs with
  `_ARCHIVED_` to mark them as archival artifacts (the prefix was
  applied *before* this audit, which is good — it tells future
  agents "this is an archive artifact, not a live report")
- **Tracker resolution:** F6 marked ~~RESOLVED~~ in followups table

## Related rows

- **Row 45** (June 11, 2026, DONE) — applied `_ARCHIVED_` prefix to
  the timeline HTMLs (a forward-looking move that prefigured this
  finding)
- **Row 47** (June 11, 2026, DONE) — moved 1,094 of the file paths
  referenced in the snapshots (mostly into `archive/timelines_and_reports/`,
  `archive/analysis_reports/`, `archive/documentation/`, etc.)
- **Row 49** (June 12, 2026, DONE) — first captured the F6 finding
  in the findings doc §4.3
- **Rows 50, 51, 52** (June 12, 2026, DONE) — moved 1,755 root
  files; their old paths are now the "stale refs" in the HTMLs
- **F1, F2, F3, F7** (June 12-13, 2026, RESOLVED) — moved more
  files; their old paths are also "stale refs" in the HTMLs
- **F6** (this commit) — RESOLVED with documentation, not file mods

## Future work (NOT in F6 scope)

If a future cleanup round wants to address the `work_timeline_tool/`
half-state (live tool at root, outputs in archive), options are:

1. **Move `work_timeline_tool/` to `archive/work_timeline_tool/`**
   — the tool is not in any CI/CD workflow, has 0 live importers.
   Moving it would consolidate the timeline subsystem in one
   archive location and remove the half-state. The 3 root-level
   generated HTMLs (`focused_timeline_detailed.html`,
   `professional_timeline.html`, `timeline_dashboard_enhanced.html`)
   would also move.

2. **Wire `work_timeline_tool/` into a real workflow** (e.g., a
   cron job, a GitHub Action, a VS Code task) and regenerate the
   HTMLs. This is a different kind of cleanup — making a dormant
   tool active.

3. **Leave as-is** — the current state is "a live dev tool that
   someone might run by hand; outputs go to a directory that's
   marked archive". This is a known half-state, documented in
   this F6 deprecation notice for future agents.

The choice depends on whether the timeline tool is intended to be
re-used. F6 closes the followup without taking a position on that.

## References

- Tracker followup F6 in `ARCHIVE_CLEANUP_TRACKER.md`
- Findings doc: this file
- Row 49 findings doc §4.3 (the original capture of the 1,094 figure)
- The 11 HTMLs themselves (preserved in `archive/timelines_and_reports/`)
- Generators (in `archive/timelines_and_reports/`,
  `archive/database_utilities/`, `archive/test_scripts/`)
- Live dev tool (in `work_timeline_tool/` at repo root — NOT in archive,
  not wired into any workflow)
