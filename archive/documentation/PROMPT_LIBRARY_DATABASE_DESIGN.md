# Prompt Library Database Design - Complete Architecture

## Database Understanding Summary

### Current Database Structure

**ai_infrastructure.db** contains:
- `users` - 6 users with auth, roles, OAuth connections
- `user_preferences` - User settings (communication style, AI model preferences)
- `oauth_tokens` - Google/Microsoft OAuth credentials
- `workspaces` - Multi-tenant workspace system
- `workspace_users` - Workspace membership
- `workspace_invitations` - Pending workspace invites

**sessions.db** contains:
- `threads` - Conversation threads (28 threads)
- `messages` - Individual messages (119 messages)
- `thread_shares` - Thread sharing mechanism (empty)
- `thread_users` - Thread user access (empty)

### Key Insights from Analysis

1. **User System**: Multi-user with workspace support (primary + sub-users)
2. **OAuth Integration**: Google and Microsoft platforms per user
3. **Thread System**: Threads belong to users/workspaces with metadata
4. **Sharing Infrastructure**: Empty `thread_shares` table shows sharing intent
5. **Preferences**: Existing `user_preferences` table for personalization

---

## Prompt Library Requirements

Based on your requirements:
1. **User-Specific Prompts** - Each user creates their own prompts
2. **User Shareable** - Users can share prompts with specific users/workspaces
3. **Global/Public** - Prompts usable by entire database

---

## Recommended Table Schema

### Table 1: `prompt_library` (Main Prompts Storage)

```sql
CREATE TABLE IF NOT EXISTS prompt_library (
    -- Primary Key
    prompt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Ownership & Visibility
    created_by_user_id INTEGER NOT NULL,
    workspace_id INTEGER NULL,  -- NULL = personal, value = workspace-scoped
    visibility TEXT NOT NULL DEFAULT 'private',  -- 'private', 'shared', 'workspace', 'public'
    
    -- Prompt Details
    prompt_name TEXT NOT NULL,
    prompt_key TEXT NOT NULL,  -- Unique identifier (e.g., 'expert_coder', 'user_123_custom_1')
    prompt_text TEXT NOT NULL,
    prompt_description TEXT,
    
    -- Categorization
    category TEXT NOT NULL,  -- 'development', 'analysis', 'data', 'style', 'business', 'creative', 'custom'
    subcategory TEXT,
    tags TEXT,  -- JSON array: ["sql", "optimization", "performance"]
    
    -- Display Properties
    icon TEXT,  -- Emoji or icon identifier (e.g., '⚡', '🐛', '📊')
    display_color TEXT,  -- Hex color for UI (#007bff)
    sort_order INTEGER DEFAULT 0,
    
    -- Prompt Type
    prompt_type TEXT NOT NULL,  -- 'quick_action', 'library', 'template', 'custom'
    is_system_prompt BOOLEAN DEFAULT 0,  -- System-provided prompts (can't be deleted)
    
    -- Usage & Stats
    use_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    effectiveness_score REAL DEFAULT 0.0,  -- User ratings average (0-5)
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,  -- Soft delete
    is_active BOOLEAN DEFAULT 1,
    
    -- Version Control
    version INTEGER DEFAULT 1,
    parent_prompt_id INTEGER,  -- For forked/cloned prompts
    
    -- Sharing Metadata
    share_count INTEGER DEFAULT 0,
    clone_count INTEGER DEFAULT 0,
    
    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_prompt_id) REFERENCES prompt_library(prompt_id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX idx_prompt_library_user ON prompt_library(created_by_user_id);
CREATE INDEX idx_prompt_library_workspace ON prompt_library(workspace_id);
CREATE INDEX idx_prompt_library_visibility ON prompt_library(visibility);
CREATE INDEX idx_prompt_library_category ON prompt_library(category);
CREATE INDEX idx_prompt_library_type ON prompt_library(prompt_type);
CREATE INDEX idx_prompt_library_key ON prompt_library(prompt_key);
CREATE INDEX idx_prompt_library_active ON prompt_library(is_active, deleted_at);
```

### Table 2: `prompt_shares` (Sharing Management)

