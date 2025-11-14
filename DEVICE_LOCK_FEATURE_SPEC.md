# Device Lock/Unlock Feature - Complete Specification

**Created:** November 14, 2025  
**Status:** Design Phase  
**Priority:** High (Multi-user data isolation)

---

## Feature Overview

Allow users to **lock threads to specific devices** for private work, while still enabling collaboration when needed. This prevents conversation collisions across multiple computers using the same user account.

### User Benefits:
- 🔒 **Lock to device** - Private work without interference
- 🔓 **Unlock to share** - Collaborate when needed
- 👀 **Read-only access** - Other devices can view but not edit locked threads
- 🔔 **Lock notifications** - See which device has control
- 🔄 **Lock transfer** - Take over from another device

---

## Database Schema Changes

### 1. Add Device Tracking Table

```sql
-- New table: device_registry
CREATE TABLE device_registry (
    device_id TEXT PRIMARY KEY,          -- UUID generated client-side
    user_id INTEGER NOT NULL,            -- Owner of device
    device_name TEXT NOT NULL,           -- "MacBook Pro", "Work Desktop", etc.
    device_fingerprint TEXT,             -- Browser/OS fingerprint
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_device_user ON device_registry(user_id);
```

### 2. Add Lock Columns to Threads Table

```sql
-- Add to existing threads table
ALTER TABLE threads ADD COLUMN locked_to_device_id TEXT DEFAULT NULL;
ALTER TABLE threads ADD COLUMN locked_at TIMESTAMP DEFAULT NULL;
ALTER TABLE threads ADD COLUMN lock_mode TEXT DEFAULT 'unlocked'; 
-- lock_mode: 'unlocked', 'locked', 'read_only'

CREATE INDEX idx_thread_locks ON threads(locked_to_device_id);
```

### 3. Add Lock History Table (Optional - for audit trail)

```sql
-- Track lock/unlock events
CREATE TABLE thread_lock_history (
    lock_id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER NOT NULL,
    device_id TEXT NOT NULL,
    action TEXT NOT NULL,              -- 'locked', 'unlocked', 'transferred'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (thread_id) REFERENCES threads(thread_id),
    FOREIGN KEY (device_id) REFERENCES device_registry(device_id)
);
```

---

## Backend Implementation

### File: `AI_infrastructure/routes/device_lock_routes.py`

