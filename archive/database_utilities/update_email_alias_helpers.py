"""
Update email_alias_helpers.py to use get_database_connection()
Replaces all 6 sqlite3.connect(DB_PATH) calls
"""

import re
from pathlib import Path

file_path = Path(__file__).parent / 'AI_infrastructure' / 'utils' / 'email_alias_helpers.py'

print(f"Updating: {file_path}")

# Read file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
old_import = """import sqlite3
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import json
from pathlib import Path

# Use centralized database path helper (Render-aware)
from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path
DB_PATH = get_ai_infrastructure_db_path()"""

new_import = """import sqlite3
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Use centralized database connection utility (SQLite + Supabase support)
from shared.database_utils import get_database_connection"""

content = content.replace(old_import, new_import)

# 2. Replace all sqlite3.connect(DB_PATH) with get_database_connection('ai_infrastructure')
pattern = r'conn = sqlite3\.connect\(DB_PATH\)'
replacement = "conn = get_database_connection('ai_infrastructure')"

matches = re.findall(pattern, content)
print(f"Found {len(matches)} occurrences of sqlite3.connect(DB_PATH)")

content = re.sub(pattern, replacement, content)

# 3. Write updated content
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Updated {file_path.name}")
print(f"   Replaced {len(matches)} database connection calls")
