# Thread — Message Construction Master Document

> **Status:** LIVING DOCUMENT. Canonical source of truth for how a thread's
> system prompt, message window, and AI response are constructed and observed.
> Created **2026-07-29** as the companion to
> [`THREAD_SYSTEM_MASTER_2026_07_22.md`](THREAD_SYSTEM_MASTER_2026_07_22.md).
>
> That doc covers **the card / drag-drop / catalogue / CASCADE layer**
> (what the user sees and how they move threads around).
> This doc covers **the prompt / message / response / token layer**
> (what the AI sees, in what order, what it emits back, and how we measure it).
>
> **Audience:** anyone debugging AI response quality, token-budget overruns,
> "the model lost track of my request" symptoms, or extending the message
> pipeline (e.g. adding a new thinking-mode provider, surfacing token usage,
> changing the conversation cap).
>
> **How to keep this doc alive:** when you change the prompt assembly
> pipeline, the message window policy, the token telemetry emitter, or any
> provider-specific quirk in `combined_agent_worker.py`, update the relevant
> section in the same PR and append a dated note to the Change log (§17).

---

## 1. What this doc covers

1. The 5 layers that make up the system prompt the AI actually sees
2. The `USERS NEW REQUEST` anchor (and why it exists)
3. The conversation-window policy (30 → 500 cap, raised 2026-07-29)
4. The AI response loop (tool-use, thinking blocks, streaming, termination)
5. The exact DB write sequence per AI turn
6. Provider-specific quirks (anthropic, openai, deepseek, MiniMax)
7. Token telemetry: model-aware context windows, tier classification,
   `token_status` SSE event, frontend indicator
8. What was implemented in this session vs what was tried and discarded
9. Honest impact assessment
10. Open work and follow-ups

---

## 2. Glossary

| Term | Meaning in this doc |
|---|---|
| **Thread** | One persistent conversation. A row in `sessions.threads` and the `sessions.messages` that belong to it. |
| **System prompt** | The single string passed as the `system` parameter to the model API. Assembled at runtime from 5 layers. |
| **tool_usage_prompt** | Layer 1 — the static 1896-line file `AI_infrastructure/prompts/tool_usage_system_prompt.md`. Loaded once at startup, cached. |
| **data_agent_prompt** | Layer 2 — the smaller dynamic prompt from `SystemPromptBuilder.build_prompt()` (base + platform guidance + tool patterns + anti-XML). |
| **user_context_block** | Layer 3 — the per-thread context injected by the prompt-injection manager (workspace, agent, summary, etc.). |
| **system_prompt_continued** | Layer 4 — a hardcoded tail block in `agent_routes_v4.py` describing `SERVER TOOLS` (web_search, etc.). |
| **USERS NEW REQUEST anchor** | Layer 5 — the user's latest message, appended *after* the literal `END OF SYSTEM INSTRUCTIONS` separator. **Added 2026-07-29 in commit `74bcc17a`.** |
| **last_message** | The text portion of the last user message, extracted by `agent_routes_v4.py` before the prompt is finalized. Used to build layer 5. |
| **last_message_content** | The *full* content list (text + image + document blocks) preserved when the message is multimodal. |
| **exec_user_prompt / exec_conversation** | The variable pair that gets fed to the provider. `exec_user_prompt` is the last user message as a string; `exec_conversation` is the conversation history *without* the last message (the last message is passed separately via the user-role message). |
| **provider** | One of `anthropic`, `openai`, `deepseek`, `MiniMax` (migration 051 widened the CHECK constraint on `organisations.ai_provider`). |
| **_PROVIDER_THINKING_MODELS** | The allowlist of (provider, model) pairs that may receive a `thinking` parameter. **Only `anthropic` (Claude Sonnet/Opus 4.x) and `MiniMax-M3` qualify.** |
| **thinking block** | A provider-native content block (`type: "thinking"`) the model can emit before text/tool_use. Contains the reasoning trace. Immutable across turns. |
| **token_status event** | An SSE message emitted on the `/ws/streaming` namespace **after each AI turn completes**. Payload: `{tokens, context_window, pct, model, tier, message_count, thread_id}`. |
| **tier** | One of `ok` (<50%), `info` (50–75%), `warning` (75–90%), `critical` (≥90%). Maps to CSS colour classes in `thread-card-styles.css`. |
| **context_window** | The model's input-token budget. Looked up via the `_MODEL_CONTEXT_WINDOWS` dict in `combined_agent_worker.py`; defaults to 1,000,000 if unknown. |

---

## 3. The construction pipeline at a glance