```python
"""
Device Lock Management Routes
Handles thread locking/unlocking per device
"""

from flask import Blueprint, request, jsonify
from AI_infrastructure.utils.database_helpers import (
    get_pooled_sqlite_connection,
    execute_sqlite_query,
    execute_sqlite_update
)
from pathlib import Path
import uuid
from datetime import datetime

device_lock_bp = Blueprint('device_lock', __name__)
DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'ai_infrastructure.db'


@device_lock_bp.route('/api/device/register', methods=['POST'])
def register_device():
    """
    Register or update device information
    
    Request:
        {
            "device_id": "uuid-or-null",  # null = generate new
            "device_name": "MacBook Pro",
            "user_id": 1,
            "device_fingerprint": "Mozilla/5.0..."
        }
    
    Response:
        {
            "success": true,
            "device_id": "abc-123-def",
            "device_name": "MacBook Pro"
        }
    """
    data = request.json
    user_id = data.get('user_id')
    device_id = data.get('device_id') or str(uuid.uuid4())
    device_name = data.get('device_name', 'Unknown Device')
    device_fingerprint = data.get('device_fingerprint', '')
    
    try:
        # Check if device exists
        existing = execute_sqlite_query(
            str(DB_PATH),
            "SELECT device_id FROM device_registry WHERE device_id = ?",
            (device_id,)
        )
        
        if existing:
            # Update last_seen_at
            execute_sqlite_update(
                str(DB_PATH),
                """UPDATE device_registry 
                   SET last_seen_at = CURRENT_TIMESTAMP,
                       device_name = ?,
                       device_fingerprint = ?
                   WHERE device_id = ?""",
                (device_name, device_fingerprint, device_id)
            )
        else:
            # Insert new device
            execute_sqlite_update(
                str(DB_PATH),
                """INSERT INTO device_registry 
                   (device_id, user_id, device_name, device_fingerprint)
                   VALUES (?, ?, ?, ?)""",
                (device_id, user_id, device_name, device_fingerprint)
            )
        
        return jsonify({
            'success': True,
            'device_id': device_id,
            'device_name': device_name
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@device_lock_bp.route('/api/thread/<int:thread_id>/lock', methods=['POST'])
def lock_thread(thread_id):
    """
    Lock thread to current device
    
    Request:
        {
            "device_id": "abc-123-def",
            "user_id": 1
        }
    
    Response:
        {
            "success": true,
            "locked_to": "MacBook Pro",
            "locked_at": "2025-11-14T10:30:00"
        }
    """
    data = request.json
    device_id = data.get('device_id')
    user_id = data.get('user_id')
    
    try:
        # Verify thread belongs to user
        thread = execute_sqlite_query(
            str(DB_PATH),
            "SELECT user_id FROM threads WHERE thread_id = ?",
            (thread_id,)
        )
        
        if not thread or thread[0]['user_id'] != user_id:
            return jsonify({'success': False, 'error': 'Thread not found'}), 404
        
        # Lock the thread
        execute_sqlite_update(
            str(DB_PATH),
            """UPDATE threads 
               SET locked_to_device_id = ?,
                   locked_at = CURRENT_TIMESTAMP,
                   lock_mode = 'locked'
               WHERE thread_id = ?""",
            (device_id, thread_id)
        )
        
        # Get device name
        device = execute_sqlite_query(
            str(DB_PATH),
            "SELECT device_name FROM device_registry WHERE device_id = ?",
            (device_id,)
        )
        
        device_name = device[0]['device_name'] if device else 'Unknown Device'
        
        # Log lock event (optional)
        execute_sqlite_update(
            str(DB_PATH),
            """INSERT INTO thread_lock_history (thread_id, device_id, action)
               VALUES (?, ?, 'locked')""",
            (thread_id, device_id)
        )
        
        return jsonify({
            'success': True,
            'locked_to': device_name,
            'locked_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@device_lock_bp.route('/api/thread/<int:thread_id>/unlock', methods=['POST'])
def unlock_thread(thread_id):
    """
    Unlock thread (make available to all devices)
    
    Request:
        {
            "device_id": "abc-123-def",
            "user_id": 1
        }
    
    Response:
        {
            "success": true,
            "message": "Thread unlocked"
        }
    """
    data = request.json
    device_id = data.get('device_id')
    user_id = data.get('user_id')
    
    try:
        # Verify thread is locked by this device OR user owns thread
        thread = execute_sqlite_query(
            str(DB_PATH),
            """SELECT locked_to_device_id, user_id 
               FROM threads WHERE thread_id = ?""",
            (thread_id,)
        )
        
        if not thread:
            return jsonify({'success': False, 'error': 'Thread not found'}), 404
        
        locked_device = thread[0]['locked_to_device_id']
        thread_user = thread[0]['user_id']
        
        # Only allow unlock if:
        # 1. Thread is locked to this device, OR
        # 2. User owns the thread (can force unlock from any device)
        if locked_device != device_id and thread_user != user_id:
            return jsonify({
                'success': False,
                'error': 'Cannot unlock thread locked by another device'
            }), 403
        
        # Unlock the thread
        execute_sqlite_update(
            str(DB_PATH),
            """UPDATE threads 
               SET locked_to_device_id = NULL,
                   locked_at = NULL,
                   lock_mode = 'unlocked'
               WHERE thread_id = ?""",
            (thread_id,)
        )
        
        # Log unlock event
        execute_sqlite_update(
            str(DB_PATH),
            """INSERT INTO thread_lock_history (thread_id, device_id, action)
               VALUES (?, ?, 'unlocked')""",
            (thread_id, device_id)
        )
        
        return jsonify({
            'success': True,
            'message': 'Thread unlocked'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@device_lock_bp.route('/api/thread/<int:thread_id>/lock-status', methods=['GET'])
def get_lock_status(thread_id):
    """
    Get lock status for thread
    
    Query params:
        device_id: Current device ID
        user_id: Current user ID
    
    Response:
        {
            "locked": true,
            "locked_to_device_id": "abc-123-def",
            "locked_to_device_name": "MacBook Pro",
            "locked_at": "2025-11-14T10:30:00",
            "is_current_device": false,
            "can_edit": false
        }
    """
    device_id = request.args.get('device_id')
    user_id = request.args.get('user_id')
    
    try:
        # Get thread lock status
        thread = execute_sqlite_query(
            str(DB_PATH),
            """SELECT t.locked_to_device_id, t.locked_at, t.lock_mode,
                      d.device_name, t.user_id
               FROM threads t
               LEFT JOIN device_registry d ON t.locked_to_device_id = d.device_id
               WHERE t.thread_id = ?""",
            (thread_id,)
        )
        
        if not thread:
            return jsonify({'success': False, 'error': 'Thread not found'}), 404
        
        thread_data = thread[0]
        locked_device_id = thread_data['locked_to_device_id']
        is_locked = locked_device_id is not None
        is_current_device = locked_device_id == device_id
        can_edit = not is_locked or is_current_device
        
        return jsonify({
            'locked': is_locked,
            'locked_to_device_id': locked_device_id,
            'locked_to_device_name': thread_data['device_name'],
            'locked_at': thread_data['locked_at'],
            'lock_mode': thread_data['lock_mode'],
            'is_current_device': is_current_device,
            'can_edit': can_edit,
            'is_owner': thread_data['user_id'] == int(user_id) if user_id else False
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@device_lock_bp.route('/api/user/<int:user_id>/devices', methods=['GET'])
def list_user_devices(user_id):
    """
    List all devices for user
    
    Response:
        {
            "devices": [
                {
                    "device_id": "abc-123",
                    "device_name": "MacBook Pro",
                    "last_seen_at": "2025-11-14T10:30:00",
                    "locked_threads_count": 3
                }
            ]
        }
    """
    try:
        devices = execute_sqlite_query(
            str(DB_PATH),
            """SELECT d.device_id, d.device_name, d.last_seen_at,
                      COUNT(t.thread_id) as locked_threads_count
               FROM device_registry d
               LEFT JOIN threads t ON t.locked_to_device_id = d.device_id
               WHERE d.user_id = ?
               GROUP BY d.device_id
               ORDER BY d.last_seen_at DESC""",
            (user_id,)
        )
        
        return jsonify({
            'success': True,
            'devices': devices
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

## Frontend Implementation

### File: `UI/business-ai-platform-v2.html` (Add Device Lock UI)

```javascript
// Device Lock Manager Class
class DeviceLockManager {
    constructor() {
        this.deviceId = this.getOrCreateDeviceId();
        this.deviceName = this.detectDeviceName();
        this.apiBaseUrl = window.location.origin;
        this.registerDevice();
    }
    
