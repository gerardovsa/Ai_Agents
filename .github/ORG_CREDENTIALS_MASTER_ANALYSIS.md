# Organisation Credentials System — Master Analysis
**Date:** March 23, 2026 (last updated March 23, 2026)**
**Purpose:** Complete authoritative reference for new chat sessions. Multi-tenant platform — one Render deployment, one Supabase database, all users types served.

---

## Multi-Tenant Platform Architecture

### The Three User Types (All Served by One Render + One Supabase DB)

| Type | Login | Org | Session Visibility | Credential Access |
|------|-------|-----|--------------------|-------------------|
| **Individual** | Own email/password | Optional — org still recommended for key storage | private (default) | Personal user_platform_credentials |
| **Team shared login** | One shared email + password | One org row, one user row | private + can set team to all see same sessions | Org-level keys behind vault password |
| **Organisation multi-user** | Each person has own email/password | Same organisation_id, different org_role | private / shared (invite) / team (whole org) | Org-level keys, gated by org_role (viewer→owner) |

### Session Visibility Rules (enforced at BOTH DB level via RLS + Python layer)

```
private  →  owner only (nobody else can see it, even in same org)
shared   →  owner + users explicitly listed in session_members table
team     →  all users with the same organisation_id (whole team sees it)
```

### Code Flow for Every Request

```
Browser → Authorization: Bearer <JWT>
    │
    ▼
flask_app.py @before_request set_rls_context_from_jwt()
    │  decodes JWT → g.rls_user_id, g.rls_organisation_id
    │
    ▼
shared/database_utils.py get_database_connection()
    │  acquires pooled psycopg2 connection
    │  calls rls_session_manager.inject_rls_vars(conn)
    │    → SELECT set_config('app.current_user_id', '12', true)
    │    → SELECT set_config('app.current_organisation_id', '3', true)
    │
    ▼
Supabase PostgreSQL (RLS active after migration 025)
    │  SELECT * FROM synergy_sessions.synergy_sessions
    │  → RLS policy filters rows: owner | shared member | same org (team)
    │
    ▼
synergy_routes.py list_sessions()
    │  Python-level visibility filter (belt-and-braces, backward compat)
    │  Returns only sessions the current user is allowed to see
    ▼
Response
```

---

## Session 3 Changes (March 23, 2026) — Multi-Tenant Implementation

### New Files Created

#### `AI_infrastructure/shared/rls_session_manager.py`
- Sets `app.current_user_id` and `app.current_organisation_id` on every psycopg2 connection
- Uses `set_config(..., true)` — **transaction-local**, safe with pgBouncer / connection pooling
- Reads from `g.rls_user_id` + `g.rls_organisation_id` (set by JWT middleware)
- Non-fatal if called outside Flask context (background tasks / migrations)
- Export: `inject_rls_vars(conn)`, `get_rls_context()`

#### `AI_infrastructure/routes/synergy_share_routes.py`
Flask blueprint `synergy_share_bp`, prefix `/api/synergy/sessions`

| Method | URL | Who can call | What it does |
|--------|-----|-------------|--------------|
| `PATCH` | `/<id>/visibility` | owner or session-admin | Set private / shared / team; auto-assigns org_id when setting team |
| `GET` | `/<id>/members` | owner or any member | List all invited members with role + username |
| `POST` | `/<id>/members` | owner or session-admin | Invite by user_id, username, or email; upserts role |
| `DELETE` | `/<id>/members/<uid>` | owner, admin, or self | Remove a member |

### Modified Files

#### `AI_infrastructure/flask_app.py`
1. **New `@before_request` handler: `set_rls_context_from_jwt()`**
   - Decodes JWT Bearer token on every API request (non-blocking on failure)
   - Sets `g.rls_user_id` (int) and `g.rls_organisation_id` (int)
   - Skips Socket.IO + static paths
   - Values flow into RLS session vars automatically via database_utils.py
2. **New import + register:** `synergy_share_bp`

#### `AI_infrastructure/shared/database_utils.py`
- After setting `search_path` and `statement_timeout`, now calls `inject_rls_vars(conn)`
- This is the single injection point — affects ALL routes that use `get_database_connection()`

