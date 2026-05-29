# Platform Comparison & UI/UX Improvement Analysis
**Date: May 29, 2026**
**Scope: Claude.ai vs ChatGPT vs This Platform — Architecture, Design, and UX Improvement Options**

---

## PART 1 — PLATFORM ARCHITECTURE COMPARISON

---

### 1. Overall Page Shell

**Claude.ai**
```
html
└── body
    └── #root  (React root)
        └── .flex.h-screen.w-full (full-viewport flex row)
            ├── [LEFT SIDEBAR]    overflow-y:scroll; width:260px; bg: dark grey
            └── [MAIN AREA]       flex:1; flex-col; bg: off-white / dark
                ├── [THREAD HEADER]    sticky top; conversation title
                ├── [MESSAGE SCROLLER] flex:1; overflow-y:auto   ← THE CONTAINER
                ├── [ARTIFACTS PANEL]  absolute right; slides in
                └── [INPUT AREA]       sticky bottom
```

**ChatGPT**
```
html
└── body
    └── #__next  (Next.js root)
        └── .relative.flex.h-full.w-full (full-viewport flex row)
            ├── [LEFT SIDEBAR]     width:260px; position:fixed; bg: sidebar grey
            └── [MAIN AREA]        margin-left:260px; flex-col
                ├── [NAV BAR]      sticky top; model selector + share + memory badge
                ├── [MESSAGE SCROLLER] overflow-y:auto; pb:32   ← THE CONTAINER
                ├── [CANVAS PANEL] absolute right; slides in for code/docs
                └── [INPUT AREA]   sticky bottom; z-index:10
```

**This Platform**
```
html
└── body
    └── .flex.h-screen (full-viewport flex row)
        ├── [LEFT SIDEBAR]         module navigation, fixed width
        └── [MAIN CONTENT AREA]    flex:1
            ├── [AGENT COLUMNS AREA]   horizontal flex row, overflow-x:auto
            │     ├── [Column-1]   .agent-column  (400/600/800px or 60px collapsed)
            │     │     ├── .agent-header
            │     │     ├── #agent-messages-{id}   ← INDEPENDENT SCROLL
            │     │     └── .agent-input-container
            │     ├── [Column-2]   ...
            │     └── [Column-N]   up to 26 columns (NATO Alpha–Zulu)
            └── [AI PRIME PANEL]   right-side panel
                  ├── .ai-chat-title
                  ├── #ai-chat-messages    ← INDEPENDENT SCROLL
                  └── .ai-chat-input-container
```

**Key shell difference:** Claude.ai and ChatGPT are single-column conversation surfaces. This platform is a **multi-threaded parallel workspace** — each column is a fully independent conversation + input + scroll unit.

| Property | Claude.ai | ChatGPT | This Platform |
|---|---|---|---|
| Container count | 1 | 1 | **1–26 simultaneous** |
| Layout model | Single centered ~768px column | Single centered ~768px column | **Horizontal flex row** |
| Scroll scope | Global single scroll | Global single scroll | **Per-column independent scroll** |
| Resize | Sidebar drag only | None | **Per-column right-edge drag** |
| Pop-out | None | None | **Float any column as overlay window** |
| Collapse | Panel-level hide | Panel-level hide | **Per-column to 60px bar** |

---

### 2. Message Bubble Philosophy

**Claude.ai:**
- User message → right-aligned pill bubble (`rounded-2xl`, `bg-bg-300 #F4F4F4`, `max-w-[85%]`)
- AI response → full-width flat prose, NO bubble background, `prose` class
- Avatar: small Claude logo inline with name at message top — not in its own column

**ChatGPT:**
- User message → right-aligned pill bubble (`rounded-3xl`, 24px radius, `max-w-[70%]`)
- AI response → full-width flat prose, NO bubble background
- Avatar: **fixed circular avatar column** always left of every AI message (model-specific icon)

