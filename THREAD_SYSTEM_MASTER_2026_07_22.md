# Thread System Master Document

> **Status:** LIVING DOCUMENT. This is the canonical source of truth for the thread system as of **2026-07-22**.
> It supersedes `THREAD_SYSTEM.md` (Jan 18 2026) and `THREAD_DRAG_DROP_FIX_NOV21.md` (Nov 21 2025),
> both of which are now **archived reference material** with significant errors listed in §11.
>
> **Last verified against:**
> - Source: `c:\Users\gpoli\GIT\AI_Agents_V11\AI_agents` (branch `v11`)
> - DB: `sessions.threads` queried directly against Supabase on 2026-07-22
> - Git: head `1b94a677` and earlier
>
> **How to keep this doc alive:** when you change a thread route, schema column,
> or drag-drop handler, update the relevant section in the same PR. Add a dated
> note at the bottom under "Change log". Do not silently let it drift.
>
> **Audience:** new contributors debugging thread drag-and-drop, AI agents, or
> anyone onboarding to the multi-agent chat system.

---

## 1. What this doc covers

1. The four UI surfaces that render "thread info cards"
2. The drag-and-drop system, including what works today and what is broken
3. The real database schema (`sessions.threads`)
4. The real backend endpoints (`/api/threads/*` — plural, not `/api/thread/*`)
5. The real frontend module layout (`UI/modules_internal/thread-manager/`)
6. Migration history that shaped the schema
7. Known bugs and open work
8. A "doc-stale" list pointing at every line in the old docs that contradicts the code

---

## 2. Glossary

| Term | Meaning in this doc |
|---|---|
| **Thread** | One persistent conversation between a user and an AI. A row in `sessions.threads`. |
| **Prime** | The single-thread chat panel on the right side of the screen. The user's primary assistant. |
| **Agent** | One of 26 named slots (Alpha-1 ... Zulu-26). Each is a column with its own chat history. |
| **Card / Thread info card** | The compact HTML element rendered by `ThreadCardTemplates.compactCard()`. It shows the thread title, agent badge, message count, timestamps, badges, tags, and action buttons. |
| **Catalogue / Thread History** | The list of every thread the user owns, shown in the Threads side menu. NOT a workspace, NOT a destination — it is a *listing*. |
| **Location** | A string field on `sessions.threads.location`: `unassigned`, `prime`, `agent-1`...`agent-26`, or `synergy`. |
| **thread_slug** | The public id used in the API and on the wire. For new threads it is a 7-8 digit integer (the SERIAL `id`); for legacy threads it is a 13-digit timestamp slug. See §6 for the lookup logic. |
| **displaced_thread** | The thread that was previously occupying a location when a new thread is dropped on it. The CASCADE pattern (§7.4) returns the displaced thread to `unassigned`. |

---

## 3. The four surfaces that render thread info cards

All four call **the same `ThreadCardTemplates.compactCard()` template**. They differ only in
which location value they pass and which container they inject the HTML into.

| # | Surface | Container element | Location passed | currentLocation passed | Draggable? | Acts as drop zone? |
|---|---|---|---|---|---|---|
| 1 | **Prime chat header** | `#thread-info-prime` | `prime` | `prime` | yes (full card) | yes (via `setupPrimeDropZone`) |
| 2 | **Agent-N column** | `#thread-info-<N>` | `agent-N` | `agent-N` | yes | yes (via `setupAgentDropZones`) |
| 3 | **Synergy Kanban card** | rendered by `thread-manager-synergy.js` (no shared template) | `synergy` | (not set) | unknown — Synergy has its own drag system | **no** |
| 4 | **Threads Catalogue (sidebar)** | `#thread-history-list` or per-renderer container | `thread-history` | thread's actual DB location (`prime`, `agent-3`, etc.) | yes | **no** |

> **Critical insight:** the catalogue is the only place where the *rendered* location
> (`thread-history`) and the *actual* thread location (e.g. `agent-3`) differ.
> See §7.6 for the bug this causes during drag.

---

## 4. The drag-and-drop system today

### 4.1 The drag (origin)

`UI/modules_internal/thread-manager/thread-manager-interactions.js:545-584` (`handleDragStart`):

