# Auth, Organisation Setup & Onboarding — UX Flow Design
**Date:** March 23, 2026
**Platform:** ValorAI — Flask + Supabase, deployed per-client on Render

---

## Part 1: Current Login Screen (What Exists Today)

### What the login page shows right now
```
┌─────────────────────────────────────────┐
│       [Valor AI Logo — SVG atom]        │
│            Valor AI                     │
│          AI Synergy Suite               │
│   ✅ Backend connected • Ready to sign  │
│─────────────────────────────────────────│
│   [■ Sign in with Microsoft 365]        │
│   [G Sign in with Google]               │
│              — OR —                     │
│   Username or Email: [______________]   │
│   Password:          [______________]   │
│   [→ Sign In]                           │
└─────────────────────────────────────────┘
```

**Three login paths exist and have full backend wiring:**
1. **Microsoft 365 OAuth** → `GET /api/auth/microsoft/login` → Azure OAuth → `/api/auth/microsoft/callback`
2. **Google OAuth** → `GET /api/auth/google/login` → Google OAuth → `/api/auth/google/callback`
3. **Username/password** → `POST /api/auth/login` → bcrypt check → JWT returned

**What the JWT contains after login (as of March 23, 2026):**
```json
{
  "user_id": 12,
  "username": "gerardo",
  "email": "gerardo@vetsuccessacademy.com",
  "role": "admin",
  "organisation_id": 1,
  "org_role": "owner",
  "org_slug": "valorai",
  "exp": 1711234567
}
```

### What's missing from the current login screen
| Gap | Impact | Priority |
|-----|--------|----------|
| No org name/logo shown | User doesn't know which client's platform they're on | High (for multi-tenant or white-label) |
| No "Welcome back" state (remembers user) | Minor UX friction for daily users | Low |
| No org badge post-login in header | User can't see they're part of "ValorAI Platform" | Medium |
| No user invitation flow | New users can't self-register | High |
| OAuth callback doesn't auto-assign org | Google/M365 users get assigned no org | High |

---

## Part 2: The Deployment Model — Multi-Tenant

**One Render service. One Supabase database. All clients/orgs live in the same database, separated by `organisation_id`.**

```
https://valorai.onrender.com     ← single deployment

Supabase DB: aeazscmhmoipfchuwcih
    ai_infrastructure.organisations
        id=1  slug='valorai'           (ValorAI / platform admin)
        id=2  slug='inhouse-print'     (InHouse Print client)
        id=3  slug='vetsuccessacademy' (VSA client)
        id=4  slug='acme-corp'         ...

    ai_infrastructure.users
        id=12  organisation_id=1  gerardo (owner)
        id=15  organisation_id=2  sarah@inhouseprint.com.au (owner)
        id=16  organisation_id=2  tom@inhouseprint.com.au (member)
        id=20  organisation_id=3  dr.smith@vsa.com (owner)
        ...
```

RLS at the DB layer ensures `organisation_id=2` users can NEVER see `organisation_id=3` data.

### How the login screen knows which org to show

The user has **no way to know** which org they're in from the URL alone (it's the same URL for everyone). So:

1. **Google/M365 OAuth** → the OAuth callback gets their verified email → look up email in `users` → find their `organisation_id` → load their org's name and show it on the post-login header
2. **Username/password** → same: login returns JWT with `org_name` + `org_slug` → show org name post-login
3. **Invite link** → `?invite_token=xyz` — the acceptance screen shows the org name from the invite record BEFORE they log in

**What should show on the login screen** (before authenticating):  
For a shared URL, you cannot show an org name at the login screen — you don't know who they are yet. The login screen stays as "Valor AI / AI Synergy Suite".

**What should show immediately after login:**  
Header badge: `"InHouse Print  [owner]"` — read from JWT `org_name` + `org_role`.

### Org creation flow (multi-tenant)

Orgs are created by the **platform admin** (you, gerardo). Clients don't self-register — you onboard them:

```
1. Platform admin creates org:
   POST /api/admin/org/create
   { "name": "InHouse Print", "slug": "inhouse-print", "plan": "business",
     "allowed_domains": ["inhouseprint.com.au"] }

2. Platform admin creates/seeds the owner user:
   POST /api/admin/org/{org_id}/seed-owner
   { "email": "sarah@inhouseprint.com.au", "temp_password": "...", "role": "owner" }
   — OR —
   Owner just clicks "Sign in with Google" and their domain auto-assigns them (if allowed_domains set)

3. Owner logs in, sees their org in the header
4. Owner goes to Settings → Organisation → Invite Member to add their team
```

