# Organisation Credentials Architecture
**Date**: March 2026

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
