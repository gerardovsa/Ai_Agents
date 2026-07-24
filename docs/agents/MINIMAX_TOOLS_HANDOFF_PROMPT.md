# MiniMax Tools Handoff Prompt

> **Use this prompt verbatim with another AI agent.** It contains everything that agent needs to build client-side equivalents of Anthropic's `web_search_20250305` and `web_fetch_20250910` server tools, so that the AI Agents Platform works correctly with the `MiniMax` provider (whose `api.minimax.io/anthropic` gateway does not implement Anthropic server tools).
>
> **Created:** June 15, 2026 · **Owner:** `gerardovsa/Ai_Agents` v11 branch
>
> This file lives at `docs/agents/MINIMAX_TOOLS_HANDOFF_PROMPT.md` per the project's `docs/agents/` convention. You can hand it to another agent in a fresh session and they will have all the context they need to implement the tools without further research.

---

# PROMPT BEGINS

You are implementing two client-side tools — `web_search` and `fetch_url` — for the AI Agents Platform, so that the `MiniMax` AI provider (and any other Anthropic-compatible provider that does not implement Anthropic's server tools) gets the same web-access capabilities that Anthropic gets natively.

## Background

The platform is a Flask + vanilla-JS multi-tenant AI chat app deployed at Render, with Supabase Postgres as the primary database. It supports four AI providers: `anthropic`, `openai`, `deepseek`, and `MiniMax` (added June 10, 2026, per migration 050/051). All four providers are dispatched through `AI_infrastructure/core/unified_ai_client.py` and `AI_infrastructure/core/combined_agent_worker.py`.

Anthropic ships with **server-side tools** — `web_search_20250305` and `web_fetch_20250910` — that run on Anthropic's infrastructure: a curated search index, content encryption/decryption for citations, and domain filtering. The platform currently appends `web_search_20250305` to the `tools` array on every chat request, unconditionally, in `AI_infrastructure/routes/agent_routes_v4.py:1480-1495`.

When the user picks `MiniMax-M3` as their model, the request goes to `https://api.minimax.io/anthropic/v1/messages`. MiniMax's gateway does **not** implement Anthropic's server tools, and rejects the request with:

```
HTTP 400 — invalid_request_error — invalid params, function name or parameters is empty (2013)
```

because the server-tool shape (`{"type": "web_search_20250305", "name": "web_search", "user_location": {...}, "max_uses": 5}`) has no `input_schema`, which MiniMax interprets as a malformed client function.

**The fix is two parts:**

1. **Gate the Anthropic server tools** on `ai_provider == 'anthropic'`. Don't send them to MiniMax or other providers.
2. **Build client-side equivalents** — `web_search` and `fetch_url` — and inject them into the `tools` list for any non-Anthropic provider. Use a real third-party search/fetch backend (Tavily is recommended; Brave Search is the alternative).

## Scope of this task

You are responsible for **only part 2** — building the two client tools. Part 1 is already drafted in the plan file at `C:\Users\gpoli\.claude\plans\ok-it-logs-me-luminous-whistle.md` (under "Change 1" and "Change 2"). The owning agent will apply that change before you start, or you can apply it yourself — it's a 5-line wrap in an `if ai_provider == 'anthropic':` block.

You will deliver:
- Two new tool schemas in `tools/schemas/`.
- Two new tool implementations in `tools/implementations/minimax/` (new subdirectory).
- A new `_init_MiniMax_tools` provider-aware function in `unified_ai_client.py` (or a new helper module — your call).
- Wiring in `agent_routes_v4.py:1480-1495` to swap server tools for client tools when `ai_provider != 'anthropic'`.
- A regression test in `AI_infrastructure/tests/test_minimax_client_tools.py`.

## Repository facts you need to know

- **Tool schema format:** `tools/schemas/*.json` is the registry-loaded schema directory. Each `.json` file has shape:
  ```json
  {
    "name": "category_or_module_name",
    "description": "...",
    "tools": [
      {
        "name": "tool_name",
        "description": "...",
        "input_schema": {
          "type": "object",
          "properties": {...},
          "required": [...]
        }
      }
    ]
  }
  ```
  The registry loader (`tools/registry_v3.py:130-221`) parses this and exposes tools via `RegistryV3().tools` (a `dict[str, dict]`).
- **Tool execution:** Wrap the implementation function with `@tool_executor()` from `tools/registry_v3.py`. The decorator registers it in the singleton registry. The function should return `{"success": bool, "data": {...}, "error": str?}`.
- **Provider dispatch:** The chat route calls `execute_streaming_request(...)` in `AI_infrastructure/core/combined_agent_worker.py`. Provider-specific behaviour is at lines 2902-2971 (client construction) and 3354-3367 (`stream_params` build). The parallel `unified_ai_client.py` has its own provider dispatch (lines 1070-1072 are the key reference for "this is how the canonical code path handles MiniMax's no-server-tools constraint").
- **The active streaming chat path** goes through `agent_routes_v4.py`, NOT `unified_ai_client.py`. Both paths must be considered. `unified_ai_client.py` is the older path used for some `/v1/chat` style endpoints. Both need the tool wiring so the system works regardless of which path the user is on.
- **4-tier credential resolver:** `AI_infrastructure/shared/org_credentials_loader.py:resolve_credentials(user_id, platform_key)` returns the first hit in: 1) per-user (`user_platform_credentials`), 2) org vault (`organisation_platform_credentials`), 3) sub-user inheritance, 4) env-var fallback. Use this for the Tavily/Brave API key.
- **No new pip dependencies needed for Tavily** — `pip install tavily-python` is one line in `requirements.txt`. Brave is just an HTTPS call with `requests`/`httpx` (already in deps).
- **Migration 053 (June 15, 2026)** added 5 columns to `user_preferences` that previously were silently dropped (`theme`, `enable_notifications`, `enable_sounds`, `max_rounds`, `round_timeout`). The frontend and backend are now in sync for those fields. You do not need to touch migrations.
- **CLAUDE.md (the project instructions)** is the source of truth for coding standards. Read `.github/copilot-instructions.md` only for the long-form version of the architecture, not as authoritative for new code.
- **The `.github/ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md`** explains the credential resolver in depth if you need it.
- **`UI/modules_external/manifest.json`** is being replaced by DB-driven module loading — do not add new modules there.
- **BOM is critical** — `.vscode/fix-bom.ps1` is a hard pre-commit requirement. Run it before reporting done.

