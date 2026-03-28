# Organisation Credentials System — Master Analysis
**Date:** March 26, 2026 (Last Updated: March 28, 2026)
**Purpose:** Complete authoritative reference for new chat sessions. Multi-tenant platform — one Render deployment, one Supabase database, all user types served.
**Status:** ✅ All migration 020–036 work complete. Platform catalog (27 platforms), module catalog (26 modules), org/user/role system, credential vault, and DB-driven permission model are LIVE in Supabase. ✅ March 28: Added module visibility section + org table schema reference.

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

## Module Visibility & Credential Requirements

The organisation system also gates **feature modules** based on four layers of visibility control:

### Layer 1: Module Enablement Per Org

**Table**: `ai_infrastructure.org_module_access`

Admin toggles modules on/off for the organisation:
- If enabled: module sidebar tab shows in UI
- If disabled: module tab hidden for all users in that org
- Example: Customer A enables Xero, Customer B disables it

### Layer 2: User Role Permissions

**Column**: `ai_infrastructure.users.org_role`

Role hierarchy: `viewer (1) < member (2) < manager (3) < admin (4) < owner (5)`

- **Viewers** cannot see Settings, Credentials, or admin-only modules
- **Members** can use enabled modules but not manage them
- **Managers+** can view/edit credentials
- **Admins+** can enable/disable modules for the org
- **Owners** have full access including vault password reveal

### Layer 3: Sub-User Inheritance

**Columns**: `parent_user_id`, `is_sub_user` on `ai_infrastructure.users`

Sub-users inherit parent's enabled modules but operate within their own role level:
- Parent (owner) enables Xero module → sub-user (viewer) can see Xero tab
- But sub-user (viewer) cannot edit Xero settings (role restriction)
- Sub-user can view only, cannot write or configure

### Layer 4: Required Platform Credentials

**Column**: `ai_infrastructure.module_catalog.required_platforms`

Modules require specific credential to function:
- Xero module requires `xero` platform credential in org vault
- WooCommerce module requires `woocommerce` credential
- If credential missing: module shows "Configuration Required" message
- If credential exists: module fully accessible

### Module Gating Example Flow

```
1. Admin enables Xero module for org
   → org_module_access[organisation_id=1, module_name='xero'].is_enabled = TRUE

2. Admin adds Xero credential to org vault
   → organisation_platform_credentials[organisation_id=1, platform='xero'] added

3. Member logs in
   → GET /api/org/modules returns { enabled_modules: ['xero', ...] }
   → Frontend shows Xero tab in sidebar

4. Member clicks Xero tab
   → Checks if 'xero' credential exists in vault
   → Credential found → full access ✓
   → Member can view/manage Xero integration

5. Admin disables Xero for the org
   → org_module_access.is_enabled = FALSE
   → Member's Xero tab disappears on next page reload
```

**See also:** [MODULE_VISIBILITY_ARCHITECTURE.md](.github/MODULE_VISIBILITY_ARCHITECTURE.md) for the complete 4-layer visibility model and `initModulesFromOrg()` implementation design.

---

## Organisation Table Schema

The `ai_infrastructure.organisations` table defines the multi-tenant entity. Complete schema with all 20 columns (across 4 migrations) documented in:

→ **[ORG_DOCUMENTATION_AND_UI_ALIGNMENT_SUMMARY_MAR28_2026.md](../ORG_DOCUMENTATION_AND_UI_ALIGNMENT_SUMMARY_MAR28_2026.md)**

Key columns:
- `id`, `name`, `slug` — org identity
- `plan_tier` — free/starter/professional/enterprise (gates feature availability)
- `visibility` — org-level default (private/unlisted/public) inherited by sessions
- `allowed_domains` — SSO auto-join email domains
- `ai_provider`, `ai_model`, `ai_max_tokens` — org-wide AI model defaults
- `vault_password_hash` — optional extra security lock on credential reveal

All users in the same `organisation_id` share:
- Enabled feature modules (from `org_module_access` table)
- Credential vault (from `organisation_platform_credentials` table)
- Team-visibility sessions (visible to all members with same org_id)

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

## Session 5 — Gap Implementation (March 25, 2026)

8 of 22 gaps fully implemented. All CRITICAL gaps resolved. All files committed.

| Gap | Fix | Files Changed | Migration |
|-----|-----|---------------|-----------|
| **GAP-C1** | Pinecone namespace = `org_{id}` per request | `tools/implementations/pinecone/pinecone_tools.py` | — |
| **GAP-C2** | `SET LOCAL ROLE authenticated` in `inject_rls_vars()` | `AI_infrastructure/shared/rls_session_manager.py` | `028_grant_authenticated_role.sql` ✅ run |
| **GAP-C3** | Per-request `resolve_api_key()` for Anthropic / OpenAI / DeepSeek | `AI_infrastructure/core/unified_ai_client.py`, `flask_app.py` | — |
| **GAP-C4** | jwt_version counter embeds in JWT, validated on every request, incremented on role change/remove | `user_auth.py`, `flask_app.py`, `organisation_credentials_routes.py` | `026_jwt_version_counter.sql` ✅ run |
| **GAP-H1** | `PUT /api/org/info` expanded to accept `name`/`description`/`visibility`; `GET` returns new fields | `organisation_credentials_routes.py` | `027_org_description_visibility.sql` ✅ run |
| **GAP-H2** | AssemblyAI client uses `org_credentials_loader.resolve_api_key()` | `tools/implementations/assemblyai.py` | — |
| **GAP-H5** | `inject_rls_vars()` logs at INFO level; log line shows `role=authenticated` | `rls_session_manager.py` | — |
| **GAP-M5** | `ALLOWED_PLATFORMS` set validates `platform` on `add_credential`; returns 400 for unknown names | `organisation_credentials_routes.py` | — |

**Remaining open (Phase 1d checkpoint):** Manual RLS verification in Supabase — log in as org 2 user, confirm `organisation_platform_credentials` returns 0 org 1 rows.

---

## Session 4 — Full Platform Alignment Analysis (March 25, 2026)

This section is the result of a comprehensive audit of the entire multi-tenant stack: database schema, auth/JWT, AI provider resolution, credential vault, vector DB isolation, module access, frontend UI, and Supabase/RLS configuration.

### What Is Already Aligned ✅

Before addressing gaps, the following components are working correctly and should not be broken:

