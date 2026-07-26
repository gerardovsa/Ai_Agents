---
title: TOOL_SYSTEM_ROBUSTNESS_2026-07-26
date: 2026-07-26
status: living document
companion_files:
  - tool_usage_system_prompt.md (current canonical prompt, edited today)
  - tool_usage_system_prompt copy 13_trimmed_2026-07-26.md (trimmed variant)
applied_commit: b8c58355 (9 fixes — thinking-block + watchdog + storage hygiene,
                              2026-07-26, deployed → gerardo v11)
                836b151d (fix #1 — server-side tool-name allowlist, 2026-07-26,
                          shipped as ancestor of subsequent auto-deploys)
scope: harden the tool-use pipeline (Anthropic, OpenAI, DeepSeek, MiniMax-M3)
                      against thinking-block hallucination, runaway loops, and
                      fabricated intermediate tool outputs.
---

# Tool-System Robustness — Dated Documentation (2026-07-26)

> **Purpose.** A durable, dated record of (a) what we shipped today, (b) the
> gaps we already know about but haven't fixed yet, (c) what the published
> guidance says we should still consider, and (d) the implementation matrix
> ranked by risk-vs-effort. Living document — update as fixes land.

---

## 0. TL;DR

Today we shipped **10 fixes + 47 smoke tests** across two commits on
2026-07-26, addressing the "Tool Test Rd 5" failure mode (orphan thinking
blocks, signature loss, 4 byte-identical "Excellent news" canned-response
loops) and the "reasoning-amplified model fabricates tool names" attack
mode. Companion system-prompt updates in
[`tool_usage_system_prompt.md`](./tool_usage_system_prompt.md) strengthen the
prompt-level defenses.

| Commit | What it shipped |
|--------|------------------|
| `b8c58355` | F1-A/B/C (signature round-trip), F2 (interleaved-aware reorder), F3 (denylist for thinking-block fields), Adj 4A/B/C (MiniMax-M3 + beta-header conditional), F4 (tool_result SDK class), F5 (runaway-loop watchdog), F6 (storage hygiene + `ensure_ascii=False`) |
| `836b151d` | **Fix #1 — server-side tool-name allowlist** at the dispatch boundary (see §1.7 below; §2.2 marked SHIPPED) |

What we **have not yet shipped** but is now well-grounded in published
research is the **server-side similarity gate** for fabricated tool outputs
inside reasoning blocks (academic confirmation at arXiv 2510.22977 per the
agent's persistent memory; same theme covered empirically by AgentSentinel,
arXiv 2509.07764) — this is the load-bearing remaining change per the
memory note. Recommended order in §5.

> **Note on §2.2 vs §1.7:** §2.2 was written *before* fix #1 shipped and
> still describes the gap as open. The "✅ SHIPPED 2026-07-26" banner at
> the top of §2.2 is the authoritative pointer; §1.7 has the implementation
> details. Do not read §2.2 in isolation.

---

## 1. What was shipped — commit `b8c58355` (Anthropic + MiniMax paths)

### 1.1 Signature round-trip (the load-bearing fix for thinking-block round-trip)

| Fix | Where | What it does |
|-----|-------|---------------|
| **F1-A** | `AI_infrastructure/core/unified_ai_client.py` (Anthropic streaming, ~L713-L741) | Capture `event.delta.signature` from the SDK and attach it to the last `thinking` block in the rolling `target_block` list |
| **F1-B** | `AI_infrastructure/core/unified_ai_client.py` (MiniMax streaming, ~L1138-L1152) | Same as F1-A but in the MiniMax-M3 path |
| **F1-C** | `AI_infrastructure/core/unified_ai_client.py` (`_convert_anthropic_event_to_sse`, ~L1323-L1418) | Forward `signature_delta` SSE event to browser-side cache |

**Side effect:** the smoke test caught a structural bug introduced by F1-C
where the original `elif hasattr(event, 'delta')` branch was **unreachable**
for any `content_block_delta` event. The corrected structure collapses all
four delta kinds (`text_delta`, `thinking_delta`, `signature_delta`,
`input_json_delta`) into one branch.

### 1.2 Thinking-block integrity (provider-conditional)

