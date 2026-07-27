# DEPRECATION NOTICE — lazy-tool-load refactor

**Date:** 2026-07-27
**Author:** Lazy-load refactor
**Plan reference:** `C:\Users\gpoli\.claude\plans\proud-snuggling-muffin.md`
**Related bundles:** None

## Why this bundle exists

The Render-hosted instance (`srv-d4k7olos9c44c73epf4i0`, repo `gerardovsa/Ai_Agents`,
branch `v11`) was crashing within seconds of the first chat message. Root cause:
boot eagerly loaded 829 tool JSON schemas + 12 `google_workspace/*` Python modules,
pre-computed MiniLM-L6-v2 embeddings over all tools (80 MB), and pre-loaded the
BAAI/bge-base-en-v1.5 model (440 MB). On the first chat, `PersistentSemanticToolSearch.search()`
held the gevent worker for 1–3 s while gunicorn's 120 s timeout ticked — the
classic silent-kill pattern (gunicorn SIGTERM / Linux OOM-killer, no Python
traceback in Render logs).

The user decided: **disable intelligent tool suggestions entirely** and switch
to **pure lazy-load** where the AI sees only the 8 meta-tools at startup and
discovers the other 829 tools on demand via `search_tools` →
`get_tool_schema` → `execute_tool`. Boot target: ~10–15 s, ~500 MB RSS (was
~60–100 s, ~1.5 GB).

## What was moved

### Whole files (7) — git mv'd into `deleted_files/`

| Original path | Archive path |
|---|---|
| `AI_infrastructure/scripts/deploy_prewarm.py` | `deleted_files/deploy_prewarm.py` |
| `tools/persistent_semantic_search.py` | `deleted_files/persistent_semantic_search.py` |
| `tools/intelligent_discovery.py` | `deleted_files/intelligent_discovery.py` |
| `tests/test_persistent_semantic_compile.py` | `deleted_files/test_persistent_semantic_compile.py` |
| `tests/test_persistent_semantic_e2e.py` | `deleted_files/test_persistent_semantic_e2e.py` |
| `tests/test_persistent_semantic_endpoint.py` | `deleted_files/test_persistent_semantic_endpoint.py` |
| `tests/test_persistent_semantic_smoke.py` | `deleted_files/test_persistent_semantic_smoke.py` |

### Files modified (7) — `.before` snapshots in `files/`

`tools__registry_v3.py.before`, `tools__implementations__meta_tools.py.before`,
`AI_infrastructure__routes__agent_routes_v4.py.before`,
`AI_infrastructure__core__combined_agent_worker.py.before`,
`AI_infrastructure__core__unified_ai_client.py.before`,
`AI_infrastructure__flask_app.py.before`, `startup.sh.before`

### Code sections extracted (10) — standalone snippets in `deleted_sections/`

Each `.py` file has a header docstring identifying its origin (file + line range),
purpose, and restore procedure. See `CHANGE_LOG.md` for the per-row inventory.

## What replaced them (live code changes)

- **Boot loads only `tools/schemas/meta_tools.json`** (8 tools, ~10 KB) plus a
  lightweight schema **index** built by reading just the `name` field from every
  other schema file (~50 ms, no `process_schema()`).
- **`_LazyModuleProxy` extended** to wrap `google_workspace/*.py` (already used
  for `tools/implementations/*`).
- **`materialize_tool(name)`** added to `RegistryV3` — parses one JSON file on
  demand, runs `process_schema()`, registers the schema + implementation. Called
  by the allowlist gates in `meta_tools.py` and `combined_agent_worker.py` so
  the AI's first call to a tool triggers materialization transparently.
- **All background prewarms removed** — no MiniLM, no BGE (for tool embeddings),
  no `/data/.prewarm_complete` marker, no `deploy_prewarm.py` step in `startup.sh`.
- **System prompt no longer injects intelligent_tool_suggestions** — the AI's
  first user message no longer triggers a 900-iteration numpy cosine loop inside
  the gevent worker.

## How to roll back

See `ROLLBACK.md` for the exact commands. Three layers of escape:

1. **Layer 1 — full bundle restore (fast):** `git mv` the whole files back +
   `cp` each `.before` snapshot over its live counterpart. Paste the
   `deleted_sections/*.py` snippets back into their named files.
2. **Layer 2 — env flag (fastest):** `LAZY_TOOLS=0` in Render env vars
   (refactored code respects the flag).
3. **Layer 3 — single `git revert`:** the refactor lives in one or two commits;
   `git revert <sha>` restores everything. The `archive/` folder is committed
   separately so it survives the revert.

## Inventory at a glance

```
archive/deprecated/2026-07-27-lazy-tool-load/
├── DEPRECATION_NOTICE.md            ← this file
├── CHANGE_LOG.md                    ← per-file/per-line change inventory
├── ROLLBACK.md                      ← exact restore commands (3 layers)
├── files/                           ← 7 .before snapshots of modified files
├── deleted_files/                   ← 7 whole files (git mv'd, history preserved)
└── deleted_sections/                ← 10 standalone .py snippet files
```

Total: 3 markdown files + 7 .before snapshots + 7 deleted whole files + 10 snippets = 27 files.

## How to read this bundle

If you are a future agent wondering "why is there a `2026-07-27-lazy-tool-load/`
folder and what was in `tools/persistent_semantic_search.py`?":

1. Read this DEPRECATION_NOTICE for the rationale.
2. Read `CHANGE_LOG.md` for the per-file inventory.
3. Open any `deleted_files/*.py` to read the original code (git log --follow
   works on these — history is preserved).
4. Open any `deleted_sections/*.py` for code sections that lived inside larger
   files. Each snippet's docstring says where it came from and how to restore.
5. Read `ROLLBACK.md` if you want to undo the refactor.
