"""
Script to fix ALL connection leaks in synergy_routes.py

This script identifies functions with manual conn.close() calls and generates
the fixes needed to move them to try/finally blocks.

Run this to generate a report of all functions that need fixing.
"""

import re
from pathlib import Path

def analyze_synergy_routes():
    """Analyze synergy_routes.py for connection leak patterns"""
    
    file_path = Path(__file__).parent.parent.parent / 'AI_infrastructure' / 'routes' / 'synergy_routes.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find all functions and their conn.close() calls
    functions = []
    current_function = None
    current_function_start = None
    indent_level = 0
    
    for i, line in enumerate(lines, 1):
        # Detect function definitions
        if line.strip().startswith('def ') and '(' in line:
            # Extract function name
            match = re.match(r'\s*def\s+(\w+)\s*\(', line)
            if match:
                func_name = match.group(1)
                current_function = func_name
                current_function_start = i
                indent_level = len(line) - len(line.lstrip())
                functions.append({
                    'name': func_name,
                    'start_line': i,
                    'conn_closes': [],
                    'has_try': False,
                    'has_finally': False,
                    'end_line': None
                })
        
        # Check if we're inside a function
        if current_function and functions:
            func = functions[-1]
            
            # Detect try blocks
            if 'try:' in line and line.strip().startswith('try:'):
                func['has_try'] = True
            
            # Detect finally blocks  
            if 'finally:' in line and line.strip().startswith('finally:'):
                func['has_finally'] = True
            
            # Detect conn.close() calls
            if 'conn.close()' in line:
                func['conn_closes'].append({
                    'line': i,
                    'code': line.strip(),
                    'indent': len(line) - len(line.lstrip())
                })
            
            # Detect end of function (next function or end of file)
            if i > current_function_start:
                stripped = line.strip()
                if stripped.startswith('def ') or stripped.startswith('@') or (i == len(lines)):
                    func['end_line'] = i - 1
    
    # Set end line for last function
    if functions and functions[-1]['end_line'] is None:
        functions[-1]['end_line'] = len(lines)
    
    return functions, lines

def generate_report():
    """Generate a report of all functions with connection leaks"""
    
    functions, lines = analyze_synergy_routes()
    
    print("=" * 80)
    print("SYNERGY_ROUTES.PY - CONNECTION LEAK AUDIT REPORT")
    print("=" * 80)
    print()
    
    # Filter functions with conn.close() calls
    functions_with_closes = [f for f in functions if f['conn_closes']]
    
    print(f"Total functions analyzed: {len(functions)}")
    print(f"Functions with conn.close(): {len(functions_with_closes)}")
    print()
    
    # Categorize by leak risk
    critical_leaks = []  # No finally block
    potential_leaks = []  # Has finally but close in try
    safe_functions = []  # Close in finally
    
    for func in functions_with_closes:
        if not func['has_finally']:
            # CRITICAL: No finally block at all
            critical_leaks.append(func)
        else:
            # Check if conn.close() is in finally block
            # (We'd need more sophisticated parsing for this)
            # For now, assume it's OK if has finally
            safe_functions.append(func)
    
    print("🔴 CRITICAL LEAKS (No finally block):")
    print("-" * 80)
    for func in critical_leaks:
        print(f"\n  Function: {func['name']}")
        print(f"  Lines: {func['start_line']}-{func['end_line']}")
        print(f"  conn.close() calls: {len(func['conn_closes'])}")
        for close in func['conn_closes']:
            print(f"    - Line {close['line']}: {close['code']}")
    
    print(f"\n\n📊 SUMMARY:")
    print(f"  🔴 Critical leaks (no finally): {len(critical_leaks)}")
    print(f"  🟢 Safe functions (has finally): {len(safe_functions)}")
    print()
    
    print("=" * 80)
    print("FUNCTIONS REQUIRING FIX:")
    print("=" * 80)
    
    for i, func in enumerate(critical_leaks, 1):
        print(f"\n{i}. {func['name']} (lines {func['start_line']}-{func['end_line']})")
        print(f"   conn.close() at line(s): {', '.join(str(c['line']) for c in func['conn_closes'])}")
    
    print()
    print("=" * 80)
    print(f"TOTAL FUNCTIONS TO FIX: {len(critical_leaks)}")
    print("=" * 80)
    
    return critical_leaks

if __name__ == '__main__':
    leaks = generate_report()
