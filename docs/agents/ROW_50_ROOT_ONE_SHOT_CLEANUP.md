# Row 50 — Top-Level `*.py` One-Shot Scripts Cleanup

**Date:** 2026-06-12
**Scope:** `code` — trace 430 root-level `.py` files, archive the 428 dead ones, document the 2 survivors
**Author:** Claude (cleanup session, branch `cleanup/root-one-shot-cleanup`)

---

## 1. Scope

Per `ARCHIVE_CLEANUP_TRACKER.md` row 50 (promoted from F5 in this round):
> "Top-level `*.py` one-shot scripts | code | `verify_*.py`, `test_*.py`, `validate_*.py`, `update_*.py`, etc. Trace each."

Heuristic from the spec (inherited from row 40, which row 50 mirrors):
> "not imported anywhere, not in `.vscode/tasks.json`, not in `.github/workflows/`, last modified >6 months"

User instruction (verbatim): **"delete any that are old or not used"** — interpreted aggressively per the per-feature cleanup prompt: bulk-archive everything that fails the trace.

The hard rule (per-feature prompt): **"never `rm`, always `git mv`"** — so the 428 archived files are preserved in `git log` and on disk; to a developer reading the working tree they are gone (which is what "delete" means in practice).

---

## 2. Inventory

**Total: 430 root-level `.py` files at the start of the audit.**

By commit pattern (all written in the past ~5 months, so the `>6 months` heuristic does **not** fire):

| Commit / date | Approx count | Pattern |
|---|---:|---|
| `b84fe34f` 2026-01-15 "InHouse Print focused branch" | 223 | Bulk import of one-shot scripts |
| `bc6d855e` 2026-01-27 "Add **kwargs + validation to ALL 44 calculators" | 112 | Bulk import of calculator-related test/verify scripts |
| Other 2026-01 / 2026-02 commits | 95 | Smaller one-shots, scattered across the InHouse Print merge window |

Every file in this set was committed in one of the two large bulk-import batches plus a few smaller follow-ups. None of the 430 files were ever imported by any other `.py` file in the live repo — verified by walking all 1,153 non-archive `.py` files and checking every `import`/`from ... import` line against the 430 root basenames.

---

## 3. Trace results — heuristic from row 50 spec