#### `AI_infrastructure/routes/synergy_routes.py`
1. `g` added to Flask imports
2. **`list_sessions()`** — multi-tenant filter:
   - `user_id` resolved from `g.rls_user_id` (JWT) or query param
   - `org_id` resolved from `g.rls_organisation_id`
   - Python visibility filter: owner → always show; team → check org_id match; shared/public → show; private → hide
   - RLS at DB level handles filtering when migration 025 is applied (belt-and-braces)
3. **`create_session()`** — auto-sets:
   - `owner_user_id` from `g.rls_user_id` (falls back to request body)
   - `organisation_id` from `g.rls_organisation_id` (falls back to request body)
   - `visibility` from request body (default `private`)
   - INSERT now includes `organisation_id, visibility` columns

### SQL Migration (run in Supabase SQL Editor)
**`AI_infrastructure/migrations/025_synergy_sessions_multitenancy.sql`** — ⏳ NOT YET RUN

What it adds to existing synergy_sessions schema:
- `synergy_sessions.organisation_id` FK → `ai_infrastructure.organisations`
- `synergy_sessions.visibility` TEXT CHECK `('private','shared','team')` DEFAULT `'private'`
- `synergy_sessions.owner_user_id` gets FK constraint to `ai_infrastructure.users`
- New table `synergy_sessions.session_members` (session_id, user_id, role, added_by, added_at)
- `milestone_comments.user_id` gets FK constraint
- `milestone_history.changed_by_user_id` INTEGER FK added
- `tasks.assigned_to_user_id` + `subtasks.assigned_to_user_id` INTEGER FK added
- 8 performance indexes
- RLS on all 8 synergy tables with `private/shared/team` visibility policies
- Backfill: existing sessions → `visibility='private'`, assigned to platform org

---

## Session 2 Changes (March 23, 2026)

> These changes were applied on top of the original architecture described below.

### New Supabase Project
- **Project ID:** `aeazscmhmoipfchuwcih`, region: `ap-southeast-2`
- **Session pooler:** `aws-0-ap-southeast-2.pooler.supabase.com:5432`, user: `postgres.aeazscmhmoipfchuwcih`
- All SQL run manually via Supabase SQL Editor (direct DNS fails from local)

### Migrations Executed
| Migration | File | Status |
|-----------|------|--------|
| 021 | `migrations/021_synergy_sessions_schema.sql` | ✅ Ran |
| 022 | `migrations/022_seed_user_data.sql` | ✅ Ran |
| SUPABASE_SETTINGS.sql | `scripts/SUPABASE_SETTINGS.sql` | ✅ Ran |
| `add_organisations_and_org_credentials.sql` | Schema: organisations, org_platform_credentials, roles, RLS | ✅ Ran (original session) |
| 023 | `migrations/023_seed_organisation.sql` | ✅ Ran |
| 024 | `migrations/024_seed_user_platform_credentials.sql` | ✅ Ran (all 12 rows) |
| 025 | `migrations/025_synergy_sessions_multitenancy.sql` | ✅ Ran |

### Correct run order for pending migrations

**Run in this sequence in Supabase SQL Editor:**
```
Step 1: 023  (creates valorai org — 025 backfill needs this)
Step 2: 024  (personal credentials for gerardo — independent, can run any order)
Step 3: 025  (synergy multi-tenancy — needs organisations table + data from 023)
```

#### Why this order?
- 025 Step 10 runs `UPDATE synergy_sessions.synergy_sessions … FROM ai_infrastructure.users u … WHERE u.organisation_id IS NOT NULL` — it needs users to have `organisation_id` set, which 023 provides for gerardo (user_id=12).
- If 023 hasn't run, user_id=12's `organisation_id` is NULL → 025 backfill is a no-op (not a crash, just nothing backfilled). Since this is a fresh DB with no existing sessions yet, this is not a problem in practice.
- 024 is fully independent (no FK to organisations) — can run before or after 025.

