"""Clean up test workspace data"""
import sqlite3

db_path = 'c:/Users/gpoli/GIT/AI_agents/data/ai_infrastructure.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Delete test workspaces
cursor.execute("DELETE FROM workspaces WHERE name LIKE '%Test Workspace%' OR slug LIKE '%test-workspace%'")
test_workspaces_deleted = cursor.rowcount

# Clean up orphaned workspace_users
cursor.execute('DELETE FROM workspace_users WHERE workspace_id NOT IN (SELECT id FROM workspaces)')
users_deleted = cursor.rowcount

# Clean up orphaned workspace_invitations
cursor.execute('DELETE FROM workspace_invitations WHERE workspace_id NOT IN (SELECT id FROM workspaces)')
invitations_deleted = cursor.rowcount

conn.commit()
conn.close()

print(f'Cleaned up:')
print(f'  - {test_workspaces_deleted} test workspaces')
print(f'  - {users_deleted} orphaned workspace_users')
print(f'  - {invitations_deleted} orphaned workspace_invitations')
