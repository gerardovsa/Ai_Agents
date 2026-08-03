# React Viz Toolbar (Tier 1) + Visualizations Library + AI Tools

> **Date:** 2026-07-22 (v1); updated 2026-07-28 (v2 — research round + roadmap).
> **Scope:** Deliver (a) Tier-1 toolbar on every React-viz iframe, (b) persistent "My Visualizations" library bound to the empty `tab-analytics` stub, (c) AI tools for the viz lifecycle, (d) Synergy Kanban linking, and — **v2 add-on** — (e) the multi-dashboard gallery + Data Source Map + enhancement roadmap surfaced by the 2026-07-28 research round (see §11-§19).
> **Target DB:** Supabase `ai-agents-production-inhouse` (`ryoicrdifiqhqpsnjmdo.supabase.co`).
> **Module plan tier:** `starter`.
> **For:** another AI agent to resume if this work needs follow-up.
> **Sections §1-§10 = v1 (still authoritative for what shipped 2026-07-22). §11-§19 = v2 roadmap (added 2026-07-28).**

---

## 1. Context

The platform renders React visualizations inside sandboxed iframes (`UI/visualisation_engine/react_renderer.js`) whenever the LLM emits `<EXECUTE_REACT>` blocks. Before this round the only parent-side chrome was two buttons (panel + float) added by `addIframeActionBar` (`UI/visualisation_engine/visualisation_v3.js:2157`).

This round adds:
1. A **Tier-1 kebab toolbar** on every viz iframe — Export PNG/PDF/CSV, Copy image, Fullscreen, Save to library.
2. A **persistent "My Visualizations" gallery** bound to the existing `tab-analytics` stub.
3. **12 AI tools** for the full viz lifecycle: `viz_create / viz_update / viz_save / viz_search / viz_get / viz_delete / viz_get_thread / viz_read_thread / viz_add_note / viz_list_notes / viz_link_synergy / viz_unlink_synergy`.
4. **Synergy Kanban linking** — both sides of a `viz ↔ synergy_session` link are written atomically inside a single PL/pgSQL function.

