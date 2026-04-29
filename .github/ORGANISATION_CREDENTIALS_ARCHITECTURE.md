# Organisation Credentials Architecture
**Date**: March 26, 2026 (Last Updated: April 30, 2026)
**Status**: ✅ Migration 036 complete. All architecture described herein is LIVE in Supabase (platform_catalog, module_catalog, org_module_access, organisation_platform_credentials tables). Full invite system complete (create, email, accept-invite frontend). Vector DB gaps resolved Apr 29 (migrations 044+045, pgvector tools, `_get_vector_provider()`). Account identity panel added Apr 30 (`#account-identity-panel`, `_updateIdentityPanel()`). See `.github/copilot-instructions.md` for complete organization system documentation.

---

## The Problem You're Solving

Your current state (before this work):

```
user_platform_credentials
├── user_id=1, platform=anthropic  ← "platform-wide" hack
├── user_id=1, platform=auspost    ← shared by everyone on env var
├── user_id=2, platform=xero       ← user-specific (correct)
└── user_id=2, platform=google_oauth ← user-specific (correct)
```

**Issues**:
- One set of Anthropic/OpenAI keys for ALL clients → no billing isolation
- AusPost uses `os.getenv('AUSPOST_API_KEY')` → can't have per-client accounts
- No concept of "this key belongs to Acme Corp, not just user 1"
- Anyone who knows how to query the DB can see all keys
- No audit trail of who looked at which key

---

## The Solution: Two-Layer Credential Model

```
Layer 1: USER credentials (personal)       → user_platform_credentials
Layer 2: ORG credentials (organisation)    → organisation_platform_credentials
```

**Layer 1 (unchanged — user-specific)**:
- Google OAuth tokens
- Microsoft OAuth tokens  
- Personal Xero connections
- Any per-person authentication

**Layer 2 (new — org-shared)**:
- Anthropic API key (the whole org uses one key or different keys per client)
- OpenAI API key
- AusPost account
- Stripe keys
- SendGrid
- Any key that belongs to the business, not one person

---

## Database Architecture

```
organisations
├── id, name, slug, plan_tier
└── vault_password_hash  ← bcrypt hash, NULL if no extra lock

users (updated)
├── id, username, email, password_hash
├── organisation_id  ←── LINKS user to their org
└── org_role         ←── viewer | member | manager | admin | owner

organisation_platform_credentials (NEW)
├── id, organisation_id, platform
├── display_name         ← "Production Anthropic Key"
├── credential_value     ← the actual API key (sk-ant-...)
├── credentials JSONB    ← for multi-field platforms
├── visible_to_role      ← who can SEE it exists (masked)
├── reveal_requires_role ← who can REVEAL the plaintext
└── environment          ← production | staging | test

credential_access_log (NEW — immutable audit trail)
├── who (user_id, username)
├── what (action: revealed | added | edited | deleted)
├── which (credential_id, platform, display_name)
├── when (performed_at)
└── vault_password_used (bool)
```

---

## Role Hierarchy

```
viewer   (1) — read-only platform access
member   (2) — standard user
manager  (3) — can SEE credentials exist (masked display)
admin    (4) — can ADD, EDIT, DELETE credentials (still masked on screen)
owner    (5) — can REVEAL plaintext values (+ all above)
```

A credential can override the defaults with `visible_to_role` and `reveal_requires_role`.

---

## The Vault Password

This is the key feature you asked about: **"behind a password so not all users can get into those API keys"**.

```
organisations.vault_password_hash
```

How it works:
1. Owner sets a vault password via `POST /api/org/vault-password`
2. It's stored as a bcrypt hash (never plaintext — even we can't recover it)
3. When anyone tries to REVEAL a credential's value (even another owner), they must supply this password
4. Wrong password → logged + denied
5. Right password → credential value returned + logged

**Visual flow on screen**:
```
[Credentials Panel]
├── Anthropic API Key
│   ├── Value: sk-ant-api03-****...****A3bC
│   └── [Reveal Key]  ← button
│       └── Prompts: "Enter vault password"
│           Input: [_____________]
│           [Cancel]  [Reveal]
│           └── On success: shows actual key for 30 seconds
│               "Copy" button → closes automatically
└── OpenAI Key
    ...
```

---

## Access Decision Flow

```
User clicks "Reveal Key"
        │
        ▼
API: POST /api/org/credentials/<id>/reveal
        │
        ├─ Authenticated? (JWT) ──────────────── No → 401
        │
        ├─ Has organisation? ─────────────────── No → 403
        │
        ├─ org_role >= reveal_requires_role? ─── No → 403 "Requires admin role"
        │                                              (your role: manager)
        ├─ Org has vault_password_hash set?
        │   ├─ Yes → Check supplied vault_password
        │   │         Mismatch → 403 "Incorrect vault password"
        │   │                    + audit log entry (reveal_failed_wrong_password)
        │   └─ No  → Skip vault check
        │
        └─ All passed → Return plaintext value ✅
                        + ALWAYS write to credential_access_log
```

---

## How the Backend Resolves API Keys

In any tool (AusPost, Anthropic, etc.), replace:
```python
# BEFORE (insecure):
api_key = os.getenv('ANTHROPIC_API_KEY')
```

With:
```python
# AFTER (org-aware):
from AI_infrastructure.shared.org_credentials_loader import resolve_api_key

api_key = resolve_api_key(user_id, 'anthropic')
if not api_key:
    return {"error": "Anthropic API key not configured. Ask your org admin to add it in Settings → Credentials."}
```