| Fix | Where | What it does |
|-----|-------|---------------|
| **F2** | `AI_infrastructure/core/unified_ai_client.py` (interleaved-aware reorder, ~L546-L567) | The reorder helper now uses an `_is_interleaved()` detector that **stops** reordering if any thinking block appears after a tool_use block. The previous unconditional reorder silently broke the interleaved-thinking shape that Anthropic and MiniMax-M3 depend on |
| **F3** | `AI_infrastructure/core/combined_agent_worker.py` (`validate_messages_for_api`, ~L161-L178) | Allowlist `{type, thinking, signature}` → **Denylist** `{_client, _callbacks, _request_id, _logprobs, request_id, trace_id}` + forward-compat preservation of unknown fields. Any new provider-side field (e.g. future `reasoning_summary`) is now preserved |
| **Adj 4A** | `AI_infrastructure/core/unified_ai_client.py` (~L599) | `interleaved-thinking-2025-05-14` beta header now sent **only** when `thinking_enabled=True`. Previously always sent |
| **Adj 4B** | `AI_infrastructure/core/unified_ai_client.py` (both paths) | Documented inline: Anthropic and MiniMax-M3 expect the same `thinking={"type":"enabled","budget_tokens":N}` shape — no per-provider branching needed |
| **Adj 4C** | `AI_infrastructure/core/unified_ai_client.py` (MiniMax path, ~L1175-L1212) | New helper strips `redacted_thinking` blocks before MiniMax-M3 call (M3 rejects them with 400) |

### 1.3 Tool-result wire contract (provider SDK parity)

| Fix | Where | What it does |
|-----|-------|---------------|
| **F4** | `AI_infrastructure/core/tool_processor.py` (`build_tool_result_blocks`, ~L232-L267) | Promote `tool_result` to SDK's `BetaToolResultBlockParam` class with explicit `is_error=not result['success']` and a defensive fallback to raw dict |

### 1.4 Runaway-loop containment

| Fix | Where | What it does |
|-----|-------|---------------|
| **F5** | `AI_infrastructure/core/combined_agent_worker.py` (agentic loop top, ~L2147-L2226) | Three-round rolling-window watchdog on text-hash and tool-hash; emits `watchdog_triggered` SSE event and breaks the loop on detection |

### 1.5 Storage hygiene

| Fix | Where | What it does |
|-----|-------|---------------|
| **F6** | `AI_infrastructure/core/unified_session_manager.py` (~L167-L171, 271, 320) + new helper `_assert_storage_parity` | All `json.dumps(..., ensure_ascii=False, default=str)`; new parity watchdog comparing `sessions.sessions.conversation` length with `sessions.messages.content` row count |

### 1.6 Smoke-test coverage

`AI_infrastructure/tests/test_tool_system_robustness_fixes.py` — **28 tests,
26 pass, 2 skipped** (the F4 tests need the `anthropic` SDK which isn't in
this local env; the file explicitly handles this with `self.skipTest(...)`).

```
Ran 28 tests in 0.769s — OK (skipped=2)
```

### 1.7 Server-side tool-name allowlist (Fix #1, commit `836b151d`)

**The single-line gate** at the dispatch boundary of the agentic loop in
`AI_infrastructure/core/combined_agent_worker.py` (`run_simple_agent_worker`,
top of the `try:` block inside the `tool_uses` loop):

```python
if not registry.is_tool_allowed(tool_name):
    # ... build a same-prefix hint (capped at 5) ...
    raise ValueError(
        f"Tool '{tool_name}' is not in the registered tool "
        f"registry ({registered_count} tools available).{hint}"
    )
```

