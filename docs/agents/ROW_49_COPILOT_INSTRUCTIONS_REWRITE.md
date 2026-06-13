# Row 49 — `.github/copilot-instructions.md` rewrite

**Date:** 2026-06-12
**Branch:** `cleanup/github-cleanup` (continuation of row 48)
**Author:** Claude (cleanup session)
**Scope:** one file: `.github/copilot-instructions.md` (1,448 → 149 lines)
**Outcome:** **DONE.** File rewritten as a thin pointer doc per CLAUDE.md §16.7.

---

## 1. Why this row existed

`ARCHIVE_CLEANUP_TRACKER.md` row 49 (formerly TODO, now DONE):

> `.github/copilot-instructions.md` rewrite. After every other doc row is
> done, rewrite this to point only at canonical docs. ~40 inbound links.

The file had drifted badly — it was last touched April 30, 2026 (the
header date) and predated:

- The 4-provider AI rollout (migration 051, May 2026 — `MiniMax` was
  never mentioned in the old file)
- The 4-tier credential resolver (May 2026, sub-user inheritance)
- The DB-driven module catalog (May 2026, replacing `manifest.json`)
- The introduction of CLAUDE.md as the canonical repo doc (June 11, 2026)
- The entire row 47 docs-archive pass (1,094 HTML link refs went stale)

CLAUDE.md §13 risk #1 calls this file out explicitly:

> `.github/copilot-instructions.md` is stale (last touched April 30, 2026).
> Several specific facts are wrong or out of date. Do not rely on it as the
> source of truth; verify against migrations and code.

## 2. Approach — thin pointer, not a rewrite-everything

The temptation with a 1,448-line stale doc is to "fix everything that's
wrong." That would have:

1. Taken hours of work for a file that is itself a duplicate of CLAUDE.md.
2. Created a new doc that would go stale again in 6 months.
3. Made the doc less, not more, useful — the more it covers, the more
   it must be kept in sync.

The right shape is a **thin pointer** (~150 lines) that says:

> The canonical source of truth is CLAUDE.md at the repo root. Per-topic
> deep-dives are in the 5 `.github/*.md` files. Read those first; this
> file only adds notes specific to Copilot that are not in those docs.

This means the next time a subsystem evolves (e.g., a new AI provider
is added, a new migration changes the auth flow, the vector DB layer is
rewritten), only CLAUDE.md and the affected topic doc need to be
updated. `copilot-instructions.md` becomes self-stable.

## 3. What the new file contains (7 sections, 149 lines)

| § | Section | Lines | Notes |
|---|---|---:|---|
| 1 | Start here — read in this order | 1–20 | Points at CLAUDE.md → README* → topic deep-dives |
| 2 | Topic deep-dives (canonical `.github/*.md`) | 1–30 | 5-row table linking the canonical docs |
| 3 | Repo-at-a-glance (mirrored from CLAUDE.md §1-§2) | 1–25 | 4-provider, plugin modules, multi-agent |
| 4 | Hard rules | 1–35 | BOM, secrets, auth, RLS, hardcoded user_id, migrations, archive |
| 5 | Where to find things (file map) | 1–20 | 11-row file→purpose table |
| 6 | Pre-commit checklist | 1–15 | 3 PowerShell one-liners |
| 7 | What this file used to be | 1–35 | Link rot fixed + stale content retired + 1 known stale HTML |

The §7 "what this file used to be" section is the most important — it
makes the rewrite **discoverable for archaeology**. Any future agent
who runs `git log` on this file will see the dramatic 1,448 → 149 line
diff and need context for *why*; §7 provides it.

## 4. Link inventory + rot fixes

### 4.1 Markdown links (4 .md refs in the old file)