### user_id=1 Retirement ✅
The old platform-global `user_id=1` credential superuser pattern has been retired.

**`AI_infrastructure/auth/user_auth.py`** — `login()` method:
- SELECT now JOINs `ai_infrastructure.organisations` to get org fields
- JWT payload now includes: `user_id, username, email, role, organisation_id, org_role, org_slug, exp`
- Login response `user` object now includes: `organisation_id, org_role, org_name, org_slug`

**`AI_infrastructure/flask_app.py`** — `/api/connections` endpoint:
- UNION query: `user_id=1` global replaced with `organisation_platform_credentials` JOIN via `users.organisation_id`
- Column renamed: `is_platform_global` → `is_org_level`

### VSA Module Fixed ✅
**`AI_infrastructure/shared/vsa_supabase_connector.py`**:
- Was querying non-existent `credentials` column — fixed
- Now uses `SELECT metadata FROM user_platform_credentials WHERE platform = 'supabase_vsa'`

**`get_supabase_credentials.py`** (created at repo root):
- Was missing — caused import crash on startup in `vsa_routes.py` and `supabase_credentials_routes.py`
- Provides `get_supabase_credentials_for_frontend(user_id)` and `get_supabase_credentials_for_backend(user_id)`
- Reads `platform='supabase_vsa'` from user credentials first, then org credential fallback

### Credential Architecture for New DB
- `user_platform_credentials`: NO `credentials` column — API keys go in `credential_value` + `metadata` JSONB
- `supabase_vsa` (VSA Veterinary Alerts DB: `wuwmvtslltqhaycyukxk`) → **org-level credential** in `organisation_platform_credentials`
- All other personal/integration keys → `user_platform_credentials` for user_id=12 (gerardo)

### Seed Data Summary (user_id=12, org valorai)
**023 org credentials** (shared team keys):
- `pinecone`, `anthropic`, `supabase_vsa` → `organisation_platform_credentials`

**024 personal credentials** (12 rows for user_id=12):
- `pinecone`, `voyager`, `openai_embeddings`, `anthropic`, `kajabi`, `supabase` (new DB), `inhouse_print` (SQL Server), `xero_print`, `shopify`, `xero_publishing`, `xero_signs`, `hunter`

**Post-run manual step:**
```sql
-- Replace placeholder after getting key from Supabase Dashboard → Settings → API
UPDATE ai_infrastructure.user_platform_credentials
SET metadata = jsonb_set(metadata, '{anon_key}', '"eyJ..."')
WHERE user_id = 12 AND platform = 'supabase';
```

---

---

## The Two Use Cases This System Serves

### Use Case 1: "Team Shared Login"
One email address + password. Multiple physical team members (e.g. 3 staff in a print shop).  
They share a **single user account** but the org's API keys are **password-protected in a vault**.  
Staff can use the platform normally; only the account owner can reveal the raw API key values.

**How the schema handles this:**
- One row in `users` (single login)
- `organisation_id` links that user to their org
- `org_role = 'owner'` gives full access
- `vault_password_hash` on `organisations` means credentials require a second password to reveal
- All tools resolve keys via `org_credentials_loader.resolve_api_key(user_id, 'anthropic')` transparently

### Use Case 2: "Multi-User Organisation"
Multiple email addresses, each person has their own login. Different roles = different access levels.  
E.g. the director can reveal API keys; staff can use tools but never see the actual keys.

**How the schema handles this:**
- Multiple rows in `users`, each with own email/password
- All share the same `organisation_id`
- Different `org_role` per user: `owner`, `admin`, `manager`, `member`, `viewer`
- RLS at DB level ensures Carol in Org 2 can NEVER see Org 1's credentials — even with a code bug

---

## Role Hierarchy

| Role    | Level | Can See Credentials (masked) | Can Add/Edit/Delete | Can Reveal Plaintext | Can Manage Members |
|---------|-------|------------------------------|---------------------|----------------------|--------------------|
| viewer  | 1     | No                           | No                  | No                   | No                 |
| member  | 2     | No                           | No                  | No                   | No                 |
| manager | 3     | Yes (masked only)            | No                  | No                   | No                 |
| admin   | 4     | Yes (masked only)            | Yes                 | No                   | Yes (non-owners)   |
| owner   | 5     | Yes (masked only)            | Yes                 | Yes (+ vault pwd)    | Yes (all)          |

