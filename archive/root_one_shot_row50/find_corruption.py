#!/usr/bin/env python3
"""Fix corrupted UTF-8 sequences in calculator_tools.json"""
from pathlib import Path

schema_path = Path("UI/modules_external/quote-calculator/schema/calculator_tools.json")

print("🔍 Finding and fixing corrupted UTF-8 sequences...")

# Read as binary
with open(schema_path, 'rb') as f:
    content = f.read()

# Find corrupted emoji sequences
import re
corrupted_pattern = b'\\xc3\\xa2.{0,20}\\xc2\\x8f'  # Match emoji corruption patterns

matches = list(re.finditer(corrupted_pattern, content))
print(f"Found {len(matches)} corrupted sequences")

if matches:
    for match in matches:
        start = match.start()
        end = match.end()
        context_start = max(0, start - 50)
        context_end = min(len(content), end + 50)
        
        print(f"\nPosition {start}-{end}:")
        print(f"Context: {content[context_start:context_end]}")
        print(f"Corrupted bytes: {content[start:end]}")

# Try to decode with error handling to see what's readable
try:
    text = content.decode('utf-8', errors='replace')
    print(f"\n✅ Decoded with replacements - length: {len(text)}")
    
    # Find lines with replacement character
    lines_with_errors = []
    for i, line in enumerate(text.split('\n'), 1):
        if '�' in line or '\ufffd' in line:
            lines_with_errors.append((i, line[:100]))
    
    print(f"\nFound {len(lines_with_errors)} lines with corruption:")
    for line_num, line_text in lines_with_errors[:5]:
        print(f"  Line {line_num}: {line_text}...")

except Exception as e:
    print(f"❌ Decode failed: {e}")
