"""
Automatically fix cursor leaks by adding cursor.close() before returns/commits
"""
import re

def fix_cursor_leaks(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find all functions with cursor = conn.cursor()
    cursor_functions = []
    in_function = None
    function_start = None
    indent_level = None
    
    for i, line in enumerate(lines):
        # Detect function start
        if line.strip().startswith('def '):
            in_function = line.strip()
            function_start = i
            indent_level = len(line) - len(line.lstrip())
        
        # Detect cursor creation
        if in_function and 'cursor = conn.cursor()' in line:
            cursor_functions.append({
                'name': in_function,
                'start': function_start,
                'cursor_line': i,
                'indent': indent_level
            })
        
        # Detect function end (next function or dedent to module level)
        if in_function and i > function_start:
            current_indent = len(line) - len(line.lstrip())
            if line.strip() and current_indent <= indent_level and line.strip().startswith('def '):
                in_function = None
    
    print(f"Found {len(cursor_functions)} functions with cursor = conn.cursor()")
    
    # For each function, find where to add cursor.close()
    modified_lines = lines.copy()
    offset = 0
    
    for func in cursor_functions:
        print(f"\nProcessing: {func['name']}")
        
        # Find all return statements and conn.commit() in this function
        function_end = len(lines)
        for i in range(func['start'] + 1, len(lines)):
            line = lines[i]
            current_indent = len(line) - len(line.lstrip())
            
            # Function ended (dedented to or past function level)
            if line.strip() and current_indent <= func['indent']:
                function_end = i
                break
        
        # Work backwards through function to find returns/commits
        close_locations = []
        for i in range(function_end - 1, func['cursor_line'], -1):
            line = lines[i]
            
            # Skip lines that are too far dedented (different scope)
            line_indent = len(line) - len(line.lstrip())
            if line.strip() and line_indent < func['indent'] + 4:
                continue
            
            # Find returns
            if 'return ' in line or line.strip() == 'return':
                # Check if cursor.close() is already on previous line
                prev_line = lines[i - 1] if i > 0 else ''
                if 'cursor.close()' not in prev_line:
                    close_locations.append(i)
            
            # Find conn.commit()
            if 'conn.commit()' in line:
                # Check if cursor.close() is already on previous line
                prev_line = lines[i - 1] if i > 0 else ''
                if 'cursor.close()' not in prev_line:
                    close_locations.append(i)
        
        # Remove duplicates and sort
        close_locations = sorted(set(close_locations))
        print(f"  Found {len(close_locations)} locations to add cursor.close()")
        
        # Insert cursor.close() at each location (work backwards to preserve line numbers)
        for loc in reversed(close_locations):
            line = modified_lines[loc + offset]
            line_indent = len(line) - len(line.lstrip())
            indent_str = ' ' * line_indent
            
            # Insert cursor.close() before this line
            close_line = f"{indent_str}cursor.close()  # ✅ AUTO-FIXED: Close cursor before return/commit\n"
            modified_lines.insert(loc + offset, close_line)
            offset += 1
            print(f"    Added cursor.close() before line {loc}")
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(modified_lines)
    
    print(f"\n✅ Fixed {len(cursor_functions)} functions in {filepath}")

if __name__ == '__main__':
    fix_cursor_leaks(r'C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\thread_routes.py')
    print("\nDone! Check the file for cursor.close() additions.")
