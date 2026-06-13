# F2 deprecation notice — 3 "copy" duplicates relocated from `core/archived/`

**Date:** 2026-06-13
**Followup:** F2 of `ARCHIVE_CLEANUP_TRACKER.md`
**Author:** Claude (cleanup session, branch `cleanup/root-md-cleanup`)
**Scope:** 3 `.py` files moved from `AI_infrastructure/core/archived/` → `archive/ai_infrastructure_core_archived_copies/`

---

## What was moved

| File | Size | Original md5 | Archived path |
|---|---:|---|---|
| `agent_worker copy 2.py` | 48,153 B | `0487f4995d1e249a0411203f02344f70` | `archive/ai_infrastructure_core_archived_copies/agent_worker copy 2.py` |
| `agent_worker copy.py` | 24,271 B | `d0ca97d2234536a59347f3bd5c3b08cd` | `archive/ai_infrastructure_core_archived_copies/agent_worker copy.py` |
| `streaming_agent_worker copy.py` | 48,800 B | `80a6b79b7506512009838460fa655148` | `archive/ai_infrastructure_core_archived_copies/streaming_agent_worker copy.py` |

The new directory `archive/ai_infrastructure_core_archived_copies/` is a
sub-archive specifically for the 3 "Copy Files (Development Versions)"
from `AI_infrastructure/core/archived/`. Path preserved (no rename) so
the `git log` chain shows the exact move.

## Why they were moved

Per CLAUDE.md §2:

> `AI_infrastructure/core/archived/` — old `agent_worker.py`,
> `streaming_agent_worker.py`, `session_handler.py`, etc. **Do not
> import from.**

And per `AI_infrastructure/core/archived/README.md` (the dir's own
README, written when the dir was created on 2025-11-20):

> ### Copy Files (Development Versions)
> - `agent_worker copy.py` - Development backup
> - `agent_worker copy 2.py` - Development backup
> - `streaming_agent_worker copy.py` - Development backup

These 3 files are **bitrot from a `cp`-based workflow that predates
git hygiene** — they were created by `cp agent_worker.py "agent_worker
copy.py"` and never maintained in source control. The md5 fingerprints
confirm:

| "Copy" file | md5 | Same as live `agent_worker.py`? |
|---|---|---|
| `agent_worker copy 2.py` | `0487f4995d1e249a0411203f02344f70` | **YES — bit-exact** |
| `agent_worker copy.py` | `d0ca97d2234536a59347f3bd5c3b08cd` | No (older revision) |
| `streaming_agent_worker copy.py` | `80a6b79b7506512009838460fa655148` | No (older revision) |

The bit-exact match on `agent_worker copy 2.py` proves the workflow
that produced it: someone ran `cp`, then continued editing the original,
and the copy was never touched. This is the most common shape of
"copy" bitrot.

## Why they're safe to move

The V4 architecture migration (Oct 2025) refactored the live worker
code from `agent_worker.py` + `streaming_agent_worker.py` →
`AI_infrastructure/core/combined_agent_worker.py` (verified via
`AI_infrastructure/combined_agent_worker.py:3` — *"Combines
agent_worker.py + streaming_agent_worker.py with all critical fixes"*).

The "live" `agent_worker.py` and `streaming_agent_worker.py` no longer
exist outside `core/archived/`. The "copy" files are duplicates of
**frozen** files, not of live code.

**Inbound-reference audit (live repo, excluding `archive/`, `tmp_row5*`,
`docs/archive/`, `*.pyc`):**

- **0 `.py` references** to any of the 3 copy files (verified by
  `git grep -lE "(agent_worker copy|streaming_agent_worker copy)\.py"
  -- '*.py' :!archive :!tmp_row5*` → 0 results)
- **5 `.md` references, all meta/audit/historical:**
  - `AI_infrastructure/core/archived/README.md` — lists them as
    "Copy Files (Development Versions)" (historical inventory; will
    be left in place per the §8 decision below)
  - `ARCHIVE_CLEANUP_TRACKER.md` — F2 row (this commit resolves it)
  - `docs/agents/ROW_41_CORE_ARCHIVED_FREEZE_VERIFICATION.md` — the
    Nov 2025 row 41 audit that deferred this move (line 144
    explicitly: *"future consolidation row (not yet scheduled)"*)
  - `archive/timelines_and_reports/CLEANUP_COMPLETE_NOV20_2025.md` —
    Nov 2025 cleanup report (already archived)
  - `docs/archive/_ARCHIVED_*` — 2 historical analysis files
    (already archived)

**1 false positive** caught in the broader search: `tools/implementations/
pinecone/pinecone_tools.py:1023` contains the string `"archived"` but
it's a MongoDB filter (`{"archived": {"$ne": true}}`) — unrelated to
the file move.

## Decision on the dir README

`AI_infrastructure/core/archived/README.md` is **not modified** in this
commit. It describes the Nov 2025 archive contents and is itself a
historical record. Modifying it to remove the "Copy Files" section
would be rewriting history. The new `archive/ai_infrastructure_core_
archived_copies/DEPRECATION_NOTICE_F2.md` (this file) is the canonical
record of where the 3 copy files went.

## Chain of custody

- **Branch:** `cleanup/root-md-cleanup` (continuation of rows 49/50/51/52
  and F1/F7 followups)
- **Commits:** 1 (this row's commit)
- **Recovery:** `git log --diff-filter=R -- archive/ai_infrastructure_core_archived_copies/` (3 file moves visible)
- **Predecessor:** row 41 (2025-11-20) froze the `core/archived/` dir
  and explicitly deferred the 3 copy files to a "future consolidation
  row (not yet scheduled)" — F2 is that row.
- **Tracker resolution:** F2 marked ~~RESOLVED~~ in followups table

## Related rows

- **Row 41** (2025-11-20) — froze `AI_infrastructure/core/archived/`
  and identified the 3 copy files as a future cleanup target
- **Row 38** (V4 architecture build, 2025-10-30) — refactored the live
  workers into `combined_agent_worker.py`; the "live" `agent_worker.py`
  and `streaming_agent_worker.py` no longer exist outside the frozen
  archived dir
- **F2** (this commit) — the deferred consolidation row 41 called out
- **F4, F5, F7, F1** — sibling followups, all RESOLVED in the same
  cleanup round (June 12-13, 2026)

## References

- Tracker followup F2 in `ARCHIVE_CLEANUP_TRACKER.md`
- Findings doc: this file (`archive/ai_infrastructure_core_archived_copies/DEPRECATION_NOTICE_F2.md`)
- Frozen-dir README: `AI_infrastructure/core/archived/README.md`
  (untouched; historical record of the Nov 2025 archive contents)
- Predecessor audit: `docs/agents/ROW_41_CORE_ARCHIVED_FREEZE_VERIFICATION.md`
  (line 144: the explicit deferral)
- V4 migration narrative: `AI_infrastructure/V4_ARCHITECTURE_STATUS.md`,
  `AI_infrastructure/COMBINED_WORKER_MIGRATION.md`,
  `AI_infrastructure/V4_BUILD_COMPLETE.md`
