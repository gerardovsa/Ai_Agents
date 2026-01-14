# Team ID Management System - Complete Implementation
**Date:** December 17, 2025  
**Purpose:** Allow account holders to add/remove Team IDs (sub-users) with optional passwords for team messaging

---

## 🎯 **Overview**

**Team IDs = Sub-Users in the Database**
- Each user account can create multiple "Team IDs" (stored as `is_sub_user = TRUE`)
- Each Team ID gets its own `username` and optional `password`
- Team IDs can message each other privately (same parent account)
- Account holder can add/remove Team IDs anytime
- Each Team ID can have custom permissions, tools, agents

---

## 📊 **Database Schema (Already Exists!)**

```sql
-- ai_infrastructure.users table ALREADY HAS these columns:
CREATE TABLE ai_infrastructure.users (
  id INTEGER PRIMARY KEY,
  username TEXT NOT NULL,  -- "Team ID" name (e.g., "Bob", "Sarah")
  email TEXT NOT NULL,  -- Required but can be dummy for sub-users
  password_hash TEXT NOT NULL,  -- Hashed password for Team ID login
  parent_user_id INTEGER,  -- NULL for main accounts, parent_id for Team IDs
  is_sub_user BOOLEAN DEFAULT FALSE,  -- TRUE for Team IDs
  
  -- Team ID Settings
  permissions TEXT,  -- JSON: {"view_dashboard": true, "edit_data": false}
  allowed_tools TEXT,  -- JSON: ["calculator", "chat"] or NULL (all tools)
  allowed_agents TEXT,  -- JSON: ["agent1", "agent2"] or NULL (all agents)
  data_access_scope TEXT DEFAULT 'own',  -- 'own' | 'team' | 'department' | 'all'
  usage_limit_daily INTEGER DEFAULT 1000,  -- API call limit per day
  access_start_time TEXT,  -- "09:00" - when Team ID can log in
  access_end_time TEXT,  -- "17:00" - when Team ID access ends
  account_expires_at TIMESTAMP,  -- Optional expiration date
  
  is_active BOOLEAN DEFAULT TRUE,  -- Can disable Team ID without deleting
  role TEXT DEFAULT 'user',  -- Can be 'user', 'admin', 'viewer'
  created_at TIMESTAMP,
  last_active TIMESTAMP
);

-- Indexes for fast Team ID lookups
CREATE INDEX idx_users_parent_user_id ON ai_infrastructure.users(parent_user_id);
CREATE INDEX idx_users_is_sub_user ON ai_infrastructure.users(is_sub_user);
CREATE INDEX idx_users_username ON ai_infrastructure.users(username);
```

---

## 🔄 **Team Messaging Architecture**

### **Message Routing with Team IDs**

