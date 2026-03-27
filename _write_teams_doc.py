"""One-shot script: rewrite TEAMS_SYSTEM_EMAIL_MODEL.md with current accurate implementation docs."""
import pathlib

content = r'''# Teams System — Email + Team Name + Password Model
**Last Updated: March 26, 2026**
**Status: FULLY IMPLEMENTED**

---

## Overview

The Teams system lets a primary account holder create named teams, each with its own password.
Team members log in using the primary holder's email, the team name, and the team password.
Once logged in, they operate under the primary user's account — using the same API credentials,
same integrations, and same billing — but their threads are tagged with their team ID for filtering.

**Login identity model:**

```
gerardo@company.com  +  sales_team  +  <team password>
        |                    |                |
 Primary user email    Team login name   Team-specific password
 (auto-filled)         (unique per email) (min 8 chars, required)
```

The combination `(parent_email, team_name)` is **globally unique** in the database.

---

## What Was Built

### Database (Migration 038)

**File:** `AI_infrastructure/migrations/038_teams_system.sql`

```sql
-- Main teams table
CREATE TABLE ai_infrastructure.teams (
    id                 SERIAL PRIMARY KEY,
    parent_user_id     INT NOT NULL,           -- FK to users.id
    parent_email       VARCHAR(255) NOT NULL,  -- gerardo@company.com
    team_name          VARCHAR(100) NOT NULL,  -- sales_team (login identifier)
    team_password_hash TEXT NOT NULL,          -- bcrypt hash
    display_name       VARCHAR(255),           -- "Sales Team" (optional friendly name)
    description        TEXT,
    color              VARCHAR(7) DEFAULT '#3498db',
    is_active          BOOLEAN DEFAULT TRUE,
    member_count       INT DEFAULT 0,
    created_at         TIMESTAMPTZ DEFAULT NOW(),
    updated_at         TIMESTAMPTZ DEFAULT NOW(),
    created_by         INT,
    CONSTRAINT teams_unique_per_email UNIQUE (parent_email, team_name)
);

-- Thread and message attribution columns
ALTER TABLE sessions.threads  ADD COLUMN IF NOT EXISTS team_id INT;
ALTER TABLE sessions.messages ADD COLUMN IF NOT EXISTS team_id INT;
```

`team_id` on threads/messages is an **integer** (`teams.id`) — not a string.

---

### Backend API Endpoints

**File:** `AI_infrastructure/routes/auth_routes.py`

All CRUD routes require `Authorization: Bearer <token>`. The team login route is public.

#### `POST /api/auth/teams/create` — Create a team

```json
// Request body
{
  "team_name": "sales_team",           // Required. Lowercase, alphanumeric + underscore, 2-50 chars
  "password": "SecurePass123!",        // Required. Min 8 chars. Also accepted as "team_password"
  "display_name": "Sales Operations",  // Optional. Human-readable name shown in UI
  "description": "Handles all...",     // Optional
  "color": "#f39c12"                   // Optional. Defaults to #3498db
}

// Success response (201)
{
  "success": true,
  "team": {
    "id": 42, "team_name": "sales_team",
    "display_name": "Sales Operations", "color": "#f39c12", "created_at": "..."
  }
}
```

> **Note:** The endpoint reads the creating user's email from their JWT automatically. No `email`
> field is needed in the request body.

#### `GET /api/auth/teams` — List my teams

```json
// Success response (200)
{
  "success": true,
  "teams": [
    {
      "id": 42,
      "team_name": "sales_team",
      "display_name": "Sales Operations",
      "description": "...",
      "color": "#f39c12",
      "member_count": 0,
      "is_active": true,
      "created_at": "2026-03-26T10:00:00Z",
      "updated_at": "2026-03-26T10:00:00Z"
    }
  ],
  "total": 1
}
```

#### `PUT /api/auth/teams/<team_name>` — Update a team

```json
// Request body (all fields optional — only send what you want to change)
{
  "display_name": "Sales Ops Team",
  "description":  "Updated description",
  "color":        "#e74c3c",
  "password":     "NewPassword456!"   // Also accepted as "team_password". Min 8 chars.
}
```

> **Note:** `team_name` cannot be changed — it is the login identifier. Delete and recreate to rename.

#### `DELETE /api/auth/teams/<team_name>` — Delete a team (soft-delete)

Sets `is_active = FALSE`. The team record is preserved for audit; the team login stops working.

#### `POST /api/auth/login/team` — Team login (no auth required)

```json
// Request body
{
  "email":     "gerardo@company.com",
  "team_name": "sales_team",
  "password":  "SecurePass123!"
}

// Success response (200)
{
  "success": true,
  "token": "<jwt>",
  "user": {
    "id":                 1,                  // Parent user's ID
    "username":           "gerardo",
    "email":              "gerardo@company.com",
    "role":               "user",
    "login_mode":         "team",
    "team_id":            42,                 // teams.id (integer)
    "team_name":          "sales_team",
    "team_display_name":  "Sales Operations",
    "team_color":         "#f39c12",
    "organisation_id":    3,
    "org_role":           "member"
  }
}
```

**JWT payload from team login:**

```json
{
  "user_id":            1,
  "team_id":            42,
  "team_name":          "sales_team",
  "team_display_name":  "Sales Operations",
  "team_color":         "#f39c12",
  "login_mode":         "team",
  "org_role":           "member",
  "plan_tier":          "professional",
  "...standard JWT fields..."
}
```

---

### Credential Inheritance

**This is automatic.** Because the JWT `user_id` is set to the **parent user's ID**, every
existing tool call, API credential lookup, and Shopify/Xero/etc. request uses the primary user's
stored credentials without any code changes.

```
Team "sales_team" logs in
  --> JWT user_id = parent_user_id (e.g. 1)
  --> Tool calls pass user_id = 1
  --> Credential injector finds Anthropic/Shopify/Xero keys for user 1
  --> Team member uses parent's integrations (no extra setup needed)
```

---

### Thread Attribution

**File:** `AI_infrastructure/routes/thread_routes.py`

When a team-login JWT is present, the integer `team_id` is extracted and stored on new threads.
This applies to both the `create_thread` and `upsert_thread` code paths.

```python
if _payload.get('login_mode') == 'team':
    team_id = _payload.get('team_id')   # integer teams.id
```

Threads created by a team login have `sessions.threads.team_id = <integer>` set, enabling:

```sql
SELECT * FROM sessions.threads WHERE user_id = 1 AND team_id = 42;
```

> **Note:** The `sessions.messages.team_id` column exists in the schema but is **not yet populated**.
> It is reserved for future message-level filtering (see Known Gaps).

---

### Frontend Login UI

**File:** `UI/business-ai-platform-v2.html`

The login screen has two panels toggled by a button:

**Standard login panel** (`#standardLoginPanel`) — default view:
- Username/email + password
- "Sign in with Team" button below switches to the team panel

**Team login panel** (`#teamLoginPanel`) — shown on click:
- **Your Email** — primary user's email
- **Team Name** — auto-sanitised to lowercase alphanumeric + underscore as you type
- **Team Password** — password field
- "Sign in as Team" button calls `handleTeamLogin()`
- "Back to standard login" link returns to the standard panel

**JS Functions:**

| Function | Purpose |
|---|---|
| `showTeamLoginPanel()` | Switch to the team login view |
| `hideTeamLoginPanel()` | Return to standard login |
| `handleTeamLogin()` | POST to `/api/auth/login/team`, store token + metadata, reload page |

On success, `handleTeamLogin()` stores in `sessionStorage`:

```javascript
sessionStorage.setItem('teamLoginMode',    'true')
sessionStorage.setItem('teamName',         'sales_team')
sessionStorage.setItem('teamDisplayName',  'Sales Operations')
sessionStorage.setItem('teamColor',        '#f39c12')
```

---

### Team Login Visual Indicators

After page reload following a team login, the app detects `sessionStorage.teamLoginMode === 'true'`
and activates three indicators:

1. **Loading Screen** (`#authDisplayNameBlock`) — shows the team display name. Hidden for all
   non-team logins.

2. **Account Sidebar Badge** (`#sidebarTeamBadge`) — a coloured pill badge with a users icon and
   the team display name, placed next to the role badge. Background colour = team colour.

3. **Header Dropdown Badge** (`#dropdownTeamBadge`) — same badge in the user dropdown menu.

The badge logic (`applyTeamBadges()`) runs at three intervals (0 ms, 800 ms, 2500 ms) to survive
profile-load DOM refresh cycles.

---

### Team Management UI

**File:** `UI/business-ai-platform-v2.html` — Account Sidebar > Teams section

| Action | UI Flow |
|---|---|
| **Create** | "Create Team" opens modal. Email pre-filled (read-only). Enter team name, password, optional display name and colour. |
| **List** | Teams section calls `GET /api/auth/teams` and renders each team with name, display name, colour band, and Active badge. |
| **Edit** | Pencil icon opens modal pre-filled (team name locked). Change display name, description, colour, or password. Leave password blank to keep existing. |
| **Delete** | Trash icon > confirm dialog > soft-delete via `DELETE /api/auth/teams/<team_name>`. |

**Key JS Functions:**

| Function | What it does |
|---|---|
| `loadTeamIdList()` | Fetches `GET /api/auth/teams`, renders team rows |
| `showCreateTeamIdModal()` | Opens modal in create mode; auto-fills email from `localStorage('userEmail')` |
| `editTeamId(teamName)` | Fetches team list, finds by name, populates modal in edit mode |
| `saveTeamId()` | POST to `/api/auth/teams/create` (create) or PUT to `/api/auth/teams/<name>` (edit) |
| `deleteTeamId(teamName)` | DELETE `/api/auth/teams/<teamName>` |

**Password field sent:** `"password"` (backend also accepts `"team_password"` as fallback).

---

## How to Use — Step by Step

### Primary account holder: Creating a team

1. Log in with your normal email + password
2. Open the Account sidebar > **Teams** tab
3. Click **Create Team**
4. Your email is pre-filled (read-only)
5. Enter a **Team Name** — lowercase, letters/numbers/underscores, e.g. `sales_team`
6. Enter a **Team Password** — minimum 8 characters
7. Optionally enter a **Display Name** (e.g. "Sales Operations") and pick a colour
8. Click **Save** — team appears in the list
9. Share the team name and password with your team members

### Team members: Logging in

1. Go to the login page
2. Click **"Sign in with Team"** (below the standard form)
3. Enter:
   - **Your Email** — the primary account holder's email (e.g. `gerardo@company.com`)
   - **Team Name** — the team login name (e.g. `sales_team`)
   - **Team Password** — set when the team was created
4. Click **"Sign in as Team"**
5. A coloured badge appears in the sidebar showing your team name
6. You have full access to the primary user's integrations and tools

### Editing a team

1. Account sidebar > Teams tab
2. Click the pencil icon on the team row
3. Change display name, description, colour, or password
4. Leave password blank to keep the existing password
5. Team name cannot be changed (it is the login identifier)

---

## Developer Reference

### Detecting team login in a Flask route

```python
import jwt

auth_header = request.headers.get('Authorization', '')
if auth_header.startswith('Bearer '):
    token   = auth_header.split(' ', 1)[1]
    payload = jwt.decode(token, options={"verify_signature": False})
    if payload.get('login_mode') == 'team':
        team_id   = payload['team_id']    # int — teams.id
        team_name = payload['team_name']  # str — e.g. "sales_team"
```

### API Quick Reference (PowerShell)

```powershell
$token = "<primary user JWT>"
$base  = "http://localhost:5000"
$hdr   = @{Authorization="Bearer $token"; 'Content-Type'='application/json'}

# Create a team
Invoke-RestMethod -Uri "$base/api/auth/teams/create" -Method POST -Headers $hdr `
  -Body '{"team_name":"support_team","password":"Support2026!","display_name":"Support Ops","color":"#e74c3c"}'

# List teams
Invoke-RestMethod -Uri "$base/api/auth/teams" -Headers $hdr

# Update a team
Invoke-RestMethod -Uri "$base/api/auth/teams/support_team" -Method PUT -Headers $hdr `
  -Body '{"display_name":"Support Operations","color":"#c0392b"}'

# Delete a team
Invoke-RestMethod -Uri "$base/api/auth/teams/support_team" -Method DELETE -Headers $hdr

# Team login (no auth header needed)
Invoke-RestMethod -Uri "$base/api/auth/login/team" -Method POST `
  -Headers @{'Content-Type'='application/json'} `
  -Body '{"email":"gerardo@company.com","team_name":"sales_team","password":"SecurePass123!"}'
```

### Querying threads by team (SQL)

```sql
-- All threads for a specific team
SELECT t.*, tm.display_name AS team_display_name
FROM sessions.threads t
JOIN ai_infrastructure.teams tm ON tm.id = t.team_id
WHERE t.user_id = 1 AND t.team_id = 42;

-- All teams for a user with thread counts
SELECT tm.team_name, tm.display_name, COUNT(t.id) AS thread_count
FROM ai_infrastructure.teams tm
LEFT JOIN sessions.threads t ON t.team_id = tm.id
WHERE tm.parent_user_id = 1 AND tm.is_active = TRUE
GROUP BY tm.id, tm.team_name, tm.display_name;
```

---

## Architecture Notes

### What the old sub-user system was

Before migration 038, teams were sub-users in `ai_infrastructure.users` with `is_sub_user=TRUE`
and `parent_user_id`. Each sub-user had their own email, separate password, and no automatic
credential inheritance. The old `/api/auth/team-ids/*` endpoints remain in `auth_routes.py` for
backward compatibility.

### What the new model is

Teams live in `ai_infrastructure.teams`. Login uses `(parent_email, team_name, team_password)`.
The JWT carries the parent's `user_id` so all existing credential lookups and tool calls work
without modification.

### Backward compatibility

- Old routes (`/api/auth/team-ids/*`) — still present, still work
- Old analytics UI (`showTeamIdAnalytics()`) — still in HTML for old team-id records
- Old `sessions.threads.team_id` may contain strings (sub-user usernames) from old data
  — new data uses integers from `teams.id`; both coexist in the column

---

## Files Changed

| File | Change Summary |
|---|---|
| `AI_infrastructure/migrations/038_teams_system.sql` | Created — `ai_infrastructure.teams` table + `team_id` columns on threads/messages |
| `AI_infrastructure/routes/auth_routes.py` | 5 new routes: teams/create, teams (GET), teams/name (PUT/DELETE), login/team. Fixed password field reading (`data.get('password') or data.get('team_password', '')`). Added password update support in PUT handler. |
| `AI_infrastructure/routes/thread_routes.py` | Fixed: `team_id` extracted as INT from JWT (`_payload.get('team_id')`) in both `create_thread` and `upsert_thread`. Previously incorrectly stored `team_name` string into the INT column. |
| `UI/business-ai-platform-v2.html` | Login panels redesign (standard + team panels). `handleTeamLogin()` JS function. Team badge HTML (`#sidebarTeamBadge`, `#dropdownTeamBadge`). `applyTeamBadges()` in DOMContentLoaded. `loadTeamIdList`, `editTeamId`, `saveTeamId`, `deleteTeamId` updated to new API endpoints and field names. `#authDisplayNameBlock` hidden by default (team login only). |

---

## Known Gaps / Future Work

| Priority | Item |
|---|---|
| Medium | `sessions.messages.team_id` column exists but is never populated. Add to message INSERT if message-level filtering is needed. |
| Medium | Thread list UI has no team filter. Threads are tagged but there is no dropdown to filter by team. |
| Low | `teams.member_count` is static (always 0). A trigger or update would maintain an accurate count. |
| Low | No "Forgot team password" flow. The primary account holder can update it via the Edit modal. |
| Low | `showTeamIdAnalytics()` references old `/api/auth/team-ids/<id>/analytics` — no analytics UI exists for new-model teams. |
'''

target = pathlib.Path(r'c:\Users\gpoli\GIT\AI_Agents_V11\AI_agents\.github\TEAMS_SYSTEM_EMAIL_MODEL.md')
target.write_text(content, encoding='utf-8')
print(f"Written {len(content)} bytes, {len(content.splitlines())} lines")
print("First line:", content.splitlines()[0])