| Aspect | Value |
|--------|-------|
| Helper added | `RegistryV3.is_tool_allowed(name)` + `RegistryV3.list_tool_names()` |
| Location of helpers | `tools/registry_v3.py` (line 899 onward) |
| Meta-tool fallback constant | `_ALLOWED_META_TOOL_NAMES = frozenset({"get_tool_schema", "execute_tool"})` |
| Test file | `AI_infrastructure/tests/test_tool_name_allowlist.py` — **19 tests, all green** |
| Non-string input handling | `None`, empty string, int, list, dict all return `False` (no TypeError on `in`) |
| Recovery path | The existing `except Exception as tool_error:` handler emits a structured `tool_result` with `is_error=True`; the model sees its hallucination labelled as failed and self-corrects on the next turn |
| Provider alignment | Provider-agnostic — gates on `tool_name` only, never on wire format. All 4 providers (Anthropic, OpenAI, DeepSeek, MiniMax-M3) route through the same `tool_uses` loop |
| DB migration | None — gate emits via existing SSE path; no new schema |
| New dependencies | None — `jsonschema` not installed (fix #2 deferred per CLAUDE.md rule #8) |
| Source-invariant tests | TA-10 in the test file grep-checks `combined_agent_worker.py` for `registry.is_tool_allowed(tool_name)` and `TOOL-ALLOWLIST`, and `tools/registry_v3.py` for `def is_tool_allowed(` and the constant. Prevents accidental regression |

**Smoke-test coverage (combined):**

| File | Tests | Notes |
|------|-------|-------|
| `AI_infrastructure/tests/test_tool_system_robustness_fixes.py` | 28 (26 pass, 2 skipped) | The 9-fix series from `b8c58355` |
| `AI_infrastructure/tests/test_tool_name_allowlist.py` | 19 (all pass) | Fix #1 from `836b151d` |
| **Total** | **47 (45 pass, 2 skipped)** | |

---

## 2. What was identified before this PR but is NOT yet shipped

These are the **known remaining gaps** in the platform's tool-use surface.
All are sourced from the agent's prior research and confirmed by the new
research in §3.

### 2.1 Server-side similarity gate (load-bearing fix per agent memory)

**Memory note (`thinking-block tool hallucination`):**
> "MiniMax-M3 (and reasoning-amplified models in general) can write
> fabricated tool output into thinking content and cite it as if it were a
> real tool_result. Academic confirmation at arXiv 2510.22977. Server-side
> similarity gate is the load-bearing fix; prompt-level rules have a
> ceiling."

**The model can say in its thinking:** "I checked Gmail and got 3 unread
emails from Acme Corp about the invoice" — *without* ever calling the
Gmail tool. The next user turn then trusts this "memory" and asks the
assistant to forward them. The assistant confidently complies because it
*believes* it checked. The guardrail must live server-side because
prompt-only rules can be reasoned around by amplified-reasoning models.

**What it looks like in code:** a new check inside the agentic loop,
between `tool_executor` and the model's next turn. For each `tool_use`
block the model emits in the next assistant turn:

1. Reject if the cited `id` does not match a `tool_use_id` we have in
   `tool_intelligence_logger` for the current session.
2. If the reasoning block for that turn *describes* a tool result that
   differs semantically from the actual result we wrote, log a
   `thought_tool_drift` event and either truncate the model output or
   replace the model's described-but-fabricated result with the real one.

Both checks require per-session evidence: a list of `tool_use_id` actually
executed in this conversation. The audit chain is already in
`tool_intelligence_logger`; the gate is a thin reader.

### 2.2 Tool-name allowlist (AgentSentinel pattern, generalizable)

> **✅ SHIPPED 2026-07-26 in commit `836b151d`** — see §1.7 for implementation
> details, file locations, test count, and provider-alignment notes. This
> section is preserved as the original motivation; do not re-read it as a
> pending gap.

The current executor dispatches by `tool_name` lookup in
`tools/registry_v3.py`. If the model invents a `tool_name` that doesn't
exist, the executor returns an error and the loop continues. But:

- The AgentSentinel paper demonstrates that *hallucinated tool names* are
  a **first-class attack vector** — attackers can register malicious
  packages with those names on PyPI.
- In our case, the executor already returns an error for unknown names,
  but the **reasoning step that produced the hallucinated name is
  silently cached into the next conversation turn**, so the model
  keeps "trying" the invented name forever.

**Mitigation:** at the very top of the agentic loop (right where F5
sits), reject any `tool_use` with a `name` not in
`RegistryV3.tool_names()` (the set of registered tool names). Emit a
`hallucinated_tool_name` event with the model's exact citation and the
allowlist it was checked against.

### 2.3 JSON-schema argument validation before execution

The model fills `tool_use.input`. The executor currently trusts the
input, parses JSON, and dispatches. If the model invents a field, the
underlying tool's implementation may fail loudly (good) or accept and
process the unexpected field (bad). The reliability of the existing
behaviour is unknown and worth measuring with a regression test.

**Mitigation:** load each tool's JSON schema from
`tools/schemas/<provider>/*.json`, run `jsonschema.validate(input, schema)`
in `tool_executor.execute_tool()`, and reject with a structured
`{"success": False, "error": "schema_validation_failed", ...}` on
failure. The schema is already authoritative — this is a one-block patch.

### 2.4 Constrained decoding for `tool_use.input`

For the four providers (Anthropic, OpenAI, DeepSeek, MiniMax) every
provider has a mechanism to constrain the `tool_use.input` JSON to a
schema. **However, the providers differ** in how this is exposed:

| Provider | Tool-input enforcement mechanism |
|----------|-----------------------------------|
| Anthropic | `input_schema` per `ToolParam` (server-enforced) |
| OpenAI | `function.parameters` per `Tool` (server-enforced via JSON Schema strict mode) |
| DeepSeek | `function.parameters` per `Tool` (OpenAI-compatible, same constraint) |
| MiniMax-M3 | Reuses Anthropic SDK with custom `base_url`, so `input_schema` is honored |

This means we **already have the right contract field** on the wire. We
need to ensure each tool's JSON schema is mapped 1:1 into
`input_schema` / `function.parameters` when the model is invoked, and
that we set `strict=True` (or its Anthropic-equivalent) where supported.
This blocks the model at the source rather than detecting afterwards.

### 2.5 Conversation integrity seal (signature-based)

The Claude conversation cache stores block-stream arrays. If a downstream
component truncates or reorders the array (currently the F2 reorder for
non-interleaved shapes, the F3 denylist strip, the migration of older
threads onto the new prompt), the next turn's signature_delta may not
match and Anthropic returns 400.

**Mitigation:** when F2/F3 mutates an assistant turn, *invalidate the
signature* on any thinking block whose sibling context was modified.
Either:

- Drop the signature (the model will then start a new thinking trace),
  OR
- Append a `signature_invalidated: true` marker that the Anthropic SDK
  treats as "use the next assistant turn's signature instead".

The Anthropic docs explicitly say signatures are tied to the entire
turn, not to a single block — so the safer default is "drop and retry".

### 2.6 Audit-log schema for forensic review

When the watchdog (F5) fires, we currently emit a `watchdog_triggered`
event but do not preserve the conversation snapshot. For post-mortem
debugging of "Tool Test Rd 5"-class failures we need:

- A `hallucination_incidents` table (or append to `tool_intelligence_logger`
  with a new `kind` value) capturing the full conversation, the round
  hashes, the watchdog trigger, and a timestamp.
- A queryable surface — likely a route on `/api/diagnostics/hallucinations`
  that lists recent incidents with filters (org, session, provider, model).

### 2.7 Self-Check style multi-sample audit (low priority, high cost)

Self-Check style approaches sample multiple invocations and flag
inconsistencies. This is gold-standard for academic benchmarks but
multiplies token cost 3-5x. **Not recommended for production** —
mention only for completeness.

---

## 3. Sources reviewed (research summary, 2026-07-26)

> **Honest disclosure.** Two of the four URLs the user named could not be
> fetched in this environment (the auto-mode classifier blocked
> `arxiv.org/abs/2510.22977`, and the Google "11 eval patterns…" search
> and "AI Agent Hallucinations: Causes…" search returned error pages).
> The arXiv ID `2510.22977` is referenced in the agent's persistent
> memory (`thinking-block tool hallucination` memory, dated before today)
> as the academic confirmation of reasoning-amplified tool fabrication.
> I substituted the three sources below, which cover the same themes.

### 3.1 AgentSentinel — arXiv 2509.07764 (directly relevant)

**Failure modes targeted:**
- Model hallucinates **non-existent Python packages** → attacker uploads
  malicious package with the same name.
- Model invents **malformed file paths** or **undefined program** names.
- ~90-100% Attack Success Rate across Claude 3.5/3.7 Sonnet and GPT-4/4o.

**Server-side defense architecture** (generalizable to our tool dispatch):
1. **Agent Instrumentation** — minimal client SDK that notifies monitor
   of every tool invocation (we already have this via
   `tool_intelligence_logger`).
2. **A2M Protocol** — stateful handshake with **unidirectional trust
   boundary** — monitoring cannot be disabled once enabled.
3. **System Tracer** — 16 eBPF/LSM probes for process / filesystem /
   network. *(We are not at this level; we are at the application-layer
   audit level, but the principle of "monitor the side effects, not just
   the model" applies.)*
4. **Real-time Security Auditor** — rule-based + LLM-based, three-tier
   cache.

**Quantitative results:**
- BadComputerUse benchmark: 60 attack scenarios, **87% ASR** average.
- AgentSentinel DSR: **79.6% average**, peaking at **96.7%** with
  Claude 3.7 Sonnet.
- FPR: 10.8% avg (0% with Claude 3.7 Sonnet).
- FNR: 4.2% avg.

**Direct takeaways for our platform:**
- The tool-name allowlist (§2.2) is the first-line defense — it's the
  application-layer analog of AgentSentin's process-trace enforcement.
- The hierarchical cache (verified file/network ops cached) generalizes
  to "verified tool_result content cached" — every tool call's actual
  result gets a content-addressable hash in
  `tool_intelligence_logger`; reasoning that cites a *different* result
  is fabrication.

### 3.2 Hallucination taxonomy (Lakera-style "factuality, fabrication,
reasoning errors, backend mitigation tactics")

Source page returned a Google error but is referenced by the title
patterns in §3.4 below; the **directly-accessible equivalent** is:

- **Galvanize** — [LLM Hallucinations 101](https://www.galvanize.com/blog/llm-hallucinations-101-why-they-happen-how-to-prevent-them/)
- **Confident AI** — [Why LLMs Hallucinate: taxonomy, prevention, detection](https://www.confident-ai.com/blog/why-llms-hallucinate-taxonomy-prevention-detection)
- **Snorkel AI** — [Mitigating LLM hallucinations at production scale](https://snorkel.ai/blog/mitigating-llm-hallucinations-at-production-scale/)
- **Towards Data Science** — [Reducing LLM Hallucinations: A Developer's Guide](https://towardsdatascience.com/reducing-llm-hallucinations-a-developers-guide/)

These all converge on the same taxonomy:

| Type | Symptom | Backend defense |
|------|---------|-----------------|
| **Factual** | Wrong dates, names, numbers | RAG grounding, retrieval-time verification |
| **Fabrication** | Invented URLs, tool names, package names, identities | **Allowlist enforcement** (§2.2) |
| **Reasoning error** | Chain-of-thought confabulation, cited-but-unexecuted steps | **Server-side similarity gate** (§2.1) |
| **Reasoning amplification** | Reasoning-amplified models fabricate *more*, not less | Same server-side gate, prompt ceiling is documented |

### 3.3 Detection-method taxonomy (EdinburghNLP awesome-hallucination-detection)

The methods in this taxonomy that are **applicable to tool-call output
verification** (sub-section of [the README](https://github.com/EdinburghNLP/awesome-hallucination-detection)):

| Method | What it does | Applicable here? |
|--------|--------------|------------------|
| **EigenScore / INSIDE** | Eigenvalues of covariance matrix of multiple sampled responses | Marginal — sampling 3x is expensive |
| **Semantic Density** | Probability distribution in semantic space | Marginal — same |
| **SelfCheckGPT** | Multi-sample consistency | Marginal |
| **SAC³** | Semantic-aware cross-check consistency | **Yes** — cross-check model's cited result vs. actual result via embedding similarity |
| **QuCo-RAG** | Corpus co-occurrence grounding | n/a — we don't have a corpus mode |
| **HaluCheck (DPA)** | Phrase-level alignment loss | Applicable post-hoc only |
| **Lynx** | Reference-free faithfulness for RAG | Applicable post-hoc only |
| **GraphEval / Pelican** | KG entailment / sub-claim verification | Applicable if we model tool calls as claims |

**Bottom line:** SAC³ cross-check is the most directly applicable to our
scenario (small N, no extra LLM call, embedding similarity only). §5
proposes a 2-employee variant: one embedding model computes cos-sim
between the model's cited tool result and the real tool result; below
threshold (recommend 0.62), we flag and possibly substitute.

### 3.4 Backend-hardening patterns (industry convergence)

From Snorkel AI's "production scale" post and Confident AI's developer
guide, the convergent backend patterns are:

1. **Validation layers** — schema-check input, schema-check output,
   reject loudly. *Direct analog: §2.3 + §2.4.*
2. **Constrained decoding** — server-enforced JSON shape via the
   provider's `input_schema` / `function.parameters`. *Direct analog:
   §2.4.*
3. **Observability** — every tool call, every reasoning block, every
   result, every rejected schema — captured and queryable. *Direct
   analog: §1.5 + §2.6.*
4. **Tool registry as the source of truth** — the model cannot invent
   tools. *Direct analog: §2.2.*

---

## 4. Provider-aware alignment matrix

The four providers expose the same logical surface (tool_use /
tool_result), but the wire contracts differ. The pending fixes must
remain consistent across all four.

| Capability | Anthropic | OpenAI | DeepSeek | MiniMax-M3 |
|------------|-----------|--------|----------|------------|
| Tool-use input schema enforcement | `tools[*].input_schema` | `tools[*].function.parameters` (strict mode) | `tools[*].function.parameters` (OpenAI-compatible) | Inherits Anthropic |
| `is_error` on tool_result | ✅ Beta | ❌ (uses separate `function_call` failure path) | ❌ (same) | ✅ Beta |
| `signature_delta` for thinking | ✅ | n/a | n/a | ✅ (same wire format) |
| `redacted_thinking` | ✅ | n/a | n/a | ❌ rejected (handled by Adj 4C) |
| Beta header required | `interleaved-thinking-2025-05-14` | n/a | n/a | ❌ do not send |
| JSON-Schema strict mode | implicit (Beta) | explicit `strict: true` | `strict: true` (when supported) | implicit |
| Real-time tool-call audit | client-side | client-side | client-side | client-side |

**Implication for §2 fixes:**

- **§2.2 (allowlist)** is provider-agnostic — it lives in our executor
  and rejects before the SDK even sees the call.
- **§2.3 (JSON schema validate)** is provider-agnostic — same input,
  same schema, same `jsonschema.validate()`.
- **§2.4 (constrained decoding)** depends on each provider's schema
  field name, but the **input** is the same JSON Schema. The mapping
  layer lives in `_init_<provider>()` in
  `core/unified_ai_client.py` and is already provider-conditional.
- **§2.1 (similarity gate)** is provider-agnostic — the reasoning
  block is exposed on every Anthropic/MiniMax return, and OpenAI/
  DeepSeek don't have thinking blocks (so the gate is a no-op for
  those two, which is correct — OpenAI/DeepSeek can't *hide*
  fabrication in a thinking block they don't have).

### Database storage requirements

The pending fixes interact with the **dual-storage** model
(`sessions.sessions.conversation` TEXT + `sessions.messages.content`
JSONB, currently monitored by F6). Specifically:

- The similarity gate (§2.1) needs the **last N tool calls** with their
  results. That is already in `tool_intelligence_logger` (per-session
  rows with `tool_use_id`, `result_content`, `created_at`). The gate
  reads from there.
- The audit sink (§2.6) needs a **schema-stable destination**. The cleanest
  addition is a new `kind` value on `tool_intelligence_logger` (e.g.
  `kind='hallucination_incident'`) — no migration required.
- The allowlist (§2.2) does **not** write to either storage — it is
  read-only against `tools/registry_v3.py`.

---

## 5. Recommended implementation matrix

Ordered by *risk reduced per unit of effort*. All entries reference
existing files; no new directory layout required.

| # | Fix | File target | Effort | Risk reduced | Status |
|---|-----|-------------|--------|--------------|--------|
| **1** | **Tool-name allowlist** (§2.2) | `AI_infrastructure/core/tool_executor.py` `execute_tool()` — reject if `tool_name not in RegistryV3.tool_names()`; loop guard in `combined_agent_worker.py` agentic loop | **S** (≈30 LOC) | High — blocks the most-cited hallucination vector in AgentSentinel | ✅ **Shipped 2026-07-26** (`836b151d` — see §1.7) |
| **2** | **JSON-schema input validation** (§2.3) | `AI_infrastructure/core/tool_executor.py` `execute_tool()` — `jsonschema.validate(parameters, tool_schema)` before dispatch | **S** (≈60 LOC including tests) | Medium — catches silently-misformed args before side effects | ⏳ Pending — requires `jsonschema` dep (deferred per CLAUDE.md rule #8) |
| **3** | **Server-side similarity gate** (§2.1) — first pass: tool_use_id grounding only | `AI_infrastructure/core/combined_agent_worker.py` — at top of loop, assert `tool_use_id ∈ session.tool_calls` | **M** (≈120 LOC including audit row write) | **Very high** — this is the load-bearing fix from the memory note | ⏳ **Next recommended** — load-bearing |
| **4** | **Hallucination incident log + diagnostics route** (§2.6) | New table value on `tool_intelligence_logger` + `AI_infrastructure/routes/diagnostics_routes.py` | **S** (≈80 LOC) | Medium — enables future forensics and validation | ⏳ Pending |
| **5** | **Constrained-decoding strict mode** (§2.4) | `AI_infrastructure/core/unified_ai_client.py` `_init_anthropic` / `_init_openai` / `_init_deepseek` / `_init_minimax` — set `strict=True` / `input_schema=` per tool, ensure 1:1 schema mapping | **M** (≈150 LOC across 4 init paths) | High — pushes constraint to the wire so the model can never emit a malformed tool call | ⏳ Pending — see §6 Q2 (OpenAI strict-mode risk) |
| **6** | **SAC³ cross-check similarity gate** (§2.1 step 2) | `AI_infrastructure/core/combined_agent_worker.py` — for reasoning-amplified models, embedding-similarity between reasoning's claim and actual tool_result; on low score, fall back to real result | **L** (≈250 LOC, requires embedding call) | High — closes the "I checked Gmail and got X" fabrication | ⏳ Pending — depends on #3 |
| **7** | **Signature-on-mutation invalidation** (§2.5) | `AI_infrastructure/core/unified_ai_client.py` — when F2/F3 mutates an assistant turn, drop the signature on any thinking block whose sibling context was touched | **S** (≈40 LOC) | Medium — prevents Anthropic 400s after our own fixes touch the cache | ⏳ Pending |
| **8** | **Reasoning-block self-check for MiniMax-M3** | `AI_infrastructure/core/combined_agent_worker.py` — when `provider == "MiniMax"` and `thinking_enabled`, run a lightweight classifier over thinking content looking for invented tool references | **L** (≈300 LOC, needs LLM-classifier call) | Marginal — overlaps with #6 | ⏳ Exploratory |

**Recommended execution order:**

1. ✅ ~~Fix #1 (allowlist)~~ — **DONE 2026-07-26** (commit `836b151d`).
2. Fix #4 (audit log) — sets up the data substrate that #3 reads from.
3. Fix #3 (similarity gate, tool_use_id grounding only) — the load-bearing
   fix from the agent memory.
4. Fix #2 (JSON-schema validate) — drops in once #1 has established the
   pattern.
5. Fix #5 (constrained-decoding strict mode) — leverages what's already
   in `_init_<provider>()`.
6. Fix #7 (signature invalidation) — small follow-up to fix our own
   post-F2/F3 400s.
7. Fix #6 (SAC³ cross-check) — when there's bandwidth.
8. Fix #8 (LLM classifier) — exploratory, behind a feature flag.

---

## 6. Open questions / decisions for the user

1. **§2.6 audit-log retention.** Should hallucination incidents live in
   `tool_intelligence_logger` (cheaper, reuses an existing table), or
   in their own `hallucination_incidents` table (cleaner separation,
   independent retention)? Default proposed: reuse the existing table
   with a new `kind` value, pending your call.
2. **§2.4 strict mode on OpenAI.** OpenAI's `strict: true` requires the
   JSON Schema to be valid by their stricter rules (e.g. all
   properties must be listed in `required`). Several of our tool
   schemas use optional fields; flipping the flag may break older
   tools. Suggest rolling out provider-by-provider with a config flag
   per tool — requires your sign-off.
3. **§2.1 similarity gate policy on false positives.** When the gate
   fires, three policies are possible: (a) reject and ask the model
   to retry, (b) silently substitute the real result, (c) log and
   emit an SSE warning so the UI can show a badge. Default proposed:
   (b) + (c) combined — never block, always log.
4. **§2.6 PII concerns.** Hallucination incidents capture full
   conversation context for forensics. The current
   `tool_intelligence_logger` is per-user / per-org (RLS-scoped).
   Confirm that's the right boundary, or do we need an additional
   admin-only view?

---

## 7. What this doc is NOT

- It is **not** a runbook. The operational steps for any individual
  fix live in the relevant code files (already documented inline per
  CLAUDE.md rule #5).
- It is **not** a substitute for the prompt. The prompt is the
  fast-changing, provider-facing half of the defenses; this doc is
  the slow-changing, server-side half.
- It is **not** exhaustive on research. The four named sources were
  investigated to the extent the environment allowed; the AgentSentinel
  paper and the EdinburghNLP taxonomy are the load-bearing external
  references. New research since today should be incorporated as a
  date-prefixed section at the bottom.

---

## 8. Citation-style sources (for follow-up reads)

- [AgentSentinel — arXiv 2509.07764](https://arxiv.org/html/2509.07764v1) — server-side defense against tool-hallucination attacks (closest to our §2.2 + §2.6)
- [EdinburghNLP awesome-hallucination-detection](https://github.com/EdinburghNLP/awesome-hallucination-detection) — full detection-method taxonomy; SAC³ + EigenScore are the most applicable (§3.3)
- [Lakera — Hallucination Types and Prevention](https://www.lakera.ai/blog/hallucination-types-and-prevention-in-llm-powered-applications) — taxonomy of factuality / fabrication / reasoning-error, with backend mitigation
- [Snorkel AI — Mitigating LLM hallucinations at production scale](https://snorkel.ai/blog/mitigating-llm-hallucinations-at-production-scale/) — constrained decoding + validation layers + observability
- [Confident AI — Why LLMs Hallucinate: taxonomy](https://www.confident-ai.com/blog/why-llms-hallucinate-taxonomy-prevention-detection) — same taxonomy with prevention patterns
- [Towards Data Science — Reducing LLM Hallucinations: A Developer's Guide](https://towardsdatascience.com/reducing-llm-hallucinations-a-developers-guide/) — engineering actionable prevention for reasoning agents
- [Promptfoo — How to red team LLM Agents](https://www.promptfoo.dev/docs/red-team/agents/) — attack patterns for tool-use vulnerabilities
- [awesome-hallucination-detection (GitHub)](https://github.com/EdinburghNLP/awesome-hallucination-detection) — embedding-similarity / Minkowski distance / SDT methods
- arXiv 2510.22977 — *referenced in agent memory as the academic
  confirmation of reasoning-amplified tool fabrication; could not be
  fetched in this session, but its theme is corroborated by
  AgentSentinel (2509.07764) above.*

---

## 9. Change history

| Date | Change | Author |
|------|--------|--------|
| 2026-07-26 | Initial version — captures applied `b8c58355` fixes, lists pending fixes, integrates 4 named sources | Claude Fable 5 (via Claude Code) |
| 2026-07-26 | **Fix #1 SHIPPED** — added `RegistryV3.is_tool_allowed()` and `RegistryV3.list_tool_names()` (`tools/registry_v3.py`); inserted a single-line allowlist gate at the dispatch boundary in `combined_agent_worker.py` (`run_simple_agent_worker`, line 2269+); the gate raises `ValueError` on unregistered names and falls through to the existing `except Exception as tool_error:` handler which emits a structured `tool_result` block with `is_error=True` — the model sees the rejection on its next turn and can self-correct; added `AI_infrastructure/tests/test_tool_name_allowlist.py` (19 tests, all green); no DB migration required (gate emits via existing SSE path); no new dependencies (`jsonschema` not installed — fix #2 deferred per CLAUDE.md rule #8); provider-agnostic — works identically for Anthropic, OpenAI/DeepSeek, MiniMax-M3 | Claude Fable 5 (via Claude Code) |
| 2026-07-26 | **Doc revision for coherence** — four places had drifted out of sync after fix #1: (a) frontmatter `applied_commit` listed only `b8c58355`, now lists both commits; (b) §0 TL;DR described the tool-name allowlist as a future recommendation, now distinguishes shipped (F1-A/B/C + F2 + F3 + 4A/B/C + F4 + F5 + F6 + allowlist) from pending (similarity gate); (c) §2.2 still read as a pending gap, now has a `✅ SHIPPED 2026-07-26 in commit 836b151d` banner pointing to §1.7; (d) §5 implementation matrix marked fix #1 as recommended-first, now marked `✅ Shipped` and a `Status` column added. Added new sub-section §1.7 documenting fix #1's file locations, helper signatures, recovery path, provider-alignment, and test count. Smoke-test coverage now totals **47 tests** (45 pass, 2 skipped) across the two test files. No code changes in this revision — doc-only. | Claude Fable 5 (via Claude Code) |
