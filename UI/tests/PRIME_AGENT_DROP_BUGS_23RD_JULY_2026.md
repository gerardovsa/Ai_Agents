# Prime / Agent Chat — Findings & Test Report

**Date:** 23rd July 2026
**Author:** Claude Code (M3, MiniMax) via Sonnet session
**Scope:** (1) Prime vs Agent chat code-path comparison; (2) Live drag-and-drop testing results
**Status:** Analysis complete; fixes proposed in §6

---

## 1. Executive Summary

| # | Finding | Severity | Status |
|---|---|---|---|
| 1 | Streaming agent thinking bubble missing `thinking-bubble` class | medium | confirmed (code-evidenced) |
| 2 | Streaming agent tool bubble missing `tool-bubble` class | high | confirmed (code-evidenced) |
| 3 | Streaming agent tool bubble starts un-collapsed | high | confirmed (code-evidenced) |
| 4 | No streaming text caret in either Prime or agent | low | confirmed |
| 5 | No TwoRule `forceFlush` before tool bubble on agent path | medium | confirmed |
| 6 | No `\n\n---\n\n` round separator on agent thinking path | low | confirmed |
| 7 | **No human-typing indicator on agent columns** (Prime has it) | low | confirmed |
| 8 | **Swap only loads the *target* of the drop, not the *source*** — `displaced_thread` is assigned in DB but never loaded into chat | **critical** | **NEW — confirmed via code path** |
| 9 | After empty-state render following swap, agent column dimensions are too wide and gain a horizontal scrollbar | medium | **NEW — reported by user** |
| 10 | Prime's empty state has no drop-target visualisation after the recent dropdown removal | medium | **NEW — reported by user** |

Items 1–7 come from static code analysis (no runtime test required). Items 8–10 come from live user testing in the deployed environment.

---

## 2. Section A — Static comparison: Prime vs Agent streaming

### 2.1 What is shared

```
            ┌────────────────────────────┐
            │   UnifiedMessageRenderer   │   ← shared
            │   createMessageHeader      │     (header, copy,
            │   openMessageFullscreen    │      expand, fullscreen)
            └─────────────┬──────────────┘
                          │
            ┌─────────────┴──────────────┐
            │                            │
   Prime streaming path     Agent streaming path
   (prime_ai_chat.js)       (agent-js.js)
   ─ className w/ helpers    ─ className w/o helpers  ❌
   ─ TwoRule flushing        ─ no TwoRule             ❌
   ─ round separator         ─ no separator           ❌
   ─ start collapsed         ─ start UN-collapsed     ❌
   ─ has typing indicator    ─ no typing indicator    ❌
```

### 2.2 Divergences — code-level evidence

| Aspect | Prime | Agent streaming | File:line |
|---|---|---|---|
| Thinking bubble class | `ai-message assistant thinking-bubble` | `ai-message assistant` (no `thinking-bubble`) | [prime_ai_chat.js:967-968](../modules_internal/agents/prime_ai_chat.js) vs [agent-js.js:5129](../modules_internal/agents/agent-js.js) |
| Thinking collapse-on-create | yes | added **after** appendChild | [agent-js.js:5210](../modules_internal/agents/agent-js.js) |
| Tool bubble class | `ai-message assistant tool-bubble` | `ai-message tool` (no `tool-bubble`) | [prime_ai_chat.js:1134-1135](../modules_internal/agents/prime_ai_chat.js) vs [agent-js.js:5279](../modules_internal/agents/agent-js.js) |
| Tool starts collapsed | yes | **no** | [prime_ai_chat.js:1135](../modules_internal/agents/prime_ai_chat.js) vs [agent-js.js:5279+](../modules_internal/agents/agent-js.js) |
| `\n\n---\n\n` round separator on new thinking block | yes (on `delta_type === 'start'`) | absent | [prime_ai_chat.js:1063-1076](../modules_internal/agents/prime_ai_chat.js) |
| TwoRule `forceFlush` before tool bubble | yes (flushes all registered processors) | absent | [prime_ai_chat.js:1106-1117](../modules_internal/agents/prime_ai_chat.js) |
| Human-typing indicator | `#prime-typing-indicator` | absent | [business-ai-platform-v2.html:21223](../../business-ai-platform-v2.html) |
| Dead `<div class="typing-indicator">` template | none | at [agent-js.js:1607-1609](../modules_internal/agents/agent-js.js), never instantiated |

