# Row 44 — Top-Level Migration Trees Audit

**Date:** 2026-06-12
**Scope:** `code` — read-only audit + 2 archive moves
**Author:** Claude (cleanup session, branch `cleanup/migration-trees-audit`)

---

## 1. Scope

Per `ARCHIVE_CLEANUP_TRACKER.md` row 44:
> "Top-level migration trees audit | code | `database/`, `database_migrations/`, `database_scripts/`, `migrations/`, `supabase_migrations/`. Confirm `AI_infrastructure/migrations/` is the only authoritative set; archive the rest."

User instruction for this row: aggressive — proceed with moves once classified.

---

## 2. Inventory

**Of 5 directories listed in the row spec, only 2 exist at the top level at the start of this audit.** The other 3 were already removed in earlier cleanup rounds (as documented in CLAUDE.md §13.11 risk #11 "Migration drift").

| Directory | Files | Status at row 44 start | Verdict |
|---|---:|---|---|
| `database/` | n/a | **Already gone** | Documented in CLAUDE.md §13.11; nothing to do |
| `database_migrations/` | n/a | **Already gone** | Documented in CLAUDE.md §13.11; nothing to do |
| `supabase_migrations/` | n/a | **Already gone** | Documented in CLAUDE.md §13.11; nothing to do |
| `database_scripts/` | 1 | Exists | **ARCHIVE** (orphaned script — see §3.1) |
| `migrations/` | 2 | Exists | **ARCHIVE** (pre-Supabase dead code — see §3.2) |

**Authoritative set (the only one that should receive new files):** `AI_infrastructure/migrations/` — 56 `.sql` + 29 `.py` migration files. Confirmed by reading the directory listing and cross-referencing CLAUDE.md §2 + §13.11.

---

## 3. Findings — what was archived and why

### 3.1 `database_scripts/populate_embeddings.py` (1 file, 20K)

**Verdict: ARCHIVE**

Two reasons, both independently disqualifying:

**(a) The import target doesn't exist.** The script's first action is:
```python
from config import get_api_key_enhanced, OPENAI_API_KEYS
```
Neither symbol exists in the current top-level `config.py` (the live config lives at `AI_infrastructure/config/`, which is a completely different module). The symbols do exist in `config.example.py` (a template file) and as inline constants in `routes/search_routes.py` and `core/universal_file_handler.py`, but `populate_embeddings.py` imports them as if from a stable `config` module — that contract was broken. The script would raise `ImportError` on first import.

**(b) Functionally a duplicate.** The active populate-embeddings script is at `tools/migrations/enable_pgvector_and_populate_embeddings.py`. The `database_scripts/populate_embeddings.py` script performs the same BGE-population operation against a different (no-longer-existing) config module.

**Verified load-bearing:** `git grep "from database_scripts" -- AI_infrastructure tools` → 0 hits. No live importer.

**Action taken:** `git mv database_scripts archive/database_scripts` (single file inside, so this is a file-level move preserving git history).

### 3.2 Top-level `migrations/` (2 files, 12K)

**Verdict: ARCHIVE (with rename to disambiguate)**

**Files:**
- `README.md` (7K) — Dated Nov 19, 2025. Documents 3 `.sql` files that **do not exist anywhere** in the repo: `supabase_production_migration_nov19_2025.sql`, `verify_migration_nov19_2025.sql`, `rollback_nov19_2025.sql`. The README is internally inconsistent — the files it describes were either moved to `AI_infrastructure/migrations/` (most likely) or never ran.
- `run_migration.py` (1K) — Pre-Supabase dead code. Uses `sqlite3` + `data/synergy_sessions.db` (the project has been on Supabase Postgres since 2025 per CLAUDE.md §1). The script also references `migrations/001_add_task_sync.sql`, which does not exist. The entire execution model is obsolete.

**Verified load-bearing:** `git grep "from migrations" -- AI_infrastructure tools` → 0 hits. No live importer.

**Why renamed (not just `archive/migrations/`):** To disambiguate from the authoritative `AI_infrastructure/migrations/`. The new name `archive/legacy_top_level_migrations/` makes the precedence unambiguous: the `AI_infrastructure/` path is current; the `archive/` path is historical. This follows the row 45 precedent of always using a **descriptive archive name** (not just `archive/<original-dir-name>/`).

**Action taken:** `git mv migrations archive/legacy_top_level_migrations`.

---

## 4. CLAUDE.md updates

Two places referenced the directories that were archived. Both were updated to reflect the audit completion.

| Line | Section | Change |
|---|---|---|
| 138 | §2 "What NOT to place where" | Added a status note: 3 of the 5 listed dirs were already gone; 2 (`database_scripts/`, `migrations/`) were moved under `archive/` during the row 44 audit (June 12, 2026) |
| 641 | §13.11 risk #11 "Migration drift" | Same status note added to the risk description, so future agents reading §13 know the audit has been performed |

No other inbound references to the moved paths were found in canonical docs. The legacy `copilot-instructions.md` is the only other doc that mentions `migrations/` at the top level, and that is being rewritten in row 49.

---

## 5. Files moved (chain of custody)

| # | From | To | Notes |
|---|---|---|---|
| 1 | `database_scripts/populate_embeddings.py` | `archive/database_scripts/populate_embeddings.py` | Renamed dir contains 1 file |
| 2 | `migrations/README.md` | `archive/legacy_top_level_migrations/README.md` | |
| 3 | `migrations/run_migration.py` | `archive/legacy_top_level_migrations/run_migration.py` | |

**Plus 2 DEPRECATION_NOTICE.md created** (one per moved dir, following the row 43/45/48 precedent).

**Plus 2 CLAUDE.md updates** (lines 138 + 641).

**Total: 5 file ops + 2 doc updates, 2 commits.**

Commit chain on `cleanup/migration-trees-audit`:
- `3352b25d` chore(cleanup/migration-trees-audit): row 44 — claim, classify, plan
- `e0300801` chore(cleanup/migration-trees-audit): row 44 — move dead top-level database_scripts + migrations under archive

---

## 6. Verification

| Check | Result |
|---|---|
| `git grep "from database_scripts" -- AI_infrastructure tools` | 0 hits (no live importer) |
| `git grep "from migrations" -- AI_infrastructure tools` | 0 hits (no live importer) |
| `ls database_scripts migrations` (post-move) | both report "No such file or directory" |
| `ls archive/database_scripts archive/legacy_top_level_migrations` | both contain expected files + DEPRECATION_NOTICE.md |
| `AI_infrastructure/migrations/` listing | 56 .sql + 29 .py — authoritative, untouched |
| CLAUDE.md line 138, 641 | Updated; re-read to confirm wording |

---

## 7. References

- **Tracker row:** row 44 of `ARCHIVE_CLEANUP_TRACKER.md` (status: DONE)
- **Branch:** `cleanup/migration-trees-audit`
- **Deprecation notices:** `archive/database_scripts/DEPRECATION_NOTICE.md`, `archive/legacy_top_level_migrations/DEPRECATION_NOTICE.md`
- **CLAUDE.md updates:** §2 line 138, §13.11 line 641
- **Related rows:** row 43 (top-level integration dirs, June 12 2026), row 45 (top-level archive dirs, June 11 2026)
