# ROLLBACK — lazy-tool-load refactor (2026-07-27)

Three layers of escape, in order of speed. Pick the fastest one that restores
the behavior you need.

## Layer 1 — Bundle restore (fastest full restore, ~2 minutes)

Restores the entire pre-refactor state from this archive. Use when:
- The lazy-load refactor introduced a regression you can't triage.
- You need to ship a fix and want the working state back.

### Step 1a — Restore whole files (git mv back)

```bash
git mv archive/deprecated/2026-07-27-lazy-tool-load/deleted_files/deploy_prewarm.py AI_infrastructure/scripts/deploy_prewarm.py
git mv archive/deprecated/2026-07-27-lazy-tool-load/deleted_files/persistent_semantic_search.py tools/persistent_semantic_search.py
git mv archive/deprecated/2026-07-27-lazy-tool-load/deleted_files/intelligent_discovery.py tools/intelligent_discovery.py
git mv archive/deprecated/2026-07-27-lazy-tool-load/deleted_files/test_persistent_semantic_compile.py tests/test_persistent_semantic_compile.py
git mv archive/deprecated/2026-07-27-lazy-tool-load/deleted_files/test_persistent_semantic_e2e.py tests/test_persistent_semantic_e2e.py
git mv archive/deprecated/2026-07-27-lazy-tool-load/deleted_files/test_persistent_semantic_endpoint.py tests/test_persistent_semantic_endpoint.py
git mv archive/deprecated/2026-07-27-lazy-tool-load/deleted_files/test_persistent_semantic_smoke.py tests/test_persistent_semantic_smoke.py
```

### Step 1b — Restore modified files (cp from .before snapshots)

```bash
ARCHIVE=archive/deprecated/2026-07-27-lazy-tool-load/files

cp $ARCHIVE/tools__registry_v3.py.before                                  tools/registry_v3.py
cp $ARCHIVE/tools__implementations__meta_tools.py.before                  tools/implementations/meta_tools.py
cp $ARCHIVE/AI_infrastructure__routes__agent_routes_v4.py.before          AI_infrastructure/routes/agent_routes_v4.py
cp $ARCHIVE/AI_infrastructure__core__combined_agent_worker.py.before      AI_infrastructure/core/combined_agent_worker.py
cp $ARCHIVE/AI_infrastructure__core__unified_ai_client.py.before          AI_infrastructure/core/unified_ai_client.py
cp $ARCHIVE/AI_infrastructure__flask_app.py.before                        AI_infrastructure/flask_app.py
cp $ARCHIVE/startup.sh.before                                             startup.sh
```

### Step 1c — Restore deleted code sections (paste snippets back)

Open each snippet file in `archive/deprecated/2026-07-27-lazy-tool-load/deleted_sections/`
and paste the code between the `# --- ORIGINAL CODE BEGINS ---` and
`# --- ORIGINAL CODE ENDS ---` markers into the live file at the line range
stated in the snippet's header docstring.

| Snippet file | Paste into | Line range |
|---|---|---|
| `flask_app__initialize_semantic_search_async.py` | `AI_infrastructure/flask_app.py` | 355–479 |
| `flask_app__start_semantic_search_initialization.py` | `AI_infrastructure/flask_app.py` | 480–490 |
| `flask_app__prewarm_classes.py` | `AI_infrastructure/flask_app.py` | 514–535 |
| `flask_app__initialize_pgvector_bge_model_async.py` | `AI_infrastructure/flask_app.py` | 538–592 |
| `flask_app__start_pgvector_bge_initialization.py` | `AI_infrastructure/flask_app.py` | 594–602 |
| `flask_app__prewarm_marker_check.py` | `AI_infrastructure/flask_app.py` | 5094–5129 |
| `flask_app__prewarm_calls.py` | `AI_infrastructure/flask_app.py` | 5154–5157 |
| `agent_routes_v4__semantic_search_cache.py` | `AI_infrastructure/routes/agent_routes_v4.py` | 71–138 |
| `agent_routes_v4__intelligent_tool_suggestions.py` | `AI_infrastructure/routes/agent_routes_v4.py` | 1318–1445 |
| `agent_routes_v4__suggestion_injection.py` | `AI_infrastructure/routes/agent_routes_v4.py` | 2185–2190 |

### Step 1d — Verify