## The two new tools

### Tool 1: `web_search`

**Purpose:** Given a search query, return a list of relevant web results with title, URL, and content snippet.

**Input schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "The search query (1-400 chars)."
    },
    "max_results": {
      "type": "integer",
      "description": "Maximum number of results to return (1-20).",
      "default": 5
    },
    "allowed_domains": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Optional: restrict to these domains."
    }
  },
  "required": ["query"]
}
```

**Output shape (always wrap in the tool's success envelope):**
```json
{
  "success": true,
  "query": "the query that was searched",
  "results": [
    {
      "title": "Page title",
      "url": "https://example.com/page",
      "content": "Extracted text snippet or summary (max ~500 chars per result).",
      "score": 0.92
    }
  ],
  "provider": "tavily"  // or "brave"
}
```

**Error shape:**
```json
{
  "success": false,
  "error": "Search backend unavailable: <details>",
  "query": "the query that was searched"
}
```

### Tool 2: `fetch_url`

**Purpose:** Given a URL, fetch its content and return the extracted text.

**Input schema:**
```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string",
      "description": "The URL to fetch (must be http or https; max 2048 chars)."
    },
    "max_chars": {
      "type": "integer",
      "description": "Maximum number of characters to return (1000-200000).",
      "default": 50000
    }
  },
  "required": ["url"]
}
```

**Output shape:**
```json
{
  "success": true,
  "url": "https://example.com/article",
  "title": "Article title (if extractable)",
  "content": "Extracted text content (HTML stripped, scripts/styles removed).",
  "truncated": false,
  "bytes_fetched": 12345
}
```

**Error shape:**
```json
{
  "success": false,
  "error": "Failed to fetch URL: <status code or reason>",
  "url": "the URL that was attempted"
}
```

## Implementation guidance

### Recommended search backend: Tavily

**Why Tavily over Brave:**
- Tavily is purpose-built for AI agents. The `/search` endpoint returns clean text snippets already extracted — no HTML parsing needed.
- Tavily has a separate `/extract` endpoint that does the equivalent of Anthropic's `web_fetch` — fetches a URL and returns clean text.
- Pricing is competitive: $0.008 per search on the "agent" tier, $0.002 on "basic".
- No rate-limit headaches on a single search call.

**If Tavily is unavailable or the user prefers:** Use Brave Search API (`https://api.search.brave.com/res/v1/web/search`) for `web_search`, and a separate URL fetcher (httpx + readability-lxml or trafilatura) for `fetch_url`. Brave is cheaper ($0.003 per search) but returns raw SERP data that needs HTML parsing.

