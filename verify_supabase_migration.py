"""
Supabase Migration Verification Script

Verifies that all production routes and APIs are using Supabase connections
instead of direct SQLite connections.

Run this after making Supabase migration changes.

Usage:
    python verify_supabase_migration.py
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def colored(text: str, color: str) -> str:
    """Add color to text"""
    return f"{color}{text}{RESET}"

def search_file_for_pattern(file_path: Path, pattern: str, is_regex: bool = True) -> List[Tuple[int, str]]:
    """
    Search file for pattern and return matching lines
    
    Returns:
        List of (line_number, line_content) tuples
    """
    matches = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if is_regex:
                    if re.search(pattern, line):
                        matches.append((line_num, line.strip()))
                else:
                    if pattern in line:
                        matches.append((line_num, line.strip()))
    except Exception as e:
        pass  # Skip files that can't be read
    return matches

def scan_directory(directory: Path, pattern: str, exclude_dirs: List[str] = None) -> Dict[str, List]:
    """
    Scan directory for files matching pattern
    
    Returns:
        Dictionary of {file_path: [(line_num, line_content), ...]}
    """
    if exclude_dirs is None:
        exclude_dirs = ['archive', 'venv', '__pycache__', 'node_modules', '.git']
    
    results = {}
    
    for py_file in directory.rglob('*.py'):
        # Skip excluded directories
        if any(excluded in str(py_file) for excluded in exclude_dirs):
            continue
        
        matches = search_file_for_pattern(py_file, pattern)
        if matches:
            results[str(py_file)] = matches
    
    return results

def main():
    """Main verification logic"""
    
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}SUPABASE MIGRATION VERIFICATION{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")
    
    project_root = Path(__file__).parent
    ai_infrastructure = project_root / 'AI_infrastructure'
    
    # Check 1: Look for direct sqlite3.connect() calls
    print(f"{BOLD}[1] Searching for direct sqlite3.connect() calls...{RESET}")
    sqlite_connects = scan_directory(
        ai_infrastructure,
        r'sqlite3\.connect\s*\(',
        exclude_dirs=['archive', 'migrations', 'database_toolkit', 'sync', 'venv', '__pycache__']
    )
    
    if sqlite_connects:
        print(f"  {RED}⚠ Found {len(sqlite_connects)} files with sqlite3.connect():{RESET}")
        for file_path, matches in sqlite_connects.items():
            relative_path = Path(file_path).relative_to(project_root)
            print(f"    {RED}✗{RESET} {relative_path}")
            for line_num, line_content in matches[:3]:  # Show first 3 matches
                print(f"      Line {line_num}: {line_content[:80]}...")
    else:
        print(f"  {GREEN}✓ No direct sqlite3.connect() calls found{RESET}")
    
    # Check 2: Verify routes use get_database_connection()
    print(f"\n{BOLD}[2] Verifying routes use get_database_connection()...{RESET}")
    routes_dir = ai_infrastructure / 'routes'
    
    routes_with_db = []
    routes_without_db = []
    
    for route_file in routes_dir.glob('*_routes.py'):
        # Skip G_Folder routes (different project)
        if 'G_Folder' in str(route_file):
            continue
        
        content = route_file.read_text(encoding='utf-8')
        
        # Check if file uses database
        if 'def get_db_connection' in content or 'sqlite3' in content or 'database' in content.lower():
            # Check if using get_database_connection()
            if 'get_database_connection(' in content:
                routes_with_db.append(route_file.name)
            else:
                routes_without_db.append(route_file.name)
    
    print(f"  {GREEN}✓ Routes using get_database_connection(): {len(routes_with_db)}{RESET}")
    for route in sorted(routes_with_db):
        print(f"    {GREEN}✓{RESET} {route}")
    
    if routes_without_db:
        print(f"  {YELLOW}⚠ Routes potentially not using Supabase: {len(routes_without_db)}{RESET}")
        for route in sorted(routes_without_db):
            print(f"    {YELLOW}?{RESET} {route}")
    
    # Check 3: Verify init_prompt_library.py uses Supabase
    print(f"\n{BOLD}[3] Checking init_prompt_library.py...{RESET}")
    init_file = ai_infrastructure / 'init_prompt_library.py'
    if init_file.exists():
        content = init_file.read_text(encoding='utf-8')
        if 'get_database_connection' in content:
            print(f"  {GREEN}✓ Uses get_database_connection(){RESET}")
        elif 'sqlite3.connect' in content:
            print(f"  {RED}✗ Still uses sqlite3.connect(){RESET}")
        else:
            print(f"  {YELLOW}? Cannot determine connection type{RESET}")
    else:
        print(f"  {YELLOW}⚠ File not found{RESET}")
    
    # Check 4: Verify kanban_analytics_routes.py uses Supabase
    print(f"\n{BOLD}[4] Checking kanban_analytics_routes.py...{RESET}")
    kanban_file = routes_dir / 'kanban_analytics_routes.py'
    if kanban_file.exists():
        content = kanban_file.read_text(encoding='utf-8')
        if 'get_database_connection' in content:
            print(f"  {GREEN}✓ Uses get_database_connection(){RESET}")
        elif 'sqlite3.connect' in content:
            print(f"  {RED}✗ Still uses sqlite3.connect(){RESET}")
        else:
            print(f"  {YELLOW}? Cannot determine connection type{RESET}")
    else:
        print(f"  {YELLOW}⚠ File not found{RESET}")
    
    # Check 5: Verify flask_app.py init
    print(f"\n{BOLD}[5] Checking flask_app.py initialization...{RESET}")
    flask_file = ai_infrastructure / 'flask_app.py'
    if flask_file.exists():
        content = flask_file.read_text(encoding='utf-8')
        if 'init_prompt_library_table()' in content and 'db_path' not in re.search(r'init_prompt_library_table\([^)]*\)', content).group(0):
            print(f"  {GREEN}✓ Calls init_prompt_library_table() without db_path{RESET}")
        elif 'init_prompt_library_table(db_path)' in content:
            print(f"  {RED}✗ Still passes db_path to init_prompt_library_table(){RESET}")
        else:
            print(f"  {YELLOW}? Cannot determine initialization method{RESET}")
    else:
        print(f"  {YELLOW}⚠ File not found{RESET}")
    
    # Check 6: Count import statements
    print(f"\n{BOLD}[6] Analyzing import statements...{RESET}")
    sqlite_imports = scan_directory(
        ai_infrastructure,
        r'^import sqlite3|^from sqlite3',
        exclude_dirs=['archive', 'migrations', 'database_toolkit', 'sync', 'tests', 'venv', '__pycache__']
    )
    
    supabase_imports = scan_directory(
        ai_infrastructure,
        r'from shared\.database_utils import get_database_connection',
        exclude_dirs=['archive', 'migrations', 'venv', '__pycache__']
    )
    
    print(f"  Files with sqlite3 imports: {len(sqlite_imports)}")
    print(f"  Files with get_database_connection imports: {len(supabase_imports)}")
    
    # Summary
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}SUMMARY{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")
    
    issues_found = len(sqlite_connects) + len(routes_without_db)
    
    if issues_found == 0:
        print(f"{GREEN}{BOLD}✓ ALL CHECKS PASSED!{RESET}")
        print(f"{GREEN}All production routes are using Supabase connections.{RESET}")
    else:
        print(f"{YELLOW}{BOLD}⚠ {issues_found} POTENTIAL ISSUES FOUND{RESET}")
        print(f"{YELLOW}Review the items above and update to use get_database_connection().{RESET}")
    
    print(f"\n{BOLD}Production Readiness:{RESET}")
    if issues_found == 0:
        print(f"  {GREEN}✓ Ready for deployment{RESET}")
    elif issues_found <= 3:
        print(f"  {YELLOW}⚠ Minor issues - fix before deployment{RESET}")
    else:
        print(f"  {RED}✗ Multiple issues - requires fixes{RESET}")
    
    print(f"\n{BOLD}Next Steps:{RESET}")
    if issues_found > 0:
        print(f"  1. Fix files listed above to use get_database_connection()")
        print(f"  2. Re-run this verification script")
        print(f"  3. Test with: BISTART")
        print(f"  4. Deploy to Render")
    else:
        print(f"  1. Test locally with: BISTART")
        print(f"  2. Run: python test_supabase_routes.py")
        print(f"  3. Deploy to Render")
        print(f"  4. Verify production logs")
    
    print(f"\n{BOLD}{'='*80}{RESET}\n")
    
    return 0 if issues_found == 0 else 1

if __name__ == '__main__':
    exit(main())