1. `event.target.closest('[data-thread-id]')` walks up to find the card root.
2. Reads `threadElement.dataset.threadId` (i.e. `data-thread-id`).
3. Validates: must be present, length <= 20, must be digits (after stripping `_`/`-`).
4. Sets custom MIME types on the drag:
   - `application/x-thread-id` = the thread id
   - `application/x-source-location` = where the drag *appeared* to start
5. Adds a `.dragging` CSS class for visual feedback.

The Nov 21 2025 fix (in `THREAD_DRAG_DROP_FIX_NOV21.md`) is intact and correct:
the switch from `event.currentTarget` to `event.target.closest('[data-thread-id]')`
plus the length/non-digit validation has prevented the HTML-text-in-drag bug for
~8 months.

### 4.2 The drop (target)

Three listeners are attached after DOM creation:

| Listener | Attached by | Target element | Effect |
|---|---|---|---|
| `setupPrimeDropZone` | `thread-manager-interactions.js:868` | `#ai-chat-panel` | Loads thread into Prime (`loadThreadInPrime`) |
| `setupAgentDropZones` | `thread-manager-interactions.js:808` | every `.agent-column` | Calls `assignThread(threadId, 'agent-N')` then re-loads |
| (multi-agent container) | same file, line 853 | `#multi-agent-container` | Just prevents default; lets bubbles reach child agent columns |

**What is NOT a drop zone today:**
- `#thread-history-list` and the catalogue sidebar (you cannot drop a thread back into the catalogue by dropping on it — only the Unload button on the card works)
- Synergy Kanban cards (Synergy has its own internal drag system)
- Unassigned "trash bin" (no such zone exists)

### 4.3 The handler (`handleDrop`, `thread-manager-interactions.js:621-761`)

1. Reads the custom MIME types.
2. Re-validates the id (defense in depth).
3. Asks `ThreadCardRegistry` to handle the drop first — this is how workflow-slug,
   automation-slug, and document drops get routed to their module's handler.
4. If `sourceLocation === targetLocation` and target is not `unassigned`/`prime`,
   skips (no-op).
5. If target is `unassigned` or `prime`: calls `loadThreadInPrime` directly,
   bypassing the assign API. This means **dropping onto Prime does not call the
   `/api/thread-assignments/assign` endpoint at all** — it relies on
   `loadThreadInPrime` to update local state only.
6. If target is `agent-N`: calls `assignThread(threadId, 'agent-N')` which hits
   `/api/thread-assignments/assign`, then `loadThreadsFromBackend()` to pull fresh
   state, then `MultiAgent.loadThreadIntoAgent` to render.

### 4.4 Multi-MIME handling

`UI/modules_internal/thread-cards/thread-card-registry.js` is a singleton that
allows other modules to register drop handlers keyed by MIME type. Today nothing
in the active module set registers a drag-and-drop handler (verified by reading
the file: the registry initialises from `moduleLoader`, which is in archive
mode — see `waitForModuleLoader` at line 142). So **the registry is currently
a no-op**, but the code path is still there for future modules.

---

## 5. Database reality (`sessions.threads`)

Queried 2026-07-22 against the production Supabase project. **39 columns** total.
Schema is **`sessions`**, not `ai_infrastructure` (this contradicts both `THREAD_SYSTEM.md`
and `CLAUDE.md`, which say `ai_infrastructure`).

