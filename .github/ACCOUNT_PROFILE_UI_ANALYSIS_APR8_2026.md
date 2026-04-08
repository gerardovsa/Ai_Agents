# Account Profile UI Analysis — 8th April 2026

**File:** `UI/business-ai-platform-v2.html` (lines 22572–23175)  
**CSS:** `UI/modules_internal/thread-manager/thread.css`  
**JS:** `UI/modules_internal/components/account_profile.js`

---

## Modal Shell

| Element | Status | Notes |
|---|---|---|
| Modal ID | `account-settings-modal` | line 22572 |
| Tab nav | Three tabs: General, Team Members, Organisation | line 22584 |
| Tab switcher fn | `switchSettingsTab(tab, btn)` | account_profile.js ~line 2790 |
| Height | `max-height: 92vh` | flex column |
| Footer | Save + Close buttons | inside `settings-tab-general` only |

---

## TAB 1: General Settings (`settings-tab-general`)

### Structure
```
modal-body
├── settings-section: "Personalisation" (collapsible)
│   ├── Nickname input
│   ├── Communication Style select
│   ├── Response Detail Level (radio chips)
│   ├── Authentication Platform select
│   ├── Location & Timezone Detection (info card, 2-col grid)
│   ├── Manual Location Override (checkbox + input)
│   └── Manual Timezone Override (checkbox + select)
├── settings-section: "Mandatory Instructions & Preferences" (collapsible)
│   ├── Explanation text
│   ├── Mandatory Instructions tag chip system (id=preferredToolsContainer)
│   └── Custom Preferences tag chip system (id=customPreferencesContainer)
└── modal-footer (Reset + Save Changes + Close)
```

### AI Settings — Where Are They?
`loadAccountSettings()` and `saveSettings()` populate:  
`modelSelect`, `temperature`, `topP`, `enableThinking`, `maxTokens`, `thinkingBudgetSlider`, `enableStreaming`, `maxRounds`, `roundTimeout`

**These elements are NOT in the General tab.** They live in a **separate AI Settings modal** (`#ai-settings-modal`, around line 21800) with sections:
- Model Options (AI Model select, Temperature, Top P, Extended Thinking)
- Round Parameters (Max Turns, Timeout Per Round, Streaming)
- Token Parameters (Max Response Tokens, Thinking Budget)

`loadAccountSettings()` safely uses `if (document.getElementById('x'))` guards so it populates whichever modal is open at the time.

### Code Connections
| Feature | JS Function | Status |
|---|---|---|
| Load settings | `loadAccountSettings()` | ✅ Connected to `/api/user/preferences` |
| Save settings | `saveSettings()` → `saveAllSettingsToBackend()` | ✅ Connected |
| Toggle manual location | `toggleManualLocation()` | ✅ Defined (line ~1610) |
| Toggle manual timezone | `toggleManualTimezone()` | ✅ Defined (line ~1621) |
| Reset settings | `resetAccountSettings()` | ✅ Defined (line ~1632) |
| Geolocation detection | `detectAndDisplayGeolocation()` | ✅ Defined (line ~1549) — IP-based |
| Add mandatory instruction | `addPreferredTool()` | ✅ Full tag chip system implemented |
| Add custom preference | `addCustomPreference()` | ✅ Full tag chip system implemented |

### Issues
| # | Issue | Severity |
|---|---|---|
| 1 | No info container / tab context header | 🟡 Medium |
| 2 | Personalisation and Mandatory Instructions sections are both open on load — form looks cluttered | 🟢 Low |
| 3 | "Detecting..." label shows on load if no stored geolocation | 🟢 Low |

---

## TAB 2: Team Members (`settings-tab-team`)

### Structure
```
settings-tab-team (display:flex, flex-direction:column)
├── .team-tab-header
│   ├── Title: "Team Members" + subtitle
│   └── Buttons: Export CSV, Import CSV (file input), Add Member
├── #addTeamMemberForm (display:none by default)
│   ├── Grid: Username/Team ID, Email, Password
│   ├── Grid: Data Access Scope select, Daily Message Limit
│   └── Buttons: Cancel, Create Member
└── scrollable list div (flex:1, overflow-y:auto)
    ├── #teamMembersLoading (spinner)
    ├── #teamMembersEmpty (no members state)
    └── #teamMembersTable (display:none — populated dynamically)
```

### Backend API Endpoints (all exist in `auth_routes.py`)
| Method | Endpoint | Function |
|---|---|---|
| POST | `/api/auth/team-ids/add` | Create sub-user |
| GET | `/api/auth/team-ids` | List sub-users |
| PUT | `/api/auth/team-ids/<team_id>` | Update sub-user |
| DELETE | `/api/auth/team-ids/<team_id>` | Delete sub-user |
| GET | `/api/auth/team-ids/export` | Export CSV |
| POST | `/api/auth/team-ids/import` | Import CSV |