```sql
CREATE TABLE IF NOT EXISTS prompt_shares (
    -- Primary Key
    share_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- What & Who
    prompt_id INTEGER NOT NULL,
    shared_by_user_id INTEGER NOT NULL,
    
    -- Share Target (ONE of these will be populated)
    shared_with_user_id INTEGER,  -- Specific user
    shared_with_workspace_id INTEGER,  -- Entire workspace
    share_scope TEXT NOT NULL,  -- 'user', 'workspace', 'public'
    
    -- Permissions
    permission TEXT NOT NULL DEFAULT 'view',  -- 'view', 'use', 'edit', 'clone'
    can_reshare BOOLEAN DEFAULT 0,
    can_modify BOOLEAN DEFAULT 0,
    
    -- Share Details
    share_link TEXT UNIQUE,  -- Optional shareable link
    share_token TEXT UNIQUE,  -- Token for link sharing
    
    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,  -- NULL = never expires
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP,
    
    -- Status
    is_active BOOLEAN DEFAULT 1,
    revoked_at TIMESTAMP,
    revoked_by_user_id INTEGER,
    revoke_reason TEXT,
    
    FOREIGN KEY (prompt_id) REFERENCES prompt_library(prompt_id) ON DELETE CASCADE,
    FOREIGN KEY (shared_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (shared_with_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (shared_with_workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (revoked_by_user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_prompt_shares_prompt ON prompt_shares(prompt_id);
CREATE INDEX idx_prompt_shares_shared_by ON prompt_shares(shared_by_user_id);
CREATE INDEX idx_prompt_shares_shared_with_user ON prompt_shares(shared_with_user_id);
CREATE INDEX idx_prompt_shares_shared_with_workspace ON prompt_shares(shared_with_workspace_id);
CREATE INDEX idx_prompt_shares_scope ON prompt_shares(share_scope);
CREATE INDEX idx_prompt_shares_active ON prompt_shares(is_active);
```

### Table 3: `prompt_usage_history` (Analytics & Tracking)

```sql
CREATE TABLE IF NOT EXISTS prompt_usage_history (
    -- Primary Key
    usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- What & Who
    prompt_id INTEGER NOT NULL,
    used_by_user_id INTEGER NOT NULL,
    thread_id INTEGER,  -- Link to conversation thread
    message_id INTEGER,  -- Link to specific message
    
    -- Context
    request_context TEXT,  -- Original user request (truncated)
    combined_prompts TEXT,  -- JSON array of all prompts used together
    
    -- Results
    success BOOLEAN,
    user_feedback_score INTEGER,  -- 1-5 rating
    user_feedback_text TEXT,
    
    -- Timing
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER,
    
    -- AI Details
    ai_model TEXT,
    ai_temperature REAL,
    tokens_used INTEGER,
    
    FOREIGN KEY (prompt_id) REFERENCES prompt_library(prompt_id) ON DELETE CASCADE,
    FOREIGN KEY (used_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_usage_history_prompt ON prompt_usage_history(prompt_id);
CREATE INDEX idx_usage_history_user ON prompt_usage_history(used_by_user_id);
CREATE INDEX idx_usage_history_thread ON prompt_usage_history(thread_id);
CREATE INDEX idx_usage_history_timestamp ON prompt_usage_history(used_at);
```

### Table 4: `prompt_preferences` (User Saved Combinations)

```sql
CREATE TABLE IF NOT EXISTS prompt_preferences (
    -- Primary Key
    preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Ownership
    user_id INTEGER NOT NULL,
    workspace_id INTEGER,
    
    -- Preference Details
    preference_name TEXT NOT NULL,
    preference_key TEXT NOT NULL,  -- Unique identifier
    description TEXT,
    
    -- Prompt Combination
    quick_actions TEXT,  -- JSON array: ["expert_coder", "debugger"]
    library_prompts TEXT,  -- JSON array: ["system_architect"]
    custom_prompt TEXT,  -- Free-form additional instructions
    
    -- Usage
    use_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    is_favorite BOOLEAN DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_prompt_preferences_user ON prompt_preferences(user_id);
CREATE INDEX idx_prompt_preferences_workspace ON prompt_preferences(workspace_id);
CREATE INDEX idx_prompt_preferences_key ON prompt_preferences(preference_key);
```

### Table 5: `prompt_categories` (Category Management)

```sql
CREATE TABLE IF NOT EXISTS prompt_categories (
    -- Primary Key
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Category Details
    category_key TEXT NOT NULL UNIQUE,
    category_name TEXT NOT NULL,
    category_description TEXT,
    
    -- Display
    icon TEXT,
    color TEXT,
    sort_order INTEGER DEFAULT 0,
    
    -- Parent/Child Hierarchy
    parent_category_id INTEGER,
    
    -- Status
    is_active BOOLEAN DEFAULT 1,
    is_system_category BOOLEAN DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (parent_category_id) REFERENCES prompt_categories(category_id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_categories_key ON prompt_categories(category_key);
CREATE INDEX idx_categories_parent ON prompt_categories(parent_category_id);
```

