# Technical Changes — Anthropic Extended Thinking & Model Handling
**Date: 23 April 2026**
**Author: Gerardo (gerardo@vetsuccessacademy.com)**
**Branch: v11 → deployed via `git push gerardo v11:v11`**

---

## Overview

This document covers all changes made across two sessions (April 2026) to correctly support Anthropic Claude's Extended Thinking feature at every layer of the stack — API call construction, conversation history management, and the settings UI. It also includes the fix for a duplicate-assistant-message bug that predated these changes but was addressed concurrently.

The work spans:
- `AI_infrastructure/routes/agent_routes_v4.py` — model detection / history cleaning
- `AI_infrastructure/core/combined_agent_worker.py` — thinking param construction + temperature enforcement
- `UI/business-ai-platform-v2.html` — settings UI temperature lock, model info banners
- `AI_infrastructure/migrations/043_cleanup_duplicate_assistant_messages.sql` — DB cleanup

---

## Background: Anthropic API Constraints Discovered

Research against Anthropic's documentation surfaced three model-specific hard constraints that were not handled:

| Constraint | Affected Models | Error if violated |
|---|---|---|
| Temperature MUST be `1.0` when thinking is enabled | All models with thinking support | `400 Bad Request` |
| `thinking.type` MUST be `"adaptive"` (NOT `"enabled"`) | `claude-opus-4-7` and newer | `400 Bad Request` |
| Any non-default `temperature` / `top_p` breaks the API | `claude-opus-4-7` | `400 Bad Request` |
| Thinking blocks MUST be passed back in multi-turn history | `claude-sonnet-4-5+`, `claude-opus-4-6+`, `claude-opus-4-7` | Corrupted reasoning / 400 |

A secondary issue found during the same investigation: `claude-sonnet-4-5-20250929` (the active model for user Gerardo, user ID 12) was not in the `THINKING_PRESERVING_MODELS` set, so the code was stripping thinking blocks from history unnecessarily when this model was active — wasting tokens on re-reasoning Claude had already done.

---

## Change 1 — `agent_routes_v4.py`: THINKING_PRESERVING_MODELS Set

**File:** `AI_infrastructure/routes/agent_routes_v4.py`  
**Line:** ~2147

### Problem
The set `THINKING_PRESERVING_MODELS` controls whether thinking blocks are stripped from conversation history before sending to the API. Models in this set **keep** thinking blocks (passing them back allows Claude to refer to earlier reasoning without re-doing it). Models **not** in this set get their thinking blocks stripped.

`claude-sonnet-4-5` and `claude-opus-4-7` were missing from the set. The active user model `claude-sonnet-4-5-20250929` is identified by its date-stripped base name (`claude-sonnet-4-5`), so it was falling into the "strip thinking" path on every request even though the model preserves them correctly.

### Fix

```python
THINKING_PRESERVING_MODELS = {
    'claude-sonnet-4-6', 'claude-opus-4-6',
    'claude-opus-4-5', 'claude-opus-4-1',
    'claude-opus-4', 'claude-sonnet-4',
    'claude-sonnet-4-5',  # ← ADDED: Sonnet 4.5 preserves thinking blocks by default
    'claude-opus-4-7',   # ← ADDED: Opus 4.7 preserves thinking blocks (adaptive only)
}
```

The helper `_model_preserves_thinking()` strips trailing `-YYYYMMDD` date suffixes before checking the set, so versioned IDs like `claude-sonnet-4-5-20250929` correctly match `claude-sonnet-4-5`:

```python
def _model_preserves_thinking(model_id: str) -> bool:
    import re
    base = re.sub(r'-\d{8}$', '', model_id)
    return base in THINKING_PRESERVING_MODELS
```

### Why It Aligns
- Anthropic's documentation confirms Sonnet 4.5+ preserves thinking blocks across turns
- The active production model for user ID 12 is `claude-sonnet-4-5-20250929` — previously it was being incorrectly stripped; now history is sent intact
- The console log from 9 April 2026 confirms `claude-sonnet-4-5-20250929` reached the stream endpoint (line: `[STREAM] ⚠️  Model switch detected: 'claude-sonnet-4-5-20250929' does not preserve thinking blocks`) — this warning will no longer fire after this fix

---

## Change 2 — `combined_agent_worker.py`: ADAPTIVE_THINKING_MODELS + Temperature Clamp