**Credentials resolution:** Use the 4-tier resolver:
```python
from AI_infrastructure.shared.org_credentials_loader import resolve_credentials
api_key = resolve_credentials(user_id, 'tavily')  # checks user → org → sub-user → env
if not api_key:
    api_key = os.environ.get('TAVILY_API_KEY')  # final fallback
```

Add a new env-var to `.env.master` (template only): `TAVILY_API_KEY=`. Add a row to `organisation_platform_credentials` per the existing 4-tier pattern if the user wants org-vault resolution.

### File structure

```
tools/
  schemas/
    minimax_web_search.json         # NEW
    minimax_fetch_url.json          # NEW
  implementations/
    minimax/
      __init__.py                   # NEW
      search.py                     # NEW (web_search implementation)
      fetch.py                      # NEW (fetch_url implementation)
      _client.py                    # NEW (Tavily/Brave HTTP client)

AI_infrastructure/
  tests/
    test_minimax_client_tools.py    # NEW
```

### Wiring

**In `agent_routes_v4.py:1480-1495`:** Replace the unconditional `server_tools` append with a provider-aware block:

```python
if ai_provider == 'anthropic':
    # Anthropic server-side tools — original block
    server_tools = [{'type': 'web_search_20250305', 'name': 'web_search', ...}]
    tools = tools + server_tools
    print(f'[STREAM] 🔷 Total tools: {len(tools)} ({len(tools) - len(server_tools)} meta + {len(server_tools)} server)')
else:
    # Client-side equivalents for non-Anthropic providers
    from tools.implementations.minimax.search import get_web_search_tool_schema
    from tools.implementations.minimax.fetch import get_fetch_url_tool_schema
    client_tools = [get_web_search_tool_schema(), get_fetch_url_tool_schema()]
    tools = tools + client_tools
    print(f'[STREAM] 🔷 Total tools: {len(tools)} ({len(tools) - len(client_tools)} meta + {len(client_tools)} client — for provider "{ai_provider}")')
```

**Mirror the same pattern in `unified_ai_client.py`** at the existing server-tool append sites (lines 519-541, 1427-1448). The model code path that uses `unified_ai_client.create_message` will then also pick up the new tools.

**Don't change `_PROVIDER_THINKING_MODELS`** — that's about Interleaved Thinking, unrelated to web tools.

### Defence-in-depth

Add a sanity filter in `combined_agent_worker.py:execute_streaming_request` (right after `stream_params` is built, around line 3354) that strips any Anthropic server-tool entries if `ai_provider != 'anthropic'`. This protects against future callers passing pre-mixed `tools` lists:

```python
if ai_provider != 'anthropic' and stream_params.get('tools'):
    _SERVER_PREFIXES = ('web_search_', 'web_fetch_')
    _client = [t for t in stream_params['tools']
               if not (isinstance(t, dict) and t.get('type', '').startswith(_SERVER_PREFIXES))]
    if len(_client) != len(stream_params['tools']):
        print(f'[STREAM] 🛡️  Stripped {len(stream_params["tools"]) - len(_client)} server tool(s) for provider "{ai_provider}"')
    stream_params['tools'] = _client
```

## Regression test

Create `AI_infrastructure/tests/test_minimax_client_tools.py` that:
- Mocks `httpx.post` (or `requests.post`) and returns canned Tavily/Brave responses.
- Calls the `web_search` and `fetch_url` tool functions with various inputs and asserts the output shape.
- Calls `execute_streaming_request` with `ai_provider='MiniMax'` and a tools list that contains a `web_search_20250305` entry — asserts the entry is stripped.
- Calls `execute_streaming_request` with `ai_provider='MiniMax'` and asserts the two new client tools are present.
- Calls `execute_streaming_request` with `ai_provider='anthropic'` and asserts the new client tools are NOT present (so Anthropic users keep the original server-tool experience).

Use `unittest.mock` — no live HTTP calls. The test should be runnable offline with `python AI_infrastructure/tests/test_minimax_client_tools.py`.

## Verification (manual, on Render after deploy)

1. Log in.
2. Open Account Profile → AI Settings. Pick `MiniMax-M3`. Save. Reload — the dropdown should stay on `MiniMax-M3` (this depends on the comprehensive account-profile fix that the owning agent deploys concurrently — confirm before testing the tools).
3. Open Prime AI. Send the message: `"What's the current weather in Brisbane? Use a web search."`
4. **Expected:** The model calls the `web_search` tool. The server log shows `[STREAM] 🔷 Total tools: 9 (7 meta + 2 client — for provider "MiniMax")`. The response includes real, current weather data sourced from the search backend.
5. Send a follow-up: `"Fetch the content at https://en.wikipedia.org/wiki/Brisbane and summarise the first paragraph."`
6. **Expected:** The model calls `fetch_url`. The response includes the actual Wikipedia content.
7. Switch to `claude-sonnet-4-6` and repeat step 3. The server log should show `[STREAM] 🔷 Total tools: 8 (7 meta + 1 server)` and the response should still work — but using Anthropic's native server tools (no Tavily call is made). Verify by checking that no `https://api.tavily.com` requests appear in the Render log.