### 2.3 Author's own comment is wrong

[agent-js.js:5129](../modules_internal/agents/agent-js.js):

```js
thinkingBubble.className = 'ai-message assistant';  // ✅ Same as Prime (no extra classes)
```

[prime_ai_chat.js:967-968](../modules_internal/agents/prime_ai_chat.js) shows Prime *does* have extra classes (`thinking-bubble`). The "✅ Same as Prime" claim is false. Same pattern at [agent-js.js:5279](../modules_internal/agents/agent-js.js) for the tool bubble. **This is strong evidence the divergence is unintentional.**

### 2.4 View-mode detection is broken for streaming agent reasoning

`AgentColumn.applyViewModeToMessage` ([agent-column.js:2020-2076](../modules_internal/agents/agent-column.js)) uses `message.classList.contains('thinking-bubble')` to decide whether to collapse/expand under the 5-mode view-mode state machine. Because the streaming path at [agent-js.js:5129](../modules_internal/agents/agent-js.js) omits this class, **view-mode toggles silently fail on streaming-reasoning blocks in agent columns**. The structured-load path at [agent-js.js:6225](../modules_internal/agents/agent-js.js) does add the class — only the streaming path is broken.

---

## 3. Section B — Live testing findings (new)

### 3.1 Test 1 — Drag Prime chat onto occupied AI agent

**Steps:**
1. Prime loaded with thread A.
2. Agent-2 loaded with thread B.
3. Dragged thread A from Prime onto agent-2's column.
4. Confirmation modal appeared. Pressed **Swap**.

**Expected:**
- agent-2 shows thread A loaded (messages visible, thread-info card showing A).
- Prime shows thread B loaded (messages visible, thread-info card showing B).

**Actual:**
- agent-2 shows thread A loaded ✓
- agent-2's thread-info card shows A ✓
- Prime's thread catalogue badge shows B (correct DB state).
- Prime's `thread-info-prime` area is **empty** (no card).
- Prime's chat panel does **not** load thread B's messages.

### 3.2 Test 2 — Swap two AI agent columns

**Steps:**
1. Agent-1 loaded with thread X.
2. Agent-2 loaded with thread Y.
3. Dragged X onto agent-2 (occupied) → pressed **Swap**.

**Expected:** Both agents loaded with each other's thread.

**Actual:** agent-2 loaded with X ✓. agent-1's column does **not** show Y; its `thread-info-1` element is empty or stale.

### 3.3 Test 3 — "Move to Thread Catalogue" from the same modal

**Steps:** Same drop as Test 1, but pressed **Move to thread catalogue** instead of swap.

**Actual:** Works correctly. The displaced thread is unassigned in the catalogue, the source thread is loaded into the target column.

### 3.4 Test 4 — Empty agent column dimensions