---

## Files & Current Status

### 1. SQL Migration
**File:** `AI_infrastructure/migrations/add_organisations_and_org_credentials.sql`  
**Status:** ✅ Fixed (4 bugs corrected — see "Bugs Fixed" section below)

**What it creates:**
- `ai_infrastructure.organisations` — top-level tenant table
- `ai_infrastructure.users` — adds `organisation_id` + `org_role` columns
- `ai_infrastructure.organisation_platform_credentials` — org-wide API keys
- `ai_infrastructure.credential_access_log` — immutable audit trail
- Helper functions: `get_role_level(TEXT)`, `user_can_list_credential()`, `user_can_reveal_credential()`, `mask_credential(TEXT)`
- RLS policies on both new tables
- Seed: creates "Platform" org and links user_id=1 as owner

---

### 2. Credential Loader
**File:** `AI_infrastructure/shared/org_credentials_loader.py`  
**Status:** ✅ Complete, no bugs found

**What it does:** 3-tier credential resolution:
1. `user_platform_credentials` (personal OAuth tokens, personal API keys)
2. `organisation_platform_credentials` (shared org keys)
3. `os.getenv()` fallback (legacy, logs a warning)

**Primary usage pattern:**
```python
from AI_infrastructure.shared.org_credentials_loader import resolve_api_key

api_key = resolve_api_key(user_id, 'anthropic')
if not api_key:
    return {"error": "Anthropic API key not configured for your organisation."}
```

**Returns `_source` tag:** `'user'`, `'org'`, or `'env'` — useful for diagnostics.

---

### 3. Backend Routes
**File:** `AI_infrastructure/routes/organisation_credentials_routes.py`  
**Status:** ✅ Complete (997 lines), no bugs found in analysis

**Endpoints:**
| Method | URL | Min Role | What it does |
|--------|-----|----------|--------------|
| GET | `/api/org/info` | member | Org name, plan, member count, your role, `has_vault_password` flag |
| PUT | `/api/org/info` | owner | Update name, display_name, timezone, logo_url |
| GET | `/api/org/members` | manager | List all members with roles |
| PUT | `/api/org/members/<id>/role` | admin | Change a member's role |
| DELETE | `/api/org/members/<id>` | owner | Remove a member from the org |
| GET | `/api/org/credentials` | manager | List credentials — masked values only |
| POST | `/api/org/credentials` | admin | Add new credential |
| PUT | `/api/org/credentials/<id>` | admin | Edit metadata or value |
| DELETE | `/api/org/credentials/<id>` | admin | Soft-delete (sets `is_active=FALSE`) |
| POST | `/api/org/credentials/<id>/reveal` | admin | Return plaintext (+ vault password check) |
| GET | `/api/org/credentials/audit-log` | admin | Who revealed what and when |
| POST | `/api/org/vault-password` | owner | Set or change vault password |
| DELETE | `/api/org/vault-password` | owner | Remove vault password |

**Blueprint registration** (add to `AI_infrastructure/flask_app.py` if not already done):
```python
from routes.organisation_credentials_routes import org_credentials_bp
app.register_blueprint(org_credentials_bp)
```

---

### 4. Frontend UI
**File:** `UI/business-ai-platform-v2.html`  
**Tab button:** line 21241 — `data-tab="organisation"` in the account sidebar  
**Handler:** `AccountSidebar.loadOrganisationTab()` at line 30340  
**OrgManager object:** line 30557  
**Status:** ✅ Complete — the Organisation tab is fully built

**What the UI shows by role:**
- **member/viewer:** Org info card only
- **manager:** + Team Members list + Credentials Vault (masked values, no add/reveal)
- **admin:** + "Add Credential" button + Delete + Edit
- **owner:** + "Reveal Key" button + Vault Password section (set/change/remove)

