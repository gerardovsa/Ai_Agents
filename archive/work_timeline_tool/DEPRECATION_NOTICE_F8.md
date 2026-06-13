# F8 deprecation notice — `work_timeline_tool/` relocated from repo root to `archive/`

**Date:** 2026-06-13
**Followup:** F8 of `ARCHIVE_CLEANUP_TRACKER.md` (closing the F6 "future work" item)
**Author:** Claude (cleanup session, branch `cleanup/root-md-cleanup`)
**Scope:** 1 dir move (18 tracked files, ~1.6 MB) from `work_timeline_tool/` → `archive/work_timeline_tool/`

---

## What was moved

| From | To | Renamed? | Files | Size |
|---|---|---|---:|---:|
| `work_timeline_tool/` | `archive/work_timeline_tool/` | **NO** (same name) | 18 | ~1.6 MB |

Contents (18 tracked files):

### Core Python scripts (7)
- `analyze_all_work.py` — work hours analyzer with daily breakdowns
- `analyze_file_activity_timeline.py` — file activity analysis
- `analyze_timestamps.py` — timestamp extraction utility
- `calculate_actual_work_hours.py` — accurate work hours calculator
- `config_template.py` — config template
- `create_focused_timeline.py` — main timeline generator (recommended)
- `professional_timeline.py` — alternative timeline generator

### Documentation (5)
- `CHANGELOG.md` — version history (v2.0, November 11, 2025)
- `INDEX.md` — file index
- `README.md` — main tool documentation
- `TRACKER_COMMAND.md` — tracker integration guide
- `USAGE_GUIDE.md` — usage walkthrough

### Generated HTML outputs (3)
- `focused_timeline_detailed.html` — main interactive dashboard output
- `professional_timeline.html` — alternative timeline view
- `timeline_dashboard_enhanced.html` — enhanced dashboard variant

### Shell / batch helpers (3)
- `install_tracker_command.ps1` — installs the tracker command
- `quick_start.ps1` — PowerShell quick start
- `quick_start.bat` — Windows batch quick start

### NOT moved (git-ignored, dev-local)
- `config.py` — listed in `.gitignore` line 83, **never committed to git**, never
  a public artifact. It was a developer's local config (presumably with personal
  project paths or environment-specific settings). `git mv` does not move
  git-ignored files, so this one was left at the source location. **The canonical
  repo's `work_timeline_tool/config.py` is preserved** (filesystem layer). The
  cleanup dir's working copy lost the file as a side-effect of the dir rename,
  which is harmless because it was never tracked.

## Why this F8 closes the F6 half-state

The F6 deprecation notice (`archive/timelines_and_reports/DEPRECATION_NOTICE_F6.md`)
flagged this as the recommended future-work option #1:

> 1. **Move `work_timeline_tool/` to `archive/work_timeline_tool/`**
>    — the tool is not in any CI/CD workflow, has 0 live importers.
>    Moving it would consolidate the timeline subsystem in one
>    archive location and remove the half-state. The 3 root-level
>    generated HTMLs (`focused_timeline_detailed.html`,
>    `professional_timeline.html`, `timeline_dashboard_enhanced.html`)
>    would also move.

F8 executes exactly that recommendation. The "half-state" (live tool at root
+ outputs in `archive/`) is resolved: the tool is now in `archive/` alongside
its outputs.

## Inbound-reference audit

A `git grep -lE "work_timeline_tool"` against the live repo (excluding
`archive/`, `tmp_row5*`, `docs/archive/`, `*.pyc`) returned **8 files**:

| File | Context | Action |
|---|---|---|
| `work_timeline_tool/install_tracker_command.ps1` | self-reference (path in install script) | **Moved with the dir** — no action needed |
| `work_timeline_tool/TRACKER_COMMAND.md` | self-reference | **Moved with the dir** |
| `work_timeline_tool/USAGE_GUIDE.md` | self-reference | **Moved with the dir** |
| `work_timeline_tool/CHANGELOG.md` | self-reference | **Moved with the dir** |
| `work_timeline_tool/INDEX.md` | self-reference | **Moved with the dir** |
| `work_timeline_tool/README.md` | self-reference | **Moved with the dir** |
| `archive/timelines_and_reports/DEPRECATION_NOTICE_F6.md` | meta (mentions `work_timeline_tool/` as future-work target) | **Already references the new location** (predates F8; F6 notice said "Move `work_timeline_tool/` to `archive/work_timeline_tool/`") |
| `ARCHIVE_CLEANUP_TRACKER.md` | meta (tracker F6/F8 mentions) | **Updated in this commit** — F8 row marked RESOLVED |

**0 production references** (no `.py` imports, no Flask route, no JS module,
no CSS @import references `work_timeline_tool/`).

**0 CI/CD references** (no `.yml`/`.yaml`/`.json`/`.toml`/`.sh`/`.ps1`/`.bat`
files outside the dir reference it). The tool has 3 shell helpers
(`install_tracker_command.ps1`, `quick_start.ps1`, `quick_start.bat`) — these
are dev-time launchers, not CI integrations.

The audit's verdict: the tool is **completely orphaned from production**.
All references are either self-references inside the dir (move with the
dir) or meta-references in cleanup docs (predate F8 and reference the new
location explicitly).

## Companion move (bundled in this commit)

**F6-row-45 followup:** the 12th HTML in `archive/timelines_and_reports/`
that row 45 missed prefixing.