**Resolution order** (behind the scenes):
```
resolve_api_key(user_id=5, platform='anthropic')
        │
        ├─ 1. Check user_platform_credentials WHERE user_id=5 AND platform='anthropic'
        │      → Not found
        │
        ├─ 2. Find user 5's organisation_id (= 3, "Acme Corp")
        │      Check organisation_platform_credentials WHERE org_id=3 AND platform='anthropic'
        │      → Found: sk-ant-api03-AcmeCorpKey...
        │      → Return this key ✅
        │
        └─ 3. (if org also had nothing)
              Fall back to os.getenv('ANTHROPIC_API_KEY')
              (logs a warning that env var fallback was used)
```

---

## API Endpoints Quick Reference

| Method | Endpoint | Min Role | Description |
|--------|----------|----------|-------------|
| GET | `/api/org/info` | member | Get org name, plan, members count |
| PUT | `/api/org/info` | owner | Update org name, timezone, logo |
| GET | `/api/org/members` | manager | List members + roles |
| PUT | `/api/org/members/<id>/role` | admin | Change a member's role |
| GET | `/api/org/credentials` | manager | List credentials (MASKED) |
| POST | `/api/org/credentials` | admin | Add new credential |
| PUT | `/api/org/credentials/<id>` | admin | Edit credential metadata/value |
| DELETE | `/api/org/credentials/<id>` | admin | Soft-delete credential |
| POST | `/api/org/credentials/<id>/reveal` | admin | **Reveal plaintext** (+ vault pwd) |
| GET | `/api/org/credentials/audit-log` | admin | View who revealed what + when |
| POST | `/api/org/vault-password` | owner | Set/change vault password |
| DELETE | `/api/org/vault-password` | owner | Remove vault password |
| POST | `/api/org/invite` | admin | Create invite (optional inline email via `provider` field: `gmail`/`outlook`) |
| GET | `/api/org/invite/pending` | admin | List pending invitations |
| DELETE | `/api/org/invite/<id>` | admin | Revoke invitation |
| POST | `/api/org/invite/<id>/send-email` | admin | Re-send invite via Gmail or Outlook OAuth |
| GET | `/api/org/invite/accept?token=<uuid>` | none | Validate token, return org name + role (no auth required) |
| POST | `/api/org/invite/accept` | any auth | Accept invite — links logged-in user to org |

---

## What Different Users See

### Member (standard team member)
- Uses the platform normally — org keys work transparently
- Visits Settings → No credentials panel shown

### Manager
- Settings → Credentials panel visible
- Sees: list of platform names + masked values (`sk-ant-****...****A3bC`)
- Cannot add/edit/reveal

### Admin
- Sees: same masked list
- Can: Add new credential, Edit existing, Delete
- Cannot: Reveal actual values

### Owner
- Sees: same masked list
- Can: Everything above + click "Reveal Key" (prompts vault password)
- Can: Set/change vault password
- Can: View full audit log

---

## Multi-Organisation (Multiple Clients)

Each client gets their own org:

```
Organisation: Acme Corp (id=1)
├── Anthropic key: sk-ant-api03-AcmeProd...
├── OpenAI key:    sk-proj-AcmeProd...
└── AusPost key:   AcmeHasTheirOwnAccount

Organisation: TechStart (id=2)
├── Anthropic key: sk-ant-api03-TechStartKey...  ← DIFFERENT key
├── OpenAI key:    (not configured — no AI billing isolation needed)
└── AusPost key:   TechStartAusPostKey

users
├── Alice (org=Acme Corp, role=owner)   → uses Acme Corp credentials
├── Bob   (org=Acme Corp, role=member)  → transparently uses Acme Corp credentials
└── Carol (org=TechStart, role=admin)   → sees ONLY TechStart credentials
```

- Alice cannot see TechStart's credentials (different org)
- Carol cannot see Acme Corp's credentials
- RLS policy at DB level enforces this even if the code has a bug

---

## Files Created

| File | Purpose |
|------|---------|
| `AI_infrastructure/migrations/add_organisations_and_org_credentials.sql` | Database schema migration |
| `AI_infrastructure/routes/organisation_credentials_routes.py` | Flask API endpoints |
| `AI_infrastructure/shared/org_credentials_loader.py` | Credential resolution (3-tier) |

---

## How to Register the Blueprint

In `AI_infrastructure/flask_app.py`, add:

```python
from routes.organisation_credentials_routes import org_credentials_bp
app.register_blueprint(org_credentials_bp)
```

---

## How to Run the Migration

In Supabase SQL Editor or psql:

```sql
\i AI_infrastructure/migrations/add_organisations_and_org_credentials.sql
```

**What it does** (all idempotent):
1. Creates `organisations` table
2. Adds `organisation_id` + `org_role` to `users`
3. Creates `organisation_platform_credentials`
4. Creates `credential_access_log`
5. Creates helper functions (`mask_credential`, `get_role_level`, etc.)
6. Enables RLS policies
7. Seeds a default "Platform" org and links user_id=1 as owner

---

## Migrating Existing Credentials

After running the migration, move platform-wide keys from the legacy setup:

```sql
-- 1. Create your first real organisation
INSERT INTO ai_infrastructure.organisations (name, slug, plan_tier)
VALUES ('Your Company', 'your-company', 'enterprise');

-- 2. Move the Anthropic key from user_id=1 to the org
INSERT INTO ai_infrastructure.organisation_platform_credentials
    (organisation_id, platform, display_name, credential_value, created_by_user_id)
SELECT
    (SELECT id FROM ai_infrastructure.organisations WHERE slug = 'your-company'),
    'anthropic',
    'Production Anthropic Key',
    credential_value,  -- or from credentials->>'api_key'
    1
FROM ai_infrastructure.user_platform_credentials
WHERE user_id = 1 AND platform = 'anthropic';

-- 3. Link your users to the org
UPDATE ai_infrastructure.users
SET organisation_id = (SELECT id FROM ai_infrastructure.organisations WHERE slug = 'your-company'),
    org_role = 'owner'
WHERE id = 1;

-- 4. Once tested, you can remove the legacy user_id=1 shared credentials
-- (keep them for now as a safety net while you verify the new system works)
```