**This Platform:**
- **Both user AND AI use the same `.ai-message` base component** — unified, not asymmetric
- Both have: avatar icon + toggle button + action buttons in `.ai-message-header`
- Both are card-style with implicit background from parent container
- Avatar colour is **type-specific** — semantic colour coding per bubble type:

| Bubble type | Avatar icon | Avatar colour |
|---|---|---|
| user | `fa-user` | default `var(--bg-tertiary)` |
| text (AI) | `fa-atom` | default |
| thinking | `fa-brain` | `#8b5cf6` purple |
| tool-use | `fa-cog` | `#eab308` amber |
| tool-result (success) | `fa-flag` | `#60A5FA` blue |
| tool-result (error) | `fa-flag` | `#ef4444` red |
| server-tool (web search) | `fa-search` | `#4ADE80` green |
| server-tool (webfetch) | `fa-globe` | `#60A5FA` blue |
| interaction-request | `fa-hand-paper` | `#ff9800` orange |
| progress-update | `fa-sync` | `#257bdd` blue |

---

### 3. Full Bubble Type Count

| Platform | Types |
|---|---|
| Claude.ai | ~4: user, AI text, thinking, tool block |
| ChatGPT | ~4: user, AI text, thinking (o-series), tool block |
| **This Platform** | **14 distinct types** |

This platform's 14 types:
1. User message
2. AI text response (streaming)
3. Thinking bubble
4. Tool use bubble (AI calling tool)
5. Tool result bubble (success)
6. Tool result bubble (error)
7. Server tool bubble (web search)
8. Server tool bubble (webfetch)
9. Tool usage summary (legacy)
10. Thinking placeholder (legacy)
11. System / stop message
12. Error recovery bubble (8 sub-variants)
13. Agent interaction request (state-machine: waiting/responded/cancelled/timeout)
14. Progress update bubble

---

### 4. Streaming Architecture

| Aspect | Claude.ai | ChatGPT | This Platform |
|---|---|---|---|
| Protocol | SSE | SSE | SSE |
| Text accumulation | Raw text → one markdown parse at end | Progressive markdown re-parse each chunk | **TwoRuleStreamProcessor** — visualization-aware (Plotly/Mermaid/CAD) |
| Tool rendering | Embedded inside AI message | Embedded inside AI message | **Separate sibling bubble per event** |
| Concurrent streams | No | No | **Yes — per `AbortController` per agent** |
| Stop mechanism | 1 global stop | 1 global stop | **Per-column `#agent-stop-btn-{id}`** |
| Force-render safeguard | None | None | `visibleText < 50% fullResponse` → force markdown fallback |

---

### 5. Input System

| Aspect | Claude.ai | ChatGPT | This Platform |
|---|---|---|---|
| Input element | `contenteditable` div | `<textarea>` | `<textarea>` |
| Input behaviour | Always visible | Always visible | **4-state sliding** (collapsed → hover → focus → expanded) |
| Max height | 400px | 200px | 300px (Prime) / 200px (Agents) |
| Voice | In "more" menu | **Always visible** | Toggle button per column |
| Prompt library | None | None | **Per-agent prompt chips** with orange accent, hover preview, drag |
| File chips | Inline in bubble | Inline in bubble | **Above textarea, separate chip row** |
| Input count | 1 global | 1 global | **1 per column** |
| Keyboard | Enter=send, Shift+Enter=newline | Same | Same |

---

### 6. Thinking Blocks

| Aspect | Claude.ai | ChatGPT | This Platform |
|---|---|---|---|
| Trigger | Manual "Think" toggle / Opus 4 / Sonnet 4.5 | Automatic on o1/o3/o4 | SSE `thinking_block` event |
| Content exposed | **Full chain-of-thought** | **Summary only** | **Full chain-of-thought** |
| Default state | Collapsed | Collapsed | Collapsed |
| Container element | Custom div + button | Native `<details>/<summary>` | Custom div + button |
| Multi-round separator | Not observed | N/A | `\n\n---\n\n` between rounds |
| History path | Same structure (embedded in message) | Same | **Different** — streaming = sibling bubble; history = embedded `.thinking-block` |
| Avatar colour | N/A | N/A | **`#8b5cf6` purple** |

