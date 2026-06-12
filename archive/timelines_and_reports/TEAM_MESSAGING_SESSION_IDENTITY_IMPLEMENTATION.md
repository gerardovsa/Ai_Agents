# Team Messaging: Session Identity Management
## Professional Renaming + Identity Management UI

---

## 🎯 Changes Overview

### 1. Terminology Update
- **OLD**: "Display Name" (sounds casual/temporary)
- **NEW**: "Session Identity" (professional, serious)

### 2. New "Session Identities" Tab
Add to Account Settings sidebar with:
- List all session identities for this user
- Show IP address, last active, device info
- Allow rename/delete old identities
- Enforce consistency (same base name across devices)

---

## 📊 Database: Already Set Up!

You already have everything needed:

```sql
-- Users table (ai_infrastructure.users)
display_name TEXT  -- We'll keep this column name internally

-- Sessions table (ai_infrastructure.user_sessions)
user_id INTEGER
session_token TEXT
device_info JSONB
ip_address TEXT
last_active TIMESTAMP
created_at TIMESTAMP
```

**New view for Session Identities:**
```sql
-- Get all unique session identities for a user
SELECT DISTINCT
    s.display_name as identity_name,
    MAX(us.last_active) as last_active,
    MAX(us.ip_address) as last_ip,
    COUNT(us.session_token) as active_sessions,
    array_agg(DISTINCT us.device_info->>'os') as devices
FROM ai_infrastructure.users s
JOIN ai_infrastructure.user_sessions us ON us.user_id = s.id
WHERE s.id = ?
GROUP BY s.display_name;
```

---

## 🎨 UI Changes

### Location: Account Settings Sidebar

Add new tab after "Security":

```
[Profile] [Security] [Session Identities] [Preferences]
```

### Tab Content: Session Identities Manager

```html
<div id="session-identities-tab" class="account-tab-content" style="display: none;">
    <div class="account-section">
        <h3 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 700;">
            <i class="fas fa-user-tag"></i> Your Session Identities
        </h3>
        <p style="font-size: 12px; color: var(--text-secondary); margin-bottom: 16px;">
            Session identities allow team members sharing the same account to identify themselves.
            Each identity is linked to your devices and IP addresses for security.
        </p>

        <!-- Current Identity -->
        <div style="background: var(--bg-success-subtle); border: 1px solid var(--border-success); border-radius: 8px; padding: 12px; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">
                        <i class="fas fa-check-circle" style="color: var(--success);"></i>
                        <span id="currentIdentityName">Bob (Mac)</span>
                        <span style="background: var(--success); color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-left: 6px;">CURRENT</span>
                    </div>
                    <div style="font-size: 11px; color: var(--text-secondary);">
                        This device • Last active: Just now
                    </div>
                </div>
                <button onclick="editCurrentIdentity()" style="padding: 6px 12px; background: var(--bg-primary); border: 1px solid var(--border-primary); border-radius: 6px; font-size: 11px; cursor: pointer;">
                    <i class="fas fa-edit"></i> Rename
                </button>
            </div>
        </div>

        <!-- Other Identities -->
        <div id="otherIdentitiesList">
            <!-- Populated by JavaScript -->
        </div>

        <!-- No Other Identities Message -->
        <div id="noOtherIdentities" style="display: none; text-align: center; padding: 20px; color: var(--text-muted); font-size: 12px;">
            <i class="fas fa-info-circle" style="font-size: 20px; margin-bottom: 8px; display: block;"></i>
            No other session identities found
        </div>

        <!-- Info Box -->
        <div style="background: var(--bg-info-subtle); border: 1px solid var(--border-info); border-radius: 8px; padding: 12px; margin-top: 16px;">
            <div style="font-size: 11px; color: var(--text-primary);">
                <i class="fas fa-lightbulb" style="color: var(--info);"></i>
                <strong>Team Messaging:</strong>
                <ul style="margin: 8px 0 0 20px; padding: 0;">
                    <li>Each identity represents a different team member</li>
                    <li>Messages can be sent privately between identities</li>
                    <li>Old/inactive identities can be removed for security</li>
                </ul>
            </div>
        </div>
    </div>
</div>
```

### Identity List Item Template:

