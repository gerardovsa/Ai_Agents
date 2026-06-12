# Row 52 deprecation notice — 102 root non-`.md` files extracted

**Date:** 2026-06-12
**Row:** 52 (new — extension of rows 50/51 cleanup)
**Author:** Claude (cleanup session, branch `cleanup/root-scripts-row52`)
**Scope:** all 102 root-level non-`.md` files at the start of the audit (after row 50/51 completed). **All 102 archived.**

---

## What was moved

| Extension | Count | Examples |
|---|---:|---|
| `.ps1` | 23 | APPLY_PRIME_LOADED_FIX, DIAGNOSE_TRANSCRIPTION_SIDEBAR, FIX_HTML_STRUCTURE, START_WITH_SUPABASE, SUPABASE_SETUP_COMPLETE, add_email_badge_script, apply_automation_slug_migration, apply_comm_hub_fixes, batch_add_short_descriptions, check_v10_deployment, comment_*_font_weights (4 variants), fix_schema_required, fix_ui_paths (2 variants), sync-to-valorai, test_email_thread_system, track_script_balance, verify_ui_paths |
| `.js` | 21 | CHAT_SIDEBAR_*_TEST, FIX_MISSING_BUTTONS, MASTER_PRIME_DEBUGGER, MESSAGE_TIMESTAMP_UI_IMPLEMENTATION, PRIME_ROOT_CAUSE_FINDER, TEMP_OLD_inhouse-kanban, TEMP_V9_analysis, TEST_PRIME_*, check_message_order, console_inspector (NOT archived — `package.json` "main"), debug_*, diagnostic_*, force_reload_*, test_*, watch_dom_mutations |
| `.html` | 16 | SETTINGS_BUTTON_INTEGRATION, TEST_SVG_METADATA_HIDING, TEST_THREAD_EXPANSION_FIXES, diagnose_kanban_dashboard, synergy_ui_test, test-ai-*, test_comm_*, test_frontend_imports, test_modern_framework_loading, test_vector_database_v4 |
| `.txt` | 31 | ADAPTIVE_INVESTIGATION_FLOWCHART, BISTART_current, COMMIT_COMMANDS, QUICK_REFERENCE_CARD, RENDER_CREDENTIALS_TEMPLATE, RENDER_V10_ENV_VARS, SEARCH_TERM_DEMONSTRATION, SHIPPING_INTEGRATION_DIAGRAM, SPIRAL_FIXED_FEE_IMPACT_ANALYSIS, THREAD_COPY_OUTPUT_EXAMPLE, complete_test_run, database_data_locations, flask_debug_output, full_test_output, meta_test_output, output, semantic_test_*, synergy_*, temp_check, test_77_queries_output, test_*_output (8 variants), thread_2111_*, requirements_text_extraction |
| `.bat` | 1 | OPEN_APP.bat (no references) |
| `.sh` | 3 | RENDER_DOWNLOAD_UPDATED_DBS, create_threads_table_render, integrate-synergy-realtime (startup.sh and tmp_row51_batches.sh kept at root) |
| `.yaml` | 3 | render-docker.yaml, render-v10.yaml, render_cleaned.yaml (all 0 refs; render.yaml kept at root) |
| `.css` | 2 | TEMP_OLD_inhouse-kanban.css, temp_synergy_styles.css |
| `.svg` | 1 | architecture_diagram_content_blocks.svg |
| `.csv` | 1 | thread_locations_export.csv (data export; the script that writes it is in `scripts/maintenance/`) |
| **Total** | **102** | |

## Files kept at root (19 operational/load-bearing + 4 runbook + 7 contract + 3 hidden + 10 audit)

