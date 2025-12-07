"""
Automatic Connection Leak Fixer
Converts 'with get_database_connection()' to explicit try/finally pattern
"""

import re
from pathlib import Path

def fix_connection_pattern(content):
    """
    Convert:
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            ...
            cursor.close()
            cursor = None
    
    To:
        conn = None
        try:
            conn = get_database_connection('sessions')
            cursor = conn.cursor()
            ...
            cursor.close()
            cursor = None
            conn.close()
            conn = None
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if conn:
                try:
                    conn.close()
                except:
                    pass
    """
    
    # Pattern to find 'with get_database_connection' blocks
    # This is complex because we need to handle indentation
    pattern = r'(\s+)with get_database_connection\(([^)]+)\) as conn:\s*\n'
    
    def replacer(match):
        indent = match.group(1)
        db_name = match.group(2)
        
        # Build replacement
        replacement = f'{indent}conn = get_database_connection({db_name})\n'
        replacement += f'{indent}try:\n'
        
        return replacement
    
    # Step 1: Replace 'with' statements
    modified = re.sub(pattern, replacer, content)
    
    # Step 2: Add conn = None initialization at function start
    # Find functions that have get_database_connection
    func_pattern = r'(def \w+\([^)]*\):\s*\n(?:\s*"""[^"]*"""\s*\n)?)((\s+)cursor = None\s*\n)'
    
    def func_replacer(match):
        func_start = match.group(1)
        cursor_init = match.group(2)
        indent = match.group(3)
        
        # Add conn = None after cursor = None
        return f'{func_start}{cursor_init}{indent}conn = None\n'
    
    modified = re.sub(func_pattern, func_replacer, modified)
    
    # Step 3: Add conn.close() before cursor.close() in main body
    # Pattern: Find cursor.close() followed by cursor = None
    close_pattern = r'(\s+)cursor\.close\(\)\s*\n\1cursor = None\s*\n'
    
    def close_replacer(match):
        indent = match.group(1)
        replacement = f'{indent}cursor.close()\n'
        replacement += f'{indent}cursor = None\n'
        replacement += f'{indent}conn.close()\n'
        replacement += f'{indent}conn = None\n'
        return replacement
    
    modified = re.sub(close_pattern, close_replacer, modified)
    
    # Step 4: Add conn cleanup to finally blocks
    # Pattern: Find finally blocks that only have cursor cleanup
    finally_pattern = r'(finally:\s*\n\s+if cursor:\s*\n\s+try:\s*\n\s+cursor\.close\(\)\s*\n\s+except:\s*\n\s+pass\s*\n)'
    
    def finally_replacer(match):
        original = match.group(1)
        indent_match = re.search(r'(\s+)if cursor:', original)
        if indent_match:
            indent = indent_match.group(1)
            # Add conn cleanup after cursor cleanup
            conn_cleanup = f'{indent}if conn:\n'
            conn_cleanup += f'{indent}    try:\n'
            conn_cleanup += f'{indent}        conn.close()\n'
            conn_cleanup += f'{indent}    except:\n'
            conn_cleanup += f'{indent}        pass\n'
            return original + conn_cleanup
        return original
    
    modified = re.sub(finally_pattern, finally_replacer, modified)
    
    # Step 5: Close the try block (add except clause before finally if needed)
    # This is tricky - need to ensure proper nesting
    
    return modified

# Read file
file_path = Path('c:/Users/gpoli/GIT/AI_agents/AI_infrastructure/routes/thread_routes.py')
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("Analyzing thread_routes.py...")
print(f"File size: {len(content)} chars, {len(content.splitlines())} lines\n")

# Count current patterns
with_count = content.count('with get_database_connection(')
finally_with_conn = content.count('if conn:')

print(f"Found {with_count} 'with get_database_connection()' statements")
print(f"Found {finally_with_conn} 'if conn:' cleanup blocks\n")

if with_count > finally_with_conn:
    print(f"⚠️  {with_count - finally_with_conn} functions missing conn cleanup!")
    print("\nThis script would fix them, but given complexity,")
    print("recommend manual fixes for safety.")
else:
    print("✅ All functions have conn cleanup")

print("\n" + "="*80)
print("RECOMMENDATION: Manual fix using find-replace pattern")
print("="*80)
print("""
Pattern to add to each 'finally' block:

        if conn:
            try:
                conn.close()
            except:
                pass
""")