```bash
# Confirm all 7 files restored
git status --short | grep "^R " | wc -l   # should be 7 renames

# Confirm modified files have their pre-refactor content
head -3 tools/registry_v3.py  # should NOT contain "materialize_tool"

# Boot smoke test
cd AI_infrastructure
python -c "from tools.registry_v3 import get_registry; r = get_registry(); print(len(r.tools))"
# Expected: 829 (not 8)

# Confirm semantic search infrastructure live
python -c "from tools.persistent_semantic_search import PersistentSemanticToolSearch; print('ok')"
# Expected: ok (no ImportError)
```

## Layer 2 — Env-flag escape hatch (instant, no code change)

The refactored `RegistryV3.__init__` checks the `LAZY_TOOLS` env var:

- `LAZY_TOOLS=1` (default after refactor): boot loads only the 8 meta-tools, schema index, lazy implementations.
- `LAZY_TOOLS=0`: boot falls back to the pre-refactor eager path (`_load_schemas()` + eager `google_workspace` + force-materialise special_modules).

To toggle:

```bash
# Render dashboard → Environment → Add env var:
LAZY_TOOLS=0

# Or via render CLI:
render env set LAZY_TOOLS=0 --service srv-d4k7olos9c44c73epf4i0
```

The env var is read on every cold start. No redeploy needed if the new
RegistryV3 code is already running — just set the env var and trigger a
restart.

**This is the recommended escape hatch for production incidents at 2 AM.**
Setting `LAZY_TOOLS=0` flips behavior without touching code or waiting for
a redeploy.

## Layer 3 — `git revert` (last resort, full history revert)

If Layer 1 is too tedious and Layer 2 isn't possible (e.g. the refactor was
the only code change and there's no LAZY_TOOLS flag yet), revert the entire
refactor commit:

```bash
# Find the refactor commit
git log --oneline | grep -i "lazy.tool.load\|lazy-load"

# Revert it
git revert <sha> --no-edit

# The archive/ folder is unaffected because it was committed BEFORE
# the refactor commit. You can delete it later if you want:
rm -rf archive/deprecated/2026-07-27-lazy-tool-load/
```

**Caveat:** if you `git revert` and then try to re-apply the refactor later,
you'll need to `git revert` again (i.e. `git revert <revert-sha>`). Keep
both commits in history.

## What does NOT need rollback

| Item | Reason |
|---|---|
| `tools/schemas/meta_tools.json` | The 8 meta-tools are identical pre/post refactor. |
| `tools/implementations/meta_tools.py` 8 functions | The 8 functions are unchanged. The only edits in this file are 3 surgical allowlist-gate changes. |
| `_LazyModuleProxy` itself | Pre-existed. The refactor just adds more users of it. |
| `_schema_fingerprint()` | Unchanged. |
| `EXCLUDED_TOOLS`, `_DISABLED_SCHEMA_FILENAMES`, `_RENDER_DISABLED_PLATFORMS`, `_DISABLED_IMPLEMENTATION_STEMS` | All unchanged. |

## Smoke tests after rollback

```bash
# 1. Registry loads 829 tools
python -c "from tools.registry_v3 import get_registry; r = get_registry(); print(len(r.tools))"

# 2. Semantic search module imports
python -c "from tools.persistent_semantic_search import PersistentSemanticToolSearch; print('ok')"

# 3. deploy_prewarm script runs without error
cd AI_infrastructure && python scripts/deploy_prewarm.py

# 4. Flask boots cleanly
python flask_app.py
# Look for "[BACKGROUND] [OK] Registry loaded with 829 tools" in logs
```

## If you keep the lazy-load and want to disable specific tools

You don't need to rollback to disable specific tools. Edit:

- `tools/registry_v3.py:_RENDER_DISABLED_PLATFORMS` (line 52–74): add the
  platform name. Affects schema loading + implementation loading + the
  index build.
- `tools/registry_v3.py:_DISABLED_IMPLEMENTATION_STEMS` (line 96–110): add
  the implementation file stem. Affects the implementation proxy only.
- `tools/registry_v3.py:_DISABLED_SCHEMA_FILENAMES` (line 76–81): add the
  schema filename. Affects schema loading only.

The `_schema_fingerprint()` warm-cache invalidates automatically on file
change (no version bump needed). Just edit and commit.