Future: `/api/admin/org/create` endpoint needs building. For now, SQL migration (023 style) per client.

---

## Part 3: User Types and Auth Flows

### Flow A — New Client Onboarding (Admin — Current Process)

**Who:** You (gerardo/platform admin), onboarding a new business client.

```
1. In Supabase SQL Editor, run a client-specific SQL seed:
   INSERT INTO ai_infrastructure.organisations
       (name, slug, display_name, plan)
       VALUES ('InHouse Print', 'inhouse-print', 'InHouse Print', 'business');

   -- Optionally set allowed_domains for Google/M365 SSO auto-provisioning:
   UPDATE ai_infrastructure.organisations
   SET allowed_domains = ARRAY['inhouseprint.com.au']
   WHERE slug = 'inhouse-print';

2. Create the owner user (or they sign in with Google/M365 and get auto-provisioned):
   INSERT INTO ai_infrastructure.users
       (username, email, password_hash, organisation_id, org_role)
   SELECT 'sarah', 'sarah@inhouseprint.com.au', crypt('TempPass1!', gen_salt('bf')),
          id, 'owner'
   FROM ai_infrastructure.organisations WHERE slug = 'inhouse-print';

3. Seed org-level credentials (Anthropic, Pinecone, etc for this client's billing):
   INSERT INTO ai_infrastructure.organisation_platform_credentials ...

4. Owner logs in → sees 'InHouse Print [owner]' badge in header
5. Owner goes to Settings → Organisation tab → sees their org, can invite team
```

**Current pain:** Still manual SQL per client. Next priority: `/api/admin/org/create` endpoint.

**Future: Platform admin endpoint** (not built yet)
```
POST /api/admin/org/create
{
  "name": "InHouse Print",
  "slug": "inhouse-print",
  "owner_email": "sarah@inhouseprint.com.au",
  "plan": "business",
  "allowed_domains": ["inhouseprint.com.au"]
}
```

---

### Flow B — New Team Member Invited by Owner (NOT YET BUILT)

**Who:** Staff member at the client's business.

**Desired flow:**
```
1. Owner logs in → Settings → Organisation tab → "Invite Member"
2. Owner enters: email, role (member/manager/admin)
3. Backend:
   - Creates pending row in org_invitations table
   - Sends invite email (SendGrid / Resend)
   - Email contains: "You've been invited to [ClientName]'s workspace on Valor AI"
   - Link: https://valorai-[clientname].onrender.com?invite_token=abc123

4. Recipient clicks link → Platform loads invite-acceptance screen
5. Recipient sees:
   "You've been invited to join [InHouse Print] on Valor AI
    Invited by: gerardo@inhouseprint.com.au
    Role: Team Member"
   
   Options:
   [Sign in with Microsoft 365]   ← if their email is M365
   [Sign in with Google]           ← if their email is Google Workspace
   [Set a password and join]       ← for non-SSO

6. After sign-in:
   - If new user: row created in users table, organisation_id set, org_role from invite
   - If existing user: just update organisation_id and org_role
   - Redirect to main platform

7. Owner sees member in Settings → Organisation → Members list
```

**What needs to be built:**
```
DB: CREATE TABLE ai_infrastructure.org_invitations (
    id SERIAL PRIMARY KEY,
    organisation_id INTEGER REFERENCES ai_infrastructure.organisations(id),
    invited_email TEXT NOT NULL,
    invited_role VARCHAR(50) DEFAULT 'member',
    invite_token UUID DEFAULT gen_random_uuid() NOT NULL UNIQUE,
    invited_by INTEGER REFERENCES ai_infrastructure.users(id),
    accepted_by INTEGER REFERENCES ai_infrastructure.users(id),
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'accepted', 'expired', 'revoked'
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '7 days',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    accepted_at TIMESTAMPTZ
);

Backend routes:
POST /api/org/invite          → create invitation, send email
GET  /api/org/invite/pending  → list pending invites (admin+)
DELETE /api/org/invite/<id>   → revoke/cancel invite (admin+)
GET  /api/auth/accept-invite?token=xyz → validate token, show acceptance screen
POST /api/auth/accept-invite  → finalise: create user + set org

Email template:
Subject: "You've been invited to join [Client Name] on Valor AI"
Body: "Click to join → https://[url]?invite_token=abc123"
Expires in 7 days.
```