**File:** `AI_infrastructure/core/combined_agent_worker.py`  
**Lines:** ~2957–2995

### Problem A — Wrong `thinking.type` for Opus 4.7
When a model is in `ADAPTIVE_THINKING_MODELS`, the worker constructs `{'type': 'adaptive'}` as the thinking parameter. Previously `claude-opus-4-7` was missing from this set, so it received `{'type': 'enabled', 'budget_tokens': N}` — which Anthropic returns a `400` for on Opus 4.7.

### Fix A

```python
ADAPTIVE_THINKING_MODELS = {
    'claude-sonnet-4-6', 'claude-opus-4-6',
    'claude-opus-4-7',  # ← ADDED: Opus 4.7 ONLY supports adaptive thinking
}
SUPPORTS_THINKING_MODELS = {
    'claude-sonnet-4-6', 'claude-opus-4-6',
    'claude-opus-4-5', 'claude-sonnet-4-5',
    'claude-haiku-4-5', 'claude-opus-4-1',
    'claude-opus-4', 'claude-sonnet-4',
    'claude-3-7-sonnet',
    'claude-opus-4-7',  # ← ADDED: Opus 4.7 supports adaptive thinking
}
```

The thinking param is constructed conditionally:

```python
if ai_thinking_enabled and model_supports_thinking:
    if _base in ADAPTIVE_THINKING_MODELS:
        thinking_param = {'type': 'adaptive'}   # No budget_tokens — Opus 4.7 path
    else:
        thinking_param = {'type': 'enabled', 'budget_tokens': ai_thinking_budget}
```

### Problem B — Non-Default Temperature on Opus 4.7
Anthropic's Opus 4.7 API rejects **any** non-default sampling parameter. If a user has saved `temperature: 0.7` in their profile and selects Opus 4.7, the request would fail with a 400.

### Fix B — Silent Clamp Guard

```python
MODELS_NO_CUSTOM_SAMPLING = {'claude-opus-4-7'}
if ai_provider == 'anthropic' and _base in MODELS_NO_CUSTOM_SAMPLING and final_temperature != 1.0:
    print(f"{log_prefix} ⚙️  Temperature clamped to 1.0 (model '{ai_model}' does not accept non-default sampling params)")
    final_temperature = 1.0
```

This is a silent server-side clamp — it does not error or surface to the user; it just forces the correct value before the API call. The print statement goes to the Flask log for observability.

### Also Existing: Thinking-Enabled Temperature Override
This logic was already present and is preserved unchanged — when **any** model has thinking enabled, temperature is locked to 1.0:

```python
final_temperature = 1.0 if thinking_param else ai_temperature
if thinking_param and ai_temperature != 1.0:
    print(f"{log_prefix} ⚙️  Temperature overridden: {ai_temperature} → 1.0 (required when thinking enabled)")
```

### Why These Align
- Both fixes prevent `400 Bad Request` errors that would silently fail AI responses
- The clamp guard is additive (not destructive) — it only fires for the specific model that requires it
- Users are not blocked; the fallback is transparent and logged

---

## Change 3 — `business-ai-platform-v2.html`: UI Temperature Lock on Thinking Toggle

**File:** `UI/business-ai-platform-v2.html`

### Sub-change 3a — New `onThinkingToggle()` Function (line ~32509)

**Problem:** The "Enable Extended Thinking" checkbox called `saveSettings()` directly on change. There was no UI enforcement that temperature must be 1.0 when thinking is on. A user could enable thinking with temperature 0.5, save that preference, and the backend would either silently override it (for non-Opus-4.7 models) or the Opus 4.7 guard would catch it — but the UI gave no indication.

**Fix:** New function that locks the temperature slider to 1.0 whenever the checkbox is checked, and unlocks it when unchecked:

```javascript
function onThinkingToggle() {
    const thinkingOn = document.getElementById('enableThinking')?.checked;
    const tempSlider = document.getElementById('temperature');
    const tempValue  = document.getElementById('tempValue');
    const lockedNote = document.getElementById('tempLockedNote');

    if (thinkingOn && tempSlider) {
        tempSlider.value    = '1.0';
        tempSlider.disabled = true;
        if (tempValue) tempValue.textContent = '1.0';
        if (lockedNote) lockedNote.style.display = 'block';
        console.log('[AI Settings] Extended Thinking enabled — temperature locked to 1.0 (API requirement)');
    } else if (tempSlider) {
        tempSlider.disabled = false;
        if (lockedNote) lockedNote.style.display = 'none';
        console.log('[AI Settings] Extended Thinking disabled — temperature slider unlocked');
    }
    saveSettings();
}
```

