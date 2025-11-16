"""Fix all remaining sqlite3.connect() in user_auth.py"""
import re
from pathlib import Path

file_path = Path('AI_infrastructure/auth/user_auth.py')
content = file_path.read_text(encoding='utf-8')

# Count occurrences
count = len(re.findall(r'with sqlite3\.connect', content))
print(f"Found {count} instances of 'with sqlite3.connect'")

# Replace all: with sqlite3.connect(self.db_path, timeout=30.0) as conn:
# →  with get_connection('ai_infrastructure') as conn:
content = re.sub(
    r'with sqlite3\.connect\(self\.db_path,\s*timeout=[\d.]+\)\s*as\s*conn:',
    "with get_connection('ai_infrastructure') as conn:",
    content
)

# Replace all: with sqlite3.connect(self.db_path) as conn:
content = re.sub(
    r'with sqlite3\.connect\(self\.db_path\)\s*as\s*conn:',
    "with get_connection('ai_infrastructure') as conn:",
    content
)

# Write back
file_path.write_text(content, encoding='utf-8')

# Verify
new_count = len(re.findall(r'with sqlite3\.connect', content))
print(f"Remaining after fix: {new_count}")
print(f"✅ Replaced {count - new_count} instances")
