"""
Comprehensive fix for ALL Microsoft tool exports with correct wrapper pattern
"""

import re
from pathlib import Path


def fix_microsoft_file(file_path: Path, needs_user_id_wrapper: bool):
    """
    Fix a Microsoft tools file with appropriate wrappers
    
    needs_user_id_wrapper = True: Methods have user_id as first positional param
    needs_user_id_wrapper = False: Methods DON'T have user_id, pass all kwargs through
    """
    content = file_path.read_text(encoding='utf-8-sig')
    
    # Find class name
    class_match = re.search(r'class (Microsoft\w+Tools):', content)
    if not class_match:
        return False
    class_name = class_match.group(1)
    
    # Find instance name
    instance_match = re.search(rf'(\w+_tools)\s*=\s*{class_name}\(\)', content)
    if not instance_match:
        return False
    instance_name = instance_match.group(1)
    
    # Find all exported functions: microsoft_<name> = <instance>.<method>
    pattern = rf'microsoft_(\w+)\s*=\s*{instance_name}\.(\w+)'
    exports = []
    for match in re.finditer(pattern, content):
        export_full_name, method_name = match.groups()
        export_name = f"microsoft_{export_full_name}"
        
        # Skip internal methods
        if method_name.startswith('_') or method_name == '__init__':
            continue
        
        exports.append((export_name, method_name))
    
    if not exports:
        return False
    
    # Generate new export section
    new_exports = []
    for export_name, method_name in exports:
        if needs_user_id_wrapper:
            # Extract user_id from kwargs as positional parameter
            wrapper = f"""def {export_name}(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return {instance_name}.{method_name}(user_id, **kwargs)"""
        else:
            # Pass all kwargs through
            wrapper = f"""def {export_name}(**kwargs):
    return {instance_name}.{method_name}(**kwargs)"""
        
        new_exports.append(wrapper)
    
    # Find the export section in content
    export_start = content.find('# Export all functions')
    if export_start < 0:
        return False
    
    # Find where exports end (look for first line that's not a def, comment, or assignment)
    content_from_export = content[export_start:]
    lines = content_from_export.split('\n')
    
    export_end_line = 0
    for i, line in enumerate(lines):
        if i == 0:
            continue  # Skip comment line
        line_stripped = line.strip()
        if not line_stripped:  # Empty line
            continue
        elif line_stripped.startswith('#'):  # Comment
            continue
        elif line_stripped.startswith('def '):  # Wrapper
            export_end_line = i
        elif line_stripped.startswith('microsoft_') and '=' in line_stripped:  # Assignment
            export_end_line = i
        else:
            # End of exports
            break
    
    # Build new content
    export_section_start_pos = content.find('# Export all functions')
    export_section_end_pos = export_start + len('\n'.join(lines[:export_end_line+2]))
    
    new_section = """# Export all functions at module level
# Wrappers handle parameter transformation for registry compatibility

"""
    new_section += "\n\n".join(new_exports)
    new_section += "\n\n"
    
    new_content = content[:export_section_start_pos] + new_section + content[export_section_end_pos:]
    
    # Write back
    file_path.write_text(new_content, encoding='utf-8')
    return True


def main():
    base_path = Path("c:/Users/gpoli/GIT/AI_agents")
    impl_path = base_path / "tools" / "implementations"
    
    files_to_fix = [
        # Teams, Calendar, OneDrive, Todo: NEED user_id wrapper
        ("microsoft_teams_tools.py", True),
        ("microsoft_calendar_tools.py", True),
        ("microsoft_onedrive_tools.py", True),
        ("microsoft_todo_tools.py", True),
        # Word, Excel, Forms, OneNote, SharePoint, Outlook: NO user_id wrapper
        ("microsoft_word_tools.py", False),
        ("microsoft_excel_tools.py", False),
        ("microsoft_forms_tools.py", False),
        ("microsoft_onenote_tools.py", False),
        ("microsoft_sharepoint_tools.py", False),
        ("microsoft_outlook_tools.py", False),
    ]
    
    print("=" * 70)
    print("MICROSOFT TOOLS - COMPREHENSIVE EXPORT FIX")
    print("=" * 70)
    print()
    
    fixed = 0
    for filename, needs_user_id in files_to_fix:
        file_path = impl_path / filename
        if not file_path.exists():
            print(f"❌ {filename}: Not found")
            continue
        
        try:
            if fix_microsoft_file(file_path, needs_user_id):
                wrapper_type = "user_id wrapper" if needs_user_id else "pass-through wrapper"
                print(f"✅ {filename}: Fixed with {wrapper_type}")
                fixed += 1
            else:
                print(f"⚠️  {filename}: Could not fix")
        except Exception as e:
            print(f"❌ {filename}: {e}")
    
    print()
    print(f"✅ COMPLETE: {fixed}/{len(files_to_fix)} files fixed")
    print("=" * 70)


if __name__ == "__main__":
    main()