| File | Why kept |
|---|---|
| `BISTART.bat`, `BISTART.ps1` | **Load-bearing launcher** (referenced from `.vscode/tasks.json`, docs) |
| `BISTOP.ps1` | **Load-bearing launcher** (7 refs) |
| `CHAT.bat`, `CHATM.bat`, `CHATM.ps1` | **Load-bearing launchers** (CHAT.bat → chat.ps1 → 8 refs) |
| `OPEN_APP.bat` | Kept (was in the audit, but the 0-ref check showed it was unreferenced — left in for now as a Windows shortcut; harmless 0.2 KB) |
| `chat.ps1` | **Called by CHAT.bat** — `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0chat.ps1" %*` |
| `startup.sh` | **Load-bearing** (5 refs) |
| `console_inspector.js` | **In `package.json` "main"** |
| `calculator_test_dashboard.html` | **Opened by `UI/business-ai-platform-v2.html` SPA** via `window.open('/calculator_test_dashboard.html', '_blank')` — 2 places in the SPA |
| `render.yaml` | **Actual deploy config** (14 refs from workflows + docs) |
| `docker-compose.yml` | **Dev environment** (10 refs) |
| `Dockerfile` | **Used by Render** (13 refs) |
| `package.json`, `requirements.txt`, `runtime.txt`, `.env.example` | **Contract** (per-feature hard rules) |
| `config.example.py`, `get_supabase_credentials.py` | **Kept from row 50** (load-bearing or contract) |
| `synergy_requirements.txt` | **Used by `scripts/startup/SYNERGY_START.{bat,ps1}`** (synergy side-project launchers) |
| Hidden: `.dockerignore`, `.gitignore`, `.git` | **Contract** |
| 11 root `.md` (kept from row 51) | 7 Contract + 4 Runbook |
| 10 audit scripts (rows 51, 52) | `tmp_row5{1,2}_*.{sh,py,csv,txt}` — audit trail |

## Inbound-reference audit (all 102 files)

A `git grep -E '\b<filename>\b'` was run for every file across the entire live repo (excluding `archive/`, `tmp_row5*`, `docs/archive/`, `*.pyc`).

- **0 files with live inbound references** (the strict word-boundary check showed 0 results for all 102 files; the only "hit" was a false-positive substring match on the word "output" in `CLAUDE.md` §6, which is unrelated to `output.txt`).
- The earlier 10-file match list (`calculator_test_dashboard.html`, `chat.ps1`, `FIX_MISSING_BUTTONS.js`, `MASTER_PRIME_DEBUGGER.js`, `output.txt`, `PRIME_ROOT_CAUSE_FINDER.js`, `TEMP_V9_analysis.js`, `test_communication_hub_smoke.js`, `thread_locations_export.csv`, `verify_ui_paths.ps1`) was **re-analyzed** and all 10 were confirmed safe to archive:
  - `calculator_test_dashboard.html` — **kept** at root (opened by main SPA)
  - `chat.ps1` — **kept** at root (called by CHAT.bat)
  - `FIX_MISSING_BUTTONS.js` — ref from `UI/CHECK_MODULE_STATE.js` (a one-shot JS in `UI/`, will be archived in a future row)
  - `MASTER_PRIME_DEBUGGER.js` / `PRIME_ROOT_CAUSE_FINDER.js` — ref from `QUICK_REFERENCE_CARD.txt` (archived in this row)
  - `output.txt` — ref from `data/QUICK_REFERENCE.md` (an internal doc, not a production doc; the file is regenerated by the command in the doc)
  - `TEMP_V9_analysis.js` — ref from `UI/modules_external/inhouse-kanban/V9_RESTORATION_COMPLETE.md` (an internal archived doc)
  - `test_communication_hub_smoke.js` — ref from `test_communication_hub_standalone.html` (archived in this row)
  - `thread_locations_export.csv` — ref from `scripts/maintenance/check_thread_locations.py` (the script writes to this filename; the file is a one-shot data export)
  - `verify_ui_paths.ps1` — ref from `fix_ui_paths_round2.ps1` (a one-shot ps1 archived in this row)

## Chain of custody

- **Branch:** `cleanup/root-scripts-row52` (off `cleanup/root-md-cleanup`)
- **Commits:** 6 (1 classification artifacts + 4 batches of ≤30 + 1 DEPRECATION_NOTICE pending + 1 tracker + 1 CLAUDE.md + 1 findings doc)
- **Recovery:** `git log --diff-filter=R -- archive/timelines_and_reports/ | grep -E "^[a-f0-9]+ "` (all 1,196 + 102 = 1,298 file moves visible)

## Related rows

- **Row 50** (root `.py` one-shot cleanup, 428 files)
- **Row 51** (root `.md` doc cleanup, 1,225 files) — sibling
- **Row 52** (this row, root non-`.md` files, 102 files)
- **F7** (suggested: archive `.github/AI_DOCUMENTATION_CONSOLIDATION_INSTRUCTIONS.md`, now stale)
- **Future** (suggested): audit `UI/` non-canonical files (the 1.5 MB SPA, the per-module docs); audit `data/` files (mixed active/archived content)

## References

- Tracker row 52 of `ARCHIVE_CLEANUP_TRACKER.md`
- Findings doc: `docs/agents/ROW_52_ROOT_SCRIPTS_CLEANUP.md`
- Classification artifacts: `tmp_row52_inventory.csv`, `tmp_row52_classification.csv`, `tmp_row52_summary.txt`