    getOrCreateDeviceId() {
        let deviceId = localStorage.getItem('device_id');
        if (!deviceId) {
            deviceId = this.generateUUID();
            localStorage.setItem('device_id', deviceId);
        }
        return deviceId;
    }
    
    detectDeviceName() {
        // Try to detect device name from browser
        const ua = navigator.userAgent;
        let name = 'Unknown Device';
        
        if (ua.includes('Mac')) name = 'Mac';
        else if (ua.includes('Windows')) name = 'Windows PC';
        else if (ua.includes('Linux')) name = 'Linux PC';
        else if (ua.includes('iPhone')) name = 'iPhone';
        else if (ua.includes('iPad')) name = 'iPad';
        else if (ua.includes('Android')) name = 'Android';
        
        // Check if user has custom name saved
        const customName = localStorage.getItem('device_name');
        if (customName) name = customName;
        
        return name;
    }
    
    async registerDevice() {
        try {
            const userId = window.currentUserId || 1;
            const response = await fetch(`${this.apiBaseUrl}/api/device/register`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    device_id: this.deviceId,
                    device_name: this.deviceName,
                    user_id: userId,
                    device_fingerprint: navigator.userAgent
                })
            });
            
            const data = await response.json();
            if (data.success) {
                console.log(`[DEVICE] Registered: ${data.device_name} (${data.device_id})`);
            }
        } catch (error) {
            console.error('[DEVICE] Registration failed:', error);
        }
    }
    
    async lockThread(threadId) {
        try {
            const userId = window.currentUserId || 1;
            const response = await fetch(`${this.apiBaseUrl}/api/thread/${threadId}/lock`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    device_id: this.deviceId,
                    user_id: userId
                })
            });
            
            const data = await response.json();
            if (data.success) {
                window.showNotification(`Thread locked to ${data.locked_to}`, 'success');
                this.updateLockUI(threadId, true);
                return true;
            } else {
                window.showNotification(`Failed to lock: ${data.error}`, 'error');
                return false;
            }
        } catch (error) {
            console.error('[DEVICE] Lock failed:', error);
            return false;
        }
    }
    
    async unlockThread(threadId) {
        try {
            const userId = window.currentUserId || 1;
            const response = await fetch(`${this.apiBaseUrl}/api/thread/${threadId}/unlock`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    device_id: this.deviceId,
                    user_id: userId
                })
            });
            
            const data = await response.json();
            if (data.success) {
                window.showNotification('Thread unlocked (available to all devices)', 'success');
                this.updateLockUI(threadId, false);
                return true;
            } else {
                window.showNotification(`Failed to unlock: ${data.error}`, 'error');
                return false;
            }
        } catch (error) {
            console.error('[DEVICE] Unlock failed:', error);
            return false;
        }
    }
    
    async getLockStatus(threadId) {
        try {
            const userId = window.currentUserId || 1;
            const response = await fetch(
                `${this.apiBaseUrl}/api/thread/${threadId}/lock-status?device_id=${this.deviceId}&user_id=${userId}`
            );
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('[DEVICE] Failed to get lock status:', error);
            return null;
        }
    }
    
    updateLockUI(threadId, isLocked) {
        // Update thread header with lock indicator
        const threadHeader = document.querySelector(`[data-thread-id="${threadId}"] .thread-header`);
        if (!threadHeader) return;
        
        let lockIndicator = threadHeader.querySelector('.lock-indicator');
        if (!lockIndicator) {
            lockIndicator = document.createElement('div');
            lockIndicator.className = 'lock-indicator';
            threadHeader.prepend(lockIndicator);
        }
        
        if (isLocked) {
            lockIndicator.innerHTML = `
                <div class="lock-status locked">
                    <i class="fas fa-lock"></i>
                    <span>Locked to this device</span>
                    <button onclick="deviceLockManager.unlockThread(${threadId})" 
                            class="unlock-btn">
                        <i class="fas fa-unlock"></i> Unlock
                    </button>
                </div>
            `;
            
            // Disable chat input on other devices
            this.disableChatInputIfNeeded(threadId);
        } else {
            lockIndicator.innerHTML = `
                <div class="lock-status unlocked">
                    <i class="fas fa-unlock"></i>
                    <span>Shared across devices</span>
                    <button onclick="deviceLockManager.lockThread(${threadId})" 
                            class="lock-btn">
                        <i class="fas fa-lock"></i> Lock to This Device
                    </button>
                </div>
            `;
            
            // Enable chat input
            this.enableChatInput(threadId);
        }
    }
    
    async disableChatInputIfNeeded(threadId) {
        const status = await this.getLockStatus(threadId);
        if (!status || !status.locked) return;
        
        if (!status.is_current_device) {
            // Thread is locked by another device
            const chatInput = document.querySelector('.ai-chat-input-container');
            if (chatInput) {
                chatInput.classList.add('disabled');
                chatInput.innerHTML = `
                    <div class="read-only-notice">
                        <i class="fas fa-lock"></i>
                        <span>Thread locked by ${status.locked_to_device_name}</span>
                        <small>You can view messages but cannot send new ones</small>
                    </div>
                `;
            }
        }
    }
    
    enableChatInput(threadId) {
        const chatInput = document.querySelector('.ai-chat-input-container');
        if (chatInput) {
            chatInput.classList.remove('disabled');
            // Restore original chat input HTML
            // (implementation depends on your existing chat input structure)
        }
    }
    
    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
}

