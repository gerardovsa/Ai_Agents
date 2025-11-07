"""
Bulk wrapper function replacement for remaining Microsoft tools files
"""

import re
from pathlib import Path


def get_exports_from_file(file_path: Path) -> list:
    """Extract the export function names from a Microsoft tools file"""
    content = file_path.read_text(encoding='utf-8-sig')
    
    # Find instance name
    instance_match = re.search(r'(\w+_tools)\s*=\s*Microsoft\w+Tools\(\)', content)
    if not instance_match:
        return []
    instance_name = instance_match.group(1)
    
    # Find all exports: microsoft_<name> = <instance>.<method>
    pattern = rf'^(microsoft_\w+)\s*=\s*{instance_name}\.(\w+)'
    exports = []
    for match in re.finditer(pattern, content, re.MULTILINE):
        export_name, method_name = match.groups()
        exports.append((export_name, method_name))
    
    return instance_name, exports


def create_wrapper_block(instance_name: str, exports: list) -> str:
    """Create wrapper function block"""
    wrappers = ["# Export all functions at module level with parameter wrappers"]
    wrappers.append("# Wrappers extract positional 'user_id' parameter from kwargs for registry compatibility")
    wrappers.append("")
    
    for export_name, method_name in exports:
        wrapper = f"""def {export_name}(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return {instance_name}.{method_name}(user_id, **kwargs)
"""
        wrappers.append(wrapper)
    
    return "\n".join(wrappers)


def fix_file(file_path: Path):
    """Replace exports in a file with wrapper functions"""
    content = file_path.read_text(encoding='utf-8-sig')
    
    instance_name, exports = get_exports_from_file(file_path)
    if not instance_name or not exports:
        print(f"⚠️  {file_path.name}: No exports found")
        return
    
    # Find the export section to replace
    # Pattern: starts with # Export comment through last export assignment
    pattern = r'# Export all functions at module level.*?\n(?:.*?\n)*?microsoft_\w+\s*=\s*\w+\.\w+\n\n'
    
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print(f"⚠️  {file_path.name}: Could not find export section")
        return
    
    # Generate new wrapper block
    new_wrappers = create_wrapper_block(instance_name, exports)
    
    # Replace
    new_content = content[:match.start()] + new_wrappers + "\n\n" + content[match.end():]
    
    # Write back
    file_path.write_text(new_content, encoding='utf-8')
    print(f"✅ {file_path.name}: {len(exports)} exports wrapped")


def main():
    base_path = Path("c:/Users/gpoli/GIT/AI_agents")
    impl_path = base_path / "tools" / "implementations"
    
    files_to_fix = [
        "microsoft_onedrive_tools.py",
        "microsoft_word_tools.py",
        "microsoft_excel_tools.py",
        "microsoft_forms_tools.py",
        "microsoft_onenote_tools.py",
        "microsoft_sharepoint_tools.py",
        "microsoft_todo_tools.py",
        "microsoft_outlook_tools.py",
    ]
    
    print("Wrapping remaining Microsoft tool exports...\n")
    
    for filename in files_to_fix:
        file_path = impl_path / filename
        if file_path.exists():
            fix_file(file_path)
        else:
            print(f"❌ {filename}: Not found")
    
    print("\n✅ COMPLETE")


if __name__ == "__main__":
    main()
