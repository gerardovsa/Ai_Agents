# CLAUDE.md — AI Agents Platform (V11)

> **Purpose.** Persistent, repo-specific instructions for Claude Code and other AI coding agents working in `c:\Users\gpoli\GIT\AI_Agents_V11\AI_agents`. Mirrors the intent of `.github/copilot-instructions.md` but is **scoped for AI-agent operation**: precise, current as of **June 11, 2026**, and stripped of any instruction that is not directly actionable.
>
> **Last reviewed against:** `git log` head `bd5841ed` (June 11, 2026) and migrations `001..051`.
> **Companion authoritative docs (read on demand, do not duplicate):**
> - `.github/copilot-instructions.md` — long-form repo encyclopedia (NOTE: last touched April 30, 2026; treat as reference, not source of truth for new code)
> - `.github/ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md` — org/team/role/credential architecture (current; contains the 4-tier credential resolver)
> - `.github/VECTOR_DB_DEVELOPER_REFERENCE.md` — vector DB quick reference for agents
> - `.github/VECTOR_DB_ORG_ALIGNMENT_ANALYSIS_APR29_2026.md` — vector DB gap analysis + change history
> - `.github/MODULE_VISIBILITY_ARCHITECTURE.md` — sidebar / module catalog / role gating
> - `.github/SVG_CAD_GENERATION_RULES.md` — required for any SVG/CAD diagram generation
> - `ARCHIVE_CLEANUP_PLAN.md`, `ARCHIVE_CLEANUP_SUMMARY_NOV30.md`, `ARCHIVE_SAFETY_VERIFICATION.md` — **the precedent for any doc-cleanup task**; read before launching a doc-audit (see §16)
> - `ARCHIVE_CLEANUP_TRACKER.md` (repo root) — **the live tracker** for the active cleanup round. One row per item, append-only chain of custody. Read this before claiming any work, and update it when you finish. See the per-feature cleanup prompt for the contract.
> - `docs/agents/PER_FEATURE_CLEANUP_PROMPT.md` — the **per-feature cleanup prompt**. Hand this to an agent (or paste into the chat) when claiming a tracker row.
> - `docs/agents/CLEANUP_BOOTSTRAP_PROMPT.md` — the **bootstrap prompt** (run once, seeds the tracker).
> - `docs/agents/CLEANUP_FINALIZER_PROMPT.md` — the **finalizer prompt** (run once at the end, verifies and writes the round summary).

---

## 1. Project Overview

A **multi-tenant AI orchestration platform** (a.k.a. "InHouse Print / BusinessAiSuite"). Single Flask backend serving a vanilla-JS single-page application. Deployed to **Render** (auto-deploys from `gerardovsa/Ai_Agents` `v11` branch) with **Supabase** as the primary database.

**Core capabilities**
- Multi-agent chat (Prime + 26 NATO-named agents Alpha-1 → Zulu-26), persistent threads, drag-and-drop assignment.
- Org / team / role hierarchy (viewer / member / manager / admin / owner) with a Fernet-encrypted **credential vault** and a per-org module enable/disable system.
- Plugin module system (`UI/modules_external/`) for Shopify, WooCommerce, Xero, AusPost, InHousePrint, etc. Each module exposes JSON tool definitions + Python wrapper implementations.
- Vector search (pgvector primary, Pinecone secondary) with chunked document upload, three embedding providers (local BGE, Voyage, OpenAI).
- Synergy Kanban, thread visibility, real-time WebSocket presence, automation scheduler, voice transcription, document processing.

**Tech stack (verified, current)**
| Layer | Tech |
|---|---|
| Backend | Flask 3.0.0, Flask-SocketIO 5.5.1, Flask-CORS 4.0.0, waitress / gunicorn (gevent) |
| Database | Supabase Postgres + `psycopg2-binary` + `supabase-py` (pinned `<3.0`); pgvector extension |
| AI clients | `anthropic>=0.40.0` (reused for MiniMax via `base_url`), `openai==1.35.0` (DeepSeek uses OpenAI-compat), local BGE via `sentence-transformers` |
| Voice | `openai-whisper` (deferred import to keep cold-start fast — commit `0ca656f5`) |
| Data / calc | `pandas==2.3.3`, `numpy>=1.26.4`, `asteval>=1.0.7`, `RestrictedPython>=6.0` |
| Integrations | `xero-python`, `ShopifyAPI`, `WooCommerce`, `pinecone>=3.0.0`, `qdrant-client`, `cadquery==2.6.1` |
| Auth | `PyJWT==2.8.0`, `bcrypt==4.0.1`, `cryptography>=42.0.0` (Fernet) |
| Frontend | Single `UI/business-ai-platform-v2.html` (~1.5 MB), vanilla JS, FontAwesome, no framework. Sidebar modules in `UI/modules_internal/` and `UI/modules_external/`. |
| Deploy | Render + `.github/workflows/database-checks.yml`, `docker-build.yml` |

**4 AI providers (as of June 11, 2026, migration 051)**
1. `anthropic` — primary, full feature set
2. `openai` — GPT-4, embeddings (`text-embedding-3-small` 768-dim)
3. `deepseek` — OpenAI-compatible
4. `MiniMax` — Anthropic-compatible (`https://api.minimax.io/anthropic`); **only `MiniMax-M3` supports Interleaved Thinking**; other M-series are text-only

---

## 2. Repository Structure

> Conventions: top-level directories have **single responsibility**. Cross-cutting concerns go in `AI_infrastructure/shared/`. Never put business logic in route files.