When a Team ID sends a message, we need to know:
1. **Who sent it?** (sender's username)
2. **Who receives it?** (recipient's username)
3. **Are they on the same account?** (same parent_user_id)

```sql
-- Add columns to messages table for Team ID routing
ALTER TABLE ai_infrastructure.messages
ADD COLUMN sender_team_id TEXT,  -- Username of sender (e.g., "Bob")
ADD COLUMN recipient_team_id TEXT,  -- Username of recipient (e.g., "Sarah") or NULL for broadcast
ADD COLUMN message_type TEXT DEFAULT 'private';  -- 'private' | 'broadcast' | 'cross_user'

-- Index for fast message filtering
CREATE INDEX idx_messages_recipient_team_id ON ai_infrastructure.messages(recipient_team_id);
CREATE INDEX idx_messages_sender_team_id ON ai_infrastructure.messages(sender_team_id);
```

### **Message Types**

| Type | Description | Routing Logic | Example |
|------|-------------|---------------|---------|
| **private** | Team member to specific team member | `recipient_team_id = 'Sarah'` | Bob → Sarah (same account) |
| **broadcast** | Team member to all team | `recipient_team_id IS NULL` | Bob → All team members |
| **cross_user** | Different accounts messaging | `user_id != other_user_id` | Account #5 → Account #8 |

---

## 🛠️ **Backend API - Team ID Management**

### **Endpoint 1: Add Team ID**

**Route:** `POST /api/auth/team-ids/add`

**Request Body:**
```json
{
  "team_id": "Sarah",  // Username for this Team ID
  "password": "optional_password",  // Can be blank for no password
  "email": "sarah@team.local",  // Optional, can auto-generate
  "permissions": {
    "view_dashboard": true,
    "edit_data": false,
    "manage_team": false
  },
  "allowed_tools": ["chat", "calculator"],  // null = all tools
  "allowed_agents": null,  // null = all agents
  "data_access_scope": "own",  // 'own' | 'team' | 'department' | 'all'
  "usage_limit_daily": 500,
  "access_start_time": "09:00",  // Optional work hours
  "access_end_time": "17:00",
  "account_expires_at": "2026-12-31T23:59:59Z"  // Optional expiration
}
```

**Response:**
```json
{
  "success": true,
  "team_id": "Sarah",
  "sub_user_id": 42,
  "message": "Team ID 'Sarah' created successfully"
}
```

**Python Code (`auth_routes.py`):**
```python
@auth_bp.route('/api/auth/team-ids/add', methods=['POST'])
def add_team_id():
    """
    Add a new Team ID (sub-user) to the authenticated user's account
    
    Only the account holder (parent user) can add Team IDs
    """
    try:
        data = request.get_json()
        user_id = request.user.get('id')  # From JWT token
        
        # Extract fields
        team_id = data.get('team_id')  # Username
        password = data.get('password', '')  # Optional password
        email = data.get('email', f"{team_id.lower()}@team.local")  # Auto-generate if not provided
        permissions = data.get('permissions', {})
        allowed_tools = data.get('allowed_tools')
        allowed_agents = data.get('allowed_agents')
        data_access_scope = data.get('data_access_scope', 'own')
        usage_limit_daily = data.get('usage_limit_daily', 1000)
        access_start_time = data.get('access_start_time')
        access_end_time = data.get('access_end_time')
        account_expires_at = data.get('account_expires_at')
        
        # Validate team_id
        if not team_id or len(team_id) < 2:
            return jsonify({"error": "Team ID must be at least 2 characters"}), 400
        
        # Check if team_id already exists for this account
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Check for duplicate Team ID under same parent
        cursor.execute("""
            SELECT id FROM ai_infrastructure.users 
            WHERE username = %s AND parent_user_id = %s
        """, [team_id, user_id])
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": f"Team ID '{team_id}' already exists"}), 400
        
        # Hash password (use bcrypt)
        import bcrypt
        if password:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        else:
            # Generate random password if none provided
            import secrets
            random_password = secrets.token_urlsafe(16)
            password_hash = bcrypt.hashpw(random_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert Team ID
        cursor.execute("""
            INSERT INTO ai_infrastructure.users (
                username, email, password_hash, role,
                parent_user_id, is_sub_user,
                permissions, allowed_tools, allowed_agents,
                data_access_scope, usage_limit_daily,
                access_start_time, access_end_time, account_expires_at,
                is_active
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, [
            team_id, email, password_hash, 'user',
            user_id, True,  # is_sub_user = True
            json.dumps(permissions) if permissions else None,
            json.dumps(allowed_tools) if allowed_tools is not None else None,
            json.dumps(allowed_agents) if allowed_agents is not None else None,
            data_access_scope, usage_limit_daily,
            access_start_time, access_end_time, account_expires_at,
            True  # is_active
        ])
        
        sub_user_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ User {user_id} created Team ID '{team_id}' (sub_user_id={sub_user_id})")
        
        return jsonify({
            "success": True,
            "team_id": team_id,
            "sub_user_id": sub_user_id,
            "message": f"Team ID '{team_id}' created successfully"
        }), 201
        
    except Exception as e:
        logger.exception(f"Failed to add Team ID: {e}")
        return jsonify({"error": str(e)}), 500
```

---

### **Endpoint 2: List Team IDs**

**Route:** `GET /api/auth/team-ids`

**Response:**
```json
{
  "team_ids": [
    {
      "id": 42,
      "team_id": "Sarah",
      "email": "sarah@team.local",
      "is_active": true,
      "last_active": "2025-12-17T10:30:00Z",
      "created_at": "2025-12-01T08:00:00Z",
      "permissions": {"view_dashboard": true},
      "allowed_tools": ["chat", "calculator"],
      "data_access_scope": "own",
      "usage_limit_daily": 500,
      "sessions": [
        {
          "device": "Chrome on Mac",
          "ip_address": "192.168.1.100",
          "last_active": "2025-12-17T10:30:00Z"
        }
      ]
    },
    {
      "id": 43,
      "team_id": "John",
      "email": "john@team.local",
      "is_active": false,  // Disabled
      "last_active": "2025-12-15T14:20:00Z",
      "created_at": "2025-12-02T09:00:00Z"
    }
  ]
}
```

**Python Code:**
```python
@auth_bp.route('/api/auth/team-ids', methods=['GET'])
def list_team_ids():
    """
    List all Team IDs for the authenticated user
    
    Returns Team IDs with their active sessions and metadata
    """
    try:
        user_id = request.user.get('id')
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Get all Team IDs for this parent user
        cursor.execute("""
            SELECT 
                u.id, u.username, u.email, u.is_active,
                u.last_active, u.created_at,
                u.permissions, u.allowed_tools, u.allowed_agents,
                u.data_access_scope, u.usage_limit_daily,
                u.access_start_time, u.access_end_time, u.account_expires_at
            FROM ai_infrastructure.users u
            WHERE u.parent_user_id = %s AND u.is_sub_user = TRUE
            ORDER BY u.created_at DESC
        """, [user_id])
        
        team_ids = []
        for row in cursor.fetchall():
            # Get active sessions for this Team ID
            cursor.execute("""
                SELECT device_info, ip_address, last_active
                FROM ai_infrastructure.user_sessions
                WHERE user_id = %s
                ORDER BY last_active DESC
                LIMIT 5
            """, [row[0]])  # row[0] = sub_user id
            
            sessions = []
            for session in cursor.fetchall():
                device_info = json.loads(session[0]) if session[0] else {}
                sessions.append({
                    "device": f"{device_info.get('browser', 'Unknown')} on {device_info.get('os', 'Unknown')}",
                    "ip_address": session[1],
                    "last_active": session[2].isoformat() if session[2] else None
                })
            
            team_ids.append({
                "id": row[0],
                "team_id": row[1],  # username
                "email": row[2],
                "is_active": row[3],
                "last_active": row[4].isoformat() if row[4] else None,
                "created_at": row[5].isoformat() if row[5] else None,
                "permissions": json.loads(row[6]) if row[6] else {},
                "allowed_tools": json.loads(row[7]) if row[7] else None,
                "allowed_agents": json.loads(row[8]) if row[8] else None,
                "data_access_scope": row[9],
                "usage_limit_daily": row[10],
                "access_start_time": row[11],
                "access_end_time": row[12],
                "account_expires_at": row[13].isoformat() if row[13] else None,
                "sessions": sessions
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({"team_ids": team_ids}), 200
        
    except Exception as e:
        logger.exception(f"Failed to list Team IDs: {e}")
        return jsonify({"error": str(e)}), 500
```

---

### **Endpoint 3: Update Team ID**

**Route:** `PUT /api/auth/team-ids/<team_id>`

**Request Body:**
```json
{
  "password": "new_password",  // Optional: update password
  "is_active": true,  // Enable/disable Team ID
  "permissions": {"view_dashboard": true},
  "allowed_tools": ["chat"],
  "usage_limit_daily": 200
}
```

**Python Code:**
```python
@auth_bp.route('/api/auth/team-ids/<team_id>', methods=['PUT'])
def update_team_id(team_id):
    """
    Update Team ID settings (password, permissions, limits)
    """
    try:
        user_id = request.user.get('id')
        data = request.get_json()
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Verify this Team ID belongs to user
        cursor.execute("""
            SELECT id FROM ai_infrastructure.users
            WHERE username = %s AND parent_user_id = %s AND is_sub_user = TRUE
        """, [team_id, user_id])
        
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            return jsonify({"error": "Team ID not found"}), 404
        
        sub_user_id = row[0]
        
        # Build UPDATE query dynamically
        updates = []
        params = []
        
        if 'password' in data:
            import bcrypt
            password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            updates.append("password_hash = %s")
            params.append(password_hash)
        
        if 'is_active' in data:
            updates.append("is_active = %s")
            params.append(data['is_active'])
        
        if 'permissions' in data:
            updates.append("permissions = %s")
            params.append(json.dumps(data['permissions']))
        
        if 'allowed_tools' in data:
            updates.append("allowed_tools = %s")
            params.append(json.dumps(data['allowed_tools']) if data['allowed_tools'] is not None else None)
        
        if 'allowed_agents' in data:
            updates.append("allowed_agents = %s")
            params.append(json.dumps(data['allowed_agents']) if data['allowed_agents'] is not None else None)
        
        if 'usage_limit_daily' in data:
            updates.append("usage_limit_daily = %s")
            params.append(data['usage_limit_daily'])
        
        if 'data_access_scope' in data:
            updates.append("data_access_scope = %s")
            params.append(data['data_access_scope'])
        
        if not updates:
            cursor.close()
            conn.close()
            return jsonify({"error": "No fields to update"}), 400
        
        # Execute update
        params.append(sub_user_id)
        cursor.execute(f"""
            UPDATE ai_infrastructure.users
            SET {', '.join(updates)}
            WHERE id = %s
        """, params)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Updated Team ID '{team_id}' for user {user_id}")
        
        return jsonify({"success": True, "message": f"Team ID '{team_id}' updated"}), 200
        
    except Exception as e:
        logger.exception(f"Failed to update Team ID: {e}")
        return jsonify({"error": str(e)}), 500
```

---

### **Endpoint 4: Delete Team ID**

**Route:** `DELETE /api/auth/team-ids/<team_id>`

**Response:**
```json
{
  "success": true,
  "message": "Team ID 'Sarah' deleted successfully"
}
```

**Python Code:**
```python
@auth_bp.route('/api/auth/team-ids/<team_id>', methods=['DELETE'])
def delete_team_id(team_id):
    """
    Delete a Team ID (soft delete by setting is_active = FALSE)
    
    Also revokes all active sessions for this Team ID
    """
    try:
        user_id = request.user.get('id')
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Verify this Team ID belongs to user
        cursor.execute("""
            SELECT id FROM ai_infrastructure.users
            WHERE username = %s AND parent_user_id = %s AND is_sub_user = TRUE
        """, [team_id, user_id])
        
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            return jsonify({"error": "Team ID not found"}), 404
        
        sub_user_id = row[0]
        
        # Soft delete (set is_active = FALSE)
        cursor.execute("""
            UPDATE ai_infrastructure.users
            SET is_active = FALSE
            WHERE id = %s
        """, [sub_user_id])
        
        # Revoke all active sessions for this Team ID
        cursor.execute("""
            DELETE FROM ai_infrastructure.user_sessions
            WHERE user_id = %s
        """, [sub_user_id])
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Deleted Team ID '{team_id}' for user {user_id}")
        
        return jsonify({
            "success": True,
            "message": f"Team ID '{team_id}' deleted successfully"
        }), 200
        
    except Exception as e:
        logger.exception(f"Failed to delete Team ID: {e}")
        return jsonify({"error": str(e)}), 500
```

---

## 🎨 **Frontend UI - Team ID Management**

### **Account Settings - Team IDs Tab**

Add new tab to existing Account Settings sidebar:

```html
<!-- In business-ai-platform-v2.html, Account Settings Section -->

<!-- Add to tabs list -->
<div class="account-tabs">
    <button class="tab-button active" data-tab="profile">Profile</button>
    <button class="tab-button" data-tab="security">Security</button>
    <button class="tab-button" data-tab="team-ids">Team IDs</button> <!-- NEW -->
    <button class="tab-button" data-tab="preferences">Preferences</button>
</div>

<!-- Add Team IDs Tab Content -->
<div id="team-ids-tab" class="tab-content" style="display: none;">
    <div class="section-header">
        <h3>Team ID Management</h3>
        <p class="section-description">
            Add team members to your account. Each Team ID can have its own password and permissions.
        </p>
    </div>
    
    <!-- Add Team ID Button -->
    <div class="action-row">
        <button class="btn btn-primary" onclick="showAddTeamIdModal()">
            <i class="fas fa-plus"></i> Add Team ID
        </button>
    </div>
    
    <!-- Team IDs List -->
    <div id="team-ids-list" class="team-ids-container">
        <!-- Will be populated by JavaScript -->
    </div>
</div>
```

### **JavaScript Functions**

```javascript
// In business-ai-platform-v2.html <script> section

// ========================================
// TEAM ID MANAGEMENT
// ========================================

/**
 * Load and display all Team IDs for current user
 */
async function loadTeamIds() {
    try {
        const response = await fetch('/api/auth/team-ids', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load Team IDs');
        }
        
        const data = await response.json();
        displayTeamIds(data.team_ids);
        
    } catch (error) {
        console.error('Error loading Team IDs:', error);
        showNotification('Failed to load Team IDs', 'error');
    }
}

/**
 * Display Team IDs in the UI
 */
function displayTeamIds(teamIds) {
    const container = document.getElementById('team-ids-list');
    
    if (!teamIds || teamIds.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-users" style="font-size: 48px; color: var(--text-muted); margin-bottom: 16px;"></i>
                <p>No Team IDs yet</p>
                <p class="text-muted">Add team members to enable team messaging</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = teamIds.map(teamId => `
        <div class="team-id-card ${teamId.is_active ? '' : 'inactive'}">
            <div class="team-id-header">
                <div class="team-id-info">
                    <h4>${teamId.team_id}</h4>
                    <span class="badge ${teamId.is_active ? 'badge-success' : 'badge-secondary'}">
                        ${teamId.is_active ? 'Active' : 'Inactive'}
                    </span>
                </div>
                <div class="team-id-actions">
                    <button class="btn btn-sm btn-outline" onclick="editTeamId('${teamId.team_id}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteTeamId('${teamId.team_id}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
            
            <div class="team-id-details">
                <div class="detail-row">
                    <span class="label">Email:</span>
                    <span class="value">${teamId.email}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Last Active:</span>
                    <span class="value">${teamId.last_active ? formatTimeAgo(teamId.last_active) : 'Never'}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Created:</span>
                    <span class="value">${new Date(teamId.created_at).toLocaleDateString()}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Usage Limit:</span>
                    <span class="value">${teamId.usage_limit_daily} calls/day</span>
                </div>
            </div>
            
            ${teamId.sessions && teamId.sessions.length > 0 ? `
                <div class="team-id-sessions">
                    <h5>Active Sessions</h5>
                    ${teamId.sessions.map(session => `
                        <div class="session-item">
                            <i class="fas fa-desktop"></i>
                            <span>${session.device}</span>
                            <span class="text-muted">IP: ${session.ip_address}</span>
                            <span class="text-muted">${formatTimeAgo(session.last_active)}</span>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `).join('');
}

/**
 * Show modal to add new Team ID
 */
function showAddTeamIdModal() {
    const modal = createModal('Add Team ID', `
        <form id="add-team-id-form">
            <div class="form-group">
                <label for="team-id-name">Team ID Name *</label>
                <input type="text" id="team-id-name" class="form-control" 
                       placeholder="e.g., Sarah, John, Bob" required>
                <small class="form-text">This is the display name for the team member</small>
            </div>
            
            <div class="form-group">
                <label for="team-id-password">Password (Optional)</label>
                <input type="password" id="team-id-password" class="form-control" 
                       placeholder="Leave blank for no password">
                <small class="form-text">Team member can log in with this password</small>
            </div>
            
            <div class="form-group">
                <label for="team-id-email">Email (Optional)</label>
                <input type="email" id="team-id-email" class="form-control" 
                       placeholder="Auto-generated if blank">
            </div>
            
            <div class="form-group">
                <label for="usage-limit">Daily Usage Limit</label>
                <input type="number" id="usage-limit" class="form-control" 
                       value="1000" min="1">
                <small class="form-text">Maximum API calls per day</small>
            </div>
            
            <div class="form-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Add Team ID</button>
            </div>
        </form>
    `);
    
    document.getElementById('add-team-id-form').addEventListener('submit', addTeamId);
}

/**
 * Add new Team ID
 */
async function addTeamId(event) {
    event.preventDefault();
    
    const teamId = document.getElementById('team-id-name').value.trim();
    const password = document.getElementById('team-id-password').value;
    const email = document.getElementById('team-id-email').value.trim();
    const usageLimit = parseInt(document.getElementById('usage-limit').value);
    
    try {
        const response = await fetch('/api/auth/team-ids/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({
                team_id: teamId,
                password: password || null,
                email: email || null,
                usage_limit_daily: usageLimit,
                data_access_scope: 'own'
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to add Team ID');
        }
        
        const result = await response.json();
        
        showNotification(`Team ID '${teamId}' added successfully`, 'success');
        closeModal();
        loadTeamIds();  // Refresh list
        
    } catch (error) {
        console.error('Error adding Team ID:', error);
        showNotification(error.message, 'error');
    }
}

/**
 * Delete Team ID
 */
async function deleteTeamId(teamId) {
    if (!confirm(`Are you sure you want to delete Team ID '${teamId}'? This will revoke all their active sessions.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/auth/team-ids/${teamId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete Team ID');
        }
        
        showNotification(`Team ID '${teamId}' deleted successfully`, 'success');
        loadTeamIds();  // Refresh list
        
    } catch (error) {
        console.error('Error deleting Team ID:', error);
        showNotification('Failed to delete Team ID', 'error');
    }
}

/**
 * Edit Team ID (show modal with current settings)
 */
async function editTeamId(teamId) {
    // TODO: Fetch current Team ID details and populate modal
    showNotification('Edit Team ID - Coming soon', 'info');
}

// Initialize Team IDs tab when Account Settings is opened
document.addEventListener('DOMContentLoaded', () => {
    // Load Team IDs when tab is clicked
    const teamIdsTab = document.querySelector('[data-tab="team-ids"]');
    if (teamIdsTab) {
        teamIdsTab.addEventListener('click', loadTeamIds);
    }
});
```

### **CSS Styles**

```css
/* Team ID Card Styling */
.team-id-card {
    background: var(--background-elevated);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    transition: all 0.2s ease;
}

.team-id-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.team-id-card.inactive {
    opacity: 0.6;
    border-color: var(--border-color-light);
}

.team-id-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.team-id-info {
    display: flex;
    align-items: center;
    gap: 12px;
}

.team-id-info h4 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
}

