#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix emoji encoding issues using byte patterns
"""

import shutil

file_path = r"C:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html"
backup_path = r"C:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html.backup"

print("Backing up original file...")
shutil.copy2(file_path, backup_path)

print("Reading file as bytes...")
with open(file_path, 'rb') as f:
    content = f.read()

print("Replacing corrupted emoji byte sequences...")

# Map corrupted byte sequences to proper UTF-8 emoji bytes
# Using byte literals to avoid encoding issues
replacements = {
    b'\xc3\xb0\xc5\xb8\xe2\x80\x9d': b'\xf0\x9f\x94\xa7',  # Wrench
    b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc2\xa6': b'\xf0\x9f\x93\xa6',  # Package
    b'\xc3\xb0\xc5\xb8\xe2\x80\xba\xc3\xaf\xc2\xb8\xef': b'\xf0\x9f\x9b\x92',  # Shopping cart (with extra bytes)
    b'\xc3\xb0\xc5\xb8\xe2\x80\xba\xc3\xaf\xc2\xb8': b'\xf0\x9f\x9b\x92',  # Shopping cart
    b'\xc3\xb0\xc5\xb8\xe2\x80\x99\xc2\xa5': b'\xf0\x9f\x91\xa5',  # People
    b'\xc3\xb0\xc5\xb8\xe2\x80\x99\xc2\xb0': b'\xf0\x9f\x92\xb0',  # Money bag
    b'\xc3\xb0\xc5\xb8\xc5\xb8\xc2\xa1': b'\xf0\x9f\x9f\xa1',  # Yellow circle
    b'\xc3\xb0\xc5\xb8\xe2\x80\x9d\xc2\xb5': b'\xf0\x9f\x94\xb5',  # Blue circle
    b'\xc3\xb0\xc5\xb8\xc5\xb8\xc2\xa2': b'\xf0\x9f\x9f\xa2',  # Green circle
    b'\xc3\xb0\xc5\xb8\xe2\x80\x9d\xc2\xb4': b'\xf0\x9f\x94\xb4',  # Red circle
    b'\xc3\xb0\xc5\xb8\xe2\x80\x9d\xcb\x86': b'\xf0\x9f\x93\x88',  # Chart increasing
    b'\xc3\xb0\xc5\xb8\xc2\x8e\xc2\xaf': b'\xf0\x9f\x8e\xaf',  # Dart
    b'\xc3\xb0\xc5\xb8\xe2\x80\xa0': b'\xf0\x9f\x8f\x86',  # Trophy
    b'\xc3\xb0\xc5\xb8\xe2\x80\x9d\xe2\x80\xa6': b'\xf0\x9f\x93\x85',  # Calendar
    b'\xc3\xb0\xc5\xb8\xc2\x8e\xc2\xa8': b'\xf0\x9f\x8e\xa8',  # Artist palette
    b'\xc3\xb0\xc5\xb8\xc5\x92': b'\xf0\x9f\x8c\x8d',  # Globe
    b'\xc3\xb0\xc5\xb8\x9a\x80': b'\xf0\x9f\x9a\x80',  # Rocket
    b'\xc3\xb0\xc5\xb8\x94\x9e': b'\xf0\x9f\x94\x9e',  # Telephone
}

count = 0
for corrupted_bytes, proper_bytes in replacements.items():
    occurrences = content.count(corrupted_bytes)
    if occurrences > 0:
        content = content.replace(corrupted_bytes, proper_bytes)
        count += occurrences
        proper_emoji = proper_bytes.decode('utf-8')
        print(f"  Replaced {occurrences}x corrupted bytes with {proper_emoji}")

print(f"\nWriting fixed content...")
with open(file_path, 'wb') as f:
    f.write(content)

print(f"\nSuccess! Fixed {count} corrupted emoji characters.")
print(f"Backup saved to: {backup_path}")