---

### 7. Tool Use Rendering

| Aspect | Claude.ai | ChatGPT | This Platform |
|---|---|---|---|
| Position | Embedded inside AI message | Embedded inside AI message | **Separate sibling bubble** (streaming) |
| Default state | Collapsed | Collapsed | Collapsed |
| Tool result | Next-turn embedded | Next-turn embedded | **Separate `tool-result-bubble`** colour-coded |
| UI command handler | None | None | `ui_command: 'open_workflow'` triggers tab switch |
| Live JSON update | N/A | N/A | `tool_input_complete` event updates bubble by `[data-tool-id]` |

---

### 8. Identity & Avatar System

**Claude.ai:** Small Claude logo inline at top of message. No per-message column.

**ChatGPT:** Fixed circular avatar column, model-specific icon (sparkles=GPT-4o, circle=o3), always visible beside every AI message.

**This Platform:**
- Avatar inside every bubble header — semantic colour per type
- Column-level identity: NATO codename + unique `fa-*` icon per agent slot (26 unique icons)
- Neither Claude nor ChatGPT use colour-coded avatars per message type

---

### 9. View Modes

| Platform | View control |
|---|---|
| Claude.ai | None |
| ChatGPT | None |
| **This Platform** | **5 modes per column:** all-expanded, all-collapsed, ai-expanded, ai-collapsed, ai-user |

Persisted per-agent via `WorkspaceManager`, survives page reload.

---

### 10. History Load vs. Streaming Structural Difference

**Claude.ai / ChatGPT:** One message = one DOM node, always. No difference between streaming and history.

**This Platform:**
```
STREAMING  → thinking-bubble + tool-bubble + tool-result-bubble + text-bubble
             = 4+ separate sibling divs in the container

HISTORY    → 1 single .ai-message.assistant div
             with thinking-block + tool-request-block embedded as children
```

Same conversation — two completely different DOM structures depending on render path.

---

### 11. Error Recovery

| Platform | Error recovery |
|---|---|
| Claude.ai | Error message inline; manual retry |
| ChatGPT | Toast notification + manual retry button |
| **This Platform** | **8 typed automatic recovery variants** — `ErrorRecoveryManager` classifies, injects styled bubble, auto-retries |

---

### 12. Feature Summary

| Feature | Claude.ai | ChatGPT | This Platform |
|---|---|---|---|
| Simultaneous agents | 1 | 1 | **Up to 26** |
| Bubble types | ~4 | ~4 | **14** |
| Visualization engine | Artifacts panel | Canvas | **TwoRuleStreamProcessor** (inline) |
| Agent interaction bubbles | No | No | **Yes — state-machine via WebSocket** |
| Progress tracking bubbles | No | No | **Yes** |
| Per-bubble collapse | No | No | **Yes — every bubble** |
| Error recovery automation | No | No | **Yes — 8 types** |
| Message pop-out window | No | No | **Yes — draggable/resizable** |
| View modes | 0 | 0 | **5 per column** |
| Input per agent | N/A | N/A | **1 per column** |
| Column resize/collapse | N/A | N/A | **Yes** |

**Core design difference:** Claude.ai and ChatGPT are **conversation interfaces** — optimised for reading a dialogue. This platform is an **agent execution workspace** — optimised for monitoring autonomous agents running tool loops, with observability into execution state at each step.

---

---

## PART 2 — UI/UX IMPROVEMENT ANALYSIS

### The Core Problem

An agentic task can produce this DOM sequence in a single agent response:

```
[thinking-bubble]         ← thinking
[tool-bubble]             ← tool call 1
[tool-result-bubble]      ← tool result 1
[tool-bubble]             ← tool call 2
[tool-result-bubble]      ← tool result 2
[tool-bubble]             ← tool call 3
[tool-result-bubble]      ← tool result 3
[text-bubble]             ← AI response text
```