### Sub-change 3b — `#tempLockedNote` Element (line ~21834)

A hidden `<small>` element added directly below the temperature slider. Shown/hidden by `onThinkingToggle()`:

```html
<small id="tempLockedNote" style="color: var(--accent-primary); margin-top: 2px; display: none;">
    <i class="fas fa-lock"></i> Locked to 1.0 — required by Extended Thinking
</small>
```

Uses `var(--accent-primary)` so it matches the theme accent colour (blue). Uses the `fa-lock` FontAwesome icon to visually communicate the lock state.

### Sub-change 3c — Checkbox `onchange` Wire-up (line ~21849)

```html
<!-- Before -->
<input type="checkbox" id="enableThinking" checked onchange="saveSettings()">

<!-- After -->
<input type="checkbox" id="enableThinking" checked onchange="onThinkingToggle()">
```

### Sub-change 3d — `loadSectionData()` ID Mismatch Bug Fix (lines ~32840–32900)

**Pre-existing bug found during investigation:** `loadSectionData()` is called when the Account Sidebar settings panel opens, to restore the user's saved preferences into the UI form fields. It was querying element IDs with an `ai_` prefix (`#ai_temperature`, `#ai_top_p`, `#ai_thinking_enabled`, `#ai_max_tokens`, `#ai_thinking_budget`) — **none of which exist in the DOM**. The actual element IDs are `#temperature`, `#topP`, `#enableThinking`, `#maxTokens`, `#thinkingBudgetSlider`. Every preference was silently failing to restore on every page load.

**Fix** — updated the querySelector calls to include both variants, and also update the display spans:

**Model Options section (temperature, topP):**
```javascript
// Temperature — actual ID is #temperature, not #ai_temperature
const tempInput = section.querySelector('#temperature, #ai_temperature, input[name="ai_temperature"]');
if (tempInput) {
    tempInput.value = prefs.ai_temperature;
    const display = document.getElementById('tempValue');
    if (display) display.textContent = prefs.ai_temperature;
}

// Top P — actual ID is #topP, not #ai_top_p
const topPInput = section.querySelector('#topP, #ai_top_p, input[name="ai_top_p"]');
if (topPInput) {
    topPInput.value = prefs.ai_top_p;
    const display = document.getElementById('toppValue');
    if (display) display.textContent = prefs.ai_top_p;
}
```

**Token Parameters section (maxTokens, thinkingBudget, enableThinking):**
```javascript
// Max tokens — actual ID is #maxTokens, not #ai_max_tokens
const maxTokensInput = section.querySelector('#maxTokens, #ai_max_tokens, input[name="ai_max_tokens"]');
if (maxTokensInput) {
    maxTokensInput.value = prefs.ai_max_tokens;
    const display = document.getElementById('tokensValue');
    if (display) display.textContent = prefs.ai_max_tokens;
}

// Thinking budget — actual ID is #thinkingBudgetSlider, not #ai_thinking_budget
const thinkingBudgetInput = section.querySelector('#thinkingBudgetSlider, #ai_thinking_budget, input[name="ai_thinking_budget"]');
if (thinkingBudgetInput) {
    thinkingBudgetInput.value = prefs.ai_thinking_budget;
    const display = document.getElementById('thinkingValue');
    if (display) display.textContent = prefs.ai_thinking_budget;
}

// Thinking checkbox — actual ID is #enableThinking, not #ai_thinking_enabled
const thinkingCheckbox = section.querySelector('#enableThinking, #ai_thinking_enabled, input[name="ai_thinking_enabled"]');
if (thinkingCheckbox) {
    thinkingCheckbox.checked = Boolean(prefs.ai_thinking_enabled);
    // Enforce temperature lock state after restoring the checkbox value
    if (typeof onThinkingToggle === 'function') onThinkingToggle();
}
```

The final line — calling `onThinkingToggle()` after restoring the thinking checkbox — is critical: it ensures that if a user had thinking enabled and saved, when they re-open the settings panel the temperature slider is already locked and the note is already visible.