---

## Data Flow & Visibility Logic

### Visibility Rules

**1. Private Prompts** (`visibility = 'private'`)
- Only visible to `created_by_user_id`
- Not shareable unless explicitly shared

**2. Shared Prompts** (`visibility = 'shared'`)
- Visible to creator
- Visible to users in `prompt_shares` table where `share_scope = 'user'`
- Requires entry in `prompt_shares`

**3. Workspace Prompts** (`visibility = 'workspace'`)
- Visible to all users in the workspace (`workspace_id`)
- Automatically available to workspace members
- Can be shared outside workspace via `prompt_shares`

**4. Public Prompts** (`visibility = 'public'`)
- Visible to ALL users in the system
- System prompts (`is_system_prompt = 1`) are always public
- Can't be deleted (only by admins)

### Query Examples

**Get User's Available Prompts:**
```sql
-- All prompts user can see
SELECT DISTINCT pl.* 
FROM prompt_library pl
LEFT JOIN prompt_shares ps ON pl.prompt_id = ps.prompt_id
LEFT JOIN workspace_users wu ON pl.workspace_id = wu.workspace_id
WHERE 
    (pl.visibility = 'public')  -- Public prompts
    OR (pl.created_by_user_id = :user_id)  -- Own prompts
    OR (pl.visibility = 'workspace' AND wu.user_id = :user_id)  -- Workspace prompts
    OR (ps.shared_with_user_id = :user_id AND ps.is_active = 1)  -- Shared with user
    OR (ps.share_scope = 'workspace' AND wu.user_id = :user_id)  -- Shared with workspace
AND pl.is_active = 1 
AND pl.deleted_at IS NULL
ORDER BY pl.sort_order, pl.prompt_name;
```

**Get User's Personal Quick Actions:**
```sql
SELECT * FROM prompt_library
WHERE created_by_user_id = :user_id
AND prompt_type = 'quick_action'
AND is_active = 1
AND deleted_at IS NULL
ORDER BY sort_order, prompt_name;
```

**Get Public Library Prompts:**
```sql
SELECT * FROM prompt_library
WHERE visibility = 'public'
AND prompt_type = 'library'
AND is_active = 1
AND deleted_at IS NULL
ORDER BY category, sort_order, prompt_name;
```

**Get Shared Prompts:**
```sql
SELECT pl.*, ps.permission, ps.shared_by_user_id, u.username AS shared_by_username
FROM prompt_library pl
INNER JOIN prompt_shares ps ON pl.prompt_id = ps.prompt_id
INNER JOIN users u ON ps.shared_by_user_id = u.id
WHERE ps.shared_with_user_id = :user_id
AND ps.is_active = 1
AND (ps.expires_at IS NULL OR ps.expires_at > CURRENT_TIMESTAMP)
AND pl.is_active = 1
ORDER BY ps.created_at DESC;
```

---

## Migration Strategy

### Step 1: Create Tables in `ai_infrastructure.db`

```python
# AI_infrastructure/database/migrations/create_prompt_library_tables.py

import sqlite3
from pathlib import Path

def migrate():
    """Create prompt library tables"""
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create all 5 tables (SQL from above)
    cursor.executescript('''
        -- [Insert all CREATE TABLE statements here]
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Prompt library tables created successfully")

if __name__ == '__main__':
    migrate()
```

### Step 2: Seed System Prompts

```python
# AI_infrastructure/database/seeds/seed_system_prompts.py

def seed_system_prompts():
    """Insert built-in system prompts"""
    
    system_prompts = [
        # Quick Actions - Development
        {
            'prompt_key': 'expert_coder',
            'prompt_name': 'Expert Coder',
            'prompt_text': 'You are an expert software engineer...',
            'category': 'development',
            'icon': '⚡',
            'prompt_type': 'quick_action',
            'visibility': 'public',
            'is_system_prompt': 1,
            'created_by_user_id': 1  # System user
        },
        # ... (16 quick actions)
        
        # Library Prompts
        {
            'prompt_key': 'system_architect',
            'prompt_name': 'System Architect',
            'prompt_text': 'You are a senior system architect...',
            'category': 'development',
            'prompt_type': 'library',
            'visibility': 'public',
            'is_system_prompt': 1,
            'created_by_user_id': 1
        },
        # ... (6 library prompts)
    ]
    
    # Insert into database
    # ...
```