---

### Flow C — Google Workspace User (Business Email = Google)

**Scenario:** InHouse Print uses `@inhouseprint.com.au` Google Workspace.

**Current behaviour (broken):**
```
User clicks "Sign in with Google"
→ Authenticates with Google
→ Callback at /api/auth/google/callback
→ Flask tries to find user by email in users table
→ If NOT found: Error or creates user with NO organisation_id
→ User logs in but sees empty platform (no org = no tools, no credentials)
```

**Desired behaviour:**
```
User clicks "Sign in with Google"
→ Authenticates with Google  
→ Flask callback receives verified email: sarah@inhouseprint.com.au
→ Check 1: Does this email already exist in users? → log them in, done
→ Check 2: Does email domain match organisations.allowed_domains?
   - organisations WHERE 'inhouseprint.com.au' = ANY(allowed_domains)
   - Found: organisation_id=1, InHouse Print
→ Auto-provision: INSERT INTO users (email, organisation_id, org_role='member', password_hash='oauth_google')
→ Log them in with org context
→ If no match: Show "Your email domain is not associated with any organisation. 
                       Contact your admin or use your invite link."
```

**DB change needed:**
```sql
ALTER TABLE ai_infrastructure.organisations 
ADD COLUMN allowed_domains TEXT[] DEFAULT '{}';

-- Seed for a client:
UPDATE ai_infrastructure.organisations 
SET allowed_domains = ARRAY['inhouseprint.com.au']
WHERE slug = 'inhouse-print';
```

---

### Flow D — Microsoft 365 User (Business Email = M365)

**Identical logic to Flow C** but via `/api/auth/microsoft/login` → `/api/auth/microsoft/callback`.

Microsoft's OAuth token includes `hd` (hosted domain) or the email domain can be parsed.

The same `allowed_domains` check applies. No separate implementation needed beyond what's described for Google.

---

### Flow E — Returning User (Existing Session)

**What happens now:**
```
User lands on platform URL
→ JavaScript checks localStorage for JWT token
→ Calls GET /api/auth/verify with token in Authorization header
→ If valid: auto-login, show main platform (skip login screen)
→ If expired or missing: show login screen
```

**What org context shows post-login:**
- JWT contains `org_name`, `org_role`, `org_slug` (as of March 23, 2026 fix)
- **None of this is currently displayed in the UI** — the header/profile area doesn't show org info
- Needed: small badge or header element: `"Logged in as gerardo · ValorAI Platform [owner]"`

---

### Flow F — Multi-Role Same Org (e.g. admin vs member)

```
Admin (Sarah) logs in → sees Settings → Organisation (full: credentials, members, vault)
Member (Tom)  logs in → sees Settings → Organisation (limited: only org info card)
Viewer (Guest) logs in → Organisation tab hidden entirely (data-org-min-role enforced in JS)
```

The role gating is fully built in the frontend (`applyOrgRoleVisibility()`) and backend (`_require_org_role()`). No additional work needed here.

---

## Part 4: Post-Login Org Context in the UI

### What should appear after login (to be built)

**Header/topbar — org badge:**
```
┌─────────────────────────────────────────────────────────────┐
│  [ValorAI Logo]   [Threads]  [Chat]   ...  [Profile ▼]      │
│                                        ↑                     │
│                               "InHouse Print  [owner]"       │
└─────────────────────────────────────────────────────────────┘
```

Read from the JWT payload (already available as `window.currentUser` or from localStorage):
```javascript
const orgName = currentUser.org_name;         // "ValorAI Platform"
const orgRole = currentUser.org_role;         // "owner"
const orgSlug = currentUser.org_slug;         // "valorai"
```

**Settings → Profile tab — org membership card:**
```
Organisation
┌─────────────────────────────┐
│  ValorAI Platform           │
│  Your role: Owner           │
│  Plan: Enterprise           │
│  [Go to Organisation Tab →] │
└─────────────────────────────┘
```

**Login screen — org branding** (read from `/api/health` which should return `CLIENT_NAME`):
```
Instead of: "Valor AI / AI Synergy Suite"
Show:       "[Client Logo]
             InHouse Print
             Powered by Valor AI"
```

---

## Part 5: Implementation Priorities

### Tier 1 — Quick wins (≤ 2 hours each)

