"""
Automated fix for critical database compatibility issues
Fixes SQLite placeholders (?) to PostgreSQL (%s)
"""
import os
import re
from pathlib import Path

# Files with critical issues from audit
CRITICAL_FIXES = {
    'AI_infrastructure/thread_manager.py': [
        {
            'line': 261,
            'old': 'WHERE w.slug = ? AND t.thread_slug = %s',
            'new': 'WHERE w.slug = %s AND t.thread_slug = %s'
        }
    ],
    'AI_infrastructure/auth/credential_injector.py': [
        {
            'search': 'last_error = ?,',
            'replace': 'last_error = %s,'
        }
    ],
    'AI_infrastructure/auth/user_auth.py': [
        {
            'search': 'WHERE username = %s OR email = ?',
            'replace': 'WHERE username = %s OR email = %s'
        }
    ],
    'AI_infrastructure/database_toolkit/session_manager.py': [
        {
            'search': 'WHERE expires_at <= ?',
            'replace': 'WHERE expires_at <= %s'
        }
    ],
    'AI_infrastructure/routes/account_linking_routes.py': [
        {
            'search': 'WHERE ual.primary_user_id = ?',
            'replace': 'WHERE ual.primary_user_id = %s'
        },
        {
            'search': 'WHERE (primary_user_id = ? AND linked_user_id = %s)',
            'replace': 'WHERE (primary_user_id = %s AND linked_user_id = %s)'
        },
        {
            'search': 'OR (primary_user_id = ? AND linked_user_id = %s)',
            'replace': 'OR (primary_user_id = %s AND linked_user_id = %s)'
        }
    ],
    'AI_infrastructure/routes/auth_routes.py': [
        {
            'search': 'AND (is_active = ? OR is_active IS NULL)',
            'replace': 'AND (is_active = %s OR is_active IS NULL)'
        }
    ],
    'AI_infrastructure/routes/google_auth_routes_V2_FIXED.py': [
        {
            'search': 'last_error = ?,',
            'replace': 'last_error = %s,'
        }
    ],
    'AI_infrastructure/routes/kanban_analytics_routes.py': [
        {
            'search': 'WHERE jt.ticket_id = ?',
            'replace': 'WHERE jt.ticket_id = %s'
        },
        {
            'search': 'WHERE jts.ticket_id = ?',
            'replace': 'WHERE jts.ticket_id = %s'
        },
        {
            'search': 'WHERE st.ticket_id = ?',
            'replace': 'WHERE st.ticket_id = %s'
        }
    ],
    'AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py': [
        {
            'search': 'last_refresh_error = ?,',
            'replace': 'last_refresh_error = %s,'
        },
        {
            'search': 'last_error = ?,',
            'replace': 'last_error = %s,'
        }
    ],
    'AI_infrastructure/routes/thread_routes.py': [
        {
            'search': 'WHERE t.user_id = ?',
            'replace': 'WHERE t.user_id = %s'
        }
    ],
    'AI_infrastructure/routes/user_management_routes.py': [
        {
            'search': 'SELECT id FROM ai_infrastructure.users WHERE username = %s OR email = ?',
            'replace': 'SELECT id FROM ai_infrastructure.users WHERE username = %s OR email = %s'
        }
    ],
    'AI_infrastructure/sync/kanban_db_sync.py': [
        {
            'search': 'AND order_date >= ?',
            'replace': 'AND order_date >= %s'
        }
    ],
    'AI_infrastructure/threads/thread_sharing_manager.py': [
        {
            'search': 'WHERE tu.thread_id = ? AND tu.removed_at IS NULL',
            'replace': 'WHERE tu.thread_id = %s AND tu.removed_at IS NULL'
        },
        {
            'search': 'WHERE tu.user_id = ? AND tu.removed_at IS NULL AND t.user_id != ?',
            'replace': 'WHERE tu.user_id = %s AND tu.removed_at IS NULL AND t.user_id != %s'
        }
    ],
    'AI_infrastructure/workspace/access_control.py': [
        {
            'search': 'WHERE w.owner_id = ?',
            'replace': 'WHERE w.owner_id = %s'
        }
    ],
    'AI_infrastructure/workspace/slug_generator.py': [
        {
            'search': 'WHERE slug = ?',
            'replace': 'WHERE slug = %s'
        }
    ],
    'AI_infrastructure/threads/thread_manager.py': [
        {
            'search': 'where_clauses.append("workspace_id = ?")',
            'replace': 'where_clauses.append("workspace_id = %s")'
        },
        {
            'search': 'where_clauses.append("user_id = ?")',
            'replace': 'where_clauses.append("user_id = %s")'
        },
        {
            'search': 'where_clauses.append("status = ?")',
            'replace': 'where_clauses.append("status = %s")'
        },
        {
            'search': 'where_clauses.append("visibility = ?")',
            'replace': 'where_clauses.append("visibility = %s")'
        }
    ],
    'AI_infrastructure/threads/message_manager.py': [
        {
            'search': 'where_clauses = ["thread_id = ?"]',
            'replace': 'where_clauses = ["thread_id = %s"]'
        },
        {
            'search': 'where_clauses.append("role = ?")',
            'replace': 'where_clauses.append("role = %s")'
        }
    ]
}

def fix_file(filepath, fixes):
    """Apply fixes to a file"""
    full_path = Path(__file__).parent / filepath
    
    if not full_path.exists():
        print(f"⚠️  File not found: {filepath}")
        return False
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes_applied = 0
        
        for fix in fixes:
            search = fix.get('search')
            replace = fix.get('replace')
            
            if search and replace:
                if search in content:
                    content = content.replace(search, replace)
                    fixes_applied += 1
                    print(f"   ✅ Fixed: {search[:60]}...")
                else:
                    print(f"   ⚠️  Not found: {search[:60]}...")
        
        if content != original_content:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {filepath} - {fixes_applied} fixes applied")
            return True
        else:
            print(f"⚠️  {filepath} - No changes made")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    print("=" * 100)
    print("AUTOMATED FIX - CRITICAL DATABASE COMPATIBILITY ISSUES")
    print("=" * 100)
    print("\nFixing SQLite placeholders (?) → PostgreSQL placeholders (%s)")
    print(f"Files to fix: {len(CRITICAL_FIXES)}\n")
    
    fixed_count = 0
    failed_count = 0
    
    for filepath, fixes in CRITICAL_FIXES.items():
        print(f"\n📄 {filepath}")
        if fix_file(filepath, fixes):
            fixed_count += 1
        else:
            failed_count += 1
    
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"✅ Files fixed: {fixed_count}")
    print(f"⚠️  Files failed/skipped: {failed_count}")
    print(f"📝 Total files: {len(CRITICAL_FIXES)}")
    
    if fixed_count > 0:
        print("\n🎉 SUCCESS! Critical database issues have been fixed.")
        print("   Next steps:")
        print("   1. Test the application: BISTART")
        print("   2. Run audit again: python audit_database_queries.py")
        print("   3. Fix remaining HIGH priority issues")
    
    print("\n" + "=" * 100)

if __name__ == "__main__":
    main()