**Role visibility gating:** `applyOrgRoleVisibility()` function (line ~30560) hides sidebar tabs based on `data-org-min-role` attributes. The "Organisation" tab is visible to all roles (no `data-org-min-role` attr — intentional, everyone can see their own org info).

---

## Bugs Found & Fixed (March 23, 2026)

### Bug 1 — CRITICAL: `COMMENT ON FUNCTION` missing argument signatures
**Would cause:** Migration fails on first run with `ERROR: function get_role_level() does not exist`

```sql
-- ❌ Before (broken):
COMMENT ON FUNCTION ai_infrastructure.get_role_level IS '...';
COMMENT ON FUNCTION ai_infrastructure.mask_credential IS '...';

-- ✅ After (fixed):
COMMENT ON FUNCTION ai_infrastructure.get_role_level(TEXT) IS '...';
COMMENT ON FUNCTION ai_infrastructure.mask_credential(TEXT) IS '...';
```

---

### Bug 2 — SECURITY: No validation on `visible_to_role` / `reveal_requires_role` columns
**Would cause:** A typo like `'adminn'` stores without error; `get_role_level()` returns 0 for unknown roles, silently denying access to everyone including owners.

```sql
-- ✅ Fixed: Added inline CHECK constraints to both columns:
visible_to_role      VARCHAR(50) DEFAULT 'manager'
    CHECK (visible_to_role IN ('viewer', 'member', 'manager', 'admin', 'owner')),
reveal_requires_role VARCHAR(50) DEFAULT 'admin'
    CHECK (reveal_requires_role IN ('viewer', 'member', 'manager', 'admin', 'owner')),
```

---

### Bug 3 — DATA INTEGRITY: UNIQUE constraint doesn't catch NULL duplicates
**Would cause:** Multiple credentials with the same `organisation_id + platform` and no `display_name` all accepted, creating ambiguous rows the loader picks arbitrarily.

```sql
-- ❌ Before:
UNIQUE(organisation_id, platform, display_name)

-- ✅ After (PostgreSQL 15+ / Supabase compatible):
UNIQUE NULLS NOT DISTINCT (organisation_id, platform, display_name)
```

---

### Bug 4 — MINOR: RLS write policy missing explicit `WITH CHECK`
**Risk level:** Low (PostgreSQL uses USING as implicit WITH CHECK for FOR ALL), but ambiguous.

```sql
-- ✅ Fixed: Added explicit WITH CHECK clause:
CREATE POLICY org_creds_write_own_org
    ON ai_infrastructure.organisation_platform_credentials
    FOR ALL
    USING (
        organisation_id = current_setting('app.current_organisation_id', true)::integer
    )
    WITH CHECK (
        organisation_id = current_setting('app.current_organisation_id', true)::integer
    );
```

---

## Architecture Alignment With Use Cases

### "Team Shared Login" flow:
```
Single user logs in (email: team@company.com, password: shared)
    │
    ├─ Flask resolves user_id = 5
    ├─ user has organisation_id = 3 ("Print Shop Co")
    ├─ org_role = 'owner'
    │
    ├─ Staff uses tools → resolve_api_key(5, 'anthropic') → org key returned transparently
    ├─ Staff visits Settings → Organisation tab → sees masked key list
    │
    └─ Owner wants to see actual key:
           Clicks "Reveal Key"
           → Prompted: "Enter vault password"
           → Enters correct password (bcrypt check against vault_password_hash)
           → Key shown for 30s (copy + auto-close)
           → Logged in credential_access_log
```

### "Multi-User Organisation" flow:
```
Organisation: "Acme Corp" (id=1)

Alice (owner) ──────┐
Bob   (admin) ──────┼── all share organisation_id=1
Carol (member) ─────┘

Alice can: reveal keys, set vault password, manage members, add/delete credentials
Bob can:   add/edit/delete credentials (still masked), view audit log
Carol can: use the platform normally — org keys work transparently, no credentials panel

Dave (org=2, TechStart) → RLS at DB level: CANNOT see Acme Corp credentials at all
```

---