---

## Testing Checklist

- [ ] Run SQL migration (no errors)
- [ ] Blueprint registered in flask_app.py
- [ ] `GET /api/org/info` returns org details for logged-in user
- [ ] `GET /api/org/credentials` returns masked values (not plaintext)
- [ ] Add a test Anthropic credential via `POST /api/org/credentials`
- [ ] Member user gets 403 when hitting credentials endpoint
- [ ] Manager user can list but not reveal
- [ ] `POST /api/org/credentials/<id>/reveal` without vault password works when no vault password set
- [ ] Set vault password, confirm reveal now requires it
- [ ] Wrong vault password → logged + denied
- [ ] `resolve_api_key(user_id, 'anthropic')` returns org key
- [ ] Audit log shows the reveal event with correct username + timestamp
- [ ] User from different org cannot see this org's credentials (RLS test)

---

## Bug Audit — March 26, 2026
**Status: ALL BUGS FIXED**

A full cross-system audit was performed across `organisation_credentials_routes.py`, `business-ai-platform-v2.html`, and `UI/modules_internal/components/account_profile.js`. The following bugs were found and fixed.

---

### BUG-1 (CRITICAL) — Org tab completely broken: ALL org API calls missing `Authorization` header
**Files**: `UI/modules_internal/components/account_profile.js`  
**Severity**: Critical — org tab showed a permanently broken/empty state for every user  
**Root cause**: Every function in `account_profile.js` that calls `/api/org/*` was sending unauthenticated requests. All backend endpoints require `@require_auth` → every call returned 401.  
**Fixed**: Added `Authorization: Bearer <authToken>` header to all 8 affected calls:

| Function | Endpoint | Method |
|---|---|---|
| `loadOrgTab()` | `/api/org/info` | GET |
| `saveOrgSettings()` | `/api/org/info` | PUT |
| `createOrganisation()` | `/api/org/info` | POST |
| `loadOrgMembers()` | `/api/org/members` | GET |
| `removeMemberFromOrg()` | `/api/org/members/:id` | DELETE |
| `inviteOrgMember()` | `/api/org/invite` | POST |
| `loadOrgInvitations()` | `/api/org/invite/pending` | GET |
| `revokeOrgInvite()` | `/api/org/invite/:id` | DELETE |

---

### BUG-2 (HIGH) — User role always displayed as "—" in org header card
**Files**: `UI/modules_internal/components/account_profile.js` (`_renderOrgDashboard`)  
**Severity**: High — user's org role was invisible; Save Settings button incorrectly hidden for admins  
**Root cause**: `_renderOrgDashboard(org)` received `data.organisation` (which has no `your_role` field). The API response has `your_role` at the **root level** (`data.your_role`), not nested inside `data.organisation`. So `org.your_role` was always `undefined`.  
**Fixed**: In `loadOrgTab()`, merged `data.your_role` into `_orgData` before passing to the render function:
```javascript
_orgData = data.organisation;
if (data.your_role) _orgData.your_role = data.your_role;  // ← fix
```
This also fixed the Save Settings button visibility check (`['owner','admin'].includes(org.your_role)`).

---

### BUG-3 (HIGH) — Module catalog never loads: `localStorage.getItem('auth_token')` typo in `loadModuleCatalog()`
**Files**: `UI/business-ai-platform-v2.html` (`OrgManager.loadModuleCatalog`)  
**Severity**: High — clicking "Modules" subtab always showed an error; org admins could not enable/disable modules  
**Root cause**: Snake_case key `'auth_token'` returns `null` from localStorage. The app-wide standard is camelCase `'authToken'`. The fetch sent an empty Bearer token → 401.  
**Fixed**: Changed `localStorage.getItem('auth_token')` → `localStorage.getItem('authToken')`.

---

### BUG-4 (HIGH) — Team IDs never load: `localStorage.getItem('auth_token')` typo in `loadTeamIdCheckboxList()`
**Files**: `UI/business-ai-platform-v2.html` (`loadTeamIdCheckboxList`)  
**Severity**: High — team ID selection in any form requiring team filtering was always empty  
**Root cause**: Same snake_case typo as BUG-3. The function had a partial fallback `window.UserAuth?.token || localStorage.getItem('auth_token')` — the fallback would work if `UserAuth` was set, but not otherwise.  
**Fixed**: Changed to `window.UserAuth?.token || localStorage.getItem('authToken') || ''`.

---

### BUG-5 (MEDIUM) — InHouse Kanban module gating silently broken
**Files**: `UI/business-ai-platform-v2.html` (sidebar HTML)  
**Severity**: Medium — `MODULE_GATE_MAP` referenced `[data-module="inhouse_kanban"]` but no sidebar button with that attribute existed; the module could never be hidden even when disabled in the org  
**Root cause**: The sidebar button was never added to the HTML when the InHouse Kanban tab was built. All other optional modules (woocommerce, vsa_veterinary) had their buttons.  
**Fixed**: Added the missing sidebar button (hidden by default):
```html
<button class="sidebar-icon-btn" data-tab="inhouse-kanban" data-module="inhouse_kanban"
    title="InHouse Kanban" style="display:none">
    <i class="fas fa-columns"></i>
</button>
```

