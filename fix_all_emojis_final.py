#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final cleanup: Replace ALL remaining corrupted emoji byte sequences
"""

import shutil
import re

file_path = r"C:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html"
backup_path = r"C:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html.backup2"

print("Creating second backup...")
shutil.copy2(file_path, backup_path)

print("Reading file as bytes...")
with open(file_path, 'rb') as f:
    content = f.read()

print("Finding all corrupted emoji patterns...")

# Pattern: ð followed by various corrupted bytes (Ÿ, ', ", â€, etc.)
# This matches the corrupted UTF-8 double-encoding pattern
corrupted_pattern = rb'\xc3\xb0[\xc2-\xc5][\x80-\xbf][\x80-\xff]{1,8}'

# Find all matches
matches = re.findall(corrupted_pattern, content)
unique_patterns = set(matches)

print(f"Found {len(matches)} total corrupted sequences ({len(unique_patterns)} unique)")

# Common emoji mappings based on byte patterns
known_mappings = {
    # Already handled
    b'\xc3\xb0\xc5\xb8\xe2\x80\x9d': b'\xf0\x9f\x94\xa7',  # Wrench  
    b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc2\xa6': b'\xf0\x9f\x93\xa6',  # Package
    b'\xc3\xb0\xc5\xb8\xe2\x80\x99\xc2\xa5': b'\xf0\x9f\x91\xa5',  # People
    b'\xc3\xb0\xc5\xb8\xe2\x80\x99\xc2\xb0': b'\xf0\x9f\x92\xb0',  # Money
    b'\xc3\xb0\xc5\xb8\xc5\xb8\xc2\xa1': b'\xf0\x9f\x9f\xa1',  # Yellow
    b'\xc3\xb0\xc5\xb8\xc5\xb8\xc2\xa2': b'\xf0\x9f\x9f\xa2',  # Green
    b'\xc3\xb0\xc5\xb8\xe2\x80\x9d\xc2\xb4': b'\xf0\x9f\x94\xb4',  # Red
    b'\xc3\xb0\xc5\xb8\xe2\x80\x9d\xc2\xb5': b'\xf0\x9f\x94\xb5',  # Blue
    
    # New mappings (guessed from context)
    b'\xc3\xb0\xc5\xb8\xc2\x8e\xc2\xa8': b'\xf0\x9f\x8e\xa8',  # Artist palette
    b'\xc3\xb0\xc5\xb8\xc2\x8e\xc2\xaf': b'\xf0\x9f\x8e\xaf',  # Dart/target
    b'\xc3\xb0\xc5\xb8\xe2\x80\x9d\xcb\x86': b'\xf0\x9f\x93\x88',  # Chart
    b'\xc3\xb0\xc5\xb8\xe2\x80\xa0': b'\xf0\x9f\x8f\x86',  # Trophy
    b'\xc3\xb0\xc5\xb8\xe2\x80\x9d\xe2\x80\xa6': b'\xf0\x9f\x93\x85',  # Calendar
    b'\xc3\xb0\xc5\xb8\xc5\x92': b'\xf0\x9f\x8c\x8d',  # Globe
    b'\xc3\xb0\xc5\xb8\x9a\x80': b'\xf0\x9f\x9a\x80',  # Rocket
    b'\xc3\xb0\xc5\xb8\x94\x9e': b'\xf0\x9f\x94\x9e',  # Phone
    b'\xc3\xb0\xc5\xb8\xe2\x80\xba\xc3\xaf\xc2\xb8\xef': b'\xf0\x9f\x9b\x92',  # Cart
    b'\xc3\xb0\xc5\xb8\xe2\x80\xba\xc3\xaf\xc2\xb8': b'\xf0\x9f\x9b\x92',  # Cart
}

# Apply known mappings first
print("\nApplying known emoji mappings...")
count_fixed = 0
for corrupted_bytes, proper_bytes in known_mappings.items():
    occurrences = content.count(corrupted_bytes)
    if occurrences > 0:
        content = content.replace(corrupted_bytes, proper_bytes)
        count_fixed += occurrences
        emoji = proper_bytes.decode('utf-8')
        print(f"  {emoji} - Fixed {occurrences} occurrences")

# For any remaining corrupted patterns, remove them or replace with [ICON]
print("\nRemoving remaining corrupted sequences...")
remaining = re.findall(corrupted_pattern, content)
if remaining:
    print(f"  Found {len(remaining)} remaining corrupted sequences")
    # Replace with empty string (remove them) or a safe placeholder
    content = re.sub(corrupted_pattern, b'', content)  # Remove them
    count_fixed += len(remaining)

print(f"\nWriting fixed content...")
with open(file_path, 'wb') as f:
    f.write(content)

print(f"\n✓ Success! Fixed/removed {count_fixed} corrupted emoji characters.")
print(f"  Backup saved to: {backup_path}")
