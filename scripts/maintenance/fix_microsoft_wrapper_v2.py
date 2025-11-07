"""
FILE: scripts/maintenance/fix_microsoft_wrapper_v2.py
PURPOSE: Fix Microsoft tool parameter signature by creating wrapper functions

This is a simpler, more direct implementation that:
1. Reads each Microsoft tools file
2. Finds all module-level exports
3. Replaces them with wrapper functions
4. Preserves all method signatures in wrapper
"""

import re
from pathlib import Path


def create_wrapper_for_export(export_line: str, instance_name: str, method_sigs: dict) -> str:
    """
    Convert: microsoft_teams_list_teams = microsoft_teams_tools.teams_list_teams
    To:      def microsoft_teams_list_teams(**kwargs): ...
    """
    # Parse: microsoft_teams_list_teams = microsoft_teams_tools.teams_list_teams
    match = re.match(r'(\w+)\s*=\s*\w+\.(\w+)', export_line.strip())
    if not match:
        return export_line  # Return original if can't parse
    
    export_name, method_name = match.groups()
    
    # Get method signature to see what parameters it needs
    method_sig = method_sigs.get(method_name, "")
    
    # Extract first parameter name (e.g., from ", user_id: str" extract "user_id")
    first_param = None
    if method_sig:
        # Remove "self" and split
        params = method_sig.split(',')
        for param in params:
            param = param.strip()
            if param and param != '**kwargs':
                # Extract name before ':' or '='
                name = param.split(':')[0].split('=')[0].strip()
                if name:
                    first_param = name
                    break
    
    if first_param and first_param not in ['kwargs', 'args']:
        # Generate wrapper that extracts positional parameter
        wrapper = f"""def {export_name}(**kwargs):
    {first_param} = kwargs.pop('{first_param}', None)
    if {first_param} is None:
        raise ValueError("{first_param} is required")
    return {instance_name}.{method_name}({first_param}, **kwargs)"""
        return wrapper
    else:
        # No special handling needed
        return export_line


def fix_microsoft_file(file_path: Path) -> bool:
    """Fix a single Microsoft tools file"""
    
    try:
        content = file_path.read_text(encoding='utf-8-sig')  # Handle BOM
    except Exception as e:
        print(f"❌ Could not read {file_path.name}: {e}")
        return False
    
    # Find class name
    class_match = re.search(r'class (Microsoft\w+Tools):', content)
    if not class_match:
        print(f"⚠️  No class found in {file_path.name}")
        return False
    class_name = class_match.group(1)
    
    # Find instance name
    instance_match = re.search(rf'(\w+_tools)\s*=\s*{class_name}\(\)', content)
    if not instance_match:
        print(f"⚠️  No instance found in {file_path.name}")
        return False
    instance_name = instance_match.group(1)
    
    # Extract all method signatures
    method_pattern = r'def (\w+)\(self(.*?)\):'
    method_sigs = {}
    for match in re.finditer(method_pattern, content):
        method_name, params = match.groups()
        method_sigs[method_name] = params  # params start with comma
    
    # Find the export section
    # Look for: microsoft_<name> = <instance>.<method> pattern
    export_pattern = rf'^(microsoft_\w+)\s*=\s*{instance_name}\.\w+'
    
    # Split content into lines
    lines = content.split('\n')
    
    # Find start of exports (look for "# Export" or "# GLOBAL" comments)
    export_start = -1
    export_end = -1
    
    for i, line in enumerate(lines):
        if 'Export' in line or 'EXPORT' in line:
            export_start = i
        elif export_start >= 0 and re.match(export_pattern, line.strip()):
            export_end = i
    
    if export_start < 0:
        print(f"⚠️  No export section found in {file_path.name}")
        return False
    
    # Find where exports end (next non-export, non-comment line or EOF)
    if export_end < 0:
        export_end = len(lines) - 1
    else:
        # Find last export line
        for i in range(export_end, len(lines)):
            if re.match(export_pattern, lines[i].strip()):
                export_end = i
            elif lines[i].strip() and not lines[i].strip().startswith('#'):
                break
    
    # Build new export section with wrappers
    new_lines = []
    
    # Copy everything before exports
    for i in range(export_start):
        new_lines.append(lines[i])
    
    # Add comment
    new_lines.append("# Export all functions at module level with parameter wrappers")
    new_lines.append("# Wrappers handle positional parameters for registry kwargs spreading")
    new_lines.append("")
    
    # Process and add wrapped exports
    export_count = 0
    for i in range(export_start + 1, export_end + 1):
        line = lines[i]
        if re.match(export_pattern, line.strip()):
            wrapper = create_wrapper_for_export(line, instance_name, method_sigs)
            new_lines.append(wrapper)
            new_lines.append("")
            export_count += 1
        elif line.strip():
            new_lines.append(line)
    
    # Copy rest of file
    for i in range(export_end + 1, len(lines)):
        new_lines.append(lines[i])
    
    # Write back
    try:
        file_path.write_text('\n'.join(new_lines), encoding='utf-8')
        print(f"✅ {file_path.name}: {export_count} exports wrapped")
        return True
    except Exception as e:
        print(f"❌ Could not write {file_path.name}: {e}")
        return False


def main():
    base_path = Path("c:/Users/gpoli/GIT/AI_agents")
    impl_path = base_path / "tools" / "implementations"
    
    microsoft_files = [
        "microsoft_teams_tools.py",
        "microsoft_calendar_tools.py",
        "microsoft_onedrive_tools.py",
        "microsoft_word_tools.py",
        "microsoft_excel_tools.py",
        "microsoft_forms_tools.py",
        "microsoft_onenote_tools.py",
        "microsoft_sharepoint_tools.py",
        "microsoft_todo_tools.py",
        "microsoft_outlook_tools.py",
    ]
    
    print("=" * 70)
    print("MICROSOFT TOOLS - PARAMETER WRAPPER FIX")
    print("=" * 70)
    print()
    
    fixed = 0
    for filename in microsoft_files:
        file_path = impl_path / filename
        if file_path.exists():
            if fix_microsoft_file(file_path):
                fixed += 1
        else:
            print(f"⚠️  Not found: {filename}")
    
    print()
    print(f"✅ COMPLETE: {fixed}/{len(microsoft_files)} files fixed")
    print("=" * 70)


if __name__ == "__main__":
    main()