| From | To | Reason |
|---|---|---|
| `archive/timelines_and_reports/work_quote_dashboard.html` (89,438 bytes) | `archive/timelines_and_reports/_ARCHIVED_work_quote_dashboard.html` | Bit-exact duplicate of `_DUPLICATE_work_quote_dashboard copy.html` (same MD5: `77b5481efd80751620825736a389d466`). Row 45 prefixed the `_DUPLICATE_` copy but missed prefixing the original. The original is the "live" version only in the sense that it's the one without a `copy` suffix — not in the sense of being actively used. F8 prefixes it as `_ARCHIVED_` to match the 8 other live originals and complete the row 45 prefix sweep. |

**Total F8 commit scope:** 19 file moves (18 `work_timeline_tool/*` + 1
`work_quote_dashboard.html` prefix) + 1 new deprecation notice
(`archive/work_timeline_tool/DEPRECATION_NOTICE_F8.md`) + 1 tracker
update + 1 chain-of-custody line appended.

## What's now in `archive/work_timeline_tool/`

The 18 tracked files preserve the dir's full structure. The 3 generated
HTMLs that the F6 notice called out specifically
(`focused_timeline_detailed.html`, `professional_timeline.html`,
`timeline_dashboard_enhanced.html`) all moved with the dir — they were
inside `work_timeline_tool/`, not at the repo root.

A future agent looking at the archived dir will see:
- A complete self-contained dev tool (Python scripts + generated outputs + docs)
- All preserved with their original relative paths
- No external dependencies (the README states "No external libraries required")
- No production wiring (0 importers, 0 CI hooks)

The tool is recoverable: if anyone ever wants to regenerate the timeline,
they can `cd archive/work_timeline_tool/ && python create_focused_timeline.py`.
Whether anyone ever wants to is a different question — F8 doesn't take a
position on that.

## Why the tool was at root in the first place (educated guess)

The README says "v2.0, November 11, 2025" and the dev-install nature
(no project integration, personal config template, hand-written
`quick_start.bat`/`quick_start.ps1` launchers) suggests this was a
**developer's personal productivity tool** that got committed by
accident — the kind of script a developer writes for themselves, runs
locally a few times, then forgets is in the repo. It was never wired
into CI, never imported by any module, never advertised in any docs.
A classic "I was just trying to visualize my own work" artifact.

## Chain of custody

- **Branch:** `cleanup/root-md-cleanup` (continuation of F1/F2/F3/F6/F7)
- **Commits:** 1 (this commit)
- **Recovery:** `git log --diff-filter=R -- archive/work_timeline_tool/`
  (18 file moves visible) and
  `git log --diff-filter=R -- archive/timelines_and_reports/_ARCHIVED_work_quote_dashboard.html`
  (1 file move visible)
- **Predecessor:** row 49 (June 12, 2026) flagged the timeline subsystem
- **Predecessor:** F6 (June 13, 2026) closed the F6 finding and flagged
  `work_timeline_tool/` as the next future-work item
- **Tracker resolution:** F8 row (currently a new row added in this
  commit) marked ~~RESOLVED~~ in followups table

## Related rows

- **Row 45** (June 11, 2026, DONE) — prefixed 9 + 2 = 11 HTMLs in
  `archive/timelines_and_reports/`. Missed the 12th (`work_quote_dashboard.html`)
  — F8 fixes that omission.
- **Row 49** (June 12, 2026, DONE) — first captured the broader timeline
  subsystem story
- **F6** (June 13, 2026, RESOLVED) — closed the 11 historical-snapshot
  HTMLs finding, flagged `work_timeline_tool/` as future work
- **F1, F2, F3, F7** (June 12-13, 2026, RESOLVED) — sibling followups
- **F8** (this commit) — closes the timeline subsystem cleanup

## Future work (NOT in F8 scope)

After F8, the timeline subsystem is **fully consolidated in `archive/`**:

- 11 + 1 (this commit) = **12 prefixed HTMLs** in `archive/timelines_and_reports/`
- 19 files (this commit) = the **full `work_timeline_tool/` dev tool** in `archive/work_timeline_tool/`
- 2 generator scripts in `archive/database_utilities/` (`create_master_timeline.py`, `create_project_gantt_chart.py`) — already in archive, not in scope
- 1 generator in `archive/timelines_and_reports/combined_project_timeline.py` — already in archive, not in scope
- 1 live utility `scripts/utilities/generate_work_quote_analysis.ps1` — this one is the only "live" piece left; its output (`_ARCHIVED_work_quote_report.html`) is in archive. Moving the generator to archive would be a separate decision (the script is `scripts/utilities/`-shaped, suggesting it's a maintainable utility, not a one-shot). F8 doesn't take a position on this.
- 4 TIMELINE_*.md docs in `archive/documentation/` — historical analysis, all in archive
- 2 work_hours.json data files in `archive/timelines_and_reports/` — source data for the archived HTMLs, all in archive

The whole timeline subsystem is now properly historical. **No remaining
timeline-related work is needed** to finish the timeline cleanup. Future
cleanup rounds can move on to other subsystems.

## References

- Tracker followup F8 in `ARCHIVE_CLEANUP_TRACKER.md`
- Findings doc: this file
- Predecessor F6 notice: `archive/timelines_and_reports/DEPRECATION_NOTICE_F6.md`
- The tool's own README: `archive/work_timeline_tool/README.md` (preserved with the move)
- Row 45 prefix work: see `ARCHIVE_CLEANUP_TRACKER.md` row 45 chain-of-custody
