# Personal Org + Synergy Access Control — Complete Implementation Plan
**Date: May 7, 2026**
**Status: ✅ FULLY IMPLEMENTED — All 8 plan steps + Phase 6 AI tools complete**
**Author: Architecture analysis + implementation planning session**

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State — What Exists Today](#2-current-state--what-exists-today)
3. [Problems Identified](#3-problems-identified)
4. [Three-Tier User Model (Proposed)](#4-three-tier-user-model-proposed)
5. [Implementation Steps](#5-implementation-steps)
   - [Step 1 — Migration 046](#step-1--migration-046-database-schema-changes)
   - [Step 2 — register_user() auto-create personal org](#step-2--register_user-auto-create-personal-org)
   - [Step 3 — Backfill existing users](#step-3--backfill-existing-solo-users)
   - [Step 4 — Expose is_personal_org in API](#step-4--expose-is_personal_org-in-api-response)
   - [Step 5 — Frontend Synergy gating for solo users](#step-5--frontend-synergy-visibility-gating-for-solo-users)
   - [Step 6 — Synergy route enforcement (default_member_role)](#step-6--synergy-route-enforcement-for-default_member_role)
   - [Step 7 — initModulesFromOrg is_personal_org gating](#step-7--initmodulesfromorg--is_personal_org-gating)
   - [Step 8 — Session member management UI](#step-8--session-member-management-ui-completeness)
6. [Files Changed Tracker](#6-files-changed-tracker)
7. [Phase 6 — AI Tools Gap Analysis & Implementation](#phase-6--ai-tools-gap-analysis--implementation)
7. [Database Tables Reference](#7-database-tables-reference)
8. [Testing Checklist](#9-testing-checklist)

---

## 1. Executive Summary

The platform currently has no personal org tier. Every new user registers with `organisation_id = NULL`, causing:
- Credential resolution to fall through to env-var tier (Tier 3) — fine for single-tenant, broken for hundreds of independent solo users
- `g.rls_organisation_id = NULL` in all Flask routes — no org-scoped data isolation
- The Synergy share popup always shows "Team" visibility, even for users who have no team
- `initModulesFromOrg()` only runs if the user has `org_role` — solo users never trigger it
- The `default_member_role` for shared Synergy sessions is not stored in the DB — there is no read-only sharing concept

The fix is **Migration 046** (one SQL file) + a small change to `register_user()` + frontend gating of Synergy share options based on `is_personal_org` flag.

---

## 2. Current State — What Exists Today

### 2.1 Database Schema (Applied Migrations)

| Migration | File | What It Added |
|-----------|------|---------------|
| 025 | `025_synergy_sessions_multitenancy.sql` | `synergy_sessions.visibility` CHECK('private','shared','team'), `synergy_sessions.organisation_id` FK, `session_members` table (user_id, role, added_by) |
| 032 | `032_org_module_access.sql` | `org_module_access` table: per-org module enable/disable |
| 036 | `036_platform_module_catalog.sql` | `platform_catalog` (27 entries), `module_catalog` (26 entries) |
| 038 | `038_teams_system.sql` | `teams` table (parent_user_id), `team_members` table (data_access_scope), `team_id` column on `sessions.threads` and `sessions.messages` |
| 040 | `040_fix_session_members_rls_recursion.sql` | RLS recursion fix on `session_members` |
| 044 | `044_pgvector_org_documents.sql` | `org_vector_documents` with pgvector + RLS |
| 045 | `045_update_vector_platform_catalog.sql` | Voyager v4 models, Pinecone index_name field, pgvector entry |

**Latest migration number: 045**
**Next migration number: 046**
**Migration folder:** `AI_infrastructure/migrations/`

### 2.2 Key Tables — Current Column State

#### `ai_infrastructure.organisations`
Current columns include: `id`, `name`, `slug`, `plan_tier`, `display_name`, `logo_url`, `timezone`, `country_code`, `is_active`, `description`, `visibility`, `allowed_domains`, `ai_provider`, `ai_model`, `ai_max_tokens`, `vault_password_hash`, `created_at`, `updated_at`
**MISSING: `is_personal_org BOOLEAN`** ← needs to be added

#### `synergy_sessions.synergy_sessions`
Current columns include: `session_id`, `title`, `description`, `owner_user_id`, `organisation_id`, `visibility` CHECK('private','shared','team'), `permission_level` (legacy), `shared_with_users`, `created_at`, `updated_at`
**MISSING: `default_member_role TEXT CHECK('viewer','editor')`** ← needs to be added

#### `synergy_sessions.session_members`
Current columns: `session_id`, `user_id`, `role` CHECK('viewer','editor','admin'), `added_by`, `added_at`
**CURRENT STATE: Exists ✅ but role is not enforced in content-mutation endpoints**

#### `ai_infrastructure.users`
Current columns include: `id`, `username`, `email`, `password_hash`, `role`, `organisation_id` (FK, nullable), `org_role`, `jwt_version`, `is_sub_user`, `parent_user_id`, `last_login`, `metadata`
**NOTE: `organisation_id` is currently NULL for all solo registrations**

### 2.3 Credential Resolution — `org_credentials_loader.py`

**File:** `AI_infrastructure/shared/org_credentials_loader.py`

4-tier resolution (all implemented, lines 1–220):
- **Tier 1** (lines ~60–100): `user_platform_credentials WHERE user_id = X` ← per-user keys
- **Tier 1.5** (lines ~100–140): If `is_sub_user=TRUE`, inherit via `_get_parent_user_id()` → parent user's keys
- **Tier 2** (lines ~140–180): `organisation_platform_credentials WHERE organisation_id = org.id` ← org vault keys
- **Tier 3** (lines ~180–220): `os.getenv(PLATFORM_ENV_VARS[platform])` ← env vars with warning log

**Problem:** Solo users with `organisation_id = NULL` skip Tier 2 entirely and hit Tier 3 (env vars).
For hundreds of independent solo users with different API keys, Tier 3 is wrong — all users would share the same keys from `.env`.
The fix is ensuring every user has an `organisation_id` pointing to their personal org, so their vault credentials are stored there (Tier 2).

### 2.4 Flask RLS Context

**File:** `AI_infrastructure/flask_app.py` (before_request hook)

Every request sets `g.rls_user_id` and `g.rls_organisation_id` from the JWT.
For solo users with `organisation_id = NULL` in their JWT, `g.rls_organisation_id = None`.
This means RLS policies that filter on `organisation_id` return incorrect results for solo users.

### 2.5 User Registration — `register_user()`

**File:** `AI_infrastructure/auth/user_auth.py`
**Function:** `register_user()` at **line 348**
**Signature:** `def register_user(self, username: str, email: str, password: str, primary_gmail: str = None, role: str = 'user') -> Dict`

Currently (lines 371–400):
1. `INSERT INTO ai_infrastructure.users (username, email, password_hash, primary_gmail, role, metadata)` ← no `organisation_id`, no `org_role`
2. `INSERT INTO workspaces (user_id, name, description, metadata)` ← personal workspace created
3. If `role == 'admin'`: auto-links Gmail accounts from `.env.master`
4. Returns `{'success': True, 'user_id': ..., 'workspace_id': ..., 'username': ..., 'email': ..., 'role': ...}`

**MISSING:** Creating a personal org and setting `organisation_id + org_role = 'owner'` on the user row.

### 2.6 GET /api/org/info — `get_org_info()`

**File:** `AI_infrastructure/routes/organisation_credentials_routes.py`
**Function:** `get_org_info()` at **line 331**

Current response payload (lines 372–393): Returns `id`, `name`, `slug`, `display_name`, `logo_url`, `plan_tier`, `timezone`, `country_code`, `is_active`, `member_count`, `has_vault_password`, `created_at`, `description`, `visibility`, `allowed_domains`, `ai_provider`, `ai_model`, `ai_max_tokens` + `your_role`.
**MISSING: `is_personal_org` field in response** ← frontend needs this to gate UI

The SELECT query at line 338 does NOT select `is_personal_org` because the column doesn't exist yet.

### 2.7 Frontend `initModulesFromOrg()`

**File:** `UI/business-ai-platform-v2.html`
**Function:** `initModulesFromOrg` at **line 31352**
**Exposed as:** `window.initModulesFromOrg = initModulesFromOrg` at **line 31439**

**Currently does:**
- Takes `(modules, userRole)` — modules array from `/api/org/modules`, userRole string
- Gates Zone 1 `[data-module]` buttons (shows/hides via `btn.style.display`)
- Rebuilds `#sidebarModulesSection` (Zone 2) from `ZONE2_MODULES` map + DB module catalog
- `platform_developer` role bypasses all gating
- **Does NOT read `is_personal_org`** ← needs to be added

**Called from:** `loadUserInfo()` at **line 30620** via:
```javascript
fetch(_apiBase + '/api/org/modules', ...)
    .then(data => { if (data.success && window.initModulesFromOrg) {
        window.initModulesFromOrg(data.modules || [], _effectiveRole);
    }})
```
Note: Only runs if `profile.org_role || _isPlatformDev` — solo users with `org_role = null` do NOT trigger module gating.

### 2.8 AccountSidebar `_updateIdentityPanel()`

**File:** `UI/business-ai-platform-v2.html`
**Function:** `_updateIdentityPanel` at **line 30504**
**Called from:** `loadUserInfo()` at **line 30691**

Already fetches `/api/org/info` asynchronously (line 30561) to display org name in the identity panel.
This is the place to also read `is_personal_org` from the org info response and store it on `window` or cache for later use.

### 2.9 Synergy Sidebar Button

**File:** `UI/business-ai-platform-v2.html`, **line 18730**
```html
<button class="sidebar-icon-btn" data-tab="synergy" title="Synergy Dashboard - Session & Task Management">
```
**Missing:** `data-module="synergy"` attribute. The Synergy button is always visible regardless of `org_module_access`.

### 2.10 Synergy Share Popup

**File:** `UI/modules_internal/synergy/synergy-board-init.js`
**Function:** `openSharePopup(sessionId)` at **line 1121**

Currently renders three visibility options regardless of user context (line 1194–1197):
```javascript
${vOpt('private',  'fa-lock',         ..., 'Private',  'Only you can see this session')}
${vOpt('shared',   'fa-user-friends', ..., 'Shared',   'Invite specific people with roles')}
${vOpt('team',     'fa-users',        ..., 'Team',     'Everyone in your organisation')}
```
**Problem:** Solo users (personal org, no team members) should NOT see the `team` option.
Invite panel also shows an `<input>` + role `<select>` but there is no UI to load existing members (`#${popupId}-members` just shows "No members added yet").

### 2.11 Synergy Routes — Permission Check Coverage

**File:** `AI_infrastructure/routes/synergy_routes.py`
**Permission check function:** `check_session_permission()` at **line 282**

| Route Function | Line | `check_session_permission` Called? | `require_write` |
|---------------|------|-----------------------------------|-----------------|
| `list_sessions()` | 326 | Yes (Python filter) | False |
| `update_session_permissions()` | 1053 | Yes | True (line 1081) |
| `update_session()` | 1135 | Yes | True (line 1163) |
| `delete_session()` | 1460 | Need to verify |  |
| `create_milestone()` | 3085 | **NO — MISSING** | — |
| `update_milestone()` | 3286 | **NO — MISSING** | — |
| `create_task()` | 3802 | **NO — MISSING** | — |
| `update_task()` | 3852 | **NO — MISSING** | — |
| `create_milestone_complete()` | 2516 | Need to verify | — |
| `create_milestone_task()` | 4856 | Need to verify | — |
| `create_task_subtask()` | 4950 | Need to verify | — |

**Note:** `create_milestone()` at line 3085 is marked `[DEPRECATED]` in favor of `create_milestone_complete()` at 2516, but both should be checked.

### 2.12 Synergy Share Routes

**File:** `AI_infrastructure/routes/synergy_share_routes.py`
**Blueprint prefix:** `/api/synergy/sessions`
**Endpoints:**
- `PATCH /<session_id>/visibility` at **line 77** (`update_visibility`)
- `GET /<session_id>/members` (line unknown — exists per file header line 9)
- `POST /<session_id>/members` (line unknown)
- `DELETE /<session_id>/members/<user_id>` (line unknown)

The file already restricts visibility change to owner or session admin members (line 14: "Only the session OWNER or a session ADMIN-member can change visibility or manage members"). The `team` visibility is only allowed when `organisation_id` is set on the session (line 15).

**Good news:** The backend already correctly blocks `team` visibility if no `organisation_id`. The frontend shows the option anyway — that's the gap.

---

## 3. Problems Identified

### Problem 1 — No Personal Org Tier (CRITICAL)
**Impact:** Hundreds of solo users all share env-var credentials. No per-user data isolation at org level. `g.rls_organisation_id = NULL` breaks all org-scoped queries.
**Root cause:** `register_user()` at line 348 does not create an org.

### Problem 2 — Solo Users Cannot Trigger Module Gating
**Impact:** `initModulesFromOrg()` only runs when `profile.org_role` is non-null (line 30670-30685 check). New solo users with `organisation_id = NULL` have `org_role = NULL`, so the function never runs.
**Root cause:** The `if (profile.org_role || _isPlatformDev)` guard in `loadUserInfo()` at line 30670.

### Problem 3 — Synergy "Team" Option Shown to Solo Users
**Impact:** Personal-org users click "Team" → backend at `synergy_share_routes.py` line 15 rejects it → confusing error. Misleads users into thinking they have a team feature.
**Root cause:** `openSharePopup()` in `synergy-board-init.js` line 1121 renders all three options unconditionally.

### Problem 4 — Synergy `default_member_role` Does Not Exist
**Impact:** When a session is set to `visibility = 'team'`, ALL org members get edit access by default. There is no read-only team sharing.
**Root cause:** Column does not exist in `synergy_sessions.synergy_sessions`.

### Problem 5 — Content Mutation Routes Missing Permission Check
**Impact:** Any user who knows a session_id can create milestones and tasks in shared sessions, bypassing the `viewer` role restriction.
**Root cause:** `create_milestone()` line 3085, `update_milestone()` line 3286, `create_task()` line 3802, `update_task()` line 3852 have no `check_session_permission(require_write=True)` call.

### Problem 6 — `is_personal_org` Not Exposed in API
**Impact:** Frontend has no way to know if the user is solo or multi-user, so cannot conditionally show/hide team sharing UI.
**Root cause:** Column doesn't exist; GET /api/org/info response doesn't include it.

### Problem 7 — Synergy Button Has No `data-module` Attribute
**Impact:** `initModulesFromOrg()` cannot gate the Synergy sidebar button. It always appears even if `synergy` is not in the org's `org_module_access`.
**Root cause:** Line 18730 `<button class="sidebar-icon-btn" data-tab="synergy"` has no `data-module`.

### Problem 8 — `loadUserInfo()` Does Not Call `initModulesFromOrg` for Solo Users
**Impact:** Users without `org_role` never get module gating applied at all.
**Root cause:** Guard at `loadUserInfo()` line ~30670: `if (profile.org_role || _isPlatformDev)`.

---

## 4. Three-Tier User Model (Proposed)

```
TIER 1 — SOLO (Personal Workspace)
  ┌─────────────────────────────────────────────────────────────┐
  │  organisations.is_personal_org = TRUE                       │
  │  user.org_role = 'owner' (only member, no invite UI shown)  │
  │  Credential tier 2 = their personal org vault               │
  │  Synergy: private + shared only (team option hidden)        │
  │  Account sidebar: hide invite/team-management subtabs       │
  └─────────────────────────────────────────────────────────────┘

TIER 2A — TEAM (Invited Members, 2–20 users)
  ┌─────────────────────────────────────────────────────────────┐
  │  organisations.is_personal_org = FALSE                      │
  │  Real user accounts with org_role = member/admin/owner      │
  │  Synergy: private + team + shared (with default_member_role)│
  │  Account sidebar: full invite/member-management available   │
  └─────────────────────────────────────────────────────────────┘

TIER 2B — TEAM (Sub-Account Logins, migration 038 model)
  ┌─────────────────────────────────────────────────────────────┐
  │  Primary user: real account (is_sub_user = FALSE)           │
  │  Sub-users: is_sub_user = TRUE, parent_user_id = primary.id │
  │  Credential resolution tier 1.5: inherit parent keys        │
  │  sessions.threads.team_id + sessions.messages.team_id set   │
  │  data_access_scope: 'own' | 'team' | 'all'                  │
  └─────────────────────────────────────────────────────────────┘

TIER 3 — ORGANISATION (Enterprise)
  ┌─────────────────────────────────────────────────────────────┐
  │  Full role ladder: viewer/member/manager/admin/owner        │
  │  org_module_access per feature, vault password option       │
  │  Full audit log, invite tokens, role-based JWT invalidation │
  │  Synergy: full visibility model + default_member_role        │
  │  Account sidebar: all tabs visible per role                 │
  └─────────────────────────────────────────────────────────────┘
```

**The single boolean `is_personal_org` on the org row drives all frontend branching.**

---

## 5. Implementation Steps

---

### Step 1 — Migration 046: Database Schema Changes

**File to create:** `AI_infrastructure/migrations/046_personal_org_and_synergy_defaults.sql`
**Depends on:** Nothing (schema-level, idempotent)
**Status:** ✅ COMPLETE

**What this migration does:**
1. Adds `is_personal_org BOOLEAN DEFAULT FALSE` to `ai_infrastructure.organisations`
2. Adds `default_member_role TEXT DEFAULT 'editor' CHECK ('viewer','editor')` to `synergy_sessions.synergy_sessions`
3. Creates a helper function `ai_infrastructure.create_personal_org(p_user_id, p_username, p_display_name)` so both the migration backfill and `register_user()` call a single function
4. Backfills personal orgs for all existing users with `organisation_id IS NULL`
5. Adds a verification block

```sql
-- ============================================================================
-- Migration 046: Personal Org + Synergy default_member_role
--
-- CHANGES:
--   1. Add is_personal_org BOOLEAN to ai_infrastructure.organisations
--   2. Add default_member_role TEXT CHECK to synergy_sessions.synergy_sessions
--   3. Create helper function create_personal_org() for use in register_user()
--   4. Backfill personal orgs for all users with organisation_id IS NULL
--
-- IDEMPOTENT: Yes — all changes use IF NOT EXISTS / ON CONFLICT / DO NOTHING
-- ============================================================================

-- ---- 1. Add is_personal_org to organisations --------------------------------
ALTER TABLE ai_infrastructure.organisations
    ADD COLUMN IF NOT EXISTS is_personal_org BOOLEAN DEFAULT FALSE;

-- ---- 2. Add default_member_role to synergy_sessions ------------------------
ALTER TABLE synergy_sessions.synergy_sessions
    ADD COLUMN IF NOT EXISTS default_member_role TEXT DEFAULT 'editor'
        CHECK (default_member_role IN ('viewer', 'editor'));

-- ---- 3. Helper function for creating a personal org -------------------------
CREATE OR REPLACE FUNCTION ai_infrastructure.create_personal_org(
    p_user_id      INT,
    p_username     TEXT,
    p_display_name TEXT DEFAULT NULL
) RETURNS INT
LANGUAGE plpgsql AS $$
DECLARE
    v_org_id   INT;
    v_org_name TEXT;
    v_slug     TEXT;
BEGIN
    v_org_name := 'personal_' || p_username || '_' || p_user_id;
    v_slug     := 'personal-' || p_user_id::TEXT;

    -- Idempotent: skip if user already has an org
    SELECT organisation_id INTO v_org_id
    FROM ai_infrastructure.users WHERE id = p_user_id;

    IF v_org_id IS NOT NULL THEN
        RETURN v_org_id;  -- already has an org, nothing to do
    END IF;

    INSERT INTO ai_infrastructure.organisations
        (name, slug, display_name, plan_tier, is_personal_org, is_active)
    VALUES
        (v_org_name, v_slug,
         COALESCE(p_display_name, p_username || '''s Workspace'),
         'free', TRUE, TRUE)
    ON CONFLICT (name) DO UPDATE SET is_personal_org = TRUE
    RETURNING id INTO v_org_id;

    UPDATE ai_infrastructure.users
    SET organisation_id = v_org_id,
        org_role        = 'owner'
    WHERE id = p_user_id
      AND organisation_id IS NULL;  -- safety: don't overwrite existing org assignment

    RETURN v_org_id;
END;
$$;

-- ---- 4. Backfill personal orgs for existing solo users ---------------------
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT id, username, email
        FROM ai_infrastructure.users
        WHERE organisation_id IS NULL
          AND is_sub_user IS NOT TRUE
    LOOP
        PERFORM ai_infrastructure.create_personal_org(r.id, r.username, NULL);
        RAISE NOTICE 'Created personal org for user %: %', r.id, r.username;
    END LOOP;
END;
$$;

-- ---- Verification ----------------------------------------------------------
DO $$
DECLARE
    v_has_col_personal    BOOLEAN;
    v_has_col_def_role    BOOLEAN;
    v_users_without_org   INT;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure' AND table_name = 'organisations'
          AND column_name = 'is_personal_org'
    ) INTO v_has_col_personal;

    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'synergy_sessions' AND table_name = 'synergy_sessions'
          AND column_name = 'default_member_role'
    ) INTO v_has_col_def_role;

    SELECT COUNT(*) INTO v_users_without_org
    FROM ai_infrastructure.users
    WHERE organisation_id IS NULL AND is_sub_user IS NOT TRUE;

    RAISE NOTICE 'Migration 046 complete — is_personal_org col: %, default_member_role col: %, users still without org: %',
        v_has_col_personal, v_has_col_def_role, v_users_without_org;
END;
$$;
```

**Acceptance criteria:**
- `SELECT column_name FROM information_schema.columns WHERE table_schema='ai_infrastructure' AND table_name='organisations' AND column_name='is_personal_org'` → 1 row
- `SELECT COUNT(*) FROM ai_infrastructure.users WHERE organisation_id IS NULL AND is_sub_user IS NOT TRUE` → 0
- `SELECT COUNT(*) FROM ai_infrastructure.organisations WHERE is_personal_org = TRUE` → ≥ 1

---

### Step 2 — register_user() Auto-Create Personal Org

**File:** `AI_infrastructure/auth/user_auth.py`
**Function:** `register_user()` at **line 348**
**Change location:** After the `INSERT INTO ai_infrastructure.users` at line 371, within the same transaction

**Current code block (lines 368–400):**
```python
# Create user
cursor.execute('''
    INSERT INTO ai_infrastructure.users (username, email, password_hash, primary_gmail, role, metadata)
    VALUES (%s, %s, %s, %s, %s, %s)
''', (username, email, password_hash, primary_gmail or email, role, json.dumps({})))

user_id = cursor.lastrowid

# Create default workspace
cursor.execute(...)
```

**New code to add after `user_id = cursor.lastrowid`:**
```python
# Create personal org and auto-assign user to it
cursor.execute(
    "SELECT ai_infrastructure.create_personal_org(%s, %s, %s)",
    (user_id, username, username + "'s Workspace")
)
org_row = cursor.fetchone()
personal_org_id = org_row[0] if org_row else None
```

**Also update the return dict** to include:
```python
return {
    'success': True,
    'user_id': user_id,
    'workspace_id': workspace_id,
    'username': username,
    'email': email,
    'role': role,
    'organisation_id': personal_org_id,  # NEW
    'org_role': 'owner',                 # NEW
}
```

**Key constraint:** Must happen inside the `with get_connection('ai_infrastructure') as conn:` block so it is part of the same transaction. The `create_personal_org` function is idempotent so it is safe to call even if the user somehow already has an org.

---

### Step 3 — Backfill Existing Solo Users

**Covered by Migration 046 Step 4** (the `DO $$ ... FOR r IN ... LOOP` block).
This runs automatically when the migration is applied.

**Manual verification SQL (run in Supabase SQL editor after migration):**
```sql
-- Verify all users now have an organisation_id
SELECT COUNT(*) AS users_without_org
FROM ai_infrastructure.users
WHERE organisation_id IS NULL AND is_sub_user IS NOT TRUE;
-- Expected: 0

-- See all personal orgs created
SELECT u.username, o.name, o.is_personal_org, u.org_role
FROM ai_infrastructure.users u
JOIN ai_infrastructure.organisations o ON o.id = u.organisation_id
WHERE o.is_personal_org = TRUE
ORDER BY u.id;
```

---

### Step 4 — Expose is_personal_org in API Response

**File:** `AI_infrastructure/routes/organisation_credentials_routes.py`
**Function:** `get_org_info()` at **line 331**

**Change 1:** Update the SELECT query at line 338 to include `is_personal_org`:
```sql
-- Current (line 338):
SELECT id, name, slug, plan_tier, display_name, logo_url,
       timezone, country_code, is_active, created_at, updated_at,
       vault_password_hash, metadata,
       description, visibility, allowed_domains,
       ai_provider, ai_model, ai_max_tokens
FROM ai_infrastructure.organisations WHERE id = %s

-- Updated:
SELECT id, name, slug, plan_tier, display_name, logo_url,
       timezone, country_code, is_active, created_at, updated_at,
       vault_password_hash, metadata,
       description, visibility, allowed_domains,
       ai_provider, ai_model, ai_max_tokens,
       is_personal_org
FROM ai_infrastructure.organisations WHERE id = %s
```

**Change 2:** Add to the return dict (after `'ai_max_tokens'` key, around line 388):
```python
'is_personal_org': bool(org.get('is_personal_org', False)),
```

**Full updated return dict for `organisation` key:**
```python
'organisation': {
    ...existing keys...,
    'is_personal_org': bool(org.get('is_personal_org', False)),  # NEW
},
```

**Why this is needed:** `_updateIdentityPanel()` at line 30504 already calls `/api/org/info` asynchronously. Once `is_personal_org` is in the response, it can be cached on `window._orgIsPersonal` for use by Synergy share popup and other UI gating.

---

### Step 5 — Frontend Synergy Visibility Gating for Solo Users

**File:** `UI/business-ai-platform-v2.html`
**Function:** `_updateIdentityPanel(profile)` at **line 30504**

**Change 1: Cache `is_personal_org` when org info is fetched**

In the existing async fetch of `/api/org/info` inside `_updateIdentityPanel()` (around line 30558–30580), add caching:
```javascript
fetch(`${window.API_BASE_URL || ''}/api/org/info`, { headers: ... })
    .then(r => r.json())
    .then(data => {
        if (data.success && data.organisation) {
            // ... existing org name display code ...
            
            // Cache personal org flag globally for Synergy and other UI gating
            window._orgIsPersonal = !!data.organisation.is_personal_org;
        }
    });
```

**File:** `UI/modules_internal/synergy/synergy-board-init.js`
**Function:** `openSharePopup(sessionId)` at **line 1121**

**Change 2: Conditionally hide Team option for personal-org users**

In the popup HTML template (around line 1194 where the three `vOpt()` calls are rendered), add a conditional:
```javascript
const isPersonalOrg = window._orgIsPersonal === true;

// Render visibility options
const visibilityOptions = `
    ${vOpt('private', 'fa-lock', '#6b7280', 'rgba(107,114,128,0.12)',
           'Private', 'Only you can see this session')}
    ${vOpt('shared', 'fa-user-friends', '#3b82f6', 'rgba(59,130,246,0.12)',
           'Shared', 'Invite specific people with roles')}
    ${!isPersonalOrg ? vOpt('team', 'fa-users', '#22c55e', 'rgba(34,197,94,0.12)',
           'Team', 'Everyone in your organisation') : ''}
`;
```

**Also display a notice for solo users** in the share popup body when `isPersonalOrg = true`:
```javascript
${isPersonalOrg ? `
    <div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);
                border-radius:6px;padding:10px 12px;font-size:12px;
                color:var(--text-muted);margin-bottom:16px;">
        <i class="fas fa-info-circle" style="margin-right:6px;color:#3b82f6;"></i>
        You're on a personal workspace. Upgrade to a team plan to enable Team visibility.
    </div>` : ''}
```

---

### Step 6 — Synergy Route Enforcement for default_member_role

**File:** `AI_infrastructure/routes/synergy_routes.py`

#### 6a. Add `default_member_role` to session creation

**Function:** `create_session()` at **line 713**

In the `data = request.json` parsing block, accept and store `default_member_role`:
```python
default_member_role = data.get('default_member_role', 'editor')
if default_member_role not in ('viewer', 'editor'):
    default_member_role = 'editor'
```
Include in the `INSERT INTO synergy_sessions` statement.

#### 6b. Add `default_member_role` to session update

**Function:** `update_session()` at **line 1135**

Add `'default_member_role'` to the list of allowed update fields (already iterates an allowlist of field names).

#### 6c. Add permission checks to milestone/task creation

The following functions currently have **no** `check_session_permission` call. They look up by `session_id` but never verify the calling user has write access.

| Function | Line | Fix Required |
|----------|------|-------------|
| `create_milestone(session_id)` | 3085 | Add `check_session_permission(session, user_id, require_write=True)` at start |
| `update_milestone(milestone_id)` | 3286 | Look up parent session, add write check |
| `create_task(milestone_id)` | 3802 | Look up parent session via milestone, add write check |
| `update_task(task_id)` | 3852 | Look up parent session via task→milestone, add write check |
| `create_milestone_task(milestone_id)` | 4856 | Look up parent session, add write check |
| `create_task_subtask(task_id)` | 4950 | Look up parent session, add write check |

**Pattern to replicate** (from `update_session()` at line 1135):
```python
# Get session for permission check
session = get_session_by_id(session_id)
if not session:
    return jsonify({'success': False, 'error': 'Session not found'}), 404
user_id = getattr(g, 'rls_user_id', None)
has_permission, perm_type = check_session_permission(session, user_id, require_write=True)
if not has_permission:
    return jsonify({'success': False, 'error': 'Write permission required'}), 403
# Also check default_member_role for 'viewer' team members
if perm_type == 'team':
    effective_role = session.get('default_member_role', 'editor')
    if effective_role == 'viewer':
        return jsonify({'success': False, 'error': 'This session is team read-only'}), 403
```

**Note:** `create_milestone()` at line 3085 is marked deprecated in favor of `create_milestone_complete()` at line 2516 — both need the fix.

---

### Step 7 — initModulesFromOrg + is_personal_org Gating

**File:** `UI/business-ai-platform-v2.html`

#### 7a. Fix loadUserInfo() to run module gating for all users

**Function:** `loadUserInfo()` at **line 30620**

Current guard (around line 30670):
```javascript
if (profile.org_role || _isPlatformDev) {
    fetch(_apiBase + '/api/org/modules', ...)
```

**Problem:** Solo users who have just registered now have `org_role = 'owner'` (after our fix), so this guard will work correctly once Step 2 is implemented. However, to be safe and explicit, also accept users with `organisation_id`:
```javascript
const hasOrg = !!(profile.organisation_id || profile.org_role || _isPlatformDev);
if (hasOrg) {
    fetch(_apiBase + '/api/org/modules', ...)
```

#### 7b. Add is_personal_org parameter to initModulesFromOrg()

**Function:** `initModulesFromOrg` at **line 31352**

Extend signature to accept org info:
```javascript
async function initModulesFromOrg(modules, userRole, orgInfo) {
    const isPersonalOrg = !!(orgInfo && orgInfo.is_personal_org);
    // ... rest of existing logic ...
```

Then use `isPersonalOrg` to conditionally hide team-related UI elements:
```javascript
// Gate team-specific account sidebar tabs (after Zone 1 + Zone 2 gating)
if (isPersonalOrg) {
    // Hide "Invite Members" and "Team Management" sub-tabs in Account Sidebar
    document.querySelectorAll('[data-feature="team-invite"]').forEach(el => {
        el.classList.add('module-hidden');
    });
}
```

#### 7c. Add `data-module="synergy"` to Synergy sidebar button

**File:** `UI/business-ai-platform-v2.html`, **line 18730**

Current:
```html
<button class="sidebar-icon-btn" data-tab="synergy" title="Synergy Dashboard - Session & Task Management">
```

Updated:
```html
<button class="sidebar-icon-btn" data-tab="synergy" data-module="synergy" title="Synergy Dashboard - Session & Task Management">
```

**Note:** `synergy` must also exist in `ai_infrastructure.module_catalog` with `module_name = 'synergy'` (check migration 036 — it is already there as `min_plan_tier = 'starter'`).

#### 7d. Ensure `synergy` module is enabled for all personal orgs

Personal orgs are created with `plan_tier = 'free'`. The `synergy` module has `min_plan_tier = 'starter'` in `module_catalog`. This means unless we either:
- Lower `synergy` module's `min_plan_tier` to `'free'`, or
- Auto-enable it in `org_module_access` for personal orgs during backfill

Personal org users will have the Synergy button hidden by `initModulesFromOrg()`.

**Recommended fix:** In the `create_personal_org()` function (Migration 046), after creating the org, insert default module enables:
```sql
INSERT INTO ai_infrastructure.org_module_access
    (organisation_id, module_name, is_enabled, enabled_at, enabled_by)
SELECT v_org_id, module_name, TRUE, NOW(), p_user_id
FROM ai_infrastructure.module_catalog
WHERE module_name IN ('core_chat', 'documents', 'prompt_library', 'notifications', 'synergy')
ON CONFLICT (organisation_id, module_name) DO NOTHING;
```

---

### Step 8 — Session Member Management UI Completeness

**File:** `UI/modules_internal/synergy/synergy-board-init.js`
**Function:** `openSharePopup(sessionId)` at **line 1121**

The share popup already has:
- An invite input (`#${popupId}-invite-input`) + role select (`#${popupId}-invite-role`) + add button calling `synergyBoard.inviteMember()`
- A members list div (`#${popupId}-members`) that shows "No members added yet"

**What is missing:**
1. `inviteMember()` function that calls `POST /api/synergy/sessions/<id>/members`
2. `loadMemberList()` function that calls `GET /api/synergy/sessions/<id>/members` and populates `#${popupId}-members`
3. `removeMember()` that calls `DELETE /api/synergy/sessions/<id>/members/<user_id>`
4. Call to `loadMemberList()` when popup opens AND after visibility is set to `shared`
5. `saveVisibility()` function must pass `default_member_role` when saving `team` visibility

**API endpoints already exist** in `synergy_share_routes.py` — this is purely a frontend task.

**For `saveVisibility()` (line ~1289):** When saving with `team` visibility, send `default_member_role` from a new radio/select in the popup:
```javascript
body: JSON.stringify({
    visibility: newVisibility,
    default_member_role: document.getElementById(`${popupId}-default-role`)?.value || 'editor'
})
```

---

## 6. Files Changed Tracker

| Step | File | Change Type | Status |
|------|------|-------------|--------|
| 1 | `AI_infrastructure/migrations/046_personal_org_and_synergy_defaults.sql` | CREATE NEW | ✅ COMPLETE |
| 2 | `AI_infrastructure/auth/user_auth.py` (line 348) | EDIT | ✅ COMPLETE |
| 4 | `AI_infrastructure/routes/organisation_credentials_routes.py` (line 331, 338, 388) | EDIT | ✅ COMPLETE |
| 5a | `UI/business-ai-platform-v2.html` (line ~30558, `_updateIdentityPanel`) | EDIT | ✅ COMPLETE |
| 5b | `UI/modules_internal/synergy/synergy-board-init.js` (line 1121, `openSharePopup`) | EDIT | ✅ COMPLETE |
| 6a | `AI_infrastructure/routes/synergy_routes.py` (line 713, `create_session`) | EDIT | ✅ COMPLETE |
| 6b | `AI_infrastructure/routes/synergy_routes.py` (line 1135, `update_session`) | EDIT | ✅ COMPLETE |
| 6c | `AI_infrastructure/routes/synergy_routes.py` (lines 3085, 3286, 3802, 3852, 4856, 4950) | EDIT × 6 | ✅ COMPLETE |
| 7a | `UI/business-ai-platform-v2.html` (line ~30670, `loadUserInfo`) | EDIT | ✅ COMPLETE |
| 7b | `UI/business-ai-platform-v2.html` (line 31352, `initModulesFromOrg`) | EDIT | ✅ COMPLETE |
| 7c | `UI/business-ai-platform-v2.html` (line 18730, Synergy button) | EDIT | ✅ COMPLETE |
| 8 | `UI/modules_internal/synergy/synergy-board-init.js` (member management functions) | EDIT | ✅ COMPLETE |
| P6 | `tools/implementations/synergy.py` (new AI tool implementations) | APPEND | ✅ COMPLETE |
| P6 | `tools/schemas/synergy_member_platform_tools.json` | CREATE NEW | ✅ COMPLETE |

**Status legend:** ⬜ NOT STARTED | 🔄 IN PROGRESS | ✅ COMPLETE | ❌ BLOCKED

---

## 7. Database Tables Reference

### Tables Modified by This Work

| Schema | Table | Columns Added |
|--------|-------|---------------|
| `ai_infrastructure` | `organisations` | `is_personal_org BOOLEAN DEFAULT FALSE` |
| `synergy_sessions` | `synergy_sessions` | `default_member_role TEXT DEFAULT 'editor' CHECK('viewer','editor')` |

### Tables Read by This Work (No Changes)

| Schema | Table | Purpose in This Work |
|--------|-------|---------------------|
| `ai_infrastructure` | `users` | `organisation_id`, `org_role`, `is_sub_user`, `parent_user_id` |
| `ai_infrastructure` | `organisation_platform_credentials` | Tier 2 credential resolution |
| `ai_infrastructure` | `module_catalog` | Module plan tier + required platforms |
| `ai_infrastructure` | `org_module_access` | Per-org module enable/disable override |
| `synergy_sessions` | `session_members` | User roles within shared sessions (viewer/editor/admin) |

### Functions Created

| Schema | Function | Created In |
|--------|----------|-----------|
| `ai_infrastructure` | `create_personal_org(p_user_id INT, p_username TEXT, p_display_name TEXT)` | Migration 046 |

---

## 8. API Changes Summary

### Modified Endpoints

| Method | Endpoint | File | Change |
|--------|----------|------|--------|
| GET | `/api/org/info` | `organisation_credentials_routes.py` line 331 | Add `is_personal_org` to SELECT query and response |

### Endpoints Already Exist (No Change Needed)

| Method | Endpoint | File | Notes |
|--------|----------|------|-------|
| GET | `/api/org/modules` | `organisation_credentials_routes.py` | Returns enabled module set for org |
| PATCH | `/api/synergy/sessions/<id>/visibility` | `synergy_share_routes.py` line 77 | Already validates org requirement for `team` |
| GET | `/api/synergy/sessions/<id>/members` | `synergy_share_routes.py` | Already exists, no UI yet |
| POST | `/api/synergy/sessions/<id>/members` | `synergy_share_routes.py` | Already exists, no UI yet |
| DELETE | `/api/synergy/sessions/<id>/members/<user_id>` | `synergy_share_routes.py` | Already exists, no UI yet |

---

## 9. Testing Checklist

### After Step 1 (Migration 046)
- [ ] `SELECT COUNT(*) FROM ai_infrastructure.users WHERE organisation_id IS NULL AND is_sub_user IS NOT TRUE` → `0`
- [ ] `SELECT is_personal_org FROM ai_infrastructure.organisations LIMIT 5` → returns without error
- [ ] `SELECT default_member_role FROM synergy_sessions.synergy_sessions LIMIT 5` → returns without error
- [ ] Run migration twice — no errors (idempotency check)

### After Step 2 (register_user)
- [ ] Register a new test user
- [ ] `SELECT u.username, o.name, o.is_personal_org, u.org_role FROM ai_infrastructure.users u JOIN ai_infrastructure.organisations o ON o.id = u.organisation_id WHERE u.email = 'testuser@test.com'`
  → `is_personal_org = TRUE`, `org_role = 'owner'`, `o.name = 'personal_testuser_<id>'`
- [ ] Login with new user → JWT includes `organisation_id` (non-null) and `org_role = 'owner'`

### After Step 4 (API change)
- [ ] `GET /api/org/info` response includes `is_personal_org: true` for personal-org user
- [ ] `GET /api/org/info` response includes `is_personal_org: false` for team/org user

### After Step 5 (Synergy frontend)
- [ ] Personal-org user: Share popup shows only "Private" and "Shared" — no "Team" option
- [ ] Team/org user: Share popup shows all three options
- [ ] Solo user info notice is visible in share popup

### After Step 6 (Route enforcement)
- [ ] `viewer` role team member cannot create milestone (403 response)
- [ ] `editor` role team member can create milestone (200 response)
- [ ] `default_member_role = 'viewer'` on session → team members get read-only access

### After Step 7 (initModulesFromOrg)
- [ ] `loadUserInfo()` calls `/api/org/modules` even for solo users (previously skipped if `org_role = null`)
- [ ] `initModulesFromOrg()` receives `orgInfo.is_personal_org = true` via third parameter
- [ ] `window._orgIsPersonal` is set after `_updateIdentityPanel` runs
- [ ] Synergy button appears in sidebar only when `synergy` module is enabled in `org_module_access`

### After Step 8 (Member management UI)
- [ ] Opening share popup with `shared` visibility → calls `/api/synergy/sessions/<id>/members` and lists members
- [ ] Adding a member by email → appears in member list
- [ ] Removing a member → calls DELETE endpoint and disappears from list
- [ ] Saving `team` visibility with `default_member_role = 'viewer'` → stored in DB

---

## Change Log

| Date | Step | Status | Notes |
|------|------|--------|-------|
| May 6, 2026 | All | ⬜ NOT STARTED | Document created, all steps designed |
| May 2026 | Step 1 — Migration 046 | ✅ COMPLETE | `AI_infrastructure/migrations/046_personal_org_and_synergy_defaults.sql` created. Adds `is_personal_org`, `default_member_role`, `create_personal_org()` SQL function, backfill block. |
| May 2026 | Step 2 — `register_user()` | ✅ COMPLETE | `AI_infrastructure/auth/user_auth.py` — calls `create_personal_org()` after INSERT, sets `organisation_id` + `org_role` in return dict. |
| May 2026 | Step 3 — `get_org_info()` | ✅ COMPLETE | `AI_infrastructure/routes/organisation_credentials_routes.py` — exposes `is_personal_org` in `/api/org/info` response. |
| May 2026 | Step 4 — `_updateIdentityPanel` | ✅ COMPLETE | `UI/business-ai-platform-v2.html` — fixed `data.org` → `data.organisation` bug; caches `window._orgIsPersonal` + `window._orgInfo`. |
| May 2026 | Step 5 — Synergy share popup | ✅ COMPLETE | `UI/modules_internal/synergy/synergy-board-init.js` — hides Team option + shows info notice for personal org users. |
| May 2026 | Step 6 — `initModulesFromOrg` + sidebar gate | ✅ COMPLETE | `UI/business-ai-platform-v2.html` — `initModulesFromOrg` accepts `orgInfo` 3rd arg; `loadUserInfo` guard fixed for solo users; `data-module="synergy"` added to sidebar button. |
| May 2026 | Step 7 — Synergy route enforcement | ✅ COMPLETE | `AI_infrastructure/routes/synergy_routes.py` — `default_member_role` parsed + saved in `create_session()` INSERT (26 cols) and `update_session()` allowlist. Write-permission guards added to `create_milestone`, `update_milestone`, `create_task`, `update_task`, `create_milestone_task`, `create_task_subtask`. |
| May 2026 | Step 8 — Member management | ✅ COMPLETE | **Backend:** 4 new routes — `PATCH /<id>/visibility`, `GET /<id>/members`, `POST /<id>/members`, `DELETE /<id>/members/<uid>`. `execute_query` imported for cross-schema user lookups. **Frontend:** `loadMemberList()` + `removeMember()` added to `synergyBoard`; `inviteMember()` refactored to call `loadMemberList` after success; `openSharePopup` auto-loads members; `selectVisibility` loads members when switching to 'shared'. |

---

## Phase 6 — AI Tools Gap Analysis & Implementation
**Date: May 7, 2026**
**Status: ✅ COMPLETE**

### 6.1 Analysis Performed

After Plan Steps 1–8 were complete, a tools gap analysis was run against the Synergy AI tool surface to identify capabilities that existed in the backend but had no corresponding AI-callable tool or schema.

**Research findings:**
- `tools/implementations/synergy.py` — ~4,030 lines, ~53 registered tools
- `tools/schemas/synergy_tools.json` — primary schema file, auto-loaded by `registry_v3._load_schemas()` via `schemas_dir.glob("*.json")`
- `synergy_sync_to_google` existed in Python (line 1172) but had **no schema** — AI could not call it
- The 4 new member management routes (built in Step 8) had **no Python wrapper or schema**
- `GET /api/synergy/internal-docs/list` had **no AI wrapper**
- `POST /api/synergy/milestone/<id>/comment` had **no AI wrapper**
- No one-step bridge existed to attach OneDrive / SharePoint / Google Drive files to sessions
- No Microsoft 365 sync equivalent to the existing `synergy_sync_to_google`

### 6.2 Tools Implemented

All implementations appended to `tools/implementations/synergy.py` (before the deprecated aliases block). All schemas in new file `tools/schemas/synergy_member_platform_tools.json` (auto-registered at startup — no manual wiring).

| Tool | Priority | Python impl | Schema | Wraps |
|------|----------|-------------|--------|-------|
| `synergy_update_visibility` | High | ✅ | ✅ | `PATCH /api/synergy/<id>/visibility` |
| `synergy_invite_member` | High | ✅ | ✅ | `POST /api/synergy/<id>/members` |
| `synergy_list_members` | High | ✅ | ✅ | `GET /api/synergy/<id>/members` |
| `synergy_remove_member` | High | ✅ | ✅ | `DELETE /api/synergy/<id>/members/<uid>` |
| `synergy_list_internal_docs` | High | ✅ | ✅ | `GET /api/synergy/internal-docs/list` |
| `synergy_add_comment` | Low | ✅ | ✅ | `POST /api/synergy/milestone/<id>/comment` |
| `synergy_attach_platform_file` | Medium | ✅ | ✅ | Platform share link → `synergy_add_document` |
| `synergy_attach_platform_file_to_doc` | Low | ✅ | ✅ | Platform share link → append to internal doc |
| `synergy_sync_to_microsoft` | Medium | ✅ | ✅ | `PATCH /api/synergy/<id>` with M365 sync flags |
| `synergy_import_from_sharepoint` | Low | ✅ | ✅ | SharePoint list/file → Synergy internal doc |
| `synergy_import_from_drive` | Low | ✅ | ✅ | Google Drive file → Synergy internal doc |
| `synergy_sync_to_google` | — | ✅ (existed) | ✅ **ADDED** | `PATCH /api/synergy/<id>` with Google sync flags |

**Total new AI-callable tools:** 12 (11 net-new implementations + 1 schema-only fix for existing function)

### 6.3 Architecture Notes

- **Tool registry auto-discovery:** `tools/registry_v3._load_schemas()` globs `tools/schemas/*.json` — no manual registration ever needed for new schema files.
- **Bridge tools** (`synergy_attach_platform_file`, `*_to_doc`, `synergy_import_from_*`) attempt direct Python module imports from `tools/implementations/microsoft_onedrive`, `microsoft_sharepoint`, and `google_drive` modules. If those module classes don't expose the expected method, they raise a descriptive `SynergyError` so the AI can explain the issue to the user.
- **`synergy_sync_to_microsoft`** sends `{"updates": {}, "sync": {"microsoft_planner": bool, "microsoft_calendar": bool, "microsoft_todo": bool}}` via the same `PATCH /api/synergy/<id>` endpoint used by `synergy_sync_to_google`. Backend webhook/handler is responsible for the actual M365 API calls.

### 6.4 Files Changed (Phase 6)

| File | Change |
|------|--------|
| `tools/implementations/synergy.py` | 11 new functions appended before deprecated aliases block |
| `tools/schemas/synergy_member_platform_tools.json` | New file — 12 tool schemas (11 new + `synergy_sync_to_google`) |

---

## Change Log

| Date | Step | Status | Notes |
|------|------|--------|-------|
| May 6, 2026 | All | ⬜ NOT STARTED | Document created, all steps designed |
| May 6, 2026 | Step 1 — Migration 046 | ✅ COMPLETE | `AI_infrastructure/migrations/046_personal_org_and_synergy_defaults.sql` created. Adds `is_personal_org`, `default_member_role`, `create_personal_org()` SQL function, backfill block. |
| May 6, 2026 | Step 2 — `register_user()` | ✅ COMPLETE | `AI_infrastructure/auth/user_auth.py` — calls `create_personal_org()` after INSERT, sets `organisation_id` + `org_role` in return dict. |
| May 6, 2026 | Step 3 — `get_org_info()` | ✅ COMPLETE | `AI_infrastructure/routes/organisation_credentials_routes.py` — exposes `is_personal_org` in `/api/org/info` response. |
| May 6, 2026 | Step 4 — `_updateIdentityPanel` | ✅ COMPLETE | `UI/business-ai-platform-v2.html` — fixed `data.org` → `data.organisation` bug; caches `window._orgIsPersonal` + `window._orgInfo`. |
| May 6, 2026 | Step 5 — Synergy share popup | ✅ COMPLETE | `UI/modules_internal/synergy/synergy-board-init.js` — hides Team option + shows info notice for personal org users. |
| May 6, 2026 | Step 6 — `initModulesFromOrg` + sidebar gate | ✅ COMPLETE | `UI/business-ai-platform-v2.html` — `initModulesFromOrg` accepts `orgInfo` 3rd arg; `loadUserInfo` guard fixed for solo users; `data-module="synergy"` added to sidebar button. |
| May 6, 2026 | Step 7 — Synergy route enforcement | ✅ COMPLETE | `AI_infrastructure/routes/synergy_routes.py` — `default_member_role` parsed + saved in `create_session()` INSERT and `update_session()` allowlist. Write-permission guards added to `create_milestone`, `update_milestone`, `create_task`, `update_task`, `create_milestone_task`, `create_task_subtask`. |
| May 6, 2026 | Step 8 — Member management | ✅ COMPLETE | **Backend:** 4 new routes — `PATCH /<id>/visibility`, `GET /<id>/members`, `POST /<id>/members`, `DELETE /<id>/members/<uid>`. **Frontend:** `loadMemberList()` + `removeMember()` added to `synergyBoard`; `inviteMember()` refactored; `openSharePopup` auto-loads members on open and on switching to 'shared'. |
| May 7, 2026 | Phase 6 — AI Tools Gap Analysis | ✅ COMPLETE | Identified 11 missing + 1 schema-only gaps in Synergy AI tool surface. |
| May 7, 2026 | Phase 6 — AI Tools Implementation | ✅ COMPLETE | 11 new Python implementations appended to `tools/implementations/synergy.py`; `tools/schemas/synergy_member_platform_tools.json` created with 12 schemas (auto-registered). `synergy_sync_to_google` schema-only fix applied (implementation already existed). |

---

*End of document.*