### Add Team Member Request Body
```json
{
  "team_id": "sarah.ops",          // required, min 2 chars
  "email": "sarah@company.com",    // optional
  "password": "...",               // optional - auto-generated if blank
  "data_access_scope": "own",      // own | team | all
  "usage_limit_daily": 1000        // integer
}
```

### Code Connections — BEFORE FIX
| Feature | HTML element | JS Function | Status |
|---|---|---|---|
| Show add form | `#addTeamMemberBtn` | `showAddTeamMemberForm()` | ❌ **NOT DEFINED** |
| Hide add form | Cancel button | `hideAddTeamMemberForm()` | ❌ **NOT DEFINED** |
| Create member | Create button | `addTeamMember()` | ❌ **NOT DEFINED** |
| Export CSV | Export button | `exportTeamIdsCsv()` | ❌ **NOT DEFINED** |
| Import CSV | File input | `importTeamIdsCsv(this)` | ❌ **NOT DEFINED** |
| Load list | - | `loadTeamMembers()` | ❌ **NOT DEFINED** |
| `switchSettingsTab('team')` | - | nothing called | ❌ List never loads |
| `#teamMembersTable` | Empty div | - | ❌ Never populated |

### Issues
| # | Issue | Severity |
|---|---|---|
| 1 | 5 onclick functions not defined — all buttons throw `ReferenceError` | 🔴 Critical |
| 2 | `teamMembersTable` div never populated — members never visible | 🔴 Critical |
| 3 | No info container | 🟡 Medium |
| 4 | Tab switch doesn't trigger list load | 🟡 Medium |

---

## TAB 3: Organisation (`settings-tab-org`)

### Structure
```
orgPanel (moveable — can be detached into sidebar)
├── #orgLoading (spinner)
├── #orgEmpty (create org CTA)
├── #orgCreateForm (create form)
└── #orgDashboard
    ├── #orgHeaderCard (org initials, name, slug, members, role)
    ├── .org-sub-tab-nav (Overview | Members | Invitations | Vault | Modules | Audit)
    └── Sub-panels:
        ├── #org-subtab-overview   — Org settings form (name/desc/visibility/AI provider)
        ├── #org-subtab-members    — Member list + Invite form
        ├── #org-subtab-invitations — Sent invites list
        ├── #org-subtab-vault      — Credentials list + Vault password
        ├── #org-subtab-modules    — Module catalog toggles
        └── #org-subtab-audit      — Access log table
```

### Code Connections
| Feature | JS Function | Status |
|---|---|---|
| Load org tab | `loadOrgTab()` | ✅ Called by `switchSettingsTab('org')` |
| Render dashboard | `_renderOrgDashboard()` | ✅ Full render with identity card |
| Role gating | `_gateOrgSubTabs()` | ✅ Hides Vault/Audit/Modules per role |
| Save org settings | `saveOrgSettings()` | ✅ PUT `/api/org/info` |
| Load members | `loadOrgMembers()` | ✅ GET `/api/org/members` |
| Remove member | `removeMemberFromOrg()` | ✅ Defined |
| Invite member | `inviteOrgMember()` | ✅ Via OrgManager |
| Load vault | `OrgManager.loadCredentials()` | ✅ Via OrgManager |
| Load modules | `OrgManager.loadModuleCatalog()` | ✅ Via OrgManager |
| Load audit | `OrgManager.loadAuditLog()` | ✅ Via OrgManager |