---

### BUG-6 (MEDIUM) — Org subtab buttons (Vault, Modules, Audit) visible to all roles
**Files**: `UI/modules_internal/components/account_profile.js` (new `_gateOrgSubTabs()` function)  
**Severity**: Medium — viewers and members saw "Vault", "Modules", and "Audit" buttons in the org panel; clicking them showed empty or broken panels since the data-loading was already role-gated but the buttons were not  
**Root cause**: `switchOrgSubTab()` correctly gates data *loading* by role (e.g., only admin+ can trigger `loadAuditLog()`), but the button visibility was never set — all 6 buttons rendered unconditionally.  
**Fixed**: Added `_gateOrgSubTabs(userRole)` called from `loadOrgTab()` after role is known. Hides buttons per role:

| Subtab | Minimum role to see |
|---|---|
| Vault | `manager` (3) |
| Modules | `member` (2) |
| Audit | `admin` (4) |

```javascript
function _gateOrgSubTabs(userRole) {
    const ROLE_LEVELS = { viewer: 1, member: 2, manager: 3, admin: 4, owner: 5 };
    const level = ROLE_LEVELS[userRole] || 0;
    const rules = { vault: 3, modules: 2, audit: 4 };
    Object.entries(rules).forEach(([subtab, minLevel]) => {
        const btn = document.querySelector(`.org-sub-tab[data-subtab="${subtab}"]`);
        if (btn) btn.style.display = level >= minLevel ? '' : 'none';
    });
}
```

---

### Items NOT Fixed (Handled Separately)
| Item | Reason |
|---|---|
| Team management section (member list rendering, role-change UI, member count) | Being handled in a separate chat session |
| `tab-vsa-veterinary-alerts` orphaned tab (no sidebar link, no module catalog entry) | Tracked in `MODULE_VISIBILITY_ARCHITECTURE.md` pending items |
| Zone 2 sidebar still driven by `manifest.json` instead of DB catalog | Tracked in `MODULE_VISIBILITY_ARCHITECTURE.md` pending items |

---

## Critical Framework Fixes — April 8, 2026

Three infrastructure bugs discovered and fixed that were blocking the invite system (and silently affecting the entire codebase).

---

### FIX-1 (CRITICAL) — `execute_query` raises `ProgrammingError` on DML without RETURNING
**File**: `AI_infrastructure/shared/database_utils.py`  
**Impact**: Every `execute_query("UPDATE ...")` or `execute_query("DELETE ...")` call using the default `fetch_mode='all'` raised `ProgrammingError: no results to fetch` in psycopg2 2.9.9, because `cursor.fetchall()` cannot be called on DML without a RETURNING clause. This silently broke every UPDATE/DELETE on any route that didn’t use `fetch_mode=None`.  
**Fix**: After `cursor.execute()`, check `cursor._cursor.description is None` to detect DML. If DML and no RETURNING: return `[]` and call `conn.commit()`. Works for all `fetch_mode` variants.

---

### FIX-2 (CRITICAL) — INSERT+RETURNING phantom commits (data persists in result but rolls back on pool return)
**File**: `AI_infrastructure/shared/database_utils.py`  
**Impact**: `PooledConnection.close()` ALWAYS calls `self._conn.rollback()` before returning the connection to the pool (to prevent aborted transaction state from leaking). Any `INSERT ... RETURNING` query had its RETURNING row delivered to the caller’s Python code, but the INSERT itself was then rolled back when the connection was released. Callers received the new record’s ID but the row never existed in the database.  
**Fix**: `execute_query` now calls `conn.commit()` for any DML statement (detected via `cursor._cursor.statusmessage` prefix `INSERT`/`UPDATE`/`DELETE`), committing the transaction before returning control.

---

### FIX-3 (CRITICAL) — Recursive trigger on `org_invitations` causes stack overflow
**File**: `AI_infrastructure/migrations/041_fix_invite_trigger_recursion.sql` (+ applied directly to production Supabase)  
**Impact**: `trg_expire_invitations` fired AFTER INSERT OR UPDATE on `org_invitations`, then called `expire_pending_invitations()`, which ran `UPDATE org_invitations SET status='expired' WHERE ...` — which re-fired the trigger infinitely. Every `INSERT` or `UPDATE` on `org_invitations` raised `ERROR: stack depth limit exceeded`.  
**Fix**: Recreated trigger with `WHEN (pg_trigger_depth() = 0)` condition so it only fires on top-level statements, not recursive calls from within the trigger function.

```sql
-- Migration 041 (idempotent)
DROP TRIGGER IF EXISTS trg_expire_invitations ON ai_infrastructure.org_invitations;
CREATE TRIGGER trg_expire_invitations
    AFTER INSERT OR UPDATE ON ai_infrastructure.org_invitations
    FOR EACH STATEMENT
    WHEN (pg_trigger_depth() = 0)
    EXECUTE FUNCTION ai_infrastructure.expire_pending_invitations();
```

---

## Invite System — Complete (April 8, 2026)

### Full End-to-End Flow