```
AI_agents/                                       (this repo root, package.json "name": "ai_agents")
├── AI_infrastructure/                           # Backend (Flask app, routes, core, auth, shared utilities, migrations)
│   ├── flask_app.py                             # ENTRY POINT — registers all blueprints, WS handlers, RLS context
│   ├── flask_integration.py                     # Legacy V3 entry (kept for some scripts)
│   ├── run_flask_no_reload.py                   # Dev server w/o auto-reload
│   ├── run_tests.py                             # Local test runner
│   ├── auth/                                    # JWT, MFA, permission checker, credential encryptor/injector/tester
│   ├── builders/                                # system_prompt_builder, tool_schema_converter
│   ├── config/                                  # logging_config, oauth_config
│   ├── core/                                    # unified_ai_client, unified_session_manager, combined_agent_worker,
│   │                                           # tool_executor, tool_processor, prompt_injection_manager,
│   │                                           # module_blueprint_loader, confirmation_manager, streaming_manager,
│   │                                           # text_extractor, document_converter, ip_location, …
│   ├── database_toolkit/                        # CLI for DB inspection
│   ├── meta_tools/                              # smart_tool_selector / instructor / platform_guide_provider
│   ├── migrations/                              # NNN_short_name.sql — all idempotent. Currently 001…051 + 999
│   ├── routes/                                  # ~50 Flask blueprints (agent_v4, auth, oauth, chat, vector_db, …)
│   ├── shared/                                  # database_utils (execute_query), credential_crypto, org_credentials_loader,
│   │                                           # platform_credentials_loader, db_connection_wrapper, rls_session_manager,
│   │                                           # circuit_breaker, connection_leak_detector, svg_post_processor
│   ├── sync/                                    # cross-service sync helpers
│   ├── tests/                                   # targeted unit tests
│   ├── threads/                                 # ThreadManager models / constants / exceptions
│   ├── tools/                                   # smart_tool_selector + audit_connection_leaks
│   ├── utils/                                   # logger, validators, formatters, file_storage, token_counter, error_handler
│   └── workspace/                               # workspace / invitation / access_control
│
├── UI/                                          # Frontend (no bundler — direct script tags)
│   ├── business-ai-platform-v2.html             # MAIN SPA. Vanilla JS, contains OrgManager, ModuleManager, AppState, ThreadManager
│   ├── pages/                                   # (currently sparse — weather-widget.html)
│   ├── fragments/                               # (currently sparse)
│   ├── modules_internal/                        # Built-in sidebar modules: vector_database, communication-hub, messages,
│   │                                           # agents, automation, notifications, internal-docs, components
│   └── modules_external/                        # Plugin modules (see §4 Architecture — Module Plugin System)
│       ├── shopify/, xero/, woocommerce/, auspost-shipping/, inhouse-print/, inhouse-kanban/,
│       │   quote-calculator/, customer-reactivation/, database-visualizer/, github/, render-management/,
│       │   local-filesystem/, dev-diagnostics/, stock-management/, cad-chat-renderer.js, ui-command-processor.js
│       └── manifest.json                        # Static module loader (being replaced by DB-driven `initModulesFromOrg()`)
│
├── tools/                                       # Tool implementations consumed by the registry
│   ├── registry_v3.py                           # @tool_executor decorator + RegistryV3 singleton
│   ├── module_plugin.py / module_plugin_loader.py
│   ├── implementations/                         # pinecone/, pgvector/, xero/, shopify/, … (Python tool wrappers)
│   ├── plugins/                                 # plugin loader
│   ├── schemas/                                 # JSON tool schemas
│   ├── migrations/                              # tool-DB sync migrations
│   ├── testing/                                 # tool test harness
│   ├── debug_version_hash.py, force_regenerate_embeddings.py, manage_semantic_cache.py
│   └── persistent_semantic_search.py, intelligent_discovery.py
│
├── tests/                                       # Top-level test scripts (calculator group runners, smoke tests, e2e)
├── docs/                                        # Misc long-form documentation (many files; treat as reference)
├── .github/
│   ├── copilot-instructions.md                  # Legacy 1449-line reference (April 30, 2026; partial)
│   ├── ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md
│   ├── VECTOR_DB_DEVELOPER_REFERENCE.md         # PRIMARY vector DB dev doc (June 11, 2026)
│   ├── VECTOR_DB_ORG_ALIGNMENT_ANALYSIS_APR29_2026.md
│   ├── MODULE_VISIBILITY_ARCHITECTURE.md
│   ├── SVG_CAD_GENERATION_RULES.md
│   ├── prompts/                                 # Domain-specific AI sub-agent prompts
│   └── workflows/                               # CI: database-checks.yml, docker-build.yml
│
├── .vscode/                                     # settings.json (UTF-8 no-BOM enforced), tasks.json, fix-bom.ps1
├── .claude/settings.local.json                  # Claude Code permission allowlist
├── .env.master                                  # All env-var keys (template, no real secrets)
├── .env.example                                 # Public-safe template — model for new env additions
├── requirements.txt                             # Pinned Python deps (grouped by function)
├── package.json / package-lock.json             # Only `three` + `manifold-3d` (for CAD viewer). Frontend has no build step.
└── runtime.txt                                  # Python version pin
```

**What NOT to place where**
- Business logic in route files → belongs in `AI_infrastructure/core/` or `tools/implementations/<provider>/`.
- Tool wrappers in route files → use `UI/modules_external/<module>/implementations/`.
- Secrets in source → use `.env` locally, `organisation_platform_credentials` table in prod (Fernet-encrypted).
- Frontend code outside `UI/` → it will not be served by Flask.

**Archived / deprecated — touch only with explicit instruction**
- `AI_infrastructure/core/archived/` — old `agent_worker.py`, `streaming_agent_worker.py`, `session_handler.py`, etc. Do not import from. **Freeze verified clean — June 12, 2026 (row 41); 0 live importers.**
- `flask_app copy.py`, `routes/* copy.py` — historical copies.
- `supabase_migrations/`, `database_migrations/`, `database_scripts/`, `migrations/`, `database/`, `database/` — multiple migration trees from earlier eras. The **only authoritative** set is `AI_infrastructure/migrations/`. Of the 5 listed: `database/`, `database_migrations/`, `supabase_migrations/` were already gone before row 44; `database_scripts/` and `migrations/` were moved under `archive/` during the row 44 audit (June 12, 2026).
- `ARCHIVE_OCT30_2025/`, `archive/` (top-level) — historical directories. Both audited:
  - `archive/` and `ARCHIVE_OCT30_2025/` audited June 11, 2026 (row 45 of `ARCHIVE_CLEANUP_TRACKER.md`)
  - `Woocommerce/`, `Cloudflare/`, `Render_backend/`, `Supabase/`, `tslot_bed_frame_docs/`, `temp_v9_comparison/` audited June 12, 2026 (row 43) and moved under `archive/`
- `archive/root_one_shot_row50/` — 428 one-shot root `.py` files (verify_*, test_*, check_*, analyze_*, add_*, audit_*, scan_*, find_*, bulk_*, backfill_*, fix_*, apply_*, …) extracted from repo root on June 12, 2026 (row 50). All 428 are standalone utilities with **0 importers** across the 1,153 non-archive `.py` files in the repo, 0 references in `.vscode/tasks.json` / `.github/workflows/`, and 0 references in any active doc. **Only 2 root `.py` files survive:** `get_supabase_credentials.py` (2 live importers — load-bearing) and `config.example.py` (contract template). Recovery: `git log --diff-filter=R -- archive/root_one_shot_row50/`.
- `google_workspace/`, `Microsoft_365_Connection/` (top-level) — **load-bearing** at top level despite the legacy "historical directories; leave alone" wording above. Both are actively imported by live route/core code. Verified June 12, 2026 (row 43): `google_workspace/` has 4+ live importers (oauth_routes.py, communication_routes.py, context_aware_ai.py, session_orchestrator.py, tools/implementations/ai_personal_tasks.py, …); `Microsoft_365_Connection/microsoft365_oauth_manager.py` is imported by `routes/microsoft_auth_routes_V2_FIXED.py`. The other 4 files in `Microsoft_365_Connection/` were extracted to `archive/Microsoft_365_Connection_unused/` (not imported by any code).
- `copilot-instructions.md.disabled` (Nov 2025 version).

---

## 3. Development Commands

> All commands are **PowerShell** unless noted; the project's tooling is Windows-first. Python is `C:\Python313\python.exe` (see `.vscode/settings.json`).

### Install / environment
```powershell
# Install Python dependencies (pinned in requirements.txt)
pip install -r requirements.txt

# Frontend has no build step (no React/Vue, no bundler). package.json only declares three + manifold-3d for CAD.
# No `npm install` is required for app code — only run if you touch the CAD viewer.
```

### Run the backend (local dev)
```powershell
# From repo root — starts Flask on the configured port (5000 or 5001)
cd AI_infrastructure
python flask_app.py
```
The script auto-loads `.env.master` (preferred) → `.env` → OS env vars. Production (Render) uses OS env vars.

### VS Code task shortcuts (`.vscode/tasks.json`)
- `🔍 Debug Version Hash`
- `🔄 Force Regenerate Embeddings`
- `📊 Check Semantic Cache Status`
- `🗑️ Invalidate Semantic Cache`
- `📈 Semantic Cache Stats`

### Database migrations
```powershell
# Run a specific migration (every migration script is self-contained + idempotent)
cd AI_infrastructure
python migrations/050_add_minimax_provider.sql   # may need a python wrapper; check filename
# OR for .py-based migrations:
python migrations/run_017_optimize_message_queries.py
```
Conventions for new migrations: `NNN_short_snake_case.sql`, `ON CONFLICT DO NOTHING` for INSERTs, `DO $$ BEGIN ... END $$` for conditional DDL, end with a `RAISE NOTICE` verify block.

