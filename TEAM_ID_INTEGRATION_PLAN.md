# Team ID Implementation - Complete Integration Plan

## ✅ Database Migration Complete

- ✅ Added `sender_team_id`, `recipient_team_id`, `message_type` to `sessions.messages`
- ✅ Created indexes for fast Team ID filtering
- ✅ Verified users table has `parent_user_id`, `is_sub_user`, `display_name`

---

## 🔍 Display Name System Analysis

### Current Implementation Found:

**1. Database Column (`users.display_name`):**
- Column exists in `ai_infrastructure.users` table
- Currently stores free-text names like "Sarah", "Bob"
- Updated via `/api/auth/update-display-name` endpoint

**2. Backend Endpoint (`auth_routes.py` line 457-520):**
```python
@auth_bp.route('/update-display-name', methods=['POST'])
def update_display_name():
    # Updates users.display_name column
    # Sanitizes to 50 chars max
```

**3. Frontend Handler (`display-name-handler.js`):**
- Shows modal prompt for display name entry
- Stores in `localStorage.session_display_name`
- Saves to backend via `/update-display-name`
- Updates `SynergyRealtime.sessionDisplayName`

**4. Account Sidebar UI (`business-ai-platform-v2.html`):**
- Line 17002-17005: Auth display name input
- Line 19640-19643: Sidebar display name input
- Line 26323-26762: Display name management functions
- Line 26693: `saveDisplayName()` function

---

## 🔄 Integration Strategy

### **Option 1: Extend Display Name to Team ID (RECOMMENDED)**

Keep existing display_name system but enhance it:

1. **Rename Column** (optional): `display_name` → `team_id` (or keep as is)
2. **Make Team ID = Username** for sub-users
3. **When creating Team ID**: Create full sub-user row with `is_sub_user=TRUE`
4. **When messaging**: Use `username` field as Team ID for routing

**Advantages:**
- Minimal code changes
- Uses existing sub-user system
- `username` is unique and indexed
- Already linked to parent via `parent_user_id`

**Implementation:**
```python
# When adding Team ID, create sub-user
INSERT INTO ai_infrastructure.users (
    username,  -- THIS IS THE TEAM ID
    email,
    password_hash,
    parent_user_id,
    is_sub_user,
    display_name  -- Same as username for consistency
) VALUES (
    'Sarah',  -- username = Team ID
    'sarah@team.local',
    password_hash,
    parent_user_id,
    TRUE,
    'Sarah'
)

# When sending message
INSERT INTO sessions.messages (
    user_id,  -- Parent account ID
    sender_team_id,  -- Username of sender
    recipient_team_id,  -- Username of recipient
    message_type,  -- 'private' | 'broadcast'
    content
) VALUES (
    5,  -- Account #5
    'Sarah',  -- Sender's username
    'Bob',  -- Recipient's username
    'private',
    'Hello Bob!'
)
```

### **Option 2: Pure Display Name (SIMPLER)**

Just use `display_name` without sub-users:

1. Keep display_name as free text
2. Add message routing by display_name
3. **Limitation**: No individual logins, no passwords, just labels

---

## 🚀 RECOMMENDED IMPLEMENTATION

**Use Option 1** - Make Team IDs = Sub-Users with individual logins:

### Backend Endpoints Needed:

**1. POST `/api/auth/team-ids/add`**
- Creates sub-user with `is_sub_user=TRUE`
- `username` = Team ID name
- `parent_user_id` = current user
- Optional password for login

**2. GET `/api/auth/team-ids`**
- Lists all sub-users for current user
- Shows active sessions, last active

**3. PUT `/api/auth/team-ids/<team_id>`**
- Update Team ID settings
- Change password, permissions

**4. DELETE `/api/auth/team-ids/<team_id>`**
- Soft delete (set `is_active=FALSE`)
- Revoke all sessions

### Message Routing Changes:

**Update message save to include Team ID:**
```python
def save_message_with_team_id(
    user_id: int,  # Parent account
    sender_team_id: str,  # Username of sender
    recipient_team_id: str | None,  # Username of recipient or None
    content: str
):
    cursor.execute("""
        INSERT INTO sessions.messages (
            user_id, sender_team_id, recipient_team_id, 
            message_type, content, role, timestamp
        ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """, [
        user_id, 
        sender_team_id, 
        recipient_team_id,
        'private' if recipient_team_id else 'broadcast',
        content,
        'user'
    ])
```

**Update message retrieval to filter by Team ID:**
```python
def get_team_messages(user_id: int, team_id: str):
    cursor.execute("""
        SELECT * FROM sessions.messages
        WHERE user_id = %s 
        AND (
            recipient_team_id = %s  -- Direct to this Team ID
            OR recipient_team_id IS NULL  -- Broadcast
            OR sender_team_id = %s  -- Sent by this Team ID
        )
        ORDER BY timestamp DESC
    """, [user_id, team_id, team_id])
```

---

## 📝 Frontend Integration

### Update Chat Sidebar to Show Team IDs:

**1. Detect Current Team ID:**
```javascript
// Get current user's Team ID
const currentTeamId = window.UserAuth?.user?.username;
const isSubUser = window.UserAuth?.user?.is_sub_user;
const parentUserId = window.UserAuth?.user?.parent_user_id;
```

**2. Show Team Members in Sidebar:**
```javascript
// Fetch Team IDs for current account
async function loadTeamMembers() {
    const response = await fetch('/api/auth/team-ids');
    const data = await response.json();
    
    displayTeamMembers(data.team_ids);
}
```

**3. Add Team ID Selector to Message Form:**
```html
<select id="recipientTeamId">
    <option value="">Broadcast to All Team</option>
    <option value="Sarah">Sarah</option>
    <option value="Bob">Bob</option>
</select>
```

---

## 🔑 Key Decisions:

1. **Team ID = username** (sub-user system)
2. **Messages table schema**: `sessions.messages` (not ai_infrastructure)
3. **Routing logic**: Filter by `recipient_team_id`
4. **Display name**: Keep for backward compatibility, but `username` is primary

---

## 📊 Next Steps:

1. ✅ Database migration complete
2. ⏳ Add Team ID endpoints to auth_routes.py
3. ⏳ Update message_service.py with Team ID routing
4. ⏳ Add Team IDs tab to Account Settings UI
5. ⏳ Update chat-sidebar.js with Team ID selector
6. ⏳ Test Team ID creation and messaging

---

## Files to Modify:

- [ ] `AI_infrastructure/routes/auth_routes.py` - Add 4 Team ID endpoints
- [ ] `AI_infrastructure/message_service.py` - Add Team ID routing functions
- [ ] `UI/business-ai-platform-v2.html` - Add Team IDs tab HTML + JavaScript
- [ ] `UI/shared/js/chat-sidebar.js` - Add Team ID selector and filtering
- [ ] `UI/shared/css/chat-sidebar.css` - Style Team ID elements