---

## Integration with Existing System

### Update `prompt_injection_manager.py`

```python
# AI_infrastructure/core/prompt_injection_manager.py

class PromptInjectionManager:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent.parent / 'data' / 'ai_infrastructure.db'
    
    def get_user_available_prompts(self, user_id: int, prompt_type: str = None):
        """Get all prompts available to user (private + shared + workspace + public)"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = '''
            SELECT DISTINCT pl.* 
            FROM prompt_library pl
            LEFT JOIN prompt_shares ps ON pl.prompt_id = ps.prompt_id
            LEFT JOIN workspace_users wu ON pl.workspace_id = wu.workspace_id
            WHERE 
                (pl.visibility = 'public')
                OR (pl.created_by_user_id = ?)
                OR (pl.visibility = 'workspace' AND wu.user_id = ?)
                OR (ps.shared_with_user_id = ? AND ps.is_active = 1)
            AND pl.is_active = 1 
            AND pl.deleted_at IS NULL
        '''
        
        params = [user_id, user_id, user_id]
        
        if prompt_type:
            query += ' AND pl.prompt_type = ?'
            params.append(prompt_type)
        
        query += ' ORDER BY pl.sort_order, pl.prompt_name'
        
        cursor.execute(query, params)
        prompts = cursor.fetchall()
        conn.close()
        
        return prompts
    
    def share_prompt(self, prompt_id: int, shared_by_user_id: int, 
                    shared_with_user_id: int = None, 
                    shared_with_workspace_id: int = None,
                    permission: str = 'view'):
        """Share prompt with user or workspace"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        share_scope = 'workspace' if shared_with_workspace_id else 'user'
        
        cursor.execute('''
            INSERT INTO prompt_shares 
            (prompt_id, shared_by_user_id, shared_with_user_id, 
             shared_with_workspace_id, share_scope, permission)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (prompt_id, shared_by_user_id, shared_with_user_id,
              shared_with_workspace_id, share_scope, permission))
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'share_id': cursor.lastrowid}
    
    def track_usage(self, prompt_id: int, user_id: int, thread_id: int = None):
        """Track prompt usage for analytics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Insert usage history
        cursor.execute('''
            INSERT INTO prompt_usage_history 
            (prompt_id, used_by_user_id, thread_id)
            VALUES (?, ?, ?)
        ''', (prompt_id, user_id, thread_id))
        
        # Update use_count and last_used_at
        cursor.execute('''
            UPDATE prompt_library 
            SET use_count = use_count + 1,
                last_used_at = CURRENT_TIMESTAMP
            WHERE prompt_id = ?
        ''', (prompt_id,))
        
        conn.commit()
        conn.close()
```

---

## API Endpoints Enhancement

### New Routes in `prompt_library_routes.py`

```python
# AI_infrastructure/routes/prompt_library_routes.py

@prompt_routes.route('/api/prompts/available', methods=['GET'])
@require_auth
def get_available_prompts():
    """Get ALL prompts available to user (private + shared + workspace + public)"""
    user_id = request.user_id
    prompt_type = request.args.get('prompt_type')
    category = request.args.get('category')
    
    manager = get_prompt_manager()
    prompts = manager.get_user_available_prompts(user_id, prompt_type)
    
    # Filter by category if specified
    if category:
        prompts = [p for p in prompts if p['category'] == category]
    
    return jsonify({
        'success': True,
        'prompts': prompts,
        'count': len(prompts)
    })

@prompt_routes.route('/api/prompts/<int:prompt_id>/share', methods=['POST'])
@require_auth
def share_prompt(prompt_id):
    """Share prompt with user or workspace"""
    user_id = request.user_id
    data = request.json
    
    shared_with_user_id = data.get('shared_with_user_id')
    shared_with_workspace_id = data.get('shared_with_workspace_id')
    permission = data.get('permission', 'view')
    
    manager = get_prompt_manager()
    result = manager.share_prompt(
        prompt_id, user_id, 
        shared_with_user_id, shared_with_workspace_id, 
        permission
    )
    
    return jsonify(result)

@prompt_routes.route('/api/prompts/shared-with-me', methods=['GET'])
@require_auth
def get_shared_prompts():
    """Get prompts shared with user"""
    user_id = request.user_id
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT pl.*, ps.permission, ps.shared_by_user_id, 
               u.username AS shared_by_username
        FROM prompt_library pl
        INNER JOIN prompt_shares ps ON pl.prompt_id = ps.prompt_id
        INNER JOIN users u ON ps.shared_by_user_id = u.id
        WHERE ps.shared_with_user_id = ?
        AND ps.is_active = 1
        AND (ps.expires_at IS NULL OR ps.expires_at > CURRENT_TIMESTAMP)
        ORDER BY ps.created_at DESC
    ''', (user_id,))
    
    prompts = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'success': True,
        'prompts': [dict(p) for p in prompts]
    })

@prompt_routes.route('/api/prompts/analytics', methods=['GET'])
@require_auth
def get_prompt_analytics():
    """Get prompt usage analytics for user"""
    user_id = request.user_id
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Most used prompts
    cursor.execute('''
        SELECT pl.prompt_name, COUNT(*) as usage_count
        FROM prompt_usage_history puh
        INNER JOIN prompt_library pl ON puh.prompt_id = pl.prompt_id
        WHERE puh.used_by_user_id = ?
        GROUP BY pl.prompt_id
        ORDER BY usage_count DESC
        LIMIT 10
    ''', (user_id,))
    
    most_used = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'success': True,
        'most_used_prompts': [dict(p) for p in most_used]
    })
```

