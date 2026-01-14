"""
FILE: scripts/maintenance/validate_modules.py
PURPOSE: Validate module structure and naming conventions

DEPENDENCIES:
- json (stdlib)
- pathlib (stdlib)
- sys (stdlib)

EXPORTS:
- validate_module_structure() - Check single module for errors
- validate_all_modules() - Check all modules in UI/external/modules/
- main() - CLI entry point with color-coded output

USAGE:
    python scripts/maintenance/validate_modules.py
    
    # From any directory (if in PATH)
    validate_modules

VALIDATION CHECKS:
1. Folder name matches module ID from manifest.json
2. manifest.json exists and is valid JSON
3. JavaScript file exists (module-id.js)
4. JavaScript file name matches module ID
5. CSS file name matches module ID (if exists)
6. Module ID follows naming convention (lowercase-with-hyphens)

RETURNS:
    Exit code 0 if all modules valid
    Exit code 1 if any validation errors found

LAST MODIFIED: 2025-11-03 - Created module validation script
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Print formatted section header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def validate_module_id_format(module_id: str) -> Tuple[bool, str]:
    """
    Validate module ID follows naming convention
    
    Rules:
    - lowercase letters only
    - hyphens for word separation
    - no spaces, underscores, special chars
    - descriptive and concise
    
    Returns:
        (is_valid, error_message)
    """
    if not module_id:
        return False, "Module ID cannot be empty"
    
    if module_id != module_id.lower():
        return False, f"Module ID must be lowercase (found: '{module_id}')"
    
    if ' ' in module_id:
        return False, f"Module ID cannot contain spaces (found: '{module_id}')"
    
    if '_' in module_id:
        return False, f"Module ID should use hyphens, not underscores (found: '{module_id}')"
    
    # Check for valid characters (lowercase letters, numbers, hyphens)
    valid_chars = set('abcdefghijklmnopqrstuvwxyz0123456789-')
    invalid_chars = set(module_id) - valid_chars
    if invalid_chars:
        return False, f"Module ID contains invalid characters: {invalid_chars}"
    
    if module_id.startswith('-') or module_id.endswith('-'):
        return False, f"Module ID cannot start or end with hyphen (found: '{module_id}')"
    
    if '--' in module_id:
        return False, f"Module ID cannot contain consecutive hyphens (found: '{module_id}')"
    
    return True, ""


def validate_module_structure(module_folder: Path) -> Tuple[bool, List[str]]:
    """
    Validate a single module's structure and naming
    
    Args:
        module_folder: Path to module folder
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    folder_name = module_folder.name
    
    print_info(f"Validating module: {folder_name}")
    
    # Check 1: manifest.json exists
    manifest_path = module_folder / 'manifest.json'
    if not manifest_path.exists():
        errors.append(f"Missing manifest.json in {folder_name}/")
        return False, errors
    
    # Check 2: manifest.json is valid JSON
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in {folder_name}/manifest.json: {e}")
        return False, errors
    
    # Check 3: manifest has 'id' field
    if 'id' not in manifest:
        errors.append(f"Missing 'id' field in {folder_name}/manifest.json")
        return False, errors
    
    module_id = manifest['id']
    
    # Check 4: Module ID format validation
    id_valid, id_error = validate_module_id_format(module_id)
    if not id_valid:
        errors.append(f"Invalid module ID format: {id_error}")
    
    # Check 5: Folder name matches module ID (CRITICAL!)
    if folder_name != module_id:
        errors.append(
            f"CRITICAL: Folder name mismatch!\n"
            f"   Folder name: '{folder_name}'\n"
            f"   Module ID:   '{module_id}'\n"
            f"   → Folder MUST be renamed to '{module_id}/' to fix 404 errors"
        )
    
    # Check 6: JavaScript file exists
    js_file = module_folder / f"{module_id}.js"
    if not js_file.exists():
        # Try folder name as fallback
        js_file_alt = module_folder / f"{folder_name}.js"
        if not js_file_alt.exists():
            errors.append(f"Missing JavaScript file: {module_id}.js")
        else:
            errors.append(
                f"JavaScript file name mismatch:\n"
                f"   Found: {folder_name}.js\n"
                f"   Expected: {module_id}.js"
            )
    
    # Check 7: CSS file naming (if exists) - ENHANCED with manifest.json awareness
    css_files = list(module_folder.glob("*.css"))
    if css_files:
        expected_css = module_folder / f"{module_id}.css"
        if expected_css not in css_files:
            # Check if CSS files are explicitly referenced in manifest dependencies
            css_in_manifest = False
            if 'dependencies' in manifest:
                css_names = [f.name for f in css_files]
                manifest_deps = manifest['dependencies']
                # Check if any CSS files are explicitly listed in dependencies
                for css_name in css_names:
                    if any(css_name in str(dep) for dep in manifest_deps):
                        css_in_manifest = True
                        break
            
            # Only report error if CSS not in manifest dependencies
            if not css_in_manifest:
                actual_css_names = [f.name for f in css_files]
                errors.append(
                    f"CSS file name mismatch:\n"
                    f"   Found: {actual_css_names}\n"
                    f"   Expected: {module_id}.css\n"
                    f"   OR: Explicitly list CSS files in manifest.json dependencies array"
                )
            else:
                # CSS is intentionally named and referenced in manifest - this is valid
                print_info(f"  Non-standard CSS naming detected but validated via manifest.json")
    
    # Check 8: Module has 'module' field with main script
    if 'module' in manifest:
        module_config = manifest['module']
        if 'main' in module_config:
            main_script = module_config['main']
            if main_script != f"{module_id}.js":
                errors.append(
                    f"manifest.json 'module.main' mismatch:\n"
                    f"   Declared: {main_script}\n"
                    f"   Expected: {module_id}.js"
                )
    
    if errors:
        return False, errors
    
    return True, []