| Column | Type | Nullable | Notes |
|---|---|---|---|
| `id` | integer (SERIAL) | NOT NULL | Internal DB id |
| `thread_slug` | text | NOT NULL | Public id on the wire. **For new threads = the integer `id` as a string. For legacy = a 13-digit timestamp slug.** Lookup clause picks between the two — see §6. |
| `workspace_id` | integer | YES | Currently always `1` per code |
| `user_id` | integer | YES | Owner |
| `name` | text | NOT NULL | Display title |
| `created_at` | timestamp | YES | (no timezone in current column type) |
| `updated_at` | timestamp | YES | |
| `metadata` | text | YES | Stored as JSON-encoded text, NOT jsonb |
| `location` | text | YES | `unassigned` / `prime` / `agent-1`..`agent-26` / `synergy` |
| `tags` | text | YES | JSON-encoded array of strings |
| `synergy_card_id` | text | YES | FK -> synergy_sessions |
| `synergy_card_name` | text | YES | Denormalised |
| `parent_thread_id` | integer | YES | Used by fork |
| `branch_name` | text | YES | Fork branch name |
| `branch_point_message_id` | text | YES | Fork point |
| `archived` | integer | YES, default `0` | 0/1 boolean |
| `token_count` | integer | YES, default `0` | Cumulative token usage |
| `locked_to_device_id` | text | YES, default `'NULL'` | Device lock |
| `locked_at` | timestamp | YES | |
| `lock_mode` | text | YES, default `'unlocked'` | `unlocked` / `locked` |
| `workflow_slug` / `workflow_title` / `workflow_id` / `workflow_name` | text | YES | Visual-automation link |
| `internal_doc_slug` / `internal_doc_title` | text | YES | Internal-docs link |
| `automation_slug` / `automation_title` | text | YES | Legacy automation link |
| `title_embedding` / `name_embedding` | USER-DEFINED (vector) | YES | pgvector embeddings (BGE local default) |
| `email_thread_id` / `email_subject` / `email_participants` | text | YES | Communication-hub email link |
| `search_vector` | tsvector | YES | Generated full-text index |
| `team_id` | text | YES | Team login attribution |
| `idempotency_key` | text | YES | De-dup for create |
| `organisation_id` | integer | YES | Multi-tenant org id |
| `visibility` | text | NOT NULL, default `'personal'` | `personal` / `team` / `org` |
| `message_count` | integer | NOT NULL, default `0` | **Added by migration 052** — maintained by trigger |
| `last_message_at` | timestamptz | YES | **Added by migration 052** |

### Other thread-adjacent tables in `sessions`:

- `sessions.thread_assignments` — current location per (user, thread). The
  `/api/thread-assignments/*` endpoint family writes here.
- `sessions.thread_members` / `sessions.thread_users` / `sessions.thread_shares`
  — multi-user membership scaffolding. Schemas exist; not heavily used today.
- `sessions.saved_threads` — bookmark/save.
- `sessions.threads_backup_20251120` — full backup taken 2025-11-20 (before a
  schema change; keep untouched).

### Tables that look like threads but are not the canonical store:

- `ai_infrastructure.saved_threads` and `public.saved_threads` — old copies.
  Do not write to them.

---

## 6. Thread id format and lookup logic

There are **two formats on the wire** and the backend has to handle both:

| Format | Example | When |
|---|---|---|
| Integer id | `"42"`, `"17743277"` | All threads created after the migration to SERIAL `id` |
| Timestamp slug | `"1763646689156"` (13 digits, > 1 trillion) | Legacy threads created before that migration |

The Python lookup clause (`AI_infrastructure/routes/thread_routes.py:73-93`):

```python
def get_thread_lookup_clause(thread_id):
    thread_id_int = int(thread_id)
    if thread_id_int > 1_000_000_000_000:  # > 1 trillion = timestamp
        return ("t.thread_slug = %s", str(thread_id))
    else:
        return ("t.id = %s", thread_id_int)
```

> **`THREAD_SYSTEM.md` is wrong about the slug format.** It claims slugs look like
> `th_<8char>_<timestamp>`. No thread in the current database uses that pattern.
> The actual format is either a raw integer (`id`) or a raw 13-digit timestamp.

---

## 7. Drop, assign, and CASCADE mechanics

### 7.1 The route: `/api/thread-assignments/assign` (POST)

Called by `thread-manager-assignment.js:141-148`. Body:
```json
{ "session_id": "<thread_slug_or_id>", "location": "prime|agent-3|unassigned", "user_id": <int> }
```

What the route does (read of `thread_routes.py` around the assign endpoint —
file is ~600+ lines, exact line range to be re-verified before any route edit):
1. Resolves the thread by lookup clause (§6).
2. Computes `previous_location` for the response (used by the CASCADE UI).
3. If another thread is *already* at the target location, marks it as
   `displaced_thread` in the response.
4. Updates `sessions.threads.location` (and possibly `sessions.thread_assignments`).
5. Returns `{ success, assignment: { session_id, location, user_id, previous_location, displaced_thread } }`.

### 7.2 The CASCADE pattern (`thread-manager-assignment.js:234-356`)