```
1. Admin: POST /api/org/invite  { email, role, provider? }
   └─ Creates row in org_invitations with UUID token + 7-day expiry
   └─ If provider='gmail'  → gmail_send_email() via Gmail OAuth token
   └─ If provider='outlook' → microsoft_outlook_send_email() via M365 OAuth token
   └─ Returns { success, invite_id, accept_url, email_sent, email_error }
        accept_url = '/?accept_invite=<uuid>'

2. Recipient opens link /?accept_invite=<uuid>
   └─ Frontend (initializeApp): reads urlParams.get('accept_invite')
   └─ Stores token in sessionStorage('pendingInviteToken')
   └─ Removes param from URL (window.history.replaceState)

3. Login (any method: email/password, OAuth, stored token)
   └─ After showMainApp() succeeds, calls checkPendingInvite()
   └─ Reads + clears sessionStorage('pendingInviteToken')
   └─ Calls handleAcceptInvite(token)

4. handleAcceptInvite(token)
   └─ GET /api/org/invite/accept?token=<uuid>  (no auth required)
        Returns: { org_name, invited_role, invited_email, expires_at }
   └─ Shows _showInviteAcceptDialog(orgName, role, onAccept)
        Modal: "You have been invited to join OrgName as member. [Decline] [Accept]"

5. User clicks Accept
   └─ POST /api/org/invite/accept  { token }  (requires JWT)
        Backend checks: email match, status=pending, not expired
        SET users.organisation_id + org_role
        SET invitations.status='accepted'
   └─ On success: success message shown, loadUserProfile() called (profile reflects new org)
   └─ On error: inline error in dialog (e.g. email mismatch, expired, already accepted)
```

### Backend Routes

| Route | Auth | Description |
|-------|------|-------------|
| `POST /api/org/invite` | admin | Create invite; optional inline email via `provider` field |
| `GET /api/org/invite/pending` | admin | List all pending invites |
| `DELETE /api/org/invite/<id>` | admin | Revoke invite (sets `status='revoked'`) |
| `POST /api/org/invite/<id>/send-email` | admin | Re-send email for existing invite |
| `GET /api/org/invite/accept?token=<uuid>` | none | Validate token; returns org info for accept dialog |
| `POST /api/org/invite/accept` | any auth | Accept invite; links user to org |

### Frontend JS Functions (all in `account_profile.js`)

```javascript
checkPendingInvite()           // Called after every login path; reads sessionStorage
handleAcceptInvite(token)      // Validates token, shows accept dialog
_showInviteAcceptDialog(...)   // Modal: org name + role + Accept/Decline buttons
_showInviteNotice(type, ...)   // Simple info/error notice modal for invalid tokens
```

### Email Content (sent via OAuth)

```
Subject: You're invited to join {org_name}

Hi,

You've been invited to join {org_name} as {role}.

Click the link below to accept:
{accept_url}

This invite expires in 7 days.
```

--- — March 26, 2026
**Migration 039 — Status: IMPLEMENTED**

Extends the existing two-tier module system (plan tier → org override) with a
third tier: per-user restrictions applied on top of the org setting.

---

### Hierarchy (three tiers)

```
Developer / Platform Admin
  └── Sets plan_tier on org (free / starter / professional / enterprise)
  └── Seeds module_catalog with min_plan_tier per module
  └── Can force-enable modules via org_module_access INSERT

Org Owner / Admin
  └── Toggles modules ON/OFF for the WHOLE organisation
      (within what their plan tier permits)
  └── Can additionally RESTRICT specific members from individual modules
      via the new "Manage Modules" button in Settings → Members

Org Member
  └── Sees whatever modules the org has enabled
      MINUS any modules an admin has restricted for them specifically

---

### New Database Table: `ai_infrastructure.user_module_access`

Created by Migration 039. Stores only *restriction* rows — absence = inherit from org.

```sql
CREATE TABLE IF NOT EXISTS ai_infrastructure.user_module_access (
    user_id         INT  NOT NULL REFERENCES ai_infrastructure.users(id) ON DELETE CASCADE,
    organisation_id INT  NOT NULL REFERENCES ai_infrastructure.organisations(id) ON DELETE CASCADE,
    module_name     VARCHAR(100) NOT NULL,
    is_enabled      BOOLEAN NOT NULL DEFAULT FALSE,
    set_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    set_by          INT REFERENCES ai_infrastructure.users(id) ON DELETE SET NULL,
    PRIMARY KEY (user_id, module_name)
);
```

**Design principle:** A row only exists when a user is *restricted* (`is_enabled=FALSE`).
If no row exists, that user inherits the org's setting. This means:
- Pre-039 users are unaffected — fallback to `get_org_enabled_modules()` works automatically
- Restricting then un-restricting a user deletes the row (back to org default)
- You cannot grant a user access beyond what the org has enabled

---

### New API Endpoints (Member Module Management)

All require `admin` role minimum. Prefix: `/api/org/`

| Method | Path | Body | Description |
|--------|------|------|-------------|
| GET | `/api/org/members/<id>/modules` | — | Returns all org modules with per-user enabled state |
| PUT | `/api/org/members/<id>/modules/<name>` | `{"enabled": true/false}` | `true` = remove restriction; `false` = add restriction |
| DELETE | `/api/org/members/<id>/modules` | — | Reset all restrictions for this member (back to org defaults) |

**GET response shape:**
```json
{
  "success": true,
  "user_id": 42,
  "modules": [
    { "module_name": "shopify",  "display_name": "Shopify",  "is_enabled": true  },
    { "module_name": "xero",     "display_name": "Xero",     "is_enabled": false }
  ]
}
```

---

### Backend Resolver: `get_user_enabled_modules(user_id)`

**File:** `AI_infrastructure/shared/org_credentials_loader.py`

```python
def get_user_enabled_modules(user_id: int) -> set:
    # Step 1: Get what the org has enabled
    org_modules = get_org_enabled_modules(user_id)
    # Step 2: Subtract any user-specific restrictions
    # Rows in user_module_access where is_enabled=FALSE are restrictions
    # Returns set of module_name strings