## Credential Resolution Priority

```
resolve_api_key(user_id=5, platform='anthropic')

1. Check user_platform_credentials WHERE user_id=5, platform='anthropic'
   → Personal key? Use it (e.g. dev's own API key for testing)

2. Look up user 5's organisation_id → get org-level credential
   → Most tools will land here (shared Anthropic billing key per client)

3. os.getenv('ANTHROPIC_API_KEY')
   → Legacy fallback, logs a warning — signals migration needed
```

---

## What Calls `resolve_api_key`

Any tool that needs an API key should use:
```python
from AI_infrastructure.shared.org_credentials_loader import resolve_api_key

# In tool implementation:
api_key = resolve_api_key(user_id, 'anthropic')
```

**Platforms that should be org-level (not user-level):**
`anthropic`, `openai`, `auspost`, `stripe`, `sendgrid`, `twilio`, `assemblyai`, `pinecone`, `deepseek`

**Platforms that should stay user-level (OAuth tokens):**
`google`, `microsoft`, `xero`, `gmail_oauth`, `outlook_oauth`

---

## Deployment Checklist (New DB: aeazscmhmoipfchuwcih)

### Schema & Migrations
- [x] 021: synergy_sessions schema (8 tables) — run ✅
- [x] 022: gerardo user seed (user_id=12) — run ✅
- [x] SUPABASE_SETTINGS.sql: realtime + RLS + indexes + extensions — run ✅
- [x] `add_organisations_and_org_credentials.sql` — run ✅
- [x] 023: valorai org + supabase_vsa org credential — run ✅
- [x] 024: 12 personal credentials for gerardo — run ✅
- [x] 025: synergy multi-tenancy (org FK, visibility, session_members, RLS) — run ✅
- [ ] Fix supabase anon_key placeholder: `UPDATE ai_infrastructure.user_platform_credentials SET metadata = jsonb_set(metadata, '{anon_key}', '"eyJ..."') WHERE user_id=12 AND platform='supabase'`

### Backend Verification
- [ ] Verify: `SELECT ai_infrastructure.get_role_level('owner');` returns `5`
- [ ] Verify: `SELECT ai_infrastructure.mask_credential('sk-ant-api03-TestKey123456789');` returns correct mask
- [ ] Blueprint registered in `flask_app.py`: `app.register_blueprint(org_credentials_bp)`
- [ ] `GET /api/org/info` returns `{ organisation: {...}, your_role: 'owner' }` for logged-in user
- [ ] `GET /api/org/credentials` returns masked list (not plaintext) for manager+
- [ ] Member user gets 403 on credentials endpoint
- [ ] Vault password flow: set → reveal requires it → wrong password logged → correct password shows key
- [ ] `resolve_api_key(user_id, 'anthropic')` returns org key (not env var)
- [ ] User from a second org cannot see first org's credentials (RLS enforcement)

### Boot Test (after all migrations)
- [ ] Run `BISTART.ps1` — no import errors
- [ ] Login as gerardo — response includes `org_name: "ValorAI Platform"`, `org_role: "owner"`, `org_slug: "valorai"`
- [ ] VSA module loads — check `/api/vsa/health`
- [ ] Connections page shows org-level credentials with `is_org_level: true` for pinecone, anthropic, supabase_vsa

---

## Known Gaps / Future Work

1. **No invite system** — members are added by directly updating `organisation_id` in the DB or via a future invite endpoint. The routes file has role-change and remove-member endpoints but no `POST /api/org/members/invite` yet. See `AUTH_FLOW_AND_ONBOARDING.md` for the full invite flow design.

