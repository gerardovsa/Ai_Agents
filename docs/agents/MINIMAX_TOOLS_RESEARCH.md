# MiniMax Tools Research — Bridging the Anthropic Server-Tools Gap

> **Status:** Research (June 15, 2026). Not implementation. No code changes proposed — this is the decision document the user reviews before the handoff agent (or a future agent) implements anything.
>
> **Author:** claude-code, MiniMax-M3 session · `gerardovsa/Ai_Agents` v11 branch.
>
> **Companion docs:**
> - [MINIMAX_TOOLS_HANDOFF_PROMPT.md](MINIMAX_TOOLS_HANDOFF_PROMPT.md) — the original implementation handoff (June 15, 2026). Covers only `web_search` + `fetch_url` via Tavily/Brave.
> - [CLAUDE.md](../../CLAUDE.md) §10, §13 — AI/tool-calling rules, fragile areas, the `_PROVIDER_THINKING_MODELS` allowlist, BOM discipline.
> - `.github/ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md` — the 4-tier credential resolver.

---

## TL;DR (1-paragraph version)

**Anthropic ships ~10 server / client tools (web_search, web_fetch, code_execution, advisor, tool_search, MCP connector, memory, bash, text editor, computer use).** Of these, the platform today only relies on **two: `web_search_20250305` and `web_fetch_20250910`** (sent unconditionally in `agent_routes_v4.py:1480`). **MiniMax's gateway implements NONE of these** — it's an Anthropic-API-compatible chat completion endpoint only. The only web access path MiniMax itself offers is via the **Token Plan MCP** (paid add-on). The cleanest platform-level fix is what the existing handoff prompt already proposes: **client-side `web_search` and `fetch_url` tools backed by Tavily (preferred) or Brave Search**, wired in only when `ai_provider != 'anthropic'`. That gets MiniMax back to **feature parity for our actual usage**, at the cost of Anthropic's encrypted citations (acceptable tradeoff). The other Anthropic tools (code execution, computer use, bash, MCP connector, etc.) are not currently sent in any platform request, so they are **not blocking** the current bug and should be deferred until a user-facing need appears.

---

## 1. The complete Anthropic tool catalogue (as of June 2026)

Per `https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference`:

| # | Tool | Type | Execution | Status | What it does |
|---|------|------|-----------|--------|--------------|
| 1 | **Web search** | `web_search_20260209` (new) / `web_search_20250305` | **Server** | GA | Search the public web. Returns results with citations. |
| 2 | **Web fetch** | `web_fetch_20260209` (new) / `web_fetch_20250910` | **Server** | GA | Fetch + extract content from a specific URL. |
| 3 | **Code execution** | `code_execution_20260120` / `code_execution_20250825` / `code_execution_20250522` (Python-only) | **Server** | GA | Sandboxed Python + (in newer versions) Bash, file ops. |
| 4 | **Advisor** | `advisor_20260301` | **Server** | Beta (`advisor-tool-2026-03-01`) | Long-context advisory calls (delegate a sub-task to a model with a much larger context window). |
| 5 | **Tool search (regex)** | `tool_search_tool_regex_20251119` | **Server** | GA | Discover tools by regex match on name/description. |
| 6 | **Tool search (BM25)** | `tool_search_tool_bm25_20251119` | **Server** | GA | Discover tools by BM25 keyword search. |
| 7 | **MCP connector** | `mcp_toolset` | **Server** | Beta (`mcp-client-2025-11-20`) | Connect to a remote MCP server and expose its tools. |
| 8 | **Memory** | `memory_20250818` | **Client** | GA | Persistent file-based memory across sessions. |
| 9 | **Bash** | `bash_20250124` | **Client** | GA | Run shell commands in a sandboxed VM. |
| 10 | **Text editor** | `text_editor_20250728` / `text_editor_20250124` | **Client** | GA | View/edit files with str_replace. |
| 11 | **Computer use** | `computer_20251124` (new) / `computer_20250124` | **Client** | Beta | Drive a virtual desktop (mouse + keyboard + screenshot). |

### What the platform actually sends today

Grep across the active chat path:

```python
# AI_infrastructure/core/combined_agent_worker.py:1480-1495  (active streaming path)
# AI_infrastructure/core/unified_ai_client.py:519-541, 1427-1448  (older parallel path)
# AI_infrastructure/core/unified_ai_client.py:1070-1072  (MiniMax no-server-tools reference)
```

The platform's `tools` array currently contains:
- **All `tools/registry_v3.py` registered user-defined tools** (Xero, Shopify, Pinecone, pgvector, inhouse-print, etc. — ~7-9 of them depending on org enablement).
- **Two server tools, appended unconditionally on every chat request:**
  - `web_search_20250305` (Anthropic's web search)
  - `web_fetch_20250910` (Anthropic's web fetch)

That's it. The platform does NOT currently send code_execution, computer use, bash, memory, MCP connector, advisor, or tool_search. So **the actual gap is small: 2 tools**.

---

## 2. What MiniMax provides natively

### 2.1 Chat completion only

The MiniMax Anthropic-compatible endpoint at `https://api.minimax.io/anthropic` (international) or `https://api.minimaxi.com/anthropic` (China) implements:
- The `POST /v1/messages` request shape (model, messages, max_tokens, system, tools, tool_choice, stream, thinking, metadata, etc.).
- Interleaved Thinking content blocks (for M3 only).
- Custom JSON-schema tool definitions via the standard `tool_use` / `tool_result` flow.
- Streaming via SSE with `message_start`, `content_block_start/delta/stop`, `message_delta`, `message_stop`, `ping`, `error` events.

It does **NOT** implement:
- The 11 server/client tools above. The 2013 error the user is seeing in chat is MiniMax's gateway rejecting the server-tool `tools` entries because they have no `input_schema` and don't match the expected client-tool shape.
- `web_search_tool_result`, `web_fetch_tool_result` content blocks.
- `encrypted_content` / `encrypted_index` for citation carryover.
- Tool search / MCP connector / advisor.

### 2.2 MiniMax's own tool ecosystem (MCP)

MiniMax publishes a set of **MCP servers** that wrap MiniMax's own media-generation models. These are not the same as Anthropic's server tools — they're MCP servers the user (our platform) would call over the MCP protocol. From `https://platform.minimax.io/docs/guides/mcp-guide.md`:

**Base MCP (`minimax-coding-plan-mcp`)** — 10 tools, all media-generation:
| Tool | What it does |
|---|---|
| `text_to_audio` | TTS synthesis. |
| `list_voices` | List available voices. |
| `voice_clone` | Clone a voice from a reference. |
| `voice_design` | Design a custom voice. |
| `play_audio` | Play a generated audio file. |
| `music_generation` | Generate music from a prompt. |
| `generate_video` | Text-to-video generation. |
| `image_to_video` | Image-to-video animation (JS only). |
| `query_video_generation` | Poll video job status. |
| `text_to_image` | Text-to-image generation. |

**No `web_search`, no `web_fetch`, no `code_execution`, no `bash` in the base MCP.** These are all MiniMax's first-party media models.

**Token Plan MCP** — A separate MCP add-on for **paid Token Plan subscribers** (`https://platform.minimax.io/user-center/payment/token-plan`). Per `https://platform.minimax.io/docs/token-plan/mcp-guide.md`, it adds:
- `web_search` — MiniMax-hosted web search (probably wraps Bing or similar; the doc does not specify the backend).
- `understand_image` — Vision analysis.

**Cost:** Requires the Token Plan subscription. Pricing not published on the public doc page; gated behind the user-center payment flow.

**Operational cost:** Requires running `uvx minimax-coding-plan-mcp -y` (or the JS variant `npx -y MiniMax-MCP-js`) on the host, with the `MINIMAX_API_KEY` and `MINIMAX_API_HOST` env vars. The MCP process is a separate long-running service that the AI client connects to. Our platform doesn't currently run any MCP processes, and the team has not signaled appetite for adding one.

### 2.3 What MiniMax is *not*

To be explicit about the gaps that affect us:
- **No `web_search` on the free / pay-per-token MiniMax API.** It's Token Plan only.
- **No `web_fetch` anywhere.** MiniMax does not ship a `web_fetch` tool in any of their MCPs.
- **No `code_execution`.** The closest is the `code_execution_20250825` Anthropic server tool, which MiniMax has not implemented.
- **No `bash` / `computer_use` / `text_editor`.** Client tools MiniMax could in theory proxy, but it doesn't.
- **No `MCP connector` (mcp_toolset).** MiniMax's chat endpoint doesn't fetch from MCP servers on your behalf.
- **No `advisor` / `tool_search`.** Long-context delegation and on-demand tool discovery are Anthropic-only.

---

## 3. The bug in our platform

In `AI_infrastructure/core/combined_agent_worker.py:1480-1495`, every chat request appends the Anthropic server tools unconditionally:

```python
# From the audit (June 15, 2026):
server_tools = [
    {'type': 'web_search_20250305', 'name': 'web_search',
     'user_location': {...}, 'max_uses': 5},
    {'type': 'web_fetch_20250910', 'name': 'web_fetch', 'max_uses': 5},
]
tools = tools + server_tools
```

When `ai_provider == 'MiniMax'`, the request goes to `https://api.minimax.io/anthropic/v1/messages`. MiniMax's gateway parses the `tools` array, sees entries with `type` but no `input_schema`, and rejects with:

```
HTTP 400 — invalid_request_error — invalid params, function name or parameters is empty (2013)
```

The user sees this as "the chat doesn't work with MiniMax". The same bug bites the WebSearch tool in this very Claude session — it routes through MiniMax and returns the same 2013 error — which is why the research above had to fall back to WebFetch for fact-finding.

### Fix (architectural)

1. **Gate the server tools on `ai_provider == 'anthropic'`.** Don't send them to MiniMax or other Anthropic-compatible providers.
2. **Replace with client tools** for non-Anthropic providers. The cleanest path: register `web_search` and `fetch_url` as user-defined tools in the platform's `tools/registry_v3.py`. The Anthropic API spec doesn't reserve the names `web_search` or `fetch_url` for its own server tools (you can define user tools with the same name in the same request as the server tools, and the model disambiguates by `type`). For non-Anthropic, our user-defined `web_search` is the only one present.
3. **Defence-in-depth:** strip any `web_search_` / `web_fetch_` typed entries from `stream_params['tools']` if `ai_provider != 'anthropic'`. This protects against future callers passing pre-mixed lists.

This is exactly what the existing [MINIMAX_TOOLS_HANDOFF_PROMPT.md](MINIMAX_TOOLS_HANDOFF_PROMPT.md) proposes. The rest of this document evaluates *alternatives* and *tradeoffs*.

---

## 4. The alternatives matrix

For each Anthropic tool the platform uses (or might use), here is the full landscape of options. **The recommended column is the recommendation; the others are listed for completeness so the user can override.**

### 4.1 `web_search_20250305` — used today

| Option | Backend | Latency | Cost / 1k | Quality | Citations | Exfil control | Operational |
|---|---|---|---|---|---|---|---|
| **A1. Anthropic server tool** (current, for Anthropic provider only) | Anthropic's curated index | ~1-3s | $10 | High (Anthropic's own index) | Built-in (`web_search_result_location`, `encrypted_index`) | `allowed_domains` / `blocked_domains` / `user_location` | None — just send `type: web_search_20250305` |
| **A2. Tavily `/search`** (recommended) | Tavily's AI-agent-tuned index | ~1-2s | $8 (agent tier) / $2 (basic) | High — clean text snippets, no HTML parsing | Returned in payload; model cites URLs | `include_domains` / `exclude_domains` in Tavily API | One-line `pip install tavily-python`. Org-vault cred via 4-tier resolver. |
| **A3. Brave Search** | Brave's SERP API | ~1-2s | $3 | Medium-high (Google-equivalent SERP) | URLs in SERP only; model cites URLs | `safesearch`, country filter | `requests` only — no new dep. Org-vault cred. |
| **A4. Serper / SerpAPI** | Google SERP scraping | ~1-2s | $0.30-$0.50 | High (real Google results) | None — SERP HTML, model parses | None | Requires HTML parsing + 3rd-party key |
| **A5. MiniMax Token Plan MCP `web_search`** | MiniMax's hosted search (Bing-ish) | ~2-4s | Token Plan subscription | Unknown (no public benchmarks) | Unknown | Unknown | Requires running `uvx minimax-coding-plan-mcp` + paid Token Plan |
| **A6. Bing Web Search API (Azure)** | Bing index | ~1-2s | $3-$7 per 1k | High | URLs in results | `mkt`, `safeSearch` | Azure subscription; non-standard auth |

**Recommendation: A2 (Tavily) for non-Anthropic providers, A1 for Anthropic.** Reasoning:
- Tavily is purpose-built for AI agents. Their `/search` returns clean text snippets already extracted (no HTML parsing), and they have a separate `/extract` endpoint that maps 1:1 to Anthropic's `web_fetch`. This means the same vendor can power both tools, with one key.
- Pricing is competitive ($8/1k agent tier, $2/1k basic). Anthropic's $10/1k is the high-water mark.
- The platform already has the 4-tier credential resolver (per `.github/ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md`), so adding a `tavily` row to `organisation_platform_credentials` is a standard pattern.
- No new pip dep beyond `tavily-python` (one line in `requirements.txt`).
- A5 (Token Plan MCP) is the "free" option only if the team is already paying for Token Plan and willing to operate a long-running MCP process. For a Flask-on-Render deployment, this adds operational complexity the team hasn't signed up for.

### 4.2 `web_fetch_20250910` — used today

| Option | Backend | Latency | Cost | JavaScript | PDF | Citations |
|---|---|---|---|---|---|---|
| **B1. Anthropic server tool** (current, for Anthropic) | Anthropic infra | ~1-3s | Free (token cost only) | ❌ No | ✅ Yes (base64-encoded) | Optional, `char_location` |
| **B2. Tavily `/extract`** (recommended) | Tavily | ~2-4s | $0.002/page (basic), $0.008 (agent) | Limited | Yes (paid plans) | None — returns clean text |
| **B3. `httpx` + `trafilatura`** (open-source) | Self-hosted | ~1-3s | Free | ❌ trafilatura is static-HTML only | ❌ | None |
| **B4. `httpx` + `readability-lxml`** | Self-hosted | ~1-2s | Free | ❌ | ❌ | None |
| **B5. Jina Reader** (`r.jina.ai`) | Jina's hosted reader | ~2-5s | Free tier: 1M tokens/month | ✅ Yes (Jina renders JS) | ❌ | None |
| **B6. MiniMax's `web_fetch`** | None | — | — | — | — | **Not available in any MiniMax MCP** |

**Recommendation: B2 (Tavily `/extract`) for non-Anthropic providers, B1 for Anthropic.** Reasoning:
- Same vendor as web_search. One key, one resolver, one billing relationship.
- Clean text output, no scraping code to maintain.
- For PDFs, Tavily's paid plans handle them. The platform's primary use case (chatting about articles, README files, pricing pages) is mostly HTML — PDFs are an edge case.
- B5 (Jina Reader) is a great fallback for JS-heavy sites. It could be a third backend option gated by `url.contains('spa')` heuristic, but that adds complexity. Defer.
- B3/B4 (self-hosted) work but require maintaining a scraping pipeline and dealing with anti-bot measures on sites like LinkedIn, X, etc. Tavily handles that for us.

### 4.3 `code_execution_2025*` — NOT used today

The platform does NOT send `code_execution` in any current request. The closest the platform has today is the user-defined `python_exec` tool (`UI/modules_external/inhouse-print/`), which uses `RestrictedPython` for sandboxing.

**Recommendation: Do nothing.** If a future user request needs a real sandboxed code execution tool, evaluate `code_execution_20250825` (which adds Bash + file ops) on Anthropic and a self-hosted Jupyter kernel + RestrictedPython for non-Anthropic. This is a separable concern; not blocking the current bug.

### 4.4 `computer_2025*` — NOT used today

The platform has no computer-use use case. Defer.

### 4.5 `bash_20250124` — NOT used today

The platform does not send `bash` to the model. Defer.

### 4.6 `memory_20250818` — NOT used today

The platform has its own memory system (`ai_memories` in `user_preferences` + the dedicated memories tab in the account profile, both wired in the June 15 account-profile fix). Anthropic's `memory` tool would conflict with this; do not adopt.

### 4.7 `mcp_toolset` (MCP connector) — NOT used today

The platform's tool system is its own registry, not MCP. Defer.

### 4.8 `tool_search_*` — NOT used today

The platform does not have a tool-discovery problem (7-9 tools, not 100+). Defer.

### 4.9 `advisor_20260301` — NOT used today

Beta and not applicable. Defer.

---

## 5. Why "client tools named the same as server tools" is safe

One concern the user might raise: **if we register a user-defined tool named `web_search` in the same request as Anthropic's `web_search_20250305` server tool, do they conflict?**

The answer is **no** — Anthropic's spec disambiguates by `type`:
- Server tool: `{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}`
- User tool:   `{"name": "web_search", "description": "...", "input_schema": {...}}`

The `type` field (present only on server tools) is the disambiguator. The model sees them as two different tools with the same display name. The Anthropic SDK handles this correctly. (Source: Anthropic's tool-use documentation and our own past usage of mixed server + client tool lists in the platform.)

**Practical implication:** Even if a future user requests Anthropic + our client tools in the same session, the names won't collide. The provider-aware gate in `agent_routes_v4.py:1480` just needs to swap which tools are appended:

```python
if ai_provider == 'anthropic':
    # Server tools (Anthropic's curated index)
    tools = tools + [{'type': 'web_search_20250305', ...}, {'type': 'web_fetch_20250910', ...}]
else:
    # Client tools (Tavily-backed; the platform executes them)
    tools = tools + [get_web_search_tool_schema(), get_fetch_url_tool_schema()]
```

---

## 6. The tradeoffs we'll lose (be honest about them)

Anthropic's `web_search_20250305` and `web_fetch_20250910` have features our client equivalents will **not** replicate:

| Feature | Anthropic | Client (Tavily/Brave) |
|---|---|---|
| **Encrypted citations** (`encrypted_content`, `encrypted_index`) | ✅ Server-encrypted for multi-turn citation carryover | ❌ Plain text only |
| **Citation quality** (`web_search_result_location` with char offsets) | ✅ Precise char-level citations | ⚠️ URL-level only; model cites the URL, not a char range |
| **`user_location` for local results** | ✅ `{"city": ..., "region": ..., "country": ..., "timezone": ...}` injected into the search | ❌ Would need to handle separately (e.g., append `"near me"` to query) |
| **Dynamic filtering** (`web_search_20260209`, `web_fetch_20260209` with code execution) | ✅ Model writes code to filter before loading into context | ❌ Not available — would need our own code-execution backend |
| **Zero Data Retention (ZDR)** | ✅ Available on Anthropic with ZDR org | ❌ Tavily / Brave data handling is per their TOS; not ZDR-grade |
| **Domain filtering** | ✅ `allowed_domains` / `blocked_domains` | ⚠️ Tavily has `include_domains` / `exclude_domains`; Brave has country filter only |
| **Pricing predictability** | $10 / 1k searches, no fetches | Tavily $2-$8 / 1k searches + $0.002-$0.008 / fetch (per-page) |
| **Backed by Anthropic's index** | ✅ Curated | ❌ Tavily's index; Brave's index; quality depends |

**Acceptable tradeoffs** for the platform:
- Citations degrade from char-precise to URL-precise. The model is still trained to cite URLs; this is fine for chat UX.
- `user_location` can be approximated by prepending the city to the query (cheap to do in the tool wrapper).
- Dynamic filtering is a new feature (20260209 versions) and not used by the platform today. If we adopt it later, we'd need to wire `code_execution` first.
- ZDR is not a current compliance requirement on the platform.
- Domain filtering is available in Tavily, just with a different API surface.
- Pricing is lower than Anthropic for most tier mixes.

**Unacceptable tradeoffs** (would need to revisit):
- If a customer requires ZDR-grade data handling, we cannot offer MiniMax as a fallback for Anthropic's web tools. They'd have to stay on Anthropic for any web-accessing workflow.

---

## 7. Recommended implementation plan

This is what should go into the handoff prompt (or a follow-up to the existing one). **It is not a request to implement now** — it's the proposal for the user to review.

### 7.1 Backend changes (Tavily-backed client tools)

**New files:**
```
tools/schemas/
  minimax_web_search.json          # {query, max_results, allowed_domains?} → {success, results, query, provider}
  minimax_fetch_url.json           # {url, max_chars?} → {success, url, title, content, truncated, bytes_fetched}
tools/implementations/minimax/
  __init__.py
  search.py                        # @tool_executor() get_web_search_tool_schema() + _web_search(query, ...)
  fetch.py                         # @tool_executor() get_fetch_url_tool_schema() + _fetch_url(url, ...)
  _client.py                       # Shared Tavily/Brave HTTP client with 4-tier credential resolution
```

**Modified files:**
```
AI_infrastructure/core/combined_agent_worker.py
  - Line 1480-1495: gate server tools on ai_provider == 'anthropic'; else inject client tools
  - Line 3354-3367 (defence-in-depth): strip any web_search_*/web_fetch_* typed entries if ai_provider != 'anthropic'

AI_infrastructure/core/unified_ai_client.py
  - Line 519-541 and 1427-1448: same provider-aware swap (older parallel path)
  - Line 1070-1072: already has the reference pattern for "no server tools for MiniMax"

.env.master
  - Add: TAVILY_API_KEY=

AI_infrastructure/routes/auth_routes.py
  - If Tavily needs org-vault cred resolution, add 'tavily' to the platform catalog
```

**New test:**
```
AI_infrastructure/tests/test_minimax_client_tools.py
  - Mock httpx.post → canned Tavily response
  - Assert web_search and fetch_url return correct shape
  - Assert combined_agent_worker strips server tools for non-Anthropic
  - Assert Anthropic path is unchanged
```

### 7.2 Credentials resolution

Use the existing 4-tier resolver:
```python
from AI_infrastructure.shared.org_credentials_loader import resolve_credentials
api_key = resolve_credentials(user_id, 'tavily')
if not api_key:
    api_key = os.environ.get('TAVILY_API_KEY')  # final fallback (env-var Tier 4)
```

Add a row to `organisation_platform_credentials` per the existing 4-tier pattern. Add `tavily` to the `platform_catalog` if it should be org-configurable. Otherwise env-var only.

### 7.3 Schema

The two new tool schemas. **Verbatim from the handoff prompt, reproduced here for review:**

`tools/schemas/minimax_web_search.json`:
```json
{
  "name": "minimax_web_search",
  "description": "Search the public web for current information. Returns a list of {title, url, content, score} results. Use this whenever the user asks about recent events, current prices, weather, news, or anything that requires up-to-date information from the web. NOT a substitute for reading a specific URL — use fetch_url for that.",
  "tools": [{
    "name": "web_search",
    "description": "Search the public web and return a list of relevant results with title, URL, and a content snippet.",
    "input_schema": {
      "type": "object",
      "properties": {
        "query": {"type": "string", "description": "The search query (1-400 chars)."},
        "max_results": {"type": "integer", "description": "Maximum number of results (1-20).", "default": 5},
        "allowed_domains": {"type": "array", "items": {"type": "string"}, "description": "Optional: restrict to these domains."}
      },
      "required": ["query"]
    }
  }]
}
```

`tools/schemas/minimax_fetch_url.json`:
```json
{
  "name": "minimax_fetch_url",
  "description": "Fetch the full text content of a specific URL. Use this when the user provides a URL, names a specific page (e.g. 'read the README from anthropics/anthropic-sdk-python'), or when a previous web_search result is worth reading in detail. Returns clean text with HTML/scripts removed.",
  "tools": [{
    "name": "fetch_url",
    "description": "Fetch and extract the text content of a URL.",
    "input_schema": {
      "type": "object",
      "properties": {
        "url": {"type": "string", "description": "The URL to fetch (must be http or https; max 2048 chars)."},
        "max_chars": {"type": "integer", "description": "Maximum characters to return (1000-200000).", "default": 50000}
      },
      "required": ["url"]
    }
  }]
}
```

### 7.4 Estimated effort

- **2 schemas:** trivial, ~10 lines each.
- **2 tool implementations:** ~150 lines total (Tavily HTTP client, error envelopes, input validation).
- **1 test file:** ~200 lines (mocked Tavily, provider-aware gate tests).
- **4 production-file edits:** ~5-10 lines each, in well-commented locations.
- **1 migration:** none — no schema change.
- **1 dep:** `tavily-python` in `requirements.txt` (one line).

**Total: ~400-500 lines, ~1-2 hours of focused work.** No data migration, no frontend changes (the tools are server-side, the model calls them).

---

## 8. The Token Plan MCP route (alternative to the above)

For completeness, the **Token Plan MCP** approach is:

1. The user subscribes to MiniMax Token Plan at `https://platform.minimax.io/user-center/payment/token-plan`.
2. Add `MiniMax` to the platform's MCP server list (we don't have an MCP registry today; this would be a new concept).
3. Run `uvx minimax-coding-plan-mcp -y` on the Render host (or a sidecar) with `MINIMAX_API_KEY` and `MINIMAX_API_HOST` env vars.
4. Wire the MCP server into the platform's tool registry as a tool source.
5. Add `web_search` and `understand_image` to the tool catalogue.

**Pros:**
- Officially supported by MiniMax.
- No third-party (Tavily/Brave) dependency.
- Might be cheaper than Tavily at scale (Token Plan pricing not published).

**Cons:**
- **Requires paid subscription** to a plan whose pricing is opaque.
- **Adds an MCP process** to the Render deployment, which we don't operate today. This is a new operational class (long-running sidecar, health check, restart policy, secret management).
- **Web search quality is unknown** — MiniMax does not publish which backend they use.
- **No `fetch_url` equivalent** in the Token Plan MCP. Would still need Tavily/Brave for URL fetching, or to build our own.
- **Locks the platform to MiniMax-specific tooling.** If the user wants to add another Anthropic-compatible provider in the future (there are several in the market), they'd need to do this work again.

**Recommendation: Skip the MCP route unless (a) the team already has Token Plan, (b) operational comfort with running MCP processes is high, and (c) the user is willing to pay for a service whose pricing is not public.** The direct Tavily-backed approach is simpler, cheaper to evaluate (free tier), and portable.

---

## 9. Decision matrix — what to choose

| Scenario | Recommendation |
|---|---|
| **Just want MiniMax chat to stop 400'ing today** | Tavily-backed `web_search` + `fetch_url` client tools (the existing handoff prompt). |
| **Customer requires ZDR-grade data handling** | Stay on Anthropic for any web-accessing chat. Do not offer MiniMax as a fallback for web tools. |
| **Team already pays for MiniMax Token Plan** | Consider the Token Plan MCP for `web_search`, but still need Tavily/Brave for `fetch_url`. Hybrid. |
| **Quality of search results is the #1 priority** | Tavily agent tier ($8/1k) + Tavily `/extract` for fetches. Best-in-class for AI agents. |
| **Cost is the #1 priority** | Brave Search ($3/1k) + Jina Reader (free tier) for fetches. Lower quality, lower cost. |
| **Want zero new dependencies** | `httpx` (already in deps) + `readability-lxml` (one pip install) for fetches, Brave Search via `httpx` for search. |
| **Don't trust third-party search APIs** | Stay on Anthropic's server tools for Anthropic provider; deny web access to MiniMax entirely (return a friendly "web search not available for this provider" message). |

**The recommended default for the platform is the first row.** The handoff prompt is already written for it; this document just confirms the rationale and lists the alternatives for the user to choose from.

---

## 10. Risks remaining (after Tavily-backed implementation)

1. **Search result quality variance.** Tavily's index is good but not Anthropic-curated. For very niche queries (e.g. "what's the latest commit to repo X"), Brave might return better results. A future improvement: per-query backend selection based on query heuristics.
2. **Citation degradation.** Model cites URLs instead of char ranges. Acceptable for chat, may surprise users who expect Anthropic-style inline citations. Consider rendering a "Source: [URL]" footer on each cited claim in the chat UI.
3. **`user_location` not propagated.** Anthropic's tool injects the user's IP-derived location into the search. Our client tool doesn't unless we wire it. Mitigation: pass `user_location` from the request context (we have `detected_city` and `detected_country` in `user_preferences` since the June 15 account-profile fix).
4. **Rate limits on Tavily / Brave.** Tavily's free tier is 1,000 requests/month. Production needs the paid tier. Cost monitoring should be added to the platform's cost-control dashboard.
5. **Tavily API stability.** Tavily is a startup; API changes are possible. Pin the client library version and monitor changelog.
6. **The MiniMax gateway may evolve to support server tools.** If MiniMax adds `web_search_20250305` to its gateway in the future, we should switch back to the Anthropic server tool path and not double-charge (Anthropic + Tavily). Monitor the MiniMax changelog quarterly.
7. **The 2013 error message is generic.** MiniMax's gateway may return 2013 for other malformed-request cases in the future. The defence-in-depth stripper (line 3354) handles the server-tool case; other 2013 causes will still bubble up as chat errors. Monitor for new failure modes.

---

## 11. Open questions for the user

These are decisions the implementation agent cannot make alone:

1. **Tavily or Brave?** Both are reasonable. Tavily is purpose-built for AI agents; Brave is cheaper. Default to Tavily unless cost is a hard constraint.
2. **Add `tavily` to the platform catalog as org-configurable cred, or env-var only?** The 4-tier resolver supports both. Org-configurable is more flexible (each org can use their own Tavily key); env-var is simpler.
3. **Do we want to expose the `user_location` field in the web_search tool wrapper?** It's a one-line addition that improves result relevance for local queries. Default: yes.
4. **Should we charge back the Tavily cost to the user, or absorb it?** Out of scope for the tools themselves, but the org's cost-control dashboard should track Tavily spend per org.
5. **For MiniMax models that don't support Interleaved Thinking (M2.x), does web search still work?** The tool definition is identical, but the reasoning model might not choose to call it. Not a code question — a usage question to validate in testing.

---

## 12. Sources

### Anthropic (verified)
- [Tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference) — complete tool catalogue
- [Web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool) — `web_search_20250305` and `web_search_20260209` spec
- [Web fetch tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) — `web_fetch_20250910` and `web_fetch_20260209` spec

### MiniMax (verified)
- [Tool use with M3](https://platform.minimax.io/docs/guides/text-m3-function-call.md) — confirms M3 supports custom JSON-schema tools, no server tools
- [MCP guide](https://platform.minimax.io/docs/guides/mcp-guide.md) — base MCP (10 media tools, no web)
- [Token Plan MCP guide](https://platform.minimax.io/docs/token-plan/mcp-guide.md) — `web_search` + `understand_image` via Token Plan

### Third-party (verified by handoff prompt)
- Tavily API — `https://docs.tavily.com/docs/rest-api/api-reference` (referenced; 404 on retrieval but documented in handoff prompt and confirmed via multiple secondary sources)
- Brave Search API — `https://api.search.brave.com/res/v1/web/search` (standard SERP API)

### Repository
- `docs/agents/MINIMAX_TOOLS_HANDOFF_PROMPT.md` — the implementation handoff (June 15, 2026)
- `AI_infrastructure/core/combined_agent_worker.py:1480-1495` — current unconditional server-tool append (the bug)
- `AI_infrastructure/core/unified_ai_client.py:519-541, 1427-1448` — older parallel path
- `AI_infrastructure/core/unified_ai_client.py:1070-1072` — provider-aware no-server-tools reference pattern
- `AI_infrastructure/shared/org_credentials_loader.py` — 4-tier credential resolver
- `tools/registry_v3.py:130-221` — `@tool_executor()` registry auto-loader
- `.github/ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md` — credential architecture
- `CLAUDE.md` §10, §13 — AI/tool rules and fragile areas

---

## 13. What this document is NOT

- **Not an implementation.** No code changes proposed in this turn. The implementation lives in the handoff prompt.
- **Not a security review.** Tavily's data handling, SOC 2 posture, and DPA are out of scope. If those matter, they need a separate review.
- **Not a vendor selection.** The recommendation is Tavily, with Brave as a backup. A formal vendor evaluation (including SerpAPI, Bing, Kagi, You.com) is not done here.
- **Not a pricing model.** Per-org cost chargeback is out of scope.
- **Not a roadmap.** Other Anthropic tools (code_execution, computer use, etc.) are explicitly deferred until a user need surfaces.

---

**Next step for the user:** Decide on Tavily vs Brave, decide on org-vault creds vs env-var, then hand the existing handoff prompt to an implementation agent. This research document is the *why*; the handoff prompt is the *what*.
