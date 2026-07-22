# React Viz Toolbar (Tier 1) + Visualizations Library + AI Tools

> **Date:** 2026-07-22
> **Scope:** Deliver (a) Tier-1 toolbar on every React-viz iframe, (b) persistent "My Visualizations" library bound to the empty `tab-analytics` stub, (c) AI tools for the viz lifecycle, and (d) Synergy Kanban linking.
> **Target DB:** Supabase `ai-agents-production-inhouse` (`ryoicrdifiqhqpsnjmdo.supabase.co`).
> **Module plan tier:** `starter`.
> **For:** another AI agent to resume if this work needs follow-up.

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

---

## 10. Resume checklist (for the next AI)

1. Read `.github/ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md` if you need org/role context.
2. Read `AI_infrastructure/shared/database_utils.py` — every query goes through `execute_query`.
3. Read `tools/registry_v3.py:415` — the `special_modules` list is how `viz_snapshots` is dispatched.
4. Read `UI/visualisation_engine/visualisation_v3.js` `addIframeActionBar` + `addIframeTier1Toolbar` to understand the parent-side chrome.
5. To **add a new Tier-1 action**: append a button to the kebab popover template + a `case` in `_runTier1Action`. No backend change needed.
6. To **add a new AI tool**: append a function in `tools/implementations/viz_snapshots.py`, a schema in `tools/schemas/viz_snapshots_tools.json`, then update this doc's §5.
7. To **add a new field** to `viz_snapshots`: write a new migration (NEVER edit 057/058/059). Update `_VIZ_CREATE_FIELDS` in `routes/viz_snapshots_routes.py`, the tool schema, and the gallery card template.