---

## UI Components for Sharing

### Share Prompt Modal

```html
<!-- Share Prompt Button (on each prompt card) -->
<button class="share-prompt-btn" onclick="openShareModal(promptId)">
  <span>🔗</span> Share
</button>

<!-- Share Modal -->
<div id="sharePromptModal" class="modal">
  <div class="modal-content">
    <h2>Share Prompt</h2>
    
    <!-- Share with specific user -->
    <div class="share-option">
      <h3>Share with User</h3>
      <input type="text" id="shareUserEmail" placeholder="Enter user email">
      <select id="sharePermission">
        <option value="view">View Only</option>
        <option value="use">Can Use</option>
        <option value="clone">Can Clone</option>
        <option value="edit">Can Edit</option>
      </select>
      <button onclick="shareWithUser()">Share</button>
    </div>
    
    <!-- Share with workspace -->
    <div class="share-option">
      <h3>Share with Workspace</h3>
      <select id="shareWorkspace">
        <!-- Populated from user's workspaces -->
      </select>
      <button onclick="shareWithWorkspace()">Share</button>
    </div>
    
    <!-- Make public -->
    <div class="share-option">
      <h3>Make Public</h3>
      <button onclick="makePublic()">Share with Everyone</button>
    </div>
  </div>
</div>

<script>
async function shareWithUser() {
  const email = document.getElementById('shareUserEmail').value;
  const permission = document.getElementById('sharePermission').value;
  
  const response = await fetch(`/api/prompts/${currentPromptId}/share`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      shared_with_email: email,
      permission: permission
    })
  });
  
  const result = await response.json();
  if (result.success) {
    alert('Prompt shared successfully!');
    closeShareModal();
  }
}
</script>
```

---

## Benefits of This Design

✅ **Scalable** - Handles millions of prompts with proper indexing
✅ **Flexible** - Supports private, shared, workspace, and public prompts
✅ **Trackable** - Usage history and analytics built-in
✅ **Secure** - Permission-based access control
✅ **User-Friendly** - Easy sharing and discovery
✅ **Analytics** - Track effectiveness and usage patterns
✅ **Version Control** - Parent/child relationships for cloned prompts
✅ **Soft Deletes** - Never lose data, just mark as deleted
✅ **Workspace Integration** - Seamless workspace collaboration

---

## Migration Timeline

**Phase 1: Core Tables** (1 day)
- Create 5 tables in ai_infrastructure.db
- Seed system prompts (16 quick actions + 6 library)

**Phase 2: Manager Integration** (1 day)
- Update PromptInjectionManager to use database
- Add sharing methods
- Add usage tracking

**Phase 3: API Routes** (1 day)
- Add sharing endpoints
- Add analytics endpoints
- Add discovery endpoints

**Phase 4: UI** (2 days)
- Share modal
- Shared prompts view
- Public prompt library browser

**Total: 5 days for complete implementation**

---

## Status

✅ **Design Complete** - Full schema and architecture defined
⏳ **Implementation** - Ready to begin migration
📊 **Testing** - After implementation

**Ready to proceed with implementation!**