## Hard constraints (do not violate)

- **Do not add a new tool without a corresponding schema JSON file** in `tools/schemas/`. The registry auto-discovers it.
- **Do not import from `AI_infrastructure/core/archived/`** — that directory is frozen per CLAUDE.md §14.
- **Do not touch `UI/modules_external/manifest.json`** — being replaced by DB-driven loading.
- **Do not touch the BGE model snapshot path** at `/data/vdb_models/` or `~/.cache/vdb_models/`.
- **Do not touch the `inhouse-print` `sys.path` surgery** in `UI/modules_external/inhouse-print/implementations/inhouse_wrapper.py` — load-bearing per CLAUDE.md §13.3.
- **Do not edit the WooCommerce V4 module** — orthogonal work.
- **Do not enable `thinking` on text-only models** — keep `_PROVIDER_THINKING_MODELS` in `combined_agent_worker.py:3010-3016` exactly as-is.
- **No emoji in source code literals** — match the existing style.
- **UTF-8 no-BOM** on all `.js`, `.html`, `.css`, `.json` files. Run `.\.vscode\fix-bom.ps1` before committing.
- **Conventional Commits message format** for your commit(s): `feat(tools,minimax): add client-side web_search and fetch_url for non-Anthropic providers`.
- **No new DB columns or migrations** — the schema is sufficient.
- **No `npm install`** — the frontend has no build step; don't touch `package.json` unless you're adding a dependency for the CAD viewer.
- **Secrets stay out of source.** Tavily API key goes in env vars or the org vault, never in code.

## Tradeoffs you should know about (be honest about these in your report)

Anthropic's `web_search_20250305` server tool has features the client-side equivalent will **not** replicate:
- **Citation tracking.** Anthropic's `web_search_tool_result` block has a special citation format (`web_search_result_location` with `encrypted_index`). The model is trained to use these. Your client tool returns plain text snippets; the model will cite URLs but not with the same quality.
- **`encrypted_content` / `encrypted_index`.** These are Anthropic-specific fields that are decrypted server-side for multi-turn citation carryover. Your client tool returns the raw content, which is bigger and less precise.
- **Quality of results.** Depends entirely on which search backend you pick. Tavily is best-in-class for AI agents; Brave is closer to Google's SERP quality.
- **Pricing.** Anthropic charges $10 per 1,000 searches. Tavily is $0.008 per search on the agent tier; Brave is $0.003. The platform absorbs this cost; account for it.

These are acceptable tradeoffs for fixing the 400 error and giving MiniMax users web access. Document them in the tool's description so the model knows what to expect.

## What to deliver

When you're done, report:
- **Files changed** (paths only).
- **What changed** (1-2 sentences per file).
- **The new schemas** (paste the two `.json` files).
- **The new implementations** (paste the two `.py` files).
- **The wiring diffs** in `agent_routes_v4.py` and `unified_ai_client.py` (just the changed blocks).
- **The defence-in-depth block** in `combined_agent_worker.py`.
- **The test results** — actual output of `python AI_infrastructure/tests/test_minimax_client_tools.py`.
- **The Render log lines** observed after a manual test (steps 4 and 5 above).
- **Any assumptions you made.**
- **Any risks remaining** (e.g. Tavily rate limits, search-result quality differences).

If you get blocked on a decision (which backend? how to handle the 4-tier credential? what input validation?), make a reasonable default, document the choice in your report, and keep moving. Don't ask — the user has authorised you to proceed.

# PROMPT ENDS

---

## After the other agent delivers

The owning agent will:
1. Apply the change-1/server-tool-gate fix from the plan file.
2. Apply the change-2/defence-in-depth fix.
3. Review the agent's commit.
4. Run the full manual verification protocol on Render.
5. Add a row to `ARCHIVE_CLEANUP_TRACKER.md` with a chain-of-custody entry if any documentation was affected.
6. Bump the relevant canonical doc's `Last updated` header.

If the other agent did not run `.\.vscode\fix-bom.ps1` before committing, the owning agent will run it and amend the commit.
