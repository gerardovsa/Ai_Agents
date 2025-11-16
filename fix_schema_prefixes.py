"""
Fix SQL queries to include schema prefixes for Supabase PostgreSQL

Tables and their schemas:
- ai_infrastructure: users, oauth_tokens, prompt_library, user_preferences, etc.
- sessions: threads, messages, saved_threads, thread_assignments, etc.
- synergy_sessions: synergy_sessions, synergy_internal_docs
"""

import re
import os
from pathlib import Path

# Schema mapping
SCHEMA_MAP = {
    # ai_infrastructure schema
    'users': 'ai_infrastructure.users',
    'oauth_tokens': 'ai_infrastructure.oauth_tokens',
    'prompt_library': 'ai_infrastructure.prompt_library',
    'user_preferences': 'ai_infrastructure.user_preferences',
    'user_sessions': 'ai_infrastructure.user_sessions',
    'user_gmail_accounts': 'ai_infrastructure.user_gmail_accounts',
    'user_platform_credentials': 'ai_infrastructure.user_platform_credentials',
    'workspaces': 'ai_infrastructure.workspaces',
    'workspace_users': 'ai_infrastructure.workspace_users',
    'workspace_invitations': 'ai_infrastructure.workspace_invitations',
    'device_registry': 'ai_infrastructure.device_registry',
    'account_link_requests': 'ai_infrastructure.account_link_requests',
    'user_account_links': 'ai_infrastructure.user_account_links',
    'thread_assignments': 'ai_infrastructure.thread_assignments',
    'user_prompt_preferences': 'ai_infrastructure.user_prompt_preferences',
    'thread_lock_history': 'ai_infrastructure.thread_lock_history',
    
    # sessions schema
    'threads': 'sessions.threads',
    'messages': 'sessions.messages',
    'saved_threads': 'sessions.saved_threads',
    'sessions': 'sessions.sessions',
    'api_sessions': 'sessions.api_sessions',
    'thread_shares': 'sessions.thread_shares',
    'thread_users': 'sessions.thread_users',
    
    # synergy_sessions schema
    'synergy_sessions': 'synergy_sessions.synergy_sessions',
    'synergy_internal_docs': 'synergy_sessions.synergy_internal_docs',
}

def fix_query(content):
    """Add schema prefixes to SQL queries"""
    
    for table_name, full_name in SCHEMA_MAP.items():
        # Skip if already has schema prefix
        if full_name in content:
            continue
            
        # Pattern 1: FROM table_name
        content = re.sub(
            rf'\bFROM\s+{table_name}\b',
            f'FROM {full_name}',
            content,
            flags=re.IGNORECASE
        )
        
        # Pattern 2: JOIN table_name
        content = re.sub(
            rf'\b(LEFT\s+JOIN|RIGHT\s+JOIN|INNER\s+JOIN|JOIN)\s+{table_name}\b',
            rf'\1 {full_name}',
            content,
            flags=re.IGNORECASE
        )
        
        # Pattern 3: INTO table_name
        content = re.sub(
            rf'\bINTO\s+{table_name}\b',
            f'INTO {full_name}',
            content,
            flags=re.IGNORECASE
        )
        
        # Pattern 4: UPDATE table_name
        content = re.sub(
            rf'\bUPDATE\s+{table_name}\b',
            f'UPDATE {full_name}',
            content,
            flags=re.IGNORECASE
        )
        
        # Pattern 5: DELETE FROM table_name
        content = re.sub(
            rf'\b(DELETE\s+FROM)\s+{table_name}\b',
            rf'\1 {full_name}',
            content,
            flags=re.IGNORECASE
        )
    
    return content

def process_file(file_path):
    """Process a single Python file"""
    print(f"\nProcessing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    content = fix_query(content)
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Count changes
        changes = sum(1 for line1, line2 in zip(original.split('\n'), content.split('\n')) if line1 != line2)
        print(f"  ✅ Fixed {changes} lines")
        return True
    else:
        print(f"  ⏭️  No changes needed")
        return False

def main():
    """Fix schema prefixes in all route files"""
    root = Path(__file__).parent
    routes_dir = root / 'AI_infrastructure' / 'routes'
    
    if not routes_dir.exists():
        print(f"❌ Routes directory not found: {routes_dir}")
        return
    
    print(f"🔍 Scanning: {routes_dir}")
    
    files = list(routes_dir.glob('*.py'))
    print(f"Found {len(files)} Python files")
    
    fixed = 0
    for file_path in files:
        if process_file(file_path):
            fixed += 1
    
    print(f"\n✅ COMPLETE: Fixed {fixed}/{len(files)} files")

if __name__ == '__main__':
    main()