```

`GET /api/org/modules` now calls `get_user_enabled_modules()`, so every user automatically gets their personalised filtered set.

---

### Frontend: "Manage Modules" per Member

In **Org Settings → Members tab**, each member row has a puzzle-piece icon button.
Clicking it expands a panel showing all org-enabled modules as checkboxes.
- Checked = user has access (default)
- Unchecked = user is restricted

JS functions added to `account_profile.js`:
- `toggleMemberModulesPanel(userId)` — fetches and renders the panel
- `setMemberModuleAccess(userId, moduleName, enabled)` — calls PUT endpoint
- `resetMemberModuleAccess(userId)` — calls DELETE endpoint, re-renders panel

---

## Module System — Developer & User Guide
**Last Updated: March 27, 2026**

This section is the authoritative reference for how modules work end-to-end: how they are defined, how they are enabled for organisations, how they are restricted per-user, and what gaps still remain on the frontend side.

---

### How a Module Gets to a User's Sidebar — The Full Chain

```
1. PLATFORM       module_catalog row exists with min_plan_tier
2. PLAN           org.plan_tier >= module.min_plan_tier  →  module is "available"
3. ORG ADMIN      org_module_access row with is_enabled=TRUE  →  module is "active for org"
4. USER ADMIN     user_module_access row with is_enabled=FALSE  →  user is "restricted"
5. FRONTEND       GET /api/org/modules  →  returns user's final enabled set
6. SIDEBAR ⚠️     initModulesFromOrg() reads the response and shows/hides items
                  ← THIS STEP IS NOT YET IMPLEMENTED (see Module Redesign Spec)
```

**Right now, steps 1–5 work correctly.** Step 6 — wiring the DB response to actual sidebar
visibility — is the pending work documented in `.github/MODULE_REDESIGN_SPEC.md`.

---

### How to Enable a Module for an Organisation (Backend)

#### Option A: Via the UI (recommended for day-to-day)
1. Log in as `admin` or `owner` of the org
2. Go to **Settings → Organisation → Modules** subtab
3. Find the module in the catalog
4. Toggle the switch to ON
5. The `PUT /api/org/modules/<module_name>` endpoint writes to `org_module_access`

#### Option B: Via SQL (for initial setup / bulk operations)
```sql
-- Enable a single module for an org
INSERT INTO ai_infrastructure.org_module_access
    (organisation_id, module_name, is_enabled, enabled_at, enabled_by)
VALUES
    (1, 'shopify', TRUE, NOW(), <admin_user_id>)
ON CONFLICT (organisation_id, module_name)
DO UPDATE SET is_enabled = TRUE, enabled_at = NOW();

-- Enable ALL professional modules for org 1
INSERT INTO ai_infrastructure.org_module_access
    (organisation_id, module_name, is_enabled, enabled_at)
SELECT 1, module_name, TRUE, NOW()
FROM ai_infrastructure.module_catalog
WHERE min_plan_tier IN ('free','starter','professional')
  AND is_active = TRUE
ON CONFLICT (organisation_id, module_name) DO UPDATE SET is_enabled = TRUE;

-- Disable a module
UPDATE ai_infrastructure.org_module_access
SET is_enabled = FALSE, enabled_at = NOW()
WHERE organisation_id = 1 AND module_name = 'shopify';
```

#### Option C: Via the API (programmatic / migration scripts)
```powershell
# Requires admin JWT token
$token = "<your_jwt>"
Invoke-RestMethod -Uri "http://localhost:5000/api/org/modules/shopify" `
    -Method PUT `
    -Headers @{ Authorization="Bearer $token"; 'Content-Type'='application/json' } `
    -Body '{"enabled": true}'
```

---

### How to Add a Brand-New Module to the Catalog

#### Step 1: Create the DB catalog entry (required)
```sql
INSERT INTO ai_infrastructure.module_catalog (
    module_name,        -- snake_case, unique key used everywhere
    display_name,       -- shown in UI
    description,        -- shown in Modules panel
    icon_class,         -- FontAwesome class e.g. "fas fa-chart-bar"
    icon_color,         -- hex color e.g. "#3B82F6"
    category,           -- "core" | "ecommerce" | "finance" | "ai" | "operations" | "dev"
    min_plan_tier,      -- "free" | "starter" | "professional" | "enterprise"
    required_platforms, -- ARRAY of platform_name strings from platform_catalog
    sort_order          -- lower = higher in list
) VALUES (
    'my_new_module',
    'My New Module',
    'What it does in one sentence',
    'fas fa-star',
    '#F59E0B',
    'operations',
    'professional',
    ARRAY[]::TEXT[],    -- no platform credentials required, or ARRAY['shopify']
    50
);
```

Once this row exists, the module catalog API (`GET /api/org/modules/catalog`) returns
it, and org admins can enable it via the Modules panel.

#### Step 2: Create the module folder structure (required for backend tools)
```
UI/modules_external/my-new-module/
├── manifest.json               ← module metadata (id, icon, capabilities)
├── my-module.js                ← frontend: V4 composition pattern
├── my-module.css               ← CSS: only module-specific overrides
├── routes/
│   └── blueprint.py            ← Flask Blueprint, auto-discovered by loader
├── tools/
│   └── my_tools.json           ← AI tool definitions
└── implementations/
    └── my_wrapper.py           ← AI tool implementations (@tool_executor)
```

#### Step 3: Add to `DYNAMIC_MODULES` in `initModulesFromOrg()` ← **NOT YET ACTIVE**
Until the frontend redesign (Step 6 in the chain above) is complete, also add to
`UI/modules_external/manifest.json` so the static loader renders the sidebar icon.

---

### How to Restrict a Module for a Specific User

