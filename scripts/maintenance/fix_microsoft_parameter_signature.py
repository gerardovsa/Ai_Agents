"""
FILE: scripts/maintenance/fix_microsoft_parameter_signature.py
PURPOSE: Fix Microsoft tool parameter signature mismatch - create wrapper functions

ISSUE:
- Microsoft tool methods use positional parameters: def method(self, user_id: str, **kwargs)
- Registry spreads all parameters as kwargs: func(**{"user_id": 1, **other_params})
- Result: TypeError - missing required positional argument 'user_id'

SOLUTION:
- Replace direct method exports with wrapper functions
- Wrappers extract positional arguments from kwargs before calling methods
- Google tools work correctly because they accept all params via **kwargs

IMPLEMENTATION:
- Scan each microsoft_*_tools.py file
- Find all module-level exports (direct method assignments)
- Generate wrapper functions that handle positional args
- Replace exports with wrapper functions

AFFECTED FILES:
1. tools/implementations/microsoft_teams_tools.py (28 exports)
2. tools/implementations/microsoft_calendar_tools.py (18 exports)
3. tools/implementations/microsoft_onedrive_tools.py (16 exports)
4. tools/implementations/microsoft_word_tools.py (22 exports)
5. tools/implementations/microsoft_excel_tools.py (23 exports)
6. tools/implementations/microsoft_forms_tools.py (13 exports)
7. tools/implementations/microsoft_onenote_tools.py (15 exports)
8. tools/implementations/microsoft_sharepoint_tools.py (17 exports)
9. tools/implementations/microsoft_todo_tools.py (12 exports)
10. tools/implementations/microsoft_outlook_tools.py (11 exports)
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


class MicrosoftWrapperGenerator:
    """Generate wrapper functions for Microsoft tool exports"""
    
    def __init__(self):
        self.base_path = Path("c:/Users/gpoli/GIT/AI_agents")
        self.impl_path = self.base_path / "tools" / "implementations"
        
    def analyze_file(self, file_path: Path) -> Tuple[str, List[str], List[str]]:
        """
        Analyze Microsoft tools file to find:
        1. Class name and instance name
        2. Method signatures with positional parameters
        3. Module-level exports
        """
        content = file_path.read_text()
        
        # Find class name (pattern: class Microsoft<Service>Tools)
        class_match = re.search(r'class (Microsoft\w+Tools):', content)
        class_name = class_match.group(1) if class_match else None
        
        # Find instance name (pattern: microsoft_<service>_tools = Microsoft<Service>Tools())
        instance_match = re.search(r'(\w+_tools)\s*=\s*' + class_name + r'\(\)', content)
        instance_name = instance_match.group(1) if instance_match else None
        
        # Find all module-level exports (pattern: microsoft_<service>_<function> = <instance>.<method>)
        export_pattern = r'^(microsoft_\w+)\s*=\s*' + instance_name + r'\.(\w+)'
        exports = re.findall(export_pattern, content, re.MULTILINE)
        
        # Find method definitions to get their parameters
        method_pattern = r'def (\w+)\(self(.*?)\):'
        methods = re.findall(method_pattern, content)
        method_sigs = {name: params for name, params in methods}
        
        return content, class_name, instance_name, exports, method_sigs
    
    def generate_wrapper_code(self, exports: List[Tuple[str, str]], 
                             method_sigs: Dict[str, str], 
                             instance_name: str) -> str:
        """Generate wrapper function code for all exports"""
        
        wrappers = []
        
        for export_name, method_name in exports:
            # Get method signature to determine positional parameters
            sig = method_sigs.get(method_name, "()")
            
            # Parse parameters (e.g., ", user_id: str, name: str = None")
            params = sig.strip()
            if params.startswith(','):
                params = params[1:].strip()
            
            # Extract first positional parameter name and type
            if params:
                # Split by comma for multiple params
                first_param = params.split(',')[0].strip()
                # Extract name (e.g., "user_id: str" -> "user_id")
                param_name = first_param.split(':')[0].strip().split('=')[0].strip()
                
                if param_name and param_name != '**kwargs':
                    # Generate wrapper that extracts the positional parameter
                    wrapper = f"""
