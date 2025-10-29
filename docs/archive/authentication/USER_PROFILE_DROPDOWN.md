# 👤 User Profile Dropdown Menu - Implementation Guide

## 📊 Current Authentication System

### Database: SQLite (`AI_infrastructure/ai_infrastructure.db`)

**Tables:**

1. **users** - User accounts
   ```sql
   - id (PRIMARY KEY)
   - username (UNIQUE)
   - email (UNIQUE)
   - password_hash
   - role ('user' or 'admin')
   - primary_gmail
   - created_at
   - last_active
   - metadata (JSON)
   ```

2. **user_gmail_accounts** - Gmail accounts linked to users
   ```sql
   - id (PRIMARY KEY)
   - user_id (FOREIGN KEY → users.id)
   - gmail_address
   - display_name
   - access_token
   - refresh_token
   - token_expiry
   - is_primary (BOOLEAN)
   - created_at
   ```

3. **user_sessions** - Active JWT sessions
   ```sql
   - id (PRIMARY KEY)
   - user_id (FOREIGN KEY → users.id)
   - token (JWT token)
   - ip_address
   - user_agent
   - created_at
   - expires_at
   ```

### API Endpoints:

- **POST** `/api/auth/register` - Register new user
- **POST** `/api/auth/login` - Login (returns JWT token + user profile)
- **GET** `/api/auth/verify` - Verify JWT token validity
- **GET** `/api/auth/profile` - Get full user profile (requires JWT)
- **GET** `/api/auth/gmail-accounts` - Get linked Gmail accounts
- **POST** `/api/auth/link-gmail` - Link new Gmail account

### Authentication Flow:

1. **User logs in** → Server returns JWT token + user profile
2. **JWT stored** in `localStorage` as `authToken`
3. **All API requests** include `Authorization: Bearer <token>` header
4. **Server verifies token** on each request
5. **Token expires** after 24 hours (configurable)

---

## 🎨 Standard User Profile Dropdown Features

### Standard Items (Industry Best Practices):

1. **User Info Section** (Read-only)
   - Avatar/Profile Picture
   - Display Name
   - Email Address
   - User Role (Admin/User)

2. **Account Management**
   - View Profile / Account Settings
   - Connected Accounts (Google Workspace, etc.)
   - Billing / Subscription (if applicable)
   - Notifications Settings

3. **Quick Actions**
   - Switch Workspace (if multi-tenant)
   - Preferences / Settings
   - Help & Documentation
   - Keyboard Shortcuts

4. **System Actions**
   - Logout
   - Sign out of all devices

### Examples from Popular Platforms:

**GitHub:**
- Signed in as @username
- Your profile
- Your repositories
- Your organizations
- Settings
- Sign out

**Google Workspace:**
- Profile photo + name
- Email
- Manage your Google Account
- Switch account
- Sign out

**Slack:**
- Profile & account
- Preferences
- Download Slack
- Sign out of [Workspace]

**Discord:**
- My Account
- User Settings
- Privacy & Safety
- Connections
- Log Out

---

## ✅ Proposed User Profile Dropdown

### Visual Layout:
```
┌─────────────────────────────────────┐
│  👤 Gerardo Oliva                   │
│  gerardo@vetsuccessacademy.com      │
│  🔑 Admin                            │
├─────────────────────────────────────┤
│  📧 Gmail Accounts (3 connected)    │
│  🔐 OAuth Status: ✅ Connected      │
├─────────────────────────────────────┤
│  ⚙️  Account Settings               │
│  🔔 Notifications                   │
│  🎨 Appearance                      │
│  🔑 Security                        │
│  🔌 Connected Services              │
│  📊 Usage & Billing                 │
├─────────────────────────────────────┤
│  📖 Help & Documentation            │
│  ⌨️  Keyboard Shortcuts             │
│  🐛 Report Bug                      │
├─────────────────────────────────────┤
│  🚪 Logout                          │
└─────────────────────────────────────┘
```

---

## 🔧 Implementation Plan

### Step 1: Update Header HTML

**Location:** `business-ai-platform-v2.html` line ~2900

**Current:**
```html
<div class="user-info" id="userInfo" style="display: none;" onclick="showUserMenu()">
    <i class="fas fa-user-circle" style="font-size: 20px;"></i>
    <div>
        <div class="user-email" id="userEmail"></div>
    </div>
</div>

<button class="logout-btn" id="logoutBtn" style="display: none;" onclick="handleLogout()">
    <i class="fas fa-sign-out-alt"></i> Logout
</button>
```

