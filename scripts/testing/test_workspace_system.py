"""
Test Workspace System - Comprehensive integration tests
from shared.database_utils import convert_sql_placeholders

Tests workspace creation, members, invitations, permissions, and slugs.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from AI_infrastructure.workspace import (
    WorkspaceManager,
    AccessControl,
    InvitationManager,
    SlugGenerator,
    WorkspaceRole,
    WorkspaceStatus,
    WorkspaceVisibility,
    InvitationStatus,
    Permission
)

from AI_infrastructure.workspace.models import (
    WorkspaceCreate,
    WorkspaceMemberCreate,
    WorkspaceInvitationCreate
)


def test_imports():
    """Test 1: Verify all imports work"""
    print("\n[TEST 1] Testing imports...")
    try:
        assert WorkspaceManager is not None
        assert AccessControl is not None
        assert InvitationManager is not None
        assert SlugGenerator is not None
        print("  PASS - All managers imported successfully")
        return True
    except Exception as e:
        print(f"  FAIL - Import error: {e}")
        return False


def test_database_schema():
    """Test 2: Verify database tables exist"""
    print("\n[TEST 2] Testing database schema...")
    import sqlite3
    
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check workspaces table has slug column
        cursor.execute("PRAGMA table_info(workspaces)")
        columns = [row[1] for row in cursor.fetchall()]
        assert 'slug' in columns, "workspaces table missing slug column"
        
        # Check workspace_users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workspace_users'")
        assert cursor.fetchone() is not None, "workspace_users table missing"
        
        # Check workspace_invitations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workspace_invitations'")
        assert cursor.fetchone() is not None, "workspace_invitations table missing"
        
        conn.close()
        print("  PASS - Database schema is correct")
        print("    - workspaces.slug: EXISTS")
        print("    - workspace_users table: EXISTS")
        print("    - workspace_invitations table: EXISTS")
        return True
    except Exception as e:
        print(f"  FAIL - Database schema error: {e}")
        return False


def test_slug_generation():
    """Test 3: Test slug generation"""
    print("\n[TEST 3] Testing slug generation...")
    try:
        slug_gen = SlugGenerator()
        
        # Test workspace slug
        slug1 = slug_gen._slugify("My Test Workspace")
        assert slug1 == "my-test-workspace", f"Expected 'my-test-workspace', got '{slug1}'"
        
        # Test special characters
        slug2 = slug_gen._slugify("AI & ML Research 2024!")
        assert slug2 == "ai-ml-research-2024", f"Expected 'ai-ml-research-2024', got '{slug2}'"
        
        # Test validation
        assert slug_gen.validate_slug("valid-slug-123") == True
        assert slug_gen.validate_slug("Invalid Slug") == False
        assert slug_gen.validate_slug("admin") == False  # Reserved word
        
        print("  PASS - Slug generation working")
        print(f"    - 'My Test Workspace' -> '{slug1}'")
        print(f"    - 'AI & ML Research 2024!' -> '{slug2}'")
        print(f"    - Validation working (reserved words blocked)")
        return True
    except Exception as e:
        print(f"  FAIL - Slug generation error: {e}")
        return False


def get_test_user_id():
    """Get an existing user ID for testing"""
    import sqlite3
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE is_active = 1 LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def test_workspace_creation():
    """Test 4: Create a workspace"""
    print("\n[TEST 4] Testing workspace creation...")
    try:
        # Get existing user
        user_id = get_test_user_id()
        if not user_id:
            print("  SKIP - No active users in database")
            return None
        
        workspace_mgr = WorkspaceManager()
        
        # Create workspace
        workspace_data = WorkspaceCreate(
            name="Test Workspace Alpha",
            description="Testing workspace system",
            owner_id=user_id,
            visibility=WorkspaceVisibility.PRIVATE
        )
        
        workspace = workspace_mgr.create_workspace(workspace_data)
        
        assert workspace.id is not None, "Workspace ID is None"
        assert workspace.slug == "test-workspace-alpha", f"Expected slug 'test-workspace-alpha', got '{workspace.slug}'"
        assert workspace.name == "Test Workspace Alpha"
        assert workspace.owner_id == user_id
        assert workspace.status == WorkspaceStatus.ACTIVE
        
        print("  PASS - Workspace created successfully")
        print(f"    - ID: {workspace.id}")
        print(f"    - Slug: {workspace.slug}")
        print(f"    - Name: {workspace.name}")
        print(f"    - Owner: {workspace.owner_id}")
        
        return (workspace.id, user_id)
    except Exception as e:
        print(f"  FAIL - Workspace creation error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_permission_system(workspace_id, owner_id):
    """Test 5: Test permission system"""
    print("\n[TEST 5] Testing permission system...")
    try:
        access_ctrl = AccessControl()
        
        # Owner should have all permissions
        assert access_ctrl.is_workspace_owner(workspace_id, owner_id) == True
        assert access_ctrl.can_edit_workspace(workspace_id, owner_id) == True
        assert access_ctrl.check_permission(workspace_id, owner_id, Permission.DELETE_WORKSPACE) == True
        
        # Non-member should have no permissions
        assert access_ctrl.can_access_workspace(workspace_id, 999) == False
        
        print("  PASS - Permission system working")
        print("    - Owner has full permissions: VERIFIED")
        print("    - Non-members blocked: VERIFIED")
        return True
    except Exception as e:
        print(f"  FAIL - Permission system error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_member_management(workspace_id, owner_id):
    """Test 6: Add and manage members"""
    print("\n[TEST 6] Testing member management...")
    try:
        workspace_mgr = WorkspaceManager()
        access_ctrl = AccessControl()
        
        # Get another user ID for testing (not the owner)
        import sqlite3
        root_dir = Path(__file__).parent.parent.parent
        db_path = root_dir / 'data' / 'ai_infrastructure.db'
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        sql, params = convert_sql_placeholders("SELECT id FROM users WHERE id != ? AND is_active = 1 LIMIT 1", (owner_id,))

        cursor.execute(sql, params)
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            print("  SKIP - Need at least 2 users for member testing")
            return True
        
        member_user_id = row[0]
        
        # Add member
        member_data = WorkspaceMemberCreate(
            workspace_id=workspace_id,
            user_id=member_user_id,
            role=WorkspaceRole.MEMBER
        )
        
        member = workspace_mgr.add_member(member_data, added_by_user_id=owner_id)
        
        assert member.user_id == member_user_id
        assert member.role == WorkspaceRole.MEMBER
        
        # Check member permissions
        assert access_ctrl.can_access_workspace(workspace_id, member_user_id) == True
        assert access_ctrl.can_create_threads(workspace_id, member_user_id) == True
        assert access_ctrl.can_edit_workspace(workspace_id, member_user_id) == False  # Members can't edit
        
        # Get members list
        members = workspace_mgr.get_members(workspace_id)
        assert len(members) >= 2  # Owner + new member
        
        print("  PASS - Member management working")
        print(f"    - Added user {member.user_id} as {member.role.value}")
        print(f"    - Member has correct permissions")
        print(f"    - Total members: {len(members)}")
        return True
    except Exception as e:
        print(f"  FAIL - Member management error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_invitation_system(workspace_id, owner_id):
    """Test 7: Test invitation system"""
    print("\n[TEST 7] Testing invitation system...")
    try:
        invite_mgr = InvitationManager()
        
        # Create invitation
        invite_data = WorkspaceInvitationCreate(
            workspace_id=workspace_id,
            invited_email="newuser@example.com",
            role=WorkspaceRole.MEMBER
        )
        
        invitation = invite_mgr.create_invitation(invite_data, invited_by_user_id=owner_id)
        
        assert invitation.id is not None
        assert invitation.token is not None
        assert len(invitation.token) > 20  # Secure token
        assert invitation.status == InvitationStatus.PENDING
        assert invitation.invited_email == "newuser@example.com"
        
        # List invitations
        invitations = invite_mgr.list_workspace_invitations(workspace_id)
        assert len(invitations) >= 1
        
        print("  PASS - Invitation system working")
        print(f"    - Invitation ID: {invitation.id}")
        print(f"    - Token length: {len(invitation.token)} chars")
        print(f"    - Status: {invitation.status.value}")
        print(f"    - Email: {invitation.invited_email}")
        return True
    except Exception as e:
        print(f"  FAIL - Invitation system error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workspace_retrieval(workspace_id):
    """Test 8: Retrieve workspace by ID and slug"""
    print("\n[TEST 8] Testing workspace retrieval...")
    try:
        workspace_mgr = WorkspaceManager()
        
        # Get by ID
        workspace = workspace_mgr.get_workspace(workspace_id=workspace_id)
        assert workspace.id == workspace_id
        
        # Get by slug
        workspace2 = workspace_mgr.get_workspace(slug="test-workspace-alpha")
        assert workspace2.id == workspace_id
        assert workspace2.slug == "test-workspace-alpha"
        
        print("  PASS - Workspace retrieval working")
        print(f"    - Retrieved by ID: {workspace.id}")
        print(f"    - Retrieved by slug: {workspace2.slug}")
        return True
    except Exception as e:
        print(f"  FAIL - Workspace retrieval error: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_test_data(workspace_id, owner_id):
    """Cleanup: Remove test workspace"""
    print("\n[CLEANUP] Removing test data...")
    try:
        workspace_mgr = WorkspaceManager()
        
        # Delete workspace (soft delete)
        workspace_mgr.delete_workspace(workspace_id, owner_id, hard_delete=False)
        
        print("  - Test workspace archived")
        return True
    except Exception as e:
        print(f"  - Cleanup error (non-critical): {e}")
        return False


def main():
    """Run all tests"""
    print("="*70)
    print("WORKSPACE SYSTEM COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    results = []
    workspace_id = None
    owner_id = None
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Database Schema", test_database_schema()))
    results.append(("Slug Generation", test_slug_generation()))
    
    workspace_result = test_workspace_creation()
    results.append(("Workspace Creation", workspace_result is not None))
    
    if workspace_result:
        workspace_id, owner_id = workspace_result
        results.append(("Permission System", test_permission_system(workspace_id, owner_id)))
        results.append(("Member Management", test_member_management(workspace_id, owner_id)))
        results.append(("Invitation System", test_invitation_system(workspace_id, owner_id)))
        results.append(("Workspace Retrieval", test_workspace_retrieval(workspace_id)))
        
        # Cleanup
        cleanup_test_data(workspace_id, owner_id)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "  " if result else "  "
        print(f"{symbol} {test_name}: {status}")
    
    print(f"\nResults: {passed}/{total} tests passed ({passed*100//total}%)")
    
    if passed == total:
        print("\n  SUCCESS - All tests passed!")
    else:
        print(f"\n  WARNING - {total - passed} test(s) failed")
    
    print("="*70)
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