That's **8 bubbles for one logical "AI turn"**. In a multi-step task, you may accumulate 40–60 bubbles quickly. The conversation becomes visually noisy, hard to scan, and the critical output (the text bubble) is buried in the execution detail.

The user observation is accurate: **flat prose (no bubble background) on the AI text response feels natural and fills the container better** — as both Claude.ai and ChatGPT demonstrate. The question is what to do with all the execution detail around it.

---

### Option 1 — "Execution Accordion" — Group All Tool Activity per Turn

**Concept:** Collapse all thinking + all tool calls + all tool results for a single AI turn into one expandable "Execution Summary" card. The AI's text response renders flat below it — no bubble.

```
┌───────────────────────────────────────────────────────┐
│  ⚙ Executed 3 tools · 4.2s   [▼ expand]              │  ← accordion header
│  (collapsed: thinking + tool-use + tool-result hidden) │
└───────────────────────────────────────────────────────┘

AI text response renders flat below, full-width, no bubble background.
Same prose style as Claude.ai / ChatGPT AI responses.
```

Expanded view:
```
▼ Executed 3 tools · 4.2s
  ├── 🧠 Thinking (2.1s)         [toggle]
  ├── ⚙ get_shopify_orders       [toggle] → ✅ 42 orders returned
  ├── ⚙ calculate_quote          [toggle] → ✅ $1,240 quoted
  └── ⚙ send_email               [toggle] → ✅ Sent to client@co.com

AI text renders flat below...
```

**Pros:**
- Dramatically reduces visual noise — 8 bubbles → 2 items
- Critical AI text is always immediately visible, never buried
- Execution detail is all accessible on demand
- Matches the "flat prose" preference for AI text
- Consistent with how Claude.ai/ChatGPT handle tool calls (embedded, not sibling)
- Still full observability when expanded
- Easier to scroll — one logical unit per AI turn

**Cons:**
- **Loses live streaming drama** — during streaming you'd need to transition from sibling bubbles → accordion (complex DOM mutation)
- Tool calls no longer update live in separate visible bubbles — harder to see what's happening right now
- Requires significant refactor of streaming rendering path (currently creates siblings, would need grouping logic)
- Users monitoring execution in real-time lose moment-by-moment visibility
- Streaming-to-history structural difference gets more complex, not less

---

### Option 2 — "Flat AI Text + Inline Tool Chips" — Claude-Style Flat with Minimal Tool Indicators

**Concept:** AI text renders completely flat, full-width (no bubble, no background). Tool calls are rendered as tiny inline status chips **within the text flow**, not as separate bubbles.

```
AI text response fills full width, no card/border, pure prose...

Lorem ipsum result from web search [🔍 web_search] dolor sit amet,
the quote came to $1,240 [⚙ calculate_quote ✓] and was sent to the client
[📧 send_email ✓].

Thinking is accessible via a small collapsed block at the very top:
  🧠 Thought for 3.2s  [▶]
```

Tool chips are inline anchors that expand a small popover with the full JSON/result.

**Pros:**
- Most visually clean possible — absolute minimum noise
- AI text is the hero, tool calls are supporting annotations
- Natural reading flow: context + tool result integrated together
- Matches how a human would naturally describe "I searched X, found Y, then did Z"
- Tiny footprint; no scrolling past large tool blocks
- Beautiful side-by-side or single column look

**Cons:**
- **Chips in text are hard to implement** — streaming text doesn't know where to insert chips until response is complete
- Loses all detail during streaming — user sees nothing about tool execution in real-time
- Tool result JSON is hidden behind a popover — less inspectable for power users/debugging
- Requires Claude to emit tool call inline markers in its text response (coordination problem)
- Error states (red chips) can be easy to miss inline
- Interaction request bubbles (Bubble 11/12) can't be chips — they need full interactive UI

---

### Option 3 — "Execution Rail" — Side Panel for Tools, Clean Main Column for Text

**Concept:** Split each agent column into two sub-panels:
- **Left rail (narrow, ~120px):** Live execution events — thinking dots, tool icons, status icons, timestamps. Scrolls with messages.
- **Right area (wide):** Only user messages (bubbles) + AI text (flat prose). No tool clutter.