**Replace With:**
```html
<!-- User Profile Button -->
<div class="user-profile-container" id="userProfileContainer" style="display: none;">
    <button class="user-profile-btn" id="userProfileBtn" onclick="toggleUserMenu()">
        <div class="user-avatar">
            <i class="fas fa-user-circle"></i>
        </div>
        <div class="user-info-text">
            <div class="user-name" id="userName">Loading...</div>
            <div class="user-role" id="userRole">User</div>
        </div>
        <i class="fas fa-chevron-down dropdown-icon"></i>
    </button>
    
    <!-- Dropdown Menu -->
    <div class="user-dropdown-menu" id="userDropdownMenu">
        <!-- User Info Section -->
        <div class="dropdown-header">
            <div class="dropdown-user-avatar">
                <i class="fas fa-user-circle"></i>
            </div>
            <div class="dropdown-user-info">
                <div class="dropdown-user-name" id="dropdownUserName">Loading...</div>
                <div class="dropdown-user-email" id="dropdownUserEmail">Loading...</div>
                <div class="dropdown-user-role" id="dropdownUserRole">
                    <span class="role-badge">User</span>
                </div>
            </div>
        </div>
        
        <!-- OAuth Status -->
        <div class="dropdown-section">
            <div class="dropdown-item" onclick="showOAuthStatus()">
                <i class="fas fa-link"></i>
                <div class="dropdown-item-content">
                    <div class="dropdown-item-title">OAuth Status</div>
                    <div class="dropdown-item-subtitle" id="oauthStatus">Not connected</div>
                </div>
                <i class="fas fa-chevron-right dropdown-item-arrow"></i>
            </div>
            
            <div class="dropdown-item" onclick="showGmailAccounts()">
                <i class="fas fa-envelope"></i>
                <div class="dropdown-item-content">
                    <div class="dropdown-item-title">Gmail Accounts</div>
                    <div class="dropdown-item-subtitle" id="gmailCount">0 connected</div>
                </div>
                <i class="fas fa-chevron-right dropdown-item-arrow"></i>
            </div>
        </div>
        
        <div class="dropdown-divider"></div>
        
        <!-- Account Management -->
        <div class="dropdown-section">
            <div class="dropdown-item" onclick="showAccountSettings()">
                <i class="fas fa-cog"></i>
                <div class="dropdown-item-content">
                    <div class="dropdown-item-title">Account Settings</div>
                </div>
            </div>
            
            <div class="dropdown-item" onclick="showNotifications()">
                <i class="fas fa-bell"></i>
                <div class="dropdown-item-content">
                    <div class="dropdown-item-title">Notifications</div>
                </div>
            </div>
            
            <div class="dropdown-item" onclick="showAppearance()">
                <i class="fas fa-paint-brush"></i>
                <div class="dropdown-item-content">
                    <div class="dropdown-item-title">Appearance</div>
                </div>
            </div>
            
            <div class="dropdown-item" onclick="showSecurity()">
                <i class="fas fa-shield-alt"></i>
                <div class="dropdown-item-content">
                    <div class="dropdown-item-title">Security</div>
                </div>
            </div>
        </div>
        
        <div class="dropdown-divider"></div>
        
        <!-- Help & Support -->
        <div class="dropdown-section">
            <div class="dropdown-item" onclick="showHelp()">
                <i class="fas fa-question-circle"></i>
                <div class="dropdown-item-content">
                    <div class="dropdown-item-title">Help & Documentation</div>
                </div>
            </div>
            
            <div class="dropdown-item" onclick="showKeyboardShortcuts()">
                <i class="fas fa-keyboard"></i>
                <div class="dropdown-item-content">
                    <div class="dropdown-item-title">Keyboard Shortcuts</div>
                </div>
            </div>
            
            <div class="dropdown-item" onclick="reportBug()">
                <i class="fas fa-bug"></i>
                <div class="dropdown-item-content">
                    <div class="dropdown-item-title">Report Bug</div>
                </div>
            </div>
        </div>
        
        <div class="dropdown-divider"></div>
        
        <!-- Logout -->
        <div class="dropdown-section">
            <div class="dropdown-item logout-item" onclick="handleLogout()">
                <i class="fas fa-sign-out-alt"></i>
                <div class="dropdown-item-content">
                    <div class="dropdown-item-title">Logout</div>
                </div>
            </div>
        </div>
    </div>
</div>
```