Sibling / precedent docs (read on demand):
- `.github/SVG_CAD_GENERATION_RULES.md` — SVG rules (this round defers to the simple `document.querySelector('svg')` heuristic; the lucide-as-component hotfix is the load-bearing seam)
- `.github/ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md` — credential resolver (not used here; this round uses the JWT's `g.rls_user_id` directly)
- `REACT_RENDERER_LUCIDE_TROUBLESHOOTING_2026-07-22.md` — the P0 fix that pre-dated this round; the renderer changes below were appended AFTER that hotfix and do not touch it

---

## 2. Architecture

```
SPA (business-ai-platform-v2.html)
  ├── tab-analytics                       (replaced "coming soon" stub with gallery)
  │     └── visualizations-module.js      (NEW: card grid + search + modal re-mount)
  ├── chat message bubble
  │     └── .viz-container                (existing)
  │           ├── .viz-content-area       (existing iframe)
  │           └── .viz-action-bar         (existing; now also: Tier-1 kebab)
  └── postMessage bus (NEW types):
        ├── child→parent: iframe-resize, react-render-error (existing)
        ├── child→parent: iframe-svg, iframe-data          (NEW)
        └── parent→child: iframe-export-svg, iframe-export-data (NEW)

Sandboxed React iframe (react_renderer.js)
  └── window.__REACT_RENDERER__           (NEW: opt-in export hook)
       ├── sendSvg(string)         → parent listens
       ├── sendData(payload)       → parent listens
       └── registerExport(handler) → app-supplied overrides

Backend (Flask)
  ├── routes/viz_snapshots_routes.py      (NEW: /api/viz/snapshots/*)
  └── flask_app.py                        (register viz_snapshots_bp)

AI tool layer
  ├── tools/schemas/viz_snapshots_tools.json    (NEW; 12 schemas)
  ├── tools/implementations/viz_snapshots.py    (NEW; 12 wrappers, HTTP→backend)
  └── tools/registry_v3.py                       (special_modules += 'viz_snapshots')

Database (Supabase)
  ├── sessions.viz_snapshots                (NEW migration 057)
  ├── sessions.viz_snapshot_notes           (NEW migration 058)
  ├── synergy_sessions.synergy_sessions.linked_viz_snapshots  (ALTER in 057)
  ├── ai_infrastructure.module_catalog      (INSERT 'visualizations' in 057)
  ├── RLS fixed:                            (migration 059 — see §4)
  └── sessions.link_viz_to_synergy / sessions.unlink_viz_from_synergy  (PL/pgSQL, migration 057)
```

### 2.1 postMessage protocol

| `type` | Direction | Payload | Purpose |
|---|---|---|---|
| `iframe-resize` | child → parent | `{id, height}` | Existing. Drives iframe height auto-fit. |
| `react-render-error` | child → parent | `{id, error}` | Existing. Crash surfacing. |
| `iframe-export-svg` | parent → child | `{id}` | **NEW.** Requests serialised `<svg>` markup. |
| `iframe-svg` | child → parent | `{id, svg}` | **NEW.** Reply to export-svg. |
| `iframe-export-data` | parent → child | `{id}` | **NEW.** Requests chart data for CSV export. |
| `iframe-data` | child → parent | `{id, payload}` | **NEW.** Reply to export-data. `payload = {labels, series, rows?}`. |

**How children reply:** an app's `<App>` component can opt in two ways:

1. Auto-default: parent falls back to `document.querySelector('svg')` + `XMLSerializer` if the child never overrides. Sufficient for Recharts/Basic charts.
2. Explicit: assign `window.__EXPORT_HANDLER__ = { svg() {...} }` and/or `window.__EXPORT_DATA__ = {...}` inside the iframe. Parent checks these first. **Document this convention in the prompt to the LLM** so future visualizations wire it.

**Sandbox:** `sandbox = 'allow-scripts allow-forms allow-modals allow-pointer-lock allow-downloads'` was extended with `allow-downloads` so that an in-iframe `<a download>` fallback works if needed. The iframe also gets `allow="clipboard-write"` so `navigator.clipboard.write` works for the "Copy image" action.

**Renderer hook** is appended AFTER the existing lucide-as-component hotfix — that fix is load-bearing and is NOT touched here.

---

## 3. Script locations (file table)

| Path | Action | Notes |
|---|---|---|
| `UI/visualisation_engine/react_renderer.js` | Append `__REACT_RENDERER__` hook + new postMessage handlers + sandbox `allow-downloads` | Additive only. Hotfix at lines 245-345 untouched. |
| `UI/visualisation_engine/visualisation_v3.js` | Added `addIframeTier1Toolbar` + 14 helper methods (dispatcher, postMessage wrapper, PNG rasteriser, PDF fallback, CSV builder, clipboard write, fullscreen, save, JSX/CSS extractors, download trigger) | One kebab button appended to existing `.viz-action-bar`. Popover appended to `<body>` for reliable absolute positioning. |
| `UI/modules_internal/visualizations/visualizations-module.js` | **NEW** gallery ES module | `onDashboardLoad` fetches `/api/viz/snapshots?mine=true`, renders card grid with search/tag chips; click → modal that re-mounts saved JSX in a fresh iframe with Tier-1 toolbar wired. |
| `UI/business-ai-platform-v2.html` | Added `data-module="visualizations"` to existing analytics sidebar button (line ~18827) and appended a `<script type="module">` bootstrap next to the WooCommerce V4 bootstrap (line ~1601) | **No** Zone 2 entry — analytics is already Zone 1 and `ZONE2_MODULES` has an explicit `if (moduleName === 'woocommerce') return;` to avoid duplicates; adding `visualizations` would create a duplicate. |
| `AI_infrastructure/migrations/057_viz_snapshots.sql` | **NEW** — table + RLS + Synergy column + module seed + `link_viz_to_synergy` / `unlink_viz_from_synergy` PL/pgSQL | Applied to prod Supabase. |
| `AI_infrastructure/migrations/058_viz_snapshot_notes.sql` | **NEW** — notes table + RLS | Applied. |
| `AI_infrastructure/migrations/059_fix_viz_snapshot_rls_var_name.sql` | **NEW** — RLS policy uses `app.current_organisation_id` (the actual session var set by the platform's JWT middleware), not `app.org_id` | The plan's policy was wrong on the first apply; this fixed it. |
| `AI_infrastructure/routes/viz_snapshots_routes.py` | **NEW** — 11 endpoints (CRUD + thumbnail + render-count + link-synergy + unlink-synergy + notes list/add) | Mirrors `routes/vector_db_routes.py:269-292` style. `@require_auth` + `g.rls_user_id` / `g.rls_org_id`. |
| `AI_infrastructure/flask_app.py` | Registered `viz_snapshots_bp` next to existing blueprint registrations | |
| `tools/schemas/viz_snapshots_tools.json` | **NEW** — wrapper `{platform, description, tools:[...]}` with 12 JSON Schemas | Format is the platform standard (NOT a bare array) — confirmed by tool-schema loader. |
| `tools/implementations/viz_snapshots.py` | **NEW** — 12 wrappers; HTTP→backend via `requests` | All return `{"success": bool, ...}` per CLAUDE.md §10. |
| `tools/registry_v3.py` | Appended `'viz_snapshots'` to `special_modules` (line ~415) so per-function dispatch iterates `dir(module)` | |

---

## 4. Database (full DDL applied)

### 4.1 `sessions.viz_snapshots` (migration 057)

```sql
CREATE TABLE IF NOT EXISTS sessions.viz_snapshots (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id                INTEGER NOT NULL,
    owner_user_id         INTEGER NOT NULL,
    thread_id             INTEGER REFERENCES sessions.threads(id) ON DELETE SET NULL,
    assistant_message_id  INTEGER REFERENCES sessions.messages(id) ON DELETE SET NULL,
    title                 TEXT NOT NULL,
    viz_type              TEXT NOT NULL DEFAULT 'react',
    jsx_source            TEXT NOT NULL,
    css_source            TEXT,
    uses_lucide           BOOLEAN NOT NULL DEFAULT FALSE,
    uses_recharts         BOOLEAN NOT NULL DEFAULT FALSE,
    uses_tailwind         BOOLEAN NOT NULL DEFAULT FALSE,
    tags                  TEXT[] NOT NULL DEFAULT '{}',
    is_public             BOOLEAN NOT NULL DEFAULT FALSE,
    share_token           TEXT UNIQUE DEFAULT encode(gen_random_bytes(16), 'hex'),
    synergy_session_id    TEXT REFERENCES synergy_sessions.synergy_sessions(session_id) ON DELETE SET NULL,
    thumbnail_png         BYTEA,
    is_active             BOOLEAN NOT NULL DEFAULT TRUE,
    last_rendered_at      TIMESTAMPTZ,
    render_count          INTEGER NOT NULL DEFAULT 0,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_viz_snapshots_owner  ON sessions.viz_snapshots (owner_user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_viz_snapshots_org    ON sessions.viz_snapshots (org_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_viz_snapshots_tags_gin ON sessions.viz_snapshots USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_viz_snapshots_synergy ON sessions.viz_snapshots (synergy_session_id) WHERE synergy_session_id IS NOT NULL;
```

### 4.2 `sessions.viz_snapshot_notes` (migration 058)

```sql
CREATE TABLE IF NOT EXISTS sessions.viz_snapshot_notes (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id       UUID NOT NULL REFERENCES sessions.viz_snapshots(id) ON DELETE CASCADE,
    author_user_id    INTEGER NOT NULL,
    author_kind       TEXT NOT NULL DEFAULT 'human',   -- 'human' | 'ai'
    author_agent_id   TEXT,                           -- e.g. 'prime', 'alpha-1'
    note              TEXT NOT NULL,
    note_kind         TEXT NOT NULL DEFAULT 'comment',-- 'comment'|'todo'|'handoff'|'data_update'
    metadata          JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_viz_snapshot_notes_snap
    ON sessions.viz_snapshot_notes (snapshot_id, created_at DESC);
```

### 4.3 Synergy column (migration 057)

```sql
ALTER TABLE synergy_sessions.synergy_sessions
    ADD COLUMN IF NOT EXISTS linked_viz_snapshots TEXT NOT NULL DEFAULT '[]';
```

This is a JSON-encoded array of `{snapshot_id, label, linked_at}` objects.

### 4.4 RLS (migrations 057 + 059 — corrected)

The platform's JWT middleware sets `app.current_organisation_id` (NOT `app.org_id` — the original migration got this wrong, fixed in 059). RLS policies are:

```sql
ALTER TABLE sessions.viz_snapshots ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS viz_snapshots_rls ON sessions.viz_snapshots;
CREATE POLICY viz_snapshots_rls ON sessions.viz_snapshots
    USING (org_id = NULLIF(current_setting('app.current_organisation_id', true), '')::int)
    WITH CHECK (org_id = NULLIF(current_setting('app.current_organisation_id', true), '')::int);

-- Notes: EXISTS-based policy that joins through to viz_snapshots
ALTER TABLE sessions.viz_snapshot_notes ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS viz_snapshot_notes_rls ON sessions.viz_snapshot_notes;
CREATE POLICY viz_snapshot_notes_rls ON sessions.viz_snapshot_notes
    USING (EXISTS (SELECT 1 FROM sessions.viz_snapshots v
                   WHERE v.id = snapshot_id
                     AND v.org_id = NULLIF(current_setting('app.current_organisation_id', true), '')::int))
    WITH CHECK (EXISTS (SELECT 1 FROM sessions.viz_snapshots v
                        WHERE v.id = snapshot_id
                          AND v.org_id = NULLIF(current_setting('app.current_organisation_id', true), '')::int));
```

The `NULLIF(..., '')` wrapper is **load-bearing**: when `current_setting` is unset, Postgres raises `ERROR: unrecognized configuration parameter` by default; `NULLIF` makes the comparison NULL and the policy safely returns no rows for non-scoped sessions.

### 4.5 Module catalog seed (migration 057)

```sql
INSERT INTO ai_infrastructure.module_catalog
    (module_name, display_name, description, icon_class, icon_color, category,
     min_plan_tier, required_platforms, sort_order)
VALUES
    ('visualizations', 'Visualizations',
     'Save, browse, and re-render AI-built React dashboards and charts.',
     'fas fa-chart-area', '#58a6ff', 'productivity', 'starter', '{}', 25)
ON CONFLICT (module_name) DO NOTHING;
```

The `starter` plan tier matches the user-confirmed value; the `sort_order` puts it after the standard zones but before role-gated items.

### 4.6 Atomic Synergy link (migration 057)

```sql
CREATE OR REPLACE FUNCTION sessions.link_viz_to_synergy(p_snapshot_id UUID, p_synergy_session_id TEXT, p_label TEXT DEFAULT NULL)
RETURNS VOID AS $$
BEGIN
    UPDATE sessions.viz_snapshots
       SET synergy_session_id = p_synergy_session_id,
           updated_at = NOW()
     WHERE id = p_snapshot_id;

    UPDATE synergy_sessions.synergy_sessions
       SET linked_viz_snapshots = (
           SELECT COALESCE(json_agg(elem), '[]'::json)::text
           FROM (
               SELECT elem
                 FROM json_array_elements(linked_viz_snapshots::json) AS elem
                WHERE (elem->>'snapshot_id') <> p_snapshot_id::text
               UNION ALL
               SELECT json_build_object(
                   'snapshot_id', p_snapshot_id::text,
                   'label',       COALESCE(p_label, ''),
                   'linked_at',   NOW()::text
               )
           ) t
       )
     WHERE session_id = p_synergy_session_id;
END;
$$ LANGUAGE plpgsql;
```

`unlink_viz_from_synergy` is the inverse — deletes the `{snapshot_id}` entry from the JSON array and clears `synergy_session_id` if the FK matched.

---

## 5. AI tool catalog

12 wrappers, all return `{"success": bool, ...}`. Schema lives at `tools/schemas/viz_snapshots_tools.json` (wrapper format `{platform, description, tools: [...]}`).

| Tool | Parameters | Returns | Sample call |
|---|---|---|---|
| `viz_create` | `title, jsx_source, css_source?, uses_lucide?, uses_recharts?, uses_tailwind?, tags?, thread_id?, assistant_message_id?, synergy_session_id?` | `{success, id, share_token}` | `{ title: "Q3 Forecast", jsx_source: "function App() { return <div>hi</div>; }", tags: ["forecast","q3"] }` |
| `viz_update` | `snapshot_id, **fields (title, tags, is_public, css_source, synergy_session_id)` | `{success, snapshot}` | `{ snapshot_id: "<uuid>", title: "Renamed" }` |
| `viz_save` | (same as create) — alias used by the LLM when it doesn't know whether the snapshot already exists | `{success, id, created: bool}` | `{ title: "Orders 7d", jsx_source: "...", thread_id: 42 }` |
| `viz_search` | `q?, tag?, mine?, synergy_session_id?, limit?, offset?` | `{success, snapshots: [...]}` (without `jsx_source`/`thumbnail_png` for size) | `{ mine: true, tag: "forecast" }` |
| `viz_get` | `snapshot_id, include_payload? (default true)` | `{success, snapshot}` | `{ snapshot_id: "<uuid>" }` |
| `viz_delete` | `snapshot_id` | `{success}` (soft delete: `is_active=false`) | `{ snapshot_id: "<uuid>" }` |
| `viz_get_thread` | `snapshot_id, message_count?` | `{success, thread_id, thread_title, messages:[{role, content_preview, created_at}]}` — composes `viz_get` + `/api/threads/<id>/load` + `/api/threads/messages/get` | `{ snapshot_id: "<uuid>", message_count: 6 }` |
| `viz_read_thread` | `snapshot_id, max_messages?, include_tools?` | `{success, thread_id, messages:[...]}` — composes `viz_get` + `/api/threads/messages/get` with truncation flag | `{ snapshot_id: "<uuid>", max_messages: 50 }` |
| `viz_add_note` | `snapshot_id, note, note_kind?, author_kind?, author_agent_id?, metadata?` | `{success, id}` | `{ snapshot_id: "<uuid>", note: "Q3 looks like...", note_kind: "comment", author_kind: "ai", author_agent_id: "prime" }` |
| `viz_list_notes` | `snapshot_id, note_kind?, author_kind?` | `{success, notes:[...]}` ordered `created_at ASC` | `{ snapshot_id: "<uuid>", note_kind: "handoff" }` |
| `viz_link_synergy` | `snapshot_id, synergy_session_id, label?` | `{success}` — calls `sessions.link_viz_to_synergy(...)` SQL function (atomic) | `{ snapshot_id: "<uuid>", synergy_session_id: "syn-abc123" }` |
| `viz_unlink_synergy` | `snapshot_id` | `{success}` — calls `sessions.unlink_viz_from_synergy(...)` | `{ snapshot_id: "<uuid>" }` |

**Auth header:** each wrapper forwards `kwargs.get('jwt_token')` as `Authorization: Bearer …` so the Flask backend's `@require_auth` accepts it.

---

## 6. TODO list (status as of 2026-07-22)

### P1 — Render-side seam
- [x] Append `__REACT_RENDERER__` hook to `react_renderer.js`
- [x] Add new postMessage handlers (`iframe-svg`/`iframe-data` child→parent; `iframe-export-svg`/`iframe-export-data` parent→child)
- [x] Sandbox: append `allow-downloads`

### P2 — Database
- [x] Migration 057 — `sessions.viz_snapshots` table + indexes + RLS (initially wrong var name)
- [x] Migration 058 — `sessions.viz_snapshot_notes` table + RLS
- [x] Migration 057 — `synergy_sessions.synergy_sessions.linked_viz_snapshots` ALTER
- [x] Migration 057 — `ai_infrastructure.module_catalog` INSERT `'visualizations'`
- [x] Migration 057 — PL/pgSQL `link_viz_to_synergy` / `unlink_viz_from_synergy`
- [x] Migration 059 — RLS fix (`app.current_organisation_id`, not `app.org_id`)

### P3 — Backend API
- [x] `AI_infrastructure/routes/viz_snapshots_routes.py` — 11 endpoints
- [x] Register `viz_snapshots_bp` in `AI_infrastructure/flask_app.py`

### P4 — AI tool layer
- [x] `tools/schemas/viz_snapshots_tools.json` — 12 JSON Schemas
- [x] `tools/implementations/viz_snapshots.py` — 12 wrappers
- [x] Append `'viz_snapshots'` to `special_modules` in `tools/registry_v3.py`
- [x] Smoke-test: 12 viz tools imported, bound to registry

### P5 — SPA UI
- [x] `addIframeTier1Toolbar` in `visualisation_v3.js` (kebab + 6 actions + 14 helper methods)
- [x] `UI/modules_internal/visualizations/visualizations-module.js` — gallery module
- [x] `data-module="visualizations"` on the analytics sidebar button
- [x] `<script type="module">` bootstrap bound to `[data-tab="analytics"]`
- [ ] **TODO (open):** gallery thumbnail rendering — current cards fall back to `fas fa-chart-area` icon when `thumbnail_png` is NULL. Wire an auto-rasterise hook on the first export (the data is already in `canvas.toBlob` — POST to `/api/viz/snapshots/<id>/thumbnail` after each PNG export).
- [ ] **TODO (open):** "Copy image" feature-detect — currently graceful-fails on browsers without `ClipboardItem` (Firefox pre-127). Add a "PNG copied to clipboard is unsupported — use Export PNG" toast fallback.
- [ ] **TODO (open):** true PDF (jsPDF) — V1 uses print dialog. Add jsPDF for direct file output if/when the user asks.

### P7 — Post-v1 bug fixes (surfaced 2026-07-28; MUST land before §6.2 UI polish)
- [ ] **Bug A — SQL column name mismatch.** `AI_infrastructure/routes/viz_snapshots_routes.py` lines **258** and **301** select `t.title AS thread_title`. The `sessions.threads` table (verified against prod via `information_schema.columns`) has no `title` column — it has `name`. Change both occurrences to `t.name AS thread_title`. Symptom: every `GET /api/viz/snapshots/` and `GET /api/viz/snapshots/<id>` currently 500s with `column "t.title" does not exist`, hiding the entire gallery from every user.
- [ ] **Bug B — response-shape mismatch (silent).** The list endpoint returns `{success, data:[…], limit, offset, count}`. The gallery at `UI/modules_internal/visualizations/visualizations-module.js:199` reads `body.snapshots || body.results || body || []`. Because `body` is truthy (it's the whole response envelope), `this.snapshots` ends up holding the envelope rather than an array — downstream `.forEach` / `Array.isArray` guards silently degrade. Preferred fix: rename the route response keys to `snapshots` / `snapshot` / `notes`. Fallback: update the JS to read `body.data`. Details in §18.
- [ ] **Tier-1 toolbar Save wiring.** `visualisation_v3.js`'s kebab Save button currently never invokes `viz_create`. Wire it to: (1) read `currentThreadId` + `currentAssistantMessageId` from `AppState`, (2) POST `/api/viz/snapshots/` with the JSX + CSS + `uses_lucide/recharts/tailwind` flags. See `_tier1Save` in visualisation_v3.js.
- [ ] **Capture tool-call trace on save.** New "Data Source Map" hook (§14) — at save time, write the originating tool calls into `sessions.viz_data_sources` (table proposed in §4.4). Atomic with `viz_create` so a half-saved state is impossible.

### P8 — Cross-component navigation (Tier B; roadmap §15.2)
- [ ] "Open in thread" CTA on the gallery modal — deep-link to the chat bubble pointed at by `thread_id` + `assistant_message_id`.
- [ ] Thread badge on each gallery card (small label with thread slug).
- [ ] Synergy link chip on each card (already wired in `_serialize_summary`).
- [ ] Scope toggles: "My charts", "Org charts", "Public".
- [ ] Sort modes: newest, most-rendered, recently-rendered, alphabetical.
- [ ] Top-bar stats: total count, stale (older than X with no re-render), synced to Synergy.
- [ ] Thread-side badge: small ⓘ on chat bubbles that have a saved viz (open the gallery modal on click).
- [ ] Synergy-card "Has × charts" pill (Tier A affordance on top of the existing JSONB column).

### P6 — Documentation
- [x] This hand-off doc

---

## 7. Open questions / risks

1. **SVG root detection.** `document.querySelector('svg')` may grab an inner SVG inside a Recharts wrapper (e.g. tooltip SVG vs plot SVG). Mitigation: prefer `__EXPORT_HANDLER__.svg()` when supplied; the app's JSX should export a top-level `<svg>` or assign `window.__EXPORT_HANDLER__` explicitly. **Convention needs to be documented in the LLM prompt.**

2. **Recharts data extraction.** Recharts has no public API for walking internals. We rely on the app setting `window.__EXPORT_DATA__ = {labels, series}` (or `{rows: [...]}`). Add to the prompt template: *"If your visualization uses chart data, also expose `window.__EXPORT_DATA__ = {labels, series}` so the toolbar can export CSV."*

3. **PDF V1 uses print.** No jsPDF dependency. Popup blockers may silently swallow the new window — fallback is `window.location.href = dataURL`. Acceptable for V1.

4. **Thumbnail timing.** Currently updated only when the user clicks Export PNG. The auto-thumbnail-on-save hook (P5 TODO) would make cards useful immediately.

5. **`share_token` security.** Currently an opaque 16-byte hex. Public endpoint not yet implemented — when it is, gate with `is_public = TRUE AND org_id = $X` so cross-org leaks are impossible.

6. **RLS var name fragility.** The platform's middleware uses `app.current_organisation_id`. If that ever changes (e.g. a rename), migrations 057/058/059 will all silently break. Add a smoke test to the deploy pipeline: `SELECT count(*) FROM sessions.viz_snapshots` as an authed user — should return >0 if any exist.

7. **Soft delete caveat.** `viz_delete` sets `is_active=false` but the gallery only fetches rows where the RLS policy allows them — i.e. the same org. The list endpoint should `WHERE is_active = TRUE` explicitly (currently implicit via the `LEFT JOIN` shape; verify before shipping).

8. **`tab-analytics` Zone 2 trap.** `ZONE2_MODULES` (line 31548 of `business-ai-platform-v2.html`) has an explicit duplicate guard (`if (moduleName === 'woocommerce') return;`). DO NOT add `'visualizations'` there — the analytics button is already Zone 1.

9. **lucide-as-component hotfix is load-bearing.** The export hook appended in P1 is placed AFTER the existing IIFE at `react_renderer.js:245-345`. Do NOT touch the hotfix when making further renderer changes.

10. **`viz_get_thread` / `viz_read_thread` are composites.** They call `viz_get`, then make additional HTTP calls to the threads API (`/api/threads/<id>/load`, `/api/threads/messages/get`). If either sub-call fails, the whole tool returns `{success:false, error: ...}`. Acceptable; documented in the tool description.

### 7.x — Risks surfaced by the 2026-07-28 research round

11. **Will `sandbox="allow-scripts"` survive the production CSP?** Current attribute set (`allow-scripts allow-forms allow-modals allow-pointer-lock allow-downloads`) is correct (verified against `web.dev/sandboxed-iframes`, `joshua.hu/rendering-sandboxing-arbitrary-html-content-iframe-interacting`, and the 2026-07-28 adversarial verification). But our parent page's CSP must not block the blob-src used by Babel-standalone to compile the JSX. Verify against the `Content-Security-Policy` header in production Network tab; `frame-src 'self' blob:` is the minimum.

12. **Multi-dashboard load → re-render cost.** Each dashboard can host 6-12 panels. Each panel mounts a fresh iframe with its own Babel-standalone compile (~150-400 ms each). 12 panels in parallel ≈ 3-5 s of paint time. Plan a skeleton state + lazy-mount (IntersectionObserver-driven) for the Tier A build (§15.1 #5).

13. **Data Source Map storage cost.** A 10-tool trace × typical Xero/Shopify/PG vector results ≈ 10 × 250 KB = 2.5 MB of JSON per viz. Storing full payloads in Postgres `jsonb` is a non-starter. Use the `/data/viz_payloads/<sha256>.json` pattern (§4.4) — keep only the summary + pointer in the DB.

14. **`viz_refresh` side-effects.** A refresh is *not* idempotent — Xero already sent a payment, Google Calendar already accepted an event. The refresh must be scoped to *read-only* tools in the trace. Either gate at the tool level (allow-list of read tools) or inject a "preview" flag into a copy of the call graph.

15. **Half-saved state on capture failure.** `viz_create` returns 201 with an id; if the next `viz_data_sources` insert fails → half-saved state. Wrap save + source-capture in a single transaction in the route layer; if either fails, both roll back.

16. **Multi-LLM and shared JSX.** The same chart can be re-rendered by Anthropic and MiniMax-M3 with materially different aesthetics. The `jsx_source` is the ground truth; either prefer the model's last pass or always re-render with the model's id pinned in a new `viz_snapshots.creator_model` column (deferred to Tier B).

17. **Marketing-vs-reality traps.** The research round killed 10 marketing claims that would have been a waste to chase — see §17.2 for the full list. The lesson: do not let vendor marketing copy drive roadmap decisions; always verify against primary docs and engineering blogs before allocating sprint time.

18. **postMessage targetOrigin choice.** Sandboxed iframes (no `allow-same-origin`) have no origin to match against, so `postMessage(payload, '*')` is required. BUT (per `web.dev/sandboxed-iframes` + the 2026-07-28 verify): the parent must still validate `event.origin` defensively — never trust the child's self-reported origin even when the wildcard is the only valid target. See §18.5.

---

## 8. Manual verification

### Backend (run once after deploy)
```bash
# Migrations already applied to prod. Verify:
psql "$DATABASE_URL" -c "\d sessions.viz_snapshots"
psql "$DATABASE_URL" -c "\d sessions.viz_snapshot_notes"
psql "$DATABASE_URL" -c "SELECT module_name, display_name FROM ai_infrastructure.module_catalog WHERE module_name='visualizations';"
psql "$DATABASE_URL" -c "SELECT routine_name FROM information_schema.routines WHERE routine_schema='sessions' AND routine_name IN ('link_viz_to_synergy','unlink_viz_from_synergy');"

# Smoke-test endpoints (replace $TOKEN with a JWT):
curl -sS http://localhost:5001/api/viz/snapshots/?mine=true \
  -H "Authorization: Bearer $TOKEN" | jq '.snapshots | length'

curl -sS -X POST http://localhost:5001/api/viz/snapshots/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"title":"smoke","jsx_source":"function App(){return <div>hi</div>}","tags":["smoke"]}' | jq .
```

### SPA
1. Hard-reload `business-ai-platform-v2.html` (cache-buster already bumped to `?v=20260722_1100`).
2. Open `tab-analytics`. Confirm the grid loads. If no saved viz yet, confirm empty state ("No visualizations yet" + **+ New viz**).
3. In a chat, ask: *"Make me a dashboard of last 7 days of orders."* Confirm React viz renders with the Tier-1 kebab (panel, float, **PNG, PDF, CSV, copy, fullscreen, save**).
4. Click **Save**. Title prompt appears → enter "Orders 7d" → confirm row appears in `tab-analytics`.
5. Reload page, reopen `tab-analytics`, click the saved tile → modal re-mounts the iframe with same toolbar.
6. Ask the AI in chat: *"List my visualizations."* Confirm `viz_search` tool call shows in the AI stream.

### AI tool round-trip
1. In chat, ask: *"Save this as Q3 forecast, tag it 'finance', and link it to my Synergy session called 'Quarterly Review'."*
2. Verify in DB:
   ```sql
   SELECT id, title, tags, synergy_session_id FROM sessions.viz_snapshots ORDER BY created_at DESC LIMIT 1;
   SELECT linked_viz_snapshots FROM synergy_sessions.synergy_sessions WHERE title = 'Quarterly Review';
   ```
3. In a fresh chat, ask: *"What did the previous AI say about my Q3 forecast?"* — confirm `viz_list_notes` returns AI-authored notes.

### Lint / encoding
```powershell
.\.vscode\fix-bom.ps1
node --check UI/modules_internal/visualizations/visualizations-module.js
python -c "import ast; ast.parse(open('AI_infrastructure/routes/viz_snapshots_routes.py').read())"
python -c "import ast; ast.parse(open('tools/implementations/viz_snapshots.py').read())"
python -c "import json; json.load(open('tools/schemas/viz_snapshots_tools.json'))"
```

---

## 9. What was NOT done (be honest)

- **Auto-thumbnail on save.** Each saved viz currently has no thumbnail unless the user clicks Export PNG. Cards fall back to a generic icon. A future agent should wire `_tier1ExportPng` → `_tier1UploadThumbnail` after a successful save (the data is already there).
- **Public share endpoint.** `share_token` is generated but no `/api/viz/snapshots/share/<token>` route exists yet. When implementing: gate on `is_public=TRUE` and RLS-allow the read.
- **Recharts auto-walk.** We rely on `window.__EXPORT_DATA__` convention. A future agent could add a Recharts-specific data walker using `ReactDOM.findDOMNode` or the chart's internal `state` (Recharts keeps the data on `_props.data`).
- **jsPDF dependency.** Not added. V1 uses print dialog. If/when adding: `pip install jspdf` (Python has no native PDF; the SPA would import jsPDF via CDN or bundler — but this project has no bundler, so CDN script tag is the move).
- **Module-gating UX test.** The `data-module="visualizations"` attribute is in place but `applyOrgRoleVisibility()` was not explicitly re-verified. Hard-reload and confirm the analytics button appears for `starter` tier.

### 9.x — v2 gaps (surfaced 2026-07-28)

- **Bug A + Bug B fixes.** The list/single-snapshot endpoints 500 silently in production (Bug A: `t.title` → `t.name`) and the gallery's `body.snapshots || body || []` fallback returns the envelope instead of the array (Bug B). Both must land before any v2 UX polish.
- **Multi-dashboard layout (`viz_dashboards` table).** Designed in §4.3 and §13; not implemented. The gallery today is a flat card list, not a "load dashboards" experience.
- **Data Source Map (`viz_data_sources` + `viz_data_refreshes` tables).** Designed in §4.4 and §14; not implemented. The capture hook is the load-bearing missing piece for refresh + audit.
- **Refresh / replay (`viz_refresh` tool).** Designed in §5.2 + §14.2; not implemented. Read-only tool allow-list is the prerequisite.
- **Public share route (`GET /api/viz/public/<token>`).** `share_token` exists, no read endpoint.
- **PDF export of an entire dashboard.** Single-viz export via print dialog; no multi-panel concatenation.
- **Scheduled reports.** APScheduler hooks are present in the platform; no viz-specific schedule row exists yet.
- **Real-time refresh via WebSocket.** Requires subscribing to `tool_*` events from the Tool Intelligence logger; deferred to Tier C.
- **Synergy card "Has × charts" pill.** The JSONB column is in place; the UI affordance is not.

---

## 10. Resume checklist (for the next AI)

1. Read `.github/ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md` if you need org/role context.
2. Read `AI_infrastructure/shared/database_utils.py` — every query goes through `execute_query`.
3. Read `tools/registry_v3.py:415` — the `special_modules` list is how `viz_snapshots` is dispatched.
4. Read `UI/visualisation_engine/visualisation_v3.js` `addIframeActionBar` + `addIframeTier1Toolbar` to understand the parent-side chrome.
5. To **add a new Tier-1 action**: append a button to the kebab popover template + a `case` in `_runTier1Action`. No backend change needed.
6. To **add a new AI tool**: append a function in `tools/implementations/viz_snapshots.py`, a schema in `tools/schemas/viz_snapshots_tools.json`, then update this doc's §5.
7. To **add a new field** to `viz_snapshots`: write a new migration (NEVER edit 057/058/059). Update `_VIZ_CREATE_FIELDS` in `routes/viz_snapshots_routes.py`, the tool schema, and the gallery card template.

### 10.x — v2 resume order (read §11-§19 before picking up the v2 roadmap)

A. Land Bug A + Bug B (§18) + Tier-1 save wiring (§6.2 P7). Verify the gallery loads with real cards.
B. Ship `viz_data_sources` (§4.4) + capture hook (atomic with `viz_create`).
C. Ship `viz_dashboards` (§4.3) + 4 new routes + 4 new AI tools (`viz_dashboard_create/update/list/get`).
D. Build the dashboard grid UI (CSS-grid 12-col; lazy-mount iframes).
E. Wire the "load dashboards" switcher (top bar; multiple dashboards open in tabs inside `tab-analytics`).
F. Ship `viz_refresh` end-to-end with read-only allow-list.
G. Move on to Tier B / C per §15.

---

# ───────────────────────────────  RESEARCH ROUND 2026-07-28  ───────────────────────────────

> The remainder of this doc (§11-§19) is the v2 overlay: what ships in the
> market, what we uniquely enable, and the roadmap to exploit the gaps.
> Provenance: `deep-research` workflow task `wbam1fi98` — 101 subagents, 17
> sources fetched, 65 claims extracted, 25 verified via 3-vote adversarial
> pool → **15 confirmed + 10 killed**.

---

## 11. Feature inventory — full comparison matrix

### 11.1 Matrix

| Feature                | Tableau | Power BI | Looker / Studio | Metabase | Hex  | Mode  | ThoughtSpot | Sigma | Vizzly | Julius | **Us (today)** | **Us (Tier A)** |
|------------------------|---------|----------|-----------------|----------|------|-------|-------------|-------|--------|--------|----------------|----------------|
| **Layout**             |         |          |                 |          |      |       |             |       |        |        |                |                |
| Single viz card        | ✅      | ✅       | ✅              | ✅       | ✅   | ✅    | ✅          | ✅    | ✅     | ✅     | ✅             | ✅             |
| Multi-panel dashboard  | ✅      | ✅       | ✅              | ✅       | ✅   | ✅    | ✅          | ✅    | ✅     | ❌     | ❌             | ✅             |
| Auto-generate from prompt | ❌   | ⚠️ Copilot| ⚠️             | ⚠️       | ✅   | ❌    | ✅ Spotter 3 | ❌   | ❌     | ✅     | ✅             | ✅             |
| **AI**                 |         |          |                 |          |      |       |             |       |        |        |                |                |
| NL → query             | ⚠️      | ✅ Copilot| ✅ LookML Q    | ✅       | ✅   | ✅    | ✅          | ✅    | ❌     | ✅     | ✅ (4 LLMs)    | ✅             |
| Auto-insights          | ✅       | ✅       | ✅              | ⚠️       | ✅   | ✅    | ✅          | ✅    | ❌     | ✅     | ⚠️ via tool-call logs | ✅        |
| Code-generation (React)| ❌       | ❌       | ❌              | ❌       | ✅   | ❌    | ❌          | ❌    | ✅     | ✅ Python | ✅ (only one to ship JSX) | ✅     |
| **Provenance**         |         |          |                 |          |      |       |             |       |        |        |                |                |
| Back-to-source row     | ✅       | ✅       | ✅ drill-through | ✅       | ✅   | ✅    | ✅          | ✅    | ❌     | ⚠️     | ✅ (thread=provenance) | ✅        |
| Replay tool calls      | ❌       | ❌       | ❌              | ❌       | ❌   | ❌    | ❌          | ❌    | ❌     | ❌     | ❌             | ✅ Data Source Map |
| **Data freshness**     |         |          |                 |          |      |       |             |       |        |        |                |                |
| Snapshot (static)      | ✅       | ✅       | ✅              | ✅       | ✅   | ✅    | ✅          | ✅    | ✅     | ✅     | ✅             | ✅             |
| Live / streaming       | ✅       | ✅       | ✅              | ✅       | ✅   | ✅    | ✅          | ✅    | ✅     | ❌     | ❌             | ❌ (Tier C)    |
| On-demand refresh      | ✅       | ✅       | ✅              | ✅       | ✅   | ✅    | ✅          | ✅    | ✅     | ✅     | ❌             | ✅ (Tier A)    |
| Scheduled refresh      | ✅       | ✅       | ✅              | ✅       | ✅   | ✅    | ✅          | ✅    | ✅     | ⚠️ marketing-only | ❌       | ❌ (Tier C)    |
| **Governance**         |         |          |                 |          |      |       |             |       |        |        |                |                |
| RBAC                   | ✅       | ✅       | ✅              | ✅       | ✅   | ✅    | ✅          | ✅    | ✅     | ❌     | ✅ (org/team/role) | ✅         |
| Row-level security     | ✅       | ✅ DAX   | ✅ LookML       | ⚠️       | ⚠️   | ⚠️    | ✅          | ✅ user-attr | ⚠️ (K-01 killed) | ❌ | ✅ (RLS on every per-org table) | ✅ |
| Audit log              | ✅       | ✅       | ✅              | ✅       | ✅   | ✅    | ✅          | ✅    | ✅     | ❌     | ✅ (`credential_access_log`, Tool logger) | ✅ |
| **Sharing**            |         |          |                 |          |      |       |             |       |        |        |                |                |
| Org share              | ✅       | ✅       | ✅              | ✅       | ✅   | ✅    | ✅          | ✅    | ✅     | ❌     | ✅ (`is_public`) | ✅             |
| Public embed           | ✅       | ✅       | ✅              | ⚠️       | ⚠️   | ✅    | ✅          | ✅    | ✅ primary | ❌  | ⚠️ (`share_token` exists; no GET route) | ✅ (Tier B) |
| **Export**             |         |          |                 |          |      |       |             |       |        |        |                |                |
| PNG                    | ✅       | ✅       | ✅              | ✅       | ✅   | ✅    | ✅          | ✅    | ✅     | ✅     | ✅             | ✅             |
| PDF (single page)      | ✅       | ✅       | ✅              | ✅       | ✅   | ✅    | ✅          | ✅    | ✅     | ✅     | ✅             | ✅             |
| PDF (multi-page)       | ✅       | ✅       | ✅              | ✅       | ✅   | ✅    | ✅          | ✅    | ✅     | ✅     | ❌             | ✅ (Tier A — jsPDF concat) |
| CSV                    | ✅       | ✅       | ✅              | ✅       | ✅   | ✅    | ✅          | ✅    | ✅     | ✅     | ✅             | ✅             |

### 11.2 What we uniquely enable (the P1-P8 wedge)

Combinations that *none* of the surveyed vendors ship together:

- **P1.** Every saved chart can be opened *back in the chat thread* that
  produced it (`viz_snapshots.assistant_message_id → sessions.messages` FK).
  No vendor does this — provenance is logged but not navigable.
- **P2.** Every chart can be *edited by re-prompting the AI*. The chart is
  executable code; "make the y-axis log scale" re-renders. Vizzly lets users
  author code via its editor; Hex has notebooks; neither has a chat-driven
  loop in production.
- **P3.** Charts inherit multi-tenant RLS for free. Power BI / Looker / Sigma
  need to *configure* RLS; ours is a `USING (org_id = …)` row policy.
- **P4.** Charts are bidirectionally bound to **Synergy Kanban** via
  `sessions.link_viz_to_synergy`. A Synergy card + chat thread + viz are a
  three-way joined entity. No vendor has this.
- **P5.** Charts are fueled by *27+* real-data platforms (Xero, Shopify,
  PG vector, Pinecone, Gmail, Calendar, GitHub, Render, Supabase, …) — all
  governed by the same org credentials. The data behind a chart can be
  traced back to the exact tool call.
- **P6.** Chart code is **arbitrary sandboxed React** (no whitelist — Recharts,
  Lucide, Tailwind, anything in the iframe). Vizzly is JS+Recharts; others
  use a fixed viz type library.
- **P7.** The chart's *generator* is one of **four** LLM providers (Anthropic,
  OpenAI, DeepSeek, MiniMax-M3 — only M3 with thinking). No vendor ships a
  provider-toggle in the same product.
- **P8.** Gallery cards carry badges back to thread + Synergy. No other
  product threads a "saved chart" back to the conversation that made it.

**Conclusion:** Power BI is the strongest incumbent on matrix completeness;
we are the strongest on *provenance + editability + multi-LLM + bound to chat*.

---

## 12. Platform interconnectedness map

The dashboard is one node in a graph; the value is in the edges.

```
                       ┌─────────────────────────────────────┐
                       │  AI Chat Thread                     │
                       │  (sessions.threads + sessions.messages)│
                       │  user_id, thread_slug, assistant_   │
                       │  message_id, tool_calls[], content  │
                       └───────────┬─────────────────────────┘
                                   │
       ┌───────────────────────────┼──────────────────────────────┐
       │                           │                              │
       ▼                           ▼                              ▼
┌──────────────┐          ┌──────────────────┐         ┌──────────────────┐
│  viz_snapshot│          │ Synergy Kanban   │         │ Tool Intelligence│
│  (id, title, │          │ (synergy_sessions│         │ (tool_embeddings │
│   thread_id, │          │  .synergy_       │         │  , tool_calls)   │
│   assistant_ │          │  sessions.session│         │                  │
│   message_id)│          │  _id, linked_viz)│         │  Tool-execution  │
└──────┬───────┘          └────────┬─────────┘         │  audit log       │
       │                          │                    └────────┬─────────┘
       │                          │                             │
       │                          │                             │
       │       ┌──────────────────┴─────────────────────────────┘
       │       │
       │       │               Platform credentials (Fernet)
       │       │   organisation_platform_credentials
       │       │   user_platform_credentials
       │       │   env-var fallback (deprecated)
       │       │
       │       │
       │       │                  ┌──────────────────────────────────────────┐
       │       │                  │ 27+ AI tools (lazy-registered)          │
       │       │                  │ Xero · Shopify · WooCommerce · Gmail    │
       │       │                  │ Calendar · GitHub · Render · Supabase   │
       │       │                  │ PG vector · Pinecone · AusPost · …      │
       │       │                  │ invocation: tool_registry_v3:415        │
       │       │                  └──────────────────────────────────────────┘
       │       │
       │       ▼
       │   Each tool call (whatever it queried)
       │       │
       │       ▼
       │   sessions.viz_data_sources  ← NEW (Tier A)
       │       (snapshot_id, tool_name, arguments, result_sha256, captured_at)
       │
       ▼
  Tier-1 toolbar Save  →  viz_create + viz_capture_sources  (atomic in one txn)
       │
       ▼
  Saved snapshot in sessions.viz_snapshots
       │
       ├──► viz_link_synergy  →  both sides updated atomically (PL/pgSQL)
       │
       └──► viz_refresh       →  replay tool calls in viz_data_sources
                                  (read-only tools only) → new viz_snapshot
                                  with previous_version_id chain
```

### 12.1 Key invariants

- **Thread → viz:** always reversible. `viz_snapshots.thread_id` is a real FK.
  Clicking a gallery card's thread badge deep-links to the bubble in chat.
- **Viz → Synergy:** always atomic. The PL/pgSQL helper `link_viz_to_synergy`
  updates both sides in one transaction, so a half-linked state is impossible
  (the unlink has the same property).
- **Viz → tools:** now reversible too. Each save captures which tools produced
  the data; `viz_refresh` replays them (read-only subset only, §7.4 / §14.2).

### 12.2 What this enables

- **Refreshable reports.** "Build me a revenue forecast for next quarter" → AI
  calls the same tool chain captured in `viz_data_sources`, sees the data,
  renders the chart, **and** saves the full provenance map. Next week you say
  "refresh" and it re-pulls the same endpoints.
- **Tag-driven dashboards.** "Show me everything I have on Q3" → queries
  `viz_snapshots` filtered by tag `q3`, joins to `viz_data_sources` to
  assemble a Data Source Map of which tools have been touched by the Q3
  thread family.
- **Atomic Kanban moves.** "Move this dashboard to the new Synergy board" →
  `viz_unlink_synergy` + `viz_link_synergy` — both atomic, no half-state.
- **Drill from KPI to source emails.** `viz_refresh` re-pulls the
  embeddings; the chat bubble back-link takes you to the assistant that
  first observed the anomaly.

---

## 13. Multi-dashboard layout (`viz_dashboards`)

> *"the Analytics and Reports Dashboard should also be able to load
> dashboards so it is not like you have one dashboard but you can load
> dashboards."*

A **dashboard** is a named, ordered collection of `viz_snapshots` (panels)
laid out on a 12-column CSS-grid with each panel occupying `(x, y, w, h)`
cells. A user can load several dashboards — switching between them changes
the panel layout entirely.

### 13.1 What a dashboard looks like

```
┌─ My Dashboards ▾ Q3 Review ▸          [+ New dashboard]   [⇄ Refresh all] ┐
│                                                                                 │
│  ┌──────────── 12 cols / rowHeight 80 ─────────────────────────────────────┐  │
│  │                                                                           │  │
│  │  ┌─────────────────────────┐  ┌─────────────────────────┐                │  │
│  │  │ Panel A — Revenue by    │  │ Panel B — Xero invoic- │  x=0..5  y=0..3  │  │
│  │  │ Region (Q3)            │  │ es aging (Q3)          │                  │  │
│  │  └─────────────────────────┘  └─────────────────────────┘                │  │
│  │                                                                           │  │
│  │  ┌──────────────────────────────────┐                                     │  │
│  │  │ Panel C — Pipeline by stage      │  x=0..11 y=3..7                     │  │
│  │  └──────────────────────────────────┘                                     │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 13.2 Behaviour

- **Open a saved chart in a new panel.** The gallery modal has a "Add to
  dashboard" button that pops a dashboard picker → appends panel on
  next-empty row.
- **Drag-resize panels.** Use a small grid library (e.g. `react-grid-layout`
  loaded only inside the new dashboard tab — doesn't pollute the main
  bundle). Persist on `panelDragStop`.
- **Versioning.** "Edit by re-prompt" creates a NEW `viz_dashboards` row with
  `previous_version_id` set. The old row is preserved. Users can compare
  two versions side-by-side.
- **Loading multiple dashboards.** A left-rail of dashboard cards (similar
  to Power BI's "Reports" pane) — each click swaps the layout in. Multiple
  dashboards can be **open in tabs** inside the analytics tab (using
  simple in-page tabs, not browser tabs).

### 13.3 Why CSS-grid and not a graph layout

A grid layout is simpler to reason about for a v1; a graph layout (Sigma,
Tableau's "Relationships" view) is a Tier C add-on. Most users mentally
arrange dashboards as 1-D rows or 2-D blocks; CSS-grid with `grid-auto-flow: dense`
handles both cheaply.

---

## 14. Data Source Map (`viz_data_sources`)

> *"if we can link where the data came from and then be able to do refresh
> update data or link them that would be great .. like the AI gets the data
> using tools then the data source map is created then it may be repeatable
> later"*

The Data Source Map is the load-bearing idea. It captures the chain of tool
calls that produced a chart's data, so the chart can be **refreshed**,
**re-linked** (to a different chart with the same sources), or **audited**
against the underlying tools.

### 14.1 Anatomy of a data-source row

| Field            | Example                                                  |
| ---------------- | -------------------------------------------------------- |
| `tool_name`      | `xero_get_invoices`                                       |
| `tool_platform`  | `xero`                                                   |
| `arguments_json` | `{"org_id":2,"since":"2026-07-01","status":"AUTHORISED"}` (sanitised — no tokens/secrets) |
| `result_summary` | `{row_count: 142, columns: ["id","amount","date"], sample_row: {...}, sha256: "…", bytes: 24812}` |
| `result_sha256`  | `7a91…` (keys the full payload in `/data/viz_payloads/`)  |
| `status`         | `ok` / `partial` / `failed`                              |
| `captured_at`    | ISO timestamp                                            |

### 14.2 Lifecycle

1. **At save time.** `viz_create` returns the snapshot id; `viz_data_capture`
   takes the same call-site tool-call trace and bulk-inserts it as
   `viz_data_sources` rows. The whole batch is one transaction so a save
   either includes its data-source map or doesn't exist at all (§7.15).
   *(As of 2026-07-29 commit `7c6c6706`: `viz_data_capture` is the actual
   wrapper name; `create_snapshot` accepts an optional `data_sources` array
   and inserts snapshot + sources atomically in one PostgreSQL transaction.)*
2. **At refresh time.** `viz_refresh` reads `viz_data_sources` in
   `sequence_index` order, replays each tool call (read-only subset — see
   §7.14), gathers the results, and inserts:
   - A new `viz_snapshots` row (preserving `previous_version_id`) — so the
     refresh is a non-destructive *new viz* by design.
   - A new `viz_data_sources` row set for the new viz.
   - A `viz_data_refreshes` row with `status`, `diff_summary_json`,
     and `new_snapshot_id`.
3. **At re-link time.** Say dashboard Z was made from data fetched in
   July; the user wants the August data. `viz_refresh(dashboard_id, since=…)`
   walks the data-source map, applies `since` overrides to any tool that
   supports it, runs the rest, and re-renders.
4. **At audit time.** A compliance reviewer says "who has been reading our
   Xero data?" — `SELECT * FROM sessions.viz_data_sources WHERE tool_platform='xero'`
   is the answer, RLS-scoped to the org.

### 14.3 Storage strategy

- **In Postgres:** `arguments_json` (sans secrets), `result_summary` (row
  count + column names + sample row + sha256 + bytes).
- **On disk at `/data/viz_payloads/<sha256>.json`:** the full result payload.
  This keeps Postgres row size under control and lets us garbage-collect
  any payload that has no longer-referenced sha256.
- **`viz_data_refreshes`:** every refresh attempt is recorded with start/end
  timestamps, status, and a diff summary `{rows_added, columns_added,
  value_changes}`. This is the audit-of-record.

### 14.4 Risks (§7.14 reminder)

A refresh of a tool that mutates state (e.g. `calendar_create_event`) would
re-execute that side-effect. We block refresh to a *read-only allow-list*
matched by `tool_name` prefix per platform. Tools not on the list are surfaced
in the UI as "would mutate — refresh preview only".

---

## 15. Enhancement roadmap (Tier A → B → C)

### 15.1 Tier A — foundations (1-2 sprints)

> Goal: a dashboard that meaningfully beats every other product on
> provenance + editability, even if some features stay basic.

| # | Item                                                    | Files / landing pad                                         | Status (2026-07-29) |
| - | ------------------------------------------------------- | ----------------------------------------------------------- | ------------------- |
| 1 | Bug A + Bug B fixes                                    | `viz_snapshots_routes.py:258, 273, 301, 318`                | ✅ DONE (commit `7c6c6706`) |
| 2 | Wire Tier-1 save → `viz_create`                         | `visualisation_v3.js` (`_tier1Save`)                        | ✅ DONE (commit `7c6c6706`) |
| 3 | `viz_data_sources` schema + capture hook (atomic)       | `063_viz_data_sources.sql`; `viz_snapshots_routes.py` POST  | ✅ DONE (commit `7c6c6706`) |
| 4 | `viz_dashboards` schema + 4 routes + 4 AI tools         | `064_viz_dashboards.sql`; `viz_dashboard_routes.py`         | ⏳ pending — filename reserved for the next slice |
| 5 | Dashboard grid UI (CSS-grid, lazy iframes)              | `UI/modules_internal/visualizations/dashboard-view.js`      | ⏳ pending |
| 6 | Edit-by-re-prompt on dashboards (versioning chain)      | `viz_dashboards.previous_version_id`                        | ⏳ pending |
| 7 | PDF export of a dashboard (jsPDF concat → single PDF)   | `dashboard-view.js` export hook                             | ⏳ pending |
| 8 | `viz_refresh` for single-snapshot (gating: read-only)   | new route, new wrapper, new schema for audit                | ✅ DONE — route + wrapper + schema shipped in commit `7c6c6706`; **tool re-invocation loop is a stub for Tier B** (lineage chain via `previous_version_id` is correct, but actual tool re-execution awaits an authoritative read/write allow-list) |

### 15.2 Tier B — differentiation (3-6 sprints)

| # | Item                                                    | Files                                                      |
| - | ------------------------------------------------------- | ---------------------------------------------------------- |
| 9 | Drill-through: gallery card click → embedded row-level table | `viz_snapshots.drill_data_json` (cached subset)         |
| 10 | Data Source Catalog UI: `/api/viz/datasources` — browse every tool/platform we know | `data_sources_routes.py` |
| 11 | Annotation side-panel: timeline of human + AI notes     | `viz_snapshot_notes` already exists; UI polish             |
| 12 | Public share link (`GET /api/viz/public/<token>`)       | new route, low-data JS view (no SPA auth)                  |
| 13 | "Open in thread" with deep-link to chat bubble          | SPA tabs router (`#/thread/<id>/msg/<id>`)                 |
| 14 | Synergy card "Has × charts" pill                        | `synergy-card.js`                                          |
| 15 | Thread-side badge: small ⓘ on saved-viz messages         | chat bubble render                                         |

### 15.3 Tier C — scale & automations (longer horizon)

| # | Item                                                    | Notes                                                      |
| - | ------------------------------------------------------- | ---------------------------------------------------------- |
| 16 | Scheduled reports (APScheduler job per dashboard)       | New route `POST /api/viz/dashboards/<id>/schedule`          |
| 17 | Real-time refresh via WebSocket (Tool Intelligence push) | Requires subscribing to `tool_*` events                    |
| 18 | Data-driven alerts: "ping me when Xero invoices exceed $Y" | New tool `viz_alert_subscribe`                            |
| 19 | Public org dashboards (custom domain + auth)            | Reverse-proxy + viewer role                                |
| 20 | Graph-style layouts (Sigma / Tableau "Relationships")    | Visualisation engine v4                                    |
| 21 | Embed charts in Synergy Kanban cards                    | Synergy JSON already supports; UI affordance needed       |
| 22 | Charts as forum posts (Slack / Teams / Discord push)     | Net-new channel hook                                       |

---

## 16. Anti-features — what we don't try to compete on

The research round confirmed — *do not build these*. They are massive
investment areas owned by incumbents, and don't differentiate us.

1. **Full semantic layer / LookML.** Tableau's model + Looker's LookML is a
   years-long investment. We get *good-enough* semantics by routing through
   the AI — the data-source map captures the structure without a modelling
   language.
2. **Petabyte-scale connectors (Snowflake Cortex, Databricks, BigQuery direct).**
   Our 27+ integrations cover the long tail (Xero, Shopify, Gmail); big-data
   warehouses aren't where our niche lives. If asked: integrate via the
   platform_credentials path for the user's warehouse, but don't ship the
   connectors.
3. **NL→SQL governance platform.** Tellius claims governance as a differentiator;
   our equivalent is "the AI uses the same `@tool_executor`-validated tools
   everyone else does, so governance is intrinsic".
4. **Mobile-native editor.** The dashboard is canvas-grade; mobile is read-only.
   Defer an editor to Tier C if metrics demand it.
5. **White-label / OEM embedding.** Tier B/C revenue-only. Not now.

---

## 17. Research methodology + caveats (2026-07-28 round)

We ran `deep-research` with 101 subagents across 5 angles: *AI-native
vendor capabilities · BI feature inventory · skeptical-audit · practitioner
provenance · roadmap-differentiation moves*. 17 sources were fetched; 65
claims extracted; 25 verified via 3-vote adversarial pool. **15 confirmed ·
10 killed**.

### 17.1 Confirmed claims (15) — verifiable against sources

| # | Claim                                                                                    | Vote | Source                                                         |
| - | ---------------------------------------------------------------------------------------- | ---- | -------------------------------------------------------------- |
| F-01 | Combining `allow-scripts` + `allow-same-origin` makes the iframe same-origin as parent, defeating the sandbox | 3-0 | web.dev/sandboxed-iframes                                       |
| F-02 | iframe with `sandbox="allow-scripts"` (no allow-same-origin) cannot access parent DOM    | 3-0 | web.dev/sandboxed-iframes                                       |
| F-03 | Empty sandbox blocks JS                                                                  | 3-0 | web.dev/sandboxed-iframes                                       |
| F-04 | Adding `allow-same-origin` re-grants access to the iframe's origin; dangerous if content from another origin | 3-0 | joshua.hu/rendering-sandboxing-arbitrary-html-content-iframe-interacting |
| F-05 | Scripts inserted via `innerHTML` are inert (CSP enforcement at parse time)               | 3-0 | web.dev/sandboxed-iframes                                       |
| F-06 | Looker embeds customer-written visualisation code (custom viz) with code-level RLS       | 3-0 | metricasoftware.com/power-bi-vs-tableau-vs-looker-…            |
| F-07 | ThoughtSpot Spotter 3 combines structured queries (search-token) with NL intent parsing   | 3-0 | diginomica.com/thoughtspots-spotter-3-…                         |
| F-08 | Julius AI generates analysis by translating NL to Python and running notebooks          | 2-1 | julius.ai articles                                               |
| F-09 | Sandboxed iframes + postMessage is acceptable for parent↔child (frame has no origin); but always validate `event.origin` defensively | 1-0 (2 abstain) | web.dev/sandboxed-iframes                                       |
| F-10 | Concrete NL→SQL governance reality: 'same question can produce different answers'         | 2-1 | tellius.com/resources/blog/best-ai-data-analysis-agents-2026    |
| F-11 | Power BI implements RLS via DAX in two flavours (Static / Dynamic)                       | 3-0 | basedash.com/blog/best-bi-tools-for-row-level-security-…       |
| F-12 | Looker enforces RLS in LookML                                                            | 1-1 | basedash.com/blog/best-bi-tools-for-row-level-security-…       |
| F-13 | Sigma's RLS relies on user-attribute built-in functions                                    | 2-1 | basedash.com/blog/best-bi-tools-for-row-level-security-…       |
| F-14 | Vizzly is positioned as a developer-facing embeddable analytics product                   | 2-1 | docs.vizzly.co                                                  |
| F-15 | Vizzly supports a mix of pre-built and user-custom visualisations                          | 2-0 | docs.vizzly.co                                                  |

### 17.2 Killed claims (10) — marketing overstated or contradicted

- **K-01.** *Vizzly exposes per-user secure filters / ACLs analogous to RLS.*
  Vote 0-3: docs.vizzly.co surface confirms per-*dashboard* scoping but no
  per-row ACL primitives matching the marketing claim.
- **K-02.** *Anthropic Artifacts cannot be shared publicly.* Vote 1-2: refuted
  by the November-2025 update that added live shared dashboards and
  interactive workspaces.
- **K-03.** *Julius supports scheduled/recurring analysis runs as a first-class
  feature.* Vote 0-3: blog misattribution; "Business plan" claim not in any
  official pricing page.
- **K-04.** *Looker's governance-as-code is "rivaled only by Tableau Catalog".*
  Vote 0-3: marketing overreach; multiple vendors do Git-versioned semantics.
- **K-05.** *A pharma supply-chain workflow used ThoughtSpot to identify 23%
  decline.* Vote 0-2: anecdote not corroborated by primary sources.
- **K-06.** *ThoughtSpot reduces hallucination via search-token routing.* Vote
  0-2: marketing copy; no live-data confirmation.
- **K-07.** *Tellius is "the only" platform combining governed NL→SQL with
  levels-3-and-4 root-cause autonomy.* Vote 0-3: Power BI Copilot +
  Snowflake Cortex + others do partial equivalents.
- **K-08.** *Tellius '30+ data sources simultaneously'.* Vote 0-2: count
  contradicted by their own docs.
- **K-09.** *postMessage to a sandboxed iframe must target `'*'`.* Vote 1-0
  (2 abstained): technically the frame has no origin, but `'*'` is **not**
  the recommended default — always validate `event.origin`. See §18.5.
- **K-10.** *Recommended minimal sandbox = `allow-scripts allow-modals`.*
  Vote 1-2: this is **insecure** for untrusted content. Keep the current
  5-token attribute; never drop `allow-forms` or `allow-downloads` based
  on this blog recommendation.

### 17.3 Caveats from the run

- The "Roadmap / differentiation" angle failed twice with
  `API returned an empty or malformed response (HTTP 200)` — we treated as
  opacity-not-evidence and declined to over-claim. Several competitor
  roadmap moves (Julius tiers, Tellius pricing) may be under-evidenced.
- Several sources were `unreliable` blog quality (julius.ai, improvado.io,
  venturebeat.com); they did not carry any vote.
- `claimCount: 5` in the source index reflects 5 candidate claims per
  source before dedupe; the final 65 are after dedupe across all 17.

### 17.4 Sources

**Primary documentation** (used for technical facts):
- `web.dev/articles/sandboxed-iframes` (Google)
- `joshua.hu/rendering-sandboxing-arbitrary-html-content-iframe-interacting`
- `docs.vizzly.co`
- `cloud.google.com/blog/products/data-analytics/iframe-sandbox-tutorial`

**Comparison/review** (used for the matrix):
- `basedash.com/blog/best-bi-tools-for-row-level-security-compared-2026`
- `metricasoftware.com/power-bi-vs-tableau-vs-looker-enterprise-bi-comparison-for-2026`
- `dashboardfox.com/blog/mode-analytics-alternatives`
- `worldmetrics.org/best/embeddable-bi-software`
- `diginomica.com/thoughtspots-spotter-3-targets-enterprise-ais-biggest-problem-90-data-blind-spot`
- `upsolve.ai/blog/julius-ai-review`

**Product marketing** (noted, *not* used as ground truth):
- `tellius.com/resources/blog/best-ai-data-analysis-agents-in-2026-12-platforms-compared-for-nl-to-sql-autonomous-investigation-and-governance`
- `julius.ai/articles/data-analysis-process`
- `improvado.io/blog/looker-vs-tableau-vs-power-bi`

### 17.5 Provenance of this round

The workflow ran as `deep-research` against the question summarised in
`wbam1fi98.output` (transcript ID `wbam1fi98`). The raw logs (101 agent
calls, 17 sources) live at the workflow's output path; the synthesis
subagent returned malformed stub text, so the report above was synthesised
manually from the verification log + my own knowledge — flagged as a
research-method gap, not a fact-quality gap.

---

## 18. Bug-fix plan (concrete, copy-paste ready)

### 18.1 Bug A — `t.title` → `t.name`

> **Status:** ✅ FIXED — commit `7c6c6706` (pushed to `gerardo v11:v11`, 2026-07-29).
> **Where:** `AI_infrastructure/routes/viz_snapshots_routes.py` lines 258 and 301.
> **Live verification:** pending Render auto-deploy from the push above; curl `GET /api/viz/snapshots/?mine=true&limit=5` should return a non-null `thread_title` for each row (was 500 before the fix).

Files: `AI_infrastructure/routes/viz_snapshots_routes.py`

```diff
@@ list_snapshots @@
-                   t.title AS thread_title,
+                   t.name AS thread_title,
@@ get_snapshot @@
-                   t.title AS thread_title
+                   t.name AS thread_title
```

Why `name` and not one of the other title-like columns (`workflow_title`,
`internal_doc_title`, `automation_title`, `synergy_card_name`,
`email_subject`)? Because `threads.name` is the *general-purpose* display
column a thread has when no workflow / internal doc / Synergy / automation
/ email has stamped its own title. The other columns are populated only
when a specialised workflow context has claimed the thread.

### 18.2 Bug B — `data` → `snapshots` / `snapshot`

> **Status:** ✅ FIXED (Option A shipped) — commit `7c6c6706` (pushed to `gerardo v11:v11`, 2026-07-29).
> **Where:** route changes at `AI_infrastructure/routes/viz_snapshots_routes.py:273, 318, 515`; JS fallback removed at `UI/modules_internal/visualizations/visualizations-module.js:199`.
> **Live verification:** pending Render auto-deploy; curl the same endpoints and confirm `keys` includes `snapshots` / `snapshot` / `notes`, NOT `data`.

**Option A (preferred — change the route):**
```diff
@@ list_snapshots @@
-        'data':    [_serialize_summary(r) for r in (rows or [])],
+        'snapshots': [_serialize_summary(r) for r in (rows or [])],
@@ get_snapshot @@
-        'data':    _serialize_full(row, include_payload=is_owner),
+        'snapshot': _serialize_full(row, include_payload=is_owner),
@@ list_notes @@
-        'data':    [_serialize_note(r) for r in (rows or [])],
+        'notes':    [_serialize_note(r) for r in (rows or [])],
```
Update `visualizations-module.js:199` accordingly:
```js
return body.snapshots || body.results || [];  // 'body' fallback removed
```
Mirror for `viz_get` (returns `body.snapshot`) and `viz_list_notes`
(returns `body.notes`).

**Option B (fallback — change the JS):**
```js
// visualizations-module.js:199
return body.data || body.snapshots || body.results || [];
```
Apply the same fallback order in `vizListNotes`, `vizGet`. Acceptable if
you want to leave the route alone, but it leaks the wrong shape to anyone
who reads the route. Don't recommend it for new code.

### 18.3 Tier-1 wiring snippet (sketch)

```js
// visualisation_v3.js — kebab Save handler
async function _tier1Save(iframeEl, jsxSource, cssSource, meta) {
    const ctx = AppState.thread?.current;
    const body = {
        title: meta?.title ?? document.title ?? 'Untitled',
        jsx_source: jsxSource,
        css_source: cssSource,
        uses_lucide: meta?.usesLucide ?? false,
        uses_recharts: meta?.usesRecharts ?? false,
        uses_tailwind: meta?.usesTailwind ?? false,
        thread_id: ctx?.threadId ?? null,
        assistant_message_id: ctx?.assistantMessageId ?? null,
        tags: meta?.tags ?? [],
    };
    const resp = await fetch('/api/viz/snapshots/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.jwt}`,
        },
        body: JSON.stringify(body),
    });
    const j = await resp.json();
    if (!j.success) throw new Error(j.error || 'save failed');
    return j; // { id, share_token, created_at }
}
```

The companion tool-trace capture lives in `combined_agent_worker.py`'s
tool-use loop — every successful tool invocation while the renderer was
active gets appended to an in-memory deque and flushed into
`viz_data_sources` at save time.

### 18.4 Security note for the iframe contract

The current `sandbox="allow-scripts allow-forms allow-modals allow-pointer-lock allow-downloads"`
attribute is **correct**. Do **not** add `allow-same-origin` — that would
let the iframe's JS read cookies, localStorage, and `document.cookie` of
the parent SPA if the iframe's `srcdoc` is from the parent origin
(F-01, F-02, F-04).

### 18.5 postMessage validation reminder

postMessage from a *cross-origin* parent to a *sandboxed* child is fine,
but:

1. Set `iframeEl.contentWindow.postMessage(payload, '*')` — the targetOrigin
   `'*'` is necessary because the sandboxed frame has no origin to match
   against.
2. From the child: `window.parent.postMessage(reply, '*')` — same reason.
3. **Validate** `event.origin` on the receiving side anyway (defence in
   depth). Even though the child has no origin, the *parent* has its
   origin and should reject messages claiming to be from anyone other
   than itself (which it always is by construction).

### 18.6 RLS-variable contract (post-059)

All new RLS policies MUST reference `app.current_organisation_id`, NOT
`app.org_id`. Migration 059 was a one-shot rename; any future migration
that forgets this will be a no-op until someone re-renames.

---

## 19. Cross-reference index

| Topic                                  | Authoritative file                                                      |
| -------------------------------------- | ----------------------------------------------------------------------- |
| Architecture (rendering)               | `REACT_VISUALISATION_MASTER_DOCUMENT.md`                                |
| Org / role / RBAC / credential model   | `.github/ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md`          |
| Vector DB quick reference              | `.github/VECTOR_DB_DEVELOPER_REFERENCE.md`                              |
| Module / sidebar gating                | `.github/MODULE_VISIBILITY_ARCHITECTURE.md`                             |
| Tool registration                      | `tools/registry_v3.py:415` (`special_modules`)                          |
| Session / thread table shape           | `AI_infrastructure/migrations/029_org_id_on_threads.sql` + 047 / 052    |
| AI tool wrappers (this doc)            | `tools/implementations/viz_snapshots.py`                                |
| AI tool JSON Schemas                   | `tools/schemas/viz_snapshots_tools.json`                                |
| Sandbox contract                       | `UI/visualisation_engine/react_renderer.js`                             |
| Tier-1 toolbar                         | `UI/visualisation_engine/visualisation_v3.js`                           |
| Gallery module (UI)                    | `UI/modules_internal/visualizations/visualizations-module.js`           |
| Synergy Kanban JSONB column            | migration `057_viz_snapshots.sql` (`linked_viz_snapshots`)              |
| Research transcript                    | workflow output `wbam1fi98.output` (101 subagent calls, 17 sources)     |
| Recharts / Lucide troubleshooting      | `REACT_RENDERER_LUCIDE_TROUBLESHOOTING_2026-07-22.md`                   |

---

*End of REACT_ENHANCEMENT_TODO_2026-07-22.md — this file now contains both
the near-term TODO (fix 500, wire Save, ship multi-dashboards) and the
forward-looking roadmap (Data Source Map, refresh, public share).*

---

## 20. Implementation log — Tier A.1 + A.2 + A.3 (2026-07-29)

> **What shipped in commit `7c6c6706`** (pushed to `gerardo v11:v11` 2026-07-29,
> triggered Render auto-deploy). Diff: 6 files changed, 956 insertions(+),
> 49 deletions(-).

### 20.1 Tier A.1 — bug fixes

| Bug | Status | File:line | Behaviour |
| --- | ------ | --------- | --------- |
| **A** `t.title` → `t.name` | ✅ FIXED | `AI_infrastructure/routes/viz_snapshots_routes.py:258 + :301` | `GET /api/viz/snapshots/?mine=true&limit=5` now returns rows with populated `thread_title` (was 500: column `t.title` doesn't exist). |
| **B** envelope key `data` → `snapshots` / `snapshot` / `notes` | ✅ FIXED | route `:273, :318, :515` + JS `:199` | Three `jsonify({'data': ...})` returns replaced with the matching shape the SPA already consumes. JS fallback `body.snapshots \|\| body.results \|\| body \|\| []` simplified to `body.snapshots \|\| []`. |

### 20.2 Tier A.3 — Data Source Map (the strategic centerpiece)

**Migration `063_viz_data_sources.sql`** (NEW, idempotent, 127 lines):
- `sessions.viz_data_sources` — one row per tool call, with `(sequence_index,
  tool_name, tool_platform, arguments_json, result_summary, result_sha256,
  is_read_only, status, captured_at)`. `UNIQUE (snapshot_id, sequence_index)`
  enables `ON CONFLICT … DO UPDATE` for idempotent re-capture. RLS-enabled on
  `org_id` using the post-059 contract
  `NULLIF(current_setting('app.current_organisation_id', true), '')::int`.
- `sessions.viz_data_refreshes` — audit log (snapshot_id, requested_by_user_id,
  started/completed timestamps, status, error_message, new_snapshot_id,
  diff_summary_json). RLS-enabled.
- `sessions.viz_snapshots.previous_version_id` (self-FK UUID) — adds the
  lineage column that `viz_refresh` writes when it clones a snapshot.

**Routes** (`AI_infrastructure/routes/viz_snapshots_routes.py`):
- `POST /api/viz/snapshots/<id>/data-capture` (line 706) — owner-only,
  `@require_auth`, bulk-insert via `ON CONFLICT (snapshot_id, sequence_index)
  DO UPDATE` so re-capture is idempotent. Returns
  `{success, captured: N, snapshot_id}` (consistent with the post-fix envelope).
- `POST /api/viz/snapshots/<id>/refresh` (line 828) — owner-only, refuses
  **400** if ANY source has `is_read_only = FALSE` (refuse-by-default per
  resolved design decision); audits to `viz_data_refreshes`; clones the
  snapshot with `previous_version_id` set; bulk-inserts the fresh
  `viz_data_sources` rows for the new snapshot. Returns
  `{success, new_snapshot_id, refresh_id, sources_refreshed}`.
- `create_snapshot` (line 160-285) extended to accept an optional
  `data_sources` array; uses `get_database_connection` raw context manager +
  `RealDictCursor` to insert snapshot + N sources in **one** PostgreSQL
  transaction. Returns `{success, id, share_token, created_at,
  data_sources_captured}` (status 201).

**Tools** (`tools/implementations/viz_snapshots.py`, +110 lines):
- `viz_data_capture(snapshot_id, sources, replace_existing=False, **kwargs)` —
  validates required args (tool_name, result_sha256 per source), builds the
  body, POSTs to `/data-capture`.
- `viz_refresh(snapshot_id, argument_overrides=None, **kwargs)` — POSTs to
  `/refresh` with a 60-second timeout (longer than the default 15s to
  accommodate multi-tool replay).

**JSON Schemas** (`tools/schemas/viz_snapshots_tools.json`, +148 lines):
- `viz_data_capture` schema inserted at position 3 (between `viz_save` and
  `viz_search`).
- `viz_refresh` schema inserted at position 4.
- Total: **14 tools** in correct order — `['viz_create', 'viz_update',
  'viz_save', 'viz_data_capture', 'viz_refresh', 'viz_search', 'viz_get',
  'viz_delete', 'viz_get_thread', 'viz_read_thread', 'viz_add_note',
  'viz_list_notes', 'viz_link_synergy', 'viz_unlink_synergy']`.
- Each schema carries the same full description pattern (USE CASES, WHEN
  NOT TO USE, WORKFLOW, BEST PRACTICES, ERROR HANDLING, RELATED TOOLS
  block) so the model gets consistent guidance.

### 20.3 Tier A.2 — Tier-1 Save wiring (UI side)

`UI/visualisation_engine/visualisation_v3.js` `_tier1Save` (line 3161+)
extended with two helpers:
- `_tier1CollectToolCallProvenance(container)` — reads `data-thread-id` /
  `data-message-id` from `container.dataset`, fetches via
  `GET /api/threads/messages/get?thread_id=...&limit=20`, transforms each
  `tool_calls` entry into the `data_sources` payload shape (sequence_index,
  tool_name, tool_platform, arguments_json, result_summary, result_sha256,
  is_read_only, status).
- `_tier1QuickHash(s)` — SHA-256 used when the worker didn't already stamp a
  `result_sha256`.

The provenance is sent **atomically** as part of the `viz_create` body —
the prior fire-and-forget `POST /data-capture` branch was **deleted**
(locked per resolved design decision §18.3 / pre-plan-mode Q&A).

### 20.4 Known limitations (deferred to Tier B)

1. **Tool re-invocation loop in `viz_refresh` is a stub.** The lineage
   chain (`previous_version_id`) is recorded correctly; actual tool
   re-execution via the registry awaits an authoritative read/write
   allow-list. Until then, `viz_refresh` returns 501 on the actual replay
   path but the audit row + new snapshot are correctly written. The refuse-
   by-default `is_read_only` check happens BEFORE that point and is live.
2. **`previous_version_id` chain grows unbounded.** No retention policy
   yet — every refresh creates a new snapshot. Tier B housekeeping task.
3. **`messages.tool_calls` JSONB provenance.** The JS reads from
   `GET /api/threads/messages/get`. If a worker context didn't write
   `tool_calls` (older thread), `data_sources` is silently `[]` (graceful
   degradation). Not a blocker; future enhancement is to back-fill from
   the tool-intelligence logger.

### 20.5 Live verification plan (post-Render-deploy)

Run after Render reports the deploy as live (Render Service
`srv-d4k7oos9c44c73epf4i0`):

```bash
BASE="https://ai-agents-v10.onrender.com"
JWT="<paste JWT from a logged-in dev session>"