```
┌─────────────────────────────────────────────────────┐
│  [Execution Rail]  │  [Conversation]                 │
│  ~120px            │  flex:1                          │
│                    │                                  │
│  🧠 3.2s           │                                  │
│  ⚙ get_orders ✓   │  AI: Here are the results...     │
│  ⚙ calc_quote ✓   │  The quote is $1,240 based on... │
│  📧 send_email ✓   │                                  │
│                    │  You: Can you also add shipping? │
│  🧠 1.1s           │                                  │
│  ⚙ get_rates ✓    │  AI: I've added $45 shipping...  │
└─────────────────────────────────────────────────────┘
```

Click any rail item → expands detail panel overlay.

**Pros:**
- Complete separation of execution detail from conversation content
- Conversation column is clean — exactly like Claude.ai or ChatGPT in appearance
- Rail provides constant visible timeline of what the agent did
- At-a-glance comparison across turns (how many tools, how long)
- Doesn't require DOM restructure of streaming path — rail is separate channel
- Agent columns already manage width — rail just eats ~120px from content width

**Cons:**
- **Reduces effective content width** per column — already narrow at 400px, losing 120px hurts
- More complex layout system — each `.agent-column` now has a sub-layout
- Mobile/narrow breakpoints would need to hide the rail
- Aligns tool calls to their turn but scrolling sync between rail and content is tricky
- Interaction request bubbles (Bubble 11/12) still need to be inline — can't go to rail
- Adds conceptual model complexity — users need to understand "left = execution, right = conversation"

---

### Option 4 — "Ghost Bubbles" — Dim/Shrink Tool Bubbles Over Time

**Concept:** Keep the current architecture but apply progressive visual decay to tool bubbles. Tool/thinking bubbles **fade and shrink** once the AI text response is complete. Old tool bubbles become very compact (~20px height) with just an icon and summary label. Only the most recent turn's tool bubbles are full-size.

```
[HISTORICAL TURN — older, compacted]
  🧠 · ⚙ get_orders · ⚙ calc · 📧 email    ← 20px compact strip
  AI text: Lorem ipsum...

[CURRENT TURN — full size during/after streaming]
  ┌─ 🧠 Thinking ──────────────────────┐ ← full bubble
  │  (collapsed, normal size)           │
  └────────────────────────────────────┘
  ┌─ ⚙ get_shopify_orders ─────────────┐
  │  (collapsed, normal size)           │
  └────────────────────────────────────┘
  AI text renders flat below
```

Hover on compact strip → expands back to full view. CSS transition on height.

**Pros:**
- **Zero refactor of streaming** — no architectural change, just CSS + JS animation
- History is still accessible — hover to restore
- Visual weight shifts naturally to the most recent exchange
- Conversation thread feels "alive" — recent = prominent, old = faded
- Requires only a post-stream hook to apply the compact class on previous turn's tool bubbles
- Most conservative change with high visual impact

**Cons:**
- Compact strip still takes vertical space — doesn't eliminate scroll depth
- Hover to expand adds friction for users who need to inspect historical tool calls
- Compaction animation timing could be jarring during active streaming
- Complex to determine "turn boundaries" in the DOM (needs turn-grouping metadata)
- Interactive request bubbles (waiting state) can't be compacted
- Doesn't solve the problem mid-stream when user is watching 8+ bubbles appear

---

### Option 5 — "Two-Tier Message System" — Conversation + Log Tabs Per Column

**Concept:** Each agent column gets two tabs at the top:
- **Chat tab** (default): Only user bubbles + AI text responses. Clean. Flat. Like Claude.ai.
- **Log tab**: Full execution trace — all thinking/tool/result bubbles in order. Full detail.

