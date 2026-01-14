"""
Fix ALL Microsoft tool exports to properly pass through kwargs
The Microsoft tools don't take user_id as a positional parameter -
they extract it from kwargs as '_user_id' for the credential injector
"""

import re
from pathlib import Path


def fix_all_microsoft_files():
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
    
    for filename in microsoft_files:
        file_path = impl_path / filename
        if not file_path.exists():
            print(f"❌ {filename}: Not found")
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8-sig')
            
            # Find class name
            class_match = re.search(r'class (Microsoft\w+Tools):', content)
            if not class_match:
                print(f"⚠️  {filename}: No class found")
                continue
            class_name = class_match.group(1)
            
            # Find instance name
            instance_match = re.search(rf'(\w+_tools)\s*=\s*{class_name}\(\)', content)
            if not instance_match:
                print(f"⚠️  {filename}: No instance found")
                continue
            instance_name = instance_match.group(1)
            
            # Find all method names by looking at def lines  
            # Extract method names from class methods (methods in the class definition)
            class_start = content.find(f'class {class_name}:')
            export_section_start = content.find('# Export all functions', class_start)
            
            if export_section_start < 0:
                print(f"⚠️  {filename}: No export section")
                continue
            
            # Get the class body (from class definition to export section)
            class_body = content[class_start:export_section_start]
            
            # Find all method definitions
            method_matches = re.finditer(r'def (\w+)\(self', class_body)
            method_names = [m.group(1) for m in method_matches]
            
            if not method_names:
                print(f"⚠️  {filename}: No methods found")
                continue
            
            # Generate new export section
            new_exports = []
            for method_name in method_names:
                export_name = f"microsoft_{method_name.replace('_', '_')}"
                # Find the actual export name pattern
                pattern = rf'(microsoft_\w+)\s*=\s*{instance_name}\.{method_name}'
                match = re.search(pattern, content)
                if match:
                    export_name = match.group(1)
                    # Create wrapper
                    wrapper = f"""def {export_name}(**kwargs):
    return {instance_name}.{method_name}(**kwargs)"""
                    new_exports.append(wrapper)
            
            if not new_exports:
                print(f"⚠️  {filename}: No exports to wrap")
                continue
            
            # Find and replace entire export section
            # Pattern: from first # Export comment to end of file or next non-whitespace/comment section
            export_pattern = r'# Export all functions.*?$'
            
            # Find all lines starting with either def (wrapped) or microsoft_* = (direct assignment)
            lines_to_replace = []
            in_export_section = False
            export_start_line = -1
            
            for i, line in enumerate(content.split('\n')):
                if '# Export all functions' in line:
                    in_export_section = True
                    export_start_line = i
                elif in_export_section:
                    if line.strip() and not line.strip().startswith('#'):
                        if line.strip().startswith('def ') or line.strip().startswith('microsoft_'):
                            continue
                        else:
                            # End of export section
                            break
            
            # Build new export section
            new_export_text = """# Export all functions at module level
# Wrappers pass through kwargs for registry compatibility
# User credentials are extracted from kwargs by individual methods

"""
            new_export_text += "\n\n".join(new_exports)
            new_export_text += "\n\n"
            
            # Replace content
            # Find start and end positions
            content_lines = content.split('\n')
            
            # Find first export comment
            export_start_idx = -1
            for i, line in enumerate(content_lines):
                if '# Export all functions' in line:
                    export_start_idx = i
                    break
            
            if export_start_idx < 0:
                print(f"⚠️  {filename}: Could not find export section start")
                continue
            
            # Find end (first non-export line after start)
            export_end_idx = export_start_idx
            for i in range(export_start_idx + 1, len(content_lines)):
                line = content_lines[i].strip()
                if not line:  # Empty line
                    continue
                elif line.startswith('#'):  # Comment
                    continue
                elif line.startswith('def '):  # Wrapper function
                    export_end_idx = i
                elif line.startswith('microsoft_') and '=' in line:  # Direct assignment
                    export_end_idx = i
                else:
                    # End of export section
                    break
            
            # Rebuild content
            new_content_lines = content_lines[:export_start_idx] + new_export_text.split('\n')[:-1] + content_lines[export_end_idx+1:]
            new_content = '\n'.join(new_content_lines)
            
            # Write back
            file_path.write_text(new_content, encoding='utf-8')
            print(f"✅ {filename}: {len(new_exports)} exports wrapped")
            
        except Exception as e:
            print(f"❌ {filename}: {e}")


if __name__ == "__main__":
    print("=" * 70)
    print("FIXING ALL MICROSOFT TOOL EXPORTS")
    print("=" * 70)
    print()
    fix_all_microsoft_files()
    print()
    print("✅ COMPLETE")
