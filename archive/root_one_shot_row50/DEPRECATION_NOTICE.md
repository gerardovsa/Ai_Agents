# Deprecation Notice: top-level `*.py` one-shot scripts (row 50)

**Date archived at this location:** June 12, 2026
**Status:** EXTRACTED from top-level `*.py` (not deleted — preserved here for historical reference)

---

## What was extracted

**428 .py files** were moved from the top-level repo root to this archive. After this extraction, the top-level repo root contains **only 2 .py files** that survive the row-50 heuristic:

| File | Why kept |
|---|---|
| `get_supabase_credentials.py` | **The only root .py with live importers** (2 other .py files import it). Genuinely load-bearing. |
| `config.example.py` | **Contract / template file** — first line of the file is: "EXAMPLE configuration file - Copy to config.py and add your real API keys DO NOT commit config.py with real keys to git!". Functions as the reference for env-var structure alongside `.env.master` and `.env.example` (which are similarly untouchable per CLAUDE.md §14). |

All 428 other top-level .py files were **standalone one-shot scripts** (utility, debug, fix, analyzer, validator, tester, scanner) that:

- Are **NOT imported** by any other .py file in the repo (verified by walking all 1,153 non-archive `.py` files and checking every `import`/`from ... import` line)
- Are **NOT referenced** in `.vscode/tasks.json` (the 5 documented tasks only reference `tools/debug_version_hash.py`, `tools/force_regenerate_embeddings.py`, `tools/manage_semantic_cache.py`)
- Are **NOT referenced** in `.github/workflows/*.yml`
- Are **NOT referenced** in any active doc (only 9 had any doc reference at all, and every one of those references is in a now-archived doc or a cleanup-meta doc like `docs/agents/ROW_4X_*`)
- Are **NOT in any active test runner** (the 5 documented `tests/run_*.py` runners only call `test_persistent_semantic_*.py` as subprocesses — they don't reference any root .py)

The full file list is in the file listing below.

## Why these were moved

Per `ARCHIVE_CLEANUP_TRACKER.md` row 50, the user instruction was: **"delete any that are old or not used"**.

Heuristic applied (from the row 40 spec, which row 50 inherited):

> "Trace each. Heuristic: not imported anywhere, not in `.vscode/tasks.json`, not in `.github/workflows/`, last modified >6 months."

Applied criteria:
1. **Not imported anywhere** — checked via walk of all 1,153 non-archive `.py` files, matching `import X` / `from X import ...` for each of the 430 root basenames.
2. **Not in `.vscode/tasks.json`** — verified 0 hits.
3. **Not in `.github/workflows/`** — verified 0 hits.
4. **Not in active docs** (CLAUDE.md, README.md, README_V11.md, docs/*.md, .github/*.md) — only 9 not-imported files had any doc mention, and all 9 of those references are in either:
   - Archived/historical docs (e.g. `docs/archive/microsoft_365/...`, `.github/_ARCHIVED_...`)
   - Cleanup-meta docs (e.g. `docs/agents/ROW_41_...`, `docs/agents/ROW_42_...`) that mention the file's existence, not its active use
   - One structural doc (`docs/PROJECT_STRUCTURE.md`) that lists the file as a "cleanup script" — implying one-shot, not ongoing use
5. **Bulk-import date** — all 430 files are <6 months old by git `Last modified`. The `>6 months` heuristic did **not** fire. However, **223 files** were committed in one batch on 2026-01-15 (commit `b84fe34f`, "InHouse Print focused branch") and **112 files** in another batch on 2026-01-27 (commit `bc6d855e`, "Add **kwargs + validation to ALL 44 calculators") — these were bulk imports, not iterative development. Files with this commit pattern and zero ongoing use are treated as **effectively old** under the user's "delete any that are old" criterion.

The hard rule from the per-feature cleanup prompt is **"never `rm`, always `git mv`"** — so all 428 files were preserved in `git log` and on disk by moving them to this archive location. To a developer reading the working tree, the files are gone (this is what "delete" means in practice); to anyone reading git history, they are recoverable.

## What's still in the repo root (2 .py files)

After this extraction, the live top-level `*.py` set is:

```
get_supabase_credentials.py    # 2 importers — load-bearing
config.example.py              # contract template
```

That's the entire `*.py` surface at the repo root.

## File listing (428 files)

The 428 archived files are in this directory. A representative sample of patterns:

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

The full list of 428 filenames is recoverable from git history (see below).

## How to recover

Preserved in `git log` history. To view the pre-move state:

```bash
git log --diff-filter=R -- archive/root_one_shot_row50/
```

To see all 428 files at their original paths:

```bash
git log --all --diff-filter=R --name-only -- '*.py' | grep -E '^[A-Z_]+\.py$|^[a-z_]+\.py$' | sort -u
```

Or to find a specific file:

```bash
git log --all -- 'bulk_fix_schema_prefix.py'
```

## References

- **Cleanup row:** row 50 of `ARCHIVE_CLEANUP_TRACKER.md` (promoted from F5)
- **Branch:** `cleanup/root-one-shot-cleanup`
- **Audit doc:** `docs/agents/ROW_50_ROOT_ONE_SHOT_CLEANUP.md` (created in this round)
- **Related rows:** row 40 (one-shot scripts in `AI_infrastructure/`, separate scope); F1 (already-flagged `bulk_fix_schema_prefix.py` — resolved by this row)