### Why These Align
- The UI now mirrors the backend constraint: temperature is visually locked when thinking is on, matching the `final_temperature = 1.0 if thinking_param` logic in `combined_agent_worker.py`
- The `loadSectionData()` fix means user preferences actually restore on every settings panel open — this was a silent regression that was present for all users
- The temperature lock state on settings restore means saved preferences are visually accurate, not misleading

---

## Change 4 — Migration 043: DB Cleanup of Duplicate Assistant Messages

**File:** `AI_infrastructure/migrations/043_cleanup_duplicate_assistant_messages.sql`  
**Status: Created. ⚠️ NOT YET EXECUTED.**

### Root Cause
The `/api/agent/<id>/start` endpoint previously both:
1. Spawned a `run_simple_agent_worker` background thread (which called Anthropic and saved to DB)
2. Returned a session token — and then the frontend connected to `/api/agent/stream/<id>`, which also called `execute_streaming_request` (another Anthropic call + DB save)

Both paths ran concurrently and both wrote the AI response to `sessions.messages`. This produced **consecutive pairs of assistant messages** for every request. For thinking-enabled models, each response had a unique `thinking.signature`, so the hash-based deduplication did not catch them.

### Fix Applied (Previous Session)
Step 6 of the `/start` endpoint handler in `agent_routes_v4.py` no longer launches the worker thread. The AI call happens exclusively in `execute_streaming_request` (the stream endpoint). All that `/start` does now is update the agent status and return the session token.

### The Migration SQL

```sql
DO $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    WITH ordered AS (
        SELECT
            m.id, m.thread_id, m.role, m.content, m.created_at,
            LAG(m.role)    OVER (PARTITION BY m.thread_id ORDER BY m.created_at, m.id) AS prev_role,
            LAG(m.id)      OVER (PARTITION BY m.thread_id ORDER BY m.created_at, m.id) AS prev_id,
            LAG(m.content) OVER (PARTITION BY m.thread_id ORDER BY m.created_at, m.id) AS prev_content
        FROM sessions.messages m
    ),
    consecutive_pairs AS (
        SELECT id AS second_id, prev_id AS first_id,
               content AS second_content, prev_content AS first_content
        FROM ordered
        WHERE role = 'assistant' AND prev_role = 'assistant'
    ),
    to_delete AS (
        SELECT
            CASE
                WHEN (
                    second_content::text LIKE '%"tool_use"%'
                    AND first_content::text NOT LIKE '%"tool_use"%'
                ) THEN first_id
                ELSE second_id
            END AS delete_id
        FROM consecutive_pairs
    )
    DELETE FROM sessions.messages
    WHERE id IN (SELECT delete_id FROM to_delete);

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RAISE NOTICE 'Deleted % duplicate assistant message(s).', deleted_count;
END $$;
```

**Strategy:**
- Keep the FIRST assistant message in each consecutive duplicate pair
- Exception: if only the second message has `tool_use` blocks and the first does not, keep the second (it contains tool results that are needed for context)
- Idempotent — safe to run multiple times

### Evidence in Console Log (9 April 2026)
The duplicate messages are visible in the console log attached to this session. The backend log shows:

```
[DB LOAD] Found 19 messages in database
[DB LOAD]   [1] assistant: ['thinking(sig)', 'text']
[DB LOAD]   [2] assistant: ['thinking(sig)', 'text']   ← duplicate of [1]
...
[DB LOAD]   [4] assistant: ['thinking(sig)', 'text']
[DB LOAD]   [5] assistant: ['thinking(sig)', 'thinking(sig)', 'text', 'text']  ← duplicate of [4]
```

And the validation step in `combined_agent_worker.py` detects and merges them before sending to the API:

```
[Combined Worker] ⚠️ Duplicate assistant message at index 2
[Combined Worker] 🔧 Merging 1 blocks into previous message
```

This merge is a **runtime workaround** — the migration is needed to fix the data at rest.

---

## Change 5 — `business-ai-platform-v2.html`: Model Behaviour Info Banners

**File:** `UI/business-ai-platform-v2.html`  
**Commit:** `d961559c` — pushed 23 April 2026

### Problem
Three API constraints were completely invisible to users in the settings UI:

1. **Opus 4.7** — temperature is always forced to 1.0 even if thinking is OFF, but nothing in the UI communicated this. A user picking Opus 4.7 and setting temperature to 0.7 would have their setting silently overridden on every request.
2. **OpenAI / DeepSeek models** — the Extended Thinking checkbox appears enabled and does nothing. No feedback that the setting is irrelevant for non-Anthropic models.
3. **Requirements only visible after interaction** — the `#tempLockedNote` lock message (from Change 3) only appears after the user manually toggles the thinking checkbox. On initial settings panel open, even if thinking was already enabled in saved prefs, there was no model-level context shown.

### Fix A — `#modelBehaviourNote` Dynamic Banner

A new `<div id="modelBehaviourNote">` element inserted between the model selector and the temperature slider. It is hidden by default and updated by `onModelChange()` each time the model dropdown changes or settings are restored.

```html
<div id="modelBehaviourNote" style="display:none; margin-bottom: var(--space-2); padding: var(--space-2); font-size: 13px; border-left: 3px solid var(--accent-primary); border-radius: 4px; background: var(--bg-tertiary);"></div>
```

Banner states by model:

| Model group | Border colour | Icon | Message |
|---|---|---|---|
| Supported Anthropic (Sonnet 4.5/4.6, Opus 4.x, etc.) | Blue (`--accent-primary`) | `fa-brain` | *Supports Extended Thinking. When enabled, temperature is automatically locked to 1.0.* |
| Claude Opus 4.7 | Amber (`--accent-warning`) | `fa-exclamation-triangle` | *Opus 4.7: Uses adaptive thinking only. Temperature and Top P are always fixed at 1.0 and cannot be customised for this model.* |
| OpenAI / DeepSeek (gpt-\*, o1, o3, deepseek-\*) | Grey (`--border-default`) | `fa-info-circle` | *Extended Thinking is not available for this model — the setting will be ignored.* |
| Legacy / unrecognised | Hidden | — | — |

### Fix B — `onModelChange()` Function

Replaces the previous `onchange="saveSettings()"` on the model select. Strips the trailing date suffix, classifies the model, and sets banner content:

```javascript
function onModelChange() {
    const model = (document.getElementById('modelSelect')?.value || '').trim();
    const note  = document.getElementById('modelBehaviourNote');
    const base  = model.replace(/-\d{8}$/, '');

    const ADAPTIVE_ONLY    = ['claude-opus-4-7'];
    const THINKING_MODELS  = [
        'claude-sonnet-4-6', 'claude-opus-4-6',
        'claude-opus-4-5',   'claude-sonnet-4-5',
        'claude-haiku-4-5',  'claude-opus-4-1',
        'claude-opus-4',     'claude-sonnet-4',
        'claude-3-7-sonnet', 'claude-opus-4-7'
    ];
    const isNonAnthropic = /^(gpt-|o1|o3|deepseek-)/.test(model);

    if (ADAPTIVE_ONLY.includes(base)) {
        // Amber warning for Opus 4.7
        note.style.borderLeftColor = 'var(--accent-warning, #f59e0b)';
        note.style.background      = 'rgba(245,158,11,0.08)';
        note.innerHTML = '<i class="fas fa-exclamation-triangle" ...></i>'
            + '<strong>Opus 4.7:</strong> Uses adaptive thinking only. Temperature and Top P are always fixed at 1.0...';
        note.style.display = 'block';
    } else if (isNonAnthropic) {
        // Grey neutral for OpenAI / DeepSeek
        note.style.borderLeftColor = 'var(--border-default, #4a5568)';
        note.style.background      = 'var(--bg-tertiary)';
        note.innerHTML = '<i class="fas fa-info-circle" ...></i>'
            + 'Extended Thinking is not available for this model — the setting will be ignored.';
        note.style.display = 'block';
    } else if (THINKING_MODELS.includes(base)) {
        // Blue info for supported Anthropic
        note.style.borderLeftColor = 'var(--accent-primary)';
        note.style.background      = 'var(--bg-tertiary)';
        note.innerHTML = '<i class="fas fa-brain" ...></i>'
            + 'Supports Extended Thinking. When enabled, temperature is automatically locked to 1.0.';
        note.style.display = 'block';
    } else {
        note.style.display = 'none';
    }

    saveSettings();
}
```

### Fix C — Static `settings-info` Box at Bottom of Model Options

A permanent blue-bordered info box appended after the Extended Thinking checkbox, matching the same `settings-info` pattern used in the Token Parameters and Appearance sections:

```html
<div class="settings-info"
    style="margin-top: var(--space-3); padding: var(--space-2); background: var(--bg-tertiary); border-left: 3px solid var(--accent-primary); border-radius: 4px; font-size: 13px;">
    <i class="fas fa-info-circle"></i> <strong>API Defaults:</strong> Temperature is automatically
    set to 1.0 when Extended Thinking is enabled. For Claude Opus 4.7, temperature is always 1.0
    regardless of this setting.
</div>
```

This box is always visible (not toggled), ensuring the constraint is stated even before the user interacts with either control.

### Fix D — `loadSectionData()` Model-Restore Hook

When the settings panel opens and restores a saved `ai_model` preference, `onModelChange()` is now called immediately so the correct banner is shown without requiring any user interaction:

```javascript
// Inside loadSectionData() → model options branch
if (prefs.ai_model) {
    const modelSelect = section.querySelector('#modelSelect, ...');
    if (modelSelect) modelSelect.value = prefs.ai_model;
    // Refresh model-behaviour info note to match restored selection
    if (typeof onModelChange === 'function') onModelChange();
}
```

### Why These Align
- The dynamic banner mirrors exactly the three model sets checked server-side (`ADAPTIVE_ONLY` ↔ `MODELS_NO_CUSTOM_SAMPLING`, `THINKING_MODELS` ↔ `SUPPORTS_THINKING_MODELS`, non-Anthropic ↔ provider check in `combined_agent_worker.py`)
- The static info box covers the general rule that applies on every request — no user action required to see it
- Together with `#tempLockedNote` (Change 3), the UI now provides three layers of feedback: model-level context, checkbox-triggered lock note, and a permanent rule reminder

---

## How All Changes Align Together

```
User opens AI Settings panel (settings panel restored from saved prefs)
│
└─ loadSectionData() called
    ├─ Restores ai_model → calls onModelChange()
    │   └─ #modelBehaviourNote shows correct banner for saved model            [Change 5]
    ├─ Restores ai_temperature → slider + display span updated                [Change 3d]
    └─ Restores ai_thinking_enabled → calls onThinkingToggle()
        ├─ If thinking was on: temp slider locked, #tempLockedNote shown       [Change 3]
        └─ saveSettings() persists state

User selects a different model from the dropdown
│
└─ onModelChange() fires                                                      [Change 5]
    ├─ Strips date suffix from model ID
    ├─ Opus 4.7    → amber banner: "always 1.0, adaptive only"               [Change 5]
    ├─ GPT / DeepSeek → grey banner: "thinking not available"                 [Change 5]
    ├─ Supported Anthropic → blue banner: "thinking OK, temp locks to 1.0"   [Change 5]
    └─ saveSettings()

User toggles "Enable Extended Thinking" checkbox
│
└─ onThinkingToggle() fires                                                   [Change 3]
    ├─ temperature slider locked to 1.0, disabled
    ├─ #tempLockedNote shown: "Locked to 1.0 — required by Extended Thinking"
    └─ saveSettings() persists the preference to localStorage

On next user message → POST /api/agent/<id>/start → GET /api/agent/stream/<id>
│
├─ agent_routes_v4.py
│   ├─ Reads ai_thinking_enabled, ai_temperature, ai_model from user prefs
│   ├─ _model_preserves_thinking(ai_model) checks THINKING_PRESERVING_MODELS  [Change 1]
│   │   ├─ claude-sonnet-4-5-20250929 → strips date suffix → "claude-sonnet-4-5" → TRUE
│   │   └─ Thinking blocks passed through in history (not stripped)
│   └─ Calls execute_streaming_request(... ai_model, ai_temperature, ai_thinking_enabled ...)
│
└─ combined_agent_worker.py
    ├─ _base = "claude-sonnet-4-5" (or "claude-opus-4-7" if user switched)
    ├─ if _base in ADAPTIVE_THINKING_MODELS:                                  [Change 2a]
    │   └─ thinking_param = {'type': 'adaptive'}          ← Opus 4.7 path
    ├─ else:
    │   └─ thinking_param = {'type': 'enabled', 'budget_tokens': N}  ← all others
    ├─ final_temperature = 1.0 if thinking_param else ai_temperature          [Change 2]
    └─ if _base in MODELS_NO_CUSTOM_SAMPLING:                                 [Change 2b]
        └─ final_temperature clamped to 1.0 regardless     ← Opus 4.7 safety net
```

