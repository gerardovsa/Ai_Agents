"""
Fix all fetch('/api/...' to use window.API_BASE_URL
"""
import re

# Read the file
with open('UI/business-ai-platform-v2.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to match fetch('/api/... but not fetch(`${...}/api/...
# This will replace fetch('/api/ with fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/api/
pattern = r"fetch\(['\"]/(api/[^'\"]+)['\"]"
replacement = r"fetch(`${window.API_BASE_URL || 'http://localhost:5001'}/\1`"

# Count matches first
matches = re.findall(pattern, content)
print(f"Found {len(matches)} instances to fix:")
for match in set(matches):
    print(f"  /{match}")

# Perform replacement
new_content = re.sub(pattern, replacement, content)

# Write back
with open('UI/business-ai-platform-v2.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\nFixed {len(matches)} fetch calls!")
print("File updated: UI/business-ai-platform-v2.html")
