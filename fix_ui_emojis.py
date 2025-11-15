#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix emoji encoding issues in business-ai-platform-v2.html
Replaces corrupted emoji byte sequences with proper Unicode emojis
"""

import shutil
import os

file_path = r"C:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html"
backup_path = r"C:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html.backup"

print("Backing up original file...")
shutil.copy2(file_path, backup_path)

print("Reading file...")
with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

print("Replacing corrupted emojis...")

# Map of corrupted emoji representations to proper Unicode
replacements = {
    'ðŸ"': '🔧',  # Wrench
    'ðŸ"¦': '📦',  # Package
    'ðŸ›ï¸': '🛒',  # Shopping cart
    'ðŸ'¥': '👥',  # People
    'ðŸ'°': '💰',  # Money bag
    'ðŸŸ¡': '🟡',  # Yellow circle
    'ðŸ"µ': '🔵',  # Blue circle
    'ðŸŸ¢': '🟢',  # Green circle
    'ðŸ"´': '🔴',  # Red circle
    'ðŸ"ˆ': '📈',  # Chart increasing
    'ðŸŽ¯': '🎯',  # Dart
    'ðŸ†': '🏆',  # Trophy
    'ðŸ"…': '📅',  # Calendar
    'ðŸŽ¨': '🎨',  # Artist palette
}

count = 0
for corrupted, proper in replacements.items():
    occurrences = content.count(corrupted)
    if occurrences > 0:
        content = content.replace(corrupted, proper)
        count += occurrences
        print(f"  Replaced {occurrences}x '{corrupted}' with {proper}")

print(f"\nWriting fixed content...")
with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)

print(f"\n✓ Success! Fixed {count} corrupted emoji characters.")
print(f"  Backup saved to: {backup_path}")