### Encoding — CRITICAL pre-commit
```powershell
# Remove UTF-8 BOM from all JS/HTML/CSS/JSON files
.\.vscode\fix-bom.ps1
```
BOM breaks ES6 module loading in production. The setting is already enforced in `.vscode/settings.json` (`"files.encoding": "utf8"`, `autoGuessEncoding: false`), but PowerShell-based edits can re-introduce BOM. Run this before every commit.

### Tests
```powershell
# Local runner
python AI_infrastructure/run_tests.py

# Per-group calculator tests (top-level tests/)
python tests/run_all_tests.py
python tests/run_group2_tests.py
python tests/run_group3_tests.py
python tests/run_group4_tests.py
python tests/run_group5_tests.py
```
**Row 42 audit (June 12, 2026):** these 5 are the only top-level `tests/` scripts documented in CLAUDE.md. 2 dead files moved to `archive/top_level_tests_row42_dead/` (17.5MB log + 9K FRED-system test); 24 other top-level test files remain as load-bearing or recently-validated.
There is **no `pytest` config in repo root** and `package.json` test script just echoes an error — do not call `npm test`.

### Smoke checks (one-liners)
```powershell
# DB connectivity
python -c "from AI_infrastructure.shared.database_utils import execute_query; print(execute_query('SELECT version()', fetch_mode='value'))"

# Tool registry size
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print(len(r.tools), list(r.tools.keys())[:10])"

# Connection-leak audit
python AI_infrastructure/tools/audit_connection_leaks.py
```

### Git / deploy
```powershell
# ONLY remote is `gerardo` (PRODUCTION). Do NOT add or push to any other remote.
git status
git add <files>
git commit -m "type(scope): description"     # Conventional Commits — feat|fix|docs|style|refactor|perf|test|chore|build|ci|revert
git push gerardo v11:v11                    # Triggers Render auto-deploy
```
`origin` (InHouseGuy/BusinessAiSuite) was removed Feb 26, 2026 — do not re-add.

### Restart on crash
```powershell
Stop-Process -Name python -Force
cd AI_infrastructure
python flask_app.py
```

---

## 4. Architecture and Data Flow

### Request lifecycle
```
HTTP / WS
  → Flask (AI_infrastructure/flask_app.py)
    → @before_request: set_rls_context_from_jwt()       # decodes Authorization: Bearer <jwt>
        → sets g.rls_user_id, g.rls_org_id
    → @require_auth                                     # rejects with 401 if no/invalid token
    → Blueprint route                                   # AI_infrastructure/routes/*.py
        → permission check (role)                       # @require_role('admin' | 'manager' | …)
        → resolve_credentials(user_id, 'platform')      # 4-tier org_credentials_loader.resolve_credentials
        → execute_query(sql, params, fetch_mode=...)    # shared/database_utils.py — pooled, transactional
        → return jsonify(...)
    → Logging with [COMPONENT] tag                       # utils/logger_config.py
```

### AI request lifecycle (more involved)
```
User message
  → POST /api/agent/chat  (routes/agent_routes_v4.py, V4 modular architecture)
    → session_manager.get_or_create_session(thread_id)
    → initialize_ai_client(org)  (core/unified_ai_client.py)
        → routes to provider-specific _init_<provider>() — anthropic | openai | deepseek | MiniMax
        → MiniMax reuses anthropic.Anthropic(base_url="https://api.minimax.io/anthropic")
    → build system prompt  (builders/system_prompt_builder.py)
    → create_message() with tool schemas
        → provider dispatch (Anthropic, OpenAI, DeepSeek, MiniMax) — all share _process_anthropic
    → tool_use loop via combined_agent_worker.py
        → tool_executor dispatches to tools/registry_v3.py
        → module_plugin_loader auto-discovers UI/modules_external/<module>/tools/*.json
        → implementations are decorated with @tool_executor()
    → streaming back via Flask-SocketIO (ws_room thread_id)
    → DB write: messages table, token counts, tool_intelligence logger
```

### Frontend ↔ backend
- Single-page `UI/business-ai-platform-v2.html` holds all global state in vanilla-JS objects (`AppState`, `ThreadManager`, `MultiAgent`, `OrgManager`, `ModuleManager`).
- Sidebar module loading is **DB-driven** since May 2026: `initModulesFromOrg()` fetches `GET /api/org/modules/catalog`, gates each button by `data-module` + `data-org-min-role`, then applies `applyOrgRoleVisibility()`.
- All authenticated fetches send `Authorization: Bearer <jwt>`; the JWT is stored client-side and refreshed via `/api/auth/refresh`.
- WebSocket uses Flask-SocketIO (gevent async mode); thread presence (`join_thread` / `leave_thread` / `typing_indicator`) and AI streaming ride the same socket.

### Tool / plugin system
- `tools/registry_v3.py` holds the singleton `RegistryV3`. Tool implementations are decorated with `@tool_executor()`; tool schemas live as JSON in `UI/modules_external/<module>/tools/*.json`.
- Modules are auto-discovered at Flask startup by `tools/module_plugin.py` (or `core/module_blueprint_loader.py` for blueprint-level modules).
- A module may also register a Flask blueprint (e.g. `UI/modules_external/shopify/shopify_routes.py`) — both routes and tools can coexist.

### 4-tier credential resolver
`AI_infrastructure/shared/org_credentials_loader.py:resolve_credentials(user_id, platform_key)` returns the first hit in this order:
1. **Personal** — `user_platform_credentials` (per-user)
2. **Org vault** — `organisation_platform_credentials` (Fernet-encrypted; preferred for shared integrations like Pinecone, Xero, Shopify)
3. **Sub-user inheritance (Tier 1.5, May 2026)** — owner credentials inherited by sub-users
4. **Env-var fallback** — `os.getenv()` (legacy; logs a warning, **do not add new callers**)

**Never** call `os.getenv('*_API_KEY')` directly for a platform key in new code — it bypasses the vault and breaks multi-tenancy (the GAP-V2/V3 pattern in the vector DB history).

### Database access
- All DB access goes through `execute_query()` in `AI_infrastructure/shared/database_utils.py` (pooled, transactional, RLS-aware).
- Connection pooling: `POOL_ENABLED=True` in `.env`. `AI_infrastructure/tools/audit_connection_leaks.py` scans route files for missing `conn.close()` / context-manager usage.
- Migrations: `AI_infrastructure/migrations/NNN_name.sql` — idempotent SQL only, no `psycopg2.connect` direct calls in app code.

### Error handling
- Tools return `{"success": bool, "data": ..., "error": str, "details": str?}`. Route handlers translate to HTTP.
- Frontend shows `AI provider overloaded` (commit `bd5841ed`) for upstream 529/overload; stops the pulsing icon.
- `utils/error_handler.py` centralises logging with tracebacks.

### Async / background
- APScheduler (`scheduler_routes.py`) for automation workflows.
- Celery is **declared** in `requirements.txt` but not actively wired in — prefer APScheduler or background threads (`_semantic_search_initialization_complete` pattern in `flask_app.py`).
- Whisper models are cached on `/data` (Render) and imported lazily (`0ca656f5`) — do NOT import `whisper` at module top level.

---

## 5. Coding Standards

These are **derived from the existing codebase** — follow them, do not invent new style.