// Initialize on page load
let deviceLockManager;
document.addEventListener('DOMContentLoaded', () => {
    deviceLockManager = new DeviceLockManager();
    console.log('[DEVICE LOCK] Manager initialized');
});
```

### CSS Styling

```css
/* Device Lock UI Styles */
.lock-indicator {
    margin-bottom: 10px;
    padding: 10px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.05);
}

.lock-status {
    display: flex;
    align-items: center;
    gap: 10px;
}

.lock-status.locked {
    color: #ffa500;
}

.lock-status.unlocked {
    color: #4caf50;
}

.lock-status i {
    font-size: 16px;
}

.lock-btn, .unlock-btn {
    margin-left: auto;
    padding: 6px 12px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s;
}

.lock-btn {
    background: rgba(255, 165, 0, 0.2);
    color: #ffa500;
}

.lock-btn:hover {
    background: rgba(255, 165, 0, 0.3);
}

.unlock-btn {
    background: rgba(76, 175, 80, 0.2);
    color: #4caf50;
}

.unlock-btn:hover {
    background: rgba(76, 175, 80, 0.3);
}

.ai-chat-input-container.disabled {
    pointer-events: none;
    opacity: 0.6;
}

.read-only-notice {
    text-align: center;
    padding: 20px;
    color: #ffa500;
}

