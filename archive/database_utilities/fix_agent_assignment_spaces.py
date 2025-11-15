"""
Fix Agent Assignment Trailing Spaces in Database

This script removes trailing spaces from agent location keys in users.metadata JSON.
Example: {"agent-2 ": "1762411564661"} -> {"agent-2": "1762411564661"}
"""

import sqlite3
import json
from pathlib import Path

def fix_assignment_spaces():
    """Fix trailing spaces in users.metadata thread_assignments JSON"""
    
    # Get database path (assignments are in sessions.db, not ai_infrastructure.db)
    root_dir = Path(__file__).parent
    db_path = root_dir / 'data' / 'sessions.db'
    
    print(f"Database: {db_path}")
    print("=" * 60)
    
    if not db_path.exists():
        print("ERROR: Database not found!")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get all users with metadata
    cursor.execute("SELECT id, metadata FROM users WHERE metadata IS NOT NULL AND metadata != ''")
    rows = cursor.fetchall()
    
    print(f"Found {len(rows)} users with metadata\n")
    
    fixed_users = 0
    fixed_assignments = 0
    
    for user_id, metadata_json in rows:
        try:
            metadata = json.loads(metadata_json)
            assignments = metadata.get('thread_assignments', {})
            
            if not assignments:
                continue
            
            # Check for keys with trailing spaces
            keys_with_spaces = [key for key in assignments.keys() if key.endswith(' ')]
            
            if keys_with_spaces:
                print(f"\nUser {user_id} - Found {len(keys_with_spaces)} assignments with trailing spaces:")
                
                # Create cleaned assignments
                cleaned_assignments = {}
                for key, value in assignments.items():
                    cleaned_key = key.rstrip()
                    print(f"  '{key}' -> '{cleaned_key}': {value}")
                    cleaned_assignments[cleaned_key] = value
                    if key != cleaned_key:
                        fixed_assignments += 1
                
                # Update metadata
                metadata['thread_assignments'] = cleaned_assignments
                new_metadata_json = json.dumps(metadata)
                
                # Update database
                cursor.execute("UPDATE users SET metadata = ? WHERE id = ?", (new_metadata_json, user_id))
                fixed_users += 1
                
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse metadata for user {user_id}: {e}")
            continue
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"Fixed {fixed_users} users ({fixed_assignments} assignments total)")
    print("=" * 60)
    
    # Verify the fix
    print("\nVerifying fix...")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, metadata FROM users WHERE metadata IS NOT NULL AND metadata != ''")
    rows = cursor.fetchall()
    
    spaces_found = 0
    for user_id, metadata_json in rows:
        try:
            metadata = json.loads(metadata_json)
            assignments = metadata.get('thread_assignments', {})
            keys_with_spaces = [key for key in assignments.keys() if key.endswith(' ')]
            spaces_found += len(keys_with_spaces)
        except:
            pass
    
    if spaces_found == 0:
        print("✅ SUCCESS: No trailing spaces found!")
    else:
        print(f"⚠️  WARNING: Still found {spaces_found} assignments with trailing spaces")
    
    print("\nCurrent assignments by user:")
    for user_id, metadata_json in rows:
        try:
            metadata = json.loads(metadata_json)
            assignments = metadata.get('thread_assignments', {})
            if assignments:
                print(f"  User {user_id}: {assignments}")
        except:
            pass
    
    conn.close()

if __name__ == '__main__':
    fix_assignment_spaces()