### Language / framework
- **Python 3.13** (per `runtime.txt` and `.vscode/settings.json` interpreter path).
- **Flask + blueprints**, not Django/FastAPI for HTTP routes. (FastAPI/uvicorn are in `requirements.txt` for the new vector DB service shape, but the primary app stays Flask.)
- **Frontend: vanilla JS only** (no React/Vue/Angular, no TypeScript build). Use ES module syntax — **BOM-free UTF-8**.

### File encoding (CRITICAL)
- Save every `.js`, `.html`, `.css`, `.json` file as **UTF-8 without BOM**. The `.vscode/settings.json` enforces this, but PowerShell-based edits can re-introduce BOM. Always run `.\.vscode\fix-bom.ps1` before committing.
- Avoid emoji in source code literals (e.g. UI titles); use plain text. Emoji are OK in tooltips, but verify no corruption.

### TypeScript / Python typing
- Python: type hints are encouraged on new code. Existing modules vary — match the surrounding style.
- No TypeScript source files in the frontend. Inline JS uses JSDoc-style comments where helpful.

### Naming
- Python: `snake_case` for files, functions, variables; `PascalCase` for classes; `UPPER_SNAKE` for constants.
- SQL: `snake_case` for tables and columns; `PascalCase` for enums-like string columns (e.g. `ai_provider = 'anthropic' | 'openai' | 'deepseek' | 'MiniMax'`).
- JS: `camelCase` for vars/funcs, `PascalCase` for classes/objects (`OrgManager`, `ThreadManager`).
- Routes: kebab-case URL paths, `snake_case` Python identifiers.
- IDs in DB: where the table is a join/cart table, use composite PK; otherwise SERIAL or UUID. The repo mixes both — match the surrounding table.

### Imports
- **Never** `from AI_infrastructure.shared.database_utils import execute_query` at module top-level inside `tools/` — circular import risk. Import inside the function (see `@tool_executor` pattern below).
- Add `AI_agents` root and `AI_infrastructure/` to `sys.path` once in `flask_app.py`; other modules rely on that. Do not duplicate `sys.path` surgery in route files.

### Functions and components
- Tools return a `dict` with at least `{"success": bool, ...}`. Do not raise for predictable user errors.
- Flask routes return `(jsonify(...), status_code)` tuples.
- Frontend: prefer pure functions and small `Class` aggregators. Avoid giant closures.

### Error handling
- Wrap multi-step tool bodies in `try/except` and return a structured error. Include `details: traceback.format_exc()` for debugging.
- Migrations must be `IF NOT EXISTS` / `ON CONFLICT DO NOTHING`. Never crash on re-run.

### Logging
- Use `utils/logger_config.py` (`setup_logger`, `log_init`, `log_config`, `log_success`, `log_warning`, `log_error`).
- Prefix log lines with a `[COMPONENT]` tag, e.g. `[VECTOR_DB]`, `[AUTH]`, `[TOOL_EXEC]`.

### Comments and documentation
- File-level docstring for non-trivial modules.
- Functions get docstrings only if the contract is non-obvious.
- `AI_infrastructure/migrations/*.sql` get a `-- ============================================================================` banner header describing purpose + idempotency note.

### API design
- Prefix: `/api/<area>/<resource>[/<id>][/<verb>]`. No version in the URL — versioned by deployment.
- `POST` for create / non-idempotent, `PUT` for full update, `PATCH` for partial (rarely used), `DELETE` for soft-delete (set `is_active=FALSE`).
- JSON bodies for everything except file uploads (multipart).

### Database access
- Use `execute_query(sql, params, fetch_mode='all' | 'one' | 'value' | None)`. Use `fetch_mode=None` for INSERT/UPDATE/DELETE.
- Schema-qualify everything: `ai_infrastructure.<table>`. RLS policies require a JWT-scoped `g.rls_user_id`.
- Never `psycopg2.connect(...)` directly in new app code.

### UI components
- Reuse existing patterns: `OrgManager`, `loadPlatformCatalog()`, `renderPlatformGrid()`, `showApiKeyForm()`.
- Sidebar buttons get `data-module="<name>"` and `data-org-min-role="<role>"` for gating.
- Dynamic platform credential forms use `dyn-field-<name>` input IDs — the first field is mapped to `#apiKeyValue`; see `.github/copilot-instructions.md` §"How to Add a New Platform" for the contract.

### State management
- Frontend: `AppState` for global app state; per-feature objects (`ThreadManager`, `OrgManager`, `ModuleManager`, `MultiAgent`).
- `localStorage` for client cache only (`thread_assignments`, `multi_agent_state`).
- Backend: `unified_session_manager` for session scoping; no global mutable state.

### Accessibility
- All interactive elements use semantic HTML (`<button>`, `<a>`, `<input>` with `<label>`).
- Color is never the only signal — pair with text or icon.

### Security
- `@require_auth` on every authenticated endpoint. Validate with the JWT in `Authorization: Bearer …` header.
- Role gates via `@require_role('admin')` (or check `g.rls_user_id` matches ownership).
- Credential values are always stored Fernet-encrypted with `enc:v1:` prefix. See `AI_infrastructure/shared/credential_crypto.py`.
- Never log secrets, never include them in error messages.

---

## 6. Agent Operating Rules

These rules apply to **every** coding task in this repo. They override any default agent behaviour that conflicts.

1. **Inspect before editing.** Open the relevant file, read the surrounding pattern, then edit. No "blind" edits.
2. **Do not assume existence.** Verify a file, function, route, env var, dep, or command exists before referencing it. Use `Glob` / `Grep` / `Read`.
3. **Smallest safe change.** Solve the requested problem. Do not refactor adjacent code.
4. **No unrelated modifications.** Files you didn't intend to change should be untouched.
5. **Preserve architecture, naming, formatting, patterns.** Match the surrounding code; this is a long-lived repo with established conventions.
6. **No broad refactors** unless explicitly requested by the user.
7. **No rename / move / delete** without a clear reason documented in the response.
8. **No new dependencies** when the existing stack solves the problem. If a new dep is necessary, justify it and check version compatibility with the `requirements.txt` pins.
9. **Secrets stay out of source.** Never commit `.env`, real API keys, customer data, or production credentials. The `.env.master` is a **template only**.
10. **Don't weaken auth, authz, validation, or RLS.** A 401/403 is doing its job; do not silence it.
11. **No silent schema / API / env-var / data-format changes.** Anything that touches `ai_infrastructure.*` tables, public API contracts, or persisted data must be called out in the response.
12. **Backwards compatibility by default.** A breaking change needs explicit user approval.
13. **Validate by reading.** When the code says it does X, do not take the docstring's word — confirm.
14. **Run the narrowest relevant checks** after editing. Do not skip because "it's obvious."
15. **Report what you did not run.** If a test/check was not executed, say so.
16. **Never claim a test passed** unless it was actually executed successfully with output.
17. **Identify assumptions, risks, and incomplete work** explicitly in the response.
18. **Keep edits reviewable.** Avoid noisy formatting changes, especially in JSON/SQL.
19. **User instructions override repo preferences** unless doing so creates a security or data-loss risk — in which case surface the concern and ask.
20. **UTF-8 no-BOM, no emoji-in-source-literal, Conventional Commits.** Run `.vscode/fix-bom.ps1` before reporting "done."

---

## 7. Required Workflow

### Before editing
- Inspect the relevant files (use `Read`, not guess). Identify the existing pattern.
- Determine the root cause or implementation area; for broad/risky/architectural changes, write a brief plan first.
- Identify the file set likely to change. If a migration is needed, also list the migration filename.

