# In-House Print Product Surface — DEPRECATION NOTICE

**Deprecated:** 2026-06-15
**Branch:** cleanup/inhouse-print-deprecation (based on cleanup/root-md-cleanup)
**Reason:** The in-house-print product surface (quote-calculator, stock-management,
inhouse-print, and the calculator-tests dashboard) is being retired. The in-house
kanban module is retained for demo use only. The platform is consolidating around
generic AI tools and the public Shopify/WooCommerce/Xero integrations.

## What was moved

| Item | From | To | File count |
|------|------|----|------------|
| quote-calculator module | UI/modules_external/quote-calculator/ | archive/inhouse_print_deprecation/quote-calculator/ | 233 files |
| stock-management module | UI/modules_external/stock-management/ | archive/inhouse_print_deprecation/stock-management/ | 46 files |
| inhouse-print module | UI/modules_external/inhouse-print/ | archive/inhouse_print_deprecation/inhouse-print/ | 11 files |
| inhouse_query.py (Python tool) | tools/implementations/inhouse_query.py | archive/inhouse_print_deprecation/inhouse_query.py | 1 file |
| calculator_test_dashboard.html (root copy) | calculator_test_dashboard.html | archive/inhouse_print_deprecation/calculator_test_dashboard_root_copy.html | 1 file |
| calculator_test_dashboard.html (UI copy) | UI/calculator_test_dashboard.html | KEPT (Flask serves this one) | 1 file |

**Total moved:** 292 files into `archive/inhouse_print_deprecation/`. **Total tracked-file delta:** -292 (renames only; no content loss).

## What was kept (deliberately)