**Database first, UI second.** Order matters.

1. Update the in-memory `thread.location` (single source of UI truth).
2. Show a `NotificationCenter` toast naming the new location.
3. **If `previous_location !== newLocation`**, clear the OLD location's UI
   (Prime panel or the prior agent column) — but only if the in-memory
   `MultiAgent.loadedThreads` says that thread was actually rendered there.
4. **If a displaced thread exists**, set its `location = 'unassigned'` and
   clear the *new* location's UI for it (so the user sees the displaced
   card leave the target column).
5. Render the thread info container in the *new* location.
6. Debounced `renderThreadList()` + `refreshAllThreadInfoCards()`.
7. Every 10th CASCADE, do a full `loadThreadsFromBackend()` to verify.

### 7.3 Deduplication

`AssignmentQueue` (lines 35-71) blocks duplicate POSTs within 1 second for the
same `(threadId, location)` key. Prevents the "same thread assigned 3x in 4 seconds"
problem from late 2025.

### 7.4 Displacement

When you drop thread A onto agent-3 and agent-3 already has thread B:
- A gets `location = 'agent-3'`
- B gets `location = 'unassigned'` and is cleared from the agent-3 column UI
- Both writes happen server-side; CASCADE on the frontend reflects both

### 7.5 Realtime

`initRealtimeSubscription` subscribes to `UPDATE` events on
`sessions.threads` filtered by `user_id`. The `handleThreadLocationChange`
callback mirrors the CASCADE pattern but with a 500 ms debounce so that our
own writes don't re-trigger ourselves in a loop.

### 7.6 The `data-current-location` bug (open issue, see §8)

`handleDragStart` reads `threadElement.dataset.currentLocation` first, falling back
to `dataset.location`. The DOM property `currentLocation` corresponds to the
attribute `data-current-location` (kebab-case to camelCase).

**The `compactCard` template (line 234-243) only emits `data-location`. It accepts
`currentLocation` as its 7th parameter but does not render it onto the element.**

The caller `renderThreadInfoContainer` in `thread-manager-ui.js` does pass the
correct `currentLocation` (e.g. `prime` for a thread that is actually loaded in
Prime, even when the card is rendered in the catalogue with `location='thread-history'`).
The parameter is silently dropped by the template.

**Effect on drag-drop:**
- Dragging a Prime-loaded thread from the catalogue reports
  `sourceLocation = 'thread-history'`, not `prime`.
- The same-location no-op check at `thread-manager-interactions.js:675`
  does NOT short-circuit (because `'thread-history' !== 'agent-3'`).
- For agent drops the CASCADE pattern still works correctly server-side, because
  the backend computes `previous_location` from the DB, not from the drag payload.
- For Prime drops the frontend calls `loadThreadInPrime` directly — also works,
  because `loadThreadInPrime` reads `this.threads` to find the thread regardless.
- So the **drop does not fail** but the source-location check, any future logic
  that branches on `sourceLocation`, and the audit trail are all misleading.

**Fix candidate (not yet implemented):** add one line to the template:

```diff
- <div class="ai-chat-header-info agent-thread-card"
-      data-thread-id="${thread.id}"
-      data-location="${location}">
+ <div class="ai-chat-header-info agent-thread-card"
+      data-thread-id="${thread.id}"
+      data-location="${location}"
+      data-current-location="${currentLocation || location}">
```

Apply the same one-line fix to `fullCard()` (line 314-377) which has the same
omission. Both `compactCard` and `fullCard` should also include
`data-source-location` if you want `handleDragStart` to fall back to it explicitly.

---

## 8. Known bugs and open work (living list)

