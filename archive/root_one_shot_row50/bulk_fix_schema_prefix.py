"""
Bulk fix for sessions. schema prefix

This script performs find/replace across all identified files to add sessions. prefix
"""

import re
import os

# Mapping of files to fix - ALL 17 files from scanner output
FIXES = {
    'AI_infrastructure/threads/message_manager.py': [
        ('FROM threads ', 'FROM sessions.threads '),
        ('FROM messages ', 'FROM sessions.messages '),
        ('UPDATE threads ', 'UPDATE sessions.threads '),
        ('UPDATE messages ', 'UPDATE sessions.messages '),
        ('DELETE FROM messages ', 'DELETE FROM sessions.messages '),
        ('SELECT id FROM threads WHERE', 'SELECT id FROM sessions.threads WHERE'),
        ('SELECT * FROM messages WHERE', 'SELECT * FROM sessions.messages WHERE'),
    ],
    'AI_infrastructure/threads/thread_manager.py': [
        ('FROM threads ', 'FROM sessions.threads '),
        ('FROM messages ', 'FROM sessions.messages '),
        ('FROM thread_shares ', 'FROM sessions.thread_shares '),
        ('UPDATE threads ', 'UPDATE sessions.threads '),
        ('DELETE FROM messages ', 'DELETE FROM sessions.messages '),
        ('DELETE FROM thread_shares ', 'DELETE FROM sessions.thread_shares '),
        ('DELETE FROM threads ', 'DELETE FROM sessions.threads '),
        ('SELECT id FROM threads WHERE', 'SELECT id FROM sessions.threads WHERE'),
        ('SELECT * FROM threads WHERE', 'SELECT * FROM sessions.threads WHERE'),
        ('SELECT user_id, visibility FROM threads WHERE', 'SELECT user_id, visibility FROM sessions.threads WHERE'),
        ('SELECT COUNT(*) FROM threads WHERE', 'SELECT COUNT(*) FROM sessions.threads WHERE'),
    ],
    'AI_infrastructure/threads/thread_sharing_manager.py': [
        ('FROM threads ', 'FROM sessions.threads '),
        ('FROM thread_users ', 'FROM sessions.thread_users '),
        ('FROM thread_shares ', 'FROM sessions.thread_shares '),
        ('UPDATE thread_users ', 'UPDATE sessions.thread_users '),
        ('UPDATE thread_shares ', 'UPDATE sessions.thread_shares '),
        ('SELECT * FROM threads WHERE', 'SELECT * FROM sessions.threads WHERE'),
        ('SELECT user_id FROM threads WHERE', 'SELECT user_id FROM sessions.threads WHERE'),
        ('SELECT role FROM thread_users', 'SELECT role FROM sessions.thread_users'),
        ('SELECT id FROM thread_users', 'SELECT id FROM sessions.thread_users'),
        ('SELECT * FROM thread_shares', 'SELECT * FROM sessions.thread_shares'),
        ('JOIN threads t ON', 'JOIN sessions.threads t ON'),
    ],
    'AI_infrastructure/routes/message_operations.py': [
        ('FROM threads ', 'FROM sessions.threads '),
        ('FROM messages ', 'FROM sessions.messages '),
        ('UPDATE threads ', 'UPDATE sessions.threads '),
        ('DELETE FROM messages ', 'DELETE FROM sessions.messages '),
        ('SELECT * FROM threads WHERE', 'SELECT * FROM sessions.threads WHERE'),
        ('SELECT * FROM messages WHERE', 'SELECT * FROM sessions.messages WHERE'),
    ],
    'AI_infrastructure/routes/thread_assignment_routes.py': [
        ('UPDATE threads ', 'UPDATE sessions.threads '),
        ('FROM threads ', 'FROM sessions.threads '),
    ],
    'AI_infrastructure/routes/thread_routes.py': [
        ('FROM threads ', 'FROM sessions.threads '),
        ('FROM messages ', 'FROM sessions.messages '),
        ('FROM saved_threads ', 'FROM sessions.saved_threads '),
        ('UPDATE threads ', 'UPDATE sessions.threads '),
        ('UPDATE saved_threads ', 'UPDATE sessions.saved_threads '),
        ('INSERT INTO threads ', 'INSERT INTO sessions.threads '),
        ('INSERT INTO messages ', 'INSERT INTO sessions.messages '),
        ('INSERT INTO saved_threads ', 'INSERT INTO sessions.saved_threads '),
        ('DELETE FROM threads ', 'DELETE FROM sessions.threads '),
        ('DELETE FROM messages ', 'DELETE FROM sessions.messages '),
        ('JOIN threads t ON', 'JOIN sessions.threads t ON'),
        ('JOIN messages m ON', 'JOIN sessions.messages m ON'),
        ('LEFT JOIN messages m ON', 'LEFT JOIN sessions.messages m ON'),
        ('SELECT id FROM threads', 'SELECT id FROM sessions.threads'),
    ],
    'AI_infrastructure/core/sync_manager.py': [
        ('FROM sessions ', 'FROM sessions.sessions '),
        ('UPDATE sessions ', 'UPDATE sessions.sessions '),
        ('SELECT session_id FROM sessions', 'SELECT session_id FROM sessions.sessions'),
    ],
    'AI_infrastructure/routes/account_linking_routes.py': [
        ('UPDATE sessions.threads SET', 'UPDATE sessions.threads SET'),  # Already has prefix
    ],
    'AI_infrastructure/routes/agent_routes_v4.py': [
        ('SELECT id FROM sessions.threads', 'SELECT id FROM sessions.threads'),  # Already has prefix
        ('FROM sessions.messages', 'FROM sessions.messages'),  # Already has prefix
        ('INSERT INTO sessions.threads', 'INSERT INTO sessions.threads'),  # Already has prefix
        ('INSERT INTO sessions.messages', 'INSERT INTO sessions.messages'),  # Already has prefix
        ('UPDATE sessions.threads', 'UPDATE sessions.threads'),  # Already has prefix
        ('FROM threads ', 'FROM sessions.threads '),  # Line 1100 and 1250 need fix
    ],
    'AI_infrastructure/routes/automation_routes.py': [
        ('UPDATE sessions.threads', 'UPDATE sessions.threads'),  # Already has prefix
    ],
    'AI_infrastructure/routes/device_lock_routes.py': [
        ('FROM sessions.threads WHERE', 'FROM sessions.threads WHERE'),  # Already has prefix
        ('UPDATE sessions.threads', 'UPDATE sessions.threads'),  # Already has prefix
    ],
    'AI_infrastructure/routes/search_routes.py': [
        ('FROM sessions.search_threads', 'FROM sessions.search_threads'),  # Already has prefix
        ('FROM sessions.search_messages', 'FROM sessions.search_messages'),  # Already has prefix
        ('FROM sessions.threads', 'FROM sessions.threads'),  # Already has prefix
        ('FROM sessions.messages m', 'FROM sessions.messages m'),  # Already has prefix
        ('JOIN sessions.threads t ON', 'JOIN sessions.threads t ON'),  # Already has prefix
    ],
    'AI_infrastructure/routes/synergy_routes.py': [
        ('UPDATE sessions.threads', 'UPDATE sessions.threads'),  # Already has prefix
        ('FROM sessions.threads', 'FROM sessions.threads'),  # Already has prefix
    ],
    'AI_infrastructure/routes/token_routes.py': [
        ('FROM sessions.threads', 'FROM sessions.threads'),  # Already has prefix
        ('UPDATE sessions.threads', 'UPDATE sessions.threads'),  # Already has prefix
    ],
    'AI_infrastructure/core/archived/session_database.py': [
        ('FROM sessions ', 'FROM sessions.sessions '),
        ('FROM messages ', 'FROM sessions.messages '),
        ('UPDATE sessions ', 'UPDATE sessions.sessions '),
        ('SELECT * FROM sessions WHERE', 'SELECT * FROM sessions.sessions WHERE'),
        ('SELECT * FROM messages WHERE', 'SELECT * FROM sessions.messages WHERE'),
        ('SELECT COUNT(*) as count FROM messages WHERE', 'SELECT COUNT(*) as count FROM sessions.messages WHERE'),
    ],
}

def apply_fixes():
    """Apply all fixes"""
    total_replacements = 0
    
    for file_path, replacements in FIXES.items():
        full_path = os.path.join('C:/Users/gpoli/GIT/AI_agents', file_path.replace('/', os.sep))
        
        if not os.path.exists(full_path):
            print(f"⚠️  File not found: {file_path}")
            continue
        
        print(f"\n📄 Processing {file_path}...")
        
        # Read file
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        file_replacements = 0
        
        # Apply replacements
        for find_str, replace_str in replacements:
            count = content.count(find_str)
            if count > 0:
                content = content.replace(find_str, replace_str)
                file_replacements += count
                print(f"  ✅ Replaced '{find_str}' → '{replace_str}' ({count} times)")
        
        # Write back if changed
        if content != original_content:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  💾 Saved {file_replacements} replacements")
            total_replacements += file_replacements
        else:
            print(f"  ℹ️  No changes needed")
    
    print(f"\n{'='*80}")
    print(f"✅ COMPLETE: Applied {total_replacements} replacements")
    print(f"{'='*80}")

if __name__ == '__main__':
    print("🔧 Bulk Schema Prefix Fix")
    print("="*80)
    apply_fixes()