```
┌─────────────────────────────────┐
│  Alpha  [Chat▼] [Log]  [...]    │ ← tab switcher in header
├─────────────────────────────────┤
│  (Chat tab active)              │
│                                 │
│  You: Analyse my sales data     │
│                                 │
│  AI: Based on your data...      │  ← flat prose, no bubble bg
│  Your revenue grew 23% in Q1... │
│                                 │
│  You: What about returns?       │
└─────────────────────────────────┘
```

Both views share the same underlying data, just different filters.

**Pros:**
- Cleanest possible Chat view — matches Claude.ai aesthetic exactly
- Power users have full access to execution detail without compromising the main view
- Zero structural change to rendering — just filter which bubbles to show/hide
- Most similar to modern debugging tools (network tab / console tab model)
- Can be implemented with CSS `display:none` on tool/thinking bubbles in Chat mode — extremely low risk
- Natural mental model — "Chat to see the conversation, Log to see the execution"

**Cons:**
- **Context switching** — users miss what's happening in the execution while on Chat tab
- During streaming, Chat tab shows nothing until text bubble starts → feels like the agent is stalled
- Need a live indicator in the Chat tab header: "⚙ Running 3 tools..." to avoid dead silence
- Two views can create confusion — "why doesn't my chat show the tool output I saw in the log?"
- Increases header chrome (adds tab row above messages)
- Doesn't improve the experience of users who WANT to watch the execution live

---

### Option 6 — "Single AI Turn Bubble" — Merge Everything into One Expandable Card

**Concept:** Redefine a full AI turn as one single card. The card has:
- **Header row:** Thinking summary pill + tool count badge + timestamp
- **Content area:** AI text, flat, full width inside the card — but no background distinguishing the card from the container
- **Expansion section (collapsed):** Full execution detail — thinking, all tool calls, all results

```
──────────────────────────────────────────────────────────
🧠 3.2s  ·  ⚙ 3 tools  ·  00:04.2               [▼ expand]

Based on your data, revenue grew 23% in Q1. The top
driver was the Shopify channel, accounting for 67% of
total orders...

[Copy] [👍] [👎] [Retry]
──────────────────────────────────────────────────────────
```

Expanded:
```
▼ Execution detail
  🧠 Thinking: "I need to query both the Shopify orders and..."
  ⚙ get_shopify_orders({ limit: 500, since: "2026-01-01" }) → ✅
  ⚙ aggregate_by_channel({ data: [...] }) → ✅
  ⚙ calculate_growth({ q1: 42000, q4_prev: 34000 }) → ✅
```

**Pros:**
- **Single DOM node per AI turn** — eliminates the 8-sibling problem completely
- Headers give immediate high-level info without opening: "3.2s thinking, 3 tools"
- Text is the focal point; metadata is secondary but persistent
- Matches the streaming→history structural inconsistency problem — BOTH paths produce one node
- Clean visual rhythm: user bubble right, AI card full-width left, alternating
- Execution section can be copy-exported as one unit
- Enables proper turn-level actions: "re-run this turn", "edit this response"

**Cons:**
- **Biggest refactor of all options** — requires streaming to accumulate into a single in-progress card (not sibling bubbles)
- The streaming experience changes fundamentally — user sees one card updating in-place rather than bubbles appearing
- Requires `TurnManager` to group events by turn before rendering
- Mid-stream, the card header needs to update live ("⚙ Running tool 2 of 3...")
- Interactive request bubbles (Bubble 11) can't be folded inside — they need to interrupt the stream
- History load is now consistent (good) but streaming changes are extensive

---

### Option 7 — "Hybrid: Flat Text + Collapsible Execution Summary Block" (Recommended Starting Point)

**Concept:** Make one targeted change only: AI text bubble loses its bubble background (goes flat prose, same as Claude.ai), and all tool/thinking bubbles above it remain but are visually demoted via a shared "execution block" wrapper with a subtle background. The grouping is visual only — no DOM restructure.