```
                    ┌─────────────────────────────────────────────────────┐
                    │   User types a message in Prime (or agent column)   │
                    └────────────────────────────┬────────────────────────┘
                                                 │
                                                 ▼
                    ┌─────────────────────────────────────────────────────┐
                    │  POST /api/agent/chat (agent_routes_v4.py)          │
                    │  - resolve credentials (4-tier loader)              │
                    │  - load conversation from sessions.messages          │
                    │  - extract last_message (Layer-5 source)             │
                    └────────────────────────────┬────────────────────────┘
                                                 │
                                                 ▼
                    ┌─────────────────────────────────────────────────────┐
                    │  Build the system prompt (5 layers, ~30–60k chars)  │
                    │   1. tool_usage_prompt           (static, cached)   │
                    │   2. data_agent_prompt           (per-org dynamic)  │
                    │   3. user_context_block          (per-thread)       │
                    │   4. system_prompt_continued     (hardcoded tail)   │
                    │   5. USERS NEW REQUEST anchor    (NEW 07-29)        │
                    └────────────────────────────┬────────────────────────┘
                                                 │
                                                 ▼
                    ┌─────────────────────────────────────────────────────┐
                    │  Build exec_conversation (history w/o last msg)     │
                    │  + exec_user_prompt (the last message as string)    │
                    └────────────────────────────┬────────────────────────┘
                                                 │
                                                 ▼
                    ┌─────────────────────────────────────────────────────┐
                    │  combined_agent_worker.run_simple_agent_worker()    │
                    │  - applies 500-message cap (NEW 07-29, was 30)      │
                    │  - chooses thinking mode (provider + model check)   │
                    │  - dispatches to provider client                    │
                    │  - runs tool-use loop until stop_reason             │
                    │  - counts total_conversation_tokens                 │
                    │  - classifies tier (ok/info/warning/critical)       │
                    │  - emits `token_status` SSE event  (NEW 07-29)      │
                    └────────────────────────────┬────────────────────────┘
                                                 │
                                                 ▼
                    ┌─────────────────────────────────────────────────────┐
                    │  Persist + stream                                   │
                    │  - INSERT INTO sessions.messages (assistant + tools) │
                    │  - UPDATE sessions.threads SET token_count,         │
                    │                            message_count (trig)     │
                    │  - Stream chunks to client via /ws/streaming         │
                    └─────────────────────────────────────────────────────┘
```

---

## 4. Detailed request lifecycle

`POST /api/agent/chat` (handler in `AI_infrastructure/routes/agent_routes_v4.py`):

1. **JWT decode** (set by `@before_request` in `flask_app.py`) — populates
   `g.rls_user_id`, `g.rls_org_id`.
2. **Body parse** — `{message, thread_id, location, model, provider, thinking_enabled, …}`.
3. **Credential resolve** — `org_credentials_loader.resolve_credentials(user_id, platform_key)`
   uses the 4-tier resolver (per-user → org vault → sub-user inheritance → env fallback).
4. **Conversation load** — `SELECT * FROM sessions.messages WHERE thread_id = $1 ORDER BY created_at`,
   returns the full history including the just-written user message.
5. **`last_message` extraction** (lines ~1115–1144) — walks the conversation
   backwards to find the user-role message. For multimodal messages
   (image/document blocks), `last_message` is the text portion and
   `last_message_content` is the full content list.
6. **Conversation split** — `conversation_without_current` = history minus the
   last user message; `exec_user_prompt` = `last_message` (string form);
   for multimodal: `exec_conversation` = history + `[{'role':'user','content': last_message_content}]`.
7. **Provider init** — `unified_ai_client.initialize_ai_client(org)` resolves
   `provider` from `organisations.ai_provider` (default fallback) and dispatches
   to `_init_anthropic` / `_init_openai` / `_init_deepseek` / `_init_minimax`.
8. **Prompt assembly** — see §5.
9. **Worker dispatch** — `run_simple_agent_worker(...)` with the conversation,
   exec_user_prompt, tools schema, and org config.
10. **Streaming** — every chunk is forwarded over `/ws/streaming` (room = thread_id).
11. **Persistence** — see §8.

---

## 5. System prompt assembly — the 5 layers

The final `system` parameter sent to the model API is built by **5 string
concatenations in this exact order**. The order matters: each layer assumes
the previous one is already in place.

### Layer 1 — `tool_usage_prompt` (static, ~30k chars)
- Source: [`AI_infrastructure/prompts/tool_usage_system_prompt.md`](AI_infrastructure/prompts/tool_usage_system_prompt.md) (1896 lines).
- Loader: `unified_ai_client.py:278` → `prompt_path = Path(__file__).parent.parent / 'prompts' / 'tool_usage_system_prompt.md'`.
- Cached on `self._tool_usage_prompt` after first read.
- Ends with a literal `END OF SYSTEM INSTRUCTIONS` terminator (which is
  what the new Layer-5 anchor visually mirrors).

