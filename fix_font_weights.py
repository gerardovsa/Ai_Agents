#!/usr/bin/env python3
"""
Final Font-Weight Cleanup Script
Comments out all uncommented font-weight declarations
December 4, 2025
"""

import re
from pathlib import Path

project_root = Path(r"c:\Users\gpoli\GIT\AI_agents")

files_to_fix = [
    "UI/modules_internal/thread-manager/thread.css",
    "UI/modules_internal/prompt-library/prompt-library.css",
    "UI/modules_internal/thread-cards/thread-card-styles.css"
]

stats = {"files": 0, "total": 0}

for rel_path in files_to_fix:
    file_path = project_root / rel_path
    print(f"Processing: {rel_path}")
    
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    # Pattern: whitespace + font-weight: value; (not already commented)
    # Negative lookbehind/lookahead to avoid already commented lines
    pattern = r'(?<!/\* )(\s+)(font-weight:\s*[^;]+;)(?! \*/)'
    
    def replace_fn(match):
        indent = match.group(1)
        declaration = match.group(2)
        return f"{indent}/* {declaration} */"
    
    content = re.sub(pattern, replace_fn, content)
    
    if content != original:
        matches = len(re.findall(pattern, original))
        file_path.write_text(content, encoding='utf-8')
        print(f"  ✓ Commented {matches} font-weight declarations")
        stats["files"] += 1
        stats["total"] += matches
    else:
        print(f"  - No uncommented font-weight found")

print(f"\n{'='*60}")
print(f"COMPLETE: {stats['files']} files modified, {stats['total']} total comments")
print(f"{'='*60}")