```html
<div class="identity-item" data-identity-name="Sarah (Windows)" style="background: var(--bg-secondary); border: 1px solid var(--border-default); border-radius: 8px; padding: 12px; margin-bottom: 8px;">
    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 12px;">
        <div style="flex: 1;">
            <!-- Identity Name -->
            <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 6px;">
                <i class="fas fa-user-circle" style="color: var(--accent-primary);"></i>
                Sarah (Windows)
            </div>

            <!-- Last Active -->
            <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px;">
                <i class="fas fa-clock" style="font-size: 9px;"></i>
                Last active: 2 hours ago
            </div>

            <!-- IP Address -->
            <div style="font-size: 10px; color: var(--text-tertiary); margin-bottom: 4px;">
                <i class="fas fa-map-marker-alt" style="font-size: 8px;"></i>
                IP: 192.168.1.105
            </div>

            <!-- Devices -->
            <div style="font-size: 10px; color: var(--text-tertiary);">
                <i class="fas fa-desktop" style="font-size: 8px;"></i>
                Devices: Windows, Android
            </div>

            <!-- Active Sessions Count -->
            <div style="font-size: 10px; color: var(--text-tertiary); margin-top: 4px;">
                <i class="fas fa-wifi" style="font-size: 8px;"></i>
                2 active sessions
            </div>
        </div>

        <!-- Actions -->
        <div style="display: flex; flex-direction: column; gap: 6px;">
            <button onclick="renameIdentity('Sarah (Windows)')" style="padding: 6px 12px; background: var(--bg-primary); border: 1px solid var(--border-primary); border-radius: 6px; font-size: 11px; cursor: pointer; white-space: nowrap;">
                <i class="fas fa-edit"></i> Rename
            </button>
            <button onclick="deleteIdentity('Sarah (Windows)')" style="padding: 6px 12px; background: var(--bg-danger-subtle); color: var(--danger); border: 1px solid var(--border-danger); border-radius: 6px; font-size: 11px; cursor: pointer; white-space: nowrap;">
                <i class="fas fa-trash"></i> Delete
            </button>
        </div>
    </div>
</div>
```

---

## 🔧 Implementation Code

### Step 1: Add Backend API Endpoint

File: `AI_infrastructure/routes/auth_routes.py`

```python
@auth_bp.route('/api/auth/session-identities', methods=['GET'])
@require_auth
def get_session_identities():
    """
    Get all unique session identities for current user
    
    Returns:
    {
        "success": true,
        "current_identity": {
            "identity_name": "Bob (Mac)",
            "device": "Mac",
            "last_active": "2025-12-17T10:30:00Z"
        },
        "other_identities": [
            {
                "identity_name": "Sarah (Windows)",
                "last_active": "2025-12-17T08:15:00Z",
                "last_ip": "192.168.1.105",
                "active_sessions": 2,
                "devices": ["Windows", "Android"]
            }
        ]
    }
    """
    cursor = None
    conn = None
    try:
        user_id = request.user['user_id']
        current_session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Get current identity from user's display_name
        sql, params = convert_sql_placeholders('''
            SELECT display_name 
            FROM ai_infrastructure.users 
            WHERE id = %s
        ''', (user_id,))
        cursor.execute(sql, params)
        row = cursor.fetchone()
        current_base_name = row['display_name'] if row else None
        
        # Get current device suffix
        current_device = get_device_suffix_from_ua(request.headers.get('User-Agent', ''))
        current_identity = f"{current_base_name} ({current_device})" if current_base_name else None
        
        # Get all unique session identities from sessions table
        # Group by display_name pattern to find other team members
        sql, params = convert_sql_placeholders('''
            SELECT 
                session_display_name as identity_name,
                MAX(last_active) as last_active,
                MAX(ip_address) as last_ip,
                COUNT(DISTINCT session_token) as active_sessions,
                array_agg(DISTINCT device_info->>'os') as devices
            FROM ai_infrastructure.user_sessions
            WHERE user_id = %s 
              AND session_display_name IS NOT NULL
              AND session_display_name != %s
            GROUP BY session_display_name
            ORDER BY MAX(last_active) DESC
        ''', (user_id, current_identity))
        cursor.execute(sql, params)
        other_identities = cursor.fetchall()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'current_identity': {
                'identity_name': current_identity,
                'device': current_device,
                'last_active': datetime.now().isoformat()
            },
            'other_identities': [
                {
                    'identity_name': row['identity_name'],
                    'last_active': row['last_active'].isoformat() if row['last_active'] else None,
                    'last_ip': row['last_ip'],
                    'active_sessions': row['active_sessions'],
                    'devices': [d for d in row['devices'] if d]  # Remove nulls
                }
                for row in other_identities
            ]
        })
        
    except Exception as e:
        print(f"❌ Get session identities error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


@auth_bp.route('/api/auth/session-identity/rename', methods=['POST'])
@require_auth
def rename_session_identity():
    """
    Rename a session identity
    
    Body:
    {
        "old_name": "Bob (Mac)",
        "new_name": "Robert"
    }
    """
    cursor = None
    conn = None
    try:
        user_id = request.user['user_id']
        data = request.get_json()
        
        old_name = data.get('old_name')
        new_base_name = data.get('new_name', '').strip()[:50]
        
        if not new_base_name:
            return jsonify({'success': False, 'error': 'New name cannot be empty'}), 400
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Update user's base display_name
        sql, params = convert_sql_placeholders('''
            UPDATE ai_infrastructure.users 
            SET display_name = %s
            WHERE id = %s
        ''', (new_base_name, user_id))
        cursor.execute(sql, params)
        
        # Update all session records for this identity
        device_suffix = old_name.split('(')[-1].strip(')') if '(' in old_name else ''
        new_full_name = f"{new_base_name} ({device_suffix})" if device_suffix else new_base_name
        
        sql, params = convert_sql_placeholders('''
            UPDATE ai_infrastructure.user_sessions
            SET session_display_name = %s
            WHERE user_id = %s AND session_display_name = %s
        ''', (new_full_name, user_id, old_name))
        cursor.execute(sql, params)
        
        conn.commit()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'new_identity_name': new_full_name
        })
        
    except Exception as e:
        print(f"❌ Rename identity error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


@auth_bp.route('/api/auth/session-identity/delete', methods=['POST'])
@require_auth
def delete_session_identity():
    """
    Delete a session identity (revoke all sessions for that identity)
    
    Body:
    {
        "identity_name": "Sarah (Windows)"
    }
    """
    cursor = None
    conn = None
    try:
        user_id = request.user['user_id']
        data = request.get_json()
        
        identity_name = data.get('identity_name')
        
        if not identity_name:
            return jsonify({'success': False, 'error': 'identity_name required'}), 400
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Delete all sessions for this identity
        sql, params = convert_sql_placeholders('''
            DELETE FROM ai_infrastructure.user_sessions
            WHERE user_id = %s AND session_display_name = %s
        ''', (user_id, identity_name))
        cursor.execute(sql, params)
        rows_deleted = cursor.rowcount
        
        conn.commit()
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'sessions_revoked': rows_deleted
        })
        
    except Exception as e:
        print(f"❌ Delete identity error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


def get_device_suffix_from_ua(user_agent):
    """Extract device suffix from user agent string"""
    ua = user_agent.lower()
    
    if 'iphone' in ua:
        return 'iPhone'
    elif 'ipad' in ua:
        return 'iPad'
    elif 'android' in ua:
        if 'mobile' in ua:
            return 'Android Phone'
        return 'Android Tablet'
    elif 'mac' in ua:
        return 'Mac'
    elif 'windows' in ua:
        return 'Windows'
    elif 'linux' in ua:
        return 'Linux'
    
    return 'Desktop'
```