| # | Status | Title | Section |
|---|---|---|---|
| 1 | DONE | `compactCard` and `fullCard` do not render `data-current-location` even though they accept it | §7.6 |
| 2 | DONE | No drop zone for the Threads Catalogue — users cannot drag a card back "into" the catalogue. New `setupCatalogueDropZone()` is wired; the catalogue now accepts drops (only while `.active`) and unassigns the dragged thread, with a guard against no-op self-drops from the catalogue itself. | §4.2 |
| 3 | OPEN | No drop zone for the Synergy Kanban cards (`thread-manager-synergy.js`) | §4.2 |
| 4 | DONE | No "unassigned" drop zone — the catalogue sidebar now serves this purpose when the user drags an in-flight card to it. (Equivalent behaviour achieved via the catalogue drop zone; no separate empty-zone widget was needed.) | §4.2 |
| 5 | DONE | `loadThreadInPrime` did not call `/api/thread-assignments/assign` — Prime location was set locally only, then re-synced by realtime. The new occupied-target branch in `handleDrop` calls `loadThreadInPrime` AFTER any required `assignThread` for the displaced thread, so the Prime DB row is consistent on drag-drop (not just on click-to-load). | §4.3 |
| 6 | OPEN | `compactCard` accepts 7 args but the `synergyMeta` and `currentLocation` parameters are both optional and frequently undefined at call sites | §3 |
| 7 | DOCUMENT | `THREAD_SYSTEM.md` and `CLAUDE.md` both claim `sessions` is `ai_infrastructure` and slugs use `th_<hex>_<ts>` — they do not | §5, §6, §11 |
| 8 | DOCUMENT | `THREAD_DRAG_DROP_FIX_NOV21.md` says drop zones live in `setupAgentDropZones()` (line 548) and `setupPrimeDropZone()` (line 600) — actual file has them at lines 808 and 868 (the file grew from ~700 to 1986 lines since that doc was written) | §11 |
| 9 | DONE | Agent-column drag-hover highlight flickers when the cursor moves between the column and a child (input, card, button). The old `dragover`+`relatedTarget`-based pattern was brittle. Replaced with the canonical dragenter/dragleave depth-counter pattern so the highlight only flips on the 0↔1 boundary. | §4.2 |
| 10 | DONE | No confirmation when dropping on an occupied Prime / agent column — a drop silently kicked the existing thread to "unassigned" with no user signal. `handleDrop` now opens a 3-button modal (Swap / Unassign-existing-to-catalogue / Cancel) when the source is prime or an agent and the target is occupied, or a 2-button modal (Unassign / Cancel) when the source is the catalogue. The backend honours `swap` by routing the displaced thread to the source's `previous_location` instead of always-unassigned. | §4.2 |
| 11 | DONE | Toast notifications showed raw slug locations (`agent-3`, `prime`, `unassigned`). Added `formatLocationName()` and `getAgentDisplayName()` helpers on `ThreadManager`; every toast now reads `Agent-3 Charlie`, `Prime`, `Catalogue`, etc. | §4.2 |
| 12 | DONE | CASCADE displaced-thread branch in `_cascadeThreadAssignment` ignored `displaced_new_location` and assumed `unassigned`. Now reads the new field from the API response so swap-mode toasts tell the user the displaced thread went to the right slot, not just "Unassigned". | §4.2 |
| 13 | DONE | "Thread History" user-visible string & icon (`fa-history`) used throughout the UI. Renamed to "Thread Catalogue" + `fa-list-ul` to match the catalogue metaphor. Updated: sidebar button title, welcome button, catalogue header, and CSS comment header. Other `fa-history` usages (Recent Activity, Credential Access Log) kept — those mean "log/history", not catalogue. | §12 |

When you fix any of these, mark the status `DONE` and add a one-line note under
"Change log" at the bottom of this file with the date and the commit SHA.

---

## 9. Migration history relevant to threads

In chronological order (reconstructed from `AI_infrastructure/migrations/` and
inline migration comments in routes):

| Migration | What it added (thread-related only) |
|---|---|
| (pre-tracked) | `sessions.threads` and `sessions.messages` created; `sessions.thread_assignments` added |
| `052_*.sql` (June 11 2026) | `message_count INT NOT NULL DEFAULT 0` and `last_message_at TIMESTAMPTZ` on `sessions.threads`, maintained by a trigger on `sessions.messages` |

The actual thread-id lookup-clause logic for the legacy integer-vs-slug
discrimination has no dedicated migration — it was a code change in
`thread_routes.py` when the `id` SERIAL column was introduced.

(No migrations were found for the email_* / workflow_* / automation_* / lock_* /
embedding / search_vector columns — those were likely added in the pre-tracked
era or via Supabase Studio directly. If you need to know exactly when, query
the `pg_attribute` system catalog for `attrelid = 'sessions.threads'::regclass`.)

---