### While editing
- Make focused, minimal changes.
- Follow existing repo patterns (see §5).
- Update types, tests, validation, and documentation **where the change requires it** — do not over-document.
- Avoid unrelated cleanup.
- Preserve backward compatibility unless told otherwise.

### After editing
Report, in this order:
- **Files changed** (paths only).
- **What changed** (1-2 sentences per file).
- **Why it changed** (the user need it solves).
- **Tests / checks executed** and the actual output.
- **Remaining risks** (anything not verified).
- **Assumptions** (anything you inferred without proof).
- **Recommended manual verification** (steps the user should run).

---

## 8. Testing Requirements

### Test layout
- `AI_infrastructure/tests/` — Python unit/integration tests for the Flask app.
- `tests/` — top-level scripts including calculator group runners (`run_group2_tests.py` … `run_group5_tests.py`) and e2e smoke tests (semantic search, vector DB, etc.).
- `AI_infrastructure/run_tests.py` — local Flask test runner.
- `tools/testing/` — tool-level test harness.

### Conventions
- No `pytest` config in repo root. Use `python <script>.py` style runners.
- When fixing a bug, **add a regression test** to the closest existing test file. Do not create a new test directory per fix.
- For a new feature, add at least one happy-path test. Mock external HTTP calls (`anthropic`, `openai`, `shopify`, `xero`, `pinecone`) so tests are offline.
- For an API change, hit the endpoint in a test (use `Flask.test_client()`).

### Run
```powershell
python AI_infrastructure/run_tests.py
python tests/run_all_tests.py
python tests/run_group3_tests.py     # example
```

### Definition of "tested"
A change is **tested** when the relevant test script has been executed and the output captured. State the command and a one-line summary of the result in the report.

---

## 9. Security and Privacy