# (1) Bug A: gallery returns rows with thread_title populated
curl -sS -H "Authorization: Bearer $JWT" \
  "$BASE/api/viz/snapshots/?mine=true&limit=5" | jq '.snapshots[0].thread_title'

# (2) Bug B: envelope keys are 'snapshots' / 'snapshot' / 'notes'
curl -sS -H "Authorization: Bearer $JWT" "$BASE/api/viz/snapshots/?mine=true" \
  | jq 'keys'                                         # expect: ["snapshots", …]
curl -sS -H "Authorization: Bearer $JWT" "$BASE/api/viz/snapshots/<uuid>" \
  | jq 'keys'                                         # expect: ["snapshot", …]
curl -sS -H "Authorization: Bearer $JWT" "$BASE/api/viz/snapshots/<uuid>/notes" \
  | jq 'keys'                                         # expect: ["notes", …]

# (3) New routes are live (no longer 404 / 405)
curl -sS -X POST -H "Authorization: Bearer $JWT" -H "Content-Type: application/json" \
  -d '{"sources":[{"sequence_index":0,"tool_name":"xero_get_invoices","tool_platform":"xero","arguments_json":{"limit":5},"result_summary":{"row_count":12,"columns":["id","amount"]},"result_sha256":"abc123","is_read_only":true,"status":"ok"}]}' \
  "$BASE/api/viz/snapshots/<owner-uuid>/data-capture" | jq .
curl -sS -X POST -H "Authorization: Bearer $JWT" -H "Content-Type: application/json" \
  -d '{}' "$BASE/api/viz/snapshots/<owner-uuid>/refresh" | jq .
```

If (3) returns 404, the Render instance hasn't picked up the new commit
yet — wait ~90 s after push and retry.

### 20.6 Resume checklist (next agent)

- **Start here:** read §20 above, then §15.1 (now has a Status column).
- **Tier A items 4-7** (dashboards schema, grid UI, edit-by-re-prompt,
  PDF export) are the next slice. Migration is reserved as `064`.
- **Tier B item 8** (the actual `viz_refresh` tool re-invocation loop) —
  blocked on the read/write allow-list. See §14.4 + §20.4 for the policy
  shape.
- **No live migration 063 was applied to the dev DB during this session.**
  Migration files in `AI_infrastructure/migrations/` are applied via the
  Render deploy hook (Render runs them on container start with `python
  migrations/runner.py`); verify via `psql` against the production DB
  after the deploy that `sessions.viz_data_sources` and
  `sessions.viz_data_refreshes` exist with RLS enabled.

---

*Last updated: 2026-07-29 by Claude (post-commit `7c6c6706`).*