# GitHub Copilot Instructions — AI Agents Platform (V11)

> **Status (2026-06-12):** This file has been rewritten as a thin pointer doc.
> The canonical source of truth for repo overview, architecture, conventions,
> and workflow is **[CLAUDE.md](../CLAUDE.md)** at the repo root. Per-topic
> deep-dives live in `.github/`. **Read those first**; this file only adds
> Copilot-specific notes that are not in those docs.

---

## 1. Start here — read in this order

1. **[CLAUDE.md](../CLAUDE.md)** — repo overview, architecture, coding
   standards, agent rules, dev commands, security, AI/tool-calling
   conventions, and the documentation-maintenance workflow. The single
   source of truth.
2. **[README.md](../README.md)** and **[README_V11.md](../README_V11.md)** —
   product overview and getting started.
3. The topic deep-dives in §2, loaded on demand.

## 2. Topic deep-dives (canonical `.github/*.md`)

If you're working on one of these subsystems, read the linked doc — it
will have more detail than any summary here, and the code has drifted
away from older summaries.

| Subsystem | Canonical doc |
|---|---|
| Org / team / role / credential architecture (4-tier resolver) | [`.github/ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md`](ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md) |
| Vector DB (pgvector primary, Pinecone secondary) | [`.github/VECTOR_DB_DEVELOPER_REFERENCE.md`](VECTOR_DB_DEVELOPER_REFERENCE.md) |
| Vector DB org-alignment history (April 2026) | [`.github/VECTOR_DB_ORG_ALIGNMENT_ANALYSIS_APR29_2026.md`](VECTOR_DB_ORG_ALIGNMENT_ANALYSIS_APR29_2026.md) |
| Sidebar / module catalog / role gating | [`.github/MODULE_VISIBILITY_ARCHITECTURE.md`](MODULE_VISIBILITY_ARCHITECTURE.md) |
| SVG / CAD diagram generation | [`.github/SVG_CAD_GENERATION_RULES.md`](SVG_CAD_GENERATION_RULES.md) |

> **Heads up:** the 6th `.md` in this directory,
> `.github/AI_DOCUMENTATION_CONSOLIDATION_INSTRUCTIONS.md`, is **stale**
> (last touched January 2026, pre-CLAUDE.md). It's scheduled to be
> archived in the next cleanup round (F7). Don't follow its "consolidate
> into 22 master docs" instructions — CLAUDE.md §16 is the current doc
> workflow.

## 3. Repo-at-a-glance (mirrored from CLAUDE.md §1-§2)

A multi-tenant AI orchestration platform. Single Flask backend serving a
vanilla-JS single-page application (`UI/business-ai-platform-v2.html`,
~1.5 MB). Deployed to **Render** (auto-deploys from `gerardovsa/Ai_Agents`
`v11` branch) with **Supabase** as the primary database.

**4 AI providers** (migration 051): `anthropic`, `openai`, `deepseek`,
`MiniMax`. Only `MiniMax-M3` and certain Anthropic models support
Interleaved Thinking content blocks — do not enable `thinking` on
text-only models (they will error or silently drop the parameter).

**Plugin module system**: `UI/modules_external/<module>/` with JSON tool
schemas + Python wrapper implementations. Auto-discovered at Flask
startup by `tools/module_plugin.py`.

**Multi-agent chat**: Prime + 26 NATO-named agents (Alpha-1 → Zulu-26).
Thread-based with drag-and-drop assignment.

## 4. Hard rules (read these or break the build)

- **UTF-8 without BOM** for every `.js`/`.html`/`.css`/`.json` you touch.
  PowerShell edits can re-introduce BOM. Run `.\.vscode\fix-bom.ps1`
  before every commit. BOM breaks ES6 module loading in production.
- **Never commit secrets.** Use `.env` locally, the
  `organisation_platform_credentials` table (Fernet-encrypted) in prod.
- **Never bypass `@require_auth` or RLS.** A 401/403 is doing its job;
  do not silence it.
- **Never add a hardcoded `user_id = 1`.** Use `g.rls_user_id` from the
  decoded JWT. Search audits: `git grep -nE "user_id *= *1"`.
