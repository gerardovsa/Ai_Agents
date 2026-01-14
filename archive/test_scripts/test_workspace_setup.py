"""
Test Workspace Setup - Verify module and database ready

Tests:
1. Import workspace module
2. Verify database tables exist
3. Test slug generation
4. Test access control
5. Create test workspace
"""

import sys
import sqlite3
from pathlib import Path

print("="*60)
print("WORKSPACE SETUP VERIFICATION")
print("="*60)

# Test 1: Import workspace module
print("\n[1/5] Testing workspace module imports...")
try:
    from AI_infrastructure.workspace import (
        WorkspaceManager,
        AccessControl,
        InvitationManager,
        SlugGenerator,
        WorkspaceRole,
        WorkspaceStatus,
        WorkspaceVisibility,
        Permission
    )
    print("  OK - All imports successful")
except Exception as e:
    print(f"  FAIL - Import error: {e}")
    sys.exit(1)

# Test 2: Verify database tables
print("\n[2/5] Testing database schema...")
try:
    db_path = Path('data/ai_infrastructure.db')
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check workspaces table has slug
    cursor.execute("PRAGMA table_info(workspaces)")
    workspace_cols = [row[1] for row in cursor.fetchall()]
    assert 'slug' in workspace_cols, "workspaces.slug column missing"
    print("  OK - workspaces table has slug column")
    
    # Check workspace_users table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workspace_users'")
    assert cursor.fetchone() is not None, "workspace_users table missing"
    print("  OK - workspace_users table exists")
    
    # Check workspace_invitations table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workspace_invitations'")
    assert cursor.fetchone() is not None, "workspace_invitations table missing"
    print("  OK - workspace_invitations table exists")
    
    conn.close()
except Exception as e:
    print(f"  FAIL - Database error: {e}")
    sys.exit(1)

# Test 3: Test slug generation
print("\n[3/5] Testing slug generator...")
try:
    slug_gen = SlugGenerator()
    
    # Test slugify
    test_slug = slug_gen._slugify("My Test Workspace!")
    assert test_slug == "my-test-workspace", f"Expected 'my-test-workspace', got '{test_slug}'"
    print(f"  OK - Slugify: 'My Test Workspace!' -> '{test_slug}'")
    
    # Test validation
    assert slug_gen.validate_slug("valid-slug-123") == True
    assert slug_gen.validate_slug("Invalid Slug") == False
    assert slug_gen.validate_slug("admin") == False  # Reserved
    print("  OK - Slug validation working")
    
except Exception as e:
    print(f"  FAIL - Slug generator error: {e}")
    sys.exit(1)

# Test 4: Test access control
print("\n[4/5] Testing access control...")
try:
    access_ctrl = AccessControl()
    
    # Test permission matrix
    owner_perms = access_ctrl.ROLE_PERMISSIONS[WorkspaceRole.OWNER]
    assert Permission.DELETE_WORKSPACE in owner_perms
    print(f"  OK - OWNER has {len(owner_perms)} permissions")
    
    admin_perms = access_ctrl.ROLE_PERMISSIONS[WorkspaceRole.ADMIN]
    assert Permission.DELETE_WORKSPACE not in admin_perms
    assert Permission.ADD_MEMBERS in admin_perms
    print(f"  OK - ADMIN has {len(admin_perms)} permissions")
    
    member_perms = access_ctrl.ROLE_PERMISSIONS[WorkspaceRole.MEMBER]
    assert Permission.CREATE_THREADS in member_perms
    assert Permission.ADD_MEMBERS not in member_perms
    print(f"  OK - MEMBER has {len(member_perms)} permissions")
    
    guest_perms = access_ctrl.ROLE_PERMISSIONS[WorkspaceRole.GUEST]
    assert Permission.VIEW_WORKSPACE in guest_perms
    assert Permission.CREATE_THREADS not in guest_perms
    print(f"  OK - GUEST has {len(guest_perms)} permissions")
    
except Exception as e:
    print(f"  FAIL - Access control error: {e}")
    sys.exit(1)

# Test 5: Create test workspace
print("\n[5/5] Testing workspace creation...")
try:
    from AI_infrastructure.workspace.models import WorkspaceCreate
    
    workspace_mgr = WorkspaceManager()
    
    # Check if test workspace already exists
    conn = sqlite3.connect('data/ai_infrastructure.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM workspaces WHERE slug = 'test-workspace-setup'")
    existing = cursor.fetchone()
    
    if existing:
        print(f"  OK - Test workspace already exists (id={existing[0]})")
        workspace_id = existing[0]
    else:
        # Create test workspace
        workspace_data = WorkspaceCreate(
            name="Test Workspace Setup",
            description="Automated test workspace",
            owner_id=1,
            visibility=WorkspaceVisibility.PRIVATE
        )
        
        workspace = workspace_mgr.create_workspace(workspace_data)
        workspace_id = workspace.id
        print(f"  OK - Created test workspace (id={workspace.id}, slug={workspace.slug})")
    
    # Verify workspace can be retrieved
    workspace = workspace_mgr.get_workspace(workspace_id=workspace_id)
    assert workspace.id == workspace_id
    print(f"  OK - Retrieved workspace: {workspace.name}")
    
    # Check workspace owner is member
    is_member = workspace_mgr.check_membership(workspace_id, user_id=1)
    assert is_member == True
    print("  OK - Owner is automatically a member")
    
    conn.close()
    
except Exception as e:
    print(f"  FAIL - Workspace creation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Success!
print("\n" + "="*60)
print("SUCCESS - All tests passed!")
print("="*60)
print("\nWorkspace System Status:")
print("  - Module imports: WORKING")
print("  - Database schema: READY")
print("  - Slug generation: WORKING")
print("  - Access control: WORKING")
print("  - Workspace CRUD: WORKING")
print("\nReady for API route development!")