#### Option A: Via the UI (recommended)
1. Log in as `admin` or `owner`
2. Go to **Settings → Organisation → Members**
3. Click the puzzle-piece icon on a member row
4. Uncheck the modules you want to restrict for that user
5. Done — takes effect immediately on next page load for that user

#### Option B: Via SQL
```sql
-- Restrict a user from the shopify module
INSERT INTO ai_infrastructure.user_module_access
    (user_id, organisation_id, module_name, is_enabled, set_by)
VALUES
    (42, 1, 'shopify', FALSE, <admin_user_id>)
ON CONFLICT (user_id, module_name) DO UPDATE SET is_enabled = FALSE;

-- Remove restriction (restore to org default)
DELETE FROM ai_infrastructure.user_module_access
WHERE user_id = 42 AND module_name = 'shopify';
```

---

### How to Verify What Modules a User Can Access

```sql
-- What does the org have enabled?
SELECT module_name, is_enabled
FROM ai_infrastructure.org_module_access
WHERE organisation_id = 1 AND is_enabled = TRUE;

-- What restrictions does user 42 have?
SELECT module_name, is_enabled
FROM ai_infrastructure.user_module_access
WHERE user_id = 42;

-- What is user 42's FINAL effective set?
-- (org enabled MINUS user restrictions)
SELECT oma.module_name
FROM ai_infrastructure.org_module_access oma
WHERE oma.organisation_id = 1
  AND oma.is_enabled = TRUE
  AND oma.module_name NOT IN (
      SELECT module_name FROM ai_infrastructure.user_module_access
      WHERE user_id = 42 AND is_enabled = FALSE
  );
```

Or hit the API:
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/org/modules" `
    -Headers @{ Authorization="Bearer <user_jwt>" }
# Returns the user's personalised filtered module set
```

---

### What the Frontend Currently Does (and Doesn't Do)

| Behaviour | Status |
|-----------|--------|
| Org admin toggles module ON in Modules panel | ✅ Works — writes to `org_module_access` |
| Admin restricts user from a module via puzzle-piece button | ✅ Works — writes to `user_module_access` |
| `GET /api/org/modules` returns user-filtered set | ✅ Works — calls `get_user_enabled_modules()` |
| Sidebar shows/hides items based on enabled modules | ❌ **NOT IMPLEMENTED** — `initModulesFromOrg()` not yet wired |
| WooCommerce tab gated by `woocommerce` module toggle | ❌ **NOT IMPLEMENTED** — hardcoded always visible |
| Zone 2 sidebar icons driven by DB instead of manifest.json | ❌ **NOT IMPLEMENTED** — still uses static file |

> **See `.github/MODULE_REDESIGN_SPEC.md` for the full specification and implementation plan for the frontend wiring.**
      (no individual grant-beyond-org — org is always the ceiling)
```

---

### Resolution Logic

```
GET /api/org/modules  (called by every logged-in user)
        │
        ▼
get_user_enabled_modules(user_id)
        │
        ├─ 1. get_org_enabled_modules(user_id)
        │      ├─ Plan-tier defaults (plan_modules table)
        │      └─ Org overrides (org_module_access table)
        │
        └─ 2. Apply user restrictions
               SELECT module_name FROM user_module_access
               WHERE user_id = X AND is_enabled = FALSE
               → discard each restricted module from set

        Returns: final set of modules this specific user can access
```

---

### Database: `user_module_access` table

```
user_module_access
├── user_id          INT  → FK users.id  CASCADE DELETE
├── organisation_id  INT  → FK organisations.id  CASCADE DELETE
├── module_name      VARCHAR(100)
├── is_enabled       BOOLEAN               ← always FALSE (restriction rows only)
├── set_at           TIMESTAMPTZ
└── set_by           INT  → FK users.id   (the admin who created the restriction)

PK: (user_id, module_name)
```

**Key point**: Only `is_enabled=FALSE` rows exist in practice. Absence of a row
means "inherit org setting" (full access if org has it). This keeps the table small
and the logic simple.

---

### New API Endpoints

| Method | Path | Min Role | Description |
|--------|------|----------|-------------|
| GET | `/api/org/members/<id>/modules` | admin | List org-enabled modules with per-user access state |
| PUT | `/api/org/members/<id>/modules/<name>` | admin | Restrict (`enabled=false`) or restore (`enabled=true`) |
| DELETE | `/api/org/members/<id>/modules` | admin | Reset ALL restrictions for a member (restore org defaults) |

**GET response shape:**
```json
{
  "success": true,
  "user_id": 5,
  "username": "Alice",
  "modules": [
    {
      "module_name":     "shopify",
      "display_name":    "Shopify",
      "icon_class":      "fab fa-shopify",
      "icon_color":      "#96bf48",
      "org_enabled":     true,
      "user_restricted": false,
      "effective":       true
    },
    {
      "module_name":     "xero",
      "display_name":    "Xero Accounting",
      "org_enabled":     true,
      "user_restricted": true,
      "effective":       false
    }
  ]
}
```

Only org-enabled modules appear — admins cannot grant modules the org doesn't have.

**PUT body:** `{ "enabled": true | false }`
- `enabled: false` → writes restriction (user loses access)
- `enabled: true`  → deletes restriction row (user inherits org access again)

---

### Frontend: Members Panel

In **Settings → Organisation → Members**, admins (and owners) now see a
**puzzle-piece button** on each manageable member row.

Clicking it toggles an **inline expandable panel** below that member showing:
- All org-enabled modules
- A checkbox per module (checked = user can access, unchecked = restricted)
- A "Reset to org defaults" button that clears all restrictions