.read-only-notice i {
    font-size: 24px;
    margin-bottom: 10px;
}

.read-only-notice span {
    display: block;
    font-size: 16px;
    margin-bottom: 5px;
}

.read-only-notice small {
    display: block;
    font-size: 13px;
    opacity: 0.7;
}
```

---

## Migration Script

### File: `scripts/add_device_lock_columns.py`

```python
"""
Add device lock columns to database
Run once to upgrade existing databases
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'data' / 'ai_infrastructure.db'

def migrate():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    print("Starting device lock migration...")
    
    try:
        # Create device_registry table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_registry (
                device_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                device_name TEXT NOT NULL,
                device_fingerprint TEXT,
                last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        print("✅ Created device_registry table")
        
        # Create index
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_device_user 
            ON device_registry(user_id)
        """)
        
        # Add columns to threads table
        try:
            cursor.execute("""
                ALTER TABLE threads 
                ADD COLUMN locked_to_device_id TEXT DEFAULT NULL
            """)
            print("✅ Added locked_to_device_id column")
        except sqlite3.OperationalError:
            print("⏭️  locked_to_device_id column already exists")
        
        try:
            cursor.execute("""
                ALTER TABLE threads 
                ADD COLUMN locked_at TIMESTAMP DEFAULT NULL
            """)
            print("✅ Added locked_at column")
        except sqlite3.OperationalError:
            print("⏭️  locked_at column already exists")
        
        try:
            cursor.execute("""
                ALTER TABLE threads 
                ADD COLUMN lock_mode TEXT DEFAULT 'unlocked'
            """)
            print("✅ Added lock_mode column")
        except sqlite3.OperationalError:
            print("⏭️  lock_mode column already exists")
        
        # Create index on locked_to_device_id
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_thread_locks 
            ON threads(locked_to_device_id)
        """)
        
        # Create thread_lock_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS thread_lock_history (
                lock_id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER NOT NULL,
                device_id TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (thread_id) REFERENCES threads(thread_id),
                FOREIGN KEY (device_id) REFERENCES device_registry(device_id)
            )
        """)
        print("✅ Created thread_lock_history table")
        
        conn.commit()
        print("\n🎉 Migration complete!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
```

---

## Usage Examples

### Scenario 1: Private Work on MacBook

```javascript
// User on MacBook Pro loads thread
const threadId = 12345;

// Lock thread to prevent interference from office PC
await deviceLockManager.lockThread(threadId);
// ✅ Thread now locked - office PC can view but not edit

// Work in private...
// Send multiple messages without interference

// When done, unlock for collaboration
await deviceLockManager.unlockThread(threadId);
// ✅ Thread now available on all devices
```

### Scenario 2: Office PC Sees Locked Thread

```javascript
// User on office PC tries to load same thread
const status = await deviceLockManager.getLockStatus(threadId);

// status = {
//     locked: true,
//     locked_to_device_name: "MacBook Pro",
//     can_edit: false
// }

// UI shows:
// 🔒 Thread locked by MacBook Pro
// [View Read-Only]

// Chat input is disabled, but can read all messages
```

### Scenario 3: Force Unlock from Any Device

```javascript
// User is thread owner, can unlock from any device
await deviceLockManager.unlockThread(threadId);
// ✅ Unlocked even if locked by another device
// (Only works if user_id matches thread owner)
```

---

## Testing Checklist

- [ ] Device registration on first load
- [ ] Lock thread from Device A
- [ ] Device B sees read-only mode
- [ ] Unlock from Device A
- [ ] Device B can now edit
- [ ] Force unlock from Device B (as owner)
- [ ] Lock history tracking
- [ ] Multiple devices list view
- [ ] Lock indicator UI
- [ ] Chat input disable/enable

---

## Benefits Summary

✅ **Solves original problem** - No more conversation collisions  
✅ **User control** - Lock when needed, share when needed  
✅ **Visual feedback** - Clear lock status indicators  
✅ **Read-only mode** - Other devices can view but not interfere  
✅ **Force unlock** - Thread owners can unlock from any device  
✅ **Audit trail** - Track lock/unlock history  
✅ **Device management** - See all devices and their locked threads

---

## Next Steps

1. Run migration: `python scripts/add_device_lock_columns.py`
2. Add routes to Flask app: Register `device_lock_bp`
3. Add frontend code to `business-ai-platform-v2.html`
4. Test with 2 devices (same user account)
5. Deploy to production

**Estimated Implementation Time:** 4-6 hours