| Layer | What Works |
|-------|-----------|
| **DB: tenant isolation** | `organisations` table, `users.organisation_id` FK, `users.org_role` — correct design |
| **DB: credential vault** | `organisation_platform_credentials` with role-gating columns, audit log, soft-delete |
| **DB: invite system** | `org_invitations` table with token expiry (added March 23) |
| **DB: pgvector isolation** | `vector_embeddings` table isolated by `user_id` + `namespace` |
| **DB: document library** | `document_library` isolated by `owner_user_id` |
| **DB: synergy sessions** | `synergy_sessions` with `organisation_id`, `visibility`, `session_members`, full RLS |
| **Auth: JWT payload** | Login response includes `org_id`, `org_name`, `org_role`, `org_slug` |
| **Auth: profile endpoint** | `GET /api/auth/profile` returns org fields from DB join |
| **Auth: RLS session vars** | `rls_session_manager.py` sets `app.current_user_id` + `app.current_organisation_id` per connection |
| **Auth: per-request injection** | `database_utils.py` calls `inject_rls_vars(conn)` after every connection checkout |
| **Credential resolver** | `org_credentials_loader.py` — correct 3-tier resolver (user → org → env), source-tagged |
| **Org credentials API** | Full CRUD at `/api/org/*` with role enforcement |
| **Vault security** | Vault password, reveal gating, bcrypt hash, 30s auto-close, audit log |
| **Frontend: org tab** | `loadOrganisationTab()` + `OrgManager` — complete for all roles |
| **Frontend: invites** | Copy-to-clipboard, send via Gmail/Outlook, revoke invite — added March 25 |
| **Frontend: role gating** | `applyOrgRoleVisibility()` hides UI by `data-org-min-role` attributes |

---

### Gap Registry

Each gap is structured for systematic resolution. Work through them in the order shown in the **Systematic Build Order** section below.

---

#### GAP-C1: Pinecone Empty Namespace — DATA LEAKAGE (CRITICAL)
**Status:** ✅ **FIXED** (March 25, 2026)  
**Affected Files:** `tools/implementations/pinecone/pinecone_tools.py`  
**Problem:** `namespace = creds.get('namespace', '')` defaults to an empty string. Every organisation's Pinecone vectors land in the same default namespace. One user can overwrite or query another user's vectors.  
**Fix Steps:**
1. In `_get_pinecone_client()` (or wherever the index is called), resolve `organisation_id` for the calling user.
2. Replace the namespace extraction line:
   ```python
   # Before:
   namespace = creds.get('namespace', '')
   
   # After:
   from AI_infrastructure.shared.database_utils import execute_query
   org_row = execute_query(
       "SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s",
       (user_id,), fetch_mode='one'
   )
   org_id = org_row['organisation_id'] if org_row else None
   namespace = f"org_{org_id}" if org_id else f"user_{user_id}"
   ```
3. Pass `namespace` to every `upsert`, `query`, and `delete` call in the file.  
**Verification Checkpoint:** Upsert a vector as user in org 1. Query Pinecone and confirm it is in namespace `org_1`. Log in as user in org 2, run a query — the `org_1` vector must NOT appear.  
**Dependencies:** None — standalone fix.

---