**1. Show org badge post-login** (multi-tenant: org name comes from JWT, not env var)
- JWT already has `org_name`, `org_role` from the Session 2 login fix
- On successful login, set a header badge element
- Note: login SCREEN stays generic — you don't know the user's org until they authenticate

**2. Show org badge post-login**
- JWT already has `org_name`, `org_role` — just render them in the profile button or topbar
- One-liner in the init function: `document.getElementById('profileOrgBadge').textContent = currentUser.org_name`

**3. `/api/org/info` call after login**
- After successful login, call `GET /api/org/info` and cache the result
- Updates UI with member count, vault status, etc.

### Tier 2 — Critical for multi-user (≤ 1 day each)

**4. `allowed_domains` column + auto-provisioning in Google/M365 callback**
- DB: `ALTER TABLE organisations ADD COLUMN allowed_domains TEXT[]`
- Both OAuth callbacks: add domain check + auto-provision user if domain matches

**5. Invite system (DB + backend)**
- `org_invitations` table (SQL migration)
- `POST /api/org/invite` endpoint
- `GET /api/auth/accept-invite?token=` endpoint
- Email sending via SendGrid or Resend (or just copy link for now)

**6. Invite UI in Organisation tab**
- "Invite Member" button in the Members section
- Opens modal: enter email + select role
- Shows pending invites list with "Revoke" option

### Tier 3 — Polish (≤ half day each)

**7. Invite acceptance screen**
- Special login page variant shown when `?invite_token=xyz` in URL
- Shows who invited them, which org, what role
- SSO buttons pre-configured for the org's email domain

**8. Organisation onboarding wizard** (for future self-service clients)
- Step 1: Create org (name, slug, plan)
- Step 2: Set up owner account
- Step 3: Add first team member or skip
- Step 4: Connect first integration (Xero/Shopify)

---

## Part 6: Database Requirements Summary

### What exists:
```sql
ai_infrastructure.organisations         -- ✅ exists
ai_infrastructure.users                 -- ✅ exists (organisation_id, org_role columns added)
ai_infrastructure.organisation_platform_credentials  -- ✅ exists
ai_infrastructure.credential_access_log -- ✅ exists
ai_infrastructure.user_platform_credentials -- ✅ exists
```

### What needs to be added:
```sql
-- 1. Domain-based SSO auto-provisioning
ALTER TABLE ai_infrastructure.organisations 
ADD COLUMN IF NOT EXISTS allowed_domains TEXT[] DEFAULT '{}';

-- 2. Invite system
CREATE TABLE IF NOT EXISTS ai_infrastructure.org_invitations (
    id SERIAL PRIMARY KEY,
    organisation_id INTEGER NOT NULL REFERENCES ai_infrastructure.organisations(id) ON DELETE CASCADE,
    invited_email TEXT NOT NULL,
    invited_role VARCHAR(50) NOT NULL DEFAULT 'member'
        CHECK (invited_role IN ('viewer', 'member', 'manager', 'admin')),
    invite_token UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
    invited_by INTEGER REFERENCES ai_infrastructure.users(id),
    accepted_by INTEGER REFERENCES ai_infrastructure.users(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'accepted', 'expired', 'revoked')),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '7 days',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    accepted_at TIMESTAMPTZ,
    UNIQUE (organisation_id, invited_email, status)  -- prevent duplicate pending invites
);
```

---

## Part 7: Decision Log

| Decision | Rationale |
|----------|-----------|
| Multi-tenant: one Render + one Supabase, all orgs in same DB | Cheaper to operate, easier to maintain, standard SaaS model. RLS enforces tenant isolation at DB level even if app code has a bug. |
| Google/M365 are primary, password is secondary | Enterprises already use SSO. Password is fallback for team accounts or demo. |
| Auto-provision by email domain (not just invite) | Allows Google Workspace admins to grant access without manual invite per person. Invite flow still needed for external or non-domain emails. |
| Login screen stays generic (no org name before auth) | You cannot know the user's org before they authenticate in a multi-tenant system. Org context is shown AFTER login via JWT data. |
| org_role stored in JWT | Avoids a DB lookup on every request. Stale if role changes — mitigated by short JWT expiry (24h) or explicit token refresh endpoint. |
| Org name in post-login header badge | Clear, minimal UI change. User always knows which org workspace they're in. |
| Invites expire in 7 days | Industry standard. Long enough for async workflows, short enough to prevent stale links. |
| Owner can set vault password | Extra security layer for revealing raw API keys. Not required for normal platform use. |