```
┌ ·· execution ·············································· ··············┐
│ 🧠 collapsed  |  ⚙ get_orders ✓  |  ⚙ calc_quote ✓  |  📧 email ✓    │ ← inline compact in block
└──────────────────────────────────────────────────────────────────────────┘
                                                                [▼ expand all]

AI text renders below as flat prose, full width, no card/border:
─────────────────────────────────────────────────────────────────
Based on your data, revenue grew 23% in Q1. The Shopify channel
accounted for 67% of total orders...

[Copy] [👍] [👎] [Retry]
─────────────────────────────────────────────────────────────────
```

During streaming: execution block grows as bubbles are added. Text renders flat below as it arrives.
After stream: execution block auto-collapses to compact pill strip.

**Pros:**
- **Minimal DOM change** — just wrap execution bubbles in a shared container div
- Preserves full live streaming visibility (bubbles still appear in real-time)
- AI text is immediately the visual focal point — flat, wide, prominent
- Execution block is clearly "this supported the response below"
- Auto-collapse after stream solves scroll depth
- No change to `UnifiedMessageRenderer`, no turn grouping needed
- Visual improvement is immediate and large

**Cons:**
- Needs a way to know "which bubbles belong to this AI turn" — turn boundary detection
- Execution block wrapper must appear/disappear correctly during streaming
- Compact pill strip still has interaction request bubbles to handle specially
- The structural streaming-vs-history inconsistency is not resolved
- Requires CSS + JS hooks on `complete` SSE event to apply auto-collapse

---

### Comparison Summary

| Option | Visual Impact | Implementation Effort | Streaming Change | Resolves Structural Inconsistency |
|---|---|---|---|---|
| 1 — Execution Accordion | ⭐⭐⭐⭐⭐ | 🔴 High | Yes — major | Partial |
| 2 — Inline Tool Chips | ⭐⭐⭐⭐⭐ | 🔴 High | Yes — fundamental | No |
| 3 — Execution Rail | ⭐⭐⭐⭐ | 🔴 High | Partial | No |
| 4 — Ghost Bubbles | ⭐⭐⭐ | 🟢 Low | No | No |
| 5 — Two-Tier Tabs | ⭐⭐⭐⭐ | 🟡 Medium | No | No |
| 6 — Single Turn Bubble | ⭐⭐⭐⭐⭐ | 🔴 Very High | Yes — complete rebuild | **Yes** |
| 7 — Hybrid Flat+Wrapper | ⭐⭐⭐⭐ | 🟡 Medium | Minimal | No |

---

### Recommended Phased Approach

**Phase 1 (Quick Win — 1–2 days):**
- Remove bubble background from `.ai-message.assistant.text-bubble` → flat prose
- Add `prose` typography class for line-height, paragraph spacing
- This alone matches the Claude.ai/ChatGPT text feel immediately

**Phase 2 (Ghost Bubbles — 2–3 days):**
- On `complete` SSE event, wrap previous tool/thinking bubbles in `.execution-block` container
- Auto-collapse the block to a compact pill strip after 2s delay
- Hover to restore full detail

**Phase 3 (Execution Accordion — 1–2 weeks):**
- Implement turn grouping in streaming path
- Single expandable "Execution summary" card per AI turn
- Full history/stream consistency

This gives maximum value with minimum risk at each step — Phase 1 can ship independently, Phase 2 builds on it, Phase 3 is a full architectural improvement for when capacity allows.

---

### Additional Targeted Quick Wins (Independent of above)

| Change | Effort | Impact |
|---|---|---|
| Thinking bubble: auto-shrink to one-liner after stream completes | Low | Medium — thinking is rarely read after fact |
| Tool result bubble: hide JSON by default, show only status icon + tool name | Low | High — tool result JSON is technical noise for most users |
| Add turn separator line between user→AI exchanges | Low | Medium — improves scanability |
| User bubble: increase max-width from 85% to full-width on narrow columns | Low | Medium — 400px column with 85% looks cramped |
| Processing indicator: replace bouncing dots with a live tool-call counter ("Running tool 2 of 3...") | Medium | High — users know what's happening |
| Interaction request bubble: full-width treatment, distinct background to stand out | Low | High — these require user action and must not be missed |
