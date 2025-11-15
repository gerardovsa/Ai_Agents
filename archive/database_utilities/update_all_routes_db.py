"""
Batch update all route files to use centralized database connections
"""

import re
from pathlib import Path

# Files to update with their database mappings
files_to_update = {
    'AI_infrastructure/routes/auth_routes.py': 'ai_infrastructure',
    'AI_infrastructure/routes/oauth_routes.py': 'ai_infrastructure',
    'AI_infrastructure/routes/user_management_routes.py': 'ai_infrastructure',
    'AI_infrastructure/routes/user_preferences_routes.py': 'ai_infrastructure',
    'AI_infrastructure/routes/token_routes.py': 'ai_infrastructure',
    'AI_infrastructure/routes/prompt_library_routes.py': 'ai_infrastructure',
    'AI_infrastructure/routes/thread_routes.py': 'sessions',
    'AI_infrastructure/routes/thread_assignment_routes.py': 'ai_infrastructure',
    'AI_infrastructure/routes/kanban_routes.py': 'kanban_analytics',
    'AI_infrastructure/routes/production_log_routes.py': 'kanban_analytics',
    'AI_infrastructure/routes/synergy_routes.py': 'synergy_sessions',
}

def update_file(file_path: Path, db_name: str):
    """Update a single route file to use get_database_connection"""
    
    if not file_path.exists():
        print(f"⚠️  Skipping {file_path} - file not found")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = 0
    
    # Check if already imported
    if 'from shared.database_utils import get_database_connection' not in content and 'get_database_connection' not in content:
        # Find a good place to add the import (after other imports)
        import_pattern = r'(import .*\nfrom .*\n)'
        if re.search(import_pattern, content):
            content = re.sub(
                r'(from pathlib import Path)',
                r'\1\nfrom shared.database_utils import get_database_connection',
                content,
                count=1
            )
            changes_made += 1
    
    # Pattern 1: Direct path construction + sqlite3.connect
    patterns = [
        # Pattern: db_path = ... / 'data' / '...db'; conn = sqlite3.connect(str(db_path))
        (r"db_path = .*? / 'data' / '[^']+\.db'\s*\n\s*conn = sqlite3\.connect\(str\(db_path\)\)",
         f"conn = get_database_connection('{db_name}')"),
        
        # Pattern: DB_PATH = ...; conn = sqlite3.connect(str(DB_PATH))
        (r"conn = sqlite3\.connect\(str\(db_path\)\)",
         f"conn = get_database_connection('{db_name}')"),
         
        # Pattern: sqlite3.connect(DB_PATH) where DB_PATH is uppercase constant
        (r"conn = sqlite3\.connect\(DB_PATH\)",
         f"conn = get_database_connection('{db_name}')"),
    ]
    
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            changes_made += 1
    
    # Only write if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated {file_path.name} ({changes_made} changes)")
        return True
    else:
        print(f"⏭️  Skipped {file_path.name} (no changes needed)")
        return False

# Process all files
print("🔄 Updating route files to use centralized database connections...\n")
updated_count = 0

for file_rel_path, db_name in files_to_update.items():
    file_path = Path(file_rel_path)
    if update_file(file_path, db_name):
        updated_count += 1

print(f"\n✅ Updated {updated_count} files successfully")
print("⚠️  Note: Some files may need manual review for complex connection patterns")
