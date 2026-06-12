# Deprecation Notice: `database_scripts/`

**Date archived at this location:** June 12, 2026
**Status:** EXTRACTED from top-level `database_scripts/` (not deleted — preserved here for historical reference)

---

## What was extracted

1 file was extracted from the top-level `database_scripts/` directory. The directory itself was not moved because **it was the only file inside it** — the rename `git mv database_scripts archive/database_scripts` is functionally a single-file move.

| File | Size | Reason for extraction |
|---|---:|---|
| `populate_embeddings.py` | 20K | Orphaned: imports `from config import get_api_key_enhanced, OPENAI_API_KEYS` — neither symbol exists in the current `config/` module (they live only in `config.example.py` template). Functionally a duplicate of `tools/migrations/enable_pgvector_and_populate_embeddings.py`. |

## Why it was moved

Per `ARCHIVE_CLEANUP_TRACKER.md` row 44, the spec was: "audit the top-level `database_scripts/`, `migrations/`, `supabase_migrations/`, `database_migrations/`, and `database/` directories to determine which are still load-bearing, which are stale duplicates, and which are dead code". The audit verified:

1. No code in `AI_infrastructure/` or `tools/` imports from `database_scripts.*` (verified via `git grep "from database_scripts" -- AI_infrastructure tools`).
2. `config.py` at the repo root is itself a stale legacy file (not the live config — that lives in `AI_infrastructure/config/`) — see row 44 audit.
3. The script duplicates functionality available at `tools/migrations/enable_pgvector_and_populate_embeddings.py`.

The hard rule from the per-feature cleanup prompt is **"never `rm`, always `git mv`"** — so the file was preserved in `git log` and on disk by moving it to this archive location.

## What's now in `database_scripts/` at the top level

After this extraction, the top-level `database_scripts/` directory no longer exists.

## How to recover

Preserved in `git log` history. To view the pre-move state:

```bash
git log --diff-filter=R -- archive/database_scripts/
```

To see the file at its original path (`database_scripts/populate_embeddings.py`):

```bash
git log --all -- 'database_scripts/populate_embeddings.py'
```

## References

- **Cleanup row:** row 44 of `ARCHIVE_CLEANUP_TRACKER.md`
- **Branch:** `cleanup/migration-trees-audit`
- **Audit doc:** `docs/agents/ROW_44_MIGRATION_TREES_AUDIT.md` (created in this round)
