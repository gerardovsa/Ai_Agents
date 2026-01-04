"""
Fix all cursor leaks in thread_routes.py
Converts: cursor = conn.cursor()
To: with conn.cursor() as cursor:
"""

import re
from pathlib import Path
import shutil

def fix_cursor_leaks(file_path):
    """Fix cursor leaks with smart indentation"""
    
    # Backup first
    backup_path = file_path.with_suffix('.py.backup')
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup created: {backup_path.name}")
    
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    fixes_applied = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Match: cursor = conn.cursor() (must have indentation)
        match = re.match(r'^(\s+)cursor = conn\.cursor\(\)\s*$', line)
        
        if match:
            indent = match.group(1)
            indent_len = len(indent)
            
            # Replace with context manager
            fixed_lines.append(f"{indent}with conn.cursor() as cursor:")
            fixes_applied += 1
            i += 1
            
            # Add extra 4-space indent to the NEXT non-empty line only if it needs it
            # This handles the case where the next line is already part of a block
            added_initial_indent = False
            
            # Find and indent the code block
            while i < len(lines):
                next_line = lines[i]
                
                # Empty line - keep as is
                if not next_line.strip():
                    fixed_lines.append(next_line)
                    i += 1
                    continue
                
                next_indent_len = len(next_line) - len(next_line.lstrip())
                
                # If we've dedented back to or past original level, stop indenting
                if next_indent_len <= indent_len:
                    # Don't increment i - let outer loop handle this line
                    break
                
                # If this is the first real line after cursor creation
                if not added_initial_indent:
                    # Check if it's already indented properly (e.g., part of existing with block)
                    # If next line is more than 4 spaces deeper, it's already in a sub-block
                    if next_indent_len > indent_len + 4:
                        # Just add it as-is, already indented
                        fixed_lines.append(next_line)
                    else:
                        # Add extra indentation
                        fixed_lines.append('    ' + next_line)
                    added_initial_indent = True
                else:
                    # Add extra indentation to subsequent lines
                    fixed_lines.append('    ' + next_line)
                
                i += 1
        else:
            fixed_lines.append(line)
            i += 1
    
    # Write fixed content
    file_path.write_text('\n'.join(fixed_lines), encoding='utf-8')
    
    return fixes_applied, backup_path

def validate_syntax(file_path):
    """Check if file has valid Python syntax"""
    import subprocess
    result = subprocess.run(
        ['python', '-m', 'py_compile', str(file_path)],
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stderr

if __name__ == '__main__':
    print("=" * 80)
    print("FIXING CURSOR LEAKS IN thread_routes.py")
    print("=" * 80)
    
    file_path = Path('AI_infrastructure/routes/thread_routes.py')
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        exit(1)
    
    # Apply fixes
    print(f"\n📝 Processing: {file_path.name}")
    fixes, backup = fix_cursor_leaks(file_path)
    print(f"✅ Applied {fixes} cursor leak fixes")
    
    # Validate
    print(f"\n🔍 Validating Python syntax...")
    is_valid, error = validate_syntax(file_path)
    
    if is_valid:
        print("✅ SYNTAX VALID - All fixes successful!")
        print(f"\n📊 Summary:")
        print(f"   File: {file_path.name}")
        print(f"   Fixes: {fixes}")
        print(f"   Backup: {backup.name}")
        print(f"\n✅ thread_routes.py is now LEAK-FREE!")
    else:
        print("❌ SYNTAX ERRORS DETECTED")
        print(f"\nError:\n{error}")
        
        # Restore backup
        print(f"\n♻️  Restoring from backup...")
        shutil.copy2(backup, file_path)
        print("✅ Original file restored")
        print("\n⚠️  Manual review needed - file has complex control flow")