**Steps:** After an unload (e.g. via Test 3's "Move to catalogue" path), agent-2's column shows the empty state.

**Expected:** Standard empty state width, no horizontal scroll.

**Actual:** The empty column is wider than its siblings and a **horizontal scrollbar appears** in the empty state. The empty state's contents (the clickable "No thread loaded" pill with chevron) appear to overflow the column's flex/grid bounds.

### 3.5 Test 5 — Prime empty state after drag-out

**Steps:** Drag a thread out of Prime (onto a free agent column, no modal). Prime is now empty.

**Expected:** A persistent visual indicator that Prime is a drop target (e.g. dashed border, "Drop a thread here" text).

**Actual:** The `thread-info-prime` element is bare — an empty `<div class="thread-info-wrapper"></div>`. There is no text, no icon, no border. The user has no visual cue that this is a drop zone. (The `drag-over` highlight does appear during an active drag, but only then.)

---

## 4. Section C — Root-cause analysis (with file:line)

### 4.1 Bug 8 — Swap only works one direction (CRITICAL)

**Affected files:**
- [UI/modules_internal/thread-manager/thread-manager-interactions.js](../modules_internal/thread-manager/thread-manager-interactions.js) — the `handleDrop` flow
- [UI/modules_internal/thread-manager/thread-manager-assignment.js](../modules_internal/thread-manager/thread-manager-assignment.js) — `assignThread` and `_cascadeThreadAssignment`

**Sequence (Test 1 — Prime → Agent-2, both occupied):**

1. User drops Prime's thread on agent-2.
2. `handleDrop(event, 'agent-2')` runs ([thread-manager-interactions.js:621+](../modules_internal/thread-manager/thread-manager-interactions.js)).
3. Target is occupied → `showAssignmentConfirmation` resolves with `{ action: 'swap' }`.
4. The `agent-N flow` branch ([thread-manager-interactions.js:743-746](../modules_internal/thread-manager/thread-manager-interactions.js)) executes:
   ```js
   const swap = choice.action === 'swap';
   await this.assignThread(threadId, targetLocation, { swap });
   ```
5. `assignThread` POSTs to `/api/thread-assignments/assign` with `swap: true`. The backend returns `displaced_thread` (Agent-2's thread) and `displaced_new_location` (the source's previous location = `'prime'`).
6. `_cascadeThreadAssignment(threadId='A', location='agent-2', assignment)` runs ([thread-manager-assignment.js:246+](../modules_internal/thread-manager/thread-manager-assignment.js)):
   - **STEP 1** — updates the in-memory `thread.location` for thread A → `'agent-2'` ✓
   - **STEP 3** — handles the displaced thread (thread B). Updates `displacedThread.location = 'prime'` and calls `await this._clearLocationUI('agent-2', 'B')` to clear Agent-2's UI ✓
   - **STEP 4** — re-renders `thread-info-2` with thread A's data ✓ (so the badge is correct)
   - **STEP 5** — calls `renderThreadList()` and `refreshAllThreadInfoCards('A')` ✓
   - **No step calls `loadThreadInPrime('B')`.** The `displaced_thread` is in the DB at `location = 'prime'`, but the chat panel never loads its messages.
7. Back in `handleDrop`, the post-swap branch runs ([thread-manager-interactions.js:758-777](../modules_internal/thread-manager/thread-manager-interactions.js)):
   ```js
   // Refreshed from backend, find thread A
   const refreshedThread = this.threads.find(t => t.id === threadId);
   // Load thread A into the target agent (agent-2)
   if (MultiAgent.loadThreadIntoAgent) {
       await MultiAgent.loadThreadIntoAgent(agentId, refreshedThread);
   }
   ```
   This loads the **target** (agent-2 with thread A) — but again, **the displaced thread (B) at Prime is never loaded**.

**The gap:** `_cascadeThreadAssignment` updates DB state and re-renders the thread-info card for the *new* location of the source thread, but does not load the *displaced* thread into *its* new location. The chat-load functions (`loadThreadInPrime`, `loadThreadIntoAgent`) are only called in the `handleDrop` post-assignment block — and that block only loads the source thread at the target, never the displaced thread at the source.

**Same root cause explains Test 2** (Agent↔Agent swap): the post-assignment block calls `loadThreadIntoAgent(targetAgentId, sourceThread)` but not `loadThreadIntoAgent(sourceAgentId, displacedThread)`.

### 4.2 Bug 9 — Wider dimensions / horizontal scroll on empty state

**Affected CSS / files:**
- [UI/modules_internal/thread-manager/thread-info-renderer.js](../modules_internal/thread-manager/thread-info-renderer.js) — `renderThreadInfoContainer`
- CSS for `.thread-info-wrapper` and `.no-thread-message` (inline in [business-ai-platform-v2.html](../../business-ai-platform-v2.html))

**Hypothesis:** After `_clearLocationUI('agent-2', displacedThreadId)` ([thread-manager-assignment.js:391+](../modules_internal/thread-manager/thread-manager-assignment.js)), the agent column is re-rendered with the empty state:

```js
headerEl.innerHTML = this.renderThreadInfoContainer(location, null, true);
```

That returns the clickable `.no-thread-message` div with a chevron icon. Likely the `display: flex` row + the absolute-positioned chevron / fixed `min-width` on the pill is overflowing the column's flex container. The fix likely needs to be CSS-side (`min-width: 0` on the flex child, or a `width: 100%` on the wrapper).

I have **not yet verified the exact CSS rule** — this requires a DevTools inspection of the rendered empty column to identify the offending width rule. A `git grep` over `min-width` / `width:` in the thread-info CSS region is the next step.

### 4.3 Bug 10 — Prime's empty state lacks drop-target visualisation

**Affected file:**
- [UI/modules_internal/thread-manager/thread-info-renderer.js:39-44](../modules_internal/thread-manager/thread-info-renderer.js)

The recent fix (Jul 23, 2026) changed the Prime empty state from a clickable dropdown trigger to:

```html
<div class="thread-info-wrapper"></div>
```

This is *too* minimal — it has no text, no border, and no visual hint. The `drag-over` class added by `handleDragOver` ([thread-manager-interactions.js:600-607](../modules_internal/thread-manager/thread-manager-interactions.js)) only appears while a drag is active.

**Comparison with agent empty state:** agent columns still have the clickable pill:
```html
<div class="no-thread-message clickable"
     onclick="AgentColumn.showThreadSelector(${agentId})">
    <i class="fas fa-comment-slash"></i>
    <span>No thread loaded</span>
    <i class="fas fa-chevron-down"></i>
</div>
```

This is the visual cue the user expects. The Prime fix removed it without adding a replacement.

---

## 5. Section D — Concrete reproduction matrix

| Repro | Result | Caused by |
|---|---|---|
| Drag Prime (loaded) onto Agent (loaded) → Swap | Target loads, source empty | Bug 8 (cascade skips source load) |
| Drag Agent-1 (loaded) onto Agent-2 (loaded) → Swap | Target loads, source empty | Bug 8 (same code path) |
| Drag Prime (loaded) onto Agent (loaded) → Move to catalogue | Works | Different code path (no displaced thread to load) |
| Drag any thread onto empty Agent | Works | Source = unassigned, no displaced thread |
| Drop a thread on Prime (no Prime thread) | Works | Unoccupied path; `loadThreadInPrime` is called at line 795 |

---

## 6. Section E — Recommended fixes (in priority order)

### 6.1 Fix Bug 8 (critical — broken swap)

**Option A — minimal patch (recommended for fast deploy):**
Extend `_cascadeThreadAssignment` to call the appropriate `loadThread*` function for the displaced thread at its `displaced_new_location`. Roughly:

```js
// in _cascadeThreadAssignment, after STEP 3 (displaced thread handled):
if (assignment.displaced_thread && assignment.displaced_new_location) {
    const dest = assignment.displaced_new_location;
    const dispId = assignment.displaced_thread;
    if (dest === 'prime' || dest === 'unassigned') {
        // prime-occupancy check
        if (typeof this.loadThreadInPrime === 'function') {
            await this.loadThreadInPrime(dispId);
        }
    } else if (dest.startsWith('agent-') && typeof MultiAgent !== 'undefined' && MultiAgent.loadThreadIntoAgent) {
        const destAgent = parseInt(dest.replace('agent-', ''));
        const dispThread = this.threads.find(t => t.id === dispId);
        if (dispThread) await MultiAgent.loadThreadIntoAgent(destAgent, dispThread);
    }
}
```

This is ~15 lines. It does *not* require a backend change — the backend already tells us where the displaced thread went.

**Option B — cleaner long-term:**
Have `handleDrop` call the load functions for *both* threads (target with source, source with displaced) after `assignThread` resolves, mirroring the symmetry the user expects. Requires touching the swap branches at lines 720-725 and 743-746.

### 6.2 Fix Bug 10 (medium — Prime empty state UX)

Restore *some* persistent visual indicator for Prime's empty state. Options:
- **Reintroduce a non-clickable drop-zone hint** in the empty wrapper: a dashed border + "Drop a thread here" text, plus a click-to-select link as secondary action.
- **Reuse the agent pattern** but make it non-clickable: same chevron pill but without the `onclick` handler. The user can still drop a thread on the wrapper.
- **Add a CSS pseudo-element** (`.thread-info-wrapper:empty::before { content: 'Drop a thread here'; }`) — minimal change, no new JS.

### 6.3 Fix Bug 9 (medium — empty column width)

Requires DevTools inspection of the rendered empty column to identify the offending CSS rule. The fix is almost certainly CSS-only (e.g. add `min-width: 0` to the flex child of the column). The empty state itself is rendering correctly; the *container* is the suspect.

### 6.4 Fixes for items 1–7 (chat rendering divergences)

Already covered in detail in the analysis. Summary:
- Add `thinking-bubble` and `tool-bubble` to the streaming agent className strings at [agent-js.js:5129, 5279](../modules_internal/agents/agent-js.js).
- Set `collapsed` on className at construction (not after appendChild).
- Add the `\n\n---\n\n` separator at `delta_type === 'start'`.
- Add TwoRule `forceFlush` before tool bubble.
- Add a human-typing indicator on agent columns (or remove the orphan template at [agent-js.js:1607-1609](../modules_internal/agents/agent-js.js)).

---

## 7. Section F — Risks and assumptions

**Assumptions:**
- Bug 8 root cause is in `_cascadeThreadAssignment` based on the visible code at [thread-manager-assignment.js:246-385](../modules_internal/thread-manager/thread-manager-assignment.js). I have **not** yet confirmed by triggering a swap in the live app and reading the resulting state — only by code-reading.
- Bug 9 root cause is CSS-driven based on the symptoms ("wider dimensions", "horizontal scroll"). I have not yet identified the exact CSS rule — DevTools inspection required.
- The "Prime doesn't return to normal empty state" symptom is the visual emptiness of the bare `<div class="thread-info-wrapper"></div>`, not a separate bug.

**Risks if the recommended fixes are applied:**
- Fix 6.1 (cascade load): If the backend's `displaced_new_location` is ever `'unassigned'` (i.e. swap collapsed because the source had no real previous location), we should NOT load the thread into Prime. The `dest === 'prime' || dest === 'unassigned'` branch must be restricted to actual prime loading — using `dest === 'prime'` only is safer. The `unassigned` case should skip the load (the displaced thread is just back in the catalogue).
- Fix 6.2 (Prime empty state): If reintroducing a clickable dropdown, we will need to delete `showPrimeThreadSelector`/`hidePrimeThreadSelector` reversal. The prior removal (Jul 23, 2026) was deliberate; restoration should be deliberate too.

**Not verified in this analysis:**
- Backend's exact response shape for `displaced_thread` / `displaced_new_location` on a swap between two agents. The code path at [thread-manager-interactions.js:725](../modules_internal/thread-manager/thread-manager-interactions.js) is similar to the agent-N path at line 746 but takes a different code branch — I have not traced it.
- Whether the "Prime → Agent swap" target's `loadThreadIntoAgent` is the right function, or if there's a `loadThreadIntoAgentForAgent` vs `loadThreadIntoAgentForPrime` distinction.

---

## 8. Files of interest

| Path | Why |
|---|---|
| [UI/modules_internal/thread-manager/thread-manager-interactions.js](../modules_internal/thread-manager/thread-manager-interactions.js) | Drop handler, swap modal, post-assignment load |
| [UI/modules_internal/thread-manager/thread-manager-assignment.js](../modules_internal/thread-manager/thread-manager-assignment.js) | `assignThread` + `_cascadeThreadAssignment` — the actual swap cascade |
| [UI/modules_internal/thread-manager/thread-info-renderer.js](../modules_internal/thread-manager/thread-info-renderer.js) | Empty-state HTML (Bug 10) |
| [UI/modules_internal/agents/agent-column.js](../modules_internal/agents/agent-column.js) | Agent column DOM, `loadThreadIntoAgent`, `unloadThread` |
| [UI/modules_internal/agents/agent-js.js](../modules_internal/agents/agent-js.js) | Streaming agent bubble builders (items 1–7) |
| [UI/modules_internal/agents/prime_ai_chat.js](../modules_internal/agents/prime_ai_chat.js) | Streaming Prime bubble builders (reference for divergence) |
| [UI/shared/utilities/message_renderer.js](../../shared/utilities/message_renderer.js) | `UnifiedMessageRenderer.render`, `createMessageHeader` (shared) |
| [UI/business-ai-platform-v2.html](../../business-ai-platform-v2.html) | CSS for drop zones, view modes, processing indicator, typing indicator |

---

## 9. Definition of "done" for these findings

- [ ] All four swap-via-Prime (Test 1), swap-via-agents (Test 2), Prime empty state (Test 5), and agent empty state width (Test 4) scenarios are passing in the deployed environment.
- [ ] Items 1, 2, 3 in the divergences table (className fixes) are deployed.
- [ ] A regression test or manual reproduction checklist for swap flows is added to `tests/` (or a `RUN_THIS.md` next to this doc).
- [ ] This doc is linked from the next PR's description.

---

## 10. Change history

| Date | Author | Change |
|---|---|---|
| 2026-07-23 | Claude (M3 via Sonnet session) | Initial findings — static analysis + live testing report |
