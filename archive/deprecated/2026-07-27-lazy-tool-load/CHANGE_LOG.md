# CHANGE LOG — lazy-tool-load refactor (2026-07-27)

Per-file, per-line inventory of every change. Companion to `DEPRECATION_NOTICE.md`.
The plan file is at `C:\Users\gpoli\.claude\plans\proud-snuggling-muffin.md`.

## Whole-file deletions (git mv → `deleted_files/`)

| Original path | Archive path | Reason | Lines (orig) |
|---|---|---|---|
| `AI_infrastructure/scripts/deploy_prewarm.py` | `deleted_files/deploy_prewarm.py` | Pre-gunicorn prewarm script — writes `/data/.prewarm_complete` marker so workers skip the background-thread prewarm. No longer needed because no prewarm exists. | 7389 B |
| `tools/persistent_semantic_search.py` | `deleted_files/persistent_semantic_search.py` | Loads MiniLM + generates 829 tool embeddings, caches in Supabase. Was the silent-kill trigger on first chat. | 22332 B / 508 lines |
| `tools/intelligent_discovery.py` | `deleted_files/intelligent_discovery.py` | Keyword + semantic hybrid scoring over all tools. Same family as `persistent_semantic_search`. | 28954 B |
| `tests/test_persistent_semantic_compile.py` | `deleted_files/test_persistent_semantic_compile.py` | Tested `persistent_semantic_search` directly. Module deleted. | 9474 B |
| `tests/test_persistent_semantic_e2e.py` | `deleted_files/test_persistent_semantic_e2e.py` | E2E test for the same. Module deleted. | 10174 B |
| `tests/test_persistent_semantic_endpoint.py` | `deleted_files/test_persistent_semantic_endpoint.py` | Endpoint test for the same. Module deleted. | 8967 B |
| `tests/test_persistent_semantic_smoke.py` | `deleted_files/test_persistent_semantic_smoke.py` | Smoke test for the same. Module deleted. | 3977 B |

## Code-section deletions (snippet → `deleted_sections/`)

### `AI_infrastructure/flask_app.py`

| Lines | Snippet | What | Why |
|---|---|---|---|
| 355–479 | `flask_app__initialize_semantic_search_async.py` | Banner + globals (`_semantic_search_initialization_complete`, `_semantic_search_initialization_error`) + the `initialize_semantic_search_async()` function (loads MiniLM, generates embeddings, writes to Supabase) | Background prewarm removed. Boot no longer loads MiniLM. |
| 480–490 | `flask_app__start_semantic_search_initialization.py` | The `start_semantic_search_initialization()` thread spawner | Callsite removed (line 5129); function itself removed too. |
| 514–535 | `flask_app__prewarm_classes.py` | `PrewarmPending`, `PrewarmFailed`, `is_prewarm_complete()`, `get_prewarm_error()` | Sentinel classes and gate helpers only meaningful with a prewarm that can fail or be pending. No prewarm → no gate. |
| 538–592 | `flask_app__initialize_pgvector_bge_model_async.py` | Banner + globals + the `initialize_pgvector_bge_model_async()` function (loads BGE 440 MB model) | ORTHOGONAL: removed for consistency with the lazy-tools philosophy but pgvector is a separate subsystem. Restore if pgvector slow-first-upload is observed. |
| 594–602 | `flask_app__start_pgvector_bge_initialization.py` | The `start_pgvector_bge_initialization()` thread spawner | Same. |
| 5094–5129 | `flask_app__prewarm_marker_check.py` | The `/data/.prewarm_complete` marker detection block + the `start_semantic_search_initialization()` call site | No prewarm → no marker → no marker check. |
| 5154–5157 | `flask_app__prewarm_calls.py` | The `start_pgvector_bge_initialization()` call site (try/except) | Same. |

### `AI_infrastructure/routes/agent_routes_v4.py`

| Lines | Snippet | What | Why |
|---|---|---|---|
| 71–138 | `agent_routes_v4__semantic_search_cache.py` | Banner + globals (`_semantic_search_cache`, `_semantic_search_lock`) + the `get_semantic_search()` lazy getter | The whole semantic-search singleton subsystem is gone. |
| 1318–1445 | `agent_routes_v4__intelligent_tool_suggestions.py` | The proactive semantic pre-search block (init, get_semantic_search, search, filter by auth platform, format 🎯 INTELLIGENT TOOL SUGGESTIONS block, except handler) | The AI no longer receives proactive suggestions. |
| 2185–2190 | `agent_routes_v4__suggestion_injection.py` | The `if intelligent_tool_suggestions: system_prompt += …` injection into the system prompt | No block → no injection. |

## File modifications (`.before` snapshot in `files/`)

### `tools/registry_v3.py` (81775 B before)

The single biggest change. The `__init__` chain `_load_schemas → _load_implementations → _load_module_plugins` becomes:

1. `_load_meta_tools_only()` — parses `tools/schemas/meta_tools.json` only (~10 ms).
2. `_build_schema_index()` — globs all 99 JSON files, reads only `tool.name` per file (~50 ms).
3. `_register_lazy_implementations()` — wraps `tools/implementations/*` AND `google_workspace/*` in `_LazyModuleProxy`. Drops force-materialise for `sql_database` / `visualization_guide` / `viz_snapshots`; keeps `meta_tools` forced (so per-function registration works).