### Step 2: Add CSS Styles

**Location:** `business-ai-platform-v2.html` CSS section (~line 260)

```css
/* ==================== USER PROFILE DROPDOWN ==================== */

.user-profile-container {
    position: relative;
}

.user-profile-btn {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: 8px;
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.2s ease;
}

.user-profile-btn:hover {
    background: var(--bg-hover);
    border-color: var(--accent-primary);
}

.user-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--accent-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 18px;
}

.user-info-text {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
}

.user-name {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.user-role {
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
}

.dropdown-icon {
    font-size: 12px;
    color: var(--text-secondary);
    transition: transform 0.2s ease;
}

.user-profile-btn.active .dropdown-icon {
    transform: rotate(180deg);
}

/* Dropdown Menu */
.user-dropdown-menu {
    position: absolute;
    top: calc(100% + 8px);
    right: 0;
    width: 320px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    z-index: 10000;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all 0.2s ease;
}

.user-dropdown-menu.active {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

/* Dropdown Header */
.dropdown-header {
    padding: var(--space-4);
    background: var(--bg-tertiary);
    border-bottom: 1px solid var(--border-default);
    border-radius: 12px 12px 0 0;
    display: flex;
    gap: var(--space-3);
}

.dropdown-user-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: var(--accent-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 24px;
    flex-shrink: 0;
}

.dropdown-user-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
}

.dropdown-user-name {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
}

.dropdown-user-email {
    font-size: 13px;
    color: var(--text-secondary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.dropdown-user-role {
    margin-top: var(--space-1);
}

.role-badge {
    display: inline-block;
    padding: 2px 8px;
    background: var(--accent-primary);
    color: white;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}

.role-badge.admin {
    background: var(--accent-error);
}

/* Dropdown Sections */
.dropdown-section {
    padding: var(--space-2);
}

.dropdown-item {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3);
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.dropdown-item:hover {
    background: var(--bg-hover);
}

.dropdown-item > i {
    width: 20px;
    font-size: 16px;
    color: var(--text-secondary);
    flex-shrink: 0;
}

.dropdown-item-content {
    flex: 1;
}

.dropdown-item-title {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
}

.dropdown-item-subtitle {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 2px;
}

.dropdown-item-arrow {
    font-size: 12px;
    color: var(--text-muted);
}

.dropdown-divider {
    height: 1px;
    background: var(--border-default);
    margin: var(--space-2) 0;
}

/* Logout Item */
.logout-item {
    color: var(--accent-error);
}

.logout-item > i {
    color: var(--accent-error);
}

.logout-item:hover {
    background: rgba(248, 81, 73, 0.1);
}

/* Click outside to close */
@media (max-width: 768px) {
    .user-dropdown-menu {
        width: 280px;
        right: -10px;
    }
    
    .user-info-text {
        display: none;
    }
}
```

### Step 3: Add JavaScript Functions

**Location:** `business-ai-platform-v2.html` after line ~8040