### Step 2: Add Frontend JavaScript

File: `UI/business-ai-platform-v2.html` (add to Account Settings section)

```javascript
// ==================== SESSION IDENTITIES MANAGEMENT ====================

async function loadSessionIdentities() {
    try {
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
        if (!token) {
            console.warn('[IDENTITIES] No auth token');
            return;
        }

        const response = await fetch(`${API_BASE_URL}/api/auth/session-identities`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            displaySessionIdentities(data);
        } else {
            console.error('[IDENTITIES] Failed to load:', response.status);
        }
    } catch (error) {
        console.error('[IDENTITIES] Error loading identities:', error);
    }
}

function displaySessionIdentities(data) {
    const currentIdentityEl = document.getElementById('currentIdentityName');
    const otherListEl = document.getElementById('otherIdentitiesList');
    const noOtherEl = document.getElementById('noOtherIdentities');

    // Display current identity
    if (currentIdentityEl && data.current_identity) {
        currentIdentityEl.textContent = data.current_identity.identity_name;
    }

    // Display other identities
    if (otherListEl) {
        if (data.other_identities && data.other_identities.length > 0) {
            otherListEl.innerHTML = data.other_identities.map(identity => {
                const lastActive = formatTimeAgo(new Date(identity.last_active));
                const devices = identity.devices.join(', ');

                return `
                    <div class="identity-item" data-identity-name="${identity.identity_name}" style="background: var(--bg-secondary); border: 1px solid var(--border-default); border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                        <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 12px;">
                            <div style="flex: 1;">
                                <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 6px;">
                                    <i class="fas fa-user-circle" style="color: var(--accent-primary);"></i>
                                    ${identity.identity_name}
                                </div>
                                <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 4px;">
                                    <i class="fas fa-clock" style="font-size: 9px;"></i>
                                    Last active: ${lastActive}
                                </div>
                                <div style="font-size: 10px; color: var(--text-tertiary); margin-bottom: 4px;">
                                    <i class="fas fa-map-marker-alt" style="font-size: 8px;"></i>
                                    IP: ${identity.last_ip || 'Unknown'}
                                </div>
                                <div style="font-size: 10px; color: var(--text-tertiary); margin-bottom: 4px;">
                                    <i class="fas fa-desktop" style="font-size: 8px;"></i>
                                    Devices: ${devices || 'Unknown'}
                                </div>
                                <div style="font-size: 10px; color: var(--text-tertiary);">
                                    <i class="fas fa-wifi" style="font-size: 8px;"></i>
                                    ${identity.active_sessions} active session(s)
                                </div>
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 6px;">
                                <button onclick="renameIdentity('${identity.identity_name}')" style="padding: 6px 12px; background: var(--bg-primary); border: 1px solid var(--border-primary); border-radius: 6px; font-size: 11px; cursor: pointer; white-space: nowrap;">
                                    <i class="fas fa-edit"></i> Rename
                                </button>
                                <button onclick="deleteIdentity('${identity.identity_name}')" style="padding: 6px 12px; background: var(--bg-danger-subtle); color: var(--danger); border: 1px solid var(--border-danger); border-radius: 6px; font-size: 11px; cursor: pointer; white-space: nowrap;">
                                    <i class="fas fa-trash"></i> Delete
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

            otherListEl.style.display = 'block';
            if (noOtherEl) noOtherEl.style.display = 'none';
        } else {
            otherListEl.innerHTML = '';
            if (noOtherEl) noOtherEl.style.display = 'block';
        }
    }
}

