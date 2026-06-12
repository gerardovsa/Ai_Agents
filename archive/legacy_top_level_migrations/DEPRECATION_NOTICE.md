# Deprecation Notice: `migrations/` (top-level, renamed to `legacy_top_level_migrations/`)

**Date archived at this location:** June 12, 2026
**Status:** EXTRACTED from top-level `migrations/` (not deleted — preserved here for historical reference)

---

## What was extracted

2 files were moved from the top-level `migrations/` directory. The directory was renamed to `legacy_top_level_migrations/` (not just `migrations/`) to disambiguate it from the **authoritative** `AI_infrastructure/migrations/` (which is the only migration tree that should receive new files per CLAUDE.md §2 and §13.11).

| File | Size | Reason for extraction |
|---|---:|---|
| `README.md` | 7K | Stale: documents 3 .sql files (`supabase_production_migration_nov19_2025.sql`, `verify_migration_nov19_2025.sql`, `rollback_nov19_2025.sql`) that **do not exist anywhere** in the repo. The README itself is dated Nov 19, 2025. |
| `run_migration.py` | 1K | Pre-Supabase dead code: uses `sqlite3` + `data/synergy_sessions.db` but the project has been on Supabase Postgres since 2025 (per CLAUDE.md §1). The script also references `migrations/001_add_task_sync.sql`, which does not exist. |

## Why it was moved

Per `ARCHIVE_CLEANUP_TRACKER.md` row 44, the spec was: "audit the top-level `database_scripts/`, `migrations/`, `supabase_migrations/`, `database_migrations/`, and `database/` directories to determine which are still load-bearing". The audit verified:

1. No code in `AI_infrastructure/` or `tools/` imports from `migrations.*` (verified via `git grep "from migrations" -- AI_infrastructure tools`).
2. The `README.md` was internally inconsistent — the files it described no longer exist.
3. The `run_migration.py` script targets a non-existent SQLite database path.
4. **None of the 4 sibling directories** (`database/`, `database_migrations/`, `supabase_migrations/`, the duplicate `database/`) existed at the top level at the start of row 44 — they had already been removed in earlier rounds.

The hard rule from the per-feature cleanup prompt is **"never `rm`, always `git mv`"** — so the files were preserved in `git log` and on disk by moving them to this archive location.

## Why the new name

The renamed bundle is `legacy_top_level_migrations/` (not just `migrations/`) so the precedence is unambiguous:

- **`AI_infrastructure/migrations/`** — authoritative, current, versioned, gets new files
- **`archive/legacy_top_level_migrations/`** — historical, frozen, no new files

## How to recover

Preserved in `git log` history. To view the pre-move state at the top-level `migrations/` path:

```bash
git log --diff-filter=R -- archive/legacy_top_level_migrations/
```

To see the README at its original path (`migrations/README.md`):

```bash
git log --all -- 'migrations/README.md'
```

## References

- **Cleanup row:** row 44 of `ARCHIVE_CLEANUP_TRACKER.md`
- **Branch:** `cleanup/migration-trees-audit`
- **Audit doc:** `docs/agents/ROW_44_MIGRATION_TREES_AUDIT.md` (created in this round)