### Info Containers (✅ all added in prior session)
| Sub-tab | Accent colour | Status |
|---|---|---|
| Overview | Blue (--accent-primary) | ✅ |
| Members | Green (--accent-success) | ✅ |
| Invitations | Orange (--accent-warning) | ✅ |
| Vault | Blue (--accent-primary) | ✅ |
| Modules | Light blue (#3b82f6) | ✅ |
| Audit | Orange (--accent-warning) | ✅ |

### Remaining Issues
| # | Issue | Severity |
|---|---|---|
| 1 | Vault: "Your Credentials" sub-label is redundant — add button stranded below heading | 🟢 Low |
| 2 | Modules: "Available Modules" sub-label is redundant | 🟢 Low |
| 3 | Audit: "Recent Access Events" sub-label is redundant | 🟢 Low |
| 4 | Modules/Audit/Vault refresh buttons are in sub-labels, not in the section header | 🟢 Low |

---

## CSS Status

| File | Class | Before | After (fixed) |
|---|---|---|---|
| `thread.css:2791` | `.settings-section-content` | `max-height: 500px` | `flex: 1; min-height: 0` |

---

## Consistency Gaps — Before / After 8th April 2026

| Feature | General | Team | Org |
|---|---|---|---|
| Info container at tab level | ~~❌~~ → **✅** | ~~❌~~ → **✅** | N/A (sub-tab level) |
| Heading: icon + title + subtitle | ~~❌~~ → **✅** | Partial → **✅** | ✅ |
| Buttons below text | ✅ | ✅ (form) | ✅ |
| Refresh/action button in heading row | N/A | N/A | ~~❌~~ → **✅** |
| Error messages | Generic `alert()` | ~~❌ broken~~ → **✅ inline banner** | `alert()` |
| Empty state | ✅ (tags) | ✅ HTML → **✅ now wired** | ✅ |

---

## Session Changes Applied (8th April 2026) — COMPLETE ✅

### 1. CSS Height Fix (`thread.css` line 2791)
`.settings-section-content` — removed `max-height: 500px`, replaced with `flex: 1; min-height: 0` so settings content fills the full modal height.

### 2. Styling Alignment — `business-ai-platform-v2.html`

| Change | Location | Detail |
|---|---|---|
| Info container added | General tab (top of modal-body) | Blue-accent panel: "Account Preferences" heading + descriptive paragraph |
| Info container added | Team tab (between header bar and form) | Green-accent panel explaining sub-accounts and CSV bulk management |
| Add button moved to heading row | Org → Vault sub-tab | Removed "Your Credentials" sub-label; `+` button now sits in the section heading row |
| Refresh button moved to heading row | Org → Modules sub-tab | Removed "Available Modules" sub-label; refresh sits in heading row |
| Refresh button moved to heading row | Org → Audit sub-tab | Removed "Recent Access Events" sub-label; refresh sits in heading row |

### 3. Team Member Functions — `account_profile.js` (~260 lines added before `ORGANISATION TAB`)

All 7 previously-undefined functions are now implemented:

| Function | Endpoint | Behaviour |
|---|---|---|
| `showAddTeamMemberForm()` | — | Reveals form, hides Add button, focuses username input |
| `hideAddTeamMemberForm()` | — | Hides form, resets all fields to defaults, shows Add button |
| `addTeamMember()` | `POST /api/auth/team-ids/add` | Validates username (≥2 chars) → creates member → refreshes list → success banner |
| `loadTeamMembers()` | `GET /api/auth/team-ids` | Renders member rows: avatar, scope badge, daily limit, active status, delete button. Shows inline error + Retry on failure |
| `deleteTeamMember(teamId)` | `DELETE /api/auth/team-ids/<id>` | `createInlineConfirm` dialog → delete → refresh → success banner |
| `exportTeamIdsCsv()` | `GET /api/auth/team-ids/export` | Fetches blob → triggers browser file download with date-stamped filename |
| `importTeamIdsCsv(fileInput)` | `POST /api/auth/team-ids/import` | Multipart upload → refresh list → success/error banner |

### 4. Tab Switch Trigger — `account_profile.js` line 2973
`switchSettingsTab('team')` now calls `loadTeamMembers()` — list loads fresh every time the Team tab is opened.

### 5. Error Handling Pattern
All team functions use `_showTeamNotification(message, type)`:
- Inline coloured banner rendered inside the Team tab (no `alert()` dialogs)
- **Error** (red): shows until user dismisses with `×`
- **Success** (green): auto-dismisses after 3 seconds
- Includes a close button and is accessible (`role="alert"`)

---

## Outstanding Items

| # | Item | Priority | Status | Notes |
|---|---|---|---|---|
| 1 | General/Org tabs — replace `alert()` with inline banners | 🟡 Medium | ✅ Done (Apr 8) | `_showGeneralNotification` + `_showOrgNotification` helpers added. `confirm()` replaced with `createInlineConfirm`. 9 affected functions updated. |
| 2 | Team member inline edit (PUT endpoint exists) | 🟢 Low | ✅ Done (Apr 8) | Pencil-icon edit button per row expands inline panel: daily limit, active toggle, optional password. `editTeamMember()` + `saveTeamMemberEdit()` added. |
| 3 | `tab-vsa-veterinary-alerts` orphaned tab | 🟢 Low | ✅ Done (Apr 8) | Tab content `<div>` + HTML comments removed. `vsa_veterinary` entry removed from JS module map. |
| 4 | Zone 2 sidebar still driven by `manifest.json` | 🟡 Medium | ⏳ Pending | DB-driven module visibility not yet wired to sidebar. See `MODULE_VISIBILITY_ARCHITECTURE.md` for full spec. |

### Remaining `alert()` Calls (Intentional — Not Changed)

| Line | Function | Reason |
|---|---|---|
| ~920 | Re-auth flow | Rare auth failure — acceptable modal interrupt |
| ~988 | `addGmailAccount()` | Coming soon stub |
| ~1693–1712 | `showNotifications/Appearance/Security/Shortcuts` | Coming soon stubs or keyboard shortcut reference |
| ~1899 | Memory delete failure | Memory panel — separate from General/Org tab |
| ~2056 | Memory add validation | Memory panel — separate from General/Org tab |