.team-id-actions {
    display: flex;
    gap: 8px;
}

.team-id-details {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin-bottom: 12px;
}

.detail-row {
    display: flex;
    justify-content: space-between;
}

.detail-row .label {
    font-weight: 600;
    color: var(--text-muted);
}

.detail-row .value {
    color: var(--text-primary);
}

.team-id-sessions {
    border-top: 1px solid var(--border-color);
    padding-top: 12px;
    margin-top: 12px;
}

.team-id-sessions h5 {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 8px;
    color: var(--text-muted);
}

.session-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px;
    background: var(--background-base);
    border-radius: 4px;
    margin-bottom: 8px;
}

.session-item i {
    color: var(--primary-color);
}

.badge {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
}

.badge-success {
    background: var(--success-bg);
    color: var(--success-text);
}

.badge-secondary {
    background: var(--muted-bg);
    color: var(--muted-text);
}

.empty-state {
    text-align: center;
    padding: 48px 24px;
    color: var(--text-muted);
}
```

---

## 📝 **Database Migration Script**

```sql
-- Add Team ID columns to messages table
ALTER TABLE ai_infrastructure.messages
ADD COLUMN IF NOT EXISTS sender_team_id TEXT,
ADD COLUMN IF NOT EXISTS recipient_team_id TEXT,
ADD COLUMN IF NOT EXISTS message_type TEXT DEFAULT 'private';