#### GAP-C2: service_role Key Bypasses All RLS — SECURITY (CRITICAL)
**Status:** ✅ **FIXED** (March 25, 2026)  
**Affected Files:** `AI_infrastructure/shared/rls_session_manager.py`, `AI_infrastructure/migrations/028_grant_authenticated_role.sql`  
**Problem:** `supabase_client.py` connects using the `SUPABASE_SERVICE_ROLE_KEY` (or the DB `SUPABASE_DB_PASSWORD` which is the Postgres superuser). The service role bypasses every RLS policy. Even though `rls_session_manager.py` sets `app.current_organisation_id`, RLS policies on the `organisation_platform_credentials` table are never evaluated because the connection's role is `service_role` / `postgres`.  
**Fix Applied:**
- `inject_rls_vars()` now calls `SET LOCAL ROLE authenticated` after setting the session vars (only when a user context exists). `SET LOCAL` is transaction-scoped — reverts automatically when `PooledConnection.close()` calls `rollback()`. Pool-safe.
- Migration `028_grant_authenticated_role.sql` grants `USAGE` + `SELECT/INSERT/UPDATE/DELETE` on all three app schemas (`ai_infrastructure`, `synergy_sessions`, `sessions`) to the `authenticated` role so the role-switch doesn't fail with permission errors.  
**Verification Checkpoint:** Log in as user in org 2. Attempt `SELECT * FROM ai_infrastructure.organisation_platform_credentials` via raw DB call (not via Flask API). Result must be 0 rows (RLS filters org 1's rows).  
**Dependencies:** Migration `028_grant_authenticated_role.sql` must be run in Supabase before deploying.  
**Note:** Background tasks (cron, embeddings) stay as `postgres` — `inject_rls_vars()` is a no-op outside Flask request context.

---

#### GAP-C3: UnifiedAIClient Uses user_id=1 for ALL Requests — WRONG BILLING KEY (CRITICAL)
**Status:** ✅ **FIXED** (March 25, 2026)  
**Affected Files:** `AI_infrastructure/core/unified_ai_client.py`  
**Problem:** `UnifiedAIClient.__init__()` calls `self._get_api_key_from_supabase('anthropic', user_id=1)` once at server startup. Every AI request from every org uses user 1's personal Anthropic key. Org-level credentials in the vault are never reached.  
**Fix Steps:**
1. Remove the startup API key initialisation from `__init__()` — do NOT store `self.anthropic_api_key` as an instance variable.
2. In the method that makes the actual API call (e.g. `call_anthropic()`, `call_openai()`), add a `user_id` parameter.
3. At call time, resolve the key:
   ```python
   from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
   
   def call_anthropic(self, messages, user_id: int, **kwargs):
       api_key = resolve_api_key(user_id, 'anthropic')
       client = anthropic.Anthropic(api_key=api_key)
       # ... rest of call
   ```
4. Update all callers that pass to `UnifiedAIClient` to include `user_id` (get it from `g.user_id` or `flask.request`).
5. Verify `openai.api_key = ...` global assignment (thread-unsafe) is also replaced with per-call client instantiation.  
**Verification Checkpoint:** Log in as user in org 2 (which has a different Anthropic key stored). Send a chat message. Check Anthropic usage dashboard — the billing must appear under org 2's key, not org 1's.  
**Dependencies:** `org_credentials_loader.py` is already built (no additional changes needed there). Needs `user_id` threaded through the call chain.

---

#### GAP-C4: JWT org_role Not Invalidated on Role Change — STALE PERMISSIONS (CRITICAL)
**Status:** ✅ **FIXED** (March 25, 2026) — Migration `026_jwt_version_counter.sql` run in Supabase.  
**Affected Files:** `AI_infrastructure/auth/user_auth.py`, `AI_infrastructure/routes/organisation_credentials_routes.py`  
**Problem:** JWT tokens have a 30-day expiry. When an admin demotes a member or removes them from an org, the user's existing JWT still contains the old `org_role`. They retain elevated permissions for up to 30 days.  
**Fix Steps:**

*Option A — JWT Version Counter (recommended):*
1. Add a `jwt_version` integer column to the `users` table (default 1).
2. Include `jwt_version` in the JWT payload at login.
3. In `require_auth` middleware, after decoding the JWT, query `SELECT jwt_version FROM users WHERE id = %s` and compare. If DB version > token version, return 401 "Session expired, please log in again".
4. In the role-change endpoint (`PATCH /api/org/members/:user_id/role`) and remove-member endpoint, increment `jwt_version` for the affected user.

*Option B — Short-lived tokens with refresh (more complex):*
1. Issue 15-minute access tokens + 7-day refresh tokens.
2. Build `POST /api/auth/refresh` endpoint.
3. On every access token expiry, client calls refresh — backend can deny refresh for demoted users.

*Recommended:* Option A first (minimal changes), Option B later.  
**Verification Checkpoint:** Log in as user, get JWT. In DB, change `users.org_role` to a lower level AND increment `jwt_version`. Make an API request with the old token — must get 401. Log in again with new JWT — correct role returned.  
**Dependencies:** None — standalone.

---

#### GAP-H1: `saveOrgSettings()` Undefined — BROKEN BUTTON (HIGH)
**Status:** ✅ **FIXED** (March 25, 2026) — Migration `027_org_description_visibility.sql` run in Supabase.  
**Affected Files:** `UI/business-ai-platform-v2.html`  
**Problem:** The `org-subtab-overview` panel has a "Save Settings" button with `onclick="saveOrgSettings()"`. This function does not exist in any JavaScript block. Clicking it throws `ReferenceError: saveOrgSettings is not defined`.  
**Fix Steps:**
1. Search the HTML for the "Save Settings" button in `org-subtab-overview`.
2. Determine what settings it should save (org name, description, allowed domains, AI provider preference, etc.).
3. Implement the function:
   ```javascript
   async function saveOrgSettings() {
       const orgName = document.getElementById('org-settings-name')?.value;
       const orgDesc = document.getElementById('org-settings-description')?.value;
       // ... gather other fields
       
       const response = await fetch('/api/org/settings', {
           method: 'PATCH',
           headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authToken}` },
           body: JSON.stringify({ name: orgName, description: orgDesc })
       });
       const data = await response.json();
       if (data.success) showNotification('Settings saved', 'success');
       else showNotification(data.error || 'Save failed', 'error');
   }
   ```
4. Add a `PATCH /api/org/settings` endpoint in `organisation_credentials_routes.py` if it does not already exist (check the route file first).  
**Verification Checkpoint:** Click "Save Settings" button — no console errors. Settings persist after page reload.  
**Dependencies:** None.

---

#### GAP-H2: Org Credentials Vault Is Storage-Only — AI Engine Ignores It (HIGH)
**Status:** ✅ **FIXED** (March 25, 2026)  
**Affected Files:** `AI_infrastructure/core/unified_ai_client.py`, `AI_infrastructure/core/tool_use_agent.py`, `AI_infrastructure/shared/org_credentials_loader.py`  
**Problem:** Users can add Anthropic/OpenAI/AssemblyAI keys to the org vault via the UI, but the AI engine never retrieves them. All AI calls still use the env-var fallback or user_id=1's personal key (see GAP-C3). The vault is a UI feature with no backend consumers.  
**Fix Steps:**
1. Complete GAP-C3 first (wire `resolve_api_key` into `UnifiedAIClient`).
2. In `tool_use_agent.py`, wherever an AI client is created (e.g. `anthropic.Anthropic(api_key=...)`), replace with `resolve_api_key(user_id, 'anthropic')`.
3. For AssemblyAI: find where its client is initialised and replace the env-var read with `resolve_api_key(user_id, 'assemblyai')`.
4. For OpenAI embeddings: find `openai.api_key = ...` or `OpenAI(api_key=...)` and apply the same pattern.
5. Test by storing a *different* key in the org vault and confirming AI calls fail (key is intentionally wrong) — this proves the vault key is actually being used.  
**Verification Checkpoint:** Store a deliberately invalid Anthropic key in org 2's vault. Log in as org 2 user. Send a message. Anthropic returns 401 (key invalid) — proves the vault key is being consumed, not the env var.  
**Dependencies:** GAP-C3 must be done first.

---

#### GAP-H3: `embedding_vector` Column Is Always NULL — Semantic Search Dead (HIGH)
**Status:** ✅ **FIXED** (Session 5) — `generate_embedding()` updated with org vault key resolution; `message_manager.py` passes `user_id`.  
**Affected Files:** `tools/implementations/conversation_memory.py`, `AI_infrastructure/threads/message_manager.py`  
**Investigation Finding:** The actual AI chat messages table is `sessions.messages.content_embedding vector(1536)` (not `workspace_chats.messages`) — `message_manager.py` already called `generate_embedding()` but it used the global `openai.api_key = os.getenv('OPENAI_API_KEY')` set at module load, which is `None` on Render if the key is only in the org vault.  
**Fix Applied:**
1. Updated `generate_embedding(text, user_id=None)` in `conversation_memory.py` to resolve the API key from the org vault via `resolve_api_key(user_id, 'openai')` (same GAP-C3 pattern), with env var as fallback.
2. Updated `message_manager.py` `create_message()` to pass `user_id=message_data.user_id` to `generate_embedding()`.
3. `generate_embedding` raises `ValueError` (instead of silently returning None) if no key is available at all.  
**Note on `workspace_chats.messages.embedding_vector`:** This is a separate workspace collaboration table. No Python code currently inserts into `workspace_chats.messages`, so its `embedding_vector` column is structurally unused — the workspace search feature has not been enabled yet. That is a separate scope beyond this gap.  
**Verification Checkpoint:** Send 5 AI chat messages. Query: `SELECT COUNT(*) FROM sessions.messages WHERE content_embedding IS NOT NULL;` — must be > 0.  
2. After saving the message row, add an async embedding call:
   ```python
   import threading
   
   def _embed_message_async(message_id: int, content: str, user_id: int):
       """Run in background thread to avoid blocking chat response."""
       try:
           from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
           api_key = resolve_api_key(user_id, 'openai')
           client = openai.OpenAI(api_key=api_key)
           response = client.embeddings.create(model="text-embedding-3-small", input=content)
           embedding = response.data[0].embedding
           execute_query(
               "UPDATE workspace_chats.messages SET embedding_vector = %s WHERE id = %s",
               (embedding, message_id)
           )
       except Exception as e:
           logger.warning(f"[EMBED] Failed to embed message {message_id}: {e}")
   
   threading.Thread(target=_embed_message_async, args=(msg_id, content, user_id), daemon=True).start()
   ```
3. Verify the IVFFlat index. Note: IVFFlat requires ≥500 rows before the index is effective. Use `ivfflat` with `lists=1` until you have enough rows, then rebuild with `lists=100`.  
**Verification Checkpoint:** Send 5 messages. Query: `SELECT COUNT(*) FROM workspace_chats.messages WHERE embedding_vector IS NOT NULL;` — must be > 0. Then query: `SELECT content FROM workspace_chats.messages ORDER BY embedding_vector <=> '[...]'::vector LIMIT 3;` — must return semantically relevant results.  
**Dependencies:** GAP-C3 helpful but not required (can use env var for OpenAI key initially).

---

#### GAP-H4: Two Parallel Org UI Panels Out of Sync (HIGH)
**Status:** ✅ **FIXED** (Session 5) — Consolidated using DOM-move pattern.  
**Affected Files:** `UI/business-ai-platform-v2.html`, `UI/modules_internal/components/account_profile.js`  
**Fix Applied:**
1. Wrapped the org panel content inside `settings-tab-org` in a new `<div id="orgPanel">` container.
2. Replaced the 174-line `AccountSidebar.loadOrganisationTab(container)` with a delegating function that moves `#orgPanel` into the sidebar container and calls `window.loadOrgTab()` (the canonical `account_profile.js` loader).
3. `loadTabContent()` now restores `#orgPanel` back to `#settings-tab-org` before clearing the container, so the account-settings modal always has the org panel available.
4. Added **Vault** and **Audit** subtabs to `orgDashboard` (matching the old sidebar's Credentials Vault + Audit Log sections), driven by `OrgManager.loadCredentials()` / `OrgManager.loadAuditLog()`.
5. Updated `switchOrgSubTab()` to handle `vault` and `audit` cases with role-gating.
6. `loadOrgTab()` in `account_profile.js` now syncs `OrgManager._userRole`, `_userLevel`, `_orgInfo` after fetch so vault/audit subtabs know the user's permission level.
7. Fixed `createOrganisation()` post-create reload to call `window.loadOrgTab()` directly.

---

#### GAP-H5: `g.rls_organisation_id` Injection — Verify Working in Production (HIGH)
**Status:** ✅ **FIXED** (March 25, 2026) — Logging upgraded to INFO; now logs `role=authenticated` as part of GAP-C2 fix.  
**Affected Files:** `AI_infrastructure/auth/user_auth.py` (`require_auth` decorator), `AI_infrastructure/shared/rls_session_manager.py`, `AI_infrastructure/shared/database_utils.py`  
**Problem:** Session 3 implemented `rls_session_manager.py` and `inject_rls_vars(conn)`. However the service_role key bypass (GAP-C2) means RLS policies are never evaluated regardless. Additionally, there is a risk that `inject_rls_vars` is called but `g.rls_organisation_id` is `None` for requests that don't go through `require_auth` (unauthenticated endpoints, background tasks).  
**Fix Steps:**
1. Add a log line in `inject_rls_vars()`: `logger.debug(f"[RLS] Setting org={org_id}, user={user_id}")`.
2. Make a test request and confirm the log appears.
3. Add a guard: if `org_id` is None, `set_config` should NOT be called (avoids setting empty string which could accidentally match).
4. After fixing GAP-C2 (anon role), run the RLS test: org 2 user must get 0 rows from org 1's credentials table.  
**Verification Checkpoint:** Make a `GET /api/org/credentials` request as org 2 user. Check DB query log — must show `set_config('app.current_organisation_id', '2', true)` was executed. The result must not contain any org 1 rows.  
**Dependencies:** GAP-C2 must be fixed for this to have any effect.

---

#### GAP-M1: No `org_module_access` Table — No Feature Gating (MEDIUM)
**Status:** `[ ]` Not Started  
**Affected Files:** `AI_infrastructure/migrations/` (new migration needed), `tools/registry_v3.py`, `AI_infrastructure/core/tool_use_agent.py`  
**Problem:** `organisations.plan_tier` column exists (`starter`, `professional`, `enterprise`) but there are no tables defining which modules/tools each plan can access. Every org can use every tool regardless of plan. There is no per-org tool filtering in `ToolUseAgent`.  
**Fix Steps:**
1. Create migration `026_org_module_access.sql`:
   ```sql
   CREATE TABLE ai_infrastructure.org_module_access (
       id SERIAL PRIMARY KEY,
       organisation_id INTEGER NOT NULL REFERENCES ai_infrastructure.organisations(id) ON DELETE CASCADE,
       module_name VARCHAR(100) NOT NULL,  -- e.g. 'shopify', 'xero', 'inhouse_print'
       is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
       enabled_at TIMESTAMPTZ DEFAULT NOW(),
       enabled_by INTEGER REFERENCES ai_infrastructure.users(id),
       UNIQUE(organisation_id, module_name)
   );
   
   -- Default access table by plan tier
   CREATE TABLE ai_infrastructure.plan_modules (
       plan_tier VARCHAR(50) NOT NULL,  -- 'starter', 'professional', 'enterprise'
       module_name VARCHAR(100) NOT NULL,
       PRIMARY KEY (plan_tier, module_name)
   );
   
   -- Seed defaults
   INSERT INTO ai_infrastructure.plan_modules VALUES
       ('starter', 'core_chat'), ('starter', 'documents'),
       ('professional', 'core_chat'), ('professional', 'documents'),
       ('professional', 'shopify'), ('professional', 'xero'),
       ('enterprise', 'core_chat'), ('enterprise', 'documents'),
       ('enterprise', 'shopify'), ('enterprise', 'xero'),
       ('enterprise', 'inhouse_print'), ('enterprise', 'quote_calculator');
   ```
2. In `ToolUseAgent` (or `registry_v3.py`), before building the tools list, filter by org's enabled modules:
   ```python
   enabled_modules = get_org_enabled_modules(organisation_id)  # query the table
   tools = [t for t in all_tools if t.get('platform') in enabled_modules]
   ```  
**Verification Checkpoint:** Set org 2 to `starter` plan. `ToolUseAgent` for org 2 user must not include `shopify` or `xero` tools in its tool list.  
**Dependencies:** None.

---

#### GAP-M2: `organisation_id` Missing from Conversations/Threads (MEDIUM)
**Status:** `[x]` FIXED — Phase 6b. Migration `029_org_id_on_threads.sql` run in Supabase (March 25, 2026).  
**Fix Applied:** `sessions.threads.organisation_id` column added + backfill trigger + index. Auto-fills from `users.organisation_id` on every new INSERT.  
**Affected Files:** `AI_infrastructure/migrations/029_org_id_on_threads.sql`  
**Original Problem:** The conversations/threads tables did not have an `organisation_id` column. If an org admin wants to see all team conversations, or if conversation history needs to be isolated by org (so org 2 can't read org 1's chats), the org FK must exist on the conversations table.  
**Fix Steps:**
1. Run: `SELECT column_name FROM information_schema.columns WHERE table_name = 'conversations';` — check if `organisation_id` exists.
2. If missing, add it: `ALTER TABLE workspace_chats.conversations ADD COLUMN organisation_id INTEGER REFERENCES ai_infrastructure.organisations(id);`
3. Backfill from user: `UPDATE workspace_chats.conversations c SET organisation_id = u.organisation_id FROM ai_infrastructure.users u WHERE c.user_id = u.id;`
4. Add RLS policy: conversations only visible if `organisation_id = current_setting(...)::int`.  
**Verification Checkpoint:** A DB query for conversations by org 2 user must return only org 2's conversations.  
**Dependencies:** GAP-C2 (service_role bypass must be fixed for RLS to matter).

---

#### GAP-M3: No Per-Org AI Provider / Model Selection (MEDIUM)
**Status:** `[x]` FIXED — Phase 7. Migration `031_org_ai_provider_model.sql` created (run in Supabase required). March 25, 2026.  
**Affected Files:** `AI_infrastructure/migrations/031_org_ai_provider_model.sql` (⚠️ NOT YET RUN), `AI_infrastructure/core/unified_ai_client.py`, `AI_infrastructure/shared/org_credentials_loader.py`, `AI_infrastructure/flask_app.py`, `AI_infrastructure/routes/organisation_credentials_routes.py`, `UI/business-ai-platform-v2.html`, `UI/modules_internal/components/account_profile.js`  
**Fix Applied:**
1. Migration `031_org_ai_provider_model.sql` — adds `ai_provider VARCHAR(50)`, `ai_model VARCHAR(100)`, `ai_max_tokens INTEGER` to `organisations` with CHECK constraints.
2. `get_org_ai_config(user_id)` in `org_credentials_loader.py` — 3-tier lookup: org config → provider default → hardcoded default. Falls back gracefully if migration not run.
3. `unified_ai_client.py` — `process_streaming()` + all `_process_*` methods accept `org_model: Optional[str] = None` and use it if set.
4. `flask_app.py` — resolves org AI config before background thread; passes `_resolved_provider` + `_org_model_override` to `process_streaming()`.
5. `GET /api/org/info` — returns `ai_provider`, `ai_model`, `ai_max_tokens`.
6. `PUT /api/org/info` — accepts and validates `ai_provider` (enum check), `ai_model` (string), `ai_max_tokens` (int 1024-32768).
7. Org overview form — `#editOrgAiProvider` select + `#editOrgAiModel` input added.
8. `account_profile.js` — `_renderOrgDashboard()` populates fields; `saveOrgSettings()` sends them.  
**Verification Checkpoint:** Set org 2's provider to `openai` and model to `gpt-4o`. Send a chat message as org 2 user. Check OpenAI usage dashboard — request must appear there, not in Anthropic.  
**Dependencies:** GAP-C3 must be done first.

---

#### GAP-M4: Xero/Shopify Cache Uses `business_id` — Not Linked to `organisations` (MEDIUM)
**Status:** `[ ]` Needs Investigation  
**Affected Files:** `UI/modules_external/shopify/`, `UI/modules_external/xero/`, `AI_infrastructure/migrations/`  
**Problem:** Xero and Shopify caches / integration tables may use a `business_id` column that is not a FK to `ai_infrastructure.organisations`. If a different org logs in, there is no guarantee their cached Shopify/Xero data is isolated from another org's data.  
**Fix Steps:**
1. Find all Shopify/Xero DB tables: search migrations for `CREATE TABLE` containing `shopify` or `xero`.
2. Check if they have `organisation_id` or only `user_id` / `business_id`.
3. If `business_id` is used and it's not linked to `organisations.id`, add an `organisation_id` column and FK.
4. Add RLS policies to these tables.  
**Verification Checkpoint:** Two orgs with different Shopify stores — each sees only their own products in the Shopify tool.  
**Dependencies:** None.

---

#### GAP-M5: Platform Name in Vault Is Free-Text — Typo Breaks Matching (MEDIUM)
**Status:** ✅ **FIXED** (March 25, 2026)  
**Affected Files:** `UI/business-ai-platform-v2.html` (org credentials add form), `AI_infrastructure/routes/organisation_credentials_routes.py`  
**Problem:** When adding a credential to the vault, the platform name is a free-text input. A user typing `"Anthropic"` vs `"anthropic"` vs `"anthropic_api"` will never match what `resolve_api_key(user_id, 'anthropic')` queries. The key is stored but silently never used.  
**Fix Steps:**
1. Change the add-credential form to use a `<select>` dropdown with standardised platform names:
   ```html
   <select id="new-cred-platform">
       <option value="anthropic">Anthropic (Claude)</option>
       <option value="openai">OpenAI (GPT)</option>
       <option value="assemblyai">AssemblyAI</option>
       <option value="pinecone">Pinecone</option>
       <option value="deepseek">DeepSeek</option>
       <option value="shopify">Shopify</option>
       <option value="xero">Xero</option>
       <option value="sendgrid">SendGrid</option>
       <option value="twilio">Twilio</option>
   </select>
   ```
2. In `organisation_credentials_routes.py`, validate `platform` on the backend against the allowed list:
   ```python
   ALLOWED_PLATFORMS = {'anthropic', 'openai', 'assemblyai', 'pinecone', 'deepseek', 'shopify', 'xero', 'sendgrid', 'twilio', 'auspost', 'stripe'}
   if platform not in ALLOWED_PLATFORMS:
       return jsonify({'error': f'Unknown platform: {platform}'}), 400
   ```
3. Add a DB check constraint on `organisation_platform_credentials.platform` (or at minimum a CHECK with a comment noting the allowed values).  
**Verification Checkpoint:** Try adding a credential with platform `"Anthropic"` (capital A) — backend returns 400. Add `"anthropic"` (lowercase) — succeeds and matches `resolve_api_key(user_id, 'anthropic')`.  
**Dependencies:** None.

---

#### GAP-M6: No `organisations.allowed_domains` for SSO Auto-Provisioning (MEDIUM)
**Status:** `[x]` FIXED — Phase 6d. Migration `030_allowed_domains_for_sso.sql` run in Supabase (March 25, 2026).  
**Affected Files:** `AI_infrastructure/migrations/030_allowed_domains_for_sso.sql` (run ✅), `AI_infrastructure/routes/google_auth_routes_V2_FIXED.py`, `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py`, `AI_infrastructure/routes/organisation_credentials_routes.py`, `UI/business-ai-platform-v2.html`, `UI/modules_internal/components/account_profile.js`  
**Fix Applied:**  
1. Migration `030_allowed_domains_for_sso.sql` — adds `allowed_domains TEXT[]` to `organisations` + GIN index (NOT YET RUN in Supabase)
2. `_auto_assign_org_by_domain(user_id, email)` helper added to both Google and Microsoft OAuth callback files. Called after new user creation only — existing users unaffected.
3. `PUT /api/org/info` updated to accept and validate `allowed_domains` array; `GET /api/org/info` returns it.  
4. Org overview form in `business-ai-platform-v2.html` adds `#editOrgAllowedDomains` input field.  
5. `saveOrgSettings()` / `_renderOrgDashboard()` in `account_profile.js` read/write `allowed_domains`.  
**Verification Checkpoint:** Add `"testcorp.com"` to org 2's allowed_domains. Sign in with Google using a `@testcorp.com` email — user is automatically assigned to org 2 with `member` role.  
**Dependencies:** GAP-H1 (org settings save) useful but not required.

---

#### GAP-L1: JWT Lacks `plan_tier` / `org_name` — Extra DB Hit per Request (LOW)
**Status:** `[ ]` Not Started  
**Affected Files:** `AI_infrastructure/auth/user_auth.py`  
**Problem:** `plan_tier` and `org_name` are not in the JWT payload. Any code that needs the plan tier must query the DB. This adds latency on every tool call that checks feature access.  
**Fix Steps:**
1. In `user_auth.py` login function, add `plan_tier` to JWT payload (it's already in the organisations row returned by the JOIN):
   ```python
   jwt_payload = {
       'user_id': user['id'],
       'org_id': user['organisation_id'],
       'org_role': user['org_role'],
       'org_name': user.get('org_name', ''),
       'plan_tier': user.get('plan_tier', 'starter'),  # ADD THIS
       'jwt_version': user.get('jwt_version', 1),      # ADD THIS (for GAP-C4)
   }
   ```
2. In `require_auth` decorator, extract `plan_tier` from JWT into `g.plan_tier`.  
**Verification Checkpoint:** After login, decode JWT — must contain `plan_tier` field.  
**Dependencies:** GAP-C4 implementation (adding `jwt_version`).

---

#### GAP-L2: Key Rotation Reminders Never Fired (LOW)
**Status:** `[ ]` Not Started  
**Affected Files:** `AI_infrastructure/routes/organisation_credentials_routes.py`, `AI_infrastructure/migrations/`  
**Problem:** `organisation_platform_credentials` has a `rotation_due_at` column but nothing reads it or sends reminders. Keys are never flagged as overdue.  
**Fix Steps:**
1. Add a background scheduled task (use APScheduler if already in use, or Render cron job) that runs daily:
   ```python
   def check_key_rotation():
       overdue = execute_query(
           "SELECT oc.id, oc.platform, o.name as org_name, u.email FROM ai_infrastructure.organisation_platform_credentials oc "
           "JOIN ai_infrastructure.organisations o ON o.id = oc.organisation_id "
           "JOIN ai_infrastructure.users u ON u.organisation_id = o.id AND u.org_role = 'owner' "
           "WHERE oc.rotation_due_at < NOW() AND oc.deleted_at IS NULL",
           fetch_mode='all'
       )
       for row in overdue:
           # Send email to org owner
           send_email(row['email'], f"API key rotation overdue for {row['platform']} in {row['org_name']}")
   ```
2. Add a banner in the org credentials UI for overdue keys.  
**Verification Checkpoint:** Set `rotation_due_at` to yesterday for a test credential. Run the cron job. Owner receives an email notification.  
**Dependencies:** Email delivery must be configured (SendGrid/Resend).

---

#### GAP-L3: No "Test Connection" for Vault Credentials (LOW)
**Status:** `[ ]` Not Started  
**Affected Files:** `AI_infrastructure/routes/organisation_credentials_routes.py`, `UI/business-ai-platform-v2.html`  
**Problem:** After adding an API key to the vault, there is no way to verify it works without triggering a real AI call. A typo in the key is only discovered during actual usage.  
**Fix Steps:**
1. Add `POST /api/org/credentials/:id/test` endpoint:
   ```python
   @org_credentials_bp.route('/credentials/<int:cred_id>/test', methods=['POST'])
   @require_org_role('manager')
   def test_credential(cred_id):
       cred = get_credential_plaintext(cred_id, g.rls_organisation_id)  # existing reveal logic
       platform = cred['platform']
       if platform == 'anthropic':
           result = test_anthropic_key(cred['credential_value'])
       elif platform == 'openai':
           result = test_openai_key(cred['credential_value'])
       # etc.
       return jsonify({'success': result['ok'], 'message': result['message']})
   ```
2. Add a "Test" button in the credentials table in the UI (visible to admin/owner).  
**Verification Checkpoint:** Add a valid Anthropic key and click Test — returns `{"success": true}`. Add an invalid key and click Test — returns `{"success": false, "message": "Invalid API key"}`.  
**Dependencies:** Vault reveal logic (already built).

---

#### GAP-L4: `realtime_messages` Has No Org Scoping (LOW)
**Status:** `[ ]` Needs Investigation  
**Affected Files:** `AI_infrastructure/migrations/`, Supabase realtime settings  
**Problem:** If a `realtime_messages` table (or channel) is used for live chat updates, it may broadcast to all connected clients regardless of org. An org 2 user could receive org 1's real-time messages.  
**Fix Steps:**
1. Check if a `realtime_messages` table exists and how Supabase Realtime is subscribed in the frontend.
2. If using row-level Supabase realtime subscriptions, add `filter: 'organisation_id=eq.{org_id}'` to the subscription.
3. Add RLS policy on the table if not already present.  
**Verification Checkpoint:** Two browser tabs logged into different orgs both open. A message sent in org 1 must not appear in org 2's real-time feed.  
**Dependencies:** GAP-C2 (RLS must work first).

---

#### GAP-L5: DeepSeek Env-Var Only — No DB Lookup (LOW)
**Status:** `[ ]` Not Started  
**Affected Files:** `AI_infrastructure/core/unified_ai_client.py`  
**Problem:** DeepSeek API key is only read from `os.getenv('DEEPSEEK_API_KEY')`. There is no path for storing a DeepSeek key in the org vault and having it resolved via `resolve_api_key`.  
**Fix Steps:**
1. In `org_credentials_loader.py`, ensure `platform='deepseek'` is handled (it should already work generically — just needs verification).
2. Add `deepseek` to the allowed platforms list (GAP-M5).
3. In `UnifiedAIClient.call_deepseek()` (after GAP-C3 fix), use `resolve_api_key(user_id, 'deepseek')` instead of `os.getenv`.  
**Verification Checkpoint:** Store a DeepSeek key in org vault with platform `deepseek`. Route a DeepSeek request as that org's user. Confirm `os.getenv` fallback is NOT hit (add a log line to verify).  
**Dependencies:** GAP-C3, GAP-M5.

---

#### GAP-L6: `is_sub_user` Referenced in UI but Not in DB Schema (LOW)
**Status:** ✅ **VERIFIED FIXED** (Session 5) — Column exists via `team_id_management_migration.sql` (line 70: `ADD COLUMN is_sub_user BOOLEAN DEFAULT FALSE` with `IF NOT EXISTS` guard). Index also created (`idx_users_is_sub_user`).  
**Affected Files:** `UI/business-ai-platform-v2.html` (`applyOrgRoleVisibility()`), `AI_infrastructure/migrations/`  
**Problem:** `applyOrgRoleVisibility()` checks for `is_sub_user` in the user data but this column may not exist on the `users` table. If it exists only in the JWT payload without a DB column, it can be forged.  
**Fix Steps:**
1. Check: `SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'is_sub_user';`
2. If missing, add it: `ALTER TABLE ai_infrastructure.users ADD COLUMN is_sub_user BOOLEAN DEFAULT FALSE;`
3. In `require_auth`, read `is_sub_user` from DB (not JWT) so it can't be forged.
4. Define what sub-user restrictions mean (which tools/tabs are hidden).  
**Verification Checkpoint:** Set a user's `is_sub_user = true`. Reload the app — restricted tabs/features must be hidden.  
**Dependencies:** None.

---

#### GAP-L7: Credential Encryption at Rest (LOW — Future Hardening)
**Status:** `[ ]` Not Started  
**Affected Files:** `AI_infrastructure/routes/organisation_credentials_routes.py`, `AI_infrastructure/migrations/`  
**Problem:** API keys are stored as plain text in `organisation_platform_credentials.credential_value`. A DB dump, SQL injection attack, or Supabase misconfiguration exposes all keys.  
**Fix Steps:**
1. Use application-layer AES-256-GCM encryption:
   ```python
   from cryptography.fernet import Fernet
   
   ENCRYPTION_KEY = os.environ['CREDENTIAL_ENCRYPTION_KEY']  # 32-byte key, store in env
   f = Fernet(ENCRYPTION_KEY)
   
   def encrypt_credential(plaintext: str) -> str:
       return f.encrypt(plaintext.encode()).decode()
   
   def decrypt_credential(ciphertext: str) -> str:
       return f.decrypt(ciphertext.encode()).decode()
   ```
2. On save: encrypt before INSERT.
3. On retrieve (for actual use, not masking): decrypt after SELECT.
4. Run a migration to encrypt existing plaintext values.  
**Verification Checkpoint:** Query `organisation_platform_credentials.credential_value` directly in Supabase SQL editor — must show encrypted ciphertext, not the actual API key.  
**Dependencies:** None — but do this AFTER the system is working correctly (easier to debug unencrypted first).

---

### Priority Matrix

| Priority | Gap | Impact |
|----------|-----|--------|
| ✅ FIXED | GAP-C2: service_role bypasses RLS | SET LOCAL ROLE authenticated + migration 028 |
| ✅ FIXED | GAP-C1: Pinecone empty namespace | Namespace = `org_{id}` per request |
| ✅ FIXED | GAP-C3: UnifiedAIClient user_id=1 | Per-request resolve_api_key() for all 3 providers |
| ✅ FIXED | GAP-C4: JWT stale on role change | jwt_version counter — migration 026 run |
| ✅ FIXED | GAP-H2: Vault storage-only, never consumed | AssemblyAI + UnifiedAIClient wired |
| ✅ FIXED | GAP-H3: embedding_vector always NULL | `generate_embedding()` now resolves org vault key; `message_manager.py` passes user_id |
| ✅ FIXED | GAP-H1: saveOrgSettings() undefined | PUT /api/org/info expanded + migration 027 |
| ✅ FIXED | GAP-H4: Two parallel org UIs | Consolidated via DOM-move + Vault/Audit subtabs added |
| ✅ FIXED | GAP-H5: Verify RLS injection working | INFO logging + role=authenticated confirmed |
| ✅ FIXED | GAP-M5: Platform name free-text | ALLOWED_PLATFORMS validation + dropdown |
| 🟡 MEDIUM | GAP-M1: No org_module_access table | No feature gating by plan |
| 🟡 MEDIUM | GAP-M3: No per-org AI provider/model | All orgs use same model |
| ✅ FIXED  | GAP-M2: Conversations missing org FK | sessions.threads.organisation_id + trigger (029) |
| 🟡 MEDIUM | GAP-M4: Shopify/Xero not org-isolated | Integration data leakage |
| ✅ FIXED  | GAP-M6: No allowed_domains for SSO | OAuth users not auto-provisioned |
| 🟢 LOW | GAP-L1: JWT missing plan_tier | Extra DB hit per request |
| 🟢 LOW | GAP-L2: Key rotation reminders unused | Silent stale keys |
| 🟢 LOW | GAP-L3: No Test Connection button | UX gap |
| 🟢 LOW | GAP-L4: realtime_messages not scoped | Possible real-time leakage |
| 🟢 LOW | GAP-L5: DeepSeek env-var only | DeepSeek not vault-compatible |
| ✅ FIXED | GAP-L6: is_sub_user not in DB | Column confirmed in team_id_management_migration.sql |
| 🟢 LOW | GAP-L7: Credentials plain text at rest | Future hardening |

---

### Systematic Build Order

Work through the phases in sequence. Each phase builds on the previous. Complete the checkpoint before starting the next phase.

---

#### Phase 1 — Foundation Security (CRITICAL data leakage)
**Goal:** Prevent cross-org data exposure at the DB and vector layer.

- `[x]` **1a.** Fix GAP-C1: Add `org_{id}` namespace enforcement in `pinecone_tools.py` ✅
- `[x]` **1b.** Fix GAP-C2: `SET LOCAL ROLE authenticated` in `inject_rls_vars()` + migration `028_grant_authenticated_role.sql` ✅
- `[x]` **1c.** Verify GAP-H5: `inject_rls_vars()` now logs at INFO level, shows `role=authenticated` ✅
- `[ ]` **1d.** Run RLS test: org 2 user sees 0 rows from org 1's credentials table ⬅ still needs manual verification

**Phase 1 Checkpoint:** Two users in different orgs. Neither can read the other's vault credentials, vectors, or conversations via raw DB access.

---

#### Phase 2 — AI Engine Wiring (CRITICAL wrong billing, HIGH broken vault)
**Goal:** Make the org credential vault actually drive AI calls.

- `[x]` **2a.** Fix GAP-C3: Per-request `resolve_api_key()` in `_process_anthropic/deepseek/openai/create_message()` ✅
- `[x]` **2b.** Fix GAP-H2: `resolve_api_key` wired into AssemblyAI; GAP-C3 covers UnifiedAIClient ✅
- `[ ]` **2c.** Fix GAP-L5: Wire DeepSeek into `resolve_api_key` path ⬅ still to do
- `[x]` **2d.** Fix GAP-M5: `ALLOWED_PLATFORMS` validation on backend; dropdown in UI ✅

**Phase 2 Checkpoint:** Store a deliberately invalid Anthropic key in org 2's vault. Org 2 user sends a message — gets Anthropic 401 error (proves vault key is used, not env var). Org 1 user (with valid key) still works normally.

---

#### Phase 3 — Auth Hardening (CRITICAL stale permissions)
**Goal:** JWT role changes take effect immediately.

- `[x]` **3a.** Fix GAP-C4: Migration `026`, login embeds version, require_auth checks DB, role-change/remove increments ✅
- `[ ]` **3b.** Fix GAP-L1: Add `plan_tier` to JWT payload ⬅ still to do (`jwt_version` already added)
- `[x]` **3c.** Update `require_auth` to check `jwt_version` against DB ✅

**Phase 3 Checkpoint:** Log in as admin. In DB, demote to member AND increment `jwt_version`. Make an API request with old token — must get 401. Log in again — new token has `org_role: 'member'`.

---

#### Phase 4 — UI Fixes (HIGH broken functionality)
**Goal:** Remove broken UI elements and consolidate org management.

- `[x]` **4a.** Fix GAP-H1: `saveOrgSettings()` existed in `account_profile.js`; expanded `PUT /api/org/info` + migration `027_org_description_visibility.sql` ✅
- `[x]` **4b.** Fix GAP-H4: Consolidated via DOM-move pattern; Vault + Audit subtabs added to `orgDashboard`; `account_profile.js` syncs `OrgManager` role state ✅
- `[x]` **4c.** Fix GAP-L6: `is_sub_user` confirmed in `team_id_management_migration.sql` (ADD COLUMN IF NOT EXISTS) ✅

**Phase 4 Checkpoint:** Every button in the org management UI functions without console errors. No `ReferenceError` on any click.

---

#### Phase 5 — Message Embeddings (HIGH semantic search)
**Goal:** Populate `embedding_vector` for all new messages and enable semantic search.

- `[x]` **5a.** Fix GAP-H3: `generate_embedding()` in `conversation_memory.py` updated to accept `user_id` and resolve from org vault (GAP-C3 pattern); `message_manager.py` passes `user_id` ✅
- `[ ]` **5b.** Test: Send 10 messages, confirm `content_embedding IS NOT NULL` in `sessions.messages` for all
- `[ ]` **5c.** Test semantic search: `conversation_memory` tool query returns semantically relevant results

**Phase 5 Checkpoint:** `SELECT COUNT(*) FROM sessions.messages WHERE content_embedding IS NOT NULL` returns > 0. Semantic search over chat history returns relevant results.

---

#### Phase 6 — Org Scoping Completeness (MEDIUM multi-tenancy)
**Goal:** Ensure all data tables are org-isolated.

- `[ ]` **6a.** Fix GAP-M2: Add `organisation_id` to conversations table + RLS policy
- `[ ]` **6b.** Fix GAP-M4: Audit Shopify/Xero tables, add org FK if missing
- `[ ]` **6c.** Fix GAP-L4: Add org filter to realtime subscriptions
- `[x]` **6d.** Fix GAP-M6: Add `allowed_domains` column + OAuth auto-provisioning ✅

**Phase 6 Checkpoint:** Two orgs, each with their own Shopify store connected. Each org's user sees only their store's products. Chat history from org 1 not visible to org 2 user.

---

#### Phase 7 — Per-Org AI Configuration (MEDIUM feature differentiation)
**Goal:** Each org can choose their AI provider and model.

- `[ ]` **7a.** Fix GAP-M3: Add `ai_provider`, `ai_model` columns to organisations table
- `[ ]` **7b.** Update `UnifiedAIClient` to read org's preferred provider
- `[ ]` **7c.** Add provider/model selector in org settings UI (owner/admin only)

**Phase 7 Checkpoint:** Org 2 set to use OpenAI/gpt-4o. Chat message from org 2 user appears in OpenAI usage dashboard, not Anthropic.

---

#### Phase 8 — Feature Gating (MEDIUM plan enforcement)
**Goal:** Plan tier controls which modules are accessible.

- `[ ]` **8a.** Fix GAP-M1: Create migration `026_org_module_access.sql` with `org_module_access` + `plan_modules` tables
- `[ ]` **8b.** Seed plan modules with starter/professional/enterprise defaults
- `[ ]` **8c.** Wire module access check into `ToolUseAgent` tool list building
- `[ ]` **8d.** Wire module access check into frontend module loading

**Phase 8 Checkpoint:** Org with `starter` plan — `ToolUseAgent` tool list excludes Shopify and Xero tools. Org with `enterprise` plan — all tools available.

---

#### Phase 9 — Polish & Hardening (LOW)
**Goal:** Security hardening and operational improvements.

- `[ ]` **9a.** Fix GAP-L2: Add scheduled key rotation reminder (APScheduler/cron)
- `[ ]` **9b.** Fix GAP-L3: Add "Test Connection" button + `POST /api/org/credentials/:id/test` endpoint
- `[ ]` **9c.** Fix GAP-L7: Implement AES-256-GCM encryption for credential values at rest
- `[ ]` **9d.** Add `deepseek` to vault UI platform dropdown (from GAP-M5 work)

**Phase 9 Checkpoint:** Test Connection returns success/failure without triggering a real chat. DB dump of `credential_value` column shows encrypted ciphertext, not plaintext API keys.

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

---

## Changelog & TODO

### Last Updated: March 28, 2026

#### Recent Changes
- ✅ **March 28** — Consolidated to 3 core documents; removed duplicate analysis files
- ✅ **March 28** — Added "Module Visibility & Credential Requirements" section
- ✅ **March 28** — Added "Organisation Table Schema" reference section
- ✅ **March 28** — Added cross-references to MODULE_VISIBILITY_ARCHITECTURE.md and ORG_DOCUMENTATION
- ✅ **March 26** — Complete multi-tenant architecture with credential vault and RLS policies

#### TODO (By Priority)

**HIGH PRIORITY — Block Implementation:**
- [ ] **GAP-C2** — Fix `service_role` bypass so RLS policies actually enforce (currently all queries bypass RLS)
- [ ] **GAP-C4** — Add `jwt_version` to JWT + `@require_auth` decorator to invalidate tokens on role change

**MEDIUM PRIORITY — Feature Gating:**
- [ ] **GAP-M1** — Create `org_module_access` + `plan_modules` tables for plan-tier feature gating
- [ ] **GAP-M2** — Add `organisation_id` FK to conversations/threads (migration applied, needs verification in code)

**MEDIUM PRIORITY — Sub-User System:**
- [ ] **GAP-E2** — Implement sub-user role restrictions (child accounts can't promote themselves above parent's role)
- [ ] **GAP-E3** — Implement sub-user credential vault access (only see parent's credentials, read-only)

**LOW PRIORITY — Polish & Hardening:**
- [ ] **GAP-L2** — Add scheduled key rotation reminders (APScheduler + email notification)
- [ ] **GAP-L3** — Add "Test Connection" button for vault credentials
- [ ] **GAP-L4** — Add AES-256-GCM encryption at rest for credential values

#### Related Files (Keep These 3 as Source of Truth)
- `../MODULE_VISIBILITY_ARCHITECTURE.md` — Module visibility model, sidebar gating, 4-layer framework
- `../ORG_DOCUMENTATION_AND_UI_ALIGNMENT_SUMMARY_MAR28_2026.md` — Organisation table schema, UI forms, API endpoints
- This file — Credentials, vault, multi-tenancy, RLS, role hierarchy, sub-user system