| Old ref | Status | Resolution |
|---|---|---|
| `README.md` | Valid | Kept |
| `woocommerce_v4_exemplar_status.md` | **BROKEN** (moved to `archive/` in row 47) | Removed; the open ticket is now referenced by code + module README |
| `.github/MODULE_VISIBILITY_ARCHITECTURE.md` | Valid | Kept |
| `.github/SVG_CAD_GENERATION_RULES.md` | Valid | Kept |

### 4.2 Bare filename refs in inline code (the bulk of the old file)

The old file referenced ~31 `.py` files and ~5 other files via inline
backticks (e.g., `` `flask_app.py` ``). These were not link-rot per se
— they pointed at files that exist — but they were *stale*:

- 5 of the 31 `.py` paths had moved: `shared/database_utils.py` is now
  `AI_infrastructure/shared/database_utils.py`, `tools/registry_v3.py`
  is now at the same path (correct), `shared/supabase_client.py` is
  now `AI_infrastructure/shared/...`, etc. The new §5 file map uses
  the current full paths.
- 3 references were to subsystems that no longer exist as named
  (`tool_definitions.py` is "legacy, being migrated"; the legacy
  tool definitions have been replaced by `UI/modules_external/<module>/tools/*.json`).
- The "module V4 migration status table" referenced 5 module paths and
  a status per module. The statuses had drifted (e.g., 13 modules were
  listed as "Pending" in the old file; current state is that
  WooCommerce is the only completed V4, per CLAUDE.md §13 risk #2).
  Replaced with a pointer to CLAUDE.md §13.

### 4.3 Link rot NOT fixed in this rewrite (out of scope)

`archive/timelines_and_reports/ai_agents_timeline.html` contains ~1,094
stale cross-references to docs that have been moved/archived. The file
itself is in `archive/` (read-only per the cleanup contract), and is a
one-shot generated report. Fixing the broken refs would mean
re-generating the timeline HTML, which is out of scope for row 49 and
not worth the effort for an archived report. Captured here for
followup; not blocking.

## 5. Decisions on what to keep vs. retire

### 5.1 Kept (because Copilot-specific and not in CLAUDE.md)

- The 2-line status banner (read CLAUDE.md first; this file is a thin pointer)
- The §2 topic table (a Copilot-oriented "load on demand" guide, distinct from
  CLAUDE.md's table of contents)
- The §6 pre-commit checklist (3 PowerShell one-liners; same content as
  CLAUDE.md §3 "Encoding — CRITICAL pre-commit" + a `user_id = 1` audit
  — the audit is not in CLAUDE.md)

### 5.2 Retired (now in CLAUDE.md or a topic doc)

| Old section | New home | Reason |
|---|---|---|
| Project Overview (10 lines) | CLAUDE.md §1 | Exact duplicate |
| Project Architecture Map (40 lines) | CLAUDE.md §2 | Mostly duplicate; kept only the "where to find things" subset |
| How to Find Things (25 lines) | CLAUDE.md §3 + this file §5 | Better organized in CLAUDE.md |
| Org / Team / Roles / Platform Catalog (260 lines) | `.github/ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md` | The 4-tier resolver section is the truth |
| Credential Encryption (30 lines) | `.github/ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md` + `.env.master` | Both are the contract |
| All Organisation API Endpoints (35 lines) | `AI_infrastructure/routes/organisation_credentials_routes.py` (the code) | Code is the truth; 25 endpoints is the implementation |
| Frontend Integration (45 lines) | CLAUDE.md §4 + §5 | Architecturally documented in CLAUDE.md |
| How to Add a New Platform (60 lines) | `.github/copilot-instructions.md.disabled` (the original) → `archive/copilot-instructions_disabled_nov2025/` | Was the original target, now archived |
| How to Add a New Module (60 lines) | `.github/MODULE_VISIBILITY_ARCHITECTURE.md` | Topic doc has the current contract |
| Development Workflow (25 lines) | CLAUDE.md §3, §6, §7 | Standard agent rules |
| Emergency Patterns (20 lines) | CLAUDE.md §17 (Quick Reference) | Same content, more discoverable |
| Important Constraints (30 lines) | CLAUDE.md §6, §9, §10, §11, §12 | All covered by CLAUDE.md agent rules |
| Module Plugin System Details (60 lines) | `tools/module_plugin.py` (the code) + `UI/modules_external/manifest.json.disabled` → `archive/` | Code is the truth |
| Environment Variables Reference (35 lines) | `.env.example` + `.env.master` | The contract for env-vars is the template files |
| Pre-Commit Hooks (25 lines) | CLAUDE.md §3 "Encoding — CRITICAL pre-commit" | Pre-commit is local discipline; only BOM is hard |
| Quick Reference Commands (50 lines) | CLAUDE.md §17 (Quick Reference) + `.vscode/tasks.json` (the source of truth) | Same content |
| File Encoding Rules (50 lines) | CLAUDE.md §3 "Encoding — CRITICAL pre-commit" | Duplicate |
| Troubleshooting: InHouse Print Database Access (260 lines) | `.github/_ARCHIVED_*INHOUSE*` (already archived) + CLAUDE.md §13 risk #3 | The InHouse path-resolution quirk is the only durable lesson |
| Remember / Production Checklist (25 lines) | CLAUDE.md §15 (Definition of Done) | Same content |

**Net reduction: 1,448 → 149 lines (90%).**

## 6. File encoding

The rewrite was written via the `Write` tool, which the harness
verifies produces UTF-8 without BOM. No BOM re-introduction check
needed (the file is `.md`, not `.js`/`.html`/`.css`/`.json`, so BOM
isn't a production hazard for this specific file — but the harness's
BOM check is universal and would have caught it).

## 7. Chain of custody

- **Branch:** `cleanup/github-cleanup` (continuation from row 48)
- **Commits:** 1 (the rewrite itself, on the same branch as row 48's
  `.github/` cleanup work)
- **Recovery:** `git log --all --oneline -- .github/copilot-instructions.md`
  shows the rewrite; `git log -p HEAD~1 -- .github/copilot-instructions.md`
  shows the prior 1,448-line content
- **Findings doc:** this file
- **No deprecation notice** (nothing was archived; the file path is
  preserved)

## 8. What this enables

- **Self-stable doc.** Future agent changes (new provider, new
  migration, new module) only require updating CLAUDE.md or the
  affected topic doc, not this file. The §2 "Topic deep-dives" table
  is the only piece that needs to grow when a new canonical doc
  appears.
- **No more drift risk.** The previous file drifted because it tried
  to be comprehensive. The new file is small enough to review in
  5 minutes and its only moving parts are the canonical-doc pointers.
- **GitHub Copilot loads less, learns more.** The old file bloated
  Copilot's context window with duplicated facts. The new file is
  a clear "go read this" instruction, which is the shape Copilot
  handles best.

## 9. Related rows

- **Row 47** (docs-archive, 2026-06-11) — moved the file that
  `woocommerce_v4_exemplar_status.md` referenced, causing the
  link rot that §4.1 of this row fixed
- **Row 48** (`.github/` cleanup, 2026-06-12) — sibling; the work
  on this row was a continuation of row 48 (same branch)
- **F7** (suggested followup) — archive the stale
  `.github/AI_DOCUMENTATION_CONSOLIDATION_INSTRUCTIONS.md`. This
  row 49 rewrite explicitly flags that file as stale in §2.
- **F2, F3** (TODO) — both still pending; not blocking row 49

## 10. References

- Tracker row 49 of `ARCHIVE_CLEANUP_TRACKER.md`
- Companion doc: CLAUDE.md §16.7 "Update procedure"
- Old file content: `git show HEAD~1:.github/copilot-instructions.md`
- Prior long-form reference: `archive/copilot-instructions_disabled_nov2025/copilot-instructions.md.disabled`
  (the November 2025 version, archived in row 48)