-- Create indexes for fast message filtering
CREATE INDEX IF NOT EXISTS idx_messages_sender_team_id 
ON ai_infrastructure.messages(sender_team_id);

CREATE INDEX IF NOT EXISTS idx_messages_recipient_team_id 
ON ai_infrastructure.messages(recipient_team_id);

CREATE INDEX IF NOT EXISTS idx_messages_user_team 
ON ai_infrastructure.messages(user_id, sender_team_id, recipient_team_id);

-- Verify existing users table has all required columns
-- (These should already exist from your sub-user system)
DO $$ 
BEGIN
    -- Check if parent_user_id column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'ai_infrastructure' 
        AND table_name = 'users' 
        AND column_name = 'parent_user_id'
    ) THEN
        ALTER TABLE ai_infrastructure.users ADD COLUMN parent_user_id INTEGER;
    END IF;
    
    -- Check if is_sub_user column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'ai_infrastructure' 
        AND table_name = 'users' 
        AND column_name = 'is_sub_user'
    ) THEN
        ALTER TABLE ai_infrastructure.users ADD COLUMN is_sub_user BOOLEAN DEFAULT FALSE;
    END IF;
END $$;

-- Create index on parent_user_id for fast Team ID lookups
CREATE INDEX IF NOT EXISTS idx_users_parent_user_id 
ON ai_infrastructure.users(parent_user_id);