### Layer 2 — `data_agent_prompt` (per-org dynamic, ~5k chars)
- Source: [`AI_infrastructure/builders/system_prompt_builder.py`](AI_infrastructure/builders/system_prompt_builder.py) — `build_prompt(user_context, available_platforms, org_id)`.
- Components: base prompt → user context → platform guidance (Google Workspace, M365, calculator, vector_db) → tool usage patterns → anti-XML instructions.
- The `vector_db` platform guidance uses `get_vector_db_guidance_text(org_id)`
  to inject the active provider + secondary providers (migration 052).
- Conditional on `available_platforms` (the user's connected integrations).

### Layer 3 — `user_context_block` (per-thread, ~1–5k chars)
- Injected by the prompt-injection manager, contains workspace name, agent
  assignment, prior summary if any, etc.
- Appended with: `system_prompt += f"\n\n{user_context_block}\n"` (line 1538).

### Layer 4 — `system_prompt_continued` (hardcoded, ~500 chars)
- A static tail block describing `SERVER TOOLS (Always Available)`:
  web_search, str_replace_based_edit_tool, list_workspace_files, etc.
- Defined inline at `agent_routes_v4.py:2015–2056`.
- Appended with: `system_prompt += system_prompt_continued` (line 2059).

### Layer 5 — `USERS NEW REQUEST` anchor **(NEW 2026-07-29)**
- Appended **after** Layer 4 with an explicit boundary so the model sees:
  ```
  \n\n---\n\n
  END OF SYSTEM INSTRUCTIONS\n\n
  ---\n\n
  USERS NEW REQUEST:\n\n
  <last_message>\n
  ```
- Implementation: `agent_routes_v4.py:2061–2077` (added in commit `74bcc17a`).
- Skipped with a warning if `last_message` is empty (defends against the
  race condition where the user message hasn't been written to the DB yet —
  the extractor at line 1147 retries once after 1 second).

### Layer 5 — why this exists
Before this change, a long Layer 1 + Layer 2 prompt could push the user's
actual task far from the model's "current focus" — particularly in extended
thinking mode where the model has a fixed context window. The anchor:

- **Mirrors the static file's terminator** (`END OF SYSTEM INSTRUCTIONS`)
  so the boundary is unambiguous to the model.
- **Duplicates the last user message** intentionally. The same content
  appears as the last `user` role message in `exec_conversation` *and* at
  the bottom of the system prompt. This is a known mitigation for
  "lost in the middle" syndrome in long-context models.
- **Costs ~1k–10k chars** per turn (the size of `last_message`). Negligible
  vs the existing prompt, but worth noting in token-budget discussions.

### Total prompt size (typical)
| Org setup | Approx. chars |
|---|---|
| Minimal (no platforms, no context) | ~30k |
| Typical (Google Workspace, vector_db, calculator) | ~40–50k |
| Heavy (all platforms + long context block) | ~60–80k |

---

## 6. Message-window policy

### Before 2026-07-29
- Hard cap of **30 messages** in `combined_agent_worker.py` (line 2256 area).
- On a 200k Sonnet window with a ~40k system prompt, 30 messages of average
  size (~2k chars each, ~500 tokens) ≈ 15k tokens. About 27% of the window.
- On M3's 1M window this was a *severe* underutilisation — the user reported
  long threads "losing track".

### After 2026-07-29 (commit `74bcc17a`)
- Cap raised to **500 messages**.
- Comment in source explicitly notes the M3 1M context rationale.
- At ~500 tokens per average message that's still ~250k tokens for a very
  long thread — comfortable for M3, tight for Sonnet 200k, will trip the
  new token_status `warning`/`critical` tier at the higher message counts.

### Where the cap is enforced
- `combined_agent_worker.py` line ~2256 (now `if len(messages) > 500: …`).
- The check is applied *after* `exec_conversation` is built but *before* the
  provider call, so it never sees the full conversation.
- Trimming strategy: oldest messages are dropped (FIFO). The user's most
  recent message is always preserved (it was extracted separately as
  `exec_user_prompt`).
- The system prompt (Layers 1–5) is **not** counted toward the 500 cap.

### Why 500, not "all messages"?
- Defends against pathological cases (a script-generated thread with 10k
  messages) where the prompt would silently exceed the model's actual
  context window even before our 90% critical tier fires.
- Gives the `token_status` indicator room to show realistic percentages —
  at 500 messages the user gets a meaningful "you're at 60% of the
  window, careful" signal before overflow.

---

## 7. AI response loop (in `combined_agent_worker.py`)

High-level shape:

```
loop:
    response = provider.create_message(
        system=system_prompt,
        messages=exec_conversation,
        tools=tool_schemas,
        thinking=thinking_param,        # only if provider+model allow
        temperature=final_temperature,   # MUST be 1.0 if thinking_param
    )

    if response.stop_reason == 'end_turn':
        save_assistant_message(response.content)
        update_token_counters()
        emit_token_status_sse()        # NEW 2026-07-29
        break

    if response.stop_reason == 'tool_use':
        for each tool_use block in response.content:
            result = tool_executor.execute(tool_use)
            save_tool_result_message(tool_use.id, result)
        continue   # back to loop top, model sees its own tool results

    if response.stop_reason == 'max_tokens':
        save_assistant_message_truncated()
        emit_token_status_sse(tier='critical')   # likely already critical
        break
```

### Thinking blocks
- Validation: `validate_and_clean_thinking_blocks()` ensures blocks are
  immutable across turns, has the right `{type, thinking, signature, data}`
  shape, and forbids consecutive assistant messages both containing thinking
  blocks (Anthropic API rejects this).
- Allowed providers + models:
  ```python
  _PROVIDER_THINKING_MODELS = {
      'anthropic': {'claude-sonnet-4-5', 'claude-sonnet-4-6',
                    'claude-opus-4-7',   'claude-opus-4-8',
                    'claude-haiku-4-5-20251001'},
      'MiniMax':  {'MiniMax-M3'},
  }
  ```
- **Adaptive thinking** (newer Anthropic param `{type: 'adaptive'}`) is
  applied to `claude-opus-4-7`. Older models use `{type: 'enabled', budget_tokens}`.
- Enabling thinking forces `temperature = 1.0` (Anthropic API requirement).
- **MiniMax-M3** is the only MiniMax variant with Interleaved Thinking —
  M2 and any future M-series are text-only by default.

### Streaming
- Every provider response is chunked via `StreamingManager` and forwarded
  on the `/ws/streaming` namespace (room = thread_id).
- The `AI_REQUEST` / `AI_RESPONSE` banner pattern (commit `7e52ce70`)
  replaces older ad-hoc banners in the SPA.
- On a 529/overload from upstream, the SPA shows "AI provider overloaded"
  (commit `bd5841ed`) and stops the pulsing icon.

---

## 8. Database write sequence (per turn)

After the AI response completes, the worker writes the following in this
order. All writes go through `execute_query()` and are RLS-scoped via
`g.rls_user_id` / `g.rls_org_id`.

| # | Table | Operation | Notes |
|---|---|---|---|
| 1 | `sessions.messages` | INSERT | The assistant's response (with thinking + tool_use blocks preserved as JSONB). |
| 2 | `sessions.messages` | INSERT (×N) | One row per tool result. Each linked to the assistant message via `parent_message_id`. |
| 3 | `sessions.threads` | UPDATE `token_count` | Cumulative input + output tokens for this turn. |
| 4 | `sessions.threads` | UPDATE `message_count` | **Maintained by trigger** from migration `052_denormalize_thread_message_counters.sql` — fires on INSERT into `sessions.messages`. |
| 5 | `sessions.threads` | UPDATE `last_message_at` | Same trigger. |
| 6 | `tool_intelligence_logger` | INSERT | Tool name, args summary, outcome (success/error). Does **not** log full model output by default (privacy). |

The `token_status` SSE event is emitted **after** steps 1–5 (so the
`message_count` field in the payload reflects the freshly-written rows).
It is NOT persisted to the DB — it's a pure real-time notification.

---

## 9. Provider-specific sequence

All four providers share `_process_anthropic` for tool-use loop handling,
but the dispatch and message-formatting differ at the edges.

### Anthropic (`_init_anthropic`)
- Direct `anthropic.Anthropic()` SDK call.
- Full thinking-block support (4 Sonnet/Opus models + Haiku 4.5).
- Tool-use loop is fully streamed.
- **Credential tier**: any of the 4 (user → org vault → sub-user inheritance → env).

### OpenAI (`_init_openai`)
- `openai.OpenAI()` SDK with `gpt-4o` / `gpt-4o-mini` etc.
- Thinking blocks are **not** emitted by OpenAI; the worker passes
  `thinking_param = None` unconditionally.
- Function-calling is converted to OpenAI's `functions`/`tools` shape by
  [`tool_schema_converter.py`](AI_infrastructure/builders/tool_schema_converter.py).
- Embeddings (`text-embedding-3-small` 768-dim) used by the vector DB
  pipeline when BGE local isn't selected.

### DeepSeek (`_init_deepseek`)
- Uses the **OpenAI SDK with a custom `base_url`** (DeepSeek is OpenAI-compatible).
- Default model: `deepseek-reasoner` (R1, supports reasoning blocks similar to thinking).
- Thinking-mode handling: DeepSeek reasoning content is converted to a
  thinking block before being returned to the rest of the worker, so the
  downstream code paths are uniform.

### MiniMax (`_init_minimax`)
- Reuses `anthropic.Anthropic(base_url="https://api.minimax.io/anthropic")`.
- **Only `MiniMax-M3` supports Interleaved Thinking** — M2 and any
  future M-series are text-only. The allowlist enforces this.
- MiniMax has zero Anthropic server tools (per
  `docs/agents/MINIMAX_TOOLS_RESEARCH.md`); for tool use, the worker
  injects Tavily-backed client tools as needed.
- Known hallucination risk: M3 can fabricate tool output into thinking
  content blocks and cite it as if real. The token cap + similarity gate
  at the prompt-injection layer are the load-bearing mitigations (see
  memory: `thinking-block-tool-hallucination`).

---

## 10. Token telemetry pipeline

### Backend (combined_agent_worker.py, lines ~2256–2372)

```python
_MODEL_CONTEXT_WINDOWS = {
    'MiniMax-M3':                1_000_000,
    'MiniMax-M2':                  200_000,
    'claude-sonnet-4-5':           200_000,
    'claude-sonnet-4-6':           200_000,
    'claude-opus-4-7':             200_000,
    'claude-opus-4-8':             200_000,
    'claude-haiku-4-5-20251001':   200_000,
    'gpt-4o':                      128_000,
    'gpt-4o-mini':                 128_000,
    'o1':                          200_000,
    'o3-mini':                     200_000,
    'deepseek-chat':                64_000,
    'deepseek-reasoner':            64_000,
}
context_window = _MODEL_CONTEXT_WINDOWS.get(ai_model, 1_000_000)  # safe default
pct_of_context = (total_conversation_tokens / context_window) * 100

if   pct_of_context >= 90: tier = 'critical'
elif pct_of_context >= 75: tier = 'warning'
elif pct_of_context >= 50: tier = 'info'
else:                      tier = 'ok'

flask_app.socketio.emit(
    'token_status',
    {
        'tokens':         total_conversation_tokens,
        'context_window': context_window,
        'pct':            round(pct_of_context, 2),
        'model':          ai_model,
        'tier':           tier,
        'message_count':  len(messages),
        'thread_id':      thread_id,
    },
    room=thread_id,
    namespace='/ws/streaming',
)
```

### Frontend (UI/business-ai-platform-v2.html + thread-card-*)

Three template files render the indicator (so it appears in Prime, every
agent column, the sidebar, and Synergy):
- [`thread-card-templates.js:compactCard()`](UI/modules_internal/thread-cards/thread-card-templates.js#L264) — the `thread-meta-row-always-visible` class (Prime-loaded thread card).
- [`thread-card-templates.js:fullCard()`](UI/modules_internal/thread-cards/thread-card-templates.js#L349) — the deprecated full card (legacy Prime panel).
- [`thread-card-templates.js:metaRow()`](UI/modules_internal/thread-cards/thread-card-templates.js#L550) — helper used by sidebar / catalogue renderers.

Each renders a `<span class="thread-token-indicator tier-ok" id="thread-token-${thread.id}">` with the placeholder text `0 / 1M` so the row never pops in/out on first paint.

CSS tiers (in [`thread-card-styles.css`](UI/modules_internal/thread-cards/thread-card-styles.css#L1379)):
| Tier | Colour | Background | Animation |
|---|---|---|---|
| `tier-ok` | slate-500 | rgba(107,114,128,0.08) | none |
| `tier-info` | blue-600 | rgba(37,99,235,0.10) | none |
| `tier-warning` | amber-700 | rgba(245,158,11,0.15) | none |
| `tier-critical` | red-700 | rgba(220,38,38,0.15) | 2s pulse |

Socket handler in `_bindSocketEvents()` (business-ai-platform-v2.html:32532):
- Listens for `token_status` events on `/ws/streaming`.
- Updates **all** `.thread-token-indicator[data-thread-id="X"]` elements on
  the page (Prime + agent columns + sidebar can all show the same thread).
- Formats the count: `1.2k` for 1k–10k, `15k` for 10k–1M, `1.2M` for ≥1M.
- Refreshes the tooltip with the model + raw token numbers.

### What this is NOT
- The indicator is **not** persisted. There's no `last_token_count` on
  `sessions.threads` (could be added — see §14 open questions).
- It's **not** emitted mid-stream — only after a full AI turn completes.
  During a long tool-use loop the indicator can be stale by 30+ seconds.
- It does **not** count tool-result tokens added during the same turn
  (only the conversation state at the start of the turn). An approximation,
  not a billing-grade count.

---

## 11. What we implemented in this session (commit `74bcc17a`, 2026-07-29)

### Change 1 — User-request anchor (Layer 5 of the system prompt)
- **File:** `AI_infrastructure/routes/agent_routes_v4.py` (+19 lines)
- **Where:** After Layer 4 (`system_prompt_continued` append at line 2059).
- **What:** Appends `END OF SYSTEM INSTRUCTIONS\n---\nUSERS NEW REQUEST:\n<last_message>`.
- **Why:** Counter the "model lost track" symptom in long threads; provide
  an unambiguous anchor at the very end of the prompt.
- **Verified:** Print statement at line 2075 logs the +chars on each turn.

### Change 2 — 30 → 500 message cap
- **File:** `AI_infrastructure/core/combined_agent_worker.py` (~+12 lines)
- **Where:** Around line 2256 (just after `_PROVIDER_THINKING_MODELS`
  allowlist; the cap is enforced earlier in the worker setup).
- **What:** Replaces the hard `30` with `500` and a comment explaining
  the M3 1M rationale.
- **Why:** Unlocks the 1M context advantage of MiniMax-M3.

### Change 3 — Token telemetry (backend SSE + frontend indicator)
- **Backend:** `AI_infrastructure/core/combined_agent_worker.py` (~+120 lines)
  - `_MODEL_CONTEXT_WINDOWS` lookup table.
  - Tier classification (ok / info / warning / critical).
  - `socketio.emit('token_status', …, room=thread_id, namespace='/ws/streaming')`
    after the AI response is finalised.
- **Frontend indicator:** `UI/modules_internal/thread-cards/thread-card-templates.js`
  (+18 lines across `compactCard`, `fullCard`, `metaRow`) — server-rendered
  placeholder span with `data-thread-id` for the DOM lookup.
- **Frontend CSS:** `UI/modules_internal/thread-cards/thread-card-styles.css`
  (+40 lines) — `.thread-token-indicator` + 4 tier colour classes + critical pulse.
- **Frontend listener:** `UI/business-ai-platform-v2.html` (+61 lines) —
  `_renderTokenStatus()` helper + `socket.on('token_status', …)` in
  `_bindSocketEvents`.
- **Why:** User-visible warning system for context-window exhaustion.

---

## 12. What we considered but didn't ship

| Idea | Reason deferred |
|---|---|
| **Add a `last_token_count` column on `sessions.threads`** | Would need a migration (after `52_denormalize_thread_message_counters.sql`). Useful for showing the indicator on a thread the user hasn't opened yet, but the SSE stream covers all loaded threads anyway. Worth doing — see §14. |
| **Persist `token_status` events to a `token_usage_log` table for billing** | Billing-grade token accounting is a separate project. The current `tool_intelligence_logger` records tool usage but not token usage. |
| **Mid-stream token-status heartbeat** (every N seconds during a long tool loop) | Would require emitting during the tool loop, not just after it. Possible with a background timer; not implemented because the user-reported symptom was post-turn staleness, not intra-turn. |
| **Smarter prompt-injection of the user-request anchor** (e.g. only re-state the *task* rather than the full message) | More elegant but riskier — the model might miss nuances in the user's exact wording. The duplication is intentional. |
| **Model-aware thinking-mode budgets** (larger budget for M3, smaller for Haiku) | `_PROVIDER_THINKING_MODELS` is provider-aware but the budget is global. Per-model tuning is a future optimisation. |
| **Replace the duplicated `last_message` in system prompt with a one-line summary** | Would require a summariser call before each turn — adds latency and an LLM dependency. The duplication is cheaper and more predictable. |
| **Cap the conversation at the model's context window, not at 500 messages** | Hard to compute without first building the prompt (chicken-and-egg). The 500 cap + `token_status` indicator gives the user enough signal. |
| **Server-side render the tier colour** based on `sessions.threads.token_count` from the DB | Would be more consistent (the indicator would be the right colour on first paint, not after the first SSE event). Requires a per-thread DB read on every card render — currently avoided by the lightweight placeholder. Worth doing if lag becomes a complaint. |

---

## 13. Impact assessment — honest

### What is unambiguously good
1. **The 500-cap raise unblocks M3's primary advantage.** The 30-cap was
   the biggest artificial constraint on a 1M-context model. Even at
   200k Sonnet, 500 messages averages ~250k tokens — pushing into the
   `warning` tier on the indicator, which is exactly when the user
   *wants* to know. (Good.)
2. **The `token_status` indicator gives the user real visibility.** Before,
   context overflow was a silent "the AI stopped making sense" event.
   Now the user gets a colour-coded chip with an exact percentage.
   This converts an invisible problem into a visible one.
3. **The user-request anchor is cheap insurance.** ~1–10k extra chars per
   turn is negligible. The "model lost track" symptom had no other fix
   identified; this addresses the most likely root cause (the model's
   attention drifting from the actual task).

### What is ambiguous or risky
1. **The user-request anchor duplicates the last user message.** On M3 this
   is fine; on a 200k Sonnet with a heavy prompt and a long thread, the
   extra tokens could push us closer to the warning tier than necessary.
   A leaner variant (one-line task reminder) would be better-engineered
   but higher-risk.
2. **The token count is approximate.** We count conversation tokens once
   at the start of a turn and add the tool-result tokens only if they're
   persisted before the next provider call. The `token_status` payload
   may understate actual tokens by 5–15% during a tool-heavy turn.
3. **The 500 cap may still be too tight for some users.** A long-running
   PDF analysis thread (BGE embeddings + many tool results) can exceed
   500 messages easily. No automated test covers this case; we ship on
   observation. If users hit it, raising to 1000 is a one-line change.

### What we did NOT do (acknowledged gaps)
1. **No regression test.** Per CLAUDE.md §8, "When fixing a bug, add a
   regression test." This was a feature, not a bug fix, but a small
   smoke test (call `/api/agent/chat`, assert a `token_status` event
   fires) would catch silent regressions in the future. Recommend adding
   one in `AI_infrastructure/tests/` next session.
2. **No DB persistence.** The token count exists only in SSE events. If a
   user reloads the page mid-turn, they lose the indicator state until
   the next AI response. See §14.
3. **No live notification on tier transitions.** A user might prefer a
   toast when the tier jumps from `ok` to `warning`. Currently silent
   colour change only. Easy follow-up.

### Net assessment
This commit is a **net positive** for AI response quality and user
visibility. The three changes target three distinct user-reported symptoms
("model lost track", "can't run long threads", "don't know when I'm running
out of context"). None of them are load-bearing for the platform's stability
(we didn't touch the tool executor, the credential resolver, the DB schema,
or the auth path), so the blast radius of any regression is limited to
the chat UX.

The biggest follow-up that would meaningfully extend the value here is
**persisting token counts on `sessions.threads`** so the indicator works
on first render (no flash from 0 → actual). See §14.

---

## 14. Open questions and follow-ups

| # | Priority | Item | Notes |
|---|---|---|---|
| 1 | medium | ~~Add `last_token_count INT` + `last_token_tier TEXT` to `sessions.threads`~~ **✅ DONE 2026-07-29 (follow-up session)** | Migration `064_thread_token_telemetry_columns.sql` adds `last_token_tier TEXT`, `last_token_model TEXT`, `last_token_pct NUMERIC(5,2)`, `last_token_updated_at TIMESTAMPTZ` (the existing `token_count` column was already there from a legacy migration, so we only added the four telemetry fields). Partial index `idx_threads_last_token_tier_pressure` covers only non-`ok` rows for cheap pressure queries. CHECK constraint pins the tier values. Worker writes via `UPDATE sessions.threads … SET last_token_tier = …` immediately after the `token_status` SSE emit at `combined_agent_worker.py` line ~2373. Idempotent; safe to re-run. |
| 2 | medium | ~~Add a regression test: `tests/test_token_status_event.py`~~ **🟡 PARTIAL 2026-07-29 (follow-up session)** | Added `AI_infrastructure/tests/test_token_status_tier_classification.py` — 22 unit tests pin the tier classification thresholds (4 boundaries + edges), the `_MODEL_CONTEXT_WINDOWS` table contents, the safe-default fallback, and the severity-rank monotonicity the toast logic relies on. The full SSE smoke (hit `/api/agent/chat`, assert event fires) is **still not covered** — covered by manual prod verification, not an automated test. Next iteration: wire `Flask.test_client()` to call the worker with a stub provider and assert the emit payload. |
| 3 | low | Mid-stream token-status heartbeat during long tool loops | Background timer that re-emits every 15s while a tool loop is running. Deferred — user-reported symptom was post-turn staleness, not intra-turn. |
| 4 | low | ~~Toast notification on tier transition (`ok → info → warning → critical`)~~ **✅ DONE 2026-07-29 (follow-up session)** | Added a closure-scoped `_previousTokenTiers` map keyed by `thread_id` in `business-ai-platform-v2.html`. At the end of `_renderTokenStatus()`, the handler compares the incoming tier to the previous one and fires `showToast(...)` only on transitions: `ok\|info → warning\|critical` fires `'error'` style; `warning\|critical → ok\|info` fires `'success'` style. `ok → info` is silent (not actionable). TIER_RANK order (`ok:0 < info:1 < warning:2 < critical:3`) is pinned by the regression test (`TestTierTransitionOrdering`). |
| 5 | low | Switch from `last_message` duplication to a one-line task reminder | Requires a summariser call; higher-risk. |
| 6 | low | Model-aware thinking budgets (per `_PROVIDER_THINKING_MODELS`) | Trivial code change; deferred until we observe budget issues. |
| 7 | low | Persist `token_status` events to a `token_usage_log` for billing | Separate project; billing-grade accounting needs its own design. |
| 8 | low | `metaRow` helper is used by only a few callers — audit and either consolidate or remove | Cosmetic. |

**Follow-up session summary (2026-07-29):** Items §14.1, §14.2 (partial), and §14.4 shipped. The other five (§14.3, §14.5–§14.8) remain open.

---

## 15. How to verify this doc

```bash
# 1. The 5-layer assembly + USERS NEW REQUEST anchor
grep -n "USERS NEW REQUEST\|END OF SYSTEM INSTRUCTIONS\|system_prompt +=" \
    AI_infrastructure/routes/agent_routes_v4.py

# 2. The 500-cap (and confirm the old 30 is gone)
grep -n "if len(messages) >\|message cap\|500\b" \
    AI_infrastructure/core/combined_agent_worker.py

# 3. The token_status emitter and tier table
grep -n "token_status\|_MODEL_CONTEXT_WINDOWS\|tier = " \
    AI_infrastructure/core/combined_agent_worker.py

# 4. The frontend indicator template + listener
grep -n "thread-token-indicator\|token_status" \
    UI/modules_internal/thread-cards/thread-card-templates.js \
    UI/business-ai-platform-v2.html

# 5. The CSS tiers
grep -n "thread-token-indicator\|tier-ok\|tier-critical" \
    UI/modules_internal/thread-cards/thread-card-styles.css

# 6. The thinking-models allowlist
grep -n "_PROVIDER_THINKING_MODELS\|SUPPORTS_THINKING_MODELS" \
    AI_infrastructure/core/combined_agent_worker.py
```

If any of these checks return fewer hits than §1–§11 imply, the doc has
drifted — update the relevant section.

---

## 16. Related documents

- [`THREAD_SYSTEM_MASTER_2026_07_22.md`](THREAD_SYSTEM_MASTER_2026_07_22.md) — the *card / drag-drop / catalogue / CASCADE* layer. Read this first if you're debugging why a thread card doesn't show or a drag-drop fails.
- `CLAUDE.md` (repo root) — repo conventions, agent operating rules, multi-tenant architecture, migration conventions.
- `.github/ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md` — the 4-tier credential resolver (relevant when the agent worker fetches API keys).
- `.github/VECTOR_DB_DEVELOPER_REFERENCE.md` — for any thread with `title_embedding` / `name_embedding` populated by the pgvector pipeline.
- `AI_infrastructure/prompts/tool_usage_system_prompt.md` — Layer 1 in full.
- `AI_infrastructure/builders/system_prompt_builder.py` — Layer 2 source.
- `AI_infrastructure/utils/token_counter.py` — exact token counts via Anthropic's `/messages/count_tokens` endpoint (used by the pre-flight banner; not yet wired into `token_status`).

---

## 17. Change log

| Date | Author | Change |
|---|---|---|
| 2026-07-29 | Feature session | Initial version. Created alongside commit `74bcc17a` which (a) added Layer 5 user-request anchor to the system prompt, (b) raised the conversation cap from 30 → 500 messages, (c) shipped end-to-end token telemetry (backend SSE + 4-tier frontend indicator in every thread card). Doc covers all three changes plus the broader pipeline they live in. |
| 2026-07-29 | Follow-up session | Shipped the three open work items from §14: (1) **migration 064_thread_token_telemetry_columns.sql** adds `last_token_tier / last_token_model / last_token_pct / last_token_updated_at` columns on `sessions.threads` with a partial index for non-`ok` rows and a CHECK constraint on the tier values; (2) worker (`combined_agent_worker.py`) now UPDATEs the thread row after every `token_status` emit, eliminating the page-reload "0 / 1M" flash; (3) **regression test** `AI_infrastructure/tests/test_token_status_tier_classification.py` pins the four tier boundaries, the `_MODEL_CONTEXT_WINDOWS` table, the safe-default fallback, and the severity-rank monotonicity the toast logic relies on — 22 tests, all passing. (4) Frontend (`business-ai-platform-v2.html`) now fires `showToast(...)` on tier transitions only: `ok\|info → warning\|critical` shows a red toast; `warning\|critical → ok\|info` shows a green toast; `ok → info` is silent. §14.2 stays PARTIAL — the SSE smoke test (full `/api/agent/chat` round-trip) is still uncovered. All other follow-ups (§14.3, §14.5–§14.8) remain open. |