def {export_name}(**kwargs):
    \"\"\"
    Wrapper for {instance_name}.{method_name}
    Extracts positional parameter '{param_name}' from kwargs before calling method
    \"\"\"
    {param_name} = kwargs.pop('{param_name}', None)
    if {param_name} is None:
        raise ValueError("'{param_name}' is required")
    return {instance_name}.{method_name}({param_name}, **kwargs)
"""
                    wrappers.append(wrapper)
                else:
                    # No positional parameters beyond self, direct assignment is OK
                    wrappers.append(f"{export_name} = {instance_name}.{method_name}")
            else:
                wrappers.append(f"{export_name} = {instance_name}.{method_name}")
        
        return "\n".join(wrappers)
    
    def fix_file(self, file_path: Path) -> bool:
        """Fix a Microsoft tools file by replacing exports with wrappers"""
        
        try:
            content = file_path.read_text()
            
            # Find the exports section
            # Pattern: starts with "# Export all functions at module level"
            # and continues until "# Create global instance" (if present) or end of file
            
            export_section_match = re.search(
                r'(# .*?Export.*?$.*?^)(?=\n#|$)',
                content,
                re.MULTILINE | re.DOTALL
            )
            
            if not export_section_match:
                print(f"❌ Could not find export section in {file_path.name}")
                return False
            
            # Get class and instance info
            class_match = re.search(r'class (Microsoft\w+Tools):', content)
            if not class_match:
                print(f"❌ Could not find class definition in {file_path.name}")
                return False
            
            class_name = class_match.group(1)
            
            # Find instance name
            instance_match = re.search(
                r'# Create global instance.*?\n' + 
                r'(\w+_tools)\s*=\s*' + class_name + r'\(\)',
                content,
                re.DOTALL
            )
            if not instance_match:
                print(f"❌ Could not find instance name in {file_path.name}")
                return False
            
            instance_name = instance_match.group(1)
            
            # Find all current exports
            export_pattern = r'^(microsoft_\w+)\s*=\s*' + instance_name + r'\.(\w+)'
            exports = re.findall(export_pattern, content, re.MULTILINE)
            
            if not exports:
                print(f"❌ No exports found in {file_path.name}")
                return False
            
            # Get method signatures
            method_pattern = r'def (\w+)\(self(.*?)\):'
            methods = re.findall(method_pattern, content)
            method_sigs = {name: params for name, params in methods}
            
            # Generate wrapper code
            wrapper_code = self.generate_wrapper_code(exports, method_sigs, instance_name)
            
            # Replace the exports section
            # Find the section starting with "# Export all functions" through all export lines
            export_section = re.search(
                r'# .*?Export all functions at module level.*?\n'
                r'(?:# .*?\n)*'  # optional comment lines
                r'# Create global instance\n'
                r'\w+_tools\s*=\s*' + class_name + r'\(\)\n'
                r'\n'
                r'# Export all functions.*?\n'
                r'(?:# .*?\n)*'  # optional comment lines
                r'(?:microsoft_\w+\s*=.*?\n)+',
                content,
                re.MULTILINE
            )
            
            if export_section:
                # Replace with new wrapper section
                new_section = f"""# Create global instance
{instance_name} = {class_name}()

# Export all functions at module level with parameter wrapper handling
# These wrappers extract positional parameters from kwargs for registry compatibility
{wrapper_code}
"""
                content = content[:export_section.start()] + new_section + content[export_section.end():]
                
                # Write back to file
                file_path.write_text(content)
                print(f"✅ Fixed {file_path.name}: {len(exports)} exports wrapped")
                return True
            else:
                print(f"⚠️  Could not find complete export section in {file_path.name}")
                return False
                
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")
            return False
    
    def run(self):
        """Process all Microsoft tools files"""
        
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
        print("MICROSOFT TOOLS PARAMETER SIGNATURE FIX")
        print("=" * 70)
        print("\nProcessing files...")
        print()
        
        fixed_count = 0
        for filename in microsoft_files:
            file_path = self.impl_path / filename
            if file_path.exists():
                if self.fix_file(file_path):
                    fixed_count += 1
            else:
                print(f"⚠️  File not found: {filename}")
        
        print()
        print("=" * 70)
        print(f"RESULTS: {fixed_count}/{len(microsoft_files)} files processed")
        print("=" * 70)


if __name__ == "__main__":
    generator = MicrosoftWrapperGenerator()
    generator.run()
