"""
Connection Leak Detection Script
Identifies functions missing connection cleanup in finally blocks
"""

import re
from pathlib import Path

def check_file_for_leaks(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern: Functions with database connections
    function_pattern = r'def (\w+)\([^)]*\):(.*?)(?=\ndef |\nclass |\Z)'
    functions = re.findall(function_pattern, content, re.DOTALL)
    
    issues = []
    
    for func_name, func_body in functions:
        has_conn = 'get_database_connection(' in func_body
        has_with = 'with get_database_connection(' in func_body
        has_finally = 'finally:' in func_body
        has_conn_cleanup = 'if conn:' in func_body and 'conn.close()' in func_body
        
        if has_conn or has_with:
            # Check if using 'with' statement
            if has_with:
                # Using with - should be safe but can still leak on exception
                if has_finally and has_conn_cleanup:
                    status = '✅ SAFE (with + finally cleanup)'
                else:
                    status = '⚠️  RISKY (with but no finally cleanup)'
                    issues.append((func_name, 'with_no_cleanup', func_body[:200]))
            else:
                # Manual connection management
                if has_finally and has_conn_cleanup:
                    status = '✅ SAFE (manual + finally cleanup)'
                elif has_finally:
                    status = '🔴 LEAK (finally exists but no conn cleanup)'
                    issues.append((func_name, 'no_conn_cleanup', func_body[:200]))
                else:
                    status = '🔴 LEAK (no finally block)'
                    issues.append((func_name, 'no_finally', func_body[:200]))
            
            # Additional check: conn = None initialization
            has_conn_init = re.search(r'\n\s+conn = None', func_body)
            if not has_conn_init and not has_with:
                status += ' (no conn=None init)'
    
    return issues

# Check thread_routes.py
file_path = Path('c:/Users/gpoli/GIT/AI_agents/AI_infrastructure/routes/thread_routes.py')

print("="*80)
print("CONNECTION LEAK DETECTION REPORT")
print("="*80)
print()

issues = check_file_for_leaks(file_path)

if not issues:
    print("✅ NO ISSUES FOUND - All functions have proper connection cleanup")
else:
    print(f"🔴 FOUND {len(issues)} FUNCTIONS WITH POTENTIAL LEAKS:\n")
    
    for func_name, issue_type, preview in issues:
        print(f"\n{'='*60}")
        print(f"Function: {func_name}()")
        print(f"Issue: {issue_type}")
        print(f"Preview: {preview.strip()[:150]}...")
        print('='*60)
    
    print(f"\n\n📊 SUMMARY:")
    print(f"   Total functions with issues: {len(issues)}")
    print(f"   Requires manual review: YES")
    print(f"   Recommended action: Add 'if conn:' cleanup to all finally blocks")

print("\n" + "="*80)
