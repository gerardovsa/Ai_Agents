# Permissions & Roles Architecture - What We Can Control

**Date:** November 10, 2025  
**Status:** 🎯 Analysis & Planning

---

## 🎯 The Big Question:

**"What level of control can we assign if we give someone a 'Team' role?"**

Answer: **A LOT!** This is a multi-agent AI platform with 594 tools across 20+ platforms. We can control access at multiple levels.

---

## 📊 Current System Analysis:

### ✅ **What EXISTS Today:**

1. **Role Field** in Users Table
   ```sql
   users.role TEXT DEFAULT 'user'
   -- Current values: 'admin' or 'user'
   ```

2. **Workspace System** (Multi-tenant Isolation)
   ```sql
   workspaces table:
     - id
     - user_id (owner)
     - name
     - description
     - metadata (JSON - can store permissions here!)
   ```

3. **594 Tools** Across Platforms:
   - Google Workspace (Docs, Sheets, Gmail, Drive, Calendar, Forms, Meet, Slides)
   - Microsoft 365 (Outlook, Teams, OneDrive, Word, Excel, PowerPoint)
   - Stripe (Payment processing)
   - Slack (Team communication)
   - Database operations (SQL queries, data analysis)
   - InHouse Print (Quote calculators)
   - Many more...

4. **OAuth Credential System**:
   - oauth_tokens table (platform, access_token, refresh_token)
   - Credential injector (injects tokens at runtime)
   - Parent OAuth inheritance (sub-users can use parent's credentials)

---

## 🔐 Permission Levels We Can Implement:

### **Level 1: Role-Based Access Control (RBAC)**

We can create a hierarchy of roles with different capabilities:

```
OWNER (Parent OAuth Account)
  ↓
ADMIN (Full Access Sub-User)
  ↓
TEAM LEAD (Department Manager)
  ↓
TEAM MEMBER (Standard User)
  ↓
READ-ONLY (View Only)
  ↓
GUEST (Limited Access)
```

### **What Each Role Can Do:**

#### 🟢 **OWNER** (OAuth Parent Account)
```json
{
  "role": "owner",
  "permissions": {
    "users": {
      "create_sub_users": true,
      "edit_sub_users": true,
      "delete_sub_users": true,
      "assign_roles": true,
      "view_all_sub_users": true
    },
    "workspace": {
      "manage_workspace": true,
      "invite_users": true,
      "billing": true,
      "oauth_management": true
    },
    "tools": {
      "access_all_tools": true,
      "tool_restrictions": []
    },
    "data": {
      "view_all_data": true,
      "edit_all_data": true,
      "delete_all_data": true,
      "export_data": true
    },
    "ai_agents": {
      "access_all_agents": true,
      "create_threads": true,
      "delete_threads": true,
      "manage_assignments": true
    }
  }
}
```

#### 🔵 **ADMIN** (Full Access Sub-User)
```json
{
  "role": "admin",
  "permissions": {
    "users": {
      "create_sub_users": true,
      "edit_sub_users": true,
      "delete_sub_users": false,  // Can't delete users
      "assign_roles": true,
      "view_all_sub_users": true
    },
    "workspace": {
      "manage_workspace": true,
      "invite_users": true,
      "billing": false,  // Can't manage billing
      "oauth_management": false  // Can't change OAuth
    },
    "tools": {
      "access_all_tools": true,
      "tool_restrictions": ["stripe_delete_*"]  // Can't delete Stripe data
    },
    "data": {
      "view_all_data": true,
      "edit_all_data": true,
      "delete_all_data": false,  // Can't delete data
      "export_data": true
    },
    "ai_agents": {
      "access_all_agents": true,
      "create_threads": true,
      "delete_threads": true,
      "manage_assignments": true
    }
  }
}
```

#### 🟡 **TEAM LEAD** (Department Manager)
```json
{
  "role": "team_lead",
  "department": "marketing",  // Scope their access
  "permissions": {
    "users": {
      "create_sub_users": false,
      "edit_sub_users": false,
      "delete_sub_users": false,
      "assign_roles": false,
      "view_all_sub_users": false,
      "view_team_users": true  // Can see their team only
    },
    "workspace": {
      "manage_workspace": false,
      "invite_users": false,
      "billing": false,
      "oauth_management": false
    },
    "tools": {
      "access_all_tools": false,
      "allowed_tools": [
        "gmail_*",          // All Gmail tools
        "google_docs_*",    // All Google Docs tools
        "google_sheets_*",  // All Google Sheets tools
        "slack_*",          // All Slack tools
        "microsoft_teams_*" // All Teams tools
      ],
      "tool_restrictions": [
        "*_delete_*",       // No deletion tools
        "stripe_*",         // No payment processing
        "database_*"        // No direct database access
      ]
    },
    "data": {
      "view_all_data": false,
      "view_department_data": true,  // Only their department's data
      "edit_department_data": true,
      "delete_all_data": false,
      "export_data": true
    },
    "ai_agents": {
      "access_all_agents": false,
      "allowed_agents": ["agent-1", "agent-2"],  // Specific agents only
      "create_threads": true,
      "delete_threads": false,
      "manage_assignments": false
    }
  }
}
```

#### 🟠 **TEAM MEMBER** (Standard User)
```json
{
  "role": "team_member",
  "department": "sales",
  "permissions": {
    "users": {
      "create_sub_users": false,
      "edit_sub_users": false,
      "delete_sub_users": false,
      "assign_roles": false,
      "view_all_sub_users": false,
      "view_team_users": false
    },
    "workspace": {
      "manage_workspace": false,
      "invite_users": false,
      "billing": false,
      "oauth_management": false
    },
    "tools": {
      "access_all_tools": false,
      "allowed_tools": [
        "gmail_send_email",
        "gmail_list_messages",
        "google_docs_create_document",
        "google_sheets_create_spreadsheet",
        "slack_post_message"
      ],
      "tool_restrictions": [
        "*_delete_*",
        "*_admin_*",
        "stripe_*",
        "database_*"
      ]
    },
    "data": {
      "view_all_data": false,
      "view_own_data": true,  // Only their own data
      "edit_own_data": true,
      "delete_all_data": false,
      "export_data": false
    },
    "ai_agents": {
      "access_all_agents": false,
      "allowed_agents": ["agent-1"],  // One agent only
      "create_threads": true,
      "delete_threads": false,
      "manage_assignments": false
    }
  }
}
```

#### ⚪ **READ-ONLY** (View Only)
```json
{
  "role": "readonly",
  "permissions": {
    "users": {
      "create_sub_users": false,
      "edit_sub_users": false,
      "delete_sub_users": false,
      "assign_roles": false,
      "view_all_sub_users": false,
      "view_team_users": false
    },
    "workspace": {
      "manage_workspace": false,
      "invite_users": false,
      "billing": false,
      "oauth_management": false
    },
    "tools": {
      "access_all_tools": false,
      "allowed_tools": [
        "gmail_list_messages",   // View only
        "google_docs_read_*",    // Read-only tools
        "google_sheets_read_*",
        "slack_list_*"
      ],
      "tool_restrictions": [
        "*_create_*",
        "*_update_*",
        "*_delete_*",
        "*_send_*",
        "*_post_*"
      ]
    },
    "data": {
      "view_all_data": false,
      "view_own_data": true,
      "edit_own_data": false,  // Read-only!
      "delete_all_data": false,
      "export_data": false
    },
    "ai_agents": {
      "access_all_agents": false,
      "allowed_agents": ["prime"],  // Prime agent only
      "create_threads": false,
      "delete_threads": false,
      "manage_assignments": false
    }
  }
}
```

#### 🔴 **GUEST** (Limited Access)
```json
{
  "role": "guest",
  "expiry_date": "2025-12-31",  // Time-limited access
  "permissions": {
    "users": {
      "create_sub_users": false,
      "edit_sub_users": false,
      "delete_sub_users": false,
      "assign_roles": false,
      "view_all_sub_users": false,
      "view_team_users": false
    },
    "workspace": {
      "manage_workspace": false,
      "invite_users": false,
      "billing": false,
      "oauth_management": false
    },
    "tools": {
      "access_all_tools": false,
      "allowed_tools": [
        "slack_post_message"  // Minimal tools
      ],
      "tool_restrictions": ["*"]  // Restricted by default
    },
    "data": {
      "view_all_data": false,
      "view_own_data": true,
      "edit_own_data": false,
      "delete_all_data": false,
      "export_data": false
    },
    "ai_agents": {
      "access_all_agents": false,
      "allowed_agents": [],  // No AI agents
      "create_threads": false,
      "delete_threads": false,
      "manage_assignments": false
    }
  }
}
```

---

## 🎛️ Level 2: Tool-Based Permissions

### **Categories of Tools (What Can Be Restricted):**

```
Communication Tools (53 tools):
  - Gmail (send, read, delete, search)
  - Outlook (send, read, calendar)
  - Slack (post, read, manage channels)
  - Microsoft Teams (post, meetings, channels)

Document Tools (87 tools):
  - Google Docs (create, read, update, delete)
  - Google Sheets (create, read, formulas, charts)
  - Google Slides (create, presentations)
  - Microsoft Word/Excel/PowerPoint

File Management (31 tools):
  - Google Drive (upload, download, share, delete)
  - OneDrive (upload, download, share)

Calendar & Scheduling (22 tools):
  - Google Calendar (create events, manage)
  - Outlook Calendar (create, manage)

Forms & Surveys (15 tools):
  - Google Forms (create, responses, analyze)

Payment Processing (24 tools):
  - Stripe (customers, payments, refunds, subscriptions)

Database Operations (42 tools):
  - SQL queries (SELECT, INSERT, UPDATE, DELETE)
  - Database management

Video Conferencing (11 tools):
  - Google Meet (create, schedule, manage)
  - Microsoft Teams Meetings

InHouse Print (7 tools):
  - Quote calculators (business cards, flyers, books, etc.)

... and 300+ more tools across 20+ platforms
```

### **Example: Team Member Restrictions**

```python
# Team Member can ONLY use these tools:
allowed_tools = [
    # Gmail - Basic only
    "gmail_send_email",
    "gmail_list_messages",
    "gmail_read_message",
    
    # Google Docs - Create/edit only
    "google_docs_create_document",
    "google_docs_update_document",
    "google_docs_read_document",
    
    # Google Sheets - Basic operations
    "google_sheets_create_spreadsheet",
    "google_sheets_read_spreadsheet",
    "google_sheets_append_data",
    
    # Slack - Communication only
    "slack_post_message",
    "slack_list_channels",
    
    # Google Drive - View/upload only
    "google_drive_list_files",
    "google_drive_upload_file",
    "google_drive_download_file"
]

# Team Member CANNOT use these tools:
restricted_tools = [
    "*_delete_*",           # No deletion
    "*_admin_*",            # No admin functions
    "stripe_*",             # No payment tools
    "database_*",           # No database access
    "gmail_delete_*",       # Can't delete emails
    "google_drive_delete_", # Can't delete files
    "slack_admin_*",        # Can't manage Slack
    "microsoft_teams_admin_*"  # Can't manage Teams
]
```

---

## 🎛️ Level 3: Data-Based Permissions

### **What Data Can They See/Edit?**

```
OWNER/ADMIN:
  ✅ All threads (Prime + all agents)
  ✅ All user data
  ✅ All conversations
  ✅ All files
  ✅ All integrations

TEAM LEAD:
  ✅ Department threads only
  ✅ Team members' data
  ✅ Department conversations
  ✅ Shared files
  ❌ Other departments' data

TEAM MEMBER:
  ✅ Own threads only
  ✅ Own conversations
  ✅ Files shared with them
  ❌ Other users' data
  ❌ Admin settings

READ-ONLY:
  ✅ View assigned threads
  ✅ View shared documents
  ❌ Cannot edit anything
  ❌ Cannot create anything
```

---

## 🎛️ Level 4: AI Agent Access Permissions

### **Which AI Agents Can They Use?**

```
Platform has 5 agent slots:
  - Prime (main agent)
  - Agent-1
  - Agent-2
  - Agent-3
  - Agent-4

OWNER/ADMIN:
  ✅ All 5 agents (Prime + 4 agents)
  ✅ Can create/delete threads
  ✅ Can assign threads to any agent
  ✅ Can manage thread assignments

TEAM LEAD:
  ✅ Prime + 2 specific agents (e.g., Agent-1, Agent-2)
  ✅ Can create threads
  ❌ Cannot delete threads
  ❌ Cannot manage assignments

TEAM MEMBER:
  ✅ Prime + 1 specific agent (e.g., Agent-1 only)
  ✅ Can create threads in allowed agents
  ❌ Cannot delete threads
  ❌ Cannot reassign threads

READ-ONLY:
  ✅ Prime only
  ✅ Can view threads
  ❌ Cannot create threads
  ❌ Cannot interact with agents
```

---

## 🎛️ Level 5: Time-Based & Usage-Based Restrictions

### **Additional Control Mechanisms:**

```json
{
  "role": "team_member",
  "restrictions": {
    "time_based": {
      "expiry_date": "2025-12-31",  // Account expires
      "work_hours_only": true,      // 9 AM - 5 PM access
      "timezone": "America/New_York",
      "allowed_days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
    },
    "usage_based": {
      "max_requests_per_day": 100,  // Rate limiting
      "max_threads": 10,             // Max threads they can create
      "max_file_uploads": 50,        // Max files per day
      "max_emails_per_day": 30       // Email sending limit
    },
    "ip_restrictions": {
      "allowed_ips": ["192.168.1.0/24"],  // Office network only
      "require_vpn": true
    }
  }
}
```

---

## 💼 Realistic "TEAM" Role Example:

### **What a "TEAM" role can realistically do:**

```json
{
  "role": "team",
  "description": "Standard team member with collaboration tools",
  "permissions": {
    "tools": {
      "allowed_categories": [
        "Gmail (basic email)",
        "Google Docs (create/edit)",
        "Google Sheets (basic operations)",
        "Slack (messaging)",
        "Google Calendar (view/create events)",
        "Google Drive (upload/view files)"
      ],
      "restricted_categories": [
        "Stripe (payment processing)",
        "Database (SQL operations)",
        "Admin tools (user management)",
        "Delete operations (all platforms)"
      ]
    },
    "ai_agents": {
      "access": "Prime + Agent-1 only",
      "can_create_threads": true,
      "can_delete_threads": false,
      "max_threads": 20
    },
    "data_access": {
      "scope": "own_data_only",
      "can_export": false,
      "can_share": true
    },
    "limits": {
      "requests_per_day": 500,
      "max_file_size": "10MB",
      "max_email_recipients": 50
    }
  }
}
```

### **What They CAN Do:**
✅ Send/receive emails (Gmail/Outlook)
✅ Create/edit Google Docs/Sheets
✅ Post messages in Slack/Teams
✅ Upload/view files in Drive/OneDrive
✅ Schedule meetings (Google Calendar/Outlook)
✅ Create threads in Prime and Agent-1
✅ Use InHouse Print quote calculators
✅ View shared documents
✅ Collaborate with team members

### **What They CANNOT Do:**
❌ Process payments (Stripe)
❌ Run database queries
❌ Delete emails/files/threads
❌ Manage user accounts
❌ Change workspace settings
❌ Access admin tools
❌ View other users' data
❌ Export bulk data
❌ Use Agent-2, Agent-3, Agent-4

---

## 🔧 Implementation Strategy:

### **Step 1: Update Users Table Schema**
```sql
ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user';
ALTER TABLE users ADD COLUMN parent_user_id INTEGER;
ALTER TABLE users ADD COLUMN permissions TEXT;  -- JSON

-- Example permissions JSON:
UPDATE users SET permissions = '{
  "allowed_tools": ["gmail_*", "google_docs_*"],
  "restricted_tools": ["*_delete_*", "stripe_*"],
  "allowed_agents": ["prime", "agent-1"],
  "max_threads": 20,
  "data_scope": "own_only"
}'
WHERE role = 'team';
```

### **Step 2: Create Permission Checker Middleware**
```python
# AI_infrastructure/auth/permission_checker.py

def check_tool_permission(user_id: int, tool_name: str) -> bool:
    """Check if user has permission to use this tool"""
    user = get_user(user_id)
    permissions = json.loads(user['permissions'] or '{}')
    
    # Check if tool is explicitly allowed
    allowed_tools = permissions.get('allowed_tools', [])
    if any(fnmatch.fnmatch(tool_name, pattern) for pattern in allowed_tools):
        return True
    
    # Check if tool is restricted
    restricted_tools = permissions.get('restricted_tools', [])
    if any(fnmatch.fnmatch(tool_name, pattern) for pattern in restricted_tools):
        return False
    
    # Default: allow for owner/admin, deny for others
    return user['role'] in ['owner', 'admin']


def check_agent_access(user_id: int, agent_id: str) -> bool:
    """Check if user can access this AI agent"""
    user = get_user(user_id)
    permissions = json.loads(user['permissions'] or '{}')
    
    allowed_agents = permissions.get('allowed_agents', [])
    return agent_id in allowed_agents


def check_data_access(user_id: int, resource_owner_id: int) -> bool:
    """Check if user can access another user's data"""
    user = get_user(user_id)
    permissions = json.loads(user['permissions'] or '{}')
    
    data_scope = permissions.get('data_scope', 'own_only')
    
    if data_scope == 'all':
        return True  # Admin/owner can see all
    elif data_scope == 'department':
        return same_department(user_id, resource_owner_id)
    elif data_scope == 'own_only':
        return user_id == resource_owner_id
    
    return False
```

### **Step 3: Inject Permission Checks**
```python
# Before executing any tool:
if not check_tool_permission(user_id, tool_name):
    raise PermissionError(f"User {user_id} not authorized to use {tool_name}")

# Before accessing AI agent:
if not check_agent_access(user_id, agent_id):
    raise PermissionError(f"User {user_id} not authorized to access {agent_id}")

# Before showing data:
if not check_data_access(user_id, data_owner_id):
    raise PermissionError(f"User {user_id} not authorized to view this data")
```

---

## 📋 Summary: "What Can We Realistically Control?"

### ✅ **EVERYTHING!**

1. **Who can create sub-users** (only owner/admin)
2. **Which tools each role can use** (594 tools, granular control)
3. **Which AI agents they can access** (5 agents, individual permissions)
4. **What data they can see/edit** (own, department, or all data)
5. **Time-based access** (work hours, expiry dates)
6. **Usage limits** (rate limiting, max threads, max emails)
7. **IP restrictions** (office network only, VPN required)
8. **OAuth inheritance** (sub-users use parent's credentials)
9. **Export capabilities** (who can export data)
10. **Admin functions** (who can manage workspace)

### 🎯 **Recommended Role Structure:**

```
Owner → Admin → Team Lead → Team Member → Read-Only → Guest
  ↓       ↓         ↓           ↓             ↓          ↓
 ALL    MOST      SOME        FEW         VIEW      MINIMAL
```

---

**Ready to implement? Let me know which permissions model you prefer!**

---

**Last Updated:** November 10, 2025  
**Author:** AI Agent (GitHub Copilot)  
**Status:** 📋 Analysis Complete - Ready for Implementation