The panel is live-updating — unchecking a module calls the PUT endpoint immediately
and updates the label inline without reloading.

**JS functions (all exported to `window`):**
```javascript
toggleMemberModulesPanel(userId)          // Open/close the panel; fetches live data on open
setMemberModuleAccess(userId, module, enabled) // PUT restriction or restore
resetMemberModuleAccess(userId)           // DELETE all restrictions for member
```

---

### Files Changed (Migration 039)

| File | Change |
|------|--------|
| `AI_infrastructure/migrations/039_user_module_access.sql` | **NEW** — creates `user_module_access` table + indexes |
| `AI_infrastructure/shared/org_credentials_loader.py` | **NEW** `get_user_enabled_modules()` — applies user restrictions on top of org set |
| `AI_infrastructure/routes/organisation_credentials_routes.py` | Updated `get_org_modules()` to call `get_user_enabled_modules()`; added 3 new member-module routes |
| `UI/modules_internal/components/account_profile.js` | Updated `loadOrgMembers()` member row template; added `toggleMemberModulesPanel()`, `setMemberModuleAccess()`, `resetMemberModuleAccess()` |

---

### Backward Compatibility

- **Pre-migration 039**: `get_user_enabled_modules()` catches the missing-table exception and falls back to `get_org_enabled_modules()` — existing behaviour preserved.
- **No impact on module catalog page**: `GET /api/org/modules/catalog` still shows org-level toggles (not affected by user restrictions — admins always see the full org state).
- **`loadAndApplyOrgModules()` in the frontend**: No change needed — it already calls `GET /api/org/modules` which now returns user-filtered results automatically.

---

## Changelog & TODO

### Last Updated: April 8, 2026

#### Recent Changes
- ✅ **April 8** — Full accept-invite frontend: `checkPendingInvite()`, `handleAcceptInvite()`, `_showInviteAcceptDialog()`, `_showInviteNotice()` in `account_profile.js`; `?accept_invite=<token>` URL detection in `initializeApp()` across all three login paths; token validated against backend before showing dialog
- ✅ **April 8** — `execute_query()` DML bug fixed (`database_utils.py`): DML without RETURNING no longer raises; INSERT+RETURNING now commits (was silently rolled back by connection pool)
- ✅ **April 8** — Recursive trigger `trg_expire_invitations` fixed with `WHEN (pg_trigger_depth() = 0)`; migration `041_fix_invite_trigger_recursion.sql` created
- ✅ **April 8** — `POST /api/org/invite` rewritten with `provider` field; inline Gmail/Outlook email sending; HTML form updated with "Send via" dropdown
- ✅ **March 26** — BUG-1–6 fixed (all org API calls now authenticated; role display; auth_token typos; InHouse Kanban sidebar button; org subtab role gating)
- ✅ **March 26** — Per-user module access (Migration 039): `user_module_access` table, `get_user_enabled_modules()`, member puzzle-piece toggle UI
- ✅ **March 26** — Migration 036: `platform_catalog` (27 platforms) + `module_catalog` (26 modules) + DB-driven credential form
- ✅ **March 26** — Credential encryption at rest: `credential_crypto.py` Fernet AES-128-CBC + `enc:v1:` prefix; `CREDENTIAL_ENCRYPTION_KEY` env var

#### TODO

**ACTIVE — Frontend Sidebar Gating (Not Yet Wired):**
- [ ] Implement `initModulesFromOrg()` in `business-ai-platform-v2.html` — see [MODULE_VISIBILITY_ARCHITECTURE.md](./MODULE_VISIBILITY_ARCHITECTURE.md) Section 6
- [ ] Gate WooCommerce `tab-sales` sidebar button + content behind `data-module="woocommerce"` attribute
- [ ] Replace `manifest.json` Zone 2 sidebar rendering with DB-driven `initModulesFromOrg()` call

**MEDIUM — Remaining Gaps:**
- [ ] **GAP-M4** — Audit Shopify/Xero integration tables for `organisation_id` FK isolation
- [ ] **GAP-E2** — Sub-user role restrictions (can’t promote above parent’s role)
- [ ] **GAP-E3** — Sub-user credential vault access (inherit parent’s credentials, read-only)

**LOW — Polish & Hardening:**
- [ ] **GAP-L2** — Scheduled key rotation reminders (APScheduler + email)
- [ ] **GAP-L3** — "Test Connection" button + `POST /api/org/credentials/<id>/test` endpoint
- [ ] **GAP-L5** — Wire DeepSeek into `resolve_api_key` path (currently env-var only)

**RESOLVED (closed):**
- ✅ Invite system: create, email, accept-invite frontend (April 8, 2026)
- ✅ Credential encryption at rest — Fernet `enc:v1:` (GAP-L7)
- ✅ `execute_query` DML commit bug + phantom INSERT (April 8, 2026)
- ✅ Recursive trigger on `org_invitations` (April 8, 2026)
- ✅ GAP-C1 through GAP-C4, GAP-H1 through GAP-H5, GAP-M1, GAP-M2, GAP-M3, GAP-M5, GAP-M6, GAP-L6

#### Related Files (Keep These 3 as Source of Truth)
- `../MODULE_VISIBILITY_ARCHITECTURE.md` — Module visibility model, sidebar gating, 4-layer framework
- `../ORG_DOCUMENTATION_AND_UI_ALIGNMENT_SUMMARY_MAR28_2026.md` — Organisation table schema, UI forms, API endpoints
- `../ORG_CREDENTIALS_MASTER_ANALYSIS.md` — Credentials, vault, multi-tenancy, RLS, role hierarchy, gap registry