The four layers (model info banner → thinking checkbox lock → history preservation → API param construction) form a complete defence-in-depth stack that prevents any path from sending an invalid request to Anthropic, and ensures users understand exactly why controls behave the way they do.

---

## File Reference Summary

| File | Change # | Change Type | Description |
|---|---|---|---|
| `AI_infrastructure/routes/agent_routes_v4.py` (L2147) | 1 | Modified | Added `claude-sonnet-4-5` and `claude-opus-4-7` to `THINKING_PRESERVING_MODELS` |
| `AI_infrastructure/core/combined_agent_worker.py` (L2957) | 2a | Modified | Added `claude-opus-4-7` to `ADAPTIVE_THINKING_MODELS` and `SUPPORTS_THINKING_MODELS` |
| `AI_infrastructure/core/combined_agent_worker.py` (L2992) | 2b | Modified | Added `MODELS_NO_CUSTOM_SAMPLING` clamp guard for Opus 4.7 |
| `UI/business-ai-platform-v2.html` (L32509) | 3a | Added | `onThinkingToggle()` function — UI temperature lock |
| `UI/business-ai-platform-v2.html` (L21834) | 3b | Added | `#tempLockedNote` hidden element under temperature slider |
| `UI/business-ai-platform-v2.html` (L21849) | 3c | Modified | `#enableThinking` onchange: `saveSettings()` → `onThinkingToggle()` |
| `UI/business-ai-platform-v2.html` (L32840–32900) | 3d | Fixed | `loadSectionData()` ID mismatch bug — preferences now restore correctly on settings open |
| `AI_infrastructure/migrations/043_cleanup_duplicate_assistant_messages.sql` | 4 | Created | Removes historical duplicate consecutive assistant messages from `sessions.messages` |
| `UI/business-ai-platform-v2.html` (~L21793) | 5a | Added | `#modelBehaviourNote` dynamic banner div below model selector |
| `UI/business-ai-platform-v2.html` (~L32509) | 5b | Added | `onModelChange()` function — classifies model, sets banner content, calls `saveSettings()` |
| `UI/business-ai-platform-v2.html` (~L21849) | 5c | Modified | `modelSelect` onchange: `saveSettings()` → `onModelChange()` |
| `UI/business-ai-platform-v2.html` (~L21854) | 5d | Added | Static `settings-info` box after thinking checkbox — permanent API defaults notice |
| `UI/business-ai-platform-v2.html` (~L32843) | 5e | Modified | `loadSectionData()` model-options branch now calls `onModelChange()` after restoring `ai_model` |

---

## Pending Actions

| # | Action | Notes |
|---|---|---|
| 1 | Run migration 043 against Supabase | Execute `043_cleanup_duplicate_assistant_messages.sql` in Supabase SQL editor to clean existing duplicates. The `/start` fix prevents new duplicates; the migration handles historical ones. |
| 2 | Browser test — thinking toggle DOM context | `onThinkingToggle()` uses `document.getElementById()`. Verify the account sidebar renders the AI settings into the same document scope, not an isolated iframe or shadow DOM, so the IDs are found correctly. |
| 3 | Browser test — model banner on initial load | Open AI Settings with a saved `claude-opus-4-7` preference and confirm the amber banner renders immediately (via `loadSectionData()` → `onModelChange()` path) without needing to change the dropdown. |
| 4 | Consider adding Opus 4.7 to model dropdown | The model dropdown in `#modelSelect` does not yet list `claude-opus-4-7`. If it is added, the `onModelChange()` base-name check will correctly classify it using the `ADAPTIVE_ONLY` set. |

---

## Console Log Evidence (9 April 2026)

The attached console log `CONSOLE_LOG_9th_APRIL_1330.md` shows a live production session. Key observations:

- `ai_thinking_enabled: 0` in user prefs → correct, thinking disabled for this request
- `ai_temperature: 1.0` → temperature already reflects a previous save with thinking enabled
- `[STREAM] ⚠️  Model switch detected: 'claude-sonnet-4-5-20250929' does not preserve thinking blocks` → this warning is the bug being fixed; after the `THINKING_PRESERVING_MODELS` change this warning will no longer appear for this model
- Duplicate assistant messages visible in DB load (messages 2, 5, 8, 11) → these are addressed by migration 043
- `[Combined Worker] ⚠️ Duplicate assistant message at index 2` → the runtime merge workaround firing 4 times per request, confirming historical data contamination