- **Never execute model-supplied code strings.** The `python_exec` tool
  uses `RestrictedPython`; respect it.
- **Migrations must be idempotent** — `IF NOT EXISTS`, `ADD COLUMN IF NOT
  EXISTS`, `INSERT … ON CONFLICT DO NOTHING`. Once a migration runs in
  any environment, never edit it; write a new one. The authoritative set
  is `AI_infrastructure/migrations/`. The legacy trees
  (`supabase_migrations/`, `database_migrations/`, `database/`,
  `migrations/`) are frozen.
- **Don't refactor archived code.** `AI_infrastructure/core/archived/`,
  `*.copy.py`, and the `.github/_ARCHIVED_*.md` files are read-only.
- **Conventional Commits** (`type(scope): summary`); deploy with
  `git push gerardo v11:v11`. `origin` was removed Feb 2026 — do not
  re-add.

## 5. Where to find things (file map)

| If you're looking for… | Look in… |
|---|---|
| Flask app entry point | `AI_infrastructure/flask_app.py` |
| All database access | `AI_infrastructure/shared/database_utils.py` (`execute_query()`) |
| Tool registry | `tools/registry_v3.py` (`@tool_executor` decorator) |
| Auto-discovered module plugins | `tools/module_plugin.py` |
| Frontend SPA (1.5 MB) | `UI/business-ai-platform-v2.html` |
| Sidebar modules | `UI/modules_internal/` (built-in), `UI/modules_external/` (plugins) |
| Migrations (authoritative) | `AI_infrastructure/migrations/NNN_*.sql` |
| Credentials / Fernet encryption | `AI_infrastructure/shared/credential_crypto.py` |
| Org / team / role routes | `AI_infrastructure/routes/organisation_credentials_routes.py` |
| Connection-leak audit | `AI_infrastructure/tools/audit_connection_leaks.py` |
| JWT decode + RLS context | `set_rls_context_from_jwt()` in `flask_app.py` |

## 6. Pre-commit checklist

```powershell
# 1. Strip BOM from any JS/HTML/CSS/JSON you touched
.\.vscode\fix-bom.ps1

# 2. Audit for hardcoded user_id or request.args.get('user_id')
git grep -nE "user_id *= *1"
git grep -nE "request\.args\.get\(['\"]user_id['\"]"

# 3. Conventional Commits + push to gerardo/v11
git commit -m "type(scope): summary"
git push gerardo v11:v11
```

## 7. What this file used to be

Prior to 2026-06-12, this file was a 1,448-line encyclopedic doc that
duplicated content now consolidated in CLAUDE.md and the 5 canonical
`.github/*.md` docs above. Per the documentation-maintenance workflow
in CLAUDE.md §16, it has been reduced to a thin pointer. The prior
content is preserved in `git log` on this file for archaeology.

**Link rot fixed in this rewrite:**
- `woocommerce_v4_exemplar_status.md` (old line 674) — referenced a
  ticket file that was moved to `archive/` during the docs-archive row
  (2026-06-11, row 47). The WooCommerce module V4 migration is still an
  open ticket; it now lives in code (`UI/modules_external/woocommerce/`)
  and the module's own README, not in a status doc.

**Stale content retired:**
- "Troubleshooting: InHouse Print Database Access (Jan 5-13, 2026)"
  section — specific to a closed fix window. The InHouse path-resolution
  quirk is now flagged in CLAUDE.md §13 risk #3.
- Environment-variables reference table — superseded by `.env.example`
  and `.env.master`, which are the contract for new env-var additions.
- Pre-commit hooks section — no GitHub Action runs lint/format. Pre-commit
  is local discipline; see CLAUDE.md §3 "Encoding — CRITICAL pre-commit"
  for the only hard pre-commit step.
- Module V4 migration status table — drifted; the truth now lives in
  CLAUDE.md §13 risk #2 (WooCommerce is the only completed module V4).

**Known stale HTML (not fixed here, recorded for the next round):**
`archive/timelines_and_reports/ai_agents_timeline.html` has ~1,094 stale
cross-references to docs that have been moved/archived. The HTML itself
is in `archive/` (read-only) and is a one-shot generated report, so the
broken refs are low-impact. Captured in the row-49 findings doc for
followup.