### Secrets
- `.env`, `.env.master`, `.env.supabase`, `.env.vector_db_example` are **template files only**. Do not commit real values.
- Production secrets live in **Render env vars** and in the **`organisation_platform_credentials`** table (Fernet-encrypted with `CREDENTIAL_ENCRYPTION_KEY`).
- Generate a new Fernet key with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`. **Changing this key makes all existing encrypted credentials unreadable** — coordinate with the team.

### AuthN / AuthZ
- JWT in `Authorization: Bearer …`. Decode in `set_rls_context_from_jwt()` (registered as `@before_request` in `flask_app.py`); sets `g.rls_user_id`, `g.rls_org_id`.
- Every authenticated endpoint must have `@require_auth`. For org-scoped data, use the `g.rls_user_id`/`g.rls_org_id` directly — never trust a query-param `user_id`.
- Roles: `viewer` < `member` < `manager` < `admin` < `owner`. Role changes bump `users.jwt_version` to invalidate live tokens.
- Vault password (optional, per-org `bcrypt` hash) gates credential reveal.

### User data
- Threads, messages, and uploaded documents are scoped by `org_id` and/or `user_id`. RLS policies enforce this at the DB layer.
- Do not log message contents, API keys, OAuth tokens, customer names, or PII.
- The `credential_access_log` table records every `list | add | edit | delete | reveal | test` action with IP, user-agent, and timestamp.

### Uploaded files
- Stored under `data/` or in Supabase storage. Validate MIME type and size before persisting.
- Text extraction (`core/text_extractor.py`) is sandboxed via `RestrictedPython` for the `python_exec` tool.

### External API calls
- Wrap with the `circuit_breaker` (`AI_infrastructure/shared/circuit_breaker.py`) for any 3rd-party HTTP call that can fail.
- Never echo a 3rd-party error verbatim — sanitize to remove headers, tokens, internal hostnames.

### AI prompts and model responses
- The platform logs the **tool schema + outcome** to `tool_intelligence_logger`; it does **not** log the model response text in full by default.
- Treat model output as **untrusted**:
  - Validate every tool-call argument against its JSON schema before execution.
  - Never `eval()` / `exec()` model-supplied code. The `python_exec` tool uses `RestrictedPython`.
  - Sanitize any string inserted into HTML/JS (`markupsafe.escape` is already imported in `flask_app.py` for display names).
  - For markdown rendering, use a vetted renderer with safe defaults (no raw HTML pass-through).

### Prompt injection
- User content can contain adversarial instructions to subvert the agent. Treat chat content as data, not instructions. Strip `<system>` / `<assistant>` role markers from any user-supplied text before injecting into prompts.

---

## 10. AI and Tool-Calling Rules

### Providers
- 4 providers (migration 051): `anthropic`, `openai`, `deepseek`, `MiniMax`. All are routed via `AI_infrastructure/core/unified_ai_client.py`.
- Adding a provider: follow `.claude/memory/anthropic-compatible-providers.md` — reuse the `Anthropic` SDK class with a custom `base_url` when the provider is Anthropic-compatible. See also the in-repo `MiniMax` integration as a worked example.
- Org default provider is stored in `organisations.ai_provider` (CHECK-constrained to the 4 values). The CHECK constraint is widened by migration 051; future providers need a new migration.

### Thinking models (Interleaved Thinking)
- Only `MiniMax-M3` and certain Anthropic models support `thinking` content blocks. Maintain the allowlist in `combined_agent_worker.py` (`_PROVIDER_THINKING_MODELS`). Do **not** enable `thinking` on text-only models — they will error or silently drop the parameter.

### Tool schemas
- JSON Schema (OpenAI-style) in `UI/modules_external/<module>/tools/*.json`. The schema is converted to provider-native format by `AI_infrastructure/builders/tool_schema_converter.py`.
- Names are `snake_case`. Descriptions are short and explicit; they are what the model uses to choose the tool.

### Tool-call validation
- The model supplies `tool_use` arguments. Validate against the JSON schema in the wrapper **before** executing any side effect. On validation failure, return `{"success": False, "error": "Invalid arguments: <details>"}` — do not raise.

### Retry / fallback
- Per-tool retry is the wrapper's responsibility (exponential backoff for 5xx, 429). The `circuit_breaker` is for whole-integration failure.
- Provider-level fallback (e.g. anthropic → openai) is **not** currently implemented; do not invent it without an explicit ask.

### Token / context management
- `utils/token_counter.py` uses `tiktoken`. Real-time token counts via `/api/tokens/*` (see `routes/token_routes.py`).
- The agent worker trims context on overflow; do not change the trim policy casually.

### Prompt storage
- System prompts are built dynamically in `builders/system_prompt_builder.py`. Hard-coded "magic strings" are a smell — use the builder.

### Structured output
- Tools return JSON-serializable dicts. `Decimal` and `datetime` are converted via `convert_to_json_serializable()` in the InHouse wrapper; replicate that pattern for new wrappers.

### Cost controls
- BGE local embeddings are the default (free). Voyage / OpenAI embeddings are opt-in via the org vault credential.
- Voice transcription defers `whisper` import to keep cold-start <60s (commit `0ca656f5`).

### Untrusted model output
- Never execute a model-supplied `command` string. The `python_exec` tool uses `RestrictedPython`; respect that.
- File paths in tool args must be normalised and checked against an allowlist (no `..`, no `C:\`, no `/etc/`).
- HTML returned by the model must pass through the safe-renderer path before being inserted via `innerHTML`.

---

## 11. Database and Migration Rules

### Conventions
- All app tables live in the `ai_infrastructure` schema. Always schema-qualify: `ai_infrastructure.<table>`.
- Primary keys: SERIAL for new tables unless the table is distributed / needs UUID. `org_vector_documents.id` is UUID (`gen_random_uuid()`).
- Foreign keys: always `ON DELETE` specified — prefer `CASCADE` for owned data, `RESTRICT` for referenced lookups.
- Soft-delete pattern: `is_active BOOLEAN DEFAULT TRUE` + filter in queries.
- Audit columns: `created_at TIMESTAMPTZ DEFAULT NOW()`, `updated_at TIMESTAMPTZ DEFAULT NOW()` (use triggers or update explicitly).
- RLS: every per-org/per-user table must have an RLS policy keyed on `g.rls_user_id` / `g.rls_org_id`. New tables are not exempt.

### Migrations
- Filename: `NNN_short_snake_case.sql` (numbered, zero-padded if you go past 099). For Python-based migrations: `NNN_short_snake_case.py`.
- Header banner:
  ```sql
  -- ============================================================================
  -- Migration NNN: <Short Title>
  -- Created: <YYYY-MM-DD>
  -- Purpose: <one or two sentences>
  -- Idempotent: <yes / describe how>
  -- ============================================================================
  ```
- Idempotency: `CREATE TABLE IF NOT EXISTS`, `ADD COLUMN IF NOT EXISTS`, `INSERT … ON CONFLICT DO NOTHING`, `DO $$ BEGIN … END $$` for conditional DDL.
- Always end with a verify block (`RAISE NOTICE '…'` or a `DO $$ … END $$` check).
- Do not chain destructive operations. A migration that drops a column needs explicit user approval.

### Generated / managed artifacts
- `requirements.txt` is the source of truth for Python deps. Update it (don't hand-edit a `pip freeze`).
- `package.json` / `package-lock.json` are only for the three.js / manifold-3d viewer; touching them requires running `npm install` locally.
- Do not check in BGE model files (~440 MB). They are downloaded on first use into `/data/vdb_models/…` (Render) or `~/.cache/vdb_models/…` (local).

### Destructive operations
- Agents must **never** DELETE or TRUNCATE without explicit user instruction, and never against a table that holds user-generated content. For dev DBs, prefer soft-delete columns.

---

## 12. UI and UX Rules

### Design system
- FontAwesome for icons. Tailwind / Bootstrap are **not** used; the SPA is hand-rolled CSS in the same HTML file.
- Color palette: see `.vscode/settings.json` `peacock.color` (`#42b883`) and `workbench.colorCustomizations` (activity bar `#65c89b`).
- Reuse the **org / module / platform** pattern: `OrgManager`, `loadPlatformCatalog()`, `renderPlatformGrid()`, `showApiKeyForm()`.

### Sidebar module gating (post–May 2026)
- Every sidebar button should have `data-module="<name>"` and (for role-gated ones) `data-org-min-role="<role>"`.
- `initModulesFromOrg()` rebuilds Zone 2 from the DB. `applyOrgRoleVisibility()` hides role-gated items.
- The `UI/modules_external/manifest.json` is **being replaced** by DB-driven loading; do not add new modules there.

### Dynamic platform credential forms
- The `required_fields[0]` element of a `platform_catalog` row maps to `#apiKeyValue`. All subsequent elements render as `dyn-field-<name>` inputs.
- See `.github/copilot-instructions.md` §"How to Add a New Platform" for the full contract.

### Loading / empty / error states
- Every async UI section has a loading state (spinner or skeleton), an empty state (icon + "Nothing here yet" + primary action), and an error state (red banner + retry).
- For AI streaming, the `AI_REQUEST` / `AI_RESPONSE` banner pattern (commit `7e52ce70`) replaces older ad-hoc banners.

### Form validation
- HTML5 `required`, `type=email|number|url`, plus JS validation before submit.
- Display server-side validation errors inline beneath the offending field, not in a modal.

### Destructive actions
- Confirm before any delete / remove / revoke. Use a typed-confirmation pattern for irreversible actions (e.g. type the org slug to confirm org deletion).
- Soft-delete is the default; hard-delete requires admin+ role and a second confirmation.

### Accessibility
- Keyboard navigable. `aria-label` on icon-only buttons. Focus visible.
- Test with Tab order at least once when adding a new modal or sidebar section.

---

## 13. Known Risks and Fragile Areas

These are **real, repository-evidenced** risks — not generic advice.

1. **`.github/copilot-instructions.md` is stale** (last touched April 30, 2026). Several specific facts are wrong or out of date (MiniMax provider not listed, auto-deploy branch misnamed, vector DB section missing the May/June 2026 evolution). Do not rely on it as the source of truth; verify against migrations and code.

2. **WooCommerce module has unresolved 400 validation errors** — `woocommerce_v4_exemplar_status.md` is the open ticket. Only the WooCommerce module has completed the Module V4 pattern migration; 13 other modules are still pending it.

3. **InHousePrint path resolution** — `UI/modules_external/inhouse-print/implementations/inhouse_wrapper.py` does explicit `sys.path` surgery. Do not refactor that block without re-running the calculator + SQL tools. The bypass of `ToolUseAgent` is intentional and load-bearing (see `INHOUSE_TOOLS_COMPLETE_FIX_JAN13_2026.md`).

4. **`g.rls_user_id` in pre-existing route files** — any route that still uses `request.args.get('user_id', 1)` or `user_id = 1` is a **security bug** (GAP-V1 pattern). When touching any route file, check that the auth decorator is in place. Use `git grep "user_id *= *1"` and `git grep "request.args.get('user_id')"` as quick audits.

5. **BOM re-introduction** — even though `.vscode/settings.json` is correct, PowerShell `Set-Content` and some editors will write BOM. `.\.vscode\fix-bom.ps1` is a hard pre-commit requirement.

6. **Large single-file SPA** — `UI/business-ai-platform-v2.html` is ~1.5 MB. Many searches will be slow; use `Grep` with a path filter. Edits inside this file are risky because of inter-function coupling (search before adding globals).

7. **Vector DB chunk re-indexing on provider change** — switching embedding providers requires **re-uploading all documents** (different model spaces are not comparable). UI must surface this warning.

8. **BGE model snapshot path** — `tools/implementations/pgvector/pgvector_tools.py` loads from the local snapshot directory to avoid HF network calls. If the model is not cached, the first deploy downloads ~440 MB. Do not switch to a "load by model name" path — it broke prod in commit `a62b8f36`.

9. **Whisper cold-start** — `openai-whisper` and `torch` imports are deferred. Do not move them to top-level imports; commit `0ca656f5` shows the 57s cold-start regression it caused.

10. **`MiniMax` constraint cascade** — `organisations.ai_provider` CHECK constraint must be widened **at the same time** as adding a new provider to the catalogs (migration 051 fixes the gap from migration 050). Apply the same pattern for any future provider.

11. **Migration drift** — there are several legacy migration trees in the repo root (`supabase_migrations/`, `database_migrations/`, `database/`, `migrations/`). The **only** authoritative set is `AI_infrastructure/migrations/`. Do not add new files to the others. Status as of row 44 (June 12, 2026): `database/`, `database_migrations/`, `supabase_migrations/` were already gone; `database_scripts/` and `migrations/` were moved under `archive/` and are now historical.

12. **Archived code that is still imported** — `AI_infrastructure/core/archived/` contains copies of the agent worker. If an old `from core.archived.X import Y` exists anywhere, it is a leak to be fixed, not a feature. **Freeze verified clean — June 12, 2026 (row 41); 0 live importers; 0 leaks.**

13. **Hardcoded `user_id=1` "platform superuser"** — was retired. Any line containing `user_id = 1` outside of test fixtures is a bug.

14. **No CI lint** — there is no GitHub Action that runs lint, type-check, or test. Pre-commit relies on local discipline. Add the change to your report's "Tests / checks executed" honestly.

---

## 14. Files That Should Not Be Edited Manually

- `package-lock.json` — regenerate with `npm install`. Don't hand-edit.
- `requirements.txt` — edit by hand, but pin to exact versions when adding; the file is grouped by function with comments.
- `AI_infrastructure/migrations/NNN_*.sql` after deploy — once a migration has run in any environment, do not edit it; write a new migration.
- `UI/modules_external/manifest.json` — being replaced by DB-driven loading. Don't add new entries here.
- `UI/modules_external/quote-calculator/backend/query_library.py` (~5,958 lines) — generated / data-heavy; edit only via its generator.
- `AI_infrastructure/flask_app copy.py` and `AI_infrastructure/routes/* copy.py` — historical copies.
- BGE model snapshot files at `/data/vdb_models/…` or `~/.cache/vdb_models/…` — managed by `sentence-transformers`.
- `.env.master` — add new env-var **keys** to the template; never put real values.
- `AI_infrastructure/core/archived/*` — frozen. Do not import from. **Freeze verified clean — June 12, 2026 (row 41).**

---

## 15. Definition of Done

A coding task is **done** when **all** of the following are true:

- [ ] The requested behaviour is implemented and matches the user's spec.
- [ ] Files changed are exactly the set that needed to change (no drive-by edits).
- [ ] Type hints / validation are present where the change requires them.
- [ ] UTF-8-no-BOM verified for any `.js / .html / .css / .json` you touched (`.\.vscode\fix-bom.ps1`).
- [ ] A relevant test was added (bug fix → regression test; new feature → happy-path test).
- [ ] The narrowest relevant check was run; results reported honestly.
- [ ] Lint / type / build checks pass where practical (state which were skipped and why).
- [ ] Security and privacy rules preserved (no secrets, no weakened auth/RLS).
- [ ] Public API / DB schema / env-var changes are called out in the report.
- [ ] `git status` is clean of files you didn't intend to touch.
- [ ] Conventional Commits message is drafted (`type(scope): summary`).
- [ ] Report includes: files changed, what/why, tests run, risks, assumptions, manual verification steps.

---

## 16. Documentation Maintenance Workflow

> This section is the agent's playbook for the recurring task of *auditing, consolidating, and archiving* the 1,200+ `.md` files in this repository. The codebase produces more documentation than code in some sprints — this section exists to keep that under control.

### 16.1 Where documentation lives

| Location | Count (approx.) | Purpose |
|---|---|---|
| Repo root `*.md` | ~1,239 | Mix of runbooks, fix logs, analysis reports, contract specs. **Most should not be at the root.** |
| `docs/` | 15 (of 22 entries) | Long-form reference material, onboarding, architecture write-ups. |
| `.github/` | ~40 | Agent-instructions, prompts, workflows, deep-dive analysis (`ORG_CREDENTIALS_…`, `VECTOR_DB_…`, `MODULE_VISIBILITY_…`, `SVG_CAD_GENERATION_RULES`, `THREAD_VISIBILITY_…`, etc.) |
| `UI/<module>/docs/`, `UI/<module>/README.md` | varies | Per-module documentation. **Keep these in the module, not the root.** |
| `archive/documentation/` | 292 | Historical docs that have already been moved. **Treat as read-only.** |
| `archive/deprecated/<YYYY-MM-DD>/` | varies | Dated deprecation bundles, each with its own `DEPRECATION_NOTICE.md`. |
| `README.md`, `README_V11.md` | 2 | The two canonical entry points. **Edit, don't archive.** |

### 16.2 Established archive conventions (already in use)

The repo already has three patterns in flight. Use the one that fits:

1. **In-place prefix** — Rename the file to `_ARCHIVED_<original_name>.md` (or move into a directory prefixed `_ARCHIVED_<date>/`). **Use when:** the doc is still linked from current docs and you want a visible "do not use" marker without breaking links. Example: `.github/_ARCHIVED_ORGANISATION_CREDENTIALS_ARCHITECTURE_UPDATED_APRIL30_2026.md`.
2. **Categorised move** — `git mv <file> archive/<category>/`. Categories in use: `analysis_reports`, `calculator_history`, `database_utilities`, `deployment_scripts`, `deprecated`, `documentation`, `documentation_<TIMESTAMP>`, `routes`, `test_scripts`, `timelines_and_reports`, `unused_routes_dec7`, `xero`. **Use when:** the doc is genuinely historical and the category is clear.
3. **Dated deprecation bundle** — `git mv <files> archive/deprecated/<YYYY-MM-DD>/` and create a `DEPRECATION_NOTICE.md` inside it listing what was moved and why. **Use when:** a feature/module is being retired and its supporting docs should be retired together.

**Precedent process files** (read before doing a big cleanup):
- `ARCHIVE_CLEANUP_PLAN.md` — the most recent cleanup plan.
- `ARCHIVE_CLEANUP_SUMMARY_NOV30.md` — the most recent cleanup report.
- `ARCHIVE_SAFETY_VERIFICATION.md` — the safety/verification checklist used last time.

### 16.3 Doc classification — every file is one of these

When auditing, classify every `.md` into exactly one bucket. This is the "what to do" decision tree:

| Bucket | Definition | Action |
|---|---|---|
| **Canonical** | The single source of truth for an architectural decision, API surface, schema, or operational procedure. Stable, version-controlled, current. | Keep at original location. Cross-link from CLAUDE.md. |
| **Historical** | Once correct, but superseded by a newer doc. Dated, specific to a moment. | Move to `archive/documentation/` (categorised) or prefix with `_ARCHIVED_` if still linked. |
| **Scratch** | A debugging log, fix-summary, or analysis that was useful for one PR but not as durable reference. | Move to `archive/documentation/` or `archive/timelines_and_reports/`. |
| **Deprecated** | Documents a feature that has been removed. | Move to `archive/deprecated/<YYYY-MM-DD>/` with a `DEPRECATION_NOTICE.md`. |
| **Debug / personal notes** | Single-purpose analysis with no ongoing audience. | Move to `archive/analysis_reports/`. |
| **Contract** | A file that the code expects to find at a fixed path (e.g. `requirements.txt`, `package.json`, `README.md`, `LICENSE`). | Never archive. |
| **Runbook** | Step-by-step operational procedure (restart, deploy, recovery). | Keep at root or `docs/`. Promote to canonical if widely used. |

### 16.4 The single-source-of-truth rule

When two documents disagree, follow this precedence — **highest wins**:

1. **Migrations** — `AI_infrastructure/migrations/NNN_*.sql` is the truth for the database. If a doc says `is_active` is `VARCHAR` and the migration says `BOOLEAN`, the migration is right.
2. **Code** — `routes/*.py`, `core/*.py`, `shared/*.py`, `UI/*.html` are the truth for behaviour. If a doc says the credential resolver is 3-tier and the code is 4-tier, the code is right.
3. **The newest dated analysis** — between two analysis docs, the one with the later date in its filename or front-matter wins.
4. **The most recent doc with a "Last updated" header** — if no migrations or code touch the topic, pick the doc with the most recent update stamp.
5. **PR/issue author** wins for *intent* — if a doc contradicts code AND a recent PR/issue is open about it, surface the conflict in the report and let the user decide.

**Never silently delete a doc that contradicts the code.** File a "doc-stale" note in your report so the user can decide.

### 16.5 Doc-audit workflow (use this when asked to "clean up the docs")

This is the canonical procedure. **Do not skip steps.**

**Step 0 — Read the canonical docs first** (15 min, saves hours later):
- This `CLAUDE.md`
- The latest `.github/ORG_CREDENTIALS_*.md` and `.github/VECTOR_DB_DEVELOPER_REFERENCE.md`
- The most recent `ARCHIVE_CLEANUP_PLAN.md` and `ARCHIVE_CLEANUP_SUMMARY_*.md`
- The most recent `.github/copilot-instructions.md` (it still links to many docs)

**Step 1 — Inventory**:
```powershell
# Build a full file list with sizes and dates
Get-ChildItem -Recurse -Include *.md -File |
  Select-Object FullName, Length, LastWriteTime |
  Sort-Object FullName |
  Export-Csv doc_inventory.csv -NoTypeInformation
```

**Step 2 — Classify**:
For each file, decide: Canonical / Historical / Scratch / Deprecated / Debug / Contract / Runbook. Use Grep on the contents to find:
- The earliest "**Created:**" / "**Date:**" header → recency
- Cross-reference links (`](../path/...)`, `(../.github/...)`) → is it still part of the live graph
- Code citations (paths like `AI_infrastructure/...` or function names) → does the cited code still exist

**Step 3 — Verify claims** (sample, don't verify every line):
- For every "canonical" claim in a doc, run `Grep` for the cited path / function / table / column to confirm it still exists in code.
- For every "now supports X" claim, find the migration or PR that introduced it.
- For every "removed/retired" claim, confirm the file is actually gone.

**Step 4 — Propose, don't execute**:
Produce a table with columns: `file | current_path | proposed_action | proposed_path | reason | risk`. Stop and show the user. Do not `git rm` anything without approval.

**Step 5 — Execute only after approval**:
```powershell
# Always use git mv — preserves history
git mv <old_path> <new_path>

# After moving, fix inbound cross-references:
# - Update relative links in surviving docs
# - Update CLAUDE.md if it referenced the moved doc
# - Update .github/copilot-instructions.md (long but mechanical)
```

**Step 6 — Add a chain-of-custody entry**:
- If you created a new `archive/deprecated/<date>/` bundle, write a `DEPRECATION_NOTICE.md` listing what was moved, why, and the cleanup-plan filename.
- If you moved >20 files, write an `ARCHIVE_CLEANUP_SUMMARY_<MONTH>.md` in the repo root following the precedent of `ARCHIVE_CLEANUP_SUMMARY_NOV30.md`.

**Step 7 — Final report** to the user: total files moved, categories used, inbound links updated, residual risks (e.g. "3 files in root still reference an archived path"), and recommended follow-up.

### 16.6 Consolidation rules (when merging multiple docs into one)

- **Preserve the change log.** When consolidating, keep the original "Last updated" header of the surviving doc and append a `## Prior versions` section that lists the merged docs and the dates of their final versions.
- **Cite the merger in the doc's front-matter** — `**Merged from:** <list>` — so future agents know the lineage.
- **Do not delete the originals** in the same commit. First, move them to `archive/documentation/` (categorised). In a later commit (or the same PR, but as a separate commit), update the new doc. This keeps `git log` honest.
- **Naming the merged doc** — prefer the name of the *current* authoritative doc, not the oldest. E.g. keep `ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md` as the survivor, not the older `ORGANISATION_CREDENTIALS_ARCHITECTURE.md` (which should be archived).
- **Update inbound links** in `.github/copilot-instructions.md`, this `CLAUDE.md`, and any other docs that pointed to the merged-away file.

### 16.7 Update procedure (when code changes invalidate docs)

When you change code, check the doc graph:

1. `Grep` the codebase for the *exact* string of the changed API/symbol/table.
2. For each doc that mentions it, re-read the surrounding paragraph to see if the change makes it wrong.
3. Update the doc in the **same PR** as the code change.
4. Bump the doc's `**Last updated:**` header to today.
5. Add a one-line note to the doc's `## Change history` (if it has one).

Do not let the doc lag more than one PR behind the code. The legacy copilot-instructions.md is a cautionary tale of what happens when it does.

### 16.8 Doc safety rules (hard constraints)

1. **Never `rm` a `.md` file** — use `git mv`. Always recoverable.
2. **Never delete a file just because it looks old.** It may be linked from a 2-year-old issue, a customer's saved PDF, or an internal SOP. Archive it instead.
3. **Never silently break inbound links.** If you move a doc, find every other file that links to it and update the link.
4. **Never touch `README.md`, `README_V11.md`, `LICENSE`, `requirements.txt` headers, or `package.json` description fields** without explicit user approval.
5. **Never consolidate two docs that disagree on a fact** — surface the conflict in your report. The user must decide which version to keep.
6. **Never move a file into `archive/` that the agent's own tools still depend on.** Verify with `Grep` that no code, prompt, or workflow references the file before moving.
7. **Never delete `archive/` subdirectories en masse.** They are categorised for a reason; cleanup should be category-by-category.
8. **Never modify a doc that is named in the recent `ARCHIVE_CLEANUP_PLAN.md`** — that plan is the user's intent; follow it, don't second-guess it.

### 16.9 Quick reference: the doc cleanup commands

```powershell
# Inventory all markdown
Get-ChildItem -Recurse -Include *.md -File | Measure-Object

# Find the 50 largest .md files at the root (likely candidates for consolidation)
Get-ChildItem -Path . -Filter *.md -File | Sort-Object Length -Descending | Select-Object -First 50 Name, Length, LastWriteTime

# Find all .md files older than 6 months
Get-ChildItem -Recurse -Include *.md -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddMonths(-6) } | Select-Object FullName, LastWriteTime

# Find cross-references to a doc you're about to move
# (use Grep tool with output_mode=files_with_matches)
# pattern:  <relative-path-of-the-doc>

# Always move, never delete
git mv <old> <new>
```

### 16.10 Definition of "the docs are clean"

The doc set is considered clean when **all** of the following are true:

- [ ] Every `.md` at the repo root is **Contract**, **Runbook**, or **Canonical** (with a clear, current purpose).
- [ ] Every file in `archive/` is older than the most recent cleanup, and `archive/deprecated/<date>/DEPRECATION_NOTICE.md` files exist for the last 3 cleanup rounds.
- [ ] Every link in `.github/copilot-instructions.md` and in this `CLAUDE.md` resolves to a file that exists at the linked path.
- [ ] The current authoritative docs (`.github/ORG_CREDENTIALS_*.md`, `.github/VECTOR_DB_DEVELOPER_REFERENCE.md`, `CLAUDE.md`, `README_V11.md`) do not contradict each other on any fact you can spot-check.
- [ ] No "## Last updated" header in a canonical doc is older than 60 days for an active subsystem.
- [ ] A most recent `ARCHIVE_CLEANUP_SUMMARY_<MONTH>.md` exists in the repo root describing the last cleanup round.

---

## 17. Quick Reference (for new contributors and agents)

```powershell
# Setup
pip install -r requirements.txt

# Run dev server
cd AI_infrastructure && python flask_app.py

# Pre-commit MUST-RUN
.\.vscode\fix-bom.ps1

# Deploy (production)
git push gerardo v11:v11

# Smoke checks
python -c "from AI_infrastructure.shared.database_utils import execute_query; print(execute_query('SELECT 1', fetch_mode='value'))"
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print(len(r.tools))"

# Vector DB quick reference
# → .github/VECTOR_DB_DEVELOPER_REFERENCE.md

# Org / credential architecture
# → .github/ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md

# Module visibility / sidebar gating
# → .github/MODULE_VISIBILITY_ARCHITECTURE.md
```

**When in doubt:** read the most recent migration in `AI_infrastructure/migrations/` for the relevant subsystem, then the most recent commit touching that subsystem in `git log -- <path>`. The code is the truth; the docs are the explanation.
