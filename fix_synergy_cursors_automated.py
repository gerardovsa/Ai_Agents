"""
Automated fix for ALL 60 cursor leaks in synergy_routes.py
Converts: cursor = conn.cursor()
To: with conn.cursor() as cursor:
"""

import re
from pathlib import Path

def fix_all_cursor_leaks():
    file_path = Path('AI_infrastructure/routes/synergy_routes.py')
    content = file_path.read_text(encoding='utf-8')
    
    # Pattern: Find "cursor = conn.cursor()" and the rest of the function
    # We need to indent everything after it by 4 spaces until we hit the return or end of try block
    
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    fixes_applied = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line has cursor = conn.cursor()
        if re.match(r'(\s+)cursor = conn\.cursor\(\)\s*$', line):
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            
            # Replace with: with conn.cursor() as cursor:
            fixed_lines.append(f"{indent_str}with conn.cursor() as cursor:  # ✅ AUTOMATED FIX: Context manager")
            
            # Now indent all following lines by +4 until we find the matching dedent or return/except/finally
            i += 1
            extra_indent = '    '
            
            # Find the extent of code to indent
            while i < len(lines):
                next_line = lines[i]
                
                # Skip empty lines
                if not next_line.strip():
                    fixed_lines.append(next_line)
                    i += 1
                    continue
                
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # If we've dedented back to or past the original level, stop indenting
                if next_indent <= indent:
                    # Don't add extra indent to this line
                    fixed_lines.append(next_line)
                    break
                
                # Add extra indent to this line
                fixed_lines.append(extra_indent + next_line)
                i += 1
            
            fixes_applied += 1
        else:
            fixed_lines.append(line)
        
        i += 1
    
    # Write back
    fixed_content = '\n'.join(fixed_lines)
    file_path.write_text(fixed_content, encoding='utf-8')
    
    print(f"✅ Applied {fixes_applied} cursor leak fixes to synergy_routes.py")
    print(f"   Changed 'cursor = conn.cursor()' to 'with conn.cursor() as cursor:'")
    print(f"   Added proper indentation for all cursor usage blocks")
    
    return fixes_applied

if __name__ == '__main__':
    print("=" * 80)
    print("AUTOMATED CURSOR LEAK FIX FOR SYNERGY_ROUTES.PY")
    print("=" * 80)
    print()
    
    fixes = fix_all_cursor_leaks()
    
    print()
    print("⚠️  IMPORTANT: Review the changes carefully!")
    print("   Some functions may have complex control flow that needs manual adjustment")
    print()
    print("Next steps:")
    print("1. Review the file for any indentation issues")
    print("2. Run: python -m py_compile AI_infrastructure/routes/synergy_routes.py")
    print("3. Test the endpoints")