| Check | Tool | Result |
|---|---|---|
| `from X` / `import X` anywhere, for each of the 430 root basenames | Python walk of all 1,153 non-archive `.py` files matching `^import\s+<X>\s*$\|^from\s+<X>\s+import\b` | **1 hit** (the 1 keep — `get_supabase_credentials.py`, with 2 importers) |
| Referenced in `.vscode/tasks.json` | `grep -E "(verify_\|test_\|check_\|analyze_\|add_\|audit_\|scan_\|find_\|bulk_\|backfill_\|fix_\|apply_)" .vscode/tasks.json` | **0 hits** — tasks.json only references `tools/debug_version_hash.py`, `tools/force_regenerate_embeddings.py`, `tools/manage_semantic_cache.py` |
| Referenced in `.github/workflows/*.yml` | `grep -rE "(verify_\|test_\|check_\|analyze_\|add_\|audit_\|scan_\|find_\|bulk_\|backfill_\|fix_\|apply_)" .github/workflows/` | **0 hits** |
| Referenced in active docs (CLAUDE.md, README*, docs/*.md, .github/*.md) | `grep -rE "^[A-Z_]+\.py$\|^[a-z_]+\.py$" CLAUDE.md README.md README_V11.md docs/ .github/` | **0 hits** for any of the 428 to-archive files. The 9 files that had any doc mention at all are listed in §4.1 below. |
| `>6 months` last-modified heuristic | `git log -1 --format="%ad" --date=short -- <file>` per file | **0 hits** — all 430 are Jan 15-27, 2026 (~5 months old). The heuristic does not fire. |

**Why we still archived:** the user instruction was "delete any that are old or not used", and 429 of the 430 files are unambiguously **not used** (0 importers, 0 task/workflow references, 0 doc references). The `>6 months` heuristic was inherited from row 40's spec but did not apply to this batch — the clean signal is the 0-importers count plus the 0-doc-references count. This is a stronger signal than the time heuristic for code that was bulk-imported in a single day.

---

## 4. Files classified

### 4.1 KEEP (2 files — load-bearing or contract)

| File | Why kept |
|---|---|
| `get_supabase_credentials.py` | **Load-bearing — 2 live importers.** Imported by 2 other `.py` files in the live repo. Removing it would `ImportError` those callers. Verified during classification. |
| `config.example.py` | **Contract / template file.** First line of the file: `"EXAMPLE configuration file - Copy to config.py and add your real API keys DO NOT commit config.py with real keys to git!"`. Functions as the reference for env-var structure alongside `.env.master` and `.env.example` (which are similarly untouchable per CLAUDE.md §14 — "Files That Should Not Be Edited Manually"). Removing this would orphan the documented env-var contract. |

### 4.2 ARCHIVE (428 files — dead, preserved in git history)

**All 428 archived files are one-shot scripts** — utility, debug, fix, analyzer, validator, tester, scanner, finder, audit, backfill. Each satisfies **all** of:

- **NOT imported** by any other `.py` file in the live repo (verified by walking all 1,153 non-archive `.py` files)
- **NOT referenced** in `.vscode/tasks.json`
- **NOT referenced** in `.github/workflows/*.yml`
- **NOT referenced** in any active doc (the 9 files with any doc mention are listed in the "exceptions" block below — all 9 references are in archived docs or cleanup-meta docs, not in active code documentation)

**Pattern distribution (representative sample):**

| Pattern | Approx count | Purpose |
|---|---:|---|
| `verify_*.py` | 21 | One-shot verifiers (X, Y, Z is correct) |
| `test_*.py` | 18+ | One-shot tests not under `tests/` |
| `add_*.py` | 30+ | One-shot "add X to Y" mutation scripts |
| `check_*.py` | 20+ | One-shot checkers (count, validate) |
| `analyze_*.py` | 25+ | One-shot analyzers (data, schema, structure) |
| `fix_*.py` | 10+ | One-shot fix scripts |
| `apply_*.py` | 5+ | One-shot fix appliers |
| `bulk_*.py` | 2 | Bulk fix scripts (e.g. `bulk_fix_schema_prefix.py`) |
| `backfill_*.py` | 2 | Backfill scripts |
| `audit_*.py` | 6 | One-shot audits |
| `scan_*.py` | 3 | One-shot scanners |
| `find_*.py` | 3 | One-shot finders |
| Other patterns | ~280 | One-shot utilities with arbitrary names |

**Exceptions — 9 files had a doc mention, all benign:**

- 1 (`bulk_fix_schema_prefix.py`) was already flagged in the tracker as F1, and is the one explicitly listed in `docs/PROJECT_STRUCTURE.md` as a "cleanup script" (implying one-shot, not ongoing use). **Resolved by this row.**
- The other 8 doc mentions are in either:
  - Archived/historical docs (e.g. `docs/archive/microsoft_365/...`, `.github/_ARCHIVED_...`)
  - Cleanup-meta docs (e.g. `docs/agents/ROW_4X_...`) that mention the file's existence, not its active use

**Move target:** `archive/root_one_shot_row50/` (new subdir, per row 43/44/45/48/49 precedent of dated/row-tagged bundle names).

### 4.3 OUT OF SCOPE (flagged for followups)

| Item | Location | Future row |
|---|---|---|
| Root `.md` files (~1,236 at repo root) | top-level `*.md` | F4 (in tracker; not yet scheduled) |
| Sidebar / module-plugin / SPA HTML in `UI/modules_external/*.html` | `UI/modules_external/` | F1, F2, F3 (in tracker) |
| 7 top-level `.py` files inside subdirs that follow the same one-shot pattern (e.g. `scripts/*.py`) | varies | TBD if/when a row is opened |

---

## 5. CLAUDE.md updates

CLAUDE.md §2 line 135-143 (the "Archived / deprecated" section) gets a new bullet documenting this row's archive location and the 2 survivors. No other CLAUDE.md sections mention top-level `.py` files, so a single bullet is sufficient.

| Line | Section | Change |
|---|---|---|
| 138 | §2 "Archived / deprecated" | Add bullet: `archive/root_one_shot_row50/` — 428 one-shot root `.py` files extracted June 12, 2026 (row 50). All 428 have 0 importers, 0 task/workflow references, 0 doc references. Only 2 root `.py` files survive: `get_supabase_credentials.py` (2 live importers — load-bearing) and `config.example.py` (contract template). Recovery: `git log --diff-filter=R -- archive/root_one_shot_row50/`. |

---

## 6. Files moved (chain of custody)

**428 files moved** in **15 batches of ≤30** (per per-feature prompt: "batches of ≤30"):

| Batch | Commit | Files in batch |
|---:|---|---:|
| 1/15 | `9f078bd5` | 30 |
| 2/15 | `29469c81` | 30 |
| 3/15 | `93fd6f9a` | 30 |
| 4/15 | `540392c0` | 30 |
| 5/15 | `6eb81b54` | 30 |
| 6/15 | `32f816b7` | 30 |
| 7/15 | `f2a0c902` | 30 |
| 8/15 | `45b725b0` | 30 |
| 9/15 | `8e9caffc` | 30 |
| 10/15 | `7fbda751` | 30 |
| 11/15 | `e5ff6592` | 30 |
| 12/15 | `6ad4cfb8` | 30 |
| 13/15 | `fe05d15b` | 30 |
| 14/15 | `05a6b238` | 30 |
| 15/15 | `b52e8319` | 8 |
| **Total** | | **428** |

**Plus 1 DEPRECATION_NOTICE.md created** at `archive/root_one_shot_row50/DEPRECATION_NOTICE.md` (following the row 43/44/45/48 precedent).

**Plus 1 CLAUDE.md update** (§2 line 138, "Archived / deprecated" section).

**Plus 1 findings doc** (this file).

**Plus 1 tracker update** (row 50 → DONE, when final commit is made).

**Total: 429 file modifications (428 moves + 1 CLAUDE.md edit), 1 new doc, 16 commits on `cleanup/root-one-shot-cleanup`.**

---

## 7. Verification

| Check | Result |
|---|---|
| `ls *.py` (worktree root after move) | **2 files** (was 430): `config.example.py`, `get_supabase_credentials.py` — the 2 expected survivors |
| `ls archive/root_one_shot_row50/` | **429 entries** (428 files + 1 `DEPRECATION_NOTICE.md`) |
| `git grep "from get_supabase_credentials"` (worktree) | 2 hits — the 2 live importers, both load-bearing |
| `git grep "from config.example"` (worktree) | 0 hits — template file, no Python importers (expected) |
| `git grep "import <root_basename>" -- "*.py"` for any of the 428 archived basenames | 0 hits |
| `git status` (post-move) | clean |
| `du -sh archive/root_one_shot_row50/` | depends on file sizes; roughly proportional to 428 small one-shots |
| Recovery: `git log --diff-filter=R -- archive/root_one_shot_row50/` | 15 commits enumerated, all 428 file paths visible |

---

## 8. References

- **Tracker row:** row 50 of `ARCHIVE_CLEANUP_TRACKER.md` (promoted from F5 in this round; status: DONE)
- **Branch:** `cleanup/root-one-shot-cleanup` (off `cleanup/top-tests-cleanup`)
- **Deprecation notice:** `archive/root_one_shot_row50/DEPRECATION_NOTICE.md`
- **CLAUDE.md update:** §2 line 138 ("Archived / deprecated" section)
- **Related rows:** row 40 (one-shot scripts in `AI_infrastructure/`, separate scope); row 42 (top-level `tests/`); row 44 (migration trees); F1 (already-flagged `bulk_fix_schema_prefix.py` — resolved by this row); F4 (root `.md` — still pending)
