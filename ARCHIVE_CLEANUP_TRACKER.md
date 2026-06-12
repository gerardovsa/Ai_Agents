# Archive & Cleanup Tracker
**Last updated:** 2026-06-11
**Owner:** Gerardo (gerardovsa)
**Active round:** June 2026 cleanup
**Staging worktree:** `C:\Users\gpoli\GIT\AI_Agents_V11_cleanup\AI_agents\` on branch `cleanup/jun-2026` (created 2026-06-11 via `git worktree add -b cleanup/jun-2026 "C:/Users/gpoli/GIT/AI_Agents_V11_cleanup/AI_agents" v11`)
- `C:\Users\gpoli\GIT\AI_Agents_V11 - Copy (15)\AI_agents\` and `C:\Users\gpoli\GIT\AI_Agents_V11 - Copy (16)\AI_agents\` are left in place as literal file-copy backups and are NOT modified.

All agent work happens in the worktree, on the `cleanup/jun-2026` branch. You merge from there to `v11`.

> **This is the single source of truth for the current doc + code + unused-script cleanup.**
> All cleanup agents must read this file before starting any work, claim a row before touching it, and update the row + append to the chain-of-custody log when done.
> **Do not archive this file. Do not move it. Do not rename it.**

---

## How to use this tracker

1. **Read `CLAUDE.md` §16** (Documentation Maintenance Workflow) and §17 (Quick Reference) before doing anything.
2. **Find a row in `TODO` status** in the master table below.
3. **Edit this file** to change that row's status to `CLAIMED` and add your session ID / branch name in the `Owner` column. Commit.
4. **Work on a feature branch** named `cleanup/<feature-slug>` (e.g. `cleanup/shopify`). The branch lives in the **staging copy** at `C:\Users\gpoli\GIT\AI_Agents_V11 - Copy (15)\AI_agents\`.
5. **Process the feature** following the per-feature cleanup prompt (input: `WORKING_DIR` = the staging copy).
6. **Update the row** to `DONE` (or `SKIPPED`/`BLOCKED` with a reason).
7. **Open a PR** in the staging copy targeting `v11`. After the user verifies, the change is mirrored back to the canonical `AI_Agents_V11`.

**Status legend**

| Status | Meaning | Who can move it |
|---|---|---|
| `TODO` | Not started | Anyone (claim it) |
| `CLAIMED` | An agent is reserved on this row | The agent that claimed it |
| `IN_PROGRESS` | The agent is actively working | The agent that claimed it |
| `DONE` | Cleaned up, PR opened, verified | Anyone after PR merge |
| `SKIPPED` | Decided not to clean this round (reason required) | Anyone with a stated reason |
| `BLOCKED` | Needs human input / decision | Only the owner |

**Scope legend**

| Code | Meaning |
|---|---|
| `docs` | Only documentation cleanup (move/merge/archive) |
| `code` | Only code cleanup (unused scripts, dead modules) |
| `code+docs` | Both — most module rows |
| `code-trace` | Trace the full code path; produce a map; only archive what's confirmed dead |
| `meta` | Top-level concern (root files, archive audits) |

---

## Where to put archived files (the rule)

| What you're retiring | Destination |
|---|---|
| **Code** (route files, scripts, configs, queries) | `archive/<category>/` at root |
| **General documentation** (analysis write-ups, fix logs, "complete" summaries) | `docs/archive/` |
| **Topic-specific doc bundle** | `docs/<topic>/archive/` (e.g. `docs/synergy/archive/`) |
| **A whole feature being retired** | `archive/deprecated/<YYYY-MM-DD>/` with `DEPRECATION_NOTICE.md` |
| **An in-place file that's still linked but superseded** | Prefix rename to `_ARCHIVED_<name>.md` (do not move) |
| **A file in the runtime data dirs** (`data/`, `exports/`, `logs/`, `templates/`) | **DO NOT archive** — these are runtime state |

Use the established categories in each destination — do not invent new sub-dirs without consulting the user.

---

## Master table (49 rows)

> Rows are ordered: do them **top-to-bottom** unless the order column says otherwise.
> Add new rows at the bottom, never in the middle.

### Section A — Cross-cutting subsystems (code+docs; trace required)

| # | Item | Scope | Code paths involved | Owner | Branch | Status | PR | Notes |
|---|------|-------|---------------------|-------|--------|--------|----|-------|
| 1 | Auth & Permissions | code-trace | `AI_infrastructure/auth/`, `routes/auth_routes.py`, `routes/oauth_routes.py`, `permission_checker.py`, `mfa_manager.py`, JWT helpers, `g.rls_user_id` callers | | | TODO | | **Process first.** Hardcoded `user_id=1` smells live here. |
| 2 | Org / Team / Role (multi-tenancy) | code-trace | `organisations`, `users`, `org_invitations`, `workspace/`, `organisations_rls_policies.sql`, JWT version | | | TODO | | RLS policies are part of the contract. |
| 3 | Credentials (4-tier resolver, Fernet, vault) | code-trace | `AI_infrastructure/shared/org_credentials_loader.py`, `platform_credentials_loader.py`, `credential_crypto.py`, `routes/organisation_credentials_routes.py` | | | TODO | | Load-bearing — touched by 30+ other rows. |
| 4 | AI Providers (Anthropic, OpenAI, DeepSeek, MiniMax) | code-trace | `core/unified_ai_client.py`, `core/unified_anthropic_client.py`, `core/combined_agent_worker.py`, `routes/connection_routes.py`, migrations 050+051 | | | TODO | | MiniMax M3 thinking only — verify `_PROVIDER_THINKING_MODELS`. |
| 5 | Tools & Registry (registry_v3, plugin loader) | code-trace | `tools/registry_v3.py`, `tools/module_plugin.py`, `tools/module_plugin_loader.py`, `core/module_blueprint_loader.py`, `core/tool_executor.py`, `core/tool_processor.py` | | | TODO | | Each tool in `tools/implementations/<provider>/` is a sub-trace. |
| 6 | Threads & Messages | code-trace | `routes/thread_routes.py`, `routes/chat_routes.py`, `routes/message_operations.py`, `threads/`, `core/thread_reconciliation.py`, `thread_sharing_manager.py` | | | TODO | | |
| 7 | Multi-Agent Coordination | code-trace | `core/combined_agent_worker.py`, `routes/agent_routes_v4.py`, `core/agent_state_manager.py`, `core/session_orchestrator.py` | | | TODO | | |
| 8 | Synergy & Kanban | code-trace | `routes/synergy_routes.py`, `routes/synergy_share_routes.py`, `routes/synergy_file_search.py`, `routes/kanban_routes.py`, `routes/kanban_supabase_routes.py`, `routes/kanban_analytics_routes.py`, `routes/inhouse_kanban_routes.py`, `docs/synergy/` | | | TODO | | |
| 9 | Vector Database | code-trace | `routes/vector_db_routes.py`, `tools/implementations/pgvector/`, `tools/implementations/pinecone/`, `routes/pgvector_routes.py`, `routes/qdrant_routes.py`, `UI/modules_internal/vector_database/`, migrations 044/045/048/049 | | | TODO | | 4-tier credential resolver already used. |
| 10 | Automation & Scheduler | code-trace | `routes/automation_routes.py`, `routes/scheduler_routes.py`, `routes/task_sync_routes.py`, `tools/implementations/automation.py` | | | TODO | | |
| 11 | Document Processing | code-trace | `core/text_extractor.py`, `core/document_converter.py`, `core/email_to_pdf_converter.py`, `routes/file_routes.py`, `routes/document_library_routes.py`, `tools/implementations/document_library*.py` | | | TODO | | |
| 12 | Communication Hub (Gmail, Outlook) | code-trace | `routes/communication_routes.py`, `routes/google_auth_routes_V2_FIXED.py`, `routes/microsoft_auth_routes_V2_FIXED.py`, `UI/modules_internal/communication-hub/`, `UI/modules_internal/messages/` | | | TODO | | |
| 13 | Frontend Shell (single-page app) | code+docs | `UI/business-ai-platform-v2.html` (1.5 MB), frontend helpers in root (`console_inspector.js`, `ui-command-processor.js`, `cad-chat-renderer.js`) | | | TODO | | **Sample-only** — do not try to clean the 1.5 MB file. |
| 14 | Sidebar & Module Visibility | code+docs | `MODULE_VISIBILITY_ARCHITECTURE.md`, `initModulesFromOrg()`, `applyOrgRoleVisibility()`, `data-module`, `data-org-min-role`, `UI/modules_internal/module_loader_v3_hybrid.js` | | | TODO | | Mostly already-done; verify gaps. |
| 15 | Real-time / WebSocket (presence, streaming) | code-trace | `flask_app.py` WS handlers, `STREAMING_WEBSOCKET_HANDLERS.py`, `ThreadPresence`, `join_thread/leave_thread/typing_indicator`, gevent async mode | | | TODO | | |

### Section B — External integration modules (code+docs; one per module)

| # | Item | Scope | Code paths involved | Owner | Branch | Status | PR | Notes |
|---|------|-------|---------------------|-------|--------|--------|----|-------|
| 16 | Shopify | code-trace | `UI/modules_external/shopify/`, `routes/shopify_routes.py` (if exists), `tools/implementations/shopify*.py` | | | TODO | | |
| 17 | Xero | code-trace | `UI/modules_external/xero/`, `routes/xero_routes.py` (if exists), `tools/implementations/xero*.py`, `analyze_xero_customers.py` | | | TODO | | |
| 18 | WooCommerce | code-trace | `UI/modules_external/woocommerce/`, `routes/woocommerce_routes.py` (if exists), `tools/implementations/woocommerce*.py` | | | TODO | | **May be BLOCKED** by known 400 errors. |
| 19 | Australia Post | code-trace | `UI/modules_external/auspost-shipping/`, `routes/auspost_routes.py`, `tools/implementations/auspost*.py` | | | TODO | | |
| 20 | InHouse Print | code-trace | `UI/modules_external/inhouse-print/` (inhouse_wrapper.py is load-bearing), `db_connector.py`, `tools/implementations/inhouse*.py`, migrations referencing it | | | TODO | | Path resolution is critical — do not break. |
| 21 | InHouse Kanban | code-trace | `UI/modules_external/inhouse-kanban/`, `routes/inhouse_kanban_routes.py` | | | TODO | | |
| 22 | Quote Calculator | code-trace | `UI/modules_external/quote-calculator/` (NOT `backend/query_library.py` — too large), `routes/quote_calculator_routes.py`, `tools/implementations/quote*.py` | | | TODO | | query_library.py (~5,958 lines) is out of scope. |
| 23 | Customer Reactivation | code-trace | `UI/modules_external/customer-reactivation/`, related migration `011_customer_reactivation_tables.sql` | | | TODO | | |
| 24 | Database Visualizer | code-trace | `UI/modules_external/database-visualizer/`, `routes/database_visualizer_routes.py` | | | TODO | | |
| 25 | GitHub | code-trace | `UI/modules_external/github/`, `tools/implementations/github.py` | | | TODO | | |
| 26 | Render Management | code-trace | `UI/modules_external/render-management/`, `routes/render_routes.py` | | | TODO | | |
| 27 | Local Filesystem | code-trace | `UI/modules_external/local-filesystem/`, related routes | | | TODO | | |
| 28 | Dev Diagnostics | code-trace | `UI/modules_external/dev-diagnostics/`, `routes/dev_tools_routes.py` | | | TODO | | |
| 29 | Stock Management | code-trace | `UI/modules_external/stock-management/`, `utils/db_path_helper.py` (Supabase stock_data schema) | | | TODO | | |

### Section C — Internal sidebar modules (code+docs; one per module)

| # | Item | Scope | Code paths involved | Owner | Branch | Status | PR | Notes |
|---|------|-------|---------------------|-------|--------|--------|----|-------|
| 30 | vector_database (internal) | code+docs | `UI/modules_internal/vector_database/` | | | TODO | | Already covered in row 9; this row is for the sidebar files. |
| 31 | communication-hub (internal) | code+docs | `UI/modules_internal/communication-hub/` | | | TODO | | Already covered in row 12. |
| 32 | messages (internal) | code+docs | `UI/modules_internal/messages/` | | | TODO | | |
| 33 | agents (internal) | code+docs | `UI/modules_internal/agents/` | | | TODO | | |
| 34 | automation (internal) | code+docs | `UI/modules_internal/automation/` | | | TODO | | |
| 35 | notifications (internal) | code+docs | `UI/modules_internal/notifications/` | | | TODO | | |
| 36 | internal-docs (internal) | code+docs | `UI/modules_internal/internal-docs/`, `internal_docs/` | | | TODO | | |
| 37 | components (internal) | code+docs | `UI/modules_internal/components/` | | | TODO | | |

### Section D — Top-level meta concerns

| # | Item | Scope | What to do | Owner | Branch | Status | PR | Notes |
|---|------|-------|------------|-------|--------|--------|----|-------|
| 38 | Root .md cleanup (1,240 files) | docs+meta | Classify every .md at the root. Move Historical/Scratch to `docs/archive/` (or topic sub-archive). Move Contract-candidates to canonical locations. | | | TODO | | **Largest row.** Plan to do in batches of 100-200 files. |
| 39 | Root operational scripts (`BISTART*.ps1`, `BISTOP.ps1`, `CHAT.bat`, `CHATM.bat/ps1`, `console_inspector.js`, fix/cursor scripts, `BROWSER_CONSOLE_COMMANDS.md`, etc.) | code | Trace each: referenced in `.vscode/tasks.json`, `package.json` "main", or any doc? Archive the rest. | | | TODO | | |
| 40 | `AI_infrastructure/` one-shot scripts (`analyze_*.py`, `check_*.py`, `find_*.py`, `fix_*.py`, `test_*.py` not under `AI_infrastructure/tests/`) | code | Trace each. Heuristic: not imported anywhere, not in `.vscode/tasks.json`, not in `.github/workflows/`, last modified >6 months. | | | TODO | | Likely high yield. |
| 41 | `AI_infrastructure/core/archived/` freeze verification | code | Confirm no live imports. Document the freeze. | | | TODO | | `agent_worker.py` and friends — verify zero callers. |
| 42 | Top-level `tests/` cleanup | code+docs | `run_group*.py`, `test_all_calculators*.py`, `test_*.py` (calculator tests). Trace each. | | | TODO | | |
| 43 | Top-level "integration" directories | meta | `Woocommerce/`, `Cloudflare/`, `Render_backend/`, `Supabase/`, `Microsoft_365_Connection/`, `google_workspace/`, `tslot_bed_frame_docs/`, `temp_v9_comparison/`. For each: is anything imported from here? Is the content archived elsewhere? | claude-row43-2026-06-12 | 2026-06-12 | DONE | cleanup/integration-dirs-audit | **2 batches, 117 file ops.** 6 orphaned integration dirs moved under `archive/`: `Woocommerce/` (1 file/68K), `Cloudflare/` (20/138K), `Render_backend/` (68/809K), `Supabase/` (12/164K), `tslot_bed_frame_docs/` (5/24K), `temp_v9_comparison/` (5/196K). 4 unused files extracted from `Microsoft_365_Connection/` to `archive/Microsoft_365_Connection_unused/`: `email_sender.py`, `microsoft365_client.py`, `quote_request_processor.py`, `test_email_integration.py` (DEPRECATION_NOTICE.md added). **2 dirs KEPT at top level** (load-bearing, load verified via grep): `google_workspace/` (20 files, 4+ live importers) and `Microsoft_365_Connection/microsoft365_oauth_manager.py` (the only live file in that dir). **CLAUDE.md line 139 fixed**: prior wording incorrectly listed `google_workspace/` and `Microsoft_365_Connection/` as 'historical'; rewrote to make the active/historical split explicit. 0 broken refs in active docs. |
| 44 | Top-level migration trees audit | code | `database/`, `database_migrations/`, `database_scripts/`, `migrations/`, `supabase_migrations/`. Confirm `AI_infrastructure/migrations/` is the only authoritative set; archive the rest. | | | TODO | | |
| 45 | Top-level archive directories audit | meta | `ARCHIVE_OCT30_2025/`, `archive/`, `_ARCHIVED_NOV25/`, `UI/ARCHIVE_OLD_UI_20251030_223356/`, `UI/components_ARCHIVED/`. For each: confirm contents are truly historical; consolidate where appropriate. | claude-row45-2026-06-11 | 2026-06-11 | DONE | cleanup/top-archive-audit | **Audit + execution.** All 5 user-mentioned dirs now consolidated. Top-level `_ARCHIVED_NOV25/` does not exist; UI-level `UI/_ARCHIVED_NOV25/` (28 files, Nov-25-2025 module-system migration snapshot) was missed in initial scan and caught during verification → moved in batch D. Audited 5 dirs total: `archive/` (13 subdirs, 636 files, ~40M), `ARCHIVE_OCT30_2025/` (3 subdirs, 14 files, 140K), `UI/ARCHIVE_OLD_UI_20251030_223356/` (12 files, 1.8M), `UI/components_ARCHIVED/` (5 files, 97K), `UI/_ARCHIVED_NOV25/` (28 files). All historical — no code imports from any. 2 JSX files in `UI/components_ARCHIVED/` are 100% dead (vanilla-JS SPA can't compile JSX). Overlap with `docs/archive/` (row 47 result): only 3 basenames match — keep both trees. Findings doc: `docs/agents/ROW_45_TOP_LEVEL_ARCHIVE_AUDIT.md`. **Followup executed (5 commits, 58 file ops)**: 3 UI-level archive dirs moved (UI/ARCHIVE_OLD_UI_20251030_223356/ → archive/ui_archives_20251030/ 12 files; UI/components_ARCHIVED/ → archive/ui_components_archived/ 5 files; UI/_ARCHIVED_NOV25/ → archive/ui_archives_20251125/ 28 files); 2 exact-dup/'_ copy' HTMLs prefixed `_DUPLICATE_`; 9 regenerable HTML dashboards + 2 git-log TXT dumps prefixed `_ARCHIVED_`; 3 DEPRECATION_NOTICE.md added; CLAUDE.md line 139 updated.
| 46 | `docs/` directory consolidation | docs | The 15 .md at root + subdirs. Promote what should be canonical. Move dated fix logs to `docs/archive/`. | claude-row46-2026-06-11 | 2026-06-11 | DONE | cleanup/docs-consolidation | 4 batches, 22 file ops. 13 .md from docs/ root + 3 from docs/features/ + 6 SYNERGY_ files → docs/archive/. Updated 4 broken refs in docs/synergy/README.md. Removed 2 empty subdirs (docs/features, docs/synergy/archive). Note: docs/icons/ (27 SVG/PNG) and docs/Fontawesome/ (15MB font install) are frontend assets misplaced in docs/ — flag for future row. |
| 47 | `docs/archive/` internal cleanup | docs | 358 files already there. Verify categorization; split into topic sub-archives where appropriate. | claude-row47-2026-06-11 | 2026-06-11 | DONE | cleanup/docs-archive | 17 batches; 271 file ops (343→602 final); 2 new subdirs (user, thread); absorbed to 5 existing (tools, microsoft_365, kanban, google_workspace, platforms/Shopify); 8 non-md moved to archive/test_scripts/; 3 google_workspace subdirs consolidated to 1; HTML link rot noted |
| 48 | `.github/` directory cleanup | docs | The 40+ files. Cross-link to canonical docs; archive superseded analyses; retire `copilot-instructions.md.disabled`; **process `copilot-instructions.md` LAST** (row 49). | claude-row48-2026-06-12 | 2026-06-12 | DONE | cleanup/github-cleanup | **3 batches, 35 file ops.** 34 .md prefixed `_ARCHIVED_` in place (19 calculator-group + 14 misc dated analyses + 1 analysis/BATCHED_RENDERING_ANALYSIS). 1 `.disabled` retired (.github/copilot-instructions.md.disabled → archive/copilot-instructions_disabled_nov2025/, with DEPRECATION_NOTICE.md). Final `.github/`: 6 canonical .md (ORG_CREDENTIALS, VECTOR_DB_DEVELOPER_REFERENCE, VECTOR_DB_ORG_ALIGNMENT, MODULE_VISIBILITY_ARCHITECTURE, SVG_CAD_GENERATION_RULES, AI_DOCUMENTATION_CONSOLIDATION_INSTRUCTIONS) + 1 active copilot-instructions.md (row 49) + 1 TEST_TEMPLATE.py + 27 prompts/ + 3 prompts/archive/ + 2 workflows/ + 35 _ARCHIVED_ files. 0 broken refs in CLAUDE.md / README / README_V11.md. **Row 49 is now unblocked** — copilot-instructions.md is the only remaining .md to rewrite, and all canonical targets still exist. |
| 49 | `.github/copilot-instructions.md` rewrite | docs | After every other doc row is done, rewrite this to point only at canonical docs. ~40 inbound links. | | | TODO | | **Process LAST.** |

> **Total: 49 rows.**
> Rows 30+31 duplicate work in rows 9+12. If the upstream row is DONE, the sidebar files just need verification — treat the internal module rows as light follow-ups, not full traces.

---

## Per-feature "trace and verify" output template

For any `code-trace` row, the agent must produce this map in the report:

```markdown
### Trace map for <feature>

