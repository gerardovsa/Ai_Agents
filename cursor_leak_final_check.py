import os
import re

routes_dir = r'c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes'

suspicious_files = [
    'communication_routes.py',
    'device_lock_routes.py', 
    'oauth_routes.py',
    'token_routes.py'
]

print("\n=== DETAILED CURSOR ANALYSIS ===\n")

for fname in suspicious_files:
    fpath = os.path.join(routes_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all cursor creations
    cursor_pattern = r'cursor\s*=\s*(?:conn|connection)\.cursor\s*\(\)'
    close_pattern = r'cursor\.close\s*\(\)'
    
    cursors = list(re.finditer(cursor_pattern, content))
    closes = list(re.finditer(close_pattern, content))
    
    print(f"{fname}:")
    print(f"  Cursor creations: {len(cursors)}")
    print(f"  Cursor closes: {len(closes)}")
    
    if len(cursors) != len(closes):
        print(f"  ❌ MISMATCH: {len(cursors) - len(closes)} missing closes")
        
        # Show line numbers
        lines = content.split('\n')
        print("\n  Cursor creation lines:")
        for match in cursors:
            line_num = content[:match.start()].count('\n') + 1
            print(f"    Line {line_num}: {lines[line_num-1].strip()}")
        
        print("\n  Cursor close lines:")
        for match in closes:
            line_num = content[:match.start()].count('\n') + 1
            print(f"    Line {line_num}: {lines[line_num-1].strip()}")
    else:
        print(f"  ✅ BALANCED")
    
    print()