## 10. Frontend module inventory (the moving parts)

All paths relative to `UI/modules_internal/thread-manager/`:

| File | Role | Last meaningful change |
|---|---|---|
| `thread-manager-core.js` | Defines `window.ThreadManager` skeleton | |
| `thread-manager-crud.js` | Create / read / update / delete thread API calls | |
| `thread-manager-ui.js` | `renderThreadList`, `renderThreadInfoContainer` (passes `currentLocation` correctly) | |
| `thread-manager-interactions.js` | **Drag/drop handlers, drop-zone setup** | Nov 21 2025 fix |
| `thread-manager-assignment.js` | **CASCADE assign, realtime, dedup** | Dec 2 2025 dedup |
| `thread-manager-messages.js` | Message send / stream | |
| `thread-manager-sync.js` | Backend sync | |
| `thread-manager-filters.js` | Tag/location filters | |
| `thread-manager-workflows.js` | Workflow linking from catalogue | |
| `thread-manager-synergy.js` | Synergy Kanban integration | |
| `thread-manager-welcome.js` | First-run welcome | |
| `thread-file-preview.js` | File upload preview | |
| `thread-info-renderer.js` | Renders `renderThreadInfoContainer` | |
| `thread-locations.js` | Location string constants (`THREAD_LOCATIONS`) | |
| `../thread-cards/thread-card-templates.js` | `compactCard()`, `fullCard()` | (open bug — §7.6) |
| `../thread-cards/thread-card-registry.js` | Singleton for module-supplied drop handlers | |

The DOM-side `ThreadManager` object lives **inside the giant SPA**
`UI/business-ai-platform-v2.html`. The class spans ~3000 lines split across the
modules above plus inline methods in the HTML. Search the HTML for
`ThreadManager.` to find inline call sites.

---

## 11. Doc-stale: contradictions in the old docs

This section is the "what not to trust" register. Every row is a fact the old
docs got wrong relative to the code today.

### `THREAD_SYSTEM.md` (Jan 18 2026)