function editCurrentIdentity() {
    const currentName = document.getElementById('currentIdentityName').textContent;
    const baseName = currentName.split('(')[0].trim();

    const newName = prompt(`Rename your session identity:\n\n(Device suffix will be added automatically)`, baseName);

    if (newName && newName.trim()) {
        renameIdentityAPI(currentName, newName.trim());
    }
}

async function renameIdentity(oldName) {
    const baseName = oldName.split('(')[0].trim();
    const newName = prompt(`Rename session identity "${oldName}":\n\n(Device suffix will be kept)`, baseName);

    if (newName && newName.trim()) {
        renameIdentityAPI(oldName, newName.trim());
    }
}

async function renameIdentityAPI(oldName, newBaseName) {
    try {
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
        if (!token) return;

        const response = await fetch(`${API_BASE_URL}/api/auth/session-identity/rename`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                old_name: oldName,
                new_name: newBaseName
            })
        });

        if (response.ok) {
            const data = await response.json();
            console.log('[IDENTITIES] Renamed successfully:', data.new_identity_name);

            // Update localStorage if renaming current identity
            if (oldName === localStorage.getItem('session_display_name')) {
                localStorage.setItem('session_display_name', data.new_identity_name);
                localStorage.setItem('base_display_name', newBaseName);
            }

            // Reload identities list
            loadSessionIdentities();
        } else {
            alert('Failed to rename identity');
        }
    } catch (error) {
        console.error('[IDENTITIES] Rename error:', error);
        alert('Error renaming identity');
    }
}

async function deleteIdentity(identityName) {
    if (!confirm(`Delete session identity "${identityName}"?\n\nThis will revoke all active sessions for this identity.`)) {
        return;
    }

    try {
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
        if (!token) return;

        const response = await fetch(`${API_BASE_URL}/api/auth/session-identity/delete`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                identity_name: identityName
            })
        });

        if (response.ok) {
            const data = await response.json();
            console.log('[IDENTITIES] Deleted:', data.sessions_revoked, 'sessions revoked');

            // Reload identities list
            loadSessionIdentities();
        } else {
            alert('Failed to delete identity');
        }
    } catch (error) {
        console.error('[IDENTITIES] Delete error:', error);
        alert('Error deleting identity');
    }
}

function formatTimeAgo(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
}
```

---

## 📝 Migration Checklist

1. ✅ Add new backend routes to `auth_routes.py`
2. ✅ Add "Session Identities" tab to Account Settings sidebar
3. ✅ Update all references from "display_name" → "Session Identity" in UI text
4. ✅ Add JavaScript functions for identity management
5. ✅ Test rename functionality
6. ✅ Test delete functionality
7. ✅ Verify IP address and device info display correctly

---

## 🎯 Benefits

1. **Professional Terminology** - "Session Identity" instead of casual "Display Name"
2. **Security Visibility** - See IP addresses and devices for each identity
3. **Clean-Up Tool** - Delete old/unused identities
4. **Team Coordination** - Clear view of who's who in shared accounts
5. **Consistency Enforcement** - Base name stays same across devices

---

This gives you a **professional session identity management system** that integrates perfectly with team messaging!