```javascript
// ==================== USER PROFILE DROPDOWN ====================

function toggleUserMenu() {
    const menu = document.getElementById('userDropdownMenu');
    const btn = document.getElementById('userProfileBtn');
    
    menu.classList.toggle('active');
    btn.classList.toggle('active');
}

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    const container = document.getElementById('userProfileContainer');
    const menu = document.getElementById('userDropdownMenu');
    const btn = document.getElementById('userProfileBtn');
    
    if (container && !container.contains(e.target)) {
        menu?.classList.remove('active');
        btn?.classList.remove('active');
    }
});

// Load user profile data
async function loadUserProfile() {
    try {
        const response = await fetch(`${API_CONFIG.baseUrl}/api/auth/profile`, {
            headers: {
                'Authorization': `Bearer ${UserAuth.token}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load profile');
        
        const data = await response.json();
        
        if (data.success) {
            const profile = data.profile;
            
            // Update header button
            document.getElementById('userName').textContent = profile.username;
            document.getElementById('userRole').textContent = profile.role;
            
            // Update dropdown header
            document.getElementById('dropdownUserName').textContent = profile.username;
            document.getElementById('dropdownUserEmail').textContent = profile.email;
            
            const roleBadge = document.querySelector('.role-badge');
            roleBadge.textContent = profile.role;
            if (profile.role === 'admin') {
                roleBadge.classList.add('admin');
            }
            
            // Update Gmail accounts count
            const gmailCount = profile.gmail_accounts?.length || 0;
            document.getElementById('gmailCount').textContent = `${gmailCount} connected`;
            
            // Update OAuth status
            const oauthStatus = document.getElementById('oauthStatus');
            if (profile.oauth_connected) {
                oauthStatus.innerHTML = '<i class="fas fa-check-circle" style="color: var(--accent-success);"></i> Connected';
            } else {
                oauthStatus.innerHTML = '<i class="fas fa-times-circle" style="color: var(--text-muted);"></i> Not connected';
            }
            
            // Show profile container
            document.getElementById('userProfileContainer').style.display = 'block';
        }
        
    } catch (error) {
        console.error('❌ Failed to load user profile:', error);
    }
}

// Profile menu actions
function showOAuthStatus() {
    alert('OAuth Status: Opens OAuth connection management');
    // TODO: Implement OAuth status modal
}

function showGmailAccounts() {
    alert('Gmail Accounts: Opens Gmail account management');
    // TODO: Implement Gmail accounts modal
}

function showAccountSettings() {
    alert('Account Settings: Opens settings panel');
    // TODO: Implement settings panel
}

function showNotifications() {
    alert('Notifications: Opens notification preferences');
    // TODO: Implement notifications panel
}

function showAppearance() {
    // Already has theme toggle, could expand
    alert('Appearance: Light/Dark theme, font size, etc.');
}

function showSecurity() {
    alert('Security: Change password, 2FA, active sessions');
    // TODO: Implement security panel
}

function showHelp() {
    window.open('/docs', '_blank');
}

function showKeyboardShortcuts() {
    alert('Keyboard Shortcuts:\n\n' +
          'Ctrl + K - Search\n' +
          'Ctrl + / - Show shortcuts\n' +
          'Ctrl + B - Toggle sidebar\n' +
          'Ctrl + Enter - Send message');
}

function reportBug() {
    window.open('https://github.com/your-repo/issues/new', '_blank');
}

// Update UserAuth.showMainApp() to load profile
const originalShowMainApp = UserAuth.showMainApp;
UserAuth.showMainApp = function() {
    originalShowMainApp.call(this);
    loadUserProfile();
};
```

---

## 🧪 Testing Checklist

### Test User Profile Display:
- [ ] Profile button shows after login
- [ ] Username displays correctly
- [ ] User role shows (User/Admin)
- [ ] Email displays in dropdown

### Test Dropdown Menu:
- [ ] Click profile button → Menu opens
- [ ] Click outside → Menu closes
- [ ] Click profile button again → Menu closes
- [ ] All menu items visible
- [ ] Smooth animation

### Test OAuth Status:
- [ ] Shows "Not connected" when no OAuth
- [ ] Shows "✅ Connected" after OAuth
- [ ] Gmail count updates correctly

### Test Menu Actions:
- [ ] OAuth Status → Opens modal (placeholder)
- [ ] Gmail Accounts → Opens modal (placeholder)
- [ ] Account Settings → Opens panel (placeholder)
- [ ] Help → Opens documentation
- [ ] Logout → Logs out successfully

### Test Responsive:
- [ ] Desktop → Shows full button with name
- [ ] Mobile → Shows avatar only
- [ ] Dropdown adjusts position
- [ ] No overflow issues

---

## 🚀 Future Enhancements

1. **Profile Picture Upload**
   - Allow users to upload custom avatar
   - Generate initials-based avatar
   - Gravatar integration

2. **Quick Stats**
   - Show usage statistics in dropdown
   - Last login time
   - Active sessions count

3. **Switch Account**
   - Multi-account support
   - Quick account switcher

4. **Status Indicator**
   - Online/Offline status
   - Custom status messages
   - Do Not Disturb mode

5. **Activity Feed**
   - Recent actions
   - Notifications preview
   - Quick access to recent items

---

**Ready to implement? I'll add the user profile dropdown to business-ai-platform-v2.html now!** 🚀