def validate_all_modules() -> Tuple[int, int, Dict[str, List[str]]]:
    """
    Validate all modules in UI/external/modules/
    
    Returns:
        (valid_count, invalid_count, error_dict)
    """
    # Get project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent
    modules_dir = project_root / 'UI' / 'external' / 'modules'
    
    if not modules_dir.exists():
        print_error(f"Modules directory not found: {modules_dir}")
        return 0, 0, {}
    
    print_info(f"Scanning modules in: {modules_dir}")
    
    # Get all module folders (directories only, skip manifest.json)
    module_folders = [
        d for d in modules_dir.iterdir() 
        if d.is_dir() and d.name not in ['.git', '__pycache__', 'node_modules']
    ]
    
    if not module_folders:
        print_warning("No module folders found")
        return 0, 0, {}
    
    print_info(f"Found {len(module_folders)} module folders\n")
    
    valid_count = 0
    invalid_count = 0
    all_errors = {}
    
    for module_folder in sorted(module_folders):
        is_valid, errors = validate_module_structure(module_folder)
        
        if is_valid:
            print_success(f"{module_folder.name}: VALID")
            valid_count += 1
        else:
            print_error(f"{module_folder.name}: INVALID")
            for error in errors:
                print(f"    {error}")
            all_errors[module_folder.name] = errors
            invalid_count += 1
        print()  # Empty line between modules
    
    return valid_count, invalid_count, all_errors


def main():
    """Main entry point for validation script"""
    print_header("MODULE STRUCTURE VALIDATION")
    
    valid, invalid, errors = validate_all_modules()
    
    # Print summary
    print_header("VALIDATION SUMMARY")
    
    total = valid + invalid
    if total == 0:
        print_warning("No modules found to validate")
        return 0
    
    print(f"Total modules scanned: {total}")
    print_success(f"Valid modules: {valid}")
    
    if invalid > 0:
        print_error(f"Invalid modules: {invalid}")
        print()
        print_header("ERRORS FOUND")
        
        for module_name, module_errors in errors.items():
            print(f"\n{Colors.RED}{Colors.BOLD}Module: {module_name}{Colors.END}")
            for error in module_errors:
                print(f"  • {error}")
        
        print()
        print_header("NEXT STEPS")
        print_info("Fix the errors above before deploying modules")
        print_info("Common fixes:")
        print("  1. Rename folder to match module ID")
        print("  2. Rename .js/.css files to match module ID")
        print("  3. Update manifest.json 'id' field to match folder")
        print()
        
        return 1  # Exit with error code
    else:
        print()
        print_success("🎉 All modules are valid and follow naming conventions!")
        print()
        return 0


if __name__ == '__main__':
    sys.exit(main())
