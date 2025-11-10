"""
Audit Google Workspace modules for missing **kwargs parameters

This script checks all Google Workspace tool implementations to ensure
they accept **kwargs for credential injection.
"""

import os
import re
import ast
from pathlib import Path

def extract_function_signatures(file_path):
    """Extract function signatures from Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        tree = ast.parse(content)
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get function name
                func_name = node.name
                
                # Skip private functions
                if func_name.startswith('_'):
                    continue
                
                # Check if has **kwargs
                has_kwargs = node.args.kwarg is not None
                
                # Get parameters
                params = []
                for arg in node.args.args:
                    params.append(arg.arg)
                
                functions.append({
                    'name': func_name,
                    'has_kwargs': has_kwargs,
                    'params': params,
                    'line': node.lineno
                })
        
        return functions
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def audit_module(module_path, module_name):
    """Audit a single module"""
    print(f"\n{'='*80}")
    print(f"AUDITING: {module_name}")
    print(f"{'='*80}")
    
    functions = extract_function_signatures(module_path)
    
    if not functions:
        print(f"No functions found in {module_name}")
        return
    
    missing_kwargs = []
    has_kwargs = []
    
    for func in functions:
        if func['has_kwargs']:
            has_kwargs.append(func)
        else:
            missing_kwargs.append(func)
    
    total = len(functions)
    missing_count = len(missing_kwargs)
    has_count = len(has_kwargs)
    
    print(f"\nTotal functions: {total}")
    print(f"  With **kwargs: {has_count} ({has_count/total*100:.1f}%)")
    print(f"  Missing **kwargs: {missing_count} ({missing_count/total*100:.1f}%)")
    
    if missing_kwargs:
        print(f"\nFUNCTIONS MISSING **kwargs:")
        for func in missing_kwargs:
            print(f"  Line {func['line']:4d}: {func['name']}({', '.join(func['params'])})")
    
    return {
        'module': module_name,
        'total': total,
        'has_kwargs': has_count,
        'missing_kwargs': missing_count,
        'missing_functions': missing_kwargs
    }

def main():
    """Main audit function"""
    base_path = Path(r'C:\Users\gpoli\GIT\AI_agents\google_workspace')
    
    modules = [
        ('google_slides.py', 'Google Slides'),
        ('google_forms.py', 'Google Forms'),
        ('google_docs.py', 'Google Docs'),
        ('google_sheets.py', 'Google Sheets'),
        ('gmail.py', 'Gmail'),
        ('google_drive.py', 'Google Drive'),
        ('google_calendar.py', 'Google Calendar'),
        ('google_tasks.py', 'Google Tasks'),
        ('google_meet.py', 'Google Meet'),
    ]
    
    results = []
    
    for module_file, module_name in modules:
        module_path = base_path / module_file
        if module_path.exists():
            result = audit_module(module_path, module_name)
            if result:
                results.append(result)
        else:
            print(f"\nModule not found: {module_path}")
    
    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"\n{'Module':<20} {'Total':<8} {'Has **kwargs':<15} {'Missing':<10} {'%'}")
    print(f"{'-'*80}")
    
    total_functions = 0
    total_missing = 0
    
    for result in results:
        total_functions += result['total']
        total_missing += result['missing_kwargs']
        pct = (result['missing_kwargs'] / result['total'] * 100) if result['total'] > 0 else 0
        status = "NEEDS FIX" if result['missing_kwargs'] > 0 else "OK"
        print(f"{result['module']:<20} {result['total']:<8} {result['has_kwargs']:<15} {result['missing_kwargs']:<10} {pct:>5.1f}% {status}")
    
    print(f"{'-'*80}")
    print(f"{'TOTAL':<20} {total_functions:<8} {total_functions-total_missing:<15} {total_missing:<10} {total_missing/total_functions*100:>5.1f}%")
    
    if total_missing > 0:
        print(f"\nACTION REQUIRED: {total_missing} functions need **kwargs added")
    else:
        print(f"\nALL MODULES OK: All functions accept **kwargs")

if __name__ == '__main__':
    main()
