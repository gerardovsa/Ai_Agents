"""
Update agent_routes_v4.py to use centralized database connections
"""

import re
from pathlib import Path

file_path = Path('AI_infrastructure/routes/agent_routes_v4.py')

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern 1: Replace sessions.db connections
pattern1 = r"        # Get thread info from sessions\.db\n        root_dir = Path\(__file__\)\.parent\.parent\.parent\n        sessions_db = root_dir / 'data' / 'sessions\.db'\n        \n        conn = sqlite3\.connect\(str\(sessions_db\)\)\n        conn\.row_factory = sqlite3\.Row\n        cursor = conn\.cursor\(\)"

replacement1 = "        # Get thread info from sessions.db\n        conn = get_database_connection('sessions')\n        cursor = conn.cursor()"

content = re.sub(pattern1, replacement1, content)

# Pattern 2: Replace synergy_sessions.db connections
pattern2 = r"            # Fetch Synergy project details\n            synergy_db = root_dir / 'data' / 'synergy_sessions\.db'\n            conn = sqlite3\.connect\(str\(synergy_db\)\)\n            conn\.row_factory = sqlite3\.Row\n            cursor = conn\.cursor\(\)"

replacement2 = "            # Fetch Synergy project details\n            conn = get_database_connection('synergy_sessions')\n            cursor = conn.cursor()"

content = re.sub(pattern2, replacement2, content)

# Pattern 3: Remove "import sqlite3" if standalone
content = re.sub(r'\n        import sqlite3\n', '\n', content)

# Remove extra Path imports
content = re.sub(r'(\s+)from pathlib import Path\n(\s+)\n(\s+)# Get thread info', r'\1# Get thread info', content)

# Save the file
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Updated agent_routes_v4.py")
print("   - Replaced sessions.db connections with get_database_connection('sessions')")
print("   - Replaced synergy_sessions.db connections with get_database_connection('synergy_sessions')")
print("   - Cleaned up redundant imports")