**Files involved (verified live):**
- `path/to/file.py` — imported by [list], referenced in [docs/route/callers]
- ...

**Files involved (orphaned, candidate for archive):**
- `path/to/old_script.py` — last modified 2025-09-14, no importers, no doc references
- ...

**Doc claims verified:**
- ✅ `<doc claim>` confirmed by `path/to/code.py:line`
- ❌ `<doc claim>` contradicted by `path/to/code.py:line` — RECOMMEND: update the doc

**Code claims verified:**
- ✅ `<doc path>` still exists
- ❌ `<doc path>` no longer exists — RECOMMEND: update the doc to remove the reference

**Dead code found (scripts that do not seem to be imported or referenced):**
- `path/to/dead.py` — heuristic match
- ...

**Dead docs found (files that contradict current code or are stale fix logs):**
- `path/to/stale.md` — last touched >6 months, contradicts migration 051
- ...
```

This is the minimum report shape for any `code-trace` row.

---

## Chain of custody

> Append a one-line entry per agent session: `YYYY-MM-DD | <feature> | <branch> | <PR-link> | <files-moved> | <status>`.
> Never edit past entries. Only append.

```
2026-06-11 | bootstrap | n/a | n/a | Created tracker (49 rows) | DONE
2026-06-11 | seed | cleanup/jun-2026 | local-commit-f5b76ad8 | Added CLAUDE.md + tracker + 3 prompts to staging worktree (5 files, 1653 insertions) | DONE
2026-06-11 | sync | cleanup/jun-2026 | local-merge-007f029d | Merged v11@0cf2f9f9 (perf hotfix: 5 files, 864+/91-) into cleanup branch; v11 pushed to gerardo | DONE
2026-06-11 | docs-archive | cleanup/docs-archive | local-branch-d9312fce+ | Row 47 done: 17 batches, 271 file ops. New subdirs: user/, thread/. Absorbed into existing: tools/, microsoft_365/, kanban/, google_workspace/, platforms/Shopify/. 8 non-md anomalies moved to archive/test_scripts/. 3 google_workspace* subdirs consolidated to 1. HTML link rot (1094 stale refs in archive/timelines_and_reports/ai_agents_timeline.html) noted for row 49. | DONE
2026-06-11 | docs-consolidation | cleanup/docs-consolidation | local-branch-c5a20e4c+ | Row 46 done: 4 batches, 22 file ops. 13 .md from docs/ root + 3 from docs/features/ + 6 SYNERGY_ files moved to docs/archive/. 4 broken refs in docs/synergy/README.md fixed. 2 empty subdirs removed (docs/features, docs/synergy/archive). Flagged: docs/icons/ (27 SVG/PNG) and docs/Fontawesome/ (15MB) are frontend assets misplaced in docs/ — for future row. | DONE
2026-06-11 | top-archive-audit | cleanup/top-archive-audit | local-branch-3fc95392 | Row 45 done: read-only audit + execution. 5 dirs audited: archive/ (13 subdirs, 636 files, ~40M), ARCHIVE_OCT30_2025/ (3 subdirs, 14 files, 140K), UI/ARCHIVE_OLD_UI_20251030_223356/ (12 files, 1.8M), UI/components_ARCHIVED/ (5 files, 97K), UI/_ARCHIVED_NOV25/ (28 files). Top-level _ARCHIVED_NOV25/ doesn't exist; UI-level one was missed in initial scan, caught in verification. 2 JSX files in UI/components_ARCHIVED/ are 100% dead code (vanilla-JS SPA). Overlap with docs/archive/ (row 47): only 3 basenames match — keep both trees. **Followup: 5 commits, 58 file ops.** 3 UI-level archive dirs moved (UI/ARCHIVE_OLD_UI_20251030_223356/ → archive/ui_archives_20251030/ 12 files; UI/components_ARCHIVED/ → archive/ui_components_archived/ 5 files; UI/_ARCHIVED_NOV25/ → archive/ui_archives_20251125/ 28 files). 2 HTMLs prefixed _DUPLICATE_ (md5-verified). 9 regenerable HTML dashboards + 2 git-log TXT dumps prefixed _ARCHIVED_. 3 DEPRECATION_NOTICE.md added. CLAUDE.md line 139 updated. Findings doc: docs/agents/ROW_45_TOP_LEVEL_ARCHIVE_AUDIT.md. | DONE
2026-06-12 | github-cleanup | cleanup/github-cleanup | local-branch-8c1cead3+ | Row 48 done: .github/ cleanup. 3 batches, 35 file ops. 34 .md prefixed _ARCHIVED_ in place (19 calculator-group + 14 misc dated + 1 analysis subdir). 1 .disabled retired (copilot-instructions.md.disabled → archive/copilot-instructions_disabled_nov2025/, with DEPRECATION_NOTICE.md). Final .github/: 6 canonical .md + 1 active copilot-instructions.md (row 49) + TEST_TEMPLATE.py + 27 prompts/ + 3 prompts/archive/ + 2 workflows/ + 35 _ARCHIVED_ files. 0 broken refs in active docs. **Row 49 is now unblocked** — copilot-instructions.md is the only remaining .md to rewrite, and all canonical targets still exist. | DONE
2026-06-12 | integration-dirs-audit | cleanup/integration-dirs-audit | local-branch-f94a9c94+ | Row 43 done: 2 batches, 117 file ops. 6 orphaned integration dirs moved under archive/ (Woocommerce/, Cloudflare/, Render_backend/, Supabase/, tslot_bed_frame_docs/, temp_v9_comparison/). 4 unused files extracted from Microsoft_365_Connection/ to archive/Microsoft_365_Connection_unused/ (with DEPRECATION_NOTICE.md). 2 dirs KEPT at top level (load-bearing): google_workspace/ (4+ live importers) and Microsoft_365_Connection/microsoft365_oauth_manager.py (the only live file in that dir). CLAUDE.md line 139 fixed: prior wording incorrectly listed google_workspace/ and Microsoft_365_Connection/ as 'historical'; rewrote to make the active/historical split explicit. 0 broken refs. **Row 49 still pending** (deferred — needs to read 60K of copilot-instructions.md first to do a faithful rewrite). | DONE
```

---

## Definition of done for this round

The cleanup round is "done" when **all 49 rows are in `DONE` or `SKIPPED` (with reason) status**, **no live code imports from an archived path**, **every link in `.github/copilot-instructions.md` and `CLAUDE.md` resolves to a file that exists**, and **a final `ARCHIVE_CLEANUP_SUMMARY_JUN11_2026.md` is written at the repo root**.

---

## Out of scope (do not include)

- The staging copy itself — we work *in* it, we don't archive it.
- Anything in `node_modules/`, `.git/`, `.pytest_cache/`, `.vscode/`, `__pycache__/`.
- Generated artefacts (BGE model files, lockfiles, `package-lock.json`, `*.pyc`).
- The `archive/` and `docs/archive/` subdirectories themselves (they are the *result* of cleanup, not candidates).
- Runtime data dirs: `data/`, `exports/`, `logs/`, `templates/`, `marketing/`, `examples/`, `frontend/` (if active).
- This tracker file itself.

---

## Conflict resolution

If two agents claim the same row, the **earlier timestamp** in the `Owner` column wins. The second agent must pick a different row.

If you discover that a `DONE` row actually needs more work (e.g. a doc was missed, a script was wrongly archived), do **not** re-open the row silently — open a new row at the bottom of the table that references the original row, and note the regression in chain of custody.

---

## Promote-to-canonical workflow (after each per-feature pass)

1. Agent opens a PR in the **staging copy**: `AI_Agents_V11 - Copy (15)\AI_agents`.
2. User reviews the diff in the staging copy.
3. If approved, user runs the same `git mv`/`git rm`/edits in the canonical `AI_Agents_V11` (or `git diff` + apply).
4. The agent updates the tracker to mark the row `DONE`.
5. The chain-of-custody log records both the staging PR and the canonical commit hash.