New methods added:
- `materialize_tool(name) -> bool` — parses one JSON file on demand, runs `process_schema()`, registers schema + implementation.
- `search_index(query, k=8)` — walks the index for substring matches without JSON re-parse.

Modified methods:
- `get_tool(name)` — on miss, calls `materialize_tool(name)` first.
- `get_tool_function(name)` — unchanged (already lazy via `_LazyModuleProxy`).

Existing patterns preserved:
- `EXCLUDED_TOOLS` security list (line 410–416): honored in `materialize_tool`.
- `_DISABLED_SCHEMA_FILENAMES` (line 76–81): honored in `_build_schema_index`.
- `_RENDER_DISABLED_PLATFORMS` (line 52–74): honored in both.
- `_DISABLED_IMPLEMENTATION_STEMS` (line 96–110): honored in `_register_lazy_implementations`.
- `_schema_fingerprint()` (line 244–270): unchanged — guards against staleness when warm cache is re-enabled.

### `tools/implementations/meta_tools.py` (58936 B before)

Three surgical edits:

| Line | Change | Before → After |
|---|---|---|
| 431 | Allowlist gate in `get_tool_schema` | `if extracted_tool_name not in registry.tools:` → `if not registry.materialize_tool(extracted_tool_name):` |
| 477–482 | Wasteful `get_anthropic_tools()` scan + latent name-compare bug | Direct `registry.tools[extracted_tool_name]` lookup + compare against `extracted_tool_name` not `tool_name` |
| 1046 | Allowlist gate in `execute_tool` | Same as line 431 |

Drive-by fix: `platform_aliases` dict at lines 73–108 has duplicate `'forms'` key; dedup to `'google_forms'`.

### `AI_infrastructure/core/combined_agent_worker.py` (224075 B before)

Two surgical edits around line 2293:

| Line | Change | Before → After |
|---|---|---|
| 2293 | Allowlist gate | `if not registry.is_tool_allowed(tool_name):` → `if not registry.materialize_tool(tool_name) or not registry.is_tool_allowed(tool_name):` |
| 2297–2304 | "Did you mean" hint source | iterates `registry.tools.keys()` → iterates `registry._schema_index.keys()` so the hint can suggest not-yet-materialized tools |

### `AI_infrastructure/core/unified_ai_client.py` (103381 B before)

**No change required.** Line 43 `self.tools = list(self.registry.tools.keys())` still works — at boot only `meta_tools.json` is loaded, so `self.tools` correctly contains 8 names.

### `AI_infrastructure/routes/agent_routes_v4.py` (164650 B before)

Three sections deleted (see snippet table above). No edits to surviving code.

### `AI_infrastructure/flask_app.py` (245368 B before)

Seven sections deleted (see snippet table above). No edits to surviving code.

### `startup.sh` (11863 B before)

Single-line edit: remove the `python AI_infrastructure/scripts/deploy_prewarm.py` call. The deploy_prewarm.py file itself was git-mv'd to `deleted_files/`, so the startup.sh call would now point to a missing file.

## Files unchanged but verified

| Path | Why verified |
|---|---|
| `tools/schemas/meta_tools.json` | The 8 meta-tools visible to the AI. Loaded eagerly. Confirmed unchanged in this refactor. |
| `tools/implementations/meta_tools.py` (special_modules block) | `meta_tools` stays in `special_modules` so per-function registration works. Other special modules (`sql_database`, `visualization_guide`, `viz_snapshots`) drop out of force-materialise. |
| `AI_infrastructure/builders/system_prompt_builder.py` | Verified to not reference `intelligent_tool_suggestions`, `PersistentSemanticToolSearch`, or any embedding machinery. |

## Test changes

Updated (not deleted):

| File | Line | Change |
|---|---|---|
| `AI_infrastructure/tests/test_tavily_tools.py` | 149 | Add `for n in expected: registry.materialize_tool(n)` before the registry.tools assertion |
| `AI_infrastructure/tests/test_tool_name_allowlist.py` | 100, 110, 125, 136 | Same pattern |
| `AI_infrastructure/tests/test_meta_tools_execute_tool.py` | 56 | Test that materialize-first works |
| `AI_infrastructure/tests/test_registry_lazy_proxy_routing.py` | 190 | Expand fixture: assert `len(registry.tools) == 8` post-boot, materialize_tool works |

Tests deleted: see "Whole-file deletions" table above (4 `tests/test_persistent_semantic_*.py`).

## Summary statistics

- **Total files touched:** 21 (7 modified + 7 git-mv'd + 7 backup snapshots + 10 snippets − 10 vs 14 because some changes overlap)
- **Whole files deleted:** 7
- **Code sections deleted:** 10 (extracted as snippets)
- **New methods added to `RegistryV3`:** 2 (`materialize_tool`, `search_index`)
- **Files unchanged but verified:** 3
- **Tests updated:** 4
- **Tests deleted:** 4
- **Estimated boot memory savings:** ~1 GB RSS (MiniLM 80 MB + BGE 440 MB + 12 google_workspace modules + Supabase tool_embeddings + 829 schema dicts ≈ ~1 GB drop in working set)
- **Estimated boot time savings:** ~45–85 s (deploy_prewarm ~30 s + background prewarm ~30 s + ~99-file schema parse 2–3 s + 12 google_workspace imports ~3–5 s)