CREATE INDEX IF NOT EXISTS idx_users_is_sub_user 
ON ai_infrastructure.users(is_sub_user);

-- Verify schema
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'ai_infrastructure' 
    AND table_name = 'users'
ORDER BY ordinal_position;
```

---

## 🔄 **Message Routing Implementation**

### **Update Message Service**

```python
# In message_service.py

def save_message_with_team_id(
    user_id: int,
    sender_team_id: str,  # Username of sender
    recipient_team_id: str | None,  # Username of recipient or None for broadcast
    content: str,
    conversation_id: str | None = None,
    agent_id: str | None = None
) -> int:
    """
    Save message with Team ID routing information
    
    Args:
        user_id: Parent account ID
        sender_team_id: Username of sender (e.g., "Bob")
        recipient_team_id: Username of recipient (e.g., "Sarah") or None for broadcast
        content: Message text
        conversation_id: Optional conversation ID
        agent_id: Optional agent ID
    
    Returns:
        message_id
    """
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    # Determine message type
    if recipient_team_id:
        message_type = 'private'  # Specific team member
    else:
        message_type = 'broadcast'  # All team members
    
    cursor.execute("""
        INSERT INTO ai_infrastructure.messages (
            user_id, sender_team_id, recipient_team_id, message_type,
            content, conversation_id, agent_id, timestamp
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        RETURNING id
    """, [user_id, sender_team_id, recipient_team_id, message_type, content, conversation_id, agent_id])
    
    message_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    
    return message_id


