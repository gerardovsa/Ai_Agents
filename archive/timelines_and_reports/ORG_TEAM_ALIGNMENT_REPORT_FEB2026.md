# Organisation, Team IDs & Role Levels — Full Alignment Report
**Date:** February 2026  
**Scope:** DB schema · Backend routes · JWT/auth flow · Frontend UI  
**Method:** Live database queries + full code audit of all 6 documents plus all related implementation files  

---

## Executive Summary

The new Organisation system (March 2026 architecture) is **structurally sound at the database and API layer** — all tables exist, all helper functions exist, all 18 API routes are wired and working. However there are **3 functional bugs** that prevent the system from working end-to-end in a live UI session:

| Priority | Bug | Symptom |
|----------|-----|---------|
| 🔴 CRITICAL | `GET /api/auth/profile` does not include `org_role`/`organisation_id` | Role-gating in UI never fires — everyone sees all tabs |
| 🔴 CRITICAL | `showCreateOrgForm()` / `createOrganisation()` JS functions not defined | "Create Organisation" button throws ReferenceError |
| 🟡 MEDIUM | JWT payload doesn't include `organisation_id` | RLS session context always has `organisation_id = NULL` |

The old **Team ID / Sub-user** system (December 2025) coexists alongside the new Organisation system and is still active.

---

## 1. Two Parallel User Hierarchy Systems

The platform currently has **two separate multi-tenancy/role systems running simultaneously**.

### 1a. OLD System — Team IDs / Sub-users (December 2025)
**Purpose:** Allow a single user to create sub-accounts that share their data.

**DB columns on `ai_infrastructure.users`:**
| Column | Type | Default |
|--------|------|---------|
| `parent_user_id` | INTEGER → FK users(id) | NULL |
| `is_sub_user` | BOOLEAN | FALSE |
| `display_name` | TEXT | NULL |

**DB columns on `sessions.messages`:**
| Column | Type |
|--------|------|
| `sender_team_id` | TEXT |
| `recipient_team_id` | TEXT |
| `message_type` | TEXT DEFAULT 'private' |

**DB columns on `sessions.threads`:**
| Column | Type |
|--------|------|
| `team_id` | TEXT |

**Backend routes:** `routes/user_management_routes.py`
- `POST /api/users/sub-users` — create sub-user
- `GET /api/users/sub-users` — list sub-users
- `PUT /api/users/sub-users/<id>` — update sub-user
- `DELETE /api/users/sub-users/<id>` — delete sub-user

**Frontend:** Security Modal → "Team ID Management" section — still visible and functional.

**Status:** ✅ Fully functional, still live.

---

### 1b. NEW System — Organisations + Roles (March 2026)
**Purpose:** Multi-tenant organisations where multiple independent users belong to a shared entity with role-based access.

**DB columns added to `ai_infrastructure.users`:**
| Column | Type | Default |
|--------|------|---------|
| `organisation_id` | INTEGER → FK organisations(id) | NULL |
| `org_role` | VARCHAR(50) CHECK IN ('viewer','member','manager','admin','owner') | 'member' |

**New table: `ai_infrastructure.organisations`:**
| Column | Type |
|--------|------|
| `id` | SERIAL PK |
| `name` | VARCHAR(255) |
| `slug` | VARCHAR(100) UNIQUE |
| `plan_tier` | VARCHAR(50) ('free','starter','professional','enterprise') |
| `display_name` | VARCHAR(255) |
| `logo_url` | TEXT |
| `timezone` | VARCHAR(100) |
| `country_code` | VARCHAR(10) |
| `vault_password_hash` | TEXT |
| `metadata` | JSONB |
| `is_active` | BOOLEAN |
| `created_at` / `updated_at` | TIMESTAMPTZ |

**Status:** ✅ Fully migrated to DB.

---

## 2. Role Hierarchy — All Layers Aligned ✅

The 5-tier role hierarchy is **consistent across all four layers**:

| Role | Level | DB CHECK | Backend `ROLE_LEVELS` | Frontend `ROLE_LEVELS` |
|------|-------|----------|-----------------------|------------------------|
| viewer | 1 | ✅ | ✅ | ✅ |
| member | 2 | ✅ | ✅ | ✅ |
| manager | 3 | ✅ | ✅ | ✅ |
| admin | 4 | ✅ | ✅ | ✅ |
| owner | 5 | ✅ | ✅ | ✅ |

**Files where `ROLE_LEVELS` is defined:**
- `AI_infrastructure/routes/organisation_credentials_routes.py` (line 58) — backend enforcement
- `UI/business-ai-platform-v2.html` (line 30919) — frontend UI gating
- `AI_infrastructure/migrations/add_organisations_and_org_credentials.sql` — DB helper function `get_role_level(TEXT)`
- `ORG_CREDENTIALS_MASTER_ANALYSIS.md` — documentation

**`data-org-min-role` attribute pattern** on UI elements is correctly implemented and would work **if the profile endpoint returned `org_role`** (see Bug #1 below).

---

## 3. Database State — Live Query Results

### Organisations Table

| id | name | slug | plan_tier | is_active |
|----|------|------|-----------|-----------|
| 1 | InHouse Print | inhouse-print | enterprise | True |

⚠️ **Only 1 organisation exists.** Documentation references a "valorai" org and a "platform" org (seeded by migration) — neither exists in the live database. These appear to be from earlier/sandbox migrations that were replaced when the InHouse Print org was manually created.

### Users — Organisation Assignment (11 users)

| User | organisation_id | org_role | is_sub_user |
|------|----------------|----------|-------------|
| gerardo (id=12) | 1 (InHouse Print) | owner | false |
| all other 10 users | NULL | member (default) | false |

Gerardo is the only user linked to an organisation. All others are unassigned. Their default `org_role='member'` is the DB default, not a meaningful assignment.

### Organisation Platform Credentials

| id | org_id | platform | display_name | environment | active |
|----|--------|----------|-------------|-------------|--------|
| 1 | 1 | pinecone | InHouse Vector DB | production | ✅ |
| 2 | 1 | anthropic | Claude API | production | ✅ |

### All Expected Tables

| Table | Exists | Notes |
|-------|--------|-------|
| `ai_infrastructure.organisations` | ✅ | 1 row |
| `ai_infrastructure.organisation_platform_credentials` | ✅ | 2 rows |
| `ai_infrastructure.credential_access_log` | ✅ | Audit trail |
| `ai_infrastructure.org_invitations` | ✅ | Empty, ready |
| `synergy_sessions.session_members` | ✅ | Empty, ready |
| `synergy_sessions.synergy_sessions.organisation_id` | ✅ | Column exists |
| `synergy_sessions.synergy_sessions.visibility` | ✅ | text, check ('private','shared','team') |

### DB Helper Functions

| Function | Exists |
|----------|--------|
| `get_role_level(TEXT)` | ✅ |
| `mask_credential(TEXT)` | ✅ |
| `user_can_list_credential(...)` | ✅ |
| `user_can_reveal_credential(...)` | ✅ |

### RLS Policies

| Schema.Table | Policy | Command |
|-------------|--------|---------|
| ai_infrastructure.credential_access_log | `cred_log_same_org` | SELECT |
| ai_infrastructure.credential_access_log | `service_role_bypass_cred_log` | ALL |
| ai_infrastructure.organisation_platform_credentials | `org_creds_same_org` | SELECT |
| ai_infrastructure.organisation_platform_credentials | `org_creds_write_own_org` | ALL |
| ai_infrastructure.organisation_platform_credentials | `service_role_bypass_org_creds` | ALL |
| ai_infrastructure.organisations | `service_role_bypass_organisations` | ALL |
| ai_infrastructure.org_invitations | `org_invitations_select` | SELECT |
| ai_infrastructure.org_invitations | `org_invitations_write` | ALL |
| synergy_sessions.synergy_sessions | `synergy_sessions_select` | SELECT |
| synergy_sessions.synergy_sessions | `synergy_sessions_write` | ALL |
| synergy_sessions.synergy_sessions | `Allow realtime subscription` | SELECT |
| synergy_sessions.session_members | `session_members_select` | SELECT |
| synergy_sessions.session_members | `session_members_write` | ALL |
| synergy_sessions.milestones | `milestones_select` / `milestones_write` | SELECT / ALL |
| synergy_sessions.tasks | `tasks_select` / `tasks_write` | SELECT / ALL |
| synergy_sessions.subtasks | `subtasks_select` | SELECT |
| synergy_sessions.milestone_comments | `comments_select` | SELECT |
| synergy_sessions.milestone_history | `history_select` | SELECT |
| synergy_sessions.synergy_internal_docs | `internal_docs_select` / `internal_docs_write` | SELECT / ALL |

⚠️ **Note on `organisations` table:** The only policy is `service_role_bypass_organisations` (for the `service_role` DB role). There is no user-facing SELECT policy. This is not a bug because the Flask backend uses a psycopg2 direct connection with a superuser/admin role that bypasses RLS entirely. All `execute_query()` calls go through this admin connection and filter by `organisation_id` in their WHERE clauses.

---

## 4. Backend Route Audit

### `routes/organisation_credentials_routes.py` — 18 Routes

| Method | URL | Min Role | Status |
|--------|-----|----------|--------|
| GET | `/api/org/info` | member | ✅ |
| PUT | `/api/org/info` | owner | ✅ |
| GET | `/api/org/members` | manager | ✅ |
| PUT | `/api/org/members/<id>/role` | admin | ✅ |
| DELETE | `/api/org/members/<id>` | owner | ✅ |
| GET | `/api/org/credentials` | manager | ✅ |
| POST | `/api/org/credentials` | admin | ✅ |
| PUT | `/api/org/credentials/<id>` | admin | ✅ |
| DELETE | `/api/org/credentials/<id>` | admin | ✅ |
| POST | `/api/org/credentials/<id>/reveal` | admin + vault pwd | ✅ |
| GET | `/api/org/credentials/audit-log` | admin | ✅ |
| POST | `/api/org/vault-password` | owner | ✅ |
| DELETE | `/api/org/vault-password` | owner | ✅ |
| POST | `/api/org/invite` | admin | ✅ |
| GET | `/api/org/invite/pending` | admin | ✅ |
| DELETE | `/api/org/invite/<id>` | admin | ✅ |
| GET | `/api/org/invite/accept` | public (token) | ✅ |
| POST | `/api/org/invite/accept` | public (token) | ✅ |
| **POST** | **`/api/org/create`** | — | ❌ **MISSING** |

**Auth enforcement pattern (correct):**
```
require_auth → verify_token() → sets g.user_id from JWT (works, user_id IS in JWT)
require_org_role('X') → get_user_org_context(g.user_id) → DB query fresh → gets org_role
```
This means the API layer is **not affected** by the JWT missing org fields — it always queries the DB directly.

### `routes/synergy_share_routes.py` — 4 Routes

| Method | URL | Status |
|--------|-----|--------|
| PATCH | `/api/synergy/sessions/<id>/visibility` | ✅ |
| GET | `/api/synergy/sessions/<id>/members` | ✅ |
| POST | `/api/synergy/sessions/<id>/members` | ✅ |
| DELETE | `/api/synergy/sessions/<id>/members/<user_id>` | ✅ |

---

## 5. Auth/JWT Flow — Bugs Found

### BUG #1 (CRITICAL) — Profile endpoint missing org fields

**File:** `AI_infrastructure/routes/auth_routes.py` → `get_profile()` (line ~238)  
**File:** `AI_infrastructure/auth/user_auth.py` → `require_auth` decorator (line 1832)  

**Flow:**
```
1. Browser opens Account Sidebar
2. AccountSidebar.loadUserInfo() → GET /api/auth/profile
3. get_profile() calls require_auth → verify_token() → returns JWT payload as request.user
4. JWT payload = {user_id, username, email, role, exp}  ← NO org fields
5. get_profile() only queries: SELECT password_hash, display_name FROM users WHERE id=%s
6. Returns: {...request.user, display_name, gmail_accounts, workspace_id, auth_platform, ...}
                                                          ← NO org_role, organisation_id, is_sub_user
7. applyOrgRoleVisibility(profile) → profile.org_role = undefined → returns immediately
8. NO visibility/role gating is ever applied to the sidebar tabs
```

**Impact:**
- `data-org-min-role` gating on sidebar tabs never activates — all users (viewers, members, etc.) see all tabs including Security and Connections
- `config.is_sub_user` check in visibility logic always evaluates to `false`

**Fix:** Expand the user query in `get_profile()` to include org fields — see Section 7.

---

### BUG #2 (MEDIUM) — JWT payload missing org fields

**File:** `AI_infrastructure/auth/user_auth.py` → `login()` (line ~471)

**Current payload:**
```python
token_payload = {
    'user_id': user_id,
    'username': username,
    'email': email,
    'role': role,
    'exp': exp_timestamp
}
```

**Missing:** `organisation_id`, `org_role`

**Impact:**
- `set_rls_context_from_jwt()` in `flask_app.py` reads `payload.get('organisation_id')` → always `None`
- `g.rls_organisation_id` is always `None`  
- `rls_session_manager.inject_rls_vars()` sets `app.current_organisation_id = None` on DB connections
- RLS policies for `organisation_platform_credentials` that check `current_setting('app.current_organisation_id')` receive NULL → policies evaluate to NULL → safe-fail to deny (but the Flask admin connection already bypasses RLS, so day-to-day API calls are unaffected)

**Note:** This does NOT break the Org API routes because `require_org_role` queries the DB directly. It only matters if you rely on the pgBouncer-compatible RLS session variables for multi-tenant data isolation at the DB level.

---

## 6. Frontend UI Audit

### Org Dashboard (Settings → Organisation tab) — ✅ Wired Correctly

| Feature | Function | API Call | Status |
|---------|----------|----------|--------|
| Load org info | `OrgManager.loadOrgInfo()` | GET `/api/org/info` | ✅ |
| Update org name | `OrgManager.saveOrgInfo()` | PUT `/api/org/info` | ✅ |
| List members | `OrgManager.loadMembers()` | GET `/api/org/members` | ✅ |
| Change member role | `OrgManager.changeMemberRole()` | PUT `/api/org/members/<id>/role` | ✅ |
| Remove member | `OrgManager.removeMember()` | DELETE `/api/org/members/<id>` | ✅ |
| Send invitation | `OrgManager.sendInvite()` | POST `/api/org/invite` | ✅ |
| List pending invitations | `OrgManager.loadPendingInvites()` | GET `/api/org/invite/pending` | ✅ |
| Revoke invitation | `OrgManager.revokeInvite()` | DELETE `/api/org/invite/<id>` | ✅ |
| View credentials | `OrgManager.loadCredentials()` | GET `/api/org/credentials` | ✅ |
| Add credential | `OrgManager.addCredential()` | POST `/api/org/credentials` | ✅ |
| Reveal credential | `OrgManager.revealCredential()` | POST `/api/org/credentials/<id>/reveal` | ✅ |
| Audit log | `OrgManager.loadAuditLog()` | GET `/api/org/credentials/audit-log` | ✅ |
| Set vault password | `OrgManager.setVaultPassword()` | POST `/api/org/vault-password` | ✅ |

### Org Creation — ❌ Completely Broken

The "No Organisation Yet" empty state shows a **Create Organisation** button. Clicking it calls `showCreateOrgForm()` — but this function is not defined anywhere in the JavaScript. All four functions are missing:

| Function | Defined? | Called from |
|----------|----------|-------------|
| `showCreateOrgForm()` | ❌ NOT DEFINED | HTML line 22956 |
| `hideCreateOrgForm()` | ❌ NOT DEFINED | HTML line 22985 |
| `updateOrgSlugPreview()` | ❌ NOT DEFINED | HTML line 22964 |
| `createOrganisation()` | ❌ NOT DEFINED | HTML line 22986 |

Additionally, **there is no `POST /api/org/create` backend endpoint**. The form has fields for: name, slug, description, visibility.

### Role Gating — ❌ Non-functional (due to Bug #1)

The `applyOrgRoleVisibility(profile)` function is correctly written and looks at `data-org-min-role` attributes, but receives `profile.org_role = undefined` → returns immediately without applying any gating.

### Old Team ID System — ✅ Still Present and Functional

The Security modal still shows "Team ID Management" and calls:
- `POST /api/auth/team-ids/add`
- `PUT /api/auth/team-ids/{teamId}`
- `DELETE /api/auth/team-ids/{teamId}`

These route to `user_management_routes.py` sub-user endpoints. Both systems coexist without conflict — a user can have both `is_sub_user=true` AND `organisation_id` set (though `applyOrgRoleVisibility` treats `is_sub_user` as level 0, which would hide all org tabs for sub-users).

---

## 7. Fixes Required

### Fix #1 — Profile Endpoint Must Return Org Fields

**File:** `AI_infrastructure/routes/auth_routes.py`  
**Function:** `get_profile()` (~line 260)

Change the first DB query from:
```python
cursor.execute(
    'SELECT password_hash, display_name FROM ai_infrastructure.users WHERE id = %s',
    (user_id,)
)
user_row = cursor.fetchone()
display_name = user_row.get('display_name')
```

To:
```python
cursor.execute(
    '''SELECT password_hash, display_name, organisation_id, org_role, is_sub_user
       FROM ai_infrastructure.users WHERE id = %s''',
    (user_id,)
)
user_row = cursor.fetchone()
display_name = user_row.get('display_name')
organisation_id = user_row.get('organisation_id')
org_role = user_row.get('org_role')
is_sub_user = user_row.get('is_sub_user', False)
```

And in the return statement, expand the profile dict:
```python
return jsonify({
    'success': True,
    'profile': {
        **request.user,
        'id': request.user['user_id'],
        'display_name': display_name,
        'organisation_id': organisation_id,   # ADD
        'org_role': org_role,                  # ADD
        'is_sub_user': is_sub_user,            # ADD
        'gmail_accounts': gmail_accounts,
        'workspace_id': workspace_id,
        'auth_platform': auth_platform,
        'google_oauth_connected': google_oauth_connected,
        'microsoft_oauth_connected': microsoft_oauth_connected
    }
})
```

**Result:** `applyOrgRoleVisibility(profile)` will correctly receive `org_role='owner'` for gerardo and show/hide sidebar tabs accordingly.

---

### Fix #2 — Add Org Creation JS Functions + Backend Endpoint

**File:** `UI/business-ai-platform-v2.html` — add 4 JS functions near the `OrgManager` object.

**File:** `AI_infrastructure/routes/organisation_credentials_routes.py` — add `POST /api/org/create` endpoint.

These are new features (not just bugs) — full implementation in Section 8.

---

### Fix #3 — Add Org Fields to JWT (Optional but Recommended)

**File:** `AI_infrastructure/auth/user_auth.py` → `login()` (~line 492)

Extend the initial user query to also fetch org data:
```python
cursor.execute('''
    SELECT id, username, email, password_hash, role, primary_gmail,
           organisation_id, org_role
    FROM ai_infrastructure.users
    WHERE username = %s OR email = %s
''', (username, username))
```

Then add to the JWT payload:
```python
token_payload = {
    'user_id': user_id,
    'username': username,
    'email': email,
    'role': role,
    'organisation_id': organisation_id,   # ADD
    'org_role': org_role,                  # ADD
    'exp': exp_timestamp
}
```

**Note:** Existing live JWTs (30-day expiry) will not have these fields until users re-login. The backend handles this gracefully since `payload.get('organisation_id')` returns `None` for old tokens. This fix is for `set_rls_context_from_jwt()` in flask_app.py to correctly propagate org context to DB connections.

---

## 8. Org Creation — Full Implementation Plan

### 8a. Backend: `POST /api/org/create`

Add to `AI_infrastructure/routes/organisation_credentials_routes.py`:

```python
@org_credentials_bp.route('/create', methods=['POST'])
@require_auth
def create_organisation():
    """POST /api/org/create — Create a new organisation and assign caller as owner.
    Requires user has NO existing organisation_id.
    """
    user_id = g.user_id

    # Check user isn't already in an org
    existing = execute_query(
        "SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s",
        (user_id,), fetch_mode='one'
    )
    if existing and existing.get('organisation_id'):
        return jsonify({'success': False, 'error': 'You are already a member of an organisation'}), 409

    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'success': False, 'error': 'Organisation name is required'}), 400

    # Auto-generate slug from name if not provided
    import re
    slug = data.get('slug') or re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

    # Check slug uniqueness
    existing_slug = execute_query(
        "SELECT id FROM ai_infrastructure.organisations WHERE slug = %s",
        (slug,), fetch_mode='one'
    )
    if existing_slug:
        return jsonify({'success': False, 'error': f'Slug "{slug}" is already taken'}), 409

    # Create the organisation
    new_org = execute_query(
        """INSERT INTO ai_infrastructure.organisations (name, slug, plan_tier, is_active)
           VALUES (%s, %s, 'free', TRUE) RETURNING id, name, slug, plan_tier""",
        (name, slug), fetch_mode='one'
    )

    # Assign the creating user as owner
    execute_query(
        "UPDATE ai_infrastructure.users SET organisation_id=%s, org_role='owner' WHERE id=%s",
        (new_org['id'], user_id)
    )

    logger.info(f"[ORG_CREDS] User {user_id} created org '{name}' (id={new_org['id']})")

    return jsonify({'success': True, 'organisation': new_org}), 201
```

### 8b. Frontend JS Functions

Add to `UI/business-ai-platform-v2.html` near the OrgManager object:

```javascript
function showCreateOrgForm() {
    document.getElementById('orgEmpty').style.display = 'none';
    document.getElementById('orgCreateForm').style.display = 'flex';
    document.getElementById('createOrgName').focus();
}

function hideCreateOrgForm() {
    document.getElementById('orgCreateForm').style.display = 'none';
    document.getElementById('orgEmpty').style.display = 'flex';
    document.getElementById('createOrgName').value = '';
    document.getElementById('createOrgSlug').value = '';
    const desc = document.getElementById('createOrgDescription');
    if (desc) desc.value = '';
}

function updateOrgSlugPreview() {
    const name = document.getElementById('createOrgName').value || '';
    const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    document.getElementById('createOrgSlug').value = slug;
}

async function createOrganisation() {
    const name = (document.getElementById('createOrgName').value || '').trim();
    const slug = (document.getElementById('createOrgSlug').value || '').trim();
    if (!name) { alert('Organisation name is required'); return; }

    const btn = document.getElementById('createOrgBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';

    try {
        const resp = await fetch(`${API_BASE_URL}/api/org/create`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, slug })
        });
        const data = await resp.json();
        if (data.success) {
            hideCreateOrgForm();
            // Reload the org tab to show the new dashboard
            AccountSidebar.loadOrganisationTab();
        } else {
            alert(data.error || 'Failed to create organisation');
        }
    } catch (e) {
        alert('Network error: ' + e.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-plus"></i> Create Organisation';
    }
}
```

---

## 9. Complete Alignment Matrix

| # | Component | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | `organisations` table | Exists with all columns | ✅ 13 columns confirmed | ✅ |
| 2 | `organisation_platform_credentials` | Exists | ✅ 2 rows (pinecone + anthropic) | ✅ |
| 3 | `credential_access_log` | Exists | ✅ | ✅ |
| 4 | `org_invitations` | Exists (migration 026) | ✅ Already in DB | ✅ |
| 5 | `session_members` | Exists | ✅ | ✅ |
| 6 | `synergy_sessions.organisation_id` | Column exists | ✅ | ✅ |
| 7 | `synergy_sessions.visibility` | Column + CHECK constraint | ✅ | ✅ |
| 8 | `users.organisation_id` | Column exists | ✅ | ✅ |
| 9 | `users.org_role` | Column, default 'member' | ✅ | ✅ |
| 10 | `users.is_sub_user` | Column, default false | ✅ | ✅ |
| 11 | `users.parent_user_id` | Column | ✅ | ✅ |
| 12 | DB helper functions (4) | All 4 functions | ✅ All 4 confirmed | ✅ |
| 13 | RLS policies (full set) | Policies on all org/synergy tables | ✅ 22 policies confirmed | ✅ |
| 14 | Role hierarchy (5 levels) | viewer/member/manager/admin/owner | ✅ Consistent in DB, backend, frontend | ✅ |
| 15 | InHouse Print org (id=1) | gerardo linked as owner | ✅ Confirmed in live DB | ✅ |
| 16 | 'valorai' / 'platform' orgs | Referenced in old docs | ❌ Not in live DB (docs outdated) | ⚠️ |
| 17 | 10 users without org | — | ⚠️ All NULL organisation_id | ⚠️ |
| 18 | Org API routes (18 endpoints) | All implemented | ✅ All present | ✅ |
| 19 | `POST /api/org/create` | Required for UI | ❌ Not implemented | ❌ FIX NEEDED |
| 20 | JWT includes `organisation_id` | Required for RLS context | ❌ Missing from jwt payload | ❌ FIX NEEDED |
| 21 | Profile endpoint includes `org_role` | Required for UI gating | ❌ Not included | ❌ FIX NEEDED |
| 22 | `showCreateOrgForm()` JS | Required for org creation | ❌ Not defined | ❌ FIX NEEDED |
| 23 | `createOrganisation()` JS | Required for org creation | ❌ Not defined | ❌ FIX NEEDED |
| 24 | `applyOrgRoleVisibility()` function | Written correctly | ✅ Code is correct, data missing | ⚠️ Blocked by #21 |
| 25 | `require_org_role` decorator | Queries DB for role | ✅ Works independently of JWT | ✅ |
| 26 | `get_user_org_context()` | DB query for org membership | ✅ Works correctly | ✅ |
| 27 | `OrgManager` dashboard JS | All API calls wired | ✅ All methods implemented | ✅ |
| 28 | Old sub-user routes | Still functional | ✅ user_management_routes.py active | ✅ |
| 29 | Synergy session sharing routes | 4 endpoints | ✅ synergy_share_routes.py active | ✅ |
| 30 | `org_credentials_loader.py` | 3-tier resolution | ✅ Complete | ✅ |

---

## 10. Priority Fixes — Ordered by Impact

### Fix 1 — Profile Endpoint (30 min, highest impact)
**File:** `AI_infrastructure/routes/auth_routes.py` → `get_profile()`

Add `organisation_id, org_role, is_sub_user` to the user SELECT query + include in return dict.  
**Unblocks:** Role-gating UI, correct org_role display in sidebar badge, `applyOrgRoleVisibility`.

### Fix 2 — Org Creation (2 hours, enables self-service)
**Files:** `organisation_credentials_routes.py` (new endpoint) + `business-ai-platform-v2.html` (4 JS functions)  
**Unblocks:** Users can create their own organisation from the UI without needing SQL.

### Fix 3 — JWT Org Fields (15 min, best practice)
**File:** `AI_infrastructure/auth/user_auth.py` → `login()`

Extend login SQL to fetch `organisation_id, org_role`. Add to JWT payload.  
**Unblocks:** `set_rls_context_from_jwt()` correctly propagates org_id to DB session variables for RLS.  
**Note:** Existing tokens will lack these fields until users re-login (acceptable — backend handles `None` gracefully).

---

*Report generated from: live DB queries (check_db_state.py) + full code audit of all 6 design documents + all migration SQL + all route files + user_auth.py + auth_routes.py + business-ai-platform-v2.html (full OrgManager + applyOrgRoleVisibility analysis)*
