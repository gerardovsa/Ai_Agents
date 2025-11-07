"""
Fix all getElementById with spaces in template literals
"""
import re

# Read the file
with open('UI/business-ai-platform-v2.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to match getElementById with spaces in IDs
# Match: getElementById(`something - with - spaces `)
pattern = r"getElementById\(`([^`]+) - ([^`]+)`\)"

def fix_id(match):
    """Remove spaces from ID selector"""
    full_id = match.group(0)
    id_content = full_id[len("getElementById(`"):-2]  # Extract content between backticks
    # Remove all spaces around hyphens and trailing spaces
    fixed_id = id_content.replace(' - ', '-').replace(' `', '`').strip()
    return f"getElementById(`{fixed_id}`)"

# Count matches
matches = re.findall(pattern, content)
print(f"Found {len(matches)} getElementById with spaces:")
for match in matches[:10]:  # Show first 10
    print(f"  {match[0]} - {match[1]}")

# Perform replacement
new_content = re.sub(r"getElementById\(`([^`]+)`\)", lambda m: fix_id(m), content)

# Write back
with open('UI/business-ai-platform-v2.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\nFixed getElementById spacing issues!")
print("File updated: UI/business-ai-platform-v2.html")