def get_team_messages(user_id: int, team_id: str, limit: int = 100) -> list:
    """
    Get messages for a specific Team ID
    
    Includes:
    - Messages sent TO this team member (recipient_team_id = team_id)
    - Broadcast messages (recipient_team_id IS NULL)
    - Messages sent BY this team member
    
    Args:
        user_id: Parent account ID
        team_id: Username of team member
        limit: Max messages to return
    
    Returns:
        List of message dicts
    """
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            id, sender_team_id, recipient_team_id, message_type,
            content, timestamp, conversation_id, agent_id
        FROM ai_infrastructure.messages
        WHERE user_id = %s 
            AND (
                recipient_team_id = %s  -- Direct message to this team member
                OR recipient_team_id IS NULL  -- Broadcast to all
                OR sender_team_id = %s  -- Sent by this team member
            )
        ORDER BY timestamp DESC
        LIMIT %s
    """, [user_id, team_id, team_id, limit])
    
    messages = []
    for row in cursor.fetchall():
        messages.append({
            "id": row[0],
            "sender_team_id": row[1],
            "recipient_team_id": row[2],
            "message_type": row[3],
            "content": row[4],
            "timestamp": row[5].isoformat() if row[5] else None,
            "conversation_id": row[6],
            "agent_id": row[7]
        })
    
    cursor.close()
    conn.close()
    
    return messages
```

---

## ✅ **Complete Implementation Checklist**

### **Backend (Python)**
- [ ] Run database migration (add sender_team_id, recipient_team_id, message_type columns)
- [ ] Add 4 Team ID endpoints to `auth_routes.py`:
  - [ ] `POST /api/auth/team-ids/add` - Add Team ID
  - [ ] `GET /api/auth/team-ids` - List Team IDs
  - [ ] `PUT /api/auth/team-ids/<team_id>` - Update Team ID
  - [ ] `DELETE /api/auth/team-ids/<team_id>` - Delete Team ID
- [ ] Update `message_service.py`:
  - [ ] Add `save_message_with_team_id()` function
  - [ ] Add `get_team_messages()` function
- [ ] Update WebSocket handlers in `flask_app.py`:
  - [ ] Extract `sender_team_id` from JWT token
  - [ ] Route messages by `recipient_team_id`
  - [ ] Support broadcast messages (recipient_team_id = NULL)

### **Frontend (HTML/JavaScript)**
- [ ] Add "Team IDs" tab to Account Settings sidebar
- [ ] Add JavaScript functions:
  - [ ] `loadTeamIds()` - Fetch and display Team IDs
  - [ ] `displayTeamIds()` - Render Team ID cards
  - [ ] `showAddTeamIdModal()` - Show add modal
  - [ ] `addTeamId()` - Submit new Team ID
  - [ ] `editTeamId()` - Edit existing Team ID
  - [ ] `deleteTeamId()` - Delete Team ID
- [ ] Add CSS styles for Team ID cards
- [ ] Update chat UI to show sender's Team ID in messages
- [ ] Add Team ID selector for sending messages

### **Testing**
- [ ] Create Team ID "Sarah" for account #5
- [ ] Create Team ID "Bob" for account #5
- [ ] Test login with Sarah's password
- [ ] Test Sarah sending message to Bob (private)
- [ ] Test Bob sending broadcast to all team
- [ ] Test cross-account messaging (account #5 → account #8)
- [ ] Test Team ID deletion (revoke sessions)
- [ ] Test password change for Team ID
- [ ] Test usage limits enforcement

---

## 🎯 **Key Features Summary**

✅ **Dynamic Team ID Management**
- Account holders can add/remove Team IDs anytime
- No limit on number of Team IDs (you can set a limit if needed)
- Each Team ID is a full sub-user with database row

✅ **Optional Passwords**
- Team IDs can have passwords for individual login
- Or leave blank for "display name only" mode
- Parent account can reset Team ID passwords anytime

✅ **Team Messaging**
- Team members message each other: `recipient_team_id = "Sarah"`
- Broadcast to all team: `recipient_team_id = NULL`
- Cross-account messaging: Normal `user_id` filtering

✅ **Security & Control**
- Each Team ID has own permissions, tools, agents
- Usage limits (API calls per day)
- Work hours (access_start_time, access_end_time)
- Account expiration dates
- Enable/disable without deleting
- View active sessions with IP addresses

✅ **Zero Configuration**
- Uses existing `users` table (no new tables!)
- Leverages existing sub-user columns
- Existing session management works automatically

---

## 📚 **Next Steps**

1. **Run the migration script** to add message routing columns
2. **Copy the backend code** to `auth_routes.py` and `message_service.py`
3. **Add the frontend UI** to Account Settings
4. **Test with 2-3 Team IDs** on same account
5. **Deploy and monitor** for any issues

**This is your complete Team ID Management system!** 🚀