| Item | Why |
|------|-----|
| inhouse-kanban/ | Used as a demo / showcase. Listed in ALWAYS_ENABLED_MODULES. |
| inhouse-kanban_routes.py | The Flask blueprint for the keep module. |
| AI_infrastructure/migrations/032_org_module_access.sql | DB-level role/platform mapping. Leave until a future migration cleans the platform_module_catalog rows. |
| AI_infrastructure/migrations/036_platform_module_catalog.sql | Same - DB-level catalog. |
| AI_infrastructure/auth/credential_injector.py (get_inhouse_print_db_credentials) | Still called by the inhouse-kanban routes. |
| AI_infrastructure/prompts/* and AI_infrastructure/docs/* | Doc-only references; left for now. |

## What was removed from the live tree

| File | Edit |
|------|------|
| UI/modules_external/manifest.json | Removed 3 module entries (quote-calculator, stock-management, inhouse-print). |
| UI/business-ai-platform-v2.html | Removed the calculator-tests sidebar button, ZONE2_MODULES entries (3), the openCalculatorDashboard() <script>, the commented-out stock button, and the placeholder #tab-stock div. |
| AI_infrastructure/flask_app.py | Commented out calculator_test_bp import/registration. Removed stock-management route + log line. |
| AI_infrastructure/config/deployment_config.py | Removed 3 entries from RENDER_DISABLED_MODULES (no longer needed - the modules are gone from the tree). |
| tools/registry_v3.py | Removed ASCII-tree reference to quote-calculator/. |
| tools/plugins/module_plugin_loader.py | Removed docstring/print references to the 3 moved modules. |
| CLAUDE.md | Updated repo tree (section 2), removed InHousePrint risk note (section 13), removed query_library.py note (section 14), added deprecation note. |

## How to recover (if needed)

```bash
# In the cleanup worktree, on the inhouse-print-deprecation branch:
git checkout cleanup/inhouse-print-deprecation
# Everything is in archive/inhouse_print_deprecation/
ls archive/inhouse_print_deprecation/

# To re-activate (NOT recommended - the modules depend on In_House_SQL):
git mv archive/inhouse_print_deprecation/quote-calculator UI/modules_external/
git mv archive/inhouse_print_deprecation/stock-management UI/modules_external/
git mv archive/inhouse_print_deprecation/inhouse-print UI/modules_external/
# ... and revert the manifest.json / flask_app.py / business-ai-platform-v2.html / CLAUDE.md edits
```

## Follow-up (for the next agent, not this PR)

- [x] ~~Clean inhouse-kanban in place (15 .md files at root mention deprecated modules).~~
      **Done 2026-06-15.** Audited all 15 .md files in inhouse-kanban/ — only 2
      matches found, both are the **live** `api:inhouse-print` platform permission
      in the README and manifest.json (inhouse-kanban still uses the
      inhouseprint_sql platform credential for the 4-tier resolver). No edits
      required. Tracked as F13.
- [x] ~~Audit and clean AI_infrastructure/prompts/ and AI_infrastructure/docs/ for stale
      references to the 3 moved modules.~~ **Done 2026-06-15.**
      - `AI_infrastructure/docs/IMPLEMENTATION_SUMMARY.md` (line 452): marked
        `http://localhost:5000/stock-management` as REMOVED with a deprecation
        pointer. Tracked as F14.
      - `AI_infrastructure/docs/MIGRATION_GUIDE.md` (line 388): same fix.
        Tracked as F14.
      - `AI_infrastructure/prompts/*` (20 files): **DEFERRED** — the active
        prompt (`tool_usage_system_prompt.md`, 97,803 bytes, 2,757 lines) is
        loaded by `unified_ai_client.py` and references many `inhouse_*` tools
        (`inhouse_calculator_guide`, `inhouse_query_guide`, `inhouse_stock_guide`,
        `inhouse_get_domain_guide`, `inhouse_query_stock_levels`, etc.). Editing
        this prompt is a much larger scope than this branch can absorb and
        should be done as a dedicated round (tracked as F15 — see notes).
      - `AI_infrastructure/tests/STOCK_MANAGEMENT_*.md` and
        `SYSTEM_DIAGNOSTICS_INTEGRATION.md`: historical analysis docs that
        reference the deprecated modules in past tense; left as historical
        record.
- [x] ~~Add a migration to soft-delete the 3 rows from platform_module_catalog.~~
      **Done 2026-06-15** — `AI_infrastructure/migrations/053_soft_delete_deprecated_inhouse_modules.sql`.
      Sets `is_active = FALSE` on the 3 module_catalog rows (inhouse_print,
      quote_calculator, stock_management). Soft-delete (not hard) so the rows
      are reversible from git history if needed. `inhouse_kanban` left ACTIVE.
      Tracked as F13.
- [x] ~~Add a migration to drop the 'inhouse_print' / 'quote_calculator' / 'stock_management'
      platform-key rows from organisation_platform_credentials' lookups.~~
      **Done 2026-06-15 with a refinement** — `AI_infrastructure/migrations/054_remove_deprecated_modules_from_plan_tiers.sql`.
      **Important caveat:** the user's followup said "platform-key rows" but the
      credential tables key on `platform_name` (e.g. `inhouseprint_sql`), NOT
      on module_name. The `inhouseprint_sql` platform row MUST stay because
      inhouse-kanban uses it for the FRED database connection (see
      `AI_infrastructure/auth/credential_injector.py:get_inhouse_print_db_credentials`).
      Migration 054 instead:
        - DELETEs the 3 module_name rows from `plan_modules` (the plan-tier
          defaults — no per-customer data, safe to hard-delete).
        - Reports how many `org_module_access` per-org override rows reference
          the archived modules, but does NOT delete them (per-customer data).
          These rows become harmless once migration 053 lands (the underlying
          module row is `is_active=FALSE`, so no UI surface references them).
          The operator can clean them up via the org admin UI or a one-off
          query: `DELETE FROM ai_infrastructure.org_module_access WHERE module_name IN ('inhouse_print', 'quote_calculator', 'stock_management');`
      Tracked as F13.
- [ ] Confirm the inhouse-kanban production workflow still runs end-to-end.
      *(user action — manual test in the IDE and on the parallel Render instance)*
- [ ] Smoke test on the parallel Render instance (ai-agents-clean.onrender.com).
      *(user action — see docs/active/RENDER_MONITORING_SETUP.md for the test
      checklist; verify /health, /api/admin/diagnostics, inhouse-kanban tab,
      org module gating.)*

## Deferred work (separate follow-up tasks)

- [ ] **F15** — `AI_infrastructure/prompts/tool_usage_system_prompt.md` and its
      20+ historical copy variants. The active prompt is loaded by
      `AI_infrastructure/core/unified_ai_client.py` and advertises many
      `inhouse_*` tool calls (`inhouse_calculator_guide()`, `inhouse_query_guide()`,
      `inhouse_stock_guide()`, etc.) that no longer exist. After the
      in-house-print archival, the AI will be told these tools are available
      but will fail when called. Editing this 97KB prompt is a substantial
      change requiring coordinated testing (prompt + AI client + tool registry).
      **Recommended: dedicated cleanup round on a new branch** with a focused
      sub-agent that:
        1. Lists every `inhouse_*` tool the prompt advertises.
        2. Cross-references each against `tools/registry_v3.py` and
           `UI/modules_external/inhouse-kanban/` to see which still exist.
        3. Edits the active prompt to remove dead tool names.
        4. Optionally consolidates the 20+ "copy N.md" variants (per the
           F1–F8 round's "many copies of the same file" finding).
- [ ] **Future removal round** — after the user is satisfied with the archival,
      open a third branch (TBD name) that `git rm -r archive/inhouse_print_deprecation/`
      and re-applies the migrations 053/054 as HARD-delete (`DELETE FROM
      module_catalog WHERE ...` instead of soft-delete). This is the irreversible
      step.