2. **No org creation UI** — new client orgs are seeded via SQL (023-style INSERT per client). Needs a `/api/admin/org/create` endpoint and lightweight onboarding wizard for the platform admin to use. NOT self-service for clients (they don't create their own org — you onboard them).

3. ~~**`app.current_organisation_id` session variable**~~ — **✅ RESOLVED (Session 3)** — `set_rls_context_from_jwt()` in `flask_app.py` extracts values from JWT and writes to `g.rls_user_id` / `g.rls_organisation_id`. `database_utils.get_database_connection()` then calls `inject_rls_vars()` which sets `set_config('app.current_user_id', ..., true)` on every connection.

4. **Credential value encryption at rest** — currently stored as plain text in the DB column. Supabase column-level encryption or application-layer AES-GCM encryption before storing would be the next hardening step.

5. **`is_sub_user` field** — referenced in `applyOrgRoleVisibility()` in the frontend but not in the DB schema. If sub-users need full access restriction (level 0), this column needs adding to the `users` table.

6. **Login screen shows no org context** (expected for multi-tenant — you don't know the user's org until they authenticate). Post-login: JWT now contains `org_name`, `org_role`, `org_slug` — just needs a header badge rendered in the UI.

7. **Google/Microsoft OAuth login does not check org membership** — the OAuth callbacks (`/api/auth/google/callback`, `/api/auth/microsoft/callback`) create or find a user by email domain but do not enforce org membership. If a user's email is not in the `users` table, they will fail to log in with a confusing error. Forward plan: OAuth callback should check if email domain matches `organisations.allowed_domains`, then auto-assign `organisation_id` and create the user row if missing.

8. **No `organisations.allowed_domains` column** — needed to auto-provision Google Workspace / M365 users. E.g. store `["inhouseprint.com.au"]` so that anyone who SSOs with that domain gets added to that org automatically.

9. **org_invitations table does not exist yet** — the invite system needs: DB table, `/api/org/invite` POST endpoint, email delivery (SendGrid/Resend), `/api/org/accept-invite?token=` GET/POST endpoint. Detailed design in `AUTH_FLOW_AND_ONBOARDING.md`.

---

## File Index Quick Reference

| File | Lines | Purpose |
|------|-------|---------|
| `AI_infrastructure/migrations/add_organisations_and_org_credentials.sql` | 419 | DB schema — run once in Supabase |
| `AI_infrastructure/migrations/025_synergy_sessions_multitenancy.sql` | — | ⏳ Synergy multi-tenancy: org FK, visibility, session_members, RLS — **NOT YET RUN** |
| `AI_infrastructure/shared/rls_session_manager.py` | — | NEW (Session 3): Sets PostgreSQL RLS session vars on every connection |
| `AI_infrastructure/routes/synergy_share_routes.py` | — | NEW (Session 3): PATCH visibility, GET/POST/DELETE members for synergy sessions |
| `migrations/021_synergy_sessions_schema.sql` | — | synergy_sessions schema (8 tables) |
| `migrations/022_seed_user_data.sql` | — | gerardo user, preferences, OAuth token |
| `migrations/023_seed_organisation.sql` | — | valorai org + workspace + org credentials (pinecone, anthropic, supabase_vsa) — **NEEDS RE-RUN** |
| `migrations/024_seed_user_platform_credentials.sql` | 170 | 12 personal credentials for user_id=12 — **NEEDS RE-RUN** |
| `AI_infrastructure/routes/organisation_credentials_routes.py` | 997 | Flask API for all org/credential operations |
| `AI_infrastructure/shared/org_credentials_loader.py` | 416 | 3-tier key resolver used by all tools |
| `AI_infrastructure/auth/user_auth.py` | — | login() JOINs organisations; JWT+response include org_name, org_role, org_slug |
| `AI_infrastructure/flask_app.py` | — | /api/connections UNION uses org table (user_id=1 retired) |
| `AI_infrastructure/shared/vsa_supabase_connector.py` | — | Fixed _get_credentials_from_db (was querying non-existent columns) |
| `get_supabase_credentials.py` | — | Created (was missing — caused startup crash); reads supabase_vsa credentials |
| `.github/ORGANISATION_CREDENTIALS_ARCHITECTURE.md` | ~270 | Architecture narrative + API quick reference |
| `.github/AUTH_FLOW_AND_ONBOARDING.md` | — | Auth UI/UX flows, org setup, invite system design |
| `UI/business-ai-platform-v2.html` (line 30340) | — | `loadOrganisationTab()` + `OrgManager` JS object |
