"""
Cleanup Test Data - Remove test workspaces and related records
from shared.database_utils import convert_sql_placeholders

Removes test workspaces that conflict with test suite expectations.
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def cleanup_test_data():
    """Remove test workspaces and related data"""
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    
    print(f"Database: {db_path}")
    print("\n" + "="*60)
    print("CLEANING TEST DATA")
    print("="*60)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get test workspaces
    cursor.execute("""
        SELECT id, slug, name FROM workspaces 
        WHERE slug LIKE 'test-workspace-%' OR slug LIKE 'my-%'
    """)
    test_workspaces = cursor.fetchall()
    
    if test_workspaces:
        print(f"\nFound {len(test_workspaces)} test workspace(s):")
        for ws_id, slug, name in test_workspaces:
            print(f"  - ID:{ws_id}, slug:{slug}, name:{name}")
        
        # Delete related data
        workspace_ids = [ws[0] for ws in test_workspaces]
        placeholders = ','.join('?' * len(workspace_ids))
        
        # Delete workspace_invitations
        cursor.execute(f"""
            DELETE FROM workspace_invitations 
            WHERE workspace_id IN ({placeholders})
        """, workspace_ids)
        deleted_invitations = cursor.rowcount
        
        # Delete workspace_users
        cursor.execute(f"""
            DELETE FROM workspace_users 
            WHERE workspace_id IN ({placeholders})
        """, workspace_ids)
        deleted_members = cursor.rowcount
        
        # Delete workspaces
        cursor.execute(f"""
            DELETE FROM workspaces 
            WHERE id IN ({placeholders})
        """, workspace_ids)
        deleted_workspaces = cursor.rowcount
        
        conn.commit()
        
        print(f"\nDeleted:")
        print(f"  - {deleted_workspaces} workspace(s)")
        print(f"  - {deleted_members} workspace member(s)")
        print(f"  - {deleted_invitations} invitation(s)")
    else:
        print("\nNo test workspaces found")
    
    # Check for orphaned workspace_users
    cursor.execute("""
        SELECT COUNT(*) FROM workspace_users wu
        WHERE NOT EXISTS (
            SELECT 1 FROM workspaces w WHERE w.id = wu.workspace_id
        )
    """)
    orphaned_members = cursor.fetchone()[0]
    
    if orphaned_members > 0:
        cursor.execute("""
            DELETE FROM workspace_users
            WHERE NOT EXISTS (
                SELECT 1 FROM workspaces w WHERE w.id = workspace_users.workspace_id
            )
        """)
        conn.commit()
        print(f"\nDeleted {orphaned_members} orphaned workspace member(s)")
    
    # Check for orphaned invitations
    cursor.execute("""
        SELECT COUNT(*) FROM workspace_invitations wi
        WHERE NOT EXISTS (
            SELECT 1 FROM workspaces w WHERE w.id = wi.workspace_id
        )
    """)
    orphaned_invitations = cursor.fetchone()[0]
    
    if orphaned_invitations > 0:
        cursor.execute("""
            DELETE FROM workspace_invitations
            WHERE NOT EXISTS (
                SELECT 1 FROM workspaces w WHERE w.id = workspace_invitations.workspace_id
            )
        """)
        conn.commit()
        print(f"Deleted {orphaned_invitations} orphaned invitation(s)")
    
    conn.close()
    
    print("\n" + "="*60)
    print("CLEANUP COMPLETE")
    print("="*60)


if __name__ == '__main__':
    cleanup_test_data()
