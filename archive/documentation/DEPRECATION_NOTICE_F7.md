# F7 deprecation notice — stale January-2026 doc-consolidation plan retired

**Date:** 2026-06-12
**Followup:** F7 of `ARCHIVE_CLEANUP_TRACKER.md`
**Author:** Claude (cleanup session, branch `cleanup/root-md-cleanup`)
**Scope:** one file: `.github/AI_DOCUMENTATION_CONSOLIDATION_INSTRUCTIONS.md` → `archive/documentation/AI_DOCUMENTATION_CONSOLIDATION_INSTRUCTIONS_jan2026.md`

---

## What was moved

| File | Size | Original path | Archived path | Reason |
|---|---:|---|---|---|
| `AI_DOCUMENTATION_CONSOLIDATION_INSTRUCTIONS.md` | 26 KB | `.github/AI_DOCUMENTATION_CONSOLIDATION_INSTRUCTIONS.md` | `archive/documentation/AI_DOCUMENTATION_CONSOLIDATION_INSTRUCTIONS_jan2026.md` | Historical bucket — superseded by CLAUDE.md §16 |

The rename adds a `_jan2026` suffix to preserve the historical context (this was a January 2026 consolidation plan, not a current instruction set).

## Why it was stale

The file is a **January 2026 instruction set** telling AI agents to
consolidate the project's 500+ root `.md` files into 22 "master technical
documents" (e.g. `ARCHITECTURE.md`, `THREAD_SYSTEM.md`, `MODULES.md`,
`AI_AGENTS.md`, `VECTOR_DATABASE.md`, `INHOUSE_PRINT.md`, etc.).

As of June 12, 2026:

- **All 14 of the consolidation-target root `.md` files it lists as
  "consolidation candidates" are now archived** (row 51, June 12, 2026
  — they were all in the "Suspicious" bucket with 0 inbound references
  from any active production doc).
- **The 22 "master technical documents" the plan was consolidating INTO
  are themselves now archived** (e.g. `ARCHITECTURE.md` →
  `archive/timelines_and_reports/`, `THREAD_SYSTEM.md` → `archive/...`,
  etc.). The plan's target structure no longer exists.
- **The current doc workflow is CLAUDE.md §16** (Documentation
  Maintenance Workflow), which is a living, single-source-of-truth
  pattern — fundamentally different from the "consolidate into 22
  master docs" pattern in this January 2026 file.
- **The new `copilot-instructions.md` (row 49, June 12, 2026) explicitly
  flags this file as stale** in §2: *"the 6th `.md` in this directory
  is stale (last touched January 2026, pre-CLAUDE.md). It's scheduled to
  be archived in the next cleanup round (F7)."*

## Inbound-reference audit

A `git grep -lE "AI_DOCUMENTATION_CONSOLIDATION_INSTRUCTIONS"` was run
against the entire live repo (excluding `archive/`, `tmp_row5*`,
`docs/archive/`, `*.pyc`).

| File | Context | Action |
|---|---|---|
| `.github/copilot-instructions.md` | §2 says "F7 will archive it" | **Updated in this commit** to remove the callout (the file is no longer there) |
| `ARCHIVE_CLEANUP_TRACKER.md` | F-row in followups; multiple findings docs mention it as "F7 candidate" | **Updated in this commit** to mark F7 RESOLVED |
| `CLAUDE.md` | §2 line 143 mentions 14 refs from this file as the reason some root `.md` files were "Suspicious" bucket | **No change needed** — historical/audit context, not a live ref |
| `docs/agents/ROW_45_TOP_LEVEL_ARCHIVE_AUDIT.md` | Audit history | **No change needed** — past-tense audit doc |
| `docs/agents/ROW_49_COPILOT_INSTRUCTIONS_REWRITE.md` | §10 "References" lists F7 as related row | **No change needed** — historical chain-of-custody |
| `docs/agents/ROW_51_ROOT_MD_CLEANUP.md` | §97, §100, §165, §168, §180 mention F7 in audit reasoning | **No change needed** — historical findings doc |
| `docs/agents/ROW_52_ROOT_SCRIPTS_CLEANUP.md` | §265, §280 mention F7 as suggested next row | **No change needed** — historical chain-of-custody |

**0 code references** (no `.py` file imports, opens, or references this file).

**Net result:** the 7 .md mentions are all meta/audit/forward-looking.
None of them will break with the file's removal. The 2 .md mentions
that were forward-looking (copilot-instructions.md, tracker) are
updated in this commit.

## Chain of custody

- **Branch:** `cleanup/root-md-cleanup` (continuation of rows 50/51/52)
- **Commits:** 1 (this row's commit)
- **Recovery:** `git log --diff-filter=R -- archive/documentation/ | grep AI_DOCUMENTATION_CONSOLIDATION`
- **Tracker resolution:** F7 marked ~~RESOLVED~~ in followups table

## Related rows

- **Row 49** (June 12, 2026, DONE) — `.github/copilot-instructions.md`
  rewrite that flagged this file as F7
- **Row 51** (June 12, 2026, DONE) — root `.md` cleanup that archived
  the 14 candidate files this instruction file was targeting
- **F4, F5** (June 12, 2026, RESOLVED) — the two big followups that
  led to row 50/51/52

## References

- Tracker followup F7 in `ARCHIVE_CLEANUP_TRACKER.md`
- Findings doc: this file
- Stale-content flag in row 49's rewrite: `.github/copilot-instructions.md` §2
- Predecessor (F7 tombstone): mentioned in `docs/agents/ROW_51_ROOT_MD_CLEANUP.md` §97, §165, §180