| Claim in old doc | Reality on 2026-07-22 |
|---|---|
| Schema: `sessions.threads (id, slug, title, user_id, agent, ai_model, system_prompt, metadata, tags)` | Real columns include 39, with `id`, `thread_slug`, `name`, `location`, **NO** `agent` (replaced by `location`), **NO** `ai_model`, **NO** `system_prompt`, **NO** `metadata` jsonb (it's text-encoded JSON), and **many** more (see §5). |
| Slug format: `th_<8char-hex>_<timestamp>` | Real format is bare integer `id` for new threads, bare 13-digit timestamp for legacy (see §6). |
| Endpoints under `/api/thread/*` | Real: `/api/threads/*` (plural) and `/api/thread-assignments/*` (see §7.1). |
| `session_id === thread_id` pattern is load-bearing | This pattern is **gone** from current code. Threads are addressed by `thread_slug` directly; `session_id` is not used. |
| `session.thread_assignments` is the source of truth for current location | Partially true: rows exist there but the live `/assigned` endpoint reads from `sessions.threads.location` directly (the `WHERE … location IN ('prime', 'agent-1', …)` filter at `thread_routes.py:759`). |
| Single ThreadManager class is in `business-ai-platform-v2.html` lines 5000-8000 | True, but the class is now *extended* by ~15 modules in `UI/modules_internal/thread-manager/` via `Object.assign(window.ThreadManager, {...})`. |
| Tests in `tests/test_threads.py` | That file does not exist (verified by glob). The "manual testing checklist" is the only living test plan. |
| 27 concurrent threads max (Prime + 26 agents) | 27 is correct, but the actual filter in `/assigned` only returns Prime + agent-1..agent-9 (10 max in the default view). The wider 1..26 is only used by the full `/list` endpoint. |
| "slug is generated once on creation, never changes" | True for `thread_slug`; but the column is now mostly a copy of `id` so it IS the id. |
| Hover-expand CSS (`height: 80px → 240px`) | The current implementation uses a `.thread-expand-on-hover` CSS class instead; old CSS does not apply. |

### `THREAD_DRAG_DROP_FIX_NOV21.md` (Nov 21 2025)

| Claim in old doc | Reality |
|---|---|
| Drag handler files at `UI/modules/thread-manager/*` | Real: `UI/modules_internal/thread-manager/*` |
| `handleDragStart` lines 335-368 | Real: lines 545-584 (the file grew from ~700 lines to 1986) |
| `setupAgentDropZones` line 548 | Real: line 808 |
| `setupPrimeDropZone` line 600 | Real: line 868 |
| File names `UI/external/modules/thread-cards/*` for cards | Real: `UI/modules_internal/thread-cards/*` |
| The fix uses `event.dataTransfer.setData('threadId', ...)` | Real: uses `application/x-thread-id` (the doc itself proposes both — the code went with the explicit MIME type, which is the safer choice) |
| The fix is "complete" | The Nov 21 fix is intact and correct for its scope (preventing HTML text in drag payload). It did **not** cover: source-location tracking from the catalogue (§7.6 bug), missing drop zones (§8 items 2-4), or the Prime load bypassing `/assign` (§8 item 5). |

> **TL;DR:** the Nov 21 doc accurately describes the 4 patches it shipped. Everything
> around those patches — file paths, line numbers, surrounding module structure — is stale.

---

## 12. How to verify this doc

If you suspect any fact in this document has drifted, run one of these checks:

```bash
# 1. Column reality
psql "$SUPABASE_DB_URL" -c "\d sessions.threads"

# 2. The compactCard bug
grep -n "data-current-location\|data-location" UI/modules_internal/thread-cards/thread-card-templates.js

# 3. Drop zone inventory
grep -rn "setupAgentDropZones\|setupPrimeDropZone\|setupSynergyDropZone\|setupHistoryDropZone" UI/

# 4. The id-format discriminator
grep -n "thread_id_int > 1_000_000_000_000\|get_thread_lookup_clause" AI_infrastructure/routes/thread_routes.py

# 5. Endpoint reality
grep -rn "@thread_bp.route" AI_infrastructure/routes/thread_routes.py
```

---

## 13. Related documents (canonical, do not duplicate here)

- `.github/ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md` — for the
  4-tier credential resolver (relevant when the AI assistants in agents need to
  call third-party APIs on the user's behalf).
- `.github/VECTOR_DB_DEVELOPER_REFERENCE.md` — for `title_embedding` and
  `name_embedding` columns on `sessions.threads` (these are populated by the
  pgvector pipeline).
- `CLAUDE.md` (repo root) — repo-level conventions, conventions for migrations,
  and the conventions for keeping this doc itself up to date.

---

## 14. Change log

| Date | Author | Change |
|---|---|---|
| 2026-07-22 | Diagnostic session | Initial version. Created from reading code, querying `sessions.threads`, and the two legacy docs. Catalogued 8 open issues. |
| 2026-07-22 | Same session | Bug #1 fixed: `compactCard` now emits `data-current-location` (with safe fallback to `location`) so `handleDragStart` correctly reports the actual thread location. Bug #9 fixed: agent-column drag-hover highlight stabilised with a dragenter/leave depth counter, replacing the brittle `dragover`+`relatedTarget` pattern. |
| 2026-07-22 | Same session | Bugs #2, #4, #5, #10, #11, #12, #13 fixed (drag-and-drop overhaul). New: `setupCatalogueDropZone()` makes the catalogue sidebar a real drop target; `setupPrimeDropZone()` now uses the depth-counter pattern; `handleDrop` opens a 3-button Swap/Unassign/Cancel modal when the drop target is occupied (or 2-button when the source is the catalogue); backend `enforce_thread_assignment_rules` honours a `swap` flag by routing the displaced thread to the source's `previous_location` and returns the new `displaced_new_location` field; both assign endpoints (`/api/thread-assignments/assign` and `/api/agent/threads/<id>/assign`) accept and forward `swap`; `assignThread` and the CASCADE displaced-thread branch read the new field; `formatLocationName` / `getAgentDisplayName` / `formatThreadTitle` helpers make every toast read `Agent-3 Charlie`, `Prime`, `"My Thread…"`; UI text `Thread History` → `Thread Catalogue` and icon `fa-history` → `fa-list-ul` (3 user-visible spots + 1 CSS comment); new hover CSS for `.ai-chat-panel.prime-drag-over` and `.thread-menu-overlay.drag-over`. |